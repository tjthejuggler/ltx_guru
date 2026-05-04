#!/usr/bin/env python3
"""
Transcribe lyrics from audio using Deepgram Nova-3 via ppq.ai.

This tool uses ASR (automatic speech recognition) to transcribe what is
*actually sung* in the audio, producing per-word timestamps. This is far
more reliable for sung music than forced alignment (Gentle), which tries
to map an external reference text onto the audio and drifts when the
text doesn't match the recording.

For long audio (>60s), the file is automatically split into overlapping
chunks to work around the Whisper API's tendency to truncate long files.

Usage:
    python transcribe_lyrics.py <audio_path> [--output OUTPUT] [--api-key KEY_FILE]
                                    [--chunk-duration SECONDS] [--language LANG]
                                    [--prompt TEXT]

Output format matches the existing synced_lyrics.json schema:
    {
      "song_title": "...",
      "artist_name": "...",
      "word_timestamps": [
        {"word": "you", "start": 0.52, "end": 0.78, "confidence": 0.95},
        ...
      ],
      "raw_lyrics": "You got a fast car...\nI remember we were driving...",
      "transcription_source": "deepgram-nova3",
      "alignment_stats": {
        "total_words": 412,
        "aligned_words": 412,
        "unaligned_words": 0,
        "quality": "EXCELLENT"
      }
    }
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PPQ_API_BASE = "https://api.ppq.ai/v1"
DEFAULT_CHUNK_DURATION = 10  # seconds — short chunks prevent Whisper from skipping sung sections
CHUNK_OVERLAP = 5  # seconds of overlap — covers the ~5s Whisper tends to skip at chunk starts
# Gap threshold for inserting a line break in raw_lyrics (seconds of silence)
LINE_BREAK_GAP = 1.5


def _load_api_key(api_key_path: str | None) -> str:
    """Load the ppq.ai API key from file or environment."""
    if api_key_path and os.path.isfile(api_key_path):
        return Path(api_key_path).read_text().strip()
    # Try environment variable
    key = os.environ.get("PPQ_API_KEY", "")
    if key:
        return key
    # Try default location
    default_path = os.path.join(os.path.dirname(__file__), "..", "sequence_maker", "ppq_api_key.txt")
    if os.path.isfile(default_path):
        return Path(default_path).read_text().strip()
    raise FileNotFoundError(
        "No ppq.ai API key found. Provide --api-key, set PPQ_API_KEY env var, "
        "or place the key in sequence_maker/ppq_api_key.txt"
    )


def _get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds using ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def _split_audio_chunk(audio_path: str, start: float, duration: float, output_path: str) -> str:
    """Extract a chunk of audio using ffmpeg. Returns the output path."""
    subprocess.run(
        ["ffmpeg", "-y", "-i", audio_path,
         "-ss", str(start), "-t", str(duration),
         "-ac", "1", "-ar", "16000",  # mono 16kHz for efficiency
         output_path],
        capture_output=True, check=True,
    )
    return output_path


def _transcribe_chunk(audio_path: str, api_key: str, language: str = "en",
                      prompt: str = "") -> dict:
    """Transcribe a single audio chunk via Deepgram Nova-3."""
    with open(audio_path, "rb") as f:
        data = {
            "model": "nova-3",
            "response_format": "verbose_json",
            "language": language,
        }
        if prompt:
            data["prompt"] = prompt[:2000]
        resp = requests.post(
            f"{PPQ_API_BASE}/audio/transcriptions",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": ("audio.mp3", f, "audio/mpeg")},
            data=data,
            timeout=180,
        )
    resp.raise_for_status()
    return resp.json()


def _merge_chunk_words(chunks_with_offsets: list[tuple[dict, float]],
                       chunk_duration: float) -> list[dict]:
    """Merge word lists from multiple chunks, adjusting timestamps by offset.

    Strategy: each chunk "owns" the words in its non-overlapping region.
    - Chunk i owns words from [i*chunk_duration, (i+1)*chunk_duration).
    - The overlap region [i*chunk_duration, i*chunk_duration + CHUNK_OVERLAP]
      is owned by chunk i (not chunk i+1), so early words are never dropped.
    - Within the overlap zone we still deduplicate by keeping the higher-
      confidence version if both chunks produced the same word.
    """
    all_words = []
    for chunk_idx, (chunk_data, offset) in enumerate(chunks_with_offsets):
        for w in chunk_data.get("words", []):
            if w.get("start") is None or w.get("end") is None:
                continue
            abs_start = w["start"] + offset
            abs_end = w["end"] + offset
            all_words.append({
                "word": w["word"],
                "start": abs_start,
                "end": abs_end,
                "confidence": w.get("confidence", 1.0),
                "_chunk": chunk_idx,
                "_offset": offset,
            })

    if not all_words:
        return []

    # Sort by start time
    all_words.sort(key=lambda w: w["start"])

    # Deduplicate: if two words overlap significantly, keep the one with
    # higher confidence. This handles the overlap zone between chunks.
    deduped = [all_words[0]]
    for w in all_words[1:]:
        prev = deduped[-1]
        # Overlap check: word starts before previous word ends (with 50ms tolerance)
        if w["start"] < prev["end"] - 0.05:
            # Keep the one with higher confidence
            if w["confidence"] > prev["confidence"]:
                deduped[-1] = w
            # else keep prev (already there)
        else:
            deduped.append(w)

    # Clean up internal fields
    for w in deduped:
        w.pop("_offset", None)
        w.pop("_chunk", None)

    return deduped


def _build_raw_lyrics(words: list[dict], line_break_gap: float = LINE_BREAK_GAP) -> str:
    """Build a human-readable lyrics string with line breaks at silence gaps.

    When the gap between consecutive words exceeds line_break_gap seconds,
    a newline is inserted instead of a space. This produces natural lyric
    lines that match how the song is phrased.
    """
    if not words:
        return ""

    parts = [words[0]["word"]]
    for i in range(1, len(words)):
        gap = words[i]["start"] - words[i - 1]["end"]
        if gap >= line_break_gap:
            parts.append("\n")
        else:
            parts.append(" ")
        parts.append(words[i]["word"])

    return "".join(parts)


def transcribe_lyrics(audio_path: str, api_key: str, language: str = "en",
                      prompt: str = "", chunk_duration: float = DEFAULT_CHUNK_DURATION,
                      song_title: str = "Unknown Song",
                      artist_name: str = "Unknown Artist") -> dict:
    """Transcribe lyrics from audio with per-word timestamps.

    For audio longer than chunk_duration, splits into overlapping chunks
    and merges the results.
    """
    audio_path = os.path.abspath(audio_path)
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    duration = _get_audio_duration(audio_path)
    logger.info(f"Audio duration: {duration:.1f}s")

    chunks_with_offsets = []

    if duration <= chunk_duration + CHUNK_OVERLAP:
        # Short enough to transcribe in one go
        logger.info("Transcribing in single chunk...")
        result = _transcribe_chunk(audio_path, api_key, language, prompt)
        chunks_with_offsets.append((result, 0.0))
    else:
        # Split into overlapping chunks
        num_chunks = int(duration // chunk_duration) + 1
        logger.info(f"Splitting into {num_chunks} chunks of ~{chunk_duration}s with {CHUNK_OVERLAP}s overlap")

        with tempfile.TemporaryDirectory(prefix="lyrics_transcribe_") as tmpdir:
            for i in range(num_chunks):
                start = i * chunk_duration
                if start >= duration:
                    break
                # Each chunk covers chunk_duration + overlap, except the last
                chunk_dur = min(chunk_duration + CHUNK_OVERLAP, duration - start)
                chunk_path = os.path.join(tmpdir, f"chunk_{i:03d}.mp3")

                logger.info(f"  Chunk {i+1}/{num_chunks}: {start:.1f}s - {start+chunk_dur:.1f}s")
                _split_audio_chunk(audio_path, start, chunk_dur, chunk_path)

                # Pass prompt to every chunk — helps the model recognise sung lyrics
                result = _transcribe_chunk(chunk_path, api_key, language, prompt)
                chunks_with_offsets.append((result, start))

                words_in_chunk = len(result.get("words", []))
                logger.info(f"    Got {words_in_chunk} words")

    # Merge all chunks
    all_words = _merge_chunk_words(chunks_with_offsets, chunk_duration)
    logger.info(f"Merged total: {len(all_words)} words")

    # Build raw lyrics text with line breaks at silence gaps
    raw_lyrics = _build_raw_lyrics(all_words)

    # Build quality stats
    total = len(all_words)
    quality = "EXCELLENT" if total > 300 else "GOOD" if total > 150 else "FAIR" if total > 50 else "POOR"

    return {
        "song_title": song_title,
        "artist_name": artist_name,
        "word_timestamps": all_words,
        "raw_lyrics": raw_lyrics,
        "transcription_source": "deepgram-nova3",
        "alignment_stats": {
            "total_words": total,
            "aligned_words": total,  # ASR always produces timestamps
            "unaligned_words": 0,
            "quality": quality,
        },
        "processing_status": "completed",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe lyrics from audio using Deepgram Nova-3 via ppq.ai"
    )
    parser.add_argument("audio_path", help="Path to the audio file (mp3, wav, etc.)")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument("--api-key", help="Path to ppq.ai API key file")
    parser.add_argument("--chunk-duration", type=float, default=DEFAULT_CHUNK_DURATION,
                        help=f"Chunk duration in seconds (default: {DEFAULT_CHUNK_DURATION})")
    parser.add_argument("--language", default="en", help="Language code (default: en)")
    parser.add_argument("--prompt", default="", help="Prompt text to guide transcription")
    parser.add_argument("--song-title", default="Unknown Song", help="Song title")
    parser.add_argument("--artist-name", default="Unknown Artist", help="Artist name")
    args = parser.parse_args()

    api_key = _load_api_key(args.api_key)

    result = transcribe_lyrics(
        audio_path=args.audio_path,
        api_key=api_key,
        language=args.language,
        prompt=args.prompt,
        chunk_duration=args.chunk_duration,
        song_title=args.song_title,
        artist_name=args.artist_name,
    )

    # Determine output path
    output_path = args.output
    if not output_path:
        base = os.path.splitext(os.path.basename(args.audio_path))[0]
        output_path = f"{base}_synced_lyrics.json"

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    stats = result["alignment_stats"]
    logger.info(f"Wrote {output_path}: {stats['total_words']} words, quality={stats['quality']}")

    # Print summary
    words = result["word_timestamps"]
    if words:
        print(f"\n=== Transcription Summary ===")
        print(f"Words: {len(words)}")
        print(f"Audio span: {words[0]['start']:.2f}s - {words[-1]['end']:.2f}s")
        print(f"Quality: {stats['quality']}")
        print(f"\n=== First 20 words ===")
        for w in words[:20]:
            print(f"  {w['start']:7.2f}s - {w['end']:7.2f}s  {w['word']}")
        print(f"\n=== Last 10 words ===")
        for w in words[-10:]:
            print(f"  {w['start']:7.2f}s - {w['end']:7.2f}s  {w['word']}")
        print(f"\n=== Gaps > 5s (missed sections) ===")
        prev_end = 0.0
        prev_word = "(start)"
        for w in words:
            gap = w["start"] - prev_end
            if gap > 5:
                print(f"  GAP {gap:5.1f}s: {prev_end:.1f}s -> {w['start']:.1f}s  "
                      f"(after '{prev_word}', before '{w['word']}')")
            prev_end = w["end"]
            prev_word = w["word"]


if __name__ == "__main__":
    main()
