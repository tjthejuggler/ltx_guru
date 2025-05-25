#!/usr/bin/env python3
"""
Word Highlight Sequence Generator

This script generates a ball sequence that highlights specific words in a song.
It creates four files:
1. A ball.json file with segments for each highlighted word
2. A json_sequence.json file with color change points
3. A seqdesign.json file for the sequence design
4. A prg.json file for the final compiled sequence

Usage:
    python generate_word_highlight_sequence.py [options]

Options:
    --lyrics LYRICS_FILE    Path to the lyrics timestamps JSON file
    --word WORD             The word to highlight (case-insensitive)
    --color R,G,B           RGB color for the highlighted word
    --background R,G,B      RGB color for the background
    --pixels PIXELS         Number of pixels for the ball
    --refresh RATE          Refresh rate for the sequence
    --output PREFIX         Prefix for output files
    --convert               Convert and compile the sequence automatically
    --audio AUDIO_FILE      Path to the audio file (relative to sequence_projects)

Author: Roo
Date: May 21, 2025
"""

import json
import os
import subprocess
from datetime import datetime
import argparse

def generate_sequence(
    lyrics_file="sequence_projects/you_know_me/lyrics_timestamps.json",
    target_word="you",
    highlight_color=[255, 0, 0],  # Red
    background_color=[0, 0, 0],    # Black
    pixels=4,
    refresh_rate=100,
    output_prefix="sequence_projects/you_know_me/word_highlight",
    audio_file="you_know_me/lubalin_you_know_me.mp3",
    auto_convert=False
):
    """
    Generate a ball sequence that highlights specific words in a song.
    
    Args:
        lyrics_file: Path to the lyrics timestamps JSON file
        target_word: The word to highlight (case-insensitive)
        highlight_color: RGB color for the highlighted word
        background_color: RGB color for the background
        pixels: Number of pixels for the ball
        refresh_rate: Refresh rate for the sequence
        output_prefix: Prefix for output files
        audio_file: Path to the audio file (relative to sequence_projects)
        auto_convert: Whether to automatically convert and compile the sequence
    """
    # Load the lyrics timestamps
    with open(lyrics_file, "r") as f:
        lyrics_data = json.load(f)
        word_timestamps = lyrics_data["word_timestamps"]
    
    # Get the total duration from the last word's end time
    total_duration = max(word["end"] for word in word_timestamps)
    
    # Get song title from the lyrics data if available
    song_title = lyrics_data.get("song_title", "")
    artist_name = lyrics_data.get("artist_name", "")
    sequence_name = f"{song_title} - {artist_name} - {target_word.title()} Only"
    
    # Create the ball sequence structure
    ball_sequence = {
        "name": sequence_name,
        "defaultPixels": pixels,
        "created": datetime.now().isoformat(),
        "modified": datetime.now().isoformat(),
        "segments": []
    }
    
    # Create the JSON sequence structure
    json_sequence = {
        "default_pixels": pixels,
        "color_format": "rgb",
        "refresh_rate": refresh_rate,
        "end_time": int(total_duration * refresh_rate),
        "sequence": {}
    }
    
    # Create a sorted list of all word timestamps
    all_words = sorted(word_timestamps, key=lambda w: w["start"])
    
    # Add the initial black color to the sequence
    json_sequence["sequence"]["0"] = {
        "color": background_color,
        "pixels": pixels
    }
    
    # Count the number of highlighted words
    highlight_count = 0
    
    # Current position in the timeline
    current_time = 0
    
    # Process each word in order
    for i, word in enumerate(all_words):
        # If this is a target word
        if word["word"].lower() == target_word.lower():
            highlight_count += 1
            
            # If there's a gap between the current time and this word, add a black segment
            if word["start"] > current_time:
                ball_sequence["segments"].append({
                    "start_time": current_time,
                    "end_time": word["start"],
                    "color": background_color,
                    "pixels": pixels,
                    "effects": []
                })
            
            # Add the highlighted segment for this word
            ball_sequence["segments"].append({
                "start_time": word["start"],
                "end_time": word["end"],
                "color": highlight_color,
                "pixels": pixels,
                "effects": []
            })
            
            # Update the current time
            current_time = word["end"]
            
            # Add color change points to the sequence
            start_frame = int(word["start"] * refresh_rate)
            end_frame = int(word["end"] * refresh_rate)
            
            # Change to highlight color at the start of the word
            json_sequence["sequence"][str(start_frame)] = {
                "color": highlight_color,
                "pixels": pixels
            }
            
            # Change back to background color at the end of the word
            json_sequence["sequence"][str(end_frame)] = {
                "color": background_color,
                "pixels": pixels
            }
    
    # If there's remaining time after the last highlighted word, add a final black segment
    if current_time < total_duration:
        ball_sequence["segments"].append({
            "start_time": current_time,
            "end_time": total_duration,
            "color": background_color,
            "pixels": pixels,
            "effects": []
        })
    
    # Save the ball sequence to a file
    output_ball_file = f"{output_prefix}.ball.json"
    with open(output_ball_file, "w") as f:
        json.dump(ball_sequence, f, indent=2)
    
    # Save the JSON sequence to a file
    output_json_file = f"{output_prefix}.json_sequence.json"
    with open(output_json_file, "w") as f:
        json.dump(json_sequence, f, indent=2)
    
    # Create the seqdesign output path
    output_seqdesign_file = f"{output_prefix}.seqdesign.json"
    output_prg_file = f"{output_prefix}.prg.json"
    
    print(f"Generated {output_ball_file}")
    print(f"Generated {output_json_file}")
    print(f"Found {highlight_count} instances of '{target_word}'")
    
    # Automatically convert and compile if requested
    if auto_convert:
        print("\nAutomatically converting and compiling sequence...")
        
        # Convert ball to seqdesign
        convert_cmd = f"python roocode_sequence_designer_tools/converters/convert_ball_to_seqdesign.py {output_ball_file} {output_seqdesign_file}"
        subprocess.run(convert_cmd, shell=True, check=True)
        print(f"Converted to {output_seqdesign_file}")
        
        # Fix the seqdesign.json file
        with open(output_seqdesign_file, "r") as f:
            seqdesign_data = json.load(f)
        
        # Update metadata
        seqdesign_data["metadata"]["total_duration_seconds"] = total_duration
        seqdesign_data["metadata"]["target_prg_refresh_rate"] = refresh_rate
        seqdesign_data["metadata"]["title"] = sequence_name
        seqdesign_data["metadata"]["audio_file_path"] = audio_file
        
        # Save the updated seqdesign file
        with open(output_seqdesign_file, "w") as f:
            json.dump(seqdesign_data, f, indent=2)
        print(f"Updated metadata in {output_seqdesign_file}")
        
        # Compile seqdesign to prg
        compile_cmd = f"python -m roocode_sequence_designer_tools.compile_seqdesign {output_seqdesign_file} {output_prg_file}"
        subprocess.run(compile_cmd, shell=True, check=True)
        print(f"Compiled to {output_prg_file}")
        
        print("\nAll files generated successfully:")
        print(f"1. Ball sequence: {output_ball_file}")
        print(f"2. JSON sequence: {output_json_file}")
        print(f"3. Sequence design: {output_seqdesign_file}")
        print(f"4. PRG file: {output_prg_file}")
    else:
        print("\nNext steps:")
        print("1. Convert ball sequence to seqdesign:")
        print(f"   python roocode_sequence_designer_tools/converters/convert_ball_to_seqdesign.py {output_ball_file} {output_seqdesign_file}")
        print("2. Compile seqdesign to prg:")
        print(f"   python -m roocode_sequence_designer_tools.compile_seqdesign {output_seqdesign_file} {output_prg_file}")
        print("\n3. Or run both steps with one command:")
        print(f"   python roocode_sequence_designer_tools/converters/convert_ball_to_seqdesign.py {output_ball_file} {output_seqdesign_file} && python -m roocode_sequence_designer_tools.compile_seqdesign {output_seqdesign_file} {output_prg_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate a ball sequence that highlights specific words in a song")
    parser.add_argument("--lyrics", default="sequence_projects/you_know_me/lyrics_timestamps.json", help="Path to the lyrics timestamps JSON file")
    parser.add_argument("--word", default="you", help="The word to highlight (case-insensitive)")
    parser.add_argument("--color", default="255,0,0", help="RGB color for the highlighted word (comma-separated)")
    parser.add_argument("--background", default="0,0,0", help="RGB color for the background (comma-separated)")
    parser.add_argument("--pixels", type=int, default=4, help="Number of pixels for the ball")
    parser.add_argument("--refresh", type=int, default=100, help="Refresh rate for the sequence")
    parser.add_argument("--output", default="sequence_projects/you_know_me/word_highlight", help="Prefix for output files")
    parser.add_argument("--audio", default="you_know_me/lubalin_you_know_me.mp3", help="Path to the audio file (relative to sequence_projects)")
    parser.add_argument("--convert", action="store_true", help="Automatically convert and compile the sequence")
    
    args = parser.parse_args()
    
    # Parse color arguments
    highlight_color = [int(c) for c in args.color.split(",")]
    background_color = [int(c) for c in args.background.split(",")]
    
    generate_sequence(
        lyrics_file=args.lyrics,
        target_word=args.word,
        highlight_color=highlight_color,
        background_color=background_color,
        pixels=args.pixels,
        refresh_rate=args.refresh,
        output_prefix=args.output,
        audio_file=args.audio,
        auto_convert=args.convert
    )

if __name__ == "__main__":
    main()