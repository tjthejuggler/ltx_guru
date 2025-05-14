#!/usr/bin/env python3
"""
Example script demonstrating the lyrics processing workflow.

This script shows how to:
1. Attempt to process lyrics from an audio file
2. Handle different partial success scenarios
3. Provide user assistance when needed

Usage:
    python lyrics_processing_workflow_example.py <audio_file_path>
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent.parent))


def initial_lyrics_processing(audio_path, output_path):
    """Attempt initial lyrics processing."""
    print("\n=== Step 1: Initial Lyrics Processing ===")
    print("Attempting to identify song, retrieve lyrics, and align with audio...")
    
    cmd = [
        "python", "-m", "roocode_sequence_designer_tools.extract_lyrics",
        audio_path,
        "--output", output_path
    ]
    subprocess.run(cmd)
    
    # Check the results
    try:
        with open(output_path, 'r') as f:
            lyrics_data = json.load(f)
        return lyrics_data
    except Exception as e:
        print(f"Error reading lyrics data: {e}")
        return None


def check_processing_status(lyrics_data):
    """Check the processing status and determine next steps."""
    print("\n=== Step 2: Checking Processing Status ===")
    
    if not lyrics_data or "processing_status" not in lyrics_data:
        print("No processing status information available.")
        return False, None
    
    status = lyrics_data["processing_status"]
    
    print(f"Song identified: {'Yes' if status['song_identified'] else 'No'}")
    print(f"Lyrics retrieved: {'Yes' if status['lyrics_retrieved'] else 'No'}")
    print(f"Lyrics aligned: {'Yes' if status['lyrics_aligned'] else 'No'}")
    
    if status["user_assistance_needed"]:
        print("\n⚠️ User Assistance Needed:")
        print(f"  {status['message']}")
        return False, status["assistance_type"]
    
    return True, None


def handle_song_identification_failure(audio_path, output_path):
    """Handle the case where song identification failed."""
    print("\n=== Step 3a: Handling Song Identification Failure ===")
    print("In a real scenario, you would:")
    print("1. Manually identify the song")
    print("2. Find the lyrics")
    print("3. Save them to a text file")
    
    # For this example, we'll create a sample lyrics file
    lyrics_file = os.path.join(os.path.dirname(output_path), "sample_lyrics.txt")
    with open(lyrics_file, 'w') as f:
        f.write("These are sample lyrics\nFor demonstration purposes\nWhen song identification fails")
    
    print(f"\nCreated sample lyrics file: {lyrics_file}")
    print("Now processing with the provided lyrics...")
    
    cmd = [
        "python", "-m", "roocode_sequence_designer_tools.extract_lyrics",
        audio_path,
        "--lyrics-file", lyrics_file,
        "--output", output_path
    ]
    subprocess.run(cmd)
    
    return lyrics_file


def handle_lyrics_retrieval_failure(audio_path, output_path, lyrics_data):
    """Handle the case where song was identified but lyrics retrieval failed."""
    print("\n=== Step 3b: Handling Lyrics Retrieval Failure ===")
    
    song_title = lyrics_data.get("song_title", "Unknown")
    artist_name = lyrics_data.get("artist_name", "Unknown")
    
    print(f"Song identified as: {song_title} by {artist_name}")
    print("In a real scenario, you would:")
    print(f"1. Find the lyrics for '{song_title}' by '{artist_name}'")
    print("2. Save them to a text file")
    
    # For this example, we'll create a sample lyrics file
    lyrics_file = os.path.join(os.path.dirname(output_path), "sample_lyrics.txt")
    with open(lyrics_file, 'w') as f:
        f.write(f"These are sample lyrics for {song_title}\nBy {artist_name}\nFor demonstration purposes")
    
    print(f"\nCreated sample lyrics file: {lyrics_file}")
    print("Now processing with the provided lyrics...")
    
    cmd = [
        "python", "-m", "roocode_sequence_designer_tools.extract_lyrics",
        audio_path,
        "--lyrics-file", lyrics_file,
        "--output", output_path
    ]
    subprocess.run(cmd)
    
    return lyrics_file


def handle_alignment_failure(audio_path, output_path, lyrics_file):
    """Handle the case where lyrics were retrieved but alignment failed."""
    print("\n=== Step 3c: Handling Alignment Failure ===")
    print("Trying with conservative alignment...")
    
    cmd = [
        "python", "-m", "roocode_sequence_designer_tools.extract_lyrics",
        audio_path,
        "--lyrics-file", lyrics_file,
        "--conservative",
        "--output", output_path
    ]
    subprocess.run(cmd)


def use_processed_lyrics(lyrics_data):
    """Demonstrate how to use the processed lyrics."""
    print("\n=== Step 4: Using Processed Lyrics ===")
    
    word_count = len(lyrics_data.get("word_timestamps", []))
    
    if word_count == 0:
        print("No word timestamps available.")
        return
    
    print(f"Successfully processed {word_count} words with timestamps.")
    print("\nExample of how to use these in a sequence design:")
    print("1. Create effects that trigger on specific words or phrases")
    print("2. Synchronize color changes with lyrics")
    print("3. Create visual emphasis for chorus sections")
    
    print("\nSample word timestamps:")
    for i, word in enumerate(lyrics_data.get("word_timestamps", [])[:5]):
        print(f"  {word['word']}: {word['start']:.2f}s - {word['end']:.2f}s")


def main():
    """Main function to demonstrate the lyrics processing workflow."""
    parser = argparse.ArgumentParser(description="Demonstrate the lyrics processing workflow.")
    parser.add_argument("audio_file_path", help="Path to the audio file to process")
    
    args = parser.parse_args()
    audio_path = args.audio_file_path
    
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found: {audio_path}")
        sys.exit(1)
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(audio_path), "lyrics_workflow_example")
    os.makedirs(output_dir, exist_ok=True)
    
    # Output path for lyrics data
    output_path = os.path.join(output_dir, "lyrics_data.json")
    
    # Step 1: Initial lyrics processing
    lyrics_data = initial_lyrics_processing(audio_path, output_path)
    
    if not lyrics_data:
        print("Failed to process lyrics. Exiting.")
        sys.exit(1)
    
    # Step 2: Check processing status
    success, assistance_type = check_processing_status(lyrics_data)
    
    # Step 3: Handle partial success cases
    lyrics_file = None
    
    if not success:
        if assistance_type == "song_identification":
            lyrics_file = handle_song_identification_failure(audio_path, output_path)
        elif assistance_type == "lyrics_text":
            lyrics_file = handle_lyrics_retrieval_failure(audio_path, output_path, lyrics_data)
        
        # Reload the lyrics data after handling
        try:
            with open(output_path, 'r') as f:
                lyrics_data = json.load(f)
            
            # Check if alignment succeeded
            status = lyrics_data.get("processing_status", {})
            if not status.get("lyrics_aligned", False) and lyrics_file:
                handle_alignment_failure(audio_path, output_path, lyrics_file)
                
                # Reload the lyrics data after handling alignment
                with open(output_path, 'r') as f:
                    lyrics_data = json.load(f)
        except Exception as e:
            print(f"Error reloading lyrics data: {e}")
    
    # Step 4: Use the processed lyrics
    use_processed_lyrics(lyrics_data)
    
    print("\n=== Workflow Example Complete ===")
    print(f"All outputs have been saved to: {output_dir}")


if __name__ == "__main__":
    main()