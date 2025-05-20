#!/usr/bin/env python3
"""
Convert lyrics timestamps to ball sequence
"""

import json
import os
import sys
import argparse

def convert_lyrics_to_ball(input_path, output_path, color=[0, 0, 255], background_color=[0, 0, 0], pixels=4):
    """
    Convert lyrics timestamps to ball sequence
    
    Args:
        input_path (str): Path to input .lyrics.json file
        output_path (str): Path to output .ball.json file
        color (list): RGB color for words [r, g, b]
        background_color (list): RGB color for gaps [r, g, b]
        pixels (int): Number of pixels (1-4)
    """
    # Load input file
    with open(input_path, 'r') as f:
        lyrics_data = json.load(f)
    
    # Extract metadata
    song_title = lyrics_data.get("song_title", "Unknown")
    artist_name = lyrics_data.get("artist_name", "Unknown")
    word_timestamps = lyrics_data.get("word_timestamps", [])
    
    # Find total duration
    total_duration = 0
    if word_timestamps:
        total_duration = max(word["end"] for word in word_timestamps) + 5.0  # Add 5 seconds buffer
    
    # Create ball sequence format
    ball_sequence = {
        "metadata": {
            "name": f"{song_title} - {artist_name} - Word Flash",
            "default_pixels": pixels,
            "refresh_rate": 50,
            "total_duration": total_duration,
            "audio_file": ""  # To be filled by the user
        },
        "segments": []
    }
    
    # Add initial black segment if first word doesn't start at 0
    if word_timestamps and word_timestamps[0]["start"] > 0:
        ball_sequence["segments"].append({
            "start_time": 0.0,
            "end_time": word_timestamps[0]["start"],
            "color": background_color,
            "pixels": pixels
        })
    
    # Add segments for each word and gap
    for i, word in enumerate(word_timestamps):
        # Add segment for the word
        ball_sequence["segments"].append({
            "start_time": word["start"],
            "end_time": word["end"],
            "color": color,
            "pixels": pixels
        })
        
        # Add segment for the gap after this word (if not the last word)
        if i < len(word_timestamps) - 1:
            next_word = word_timestamps[i + 1]
            if word["end"] < next_word["start"]:
                ball_sequence["segments"].append({
                    "start_time": word["end"],
                    "end_time": next_word["start"],
                    "color": background_color,
                    "pixels": pixels
                })
    
    # Add final black segment after the last word
    if word_timestamps:
        ball_sequence["segments"].append({
            "start_time": word_timestamps[-1]["end"],
            "end_time": total_duration,
            "color": background_color,
            "pixels": pixels
        })
    
    # Write output file
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(output_path, 'w') as f:
        json.dump(ball_sequence, f, indent=2)
    
    print(f"Converted {input_path} to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert lyrics timestamps to ball sequence")
    parser.add_argument("input_file", help="Path to input .lyrics.json file")
    parser.add_argument("output_file", help="Path to output .ball.json file")
    parser.add_argument("--color", default="0,0,255", help="RGB color for words (comma-separated, e.g., '0,0,255')")
    parser.add_argument("--background", default="0,0,0", help="RGB color for gaps (comma-separated, e.g., '0,0,0')")
    parser.add_argument("--pixels", type=int, default=4, help="Number of pixels (1-4)")
    
    args = parser.parse_args()
    
    try:
        color = [int(x) for x in args.color.split(",")]
        if len(color) != 3:
            raise ValueError("Color must have 3 components")
    except:
        print(f"Warning: Invalid color format: {args.color}. Using default blue [0,0,255].")
        color = [0, 0, 255]
    
    try:
        background_color = [int(x) for x in args.background.split(",")]
        if len(background_color) != 3:
            raise ValueError("Background color must have 3 components")
    except:
        print(f"Warning: Invalid background color format: {args.background}. Using default black [0,0,0].")
        background_color = [0, 0, 0]
    
    convert_lyrics_to_ball(args.input_file, args.output_file, color, background_color, args.pixels)

if __name__ == "__main__":
    main()