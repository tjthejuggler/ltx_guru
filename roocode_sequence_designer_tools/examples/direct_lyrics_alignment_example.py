#!/usr/bin/env python3
"""
Direct Lyrics Alignment Example

This script demonstrates the simplified workflow for extracting lyrics timestamps
using the align_lyrics.py tool, which is the most efficient method.

Usage:
    python -m roocode_sequence_designer_tools.examples.direct_lyrics_alignment_example [path/to/audio.mp3]
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

def run_alignment(audio_path, lyrics_path):
    """Run the direct lyrics alignment process using align_lyrics.py."""
    # Define the output path
    output_path = "example_lyrics_timestamps.json"
    
    # Find the align_lyrics.py script
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_dir = os.path.dirname(script_dir)
    align_lyrics_path = os.path.join(project_dir, "align_lyrics.py")
    
    if not os.path.exists(align_lyrics_path):
        align_lyrics_path = os.path.join(script_dir, "align_lyrics.py")
    
    if not os.path.exists(align_lyrics_path):
        print("Error: Could not find align_lyrics.py script")
        return None
    
    # Build the command
    cmd = [
        sys.executable,
        align_lyrics_path,
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
        print(f"Lyrics alignment completed successfully!")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error running lyrics alignment: {e}")
        return None

def display_results(output_path):
    """Display the results of the lyrics alignment."""
    if not os.path.exists(output_path):
        print(f"Output file not found: {output_path}")
        return
    
    try:
        with open(output_path, "r") as f:
            data = json.load(f)
        
        print("\n=== Lyrics Alignment Results ===")
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
        
        # Show an example of how to use these timestamps in a sequence design
        print("\nExample usage in a sequence design:")
        print("""
{
  "effects": [
    {
      "type": "pulse_on_beat",
      "start_time": 0,
      "end_time": 180,
      "parameters": {
        "color": {"r": 255, "g": 0, "b": 0},
        "beat_source": "custom_times: [WORD_TIMESTAMPS]",
        "pulse_duration_seconds": 0.3
      }
    }
  ]
}
""")
        print("Where WORD_TIMESTAMPS would be replaced with the start times of each word.")
    except Exception as e:
        print(f"Error reading output file: {e}")

def compare_methods():
    """Compare the different methods for lyrics alignment."""
    print("\n=== Comparison of Lyrics Alignment Methods ===")
    print("\n1. align_lyrics.py (Recommended)")
    print("   - One-step process that handles everything automatically")
    print("   - Automatically starts the Gentle server if needed")
    print("   - Uses conservative alignment for better results")
    print("   - Command: python align_lyrics.py audio.mp3 lyrics.txt output.json")
    
    print("\n2. extract_lyrics_simple.py")
    print("   - Two-step process (start Gentle, then run extraction)")
    print("   - Requires manual server startup in some cases")
    print("   - Command: python -m roocode_sequence_designer_tools.extract_lyrics_simple audio.mp3 lyrics.txt output.json")
    
    print("\n3. extract_lyrics.py")
    print("   - Multi-step process with more options")
    print("   - Requires manual server startup")
    print("   - Command: python -m roocode_sequence_designer_tools.extract_lyrics audio.mp3 --lyrics-file lyrics.txt --output output.json --conservative")
    
    print("\nThe align_lyrics.py method is recommended for most use cases due to its simplicity and efficiency.")

def main():
    """Main function to run the example."""
    print("=== Direct Lyrics Alignment Example ===")
    
    # Check if an audio file path was provided
    if len(sys.argv) > 1:
        audio_path = sys.argv[1]
        print(f"Using provided audio file: {audio_path}")
    else:
        print("No audio file provided. Please provide an audio file path as an argument.")
        print("Example: python -m roocode_sequence_designer_tools.examples.direct_lyrics_alignment_example path/to/audio.mp3")
        return
    
    # Create example lyrics file
    lyrics_path = create_example_lyrics_file()
    
    # Run alignment
    output_path = run_alignment(audio_path, lyrics_path)
    
    # Display results
    if output_path:
        display_results(output_path)
    
    # Compare methods
    compare_methods()
    
    print("\nExample completed!")

if __name__ == "__main__":
    main()