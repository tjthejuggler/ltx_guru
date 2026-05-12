#!/usr/bin/env python3
"""Generate bushes_of_love project files from synced lyrics."""

import json
import os
from datetime import datetime, timezone

PROJECT_DIR = "sequence_projects/bushes_of_love"
SYNCED_LYRICS = os.path.join(PROJECT_DIR, "bushes_of_love_synced_lyrics.json")
AUDIO_FILE = "sequence_maker/songs/Bushes of Love.mp3"
DURATION = 284.186122
SONG_TITLE = "Bushes of Love"
ARTIST = "Bad Lip Reading"

# Color scheme
COLOR_BLUE = [0, 0, 255]
COLOR_DARK_ORANGE = [165, 42, 0]    # ~65% brightness orange
COLOR_BRIGHT_ORANGE = [255, 165, 0]  # brightest orange
COLOR_BLACK = [0, 0, 0]
DEFAULT_PIXELS = 3
REFRESH_RATE = 50
LEAD_IN_SECONDS = 5.0


def load_synced_lyrics():
    with open(SYNCED_LYRICS, "r") as f:
        return json.load(f)


def interpolate_gaps(word_timestamps):
    """Fill in None start/end timestamps by linear interpolation."""
    # First pass: find aligned words before and after each gap
    result = list(word_timestamps)  # shallow copy

    # Collect gap ranges (sequences of unaligned words)
    gaps = []
    i = 0
    while i < len(result):
        if result[i]["start"] is None:
            # Find the extent of this gap
            gap_start_idx = i
            while i < len(result) and result[i]["start"] is None:
                i += 1
            gap_end_idx = i  # first aligned word after gap (or end)
            gaps.append((gap_start_idx, gap_end_idx))
        else:
            i += 1

    for gap_start_idx, gap_end_idx in gaps:
        # Find the last aligned word before the gap
        prev_time = 0.0
        for j in range(gap_start_idx - 1, -1, -1):
            if result[j]["start"] is not None:
                prev_time = result[j]["end"]
                break

        # Find the first aligned word after the gap
        next_time = DURATION
        if gap_end_idx < len(result) and result[gap_end_idx]["start"] is not None:
            next_time = result[gap_end_idx]["start"]

        # Distribute unaligned words evenly across the gap
        num_words = gap_end_idx - gap_start_idx
        if num_words > 0:
            span = next_time - prev_time
            word_duration = span / (num_words + 1)  # +1 for spacing
            for k, idx in enumerate(range(gap_start_idx, gap_end_idx)):
                start = round(prev_time + (k + 1) * word_duration - word_duration * 0.8, 3)
                end = round(prev_time + (k + 1) * word_duration, 3)
                # Ensure start < end and both are positive
                start = max(start, prev_time + k * 0.05)
                end = max(end, start + 0.05)
                result[idx] = dict(result[idx], start=start, end=end, case="interpolated")

    return result


def starts_with_b(word):
    """Check if word starts with letter B (case-insensitive)."""
    w = word.strip("',.!?\"()").lower()
    return len(w) > 0 and w[0] == 'b'


