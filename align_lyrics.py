#!/usr/bin/env python3
"""
Lyrics Alignment Tool

This script aligns lyrics with audio files using the Gentle forced alignment API.
It automatically ensures the Gentle server is running and provides timestamps for each word.

Usage:
    python align_lyrics.py <audio_file> <lyrics_file> <output_file> [--song-title "Song Title"] [--artist-name "Artist Name"] [--no-conservative]

Example:
    python align_lyrics.py song.mp3 lyrics.txt timestamps.json --song-title "My Song" --artist-name "My Artist"
"""

import os
import sys
import json
import requests
import time
import argparse
from pathlib import Path

def check_gentle_server():
    """Check if the Gentle server is running."""
    try:
        response = requests.get("http://localhost:8765", timeout=2)
        if response.status_code == 200:
            print("Gentle server is running.")
            return True
        else:
            print(f"Gentle server returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error connecting to Gentle server: {e}")
        return False

def align_lyrics(audio_path, lyrics_path, output_path, conservative=True):
    """
    Align lyrics with audio using the Gentle API.
    
    Args:
        audio_path: Path to the audio file
        lyrics_path: Path to the lyrics file
        output_path: Path to save the output JSON
        conservative: Whether to use conservative alignment
    
    Returns:
        bool: Success status
    """
    print(f"Aligning audio: {audio_path}")
    print(f"Using lyrics from: {lyrics_path}")
    
    # Check if the Gentle server is running
    if not check_gentle_server():
        print("Gentle server is not running. Please start it first.")
        return False
    
    # Load the lyrics
    try:
        with open(lyrics_path, 'r') as f:
            lyrics_text = f.read()
        print(f"Loaded lyrics ({len(lyrics_text)} characters)")
    except Exception as e:
        print(f"Error loading lyrics: {e}")
        return False
    
    # Ensure audio path is absolute
    audio_path = os.path.abspath(audio_path)
    
    # Verify the file exists
    if not os.path.exists(audio_path):
        print(f"Audio file does not exist: {audio_path}")
        return False
    
    # Send request to Gentle
    try:
        print("Opening audio file for Gentle alignment")
        
        with open(audio_path, 'rb') as audio_file:
            files = {
                'audio': audio_file,
                'transcript': (None, lyrics_text)
            }
            
            print("Sending request to Gentle API")
            
            # Build the URL with parameters
            url = 'http://localhost:8765/transcriptions?async=false'
            if conservative:
                url += '&conservative=true'
                print("Using conservative alignment mode")
            
            response = requests.post(
                url,
                files=files,
                timeout=120  # Increase timeout to 2 minutes
            )
    except FileNotFoundError as e:
        print(f"Error opening audio file: {e}")
        return False
    except requests.RequestException as e:
        print(f"Error communicating with Gentle API: {e}")
        return False
    
    # Check if request was successful
    if response.status_code != 200:
        print(f"Gentle API error: {response.status_code}")
        print(response.text)
        return False
    
    # Parse response
    try:
        result = response.json()
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print("Response might not be JSON. Saving raw response to file.")
        with open("gentle_raw_response.txt", "w") as f:
            f.write(response.text)
        print("Raw response saved to gentle_raw_response.txt")
        return False
    
    # Extract word timestamps
    word_timestamps = []
    
    for word in result.get('words', []):
        # Skip words without alignment
        if 'start' not in word or 'end' not in word:
            continue
        
        # Create word timestamp object
        word_timestamp = {
            'word': word.get('alignedWord', ''),
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
        with open(output_path, 'w') as f:
            json.dump(lyrics_data, f, indent=2)
        print(f"Lyrics data saved to {output_path}")
    except Exception as e:
        print(f"Error saving lyrics data: {e}")
        return False
    
    # Print summary
    word_count = len(word_timestamps)
    print(f"\nProcessed {word_count} words with timestamps.")
    
    if word_count > 0:
        print("\nFirst few words with timestamps:")
        for i, word in enumerate(word_timestamps[:5]):
            print(f"  {word['word']}: {word['start']:.2f}s - {word['end']:.2f}s")
    
    return True

def start_gentle_server():
    """
    Attempt to start the Gentle server if it's not already running.
    
    Returns:
        bool: True if server is running or was started successfully, False otherwise
    """
    if check_gentle_server():
        return True
        
    print("Attempting to start Gentle server...")
    try:
        # Try to find and run the start_gentle.py script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        
        # Check common locations for the start_gentle.py script
        possible_paths = [
            os.path.join(project_dir, "sequence_maker", "scripts", "start_gentle.py"),
            os.path.join(project_dir, "scripts", "start_gentle.py"),
            os.path.join(script_dir, "start_gentle.py")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found start_gentle.py at {path}")
                result = os.system(f"{sys.executable} {path}")
                if result == 0 and check_gentle_server():
                    print("Successfully started Gentle server")
                    return True
        
        print("Could not find or start the Gentle server")
        return False
    except Exception as e:
        print(f"Error starting Gentle server: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Align lyrics with audio using Gentle forced alignment")
    parser.add_argument("audio_file", help="Path to the audio file")
    parser.add_argument("lyrics_file", help="Path to the lyrics text file")
    parser.add_argument("output_file", help="Path to save the output JSON file with timestamps")
    parser.add_argument("--song-title", default=None, help="Title of the song")
    parser.add_argument("--artist-name", default=None, help="Name of the artist")
    parser.add_argument("--no-conservative", action="store_true", help="Disable conservative alignment mode")
    
    args = parser.parse_args()
    
    # Determine song title and artist name from filename if not provided
    song_title = args.song_title
    artist_name = args.artist_name
    
    if song_title is None or artist_name is None:
        # Try to extract from filename
        filename = os.path.basename(args.audio_file)
        name_parts = os.path.splitext(filename)[0].split('_')
        
        if len(name_parts) >= 2 and song_title is None:
            song_title = ' '.join(name_parts[:-1]).title()
        elif song_title is None:
            song_title = name_parts[0].title()
            
        if artist_name is None and len(name_parts) >= 2:
            artist_name = name_parts[-1].title()
        elif artist_name is None:
            artist_name = "Unknown Artist"
    
    # Ensure the Gentle server is running
    if not start_gentle_server():
        print("Error: Gentle server is required for lyrics alignment")
        sys.exit(1)
    
    # Check if files exist
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file not found: {args.audio_file}")
        sys.exit(1)
    
    if not os.path.exists(args.lyrics_file):
        print(f"Error: Lyrics file not found: {args.lyrics_file}")
        sys.exit(1)
    
    # Run alignment
    conservative = not args.no_conservative
    success = align_lyrics(args.audio_file, args.lyrics_file, args.output_file, conservative=conservative)
    
    if success:
        print("\nLyrics alignment completed successfully!")
    else:
        print("\nLyrics alignment failed.")