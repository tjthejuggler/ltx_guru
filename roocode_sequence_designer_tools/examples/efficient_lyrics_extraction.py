#!/usr/bin/env python3
"""
Efficient Lyrics Extraction Example

This script demonstrates the most efficient approach for extracting lyrics timestamps
from audio files. It follows the optimized workflow documented in lyrics_extraction_efficiency.md.
It also maintains proper file organization by storing all related files in the same
subdirectory within the sequence_projects folder.

Usage:
    python -m roocode_sequence_designer_tools.examples.efficient_lyrics_extraction audio_file [lyrics_file] [output_file]

Example:
    python -m roocode_sequence_designer_tools.examples.efficient_lyrics_extraction sequence_projects/song_name/artist_song_name.mp3
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

def ensure_gentle_running():
    """Ensure the Gentle server is running."""
    print("Checking if Gentle server is running...")
    
    try:
        # Try to import requests here to avoid dependency issues
        import requests
        response = requests.get("http://localhost:8765", timeout=2)
        if response.status_code == 200:
            print("✓ Gentle server is already running.")
            return True
    except Exception:
        print("! Gentle server is not running. Starting it now...")
    
    # Try to start the Gentle server
    try:
        result = subprocess.run(
            [sys.executable, "-m", "sequence_maker.scripts.start_gentle"],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error starting Gentle server: {e}")
        print(e.stdout)
        print(e.stderr)
        return False

def ensure_project_directory(audio_path):
    """Ensure the audio file is in a proper project directory and return paths."""
    # Get the directory containing the audio file
    audio_dir = os.path.dirname(audio_path)
    
    # If the audio file is not in a subdirectory of sequence_projects, warn the user
    if not audio_dir.startswith('sequence_projects/'):
        print("WARNING: Audio file should be in a subdirectory of sequence_projects/")
        print("For proper organization, move your audio file to sequence_projects/song_name/")
    
    # Extract the song directory and create it if it doesn't exist
    song_dir = audio_dir
    if not os.path.exists(song_dir):
        os.makedirs(song_dir, exist_ok=True)
        print(f"Created project directory: {song_dir}")
    
    # Generate default paths for lyrics and timestamps files
    filename = os.path.basename(audio_path)
    base_name = os.path.splitext(filename)[0]
    
    lyrics_path = os.path.join(song_dir, "lyrics.txt")
    output_path = os.path.join(song_dir, "lyrics_timestamps.json")
    
    return song_dir, lyrics_path, output_path

def extract_song_info_from_filename(audio_path):
    """Extract song title and artist from filename if possible."""
    filename = os.path.basename(audio_path)
    name_parts = os.path.splitext(filename)[0].split('_')
    
    if len(name_parts) >= 2:
        artist = name_parts[0].title()
        title = ' '.join(name_parts[1:]).title()
    else:
        artist = "Unknown Artist"
        title = name_parts[0].title()
    
    return title, artist

def align_lyrics(audio_path, lyrics_path, output_path):
    """Align lyrics with audio using the most efficient approach."""
    # Extract song info from filename
    song_title, artist_name = extract_song_info_from_filename(audio_path)
    
    print(f"Extracted song info from filename: '{song_title}' by {artist_name}")
    print(f"Aligning lyrics for: {audio_path}")
    
    # Use align_lyrics.py directly (most efficient approach)
    try:
        cmd = [
            sys.executable,
            "align_lyrics.py",
            audio_path,
            lyrics_path,
            output_path,
            "--song-title", song_title,
            "--artist-name", artist_name
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during alignment: {e}")
        print(e.stdout)
        print(e.stderr)
        return False

def display_sample_results(output_path, max_samples=5):
    """Display a sample of the results to avoid token waste."""
    try:
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        word_timestamps = data.get('word_timestamps', [])
        total_words = len(word_timestamps)
        
        print(f"\nSuccessfully processed {total_words} words with timestamps.")
        
        if total_words > 0:
            print(f"\nShowing first {min(max_samples, total_words)} words with timestamps:")
            for i, word in enumerate(word_timestamps[:max_samples]):
                print(f"  {word['word']}: {word['start']:.2f}s - {word['end']:.2f}s")
            
            if total_words > max_samples:
                print(f"  ... and {total_words - max_samples} more words")
        
        return True
    except Exception as e:
        print(f"Error displaying results: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Efficient lyrics extraction example")
    parser.add_argument("audio_file", help="Path to the audio file")
    parser.add_argument("lyrics_file", nargs='?', help="Path to the lyrics text file (optional, defaults to song_dir/lyrics.txt)")
    parser.add_argument("output_file", nargs='?', help="Path to save the output JSON file (optional, defaults to song_dir/lyrics_timestamps.json)")
    
    args = parser.parse_args()
    
    # Step 0: Ensure proper project directory structure and get paths
    song_dir, default_lyrics_path, default_output_path = ensure_project_directory(args.audio_file)
    
    # Use provided paths or defaults
    lyrics_path = args.lyrics_file if args.lyrics_file else default_lyrics_path
    output_path = args.output_file if args.output_file else default_output_path
    
    print(f"Project directory: {song_dir}")
    print(f"Lyrics file: {lyrics_path}")
    print(f"Output file: {output_path}")
    
    # Step 1: Ensure Gentle server is running
    if not ensure_gentle_running():
        print("Failed to start Gentle server. Exiting.")
        sys.exit(1)
    
    # Step 2: Align lyrics (using the most efficient approach)
    if not align_lyrics(args.audio_file, lyrics_path, output_path):
        print("Lyrics alignment failed. Exiting.")
        sys.exit(1)
    
    # Step 3: Display sample results (to avoid token waste)
    display_sample_results(output_path)
    
    print(f"\nFull results saved to: {output_path}")
    print("Lyrics extraction completed successfully!")
    print("\nFile organization:")
    print(f"  Audio file: {args.audio_file}")
    print(f"  Lyrics file: {lyrics_path}")
    print(f"  Timestamps file: {output_path}")

if __name__ == "__main__":
    main()