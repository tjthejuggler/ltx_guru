# Lyrics Extraction and Alignment Guide

*Last updated: 2026-05-04 11:30:00*

This guide explains how to extract and align lyrics with audio files to generate precise word-level timestamps. These timestamps can be used for creating synchronized light sequences that match lyrics in songs.

---

## Two Pipelines: Choose Based on Whether You Have Lyrics

| Situation | Pipeline | Tools |
|-----------|----------|-------|
| **No lyrics available** — transcribe from audio only | **ASR-only** | `transcribe_lyrics.py` |
| **Lyrics provided** — use them as ground truth | **Ground-truth alignment** | `align_lyrics_gentle.py` (Gentle forced alignment) |

---

## Pipeline 1: ASR-Only (no lyrics provided)

**Use [`transcribe_lyrics.py`](../transcribe_lyrics.py) when you do NOT have the lyrics text.** This tool uses Deepgram Nova-3 via ppq.ai to transcribe the audio directly, producing per-word timestamps from what the singer actually sang. No Docker, no Gentle, no alignment step needed.

```bash
source ltx_guru/bin/activate
python3 roocode_sequence_designer_tools/transcribe_lyrics.py \
  "path/to/song.mp3" \
  --output "sequence_projects/my_song/my_song_synced_lyrics.json" \
  --song-title "Song Title" \
  --artist-name "Artist Name"
```

**Line breaks in `raw_lyrics` (ASR-only):** The `raw_lyrics` field uses `_build_raw_lyrics()` to insert `\n` whenever the gap between consecutive ASR words is ≥ 1.5 s (`LINE_BREAK_GAP = 1.5`). This produces human-readable, line-separated lyrics that match the natural phrasing of the song as detected from silence gaps.

**Output format:**
```json
{
  "word_timestamps": [{"word": "you", "start": 20.64, "end": 20.96, "confidence": 0.98}, ...],
  "raw_lyrics": "You got a fast car\nI want a ticket to anywhere\n...",
  "transcription_source": "deepgram-nova3",
  "alignment_stats": {"total_words": 480, "aligned_words": 480, "unaligned_words": 0, "quality": "EXCELLENT"}
}
```

**Known limitation:** The Whisper backend consistently skips ~9-second sections at specific absolute positions in some songs (e.g. instrumental breaks). These gaps appear at the same timestamps regardless of chunk size or overlap — they are an inherent ASR limitation, not a bug in the tool.

**Note:** The ASR transcribes what the singer actually sang, which may differ from the written lyrics (improvised lines, repeated choruses, etc.). This is correct behaviour — the timestamps reflect the real audio.

---

## Pipeline 2: Ground-Truth Alignment (lyrics provided)

**Use this pipeline when you have the full lyrics text and want timestamps for every word.** Gentle forced alignment takes the known lyrics and the audio, then finds the precise timestamp for every word — no ASR step needed.

**Requirements:** Gentle server must be running (`curl http://localhost:8765` should return a response). Gentle runs as a Docker container.

### Step 1 — Save the lyrics

Save the clean lyrics to a text file (no section labels like `[Verse 1]`, no timestamps). **Preserve the original line breaks** — each line in the file becomes a line in `raw_lyrics`.

```
sequence_projects/my_song/lyrics.txt
```

### Step 2 — Run Gentle forced alignment

```bash
source ltx_guru/bin/activate
python3 roocode_sequence_designer_tools/align_lyrics_gentle.py \
  "path/to/song.mp3" \
  "sequence_projects/my_song/lyrics.txt" \
  --output "sequence_projects/my_song/my_song_synced_lyrics.json" \
  --song-title "Song Title" \
  --artist-name "Artist Name"
```

**Line breaks in `raw_lyrics` (ground-truth pipeline):** `align_lyrics_gentle.py` sets `raw_lyrics` directly from the input `lyrics.txt` file content. **The original line breaks from the lyrics file are preserved exactly.** This means the `raw_lyrics` field in the output will have the same line structure as the lyrics you provided — one lyric line per line.

**Output format:**
```json
{
  "word_timestamps": [
    {"word": "you", "start": 20.94, "end": 20.98},
    {"word": "got", "start": 20.98, "end": 21.09},
    ...
  ],
  "raw_lyrics": "You got a fast car\nI want a ticket to anywhere\nMaybe we make a deal\n...",
  "transcription_source": "gentle-forced-alignment",
  "alignment_stats": {"total_words": 511, "aligned_words": 479, "not_found": 32, "aligned_pct": 93.7, "quality": "EXCELLENT"}
}
```

