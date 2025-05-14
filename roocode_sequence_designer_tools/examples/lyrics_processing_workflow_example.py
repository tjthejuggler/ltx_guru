#!/usr/bin/env python3
"""
Example script demonstrating the optimized lyrics processing workflow.

This script shows how to:
1. Start the Gentle server (critical first step)
2. Check for API keys and determine the most efficient approach
3. Process lyrics with the appropriate flags for best results
4. Handle different scenarios efficiently

Usage:
    python lyrics_processing_workflow_example.py <audio_file_path>
"""

import os
import sys
import json
import subprocess
import argparse
import time
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent.parent))


def start_gentle_server():
    """Start the Gentle server if it's not already running."""
    print("\n=== Step 1: Starting Gentle Server ===")
    print("Checking if Gentle server is running...")
    
    # Check if Gentle is already running
    try:
        import requests
        response = requests.get("http://localhost:8765", timeout=2)
        if response.status_code == 200:
            print("Gentle server is already running.")
            return True
    except Exception:
        print("Gentle server is not running. Starting it now...")
    
    # Start the Gentle server
    cmd = [
        "python", "-m", "sequence_maker.scripts.start_gentle"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if "Gentle started successfully" in result.stdout or "Gentle is already running" in result.stdout:
        print("Gentle server started successfully.")
        return True
    else:
        print("Failed to start Gentle server. Check Docker installation.")
        print(f"Output: {result.stdout}")
        print(f"Error: {result.stderr}")
        return False


def check_api_keys():
    """Check if API keys are available."""
    print("\n=== Step 2: Checking API Keys ===")
    
    # Try a simple command that would show API key status in output
    cmd = [
        "python", "-m", "roocode_sequence_designer_tools.extract_lyrics",
        "--help"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    api_keys_missing = "API keys file not found" in result.stderr or "Missing ACRCloud API keys" in result.stderr
    
    if api_keys_missing:
        print("API keys are missing or incomplete.")
        print("Automatic song identification will not work.")
        print("We'll skip directly to manual lyrics processing.")
        return False
    else:
        print("API keys appear to be configured.")
        return True


def attempt_automatic_processing(audio_path, output_path):
    """Attempt automatic lyrics processing."""
    print("\n=== Step 3a: Attempting Automatic Lyrics Processing ===")
    print("Trying to identify song, retrieve lyrics, and align with audio...")
    
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
        
        status = lyrics_data.get("processing_status", {})
        if status.get("lyrics_aligned", False):
            print("Automatic processing succeeded!")
            return lyrics_data, True
        else:
            print("Automatic processing failed to align lyrics.")
            return lyrics_data, False
    except Exception as e:
        print(f"Error reading lyrics data: {e}")
        return None, False


def process_with_user_lyrics(audio_path, output_path, lyrics_text=None):
    """Process lyrics with user-provided text."""
    print("\n=== Step 3b: Processing with User-Provided Lyrics ===")
    
    # Create a lyrics file
    lyrics_file = os.path.join(os.path.dirname(output_path), "user_lyrics.txt")
    
    if lyrics_text is None:
        # In a real application, you would get this from user input
        lyrics_text = "These are sample lyrics\nFor demonstration purposes\nProvided by the user"
    
    with open(lyrics_file, 'w') as f:
        f.write(lyrics_text)
    
    print(f"Created lyrics file: {lyrics_file}")
    print("Processing with conservative alignment for best results...")
    
    # Always use the --conservative flag for better alignment results
    cmd = [
        "python", "-m", "roocode_sequence_designer_tools.extract_lyrics",
        audio_path,
        "--lyrics-file", lyrics_file,
        "--conservative",  # This flag is crucial for successful alignment
        "--output", output_path
    ]
    subprocess.run(cmd)
    
    # Check the results
    try:
        with open(output_path, 'r') as f:
            lyrics_data = json.load(f)
        
        status = lyrics_data.get("processing_status", {})
        if status.get("lyrics_aligned", False):
            print("Lyrics alignment succeeded!")
            return lyrics_data
        else:
            print("Lyrics alignment failed even with conservative mode.")
            return lyrics_data
    except Exception as e:
        print(f"Error reading lyrics data: {e}")
        return None


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
    """Main function demonstrating the optimized lyrics processing workflow."""
    parser = argparse.ArgumentParser(description="Demonstrate the optimized lyrics processing workflow.")
    parser.add_argument("audio_file_path", help="Path to the audio file to process")
    parser.add_argument("--lyrics", help="Optional path to a lyrics text file")
    
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
    
    # Step 1: Start the Gentle server (CRITICAL first step)
    if not start_gentle_server():
        print("Failed to start Gentle server. Exiting.")
        sys.exit(1)
    
    # Step 2: Check if API keys are available
    api_keys_available = check_api_keys()
    
    # Step 3: Process lyrics using the most efficient approach
    lyrics_data = None
    
    if args.lyrics:
        # If lyrics file is provided, use it directly with conservative alignment
        print(f"Using provided lyrics file: {args.lyrics}")
        with open(args.lyrics, 'r') as f:
            lyrics_text = f.read()
        lyrics_data = process_with_user_lyrics(audio_path, output_path, lyrics_text)
    elif api_keys_available:
        # Try automatic processing first
        lyrics_data, success = attempt_automatic_processing(audio_path, output_path)
        if not success:
            # If automatic processing fails, fall back to user-provided lyrics
            lyrics_data = process_with_user_lyrics(audio_path, output_path)
    else:
        # Skip directly to user-provided lyrics if API keys are missing
        lyrics_data = process_with_user_lyrics(audio_path, output_path)
    
    if not lyrics_data:
        print("Failed to process lyrics. Exiting.")
        sys.exit(1)
    
    # Step 4: Use the processed lyrics
    use_processed_lyrics(lyrics_data)
    
    print("\n=== Workflow Example Complete ===")
    print(f"All outputs have been saved to: {output_dir}")
    print("\nKey takeaways for efficient lyrics processing:")
    print("1. Always start the Gentle server first")
    print("2. Use the --conservative flag when providing lyrics")
    print("3. Skip automatic identification if API keys are missing")
    print("4. Process user-provided lyrics in a single step")


if __name__ == "__main__":
    main()