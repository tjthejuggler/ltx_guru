#!/usr/bin/env python3
"""
Simple Lyrics Extraction Tool

This script provides a simplified workflow for extracting and aligning lyrics with audio.
It bypasses the song identification step and directly uses user-provided lyrics.

Usage:
    python -m roocode_sequence_designer_tools.extract_lyrics_simple audio_file lyrics_file output_file

Example:
    python -m roocode_sequence_designer_tools.extract_lyrics_simple song.mp3 lyrics.txt timestamps.json
"""

import os
import sys
import json
import argparse
import logging
import requests
import subprocess
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LyricsExtractor")

def ensure_gentle_running():
    """
    Ensure the Gentle server is running.
    
    Returns:
        bool: True if Gentle is running, False otherwise
    """
    logger.info("Checking if Gentle server is running...")
    
    try:
        response = requests.get("http://localhost:8765", timeout=2)
        if response.status_code == 200:
            logger.info("Gentle server is already running.")
            return True
    except Exception:
        logger.info("Gentle server is not running. Starting it now...")
    
    # Try to start the Gentle server
    try:
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        start_gentle_script = os.path.join(script_dir, "sequence_maker", "scripts", "start_gentle.py")
        
        if not os.path.exists(start_gentle_script):
            logger.error(f"Could not find start_gentle.py at {start_gentle_script}")
            return False
        
        logger.info(f"Running start_gentle.py from {start_gentle_script}")
        subprocess.run([sys.executable, start_gentle_script], check=True)
        
        # Check if it's running now
        response = requests.get("http://localhost:8765", timeout=2)
        if response.status_code == 200:
            logger.info("Gentle server started successfully.")
            return True
        else:
            logger.error("Failed to start Gentle server.")
            return False
    except Exception as e:
        logger.error(f"Error starting Gentle server: {e}")
        return False

def align_lyrics(audio_path, lyrics_path, output_path, song_title="Unknown Song", artist_name="Unknown Artist"):
    """
    Align lyrics with audio using the Gentle API.
    
    Args:
        audio_path: Path to the audio file
        lyrics_path: Path to the lyrics file
        output_path: Path to save the output JSON
        song_title: Title of the song
        artist_name: Name of the artist
    
    Returns:
        bool: Success status
    """
    logger.info(f"Aligning audio: {audio_path}")
    logger.info(f"Using lyrics from: {lyrics_path}")
    
    # Ensure audio path is absolute
    audio_path = os.path.abspath(audio_path)
    
    # Verify the file exists
    if not os.path.exists(audio_path):
        logger.error(f"Audio file does not exist: {audio_path}")
        return False
    
    # Load the lyrics
    try:
        with open(lyrics_path, 'r') as f:
            lyrics_text = f.read()
        logger.info(f"Loaded lyrics ({len(lyrics_text)} characters)")
    except Exception as e:
        logger.error(f"Error loading lyrics: {e}")
        return False
    
    # Send request to Gentle
    try:
        logger.info("Opening audio file for Gentle alignment")
        
        with open(audio_path, 'rb') as audio_file:
            files = {
                'audio': audio_file,
                'transcript': (None, lyrics_text)
            }
            
            logger.info("Sending request to Gentle API with conservative alignment")
            
            # Always use conservative alignment for better results
            url = 'http://localhost:8765/transcriptions?async=false&conservative=true'
            
            response = requests.post(
                url,
                files=files,
                timeout=300  # 5 minutes timeout for longer audio files
            )
    except Exception as e:
        logger.error(f"Error during alignment: {e}")
        return False
    
    # Check if request was successful
    if response.status_code != 200:
        logger.error(f"Gentle API error: {response.status_code}")
        logger.error(response.text)
        return False
    
    # Parse response
    try:
        result = response.json()
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON response: {e}")
        logger.error("Response might not be JSON. Saving raw response to file.")
        with open("gentle_raw_response.txt", "w") as f:
            f.write(response.text)
        logger.error("Raw response saved to gentle_raw_response.txt")
        return False
    
    # Extract word timestamps
    word_timestamps = []
    
    for word in result.get('words', []):
        # Skip words without alignment
        if 'start' not in word or 'end' not in word:
            continue
        
        # Create word timestamp object
        word_timestamp = {
            'word': word.get('alignedWord', word.get('word', '')),
            'start': word.get('start', 0.0),
            'end': word.get('end', 0.0)
        }
        
        word_timestamps.append(word_timestamp)
    
    # Create the output data
    lyrics_data = {
        "song_title": song_title,
        "artist_name": artist_name,
        "raw_lyrics": lyrics_text,
        "word_timestamps": word_timestamps,
        "processing_status": {
            "song_identified": True,
            "lyrics_retrieved": True,
            "lyrics_aligned": len(word_timestamps) > 0,
            "user_assistance_needed": False,
            "message": "Lyrics aligned successfully."
        }
    }
    
    # Save to file
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(lyrics_data, f, indent=2)
        logger.info(f"Lyrics data saved to {output_path}")
    except Exception as e:
        logger.error(f"Error saving lyrics data: {e}")
        return False
    
    # Print summary
    word_count = len(word_timestamps)
    logger.info(f"Processed {word_count} words with timestamps.")
    
    if word_count > 0:
        logger.info("First few words with timestamps:")
        for i, word in enumerate(word_timestamps[:5]):
            logger.info(f"  {word['word']}: {word['start']:.2f}s - {word['end']:.2f}s")
    
    return True

def main():
    """Main function to parse arguments and align lyrics."""
    parser = argparse.ArgumentParser(description="Simple lyrics extraction and alignment tool.")
    parser.add_argument("audio_file", help="Path to the audio file")
    parser.add_argument("lyrics_file", help="Path to the lyrics file")
    parser.add_argument("output_file", help="Path to save the output JSON file")
    parser.add_argument("--song-title", default="Unknown Song", help="Title of the song")
    parser.add_argument("--artist-name", default="Unknown Artist", help="Name of the artist")
    
    args = parser.parse_args()
    
    # Ensure Gentle is running
    if not ensure_gentle_running():
        logger.error("Failed to ensure Gentle server is running. Exiting.")
        sys.exit(1)
    
    # Align lyrics
    success = align_lyrics(
        args.audio_file,
        args.lyrics_file,
        args.output_file,
        args.song_title,
        args.artist_name
    )
    
    if success:
        logger.info("Lyrics alignment completed successfully!")
        sys.exit(0)
    else:
        logger.error("Lyrics alignment failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()