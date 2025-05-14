#!/usr/bin/env python3
"""
Custom script to process lyrics for "You Know Me" by Lubalin.
"""

import os
import sys
import json
import requests
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent))

# Try to import the AudioAnalyzer
try:
    from sequence_maker.managers.audio_analysis_manager import AudioAnalyzer
except ImportError:
    try:
        from roo_code_sequence_maker.audio_analyzer import AudioAnalyzer
    except ImportError:
        print("Error: Could not import AudioAnalyzer. Make sure the module is available.")
        sys.exit(1)

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

def process_lyrics(audio_path, lyrics_path, output_path):
    """Process lyrics with the audio file."""
    print(f"Processing audio: {audio_path}")
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
    
    # Initialize the analyzer
    analyzer = AudioAnalyzer()
    
    # Prepare analysis parameters
    analysis_params = {
        'request_lyrics': True,
        'conservative_lyrics_alignment': True,
        'user_provided_lyrics': lyrics_text
    }
    
    # Analyze the audio
    print("Analyzing audio and aligning lyrics...")
    try:
        analysis_data = analyzer.analyze_audio(audio_path, analysis_params=analysis_params)
    except Exception as e:
        print(f"Error analyzing audio: {e}")
        return False
    
    # Extract lyrics data
    if 'lyrics_info' not in analysis_data:
        print("No lyrics information found in analysis data")
        return False
    
    lyrics_data = analysis_data['lyrics_info']
    
    # Add processing status information
    processing_status = {
        "song_identified": lyrics_data.get("song_title") is not None and lyrics_data.get("artist_name") is not None,
        "lyrics_retrieved": lyrics_data.get("raw_lyrics") is not None,
        "lyrics_aligned": len(lyrics_data.get("word_timestamps", [])) > 0,
        "user_assistance_needed": False,
        "assistance_type": None,
        "message": "Lyrics processing completed successfully."
    }
    
    lyrics_data["processing_status"] = processing_status
    
    # Save to file
    try:
        with open(output_path, 'w') as f:
            json.dump(lyrics_data, f, indent=2)
        print(f"Lyrics data saved to {output_path}")
    except Exception as e:
        print(f"Error saving lyrics data: {e}")
        return False
    
    # Print summary
    word_count = len(lyrics_data.get("word_timestamps", []))
    print(f"\nProcessed {word_count} words with timestamps.")
    
    if word_count > 0:
        print("\nFirst few words with timestamps:")
        for i, word in enumerate(lyrics_data.get("word_timestamps", [])[:5]):
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
    
    success = process_lyrics(audio_path, lyrics_path, output_path)
    
    if success:
        print("\nLyrics processing completed successfully!")
    else:
        print("\nLyrics processing failed.")