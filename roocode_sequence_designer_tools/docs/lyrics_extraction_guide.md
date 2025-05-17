# Lyrics Extraction and Alignment Guide

This guide explains how to extract and align lyrics with audio files to generate precise word-level timestamps. These timestamps can be used for creating synchronized light sequences that match lyrics in songs.

## Available Tools

The project provides several tools for lyrics extraction and alignment:

1. **align_lyrics.py** (Recommended) - Direct lyrics alignment tool that uses the Gentle API to generate precise word-level timestamps. Automatically ensures Gentle server is running and handles all alignment steps in one command.

2. **extract_lyrics_simple.py** - Simplified tool for extracting lyrics timestamps using user-provided lyrics. Bypasses API requirements and automatically ensures Gentle server is running.

3. **extract_lyrics.py** - Advanced tool that extracts and processes lyrics from audio files with options for time range filtering and formatting.

## Prerequisites

- Python 3.6+
- Docker (for running the Gentle forced alignment server)
- Audio file in a supported format (MP3, WAV, etc.)
- Lyrics text file

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
   python -m roocode_sequence_designer_tools.extract_lyrics song.mp3 --lyrics-file song.lyrics.txt --output song.synced_lyrics.json --conservative
   ```

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
      "end": 10.5
    },
    {
      "word": "word",
      "start": 10.6,
      "end": 10.9
    },
    ...
  ],
  "processing_status": {
    "song_identified": true,
    "lyrics_retrieved": true,
    "lyrics_aligned": true,
    "user_assistance_needed": false,
    "message": "Lyrics aligned successfully."
  }
}
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

If the alignment quality is poor:

1. Ensure your lyrics text matches the actual sung lyrics as closely as possible
2. Try using the `--conservative` flag (or avoid `--no-conservative` with align_lyrics.py) for more accurate but potentially fewer alignments
3. Check that your audio file is clear and of good quality
4. For songs with rapid lyrics, consider breaking the alignment into smaller sections

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