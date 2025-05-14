# Lyrics Processing in Sequence Maker

This document explains how to set up and use the lyrics processing feature in Sequence Maker.

## Overview

The lyrics processing feature allows you to automatically extract and align lyrics to your audio files. This is done through a pipeline that:

1. Identifies the song using ACRCloud's audio recognition service
2. Fetches the lyrics using the Genius API
3. Aligns the lyrics to the audio using Gentle (a forced aligner)
4. Displays the aligned lyrics in the Sequence Maker interface

## Setup

### Prerequisites

- Docker installed on your system (for running Gentle)
- API keys for ACRCloud and Genius

### API Keys

You need to obtain API keys for the following services:

1. **ACRCloud** (for song identification)
   - Sign up at [https://console.acrcloud.com/signup](https://console.acrcloud.com/signup)
   - Create a project and get your Access Key, Secret Key, and Host URL

2. **Genius API** (for lyrics retrieval)
   - Sign up at [https://docs.genius.com/](https://docs.genius.com/)
   - Generate an API Token from the dashboard

### Configuration

1. Create a directory at `~/.ltx_sequence_maker/` if it doesn't exist
2. Create a file named `api_keys.json` in that directory with the following content:

```json
{
    "acr_access_key": "YOUR_ACR_ACCESS_KEY",
    "acr_secret_key": "YOUR_ACR_SECRET_KEY",
    "acr_host": "YOUR_ACR_HOST",
    "genius_api_key": "YOUR_GENIUS_API_KEY"
}
```

3. Replace the placeholder values with your actual API keys

### Python Dependencies

The lyrics processing feature requires the following Python packages:
- requests
- lyricsgenius

You can install them using pip:
```
pip install requests lyricsgenius
```

### Docker Setup

The lyrics processing feature uses Gentle for word-level alignment, which runs in a Docker container. **Docker must be installed and running on your system** for the lyrics alignment to work.

#### Docker Installation

1. **Install Docker**:
   - For Windows: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
   - For macOS: [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
   - For Linux: [Docker Engine](https://docs.docker.com/engine/install/)

2. **Ensure Docker is running** before attempting to process lyrics.

3. **Make sure Docker is in your PATH**:
   - The application needs to be able to execute the `docker` and `docker-compose` commands.
   - If you installed Docker Desktop, this should be configured automatically.

#### Starting the Gentle Server

**CRITICAL**: The Gentle server must be running before attempting to process lyrics. There are two ways to start it:

1. **Automatic start**: The first time you process lyrics in the Sequence Maker GUI, it will attempt to start the Gentle server automatically.

2. **Manual start (recommended)**: For more reliable operation, start the Gentle server manually before processing lyrics:
   ```
   python -m sequence_maker.scripts.start_gentle
   ```
   This script will:
   - Check if Docker is installed and running
   - Start the Gentle Docker container if it's not already running
   - Verify that the Gentle API is accessible

Starting the server manually is especially important when using command-line tools or when troubleshooting alignment issues.

#### Docker Troubleshooting

If you encounter Docker-related errors when processing lyrics:

1. Verify Docker is installed by running `docker --version` in a terminal.
2. Ensure Docker is running (check for the Docker icon in your system tray or menu bar).
3. Make sure you have permission to run Docker (on Linux, your user may need to be in the `docker` group).
4. If using Docker Desktop, check its status in the Docker Desktop dashboard.
5. Check if the Gentle server is running by opening http://localhost:8765 in a web browser.

## Usage

### GUI Usage

1. Load an audio file in Sequence Maker
2. Click on the "Process Lyrics" button in the Lyrics widget or select "Process Lyrics" from the Tools menu
3. Wait for the processing to complete (this may take a few minutes)
4. Once processing is complete, the lyrics will be displayed in the Lyrics widget
5. The lyrics will be synchronized with the audio playback, highlighting the current word

### Command-Line Usage

For more control or batch processing, you can use the command-line tools directly:

#### Optimized Workflow for Lyrics Extraction

1. **Start the Gentle server** (if not already running):
   ```
   python -m sequence_maker.scripts.start_gentle
   ```

2. **Check if you have API keys configured**:
   If you see messages like "API keys file not found" or "Missing ACRCloud API keys", automatic song identification won't work. Skip directly to step 4.

3. **Try automatic lyrics extraction**:
   ```
   python -m roocode_sequence_designer_tools.extract_lyrics path/to/audio.mp3 --output lyrics_data.json
   ```

4. **If automatic extraction fails, save lyrics to a text file**:
   Create a file (e.g., `lyrics.txt`) containing the complete lyrics text.

5. **Run extraction with conservative alignment**:
   ```
   python -m roocode_sequence_designer_tools.extract_lyrics path/to/audio.mp3 --lyrics-file lyrics.txt --output lyrics_timestamps.json --conservative
   ```
   The `--conservative` flag is crucial for successful alignment and should always be used when providing your own lyrics.

6. **Check the results**:
   The output JSON file will contain word-level timestamps that can be used in your sequence designs.

## Troubleshooting

### Missing API Keys

If you see an error about missing API keys:
1. Make sure you've created the `api_keys.json` file as described in the Configuration section.
2. If you don't have API keys, you can still use the lyrics processing feature by providing the lyrics text manually.

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

### Song Identification Issues

If the song cannot be identified:

1. The application will prompt you to manually input the lyrics
2. A dialog will appear where you can paste or type the lyrics
3. After submitting the lyrics, the application will continue with the alignment process
4. If you prefer automatic identification, make sure your ACRCloud API keys are correct
5. Try a different audio file with clearer audio quality
6. Make sure the song is in the ACRCloud database (popular songs are more likely to be recognized)

### Lyrics Alignment Issues

If lyrics are not aligning properly:

1. Make sure the Gentle server is running (check http://localhost:8765)
2. Try using the `--conservative` flag when running the extract_lyrics.py tool
3. Ensure the lyrics text exactly matches the audio (including all verses, choruses, etc.)
4. Check that the audio quality is good enough for alignment
5. For very challenging audio, you might need to manually adjust timestamps

## Privacy and Data Usage

- Your audio files are processed locally and are not uploaded to any external service except for song identification
- Small audio samples may be sent to ACRCloud for song identification
- Lyrics are fetched from Genius based on the identified song
- No personal data is collected or stored