Words not found in the audio are omitted from `word_timestamps` (Gentle only returns words it successfully aligned). The `raw_lyrics` field always contains the full original lyrics with line breaks intact.

**Quality benchmark (Fast Car, Tracy Chapman):** 479/511 words aligned (93.7%), 0 out-of-order timestamps, audio span 20.94s–275.86s.

---

## ⭐ Why Deepgram over Gentle

**API key:** stored at `sequence_maker/ppq_api_key.txt`

**Chunking strategy (2026-05-04):** Audio is split into **10-second chunks with 5-second overlap** (`DEFAULT_CHUNK_DURATION = 10`, `CHUNK_OVERLAP = 5`). Short chunks prevent the Whisper backend from skipping sung sections. The overlap ensures words near chunk boundaries are not dropped by the deduplication logic.

- Gentle forced-alignment requires Docker and a running server
- Gentle silently drops ~20–30% of words on sung music (singer improvises, words differ from written lyrics)
- Deepgram transcribes what is actually heard — 100% of words have timestamps, 0 out-of-order
- The output is the synced lyrics file directly — no post-processing needed

---

## Legacy: Gentle Forced Alignment (NOT recommended for sung music)

The tools below use [Gentle](https://github.com/lowerquality/gentle) forced alignment. **Do not use these for sung music** — Gentle silently rejects ~20–30% of words, producing large timestamp gaps. Only use Gentle for spoken-word audio where you need high-confidence-only timestamps.

### Important: do NOT use conservative alignment for sung music

Gentle has a "conservative" alignment mode that **silently rejects ~20–30 % of words on sung music**, leaving large gaps in the timeline (this is what produced the broken `fast_car_synced_lyrics.json` on 2026-05-04).

As of **2026-05-04** all three tools default to **non-conservative** alignment. You only need to opt in to conservative mode (via `--conservative` on `align_lyrics.py` and `extract_lyrics_simple.py`) for spoken-word audio where you specifically need high-confidence-only timestamps.

## Available Tools

The project provides several tools for lyrics extraction and alignment:

0. **transcribe_lyrics.py** ⭐ **(PREFERRED)** - Uses Deepgram Nova-3 via ppq.ai. No Docker needed. Transcribes what is actually sung. Direct output, no alignment step.

1. **align_lyrics.py** (Gentle, legacy) - Direct lyrics alignment tool that uses the Gentle API to generate precise word-level timestamps. Automatically ensures Gentle server is running and handles all alignment steps in one command. **Conservative mode is OFF by default.**

2. **extract_lyrics_simple.py** (Gentle, legacy) - Simplified tool for extracting lyrics timestamps using user-provided lyrics. Bypasses API requirements and automatically ensures Gentle server is running. **Conservative mode is OFF by default.**

3. **extract_lyrics.py** (Gentle, legacy) - Advanced tool that extracts and processes lyrics from audio files with options for time range filtering and formatting. Conservative mode is OFF by default.

## Prerequisites

- Python 3.6+
- ppq.ai API key at `sequence_maker/ppq_api_key.txt` (for Deepgram/transcribe_lyrics.py)
- Docker (only needed for Gentle-based tools — legacy)
- Audio file in a supported format (MP3, WAV, etc.)
- Lyrics text file (optional for Deepgram — used as prompt hint only)

## Quick Start Guide

### Method 1: Using align_lyrics.py (Recommended)

This is the most straightforward method and requires minimal setup:

1. Create a text file containing the lyrics of your song (e.g., `lyrics.txt`)

2. Run the alignment tool:
   ```bash
   python align_lyrics.py song.mp3 lyrics.txt timestamps.json --song-title "Song Title" --artist-name "Artist Name"
   ```

3. The tool will:
   - Automatically start the Gentle server if it's not running
   - Process the audio and lyrics
   - Generate a JSON file with word-level timestamps

### Method 2: Using extract_lyrics_simple.py

This method is useful if you're working within the roocode_sequence_designer_tools module:

1. Create a text file containing the lyrics of your song (e.g., `song.lyrics.txt`)

2. Run the extraction tool:
   ```bash
   python -m roocode_sequence_designer_tools.extract_lyrics_simple song.mp3 song.lyrics.txt song.synced_lyrics.json --song-title "Song Title" --artist-name "Artist Name"
   ```

### Method 3: Using extract_lyrics.py

This method provides more advanced options but requires more setup:

1. Create a text file containing the lyrics of your song (e.g., `song.lyrics.txt`)

2. Start the Gentle server:
   ```bash
   python -m sequence_maker.scripts.start_gentle
   ```

3. Run the extraction tool:
   ```bash
   python -m roocode_sequence_designer_tools.extract_lyrics song.mp3 --lyrics-file song.lyrics.txt --output song.synced_lyrics.json
   ```

   (Don't pass `--conservative` for sung music — it drops too many words. The flag still exists for spoken-word use cases.)

## Output Format

All tools generate a JSON file with the following structure:

```json
{
  "song_title": "Song Title",
  "artist_name": "Artist Name",
  "raw_lyrics": "Full lyrics text...",
  "word_timestamps": [
    {
      "word": "first",
      "start": 10.2,
      "end": 10.5,
      "case": "success"
    },
    {
      "word": "word",
      "start": 10.6,
      "end": 10.9,
      "case": "success"
    },
    {
      "word": "uh",
      "start": null,
      "end": null,
      "case": "not-found-in-audio"
    }
  ],
  "alignment_stats": {
    "total_words": 459,
    "aligned_words": 358,
    "not_found_in_audio": 101,
    "other_unaligned": 0,
    "aligned_percentage": 77.99,
    "quality": "GOOD",
    "conservative_mode": false
  },
  "processing_status": {
    "song_identified": true,
    "lyrics_retrieved": true,
    "lyrics_aligned": true,
    "user_assistance_needed": false,
    "message": "Lyrics aligned: 358/459 words (GOOD)."
  }
}
```

### Consumer guidance

When you read `word_timestamps`, **always check `start is None` (or `case != 'success'`)** before doing arithmetic. Older code that did `word['start']` unconditionally will need a tiny update:

```python
for w in data['word_timestamps']:
    if w['start'] is None:
        continue                  # un-aligned word — skip or interpolate
    use(w['word'], w['start'], w['end'])
```

## Troubleshooting

### Gentle Server Issues

If you encounter issues with the Gentle server:

1. Ensure Docker is installed and running
2. Try starting the Gentle server manually:
   ```bash
   python -m sequence_maker.scripts.start_gentle
   ```
3. Check if the server is running by visiting http://localhost:8765 in your browser

### Alignment Issues

If the alignment quality is poor (look at `alignment_stats.quality` in the output JSON, or the warning log line):

1. Ensure your lyrics text matches the **actual sung lyrics** as closely as possible (Gentle is sensitive to filler words like "yeah" and ad-libs that aren't in the printed lyrics).
2. **Do NOT enable `--conservative`** for sung music. It will silently drop a large fraction of words.
3. Check that your audio file is clear and of good quality. Heavy backing vocals, mumbling, or lossy compression all reduce alignment rate.
4. For songs with rapid lyrics, consider breaking the alignment into smaller sections.
5. If a specific section refuses to align, transcribe just that section verbatim (including ad-libs and repeats) and re-run.

## Advanced Usage

### Time Range Filtering

You can extract lyrics for a specific time range using the extract_lyrics.py tool:

```bash
python -m roocode_sequence_designer_tools.extract_lyrics song.mp3 --lyrics-file lyrics.txt --output timestamps.json --start-time 30 --end-time 60
```

### Formatting Options

The extract_lyrics.py tool provides options for formatted output:

```bash
python -m roocode_sequence_designer_tools.extract_lyrics song.mp3 --lyrics-file lyrics.txt --format-text --include-timestamps
```

## Integration with Light Sequences

The word timestamps can be used to create synchronized light effects that match the lyrics. For example:

1. Extract lyrics timestamps using one of the methods above
2. Use the timestamps to create pulse effects that trigger on specific words
3. Create color changes that match different sections of the lyrics

Example of using lyrics timestamps in a sequence design:

```json
{
  "effects": [
    {
      "type": "pulse_on_beat",
      "start_time": 0,
      "end_time": 180,
      "parameters": {
        "color": {"r": 255, "g": 0, "b": 0},
        "beat_source": "custom_times: [10.7, 11.04, 11.36, ...]",
        "pulse_duration_seconds": 0.3
      }
    }
  ]
}
```

## Further Resources

- [Gentle Forced Aligner](https://github.com/lowerquality/gentle)
- [Audio Analysis Guide](audio_analysis_report_tool.md)
- [Sequence Design Guide](roocode_user_guide_sequence_design.md)