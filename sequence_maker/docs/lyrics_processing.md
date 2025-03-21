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

1. Create a directory at `~/.sequence_maker/` if it doesn't exist
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

The first time you process lyrics, Sequence Maker will automatically pull and run the Gentle Docker container. This may take a few minutes depending on your internet connection.

#### Docker Troubleshooting

If you encounter Docker-related errors when processing lyrics:

1. Verify Docker is installed by running `docker --version` in a terminal.
2. Ensure Docker is running (check for the Docker icon in your system tray or menu bar).
3. Make sure you have permission to run Docker (on Linux, your user may need to be in the `docker` group).
4. If using Docker Desktop, check its status in the Docker Desktop dashboard.

## Usage

1. Load an audio file in Sequence Maker
2. Click on the "Process Lyrics" button in the Lyrics widget or select "Process Lyrics" from the Tools menu
3. Wait for the processing to complete (this may take a few minutes)
4. Once processing is complete, the lyrics will be displayed in the Lyrics widget
5. The lyrics will be synchronized with the audio playback, highlighting the current word

## Troubleshooting

### Missing API Keys

If you see an error about missing API keys, make sure you've created the `api_keys.json` file as described in the Configuration section.

### Docker Issues

If you encounter issues with Docker:

1. Make sure Docker is installed and running
2. Try running the Gentle container manually:
   ```
   docker run -p 8765:8765 lowerquality/gentle
   ```
3. Check if you can access the Gentle API at http://localhost:8765

### Song Identification Issues

If the song cannot be identified:

1. The application will prompt you to manually input the lyrics
2. A dialog will appear where you can paste or type the lyrics
3. After submitting the lyrics, the application will continue with the alignment process
4. If you prefer automatic identification, make sure your ACRCloud API keys are correct
5. Try a different audio file with clearer audio quality
6. Make sure the song is in the ACRCloud database (popular songs are more likely to be recognized)

### Lyrics Retrieval Issues

If lyrics cannot be retrieved:

1. Make sure your Genius API key is correct
2. Check if the song has lyrics available on Genius
3. Try a different song

## Privacy and Data Usage

- Your audio files are processed locally and are not uploaded to any external service except for song identification
- Small audio samples may be sent to ACRCloud for song identification
- Lyrics are fetched from Genius based on the identified song
- No personal data is collected or stored