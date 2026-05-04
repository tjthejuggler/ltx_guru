#!/usr/bin/env python3
"""
align_with_anchors.py - Hybrid lyrics alignment using ASR anchors + lyrics text.

The Whisper/Nova-3 API skips large sections of sung music, producing sparse
word-level timestamps. This tool:

  1. Takes the sparse ASR output (word + start + end) as anchor timestamps.
  2. Takes the full lyrics text (all words in order).
  3. Uses dynamic programming sequence alignment to match ASR words to lyrics
     positions while preserving temporal order.
  4. Interpolates timestamps for lyrics words that fall between anchors.
  5. Extrapolates timestamps before the first anchor and after the last anchor.

The result is a complete word_timestamps list covering the whole song, where:
  - Words matched to ASR anchors have accurate timestamps (confidence=1.0).
  - Interpolated words have estimated timestamps (confidence=0.0, interpolated=True).

Usage:
    python align_with_anchors.py <asr_json> <lyrics_txt> [--output OUTPUT]
                                 [--audio-duration SECONDS]
"""

import argparse
import json
import os
import re
import sys


# ---------------------------------------------------------------------------
# Text normalisation helpers
# ---------------------------------------------------------------------------

def _normalise(word: str) -> str:
    """Lowercase, strip punctuation for fuzzy matching."""
    return re.sub(r"[^a-z0-9']", "", word.lower())


def _tokenise_lyrics(text: str) -> list:
    """Split lyrics text into a flat list of words (preserving order)."""
    words = []
    for line in text.splitlines():
        for w in line.split():
            w = w.strip()
            if w:
                words.append(w)
    return words


# ---------------------------------------------------------------------------
# Sequence alignment (order-preserving)
# ---------------------------------------------------------------------------

