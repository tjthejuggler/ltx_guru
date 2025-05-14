#!/usr/bin/env python3
"""
Direct lyrics alignment script for "You Know Me" by Lubalin.
This script uses the same approach as the LyricsManager class in sequence_maker.
"""

import os
import sys
import json
import requests
import time
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
        "song_title": "You Know Me",
        "artist_name": "Lubalin",
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

if __name__ == "__main__":
    audio_path = "sequence_projects/you_know_me/lubalin_you_know_me.mp3"
    lyrics_path = "you_know_me_lyrics.txt"
    output_path = "you_know_me_lyrics_timestamps.json"
    
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found: {audio_path}")
        sys.exit(1)
    
    if not os.path.exists(lyrics_path):
        print(f"Error: Lyrics file not found: {lyrics_path}")
        sys.exit(1)
    
    success = align_lyrics(audio_path, lyrics_path, output_path, conservative=True)
    
    if success:
        print("\nLyrics alignment completed successfully!")
    else:
        print("\nLyrics alignment failed.")