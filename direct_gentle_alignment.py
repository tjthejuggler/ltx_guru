#!/usr/bin/env python3
"""
Direct Gentle API alignment script.
This script bypasses the sequence_maker tools and directly uses the Gentle API.
It now accepts command-line arguments for generic use.
"""

import os
import sys
import json
import requests
import argparse # Added argparse
from pathlib import Path

def align_with_gentle(audio_path, lyrics_path, output_path, song_title="Unknown Song", artist_name="Unknown Artist", conservative=True):
    """
    Directly align lyrics with audio using the Gentle API.
    
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
    try:
        response = requests.get("http://localhost:8765", timeout=2)
        if response.status_code != 200:
            print(f"Gentle server returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error connecting to Gentle server: {e}")
        return False
    
    # Load the lyrics
    try:
        with open(lyrics_path, 'r') as f:
            lyrics_text = f.read()
        print(f"Loaded lyrics ({len(lyrics_text)} characters)")
    except Exception as e:
        print(f"Error loading lyrics: {e}")
        return False
    
    # Prepare the request
    url = "http://localhost:8765/transcriptions"
    
    # Prepare the files and data
    files = {
        'audio': (os.path.basename(audio_path), open(audio_path, 'rb'), 'audio/mpeg')
    }
    
    data = {
        'transcript': lyrics_text
    }
    
    if conservative:
        data['conservative'] = 'on'
    
    # Send the request
    print("Sending request to Gentle API...")
    try:
        response = requests.post(url, files=files, data=data)
        
        if response.status_code != 200:
            print(f"Gentle API returned status code {response.status_code}")
            print(response.text)
            return False
        
        # Print the raw response for debugging
        print("Raw response from Gentle API:")
        print(response.text[:500])  # Print first 500 chars to avoid overwhelming output
        
        # Try to parse the response
        try:
            alignment_data = response.json()
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print("Response might not be JSON. Saving raw response to file.")
            with open("gentle_raw_response.txt", "w") as f:
                f.write(response.text)
            print("Raw response saved to gentle_raw_response.txt")
            return False
        
        # Convert Gentle format to our format
        word_timestamps = []
        
        if 'words' in alignment_data:
            for word in alignment_data['words']:
                if 'start' in word and 'end' in word:
                    word_timestamps.append({
                        'word': word['word'],
                        'start': word['start'],
                        'end': word['end'],
                        'confidence': word.get('confidence', 1.0)
                    })
        
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
        with open(output_path, 'w') as f:
            json.dump(lyrics_data, f, indent=2)
        print(f"Lyrics data saved to {output_path}")
        
        # Print summary
        word_count = len(word_timestamps)
        print(f"\nProcessed {word_count} words with timestamps.")
        
        if word_count > 0:
            print("\nFirst few words with timestamps:")
            for i, word in enumerate(word_timestamps[:5]):
                print(f"  {word['word']}: {word['start']:.2f}s - {word['end']:.2f}s")
        
        return True
    
    except Exception as e:
        print(f"Error during alignment: {e}")
        return False
    finally:
        # Close the file
        files['audio'][1].close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Directly align lyrics with audio using the Gentle API.")
    parser.add_argument("audio_file", help="Path to the audio file (e.g., song.mp3)")
    parser.add_argument("lyrics_file", help="Path to the lyrics text file (e.g., lyrics.txt)")
    parser.add_argument("output_file", help="Path to save the output JSON file (e.g., timestamps.json)")
    parser.add_argument("--song-title", default="Unknown Song", help="Song title for metadata")
    parser.add_argument("--artist-name", default="Unknown Artist", help="Artist name for metadata")
    parser.add_argument("--no-conservative", action="store_false", dest="conservative", help="Disable conservative alignment in Gentle")
    
    args = parser.parse_args()

    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file not found: {args.audio_file}")
        sys.exit(1)
    
    if not os.path.exists(args.lyrics_file):
        print(f"Error: Lyrics file not found: {args.lyrics_file}")
        sys.exit(1)
    
    success = align_with_gentle(
        args.audio_file,
        args.lyrics_file,
        args.output_file,
        song_title=args.song_title,
        artist_name=args.artist_name,
        conservative=args.conservative
    )
    
    if success:
        print("\nLyrics alignment completed successfully!")
    else:
        print("\nLyrics alignment failed.")