def _align_sequences(lyrics_words: list, asr_words: list,
                     audio_duration: float = None) -> list:
    """
    Align ASR words to lyrics positions using time-based positioning.

    Strategy:
    1. First pass: try exact/partial text matching within a ±SEARCH_WINDOW
       around the time-estimated lyrics position. This gives high-confidence
       anchors where the ASR transcription matches the lyrics text.
    2. Second pass: for every ASR word that didn't match in pass 1, use the
       time-based position directly as an anchor (no text matching required).
       This handles cases where the singer improvises or the ASR mishears words.

    Returns a list of (lyrics_index, asr_index) pairs, sorted by lyrics_index.
    """
    n_lyrics = len(lyrics_words)
    n_asr = len(asr_words)

    if n_lyrics == 0 or n_asr == 0:
        return []

    norm_lyrics = [_normalise(w) for w in lyrics_words]
    norm_asr = [_normalise(w["word"]) for w in asr_words]

    # How far (in lyrics positions) to search around the time-estimated position
    SEARCH_WINDOW = 60

    if audio_duration is None:
        asr_end_t = asr_words[-1].get("end", 300.0) if asr_words else 300.0
        audio_duration = asr_end_t + 5.0

    def text_score(li, ai):
        lw = norm_lyrics[li]
        aw = norm_asr[ai]
        if not lw or not aw:
            return 0
        if lw == aw:
            return 2
        if lw.startswith(aw) or aw.startswith(lw):
            return 1
        if len(lw) >= 3 and len(aw) >= 3 and lw[:3] == aw[:3]:
            return 1
        return 0

    def time_to_lyrics_pos(t):
        """Convert audio timestamp to estimated lyrics word index."""
        return int(t / audio_duration * n_lyrics)

    # --- Pass 1: text-match anchors ---
    text_matches = {}  # asr_index -> lyrics_index
    used_lyrics = set()
    min_lyrics_pos = 0

    for ai in range(n_asr):
        aw = norm_asr[ai]
        if not aw:
            continue
        t = asr_words[ai].get("start", 0.0)
        expected_pos = time_to_lyrics_pos(t)
        search_start = max(min_lyrics_pos, expected_pos - SEARCH_WINDOW)
        search_end = min(n_lyrics, expected_pos + SEARCH_WINDOW + 1)

        best_score = 0
        best_pos = -1
        for li in range(search_start, search_end):
            if li in used_lyrics:
                continue
            s = text_score(li, ai)
            if s > best_score:
                best_score = s
                best_pos = li

        if best_pos >= 0 and best_score > 0:
            text_matches[ai] = best_pos
            used_lyrics.add(best_pos)
            min_lyrics_pos = best_pos + 1

    # --- Pass 2: time-only anchors for unmatched ASR words ---
    # Process unmatched ASR words in time order, assigning each to the
    # nearest unoccupied lyrics position >= the current min_lyrics_pos.
    # This preserves temporal order.
    unmatched = sorted(
        [ai for ai in range(n_asr) if ai not in text_matches and norm_asr[ai]],
        key=lambda ai: asr_words[ai].get("start", 0.0)
    )

    all_matches = dict(text_matches)  # asr_index -> lyrics_index
    # Rebuild min_lyrics_pos from text_matches (sorted by lyrics pos)
    p2_min_pos = 0
    if text_matches:
        p2_min_pos = max(text_matches.values()) + 1

    # We need to interleave pass-2 anchors with pass-1 anchors in time order.
    # Build a combined list of (time, ai, lpos_or_None) for pass-1 matches,
    # then process pass-2 in time order respecting gaps between pass-1 anchors.

    # Build sorted list of pass-1 anchors by time
    p1_by_time = sorted(
        [(asr_words[ai].get("start", 0.0), lpos) for ai, lpos in text_matches.items()],
        key=lambda x: x[0]
    )

    # For each unmatched ASR word, find the valid lyrics range:
    # - must be >= min_lyrics_pos (order constraint)
    # - must be < next pass-1 anchor's lyrics pos (don't cross pass-1 anchors)
    # Build a lookup: for a given time t, what is the max lyrics pos allowed?
    def get_max_lpos_for_time(t):
        """Return the lyrics pos of the next pass-1 anchor after time t."""
        for anchor_t, anchor_lpos in p1_by_time:
            if anchor_t > t:
                return anchor_lpos - 1
        return n_lyrics - 1

    p2_min_pos = 0  # reset; will advance as we assign

    for ai in unmatched:
        t = asr_words[ai].get("start", 0.0)
        expected_pos = time_to_lyrics_pos(t)
        max_lpos = get_max_lpos_for_time(t)

        # Clamp expected_pos to valid range
        search_start = max(p2_min_pos, expected_pos - SEARCH_WINDOW)
        search_end = min(max_lpos + 1, expected_pos + SEARCH_WINDOW + 1)

        if search_start > search_end:
            continue

        # Find nearest unoccupied position to expected_pos within range
        candidate = -1
        for delta in range(0, SEARCH_WINDOW + 1):
            for pos in [expected_pos + delta, expected_pos - delta]:
                if search_start <= pos <= max_lpos and pos not in used_lyrics:
                    candidate = pos
                    break
            if candidate >= 0:
                break

        if candidate >= 0:
            all_matches[ai] = candidate
            used_lyrics.add(candidate)
            p2_min_pos = candidate + 1

    # Sort by lyrics position (order-preserving)
    matches = sorted(
        [(lpos, ai) for ai, lpos in all_matches.items()],
        key=lambda x: x[0]
    )
    return matches


# ---------------------------------------------------------------------------
# Interpolation
# ---------------------------------------------------------------------------

