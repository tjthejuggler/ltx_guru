#!/usr/bin/env python3
"""
align_lyrics_gentle.py - Ground-truth lyrics alignment using Gentle forced alignment.

Use this pipeline when you HAVE the exact lyrics for a song. Gentle performs
forced alignment: it takes the known lyrics text and the audio, then finds the
precise timestamp for every word in the lyrics.

Advantages over the ASR-only pipeline:
  - Every word in the lyrics gets a timestamp (no gaps from missed sections)
  - Timestamps are accurate because Gentle aligns to the exact text you provide
  - Line breaks from the original lyrics file are preserved in raw_lyrics

Prerequisites:
  - Gentle must be running: docker run -p 8765:8765 lowerquality/gentle
  - Check with: curl http://localhost:8765/transcriptions

Usage:
    python align_lyrics_gentle.py <audio_file> <lyrics_txt> [options]

    python align_lyrics_gentle.py \\
        "sequence_maker/songs/Tracy Chapman Fast Car Lyrics.mp3" \\
        sequence_projects/fast_car_ground_truth/lyrics.txt \\
        --output sequence_projects/fast_car_ground_truth/fast_car_ground_truth_synced_lyrics.json \\
        --song-title "Fast Car" \\
        --artist-name "Tracy Chapman"
"""

import argparse
import json
import os
import sys

import requests


GENTLE_URL = "http://localhost:8765/transcriptions?async=false"


def _check_gentle() -> bool:
    """Return True if Gentle server is reachable."""
    try:
        r = requests.get("http://localhost:8765/", timeout=5)
        return r.status_code in (200, 405)
    except Exception:
        return False


def align_lyrics_gentle(
    audio_path: str,
    lyrics_txt_path: str,
    output_path: str,
    song_title: str = "",
    artist_name: str = "",
) -> dict:
    """
    Align lyrics to audio using Gentle forced alignment.

    Returns the synced_lyrics dict (also written to output_path).
    """
    audio_path = os.path.abspath(audio_path)
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    with open(lyrics_txt_path, "r") as f:
        lyrics_text = f.read()

    if not lyrics_text.strip():
        raise ValueError(f"Lyrics file is empty: {lyrics_txt_path}")

    print(f"Audio:  {audio_path}")
    print(f"Lyrics: {lyrics_txt_path} ({len(lyrics_text)} chars)")

    if not _check_gentle():
        raise RuntimeError(
            "Gentle server is not running. Start it with:\n"
            "  docker run -p 8765:8765 lowerquality/gentle"
        )

    print("Sending to Gentle for forced alignment (this may take a minute)...")
    with open(audio_path, "rb") as audio_file:
        response = requests.post(
            GENTLE_URL,
            files={
                "audio": audio_file,
                "transcript": (None, lyrics_text),
            },
            timeout=600,  # 10 min for long songs
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"Gentle API error {response.status_code}: {response.text[:500]}"
        )

    gentle_result = response.json()

    # Build word_timestamps — keep every word from the lyrics, even unaligned ones.
    # Unaligned words get start=None, end=None so downstream tools can see the
    # full lyric text and interpolate if needed.
    word_timestamps = []
    aligned_count = 0
    not_found_count = 0

    for word in gentle_result.get("words", []):
        case = word.get("case", "unknown")
        original_word = word.get("word", "")
        aligned_word = word.get("alignedWord", original_word)

        if "start" in word and "end" in word:
            word_timestamps.append({
                "word": aligned_word or original_word,
                "start": round(word["start"], 3),
                "end": round(word["end"], 3),
                "case": case,
            })
            aligned_count += 1
        else:
            word_timestamps.append({
                "word": original_word,
                "start": None,
                "end": None,
                "case": case,
            })
            if case == "not-found-in-audio":
                not_found_count += 1

    total = len(word_timestamps)
    pct = (100.0 * aligned_count / total) if total else 0.0
    quality = (
        "EXCELLENT" if pct >= 90 else
        "GOOD"      if pct >= 75 else
        "FAIR"      if pct >= 60 else
        "POOR"
    )

    print(f"Aligned: {aligned_count}/{total} words ({pct:.1f}%) — {quality}")
    if not_found_count:
        print(f"  Not found in audio: {not_found_count} words")

    # Verify timestamps are monotonically increasing (sanity check)
    aligned_words = [w for w in word_timestamps if w["start"] is not None]
    out_of_order = sum(
        1 for i in range(1, len(aligned_words))
        if aligned_words[i]["start"] < aligned_words[i - 1]["start"]
    )
    if out_of_order:
        print(f"WARNING: {out_of_order} out-of-order timestamps in Gentle output")
    else:
        print("Timestamps are monotonically increasing ✓")

    result = {
        "song_title": song_title,
        "artist_name": artist_name,
        # Preserve original line breaks from the lyrics file
        "raw_lyrics": lyrics_text.strip(),
        "word_timestamps": word_timestamps,
        "transcription_source": "gentle-forced-alignment",
        "alignment_stats": {
            "total_words": total,
            "aligned_words": aligned_count,
            "not_found_in_audio": not_found_count,
            "aligned_percentage": round(pct, 2),
            "quality": quality,
            "out_of_order_timestamps": out_of_order,
        },
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote {output_path}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Align known lyrics to audio using Gentle forced alignment"
    )
    parser.add_argument("audio", help="Path to audio file (MP3/WAV/etc.)")
    parser.add_argument("lyrics", help="Path to plain-text lyrics file")
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output JSON path for synced lyrics",
    )
    parser.add_argument("--song-title", default="", help="Song title (metadata)")
    parser.add_argument("--artist-name", default="", help="Artist name (metadata)")
    args = parser.parse_args()

    result = align_lyrics_gentle(
        audio_path=args.audio,
        lyrics_txt_path=args.lyrics,
        output_path=args.output,
        song_title=args.song_title,
        artist_name=args.artist_name,
    )

    words = result["word_timestamps"]
    stats = result["alignment_stats"]
    print(f"\n=== Summary ===")
    print(f"Total words:   {stats['total_words']}")
    print(f"Aligned:       {stats['aligned_words']} ({stats['aligned_percentage']:.1f}%)")
    print(f"Not found:     {stats['not_found_in_audio']}")
    print(f"Quality:       {stats['quality']}")

    aligned = [w for w in words if w["start"] is not None]
    if aligned:
        print(f"Audio span:    {aligned[0]['start']:.2f}s – {aligned[-1]['end']:.2f}s")

    print(f"\n=== First 20 words ===")
    for w in words[:20]:
        if w["start"] is not None:
            print(f"  {w['start']:7.2f}s - {w['end']:7.2f}s  {w['word']}")
        else:
            print(f"  [not found]          {w['word']}")

    print(f"\n=== Last 10 words ===")
    for w in words[-10:]:
        if w["start"] is not None:
            print(f"  {w['start']:7.2f}s - {w['end']:7.2f}s  {w['word']}")
        else:
            print(f"  [not found]          {w['word']}")


if __name__ == "__main__":
    main()