def generate_ball_json(synced):
    """Generate .ball.json with Ball 1: blue on B-words + dark orange lead-in."""
    wts = interpolate_gaps(synced["word_timestamps"])
    segments = []
    last_end = 0.0

    # Collect all B-word events with lead-ins
    events = []  # (start, end, color)
    for wt in wts:
        if wt["start"] is None:
            continue
        if starts_with_b(wt["word"]):
            lead_start = max(wt["start"] - LEAD_IN_SECONDS, 0.0)
            events.append((lead_start, wt["start"], COLOR_DARK_ORANGE))
            events.append((wt["start"], wt["end"], COLOR_BLUE))

    # Sort events by start time
    events.sort(key=lambda e: e[0])

    # Build segments: fill gaps with black, then insert events
    for ev_start, ev_end, color in events:
        if ev_start > last_end + 0.01:
            segments.append({
                "start_time": round(last_end, 3),
                "end_time": round(ev_start, 3),
                "color": COLOR_BLACK,
                "pixels": DEFAULT_PIXELS
            })
        segments.append({
            "start_time": round(ev_start, 3),
            "end_time": round(ev_end, 3),
            "color": color,
            "pixels": DEFAULT_PIXELS
        })
        last_end = max(last_end, ev_end)

    # Trailing black
    if last_end < DURATION:
        segments.append({
            "start_time": round(last_end, 3),
            "end_time": round(DURATION, 3),
            "color": COLOR_BLACK,
            "pixels": DEFAULT_PIXELS
        })

    return {
        "metadata": {
            "name": "bushes_of_love.ball",
            "default_pixels": DEFAULT_PIXELS,
            "refresh_rate": REFRESH_RATE,
            "total_duration": round(DURATION, 2),
            "audio_file": AUDIO_FILE
        },
        "segments": segments
    }


def generate_smproj(synced):
    """Generate .smproj with 3 ball timelines + lyrics."""
    now = datetime.now(timezone.utc).isoformat()
    wts = interpolate_gaps(synced["word_timestamps"])

    def make_ball1_timeline():
        """Ball 1: dark orange lead-in before B-words, blue during B-words, black otherwise."""
        segments = []
        last_end = 0.0

        events = []
        for wt in wts:
            if wt["start"] is None:
                continue
            if starts_with_b(wt["word"]):
                lead_start = max(wt["start"] - LEAD_IN_SECONDS, 0.0)
                events.append((lead_start, wt["start"], COLOR_DARK_ORANGE))
                events.append((wt["start"], wt["end"], COLOR_BLUE))

        events.sort(key=lambda e: e[0])

        for ev_start, ev_end, color in events:
            if ev_start > last_end + 0.01:
                segments.append({
                    "startTime": round(last_end, 3),
                    "endTime": round(ev_start, 3),
                    "color": COLOR_BLACK,
                    "pixels": DEFAULT_PIXELS,
                    "effects": [],
                    "segment_type": "solid"
                })
            segments.append({
                "startTime": round(ev_start, 3),
                "endTime": round(ev_end, 3),
                "color": color,
                "pixels": DEFAULT_PIXELS,
                "effects": [],
                "segment_type": "solid"
            })
            last_end = max(last_end, ev_end)

        if last_end < DURATION:
            segments.append({
                "startTime": round(last_end, 3),
                "endTime": round(DURATION, 3),
                "color": COLOR_BLACK,
                "pixels": DEFAULT_PIXELS,
                "effects": [],
                "segment_type": "solid"
            })

        return {
            "name": "Ball 1",
            "defaultPixels": DEFAULT_PIXELS,
            "created": now,
            "modified": now,
            "segments": segments
        }

    def make_solid_orange_timeline(ball_name):
        """Balls 2 & 3: solid bright orange for the entire song."""
        return {
            "name": ball_name,
            "defaultPixels": DEFAULT_PIXELS,
            "created": now,
            "modified": now,
            "segments": [{
                "startTime": 0.0,
                "endTime": round(DURATION, 3),
                "color": COLOR_BRIGHT_ORANGE,
                "pixels": DEFAULT_PIXELS,
                "effects": [],
                "segment_type": "solid"
            }]
        }

    # Build lyrics dict matching Lyrics.from_dict() schema
    lyrics_dict = {
        "song_name": SONG_TITLE,
        "artist_name": ARTIST,
        "lyrics_text": synced["raw_lyrics"],
        "word_timestamps": [
            {"word": wt["word"], "start": wt["start"], "end": wt["end"]}
            for wt in wts if wt["start"] is not None
        ]
    }

    return {
        "metadata": {
            "version": "0.1.0",
            "created": now,
            "modified": now,
            "name": SONG_TITLE.lower().replace(" ", "_"),
            "description": f"Sequence for {SONG_TITLE} by {ARTIST}"
        },
        "settings": {
            "defaultPixels": DEFAULT_PIXELS,
            "refreshRate": 1,
            "totalDuration": DURATION,
            "zoomLevel": 1.0
        },
        "keyMappings": {},
        "effects": {},
        "timelines": [
            make_ball1_timeline(),
            make_solid_orange_timeline("Ball 2"),
            make_solid_orange_timeline("Ball 3"),
        ],
        "lyrics": lyrics_dict
    }