def _interpolate(lyrics_words: list, anchors: list, audio_duration: float) -> list:
    """
    Build a complete word_timestamps list for all lyrics words.

    anchors: list of (lyrics_index, asr_word_dict) pairs, sorted by lyrics_index
    """
    n = len(lyrics_words)
    result = [None] * n

    if not anchors:
        # No anchors — spread evenly across audio duration
        per_word = audio_duration / max(n, 1)
        for i, w in enumerate(lyrics_words):
            s = i * per_word
            e = s + per_word * 0.8
            result[i] = {"word": w, "start": round(s, 3),
                         "end": round(e, 3), "confidence": 0.0,
                         "interpolated": True}
        return result

    # Place anchor words
    for lpos, asr_w in anchors:
        result[lpos] = {
            "word": lyrics_words[lpos],
            "start": asr_w["start"],
            "end": asr_w["end"],
            "confidence": asr_w.get("confidence", 1.0),
            "interpolated": False,
        }

    anchor_positions = [lpos for lpos, _ in anchors]

    # --- Interpolate between consecutive anchors ---
    for seg_idx in range(len(anchor_positions) - 1):
        lo = anchor_positions[seg_idx]
        hi = anchor_positions[seg_idx + 1]
        if hi - lo <= 1:
            continue
        t_start = result[lo]["end"]
        t_end = result[hi]["start"]
        gap_words = hi - lo - 1
        if gap_words <= 0 or t_end <= t_start:
            # Timestamps are inverted or equal — spread minimally
            t_end = t_start + gap_words * 0.3
        per_word = (t_end - t_start) / (gap_words + 1)
        for k, lpos in enumerate(range(lo + 1, hi)):
            s = t_start + (k + 1) * per_word
            e = s + per_word * 0.8
            result[lpos] = {
                "word": lyrics_words[lpos],
                "start": round(max(s, 0.0), 3),
                "end": round(min(e, t_end), 3),
                "confidence": 0.0,
                "interpolated": True,
            }

    # --- Estimate words-per-second from anchor density ---
    if len(anchor_positions) >= 2:
        total_anchor_time = (result[anchor_positions[-1]]["start"]
                             - result[anchor_positions[0]]["end"])
        total_anchor_words = anchor_positions[-1] - anchor_positions[0]
        wps = total_anchor_words / max(total_anchor_time, 1.0)
        wps = max(0.5, min(wps, 5.0))  # clamp to sane range
    else:
        wps = 2.0
    per_word = 1.0 / wps

    # --- Extrapolate before first anchor ---
    first_pos = anchor_positions[0]
    if first_pos > 0:
        anchor_start = result[first_pos]["start"]
        for k, lpos in enumerate(range(first_pos - 1, -1, -1)):
            s = anchor_start - (k + 1) * per_word
            e = s + per_word * 0.8
            result[lpos] = {
                "word": lyrics_words[lpos],
                "start": round(max(s, 0.0), 3),
                "end": round(max(e, 0.01), 3),
                "confidence": 0.0,
                "interpolated": True,
            }

    # --- Extrapolate after last anchor ---
    last_pos = anchor_positions[-1]
    if last_pos < n - 1:
        anchor_end = result[last_pos]["end"]
        for k, lpos in enumerate(range(last_pos + 1, n)):
            s = anchor_end + k * per_word
            e = s + per_word * 0.8
            result[lpos] = {
                "word": lyrics_words[lpos],
                "start": round(s, 3),
                "end": round(min(e, audio_duration), 3),
                "confidence": 0.0,
                "interpolated": True,
            }

    # Fill any remaining None slots
    for i in range(n):
        if result[i] is None:
            result[i] = {
                "word": lyrics_words[i],
                "start": 0.0,
                "end": 0.1,
                "confidence": 0.0,
                "interpolated": True,
            }

    return result


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def align_with_anchors(asr_json_path: str,
                       lyrics_txt_path: str,
                       output_path: str = None,
                       audio_duration: float = None) -> dict:
    """
    Merge ASR anchors with full lyrics text to produce complete timestamps.
    Returns the updated synced_lyrics dict.
    """
    with open(asr_json_path) as f:
        asr_data = json.load(f)

    with open(lyrics_txt_path) as f:
        lyrics_text = f.read()

    asr_words = asr_data.get("word_timestamps", [])
    # Filter to only words that have real timestamps
    asr_anchors = [w for w in asr_words
                   if w.get("start") is not None and w.get("end") is not None
                   and not w.get("interpolated", False)]

    lyrics_words = _tokenise_lyrics(lyrics_text)

    if audio_duration is None:
        if asr_anchors:
            audio_duration = asr_anchors[-1]["end"] + 5.0
        else:
            audio_duration = 300.0

    print(f"Lyrics words: {len(lyrics_words)}")
    print(f"ASR anchor words: {len(asr_anchors)}")
    print(f"Audio duration: {audio_duration:.1f}s")

    # Align ASR words to lyrics positions (time-based positioning)
    raw_matches = _align_sequences(lyrics_words, asr_anchors, audio_duration)

    # Convert (lyrics_idx, asr_idx) to (lyrics_idx, asr_word_dict)
    anchors = [(lpos, asr_anchors[ai]) for lpos, ai in raw_matches]

    print(f"Matched anchors: {len(anchors)} of {len(asr_anchors)} ASR words")

    # Build complete word list with interpolated timestamps
    complete_words = _interpolate(lyrics_words, anchors, audio_duration)

    anchored = sum(1 for w in complete_words if not w.get("interpolated", False))
    interpolated = len(complete_words) - anchored

    print(f"Output: {len(complete_words)} words "
          f"({anchored} anchored, {interpolated} interpolated)")

    # Verify timestamps are monotonically increasing
    prev_start = -1
    out_of_order = 0
    for w in complete_words:
        if w["start"] < prev_start:
            out_of_order += 1
        prev_start = w["start"]
    if out_of_order:
        print(f"WARNING: {out_of_order} out-of-order timestamps detected")

    # Build output
    result = dict(asr_data)
    result["word_timestamps"] = complete_words
    result["raw_lyrics"] = " ".join(w["word"] for w in complete_words)
    result["alignment_stats"] = {
        "total_words": len(complete_words),
        "aligned_words": anchored,
        "unaligned_words": interpolated,
        "quality": (
            "EXCELLENT" if anchored / max(len(complete_words), 1) > 0.8
            else "GOOD" if anchored / max(len(complete_words), 1) > 0.5
            else "FAIR"
        ),
        "method": "asr-anchored-interpolation",
    }

    out = output_path or asr_json_path
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote {out}")
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Fill ASR gaps using lyrics text interpolation"
    )
    parser.add_argument("asr_json", help="Path to ASR output JSON")
    parser.add_argument("lyrics_txt", help="Path to plain-text lyrics file")
    parser.add_argument("--output", "-o",
                        help="Output JSON path (default: overwrite asr_json)")
    parser.add_argument("--audio-duration", type=float,
                        help="Total audio duration in seconds")
    args = parser.parse_args()

    result = align_with_anchors(
        asr_json_path=args.asr_json,
        lyrics_txt_path=args.lyrics_txt,
        output_path=args.output,
        audio_duration=args.audio_duration,
    )

    words = result["word_timestamps"]
    stats = result["alignment_stats"]
    print(f"\n=== Summary ===")
    print(f"Total words: {stats['total_words']}")
    print(f"Anchored (ASR): {stats['aligned_words']}")
    print(f"Interpolated: {stats['unaligned_words']}")
    print(f"Quality: {stats['quality']}")
    print(f"\n=== First 20 words ===")
    for w in words[:20]:
        flag = " [interp]" if w.get("interpolated") else ""
        print(f"  {w['start']:7.2f}s - {w['end']:7.2f}s  {w['word']}{flag}")
    print(f"\n=== Last 10 words ===")
    for w in words[-10:]:
        flag = " [interp]" if w.get("interpolated") else ""
        print(f"  {w['start']:7.2f}s - {w['end']:7.2f}s  {w['word']}{flag}")


if __name__ == "__main__":
    main()
