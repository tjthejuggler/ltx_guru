# Lyrics Processing in Sequence Maker

This document explains how to extract and align lyrics with audio files in Sequence Maker.

## Overview

The lyrics processing feature allows you to align lyrics to your audio files, generating word-level timestamps that can be used in sequence designs. This document provides a **simplified workflow** that bypasses the complex API setup.

## Prerequisites

- Docker installed on your system (for running Gentle)
- The audio file you want to process
- The lyrics text for the song

## Quick Start Guide

### Step 1: Start the Gentle Server

The Gentle server must be running before attempting to process lyrics:

```bash
python -m sequence_maker.scripts.start_gentle
```

This script will:
- Check if Docker is installed and running
- Start the Gentle Docker container if it's not already running
- Verify that the Gentle API is accessible

### Step 2: Prepare Your Lyrics

Create a text file containing the complete lyrics of the song. For example, `lyrics.txt`:

```
You know me
Anytime you hit me it's just not a good time
Guess there's always something, they say that's a good sign
...
```

### Step 3: Extract Lyrics Timestamps

Use our simplified extraction tool:

```bash
python -m roocode_sequence_designer_tools.extract_lyrics_simple song.mp3 lyrics.txt output.synced_lyrics.json
```

This will:
1. Ensure the Gentle server is running
2. Align the lyrics with the audio
3. Save the word-level timestamps to the output file

### Step 4: Use the Timestamps

The output JSON file contains word-level timestamps that can be used in your sequence designs:

```json
{
  "song_title": "Song Title",
  "artist_name": "Artist Name",
  "word_timestamps": [
    {
      "word": "you",
      "start": 10.7,
      "end": 11.03
    },
    {
      "word": "know",
      "start": 11.04,
      "end": 11.33
    },
    ...
  ]
}
```

This file will be saved with the `.synced_lyrics.json` extension to follow the standardized naming convention.

## Detailed Usage

### Command-Line Options

The `extract_lyrics_simple.py` tool accepts the following parameters:

```bash
python -m roocode_sequence_designer_tools.extract_lyrics_simple [audio_file] [lyrics_file] [output_file.synced_lyrics.json] [options]
```

Options:
- `--song-title "Song Title"`: Specify the song title (default: "Unknown Song")
- `--artist-name "Artist Name"`: Specify the artist name (default: "Unknown Artist")

### Alternative Approaches

If you prefer to use the original extraction tool with more options:

```bash
python -m roocode_sequence_designer_tools.extract_lyrics [audio_file] --lyrics-file [lyrics_file.lyrics.txt] --output [output_file.synced_lyrics.json] --conservative
```

The `--conservative` flag is crucial for successful alignment and should always be used when providing your own lyrics.

## Troubleshooting

### Docker Issues

If you encounter issues with Docker:

1. Make sure Docker is installed and running
2. Try starting the Gentle server manually:
   ```
   python -m sequence_maker.scripts.start_gentle
   ```
3. If that fails, try running the Gentle container directly:
   ```
   docker run -p 8765:8765 lowerquality/gentle
   ```
4. Check if you can access the Gentle API at http://localhost:8765

### Lyrics Alignment Issues

If lyrics are not aligning properly:

1. Make sure the Gentle server is running (check http://localhost:8765)
2. Ensure the lyrics text exactly matches the audio (including all verses, choruses, etc.)
3. Check that the audio quality is good enough for alignment
4. For very challenging audio, you might need to manually adjust timestamps

## Advanced: API-Based Workflow (Optional)

For users who want to use the automatic song identification and lyrics retrieval features, you'll need to set up API keys:

1. **ACRCloud** (for song identification)
   - Sign up at [https://console.acrcloud.com/signup](https://console.acrcloud.com/signup)
   - Create a project and get your Access Key, Secret Key, and Host URL

2. **Genius API** (for lyrics retrieval)
   - Sign up at [https://docs.genius.com/](https://docs.genius.com/)
   - Generate an API Token from the dashboard

3. Create a file named `api_keys.json` in the `~/.ltx_sequence_maker/` directory:
   ```json
   {
       "acr_access_key": "YOUR_ACR_ACCESS_KEY",
       "acr_secret_key": "YOUR_ACR_SECRET_KEY",
       "acr_host": "YOUR_ACR_HOST",
       "genius_api_key": "YOUR_GENIUS_API_KEY"
   }
   ```

4. Use the standard extraction tool:
   ```
   python -m roocode_sequence_designer_tools.extract_lyrics path/to/audio.mp3 --output lyrics_data.synced_lyrics.json
   ```

## File Naming Conventions

To maintain consistency across the LTX Guru ecosystem, please use these standardized file extensions:

| File Type | Extension | Example |
|-----------|-----------|---------|
| Raw Lyrics | `.lyrics.txt` | `song_name.lyrics.txt` |
| Timestamped Lyrics | `.synced_lyrics.json` | `song_name.synced_lyrics.json` |

Using these standardized extensions helps ensure compatibility with all tools in the ecosystem.

## Privacy and Data Usage

- Your audio files are processed locally and are not uploaded to any external service except for song identification (if using the API-based workflow)
- Small audio samples may be sent to ACRCloud for song identification (if using the API-based workflow)
- Lyrics are fetched from Genius based on the identified song (if using the API-based workflow)
- No personal data is collected or stored