def generate_seqdesign(synced):
    """Generate .seqdesign.json with effects timeline."""
    wts = interpolate_gaps(synced["word_timestamps"])
    effects = []

    for wt in wts:
        if wt["start"] is None:
            continue
        if starts_with_b(wt["word"]):
            lead_start = max(wt["start"] - LEAD_IN_SECONDS, 0.0)
            effects.append({
                "type": "SolidColor",
                "timing": {
                    "start_seconds": round(lead_start, 3),
                    "end_seconds": round(wt["start"], 3)
                },
                "params": {"color": COLOR_DARK_ORANGE}
            })
            effects.append({
                "type": "SolidColor",
                "timing": {
                    "start_seconds": round(wt["start"], 3),
                    "end_seconds": round(wt["end"], 3)
                },
                "params": {"color": COLOR_BLUE}
            })

    return {
        "metadata": {
            "version": "1.0.0",
            "title": f"{SONG_TITLE} - B-Word Highlights",
            "artist": ARTIST,
            "description": f"Blue on B-words with dark orange lead-in. Balls 2&3 solid orange.",
            "target_prg_refresh_rate": REFRESH_RATE,
            "default_pixels": DEFAULT_PIXELS,
            "audio_file": AUDIO_FILE
        },
        "effects_timeline": effects
    }


def generate_song_data(synced):
    """Generate song_data.json."""
    wts = interpolate_gaps(synced["word_timestamps"])
    return {
        "_version": "1.0",
        "_created": datetime.now(timezone.utc).isoformat(),
        "_last_updated": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "song_title": SONG_TITLE,
            "artist_name": ARTIST,
            "audio_file": "Bushes of Love.mp3",
            "duration_seconds": round(DURATION, 2),
            "genre": "Comedy/Parody"
        },
        "lyrics": {
            "raw_text": synced["raw_lyrics"],
            "raw_text_file": "lyrics.txt",
            "synced_lyrics_file": "bushes_of_love_synced_lyrics.json",
            "synced_lyrics_data": None,
            "word_count": len(wts)
        },
        "audio_analysis": {
            "analysis_report_file": None,
            "estimated_tempo": None,
            "time_signature": None,
            "key": None,
            "beats": None,
            "downbeats": None,
            "sections": None,
            "energy_profile": None,
            "onset_times": None,
            "spectral_features": None
        },
        "sequences": {}
    }


def main():
    synced = load_synced_lyrics()
    wts = interpolate_gaps(synced["word_timestamps"])
    aligned = sum(1 for w in wts if w["start"] is not None)
    print(f"Loaded {len(wts)} words ({aligned} after interpolation)")

    # Generate all files
    ball = generate_ball_json(synced)
    smproj = generate_smproj(synced)
    seqdesign = generate_seqdesign(synced)
    song_data = generate_song_data(synced)

    # Write files
    files = {
        "bushes_of_love.ball.json": ball,
        "bushes_of_love.smproj": smproj,
        "bushes_of_love.seqdesign.json": seqdesign,
        "song_data.json": song_data,
    }

    for fname, data in files.items():
        path = os.path.join(PROJECT_DIR, fname)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Wrote {path} ({os.path.getsize(path)} bytes)")

    # Count B-words for info
    b_words = [w for w in wts if w["start"] is not None and starts_with_b(w["word"])]
    print(f"\nB-words found: {len(b_words)}")
    for bw in b_words[:10]:
        print(f"  {bw['start']:7.2f}s - {bw['end']:7.2f}s  {bw['word']}")

    print(f"\nDone! Project files generated in {PROJECT_DIR}")


if __name__ == "__main__":
    main()
