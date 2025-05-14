#!/usr/bin/env python3
"""
Lyrics Extraction Example

This script demonstrates the simplified workflow for extracting lyrics timestamps
using the extract_lyrics_simple.py tool.

Usage:
    python -m roocode_sequence_designer_tools.examples.lyrics_extraction_example
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def create_example_lyrics_file():
    """Create an example lyrics file for demonstration."""
    lyrics = """You know me
Anytime you hit me it's just not a good time
Guess there's always something, they say that's a good sign
Maybe good times don't come like they used to
Never satisfied, you would think it's by design
No matter what I'm doin it's just not enough
The way it hurts inside it's just like when you fall in love
It's not enough to have it all, I want it all at once
Oh that's all it was
You know me"""

    lyrics_path = "example_lyrics.txt"
    with open(lyrics_path, "w") as f:
        f.write(lyrics)
    
    print(f"Created example lyrics file: {lyrics_path}")
    return lyrics_path

def run_extraction(audio_path, lyrics_path):
    """Run the lyrics extraction process."""
    # Define the output path
    output_path = "example_lyrics_timestamps.json"
    
    # Build the command
    cmd = [
        sys.executable,
        "-m",
        "roocode_sequence_designer_tools.extract_lyrics_simple",
        audio_path,
        lyrics_path,
        output_path,
        "--song-title", "Example Song",
        "--artist-name", "Example Artist"
    ]
    
    # Run the command
    print(f"Running command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"Lyrics extraction completed successfully!")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error running lyrics extraction: {e}")
        return None

def display_results(output_path):
    """Display the results of the lyrics extraction."""
    if not os.path.exists(output_path):
        print(f"Output file not found: {output_path}")
        return
    
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
        
        print("\n=== Lyrics Extraction Results ===")
        print(f"Song: {data.get('song_title', 'Unknown')}")
        print(f"Artist: {data.get('artist_name', 'Unknown')}")
        
        word_timestamps = data.get("word_timestamps", [])
        print(f"\nExtracted {len(word_timestamps)} word timestamps")
        
        if word_timestamps:
            print("\nFirst 5 words with timestamps:")
            for i, word in enumerate(word_timestamps[:5]):
                print(f"  {word['word']}: {word['start']:.2f}s - {word['end']:.2f}s")
        
        print("\nThese timestamps can now be used in sequence designs to synchronize")
        print("light effects with specific lyrics in the song.")
    except Exception as e:
        print(f"Error reading output file: {e}")

def main():
    """Main function to run the example."""
    print("=== Lyrics Extraction Example ===")
    
    # Check if an audio file path was provided
    if len(sys.argv) > 1:
        audio_path = sys.argv[1]
        print(f"Using provided audio file: {audio_path}")
    else:
        print("No audio file provided. Please provide an audio file path as an argument.")
        print("Example: python -m roocode_sequence_designer_tools.examples.lyrics_extraction_example path/to/audio.mp3")
        return
    
    # Create example lyrics file
    lyrics_path = create_example_lyrics_file()
    
    # Run extraction
    output_path = run_extraction(audio_path, lyrics_path)
    
    # Display results
    if output_path:
        display_results(output_path)
    
    print("\nExample completed!")

if __name__ == "__main__":
    main()