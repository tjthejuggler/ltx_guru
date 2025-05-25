#!/usr/bin/env python3
"""
Generate a ball sequence where only the word "you" is blue and everything else is black
"""

import json
import os
import sys

def generate_you_only_sequence(input_path, output_path, you_color=[0, 0, 255], background_color=[0, 0, 0], pixels=4):
    """
    Generate a ball sequence where only the word "you" is blue and everything else is black
    
    Args:
        input_path (str): Path to input .lyrics.json file
        output_path (str): Path to output .ball.json file
        you_color (list): RGB color for the word "you" [r, g, b]
        background_color (list): RGB color for all other words and gaps [r, g, b]
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
            "name": f"{song_title} - {artist_name} - You Only",
            "default_pixels": pixels,
            "refresh_rate": 50,
            "total_duration": total_duration,
            "audio_file": f"sequence_projects/you_know_me/lubalin_you_know_me.mp3"
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
    
    # Process each word
    current_time = 0.0
    for word in word_timestamps:
        # If there's a gap between current_time and this word's start, add a black segment
        if word["start"] > current_time:
            ball_sequence["segments"].append({
                "start_time": current_time,
                "end_time": word["start"],
                "color": background_color,
                "pixels": pixels
            })
        
        # Add segment for the word - blue if "you", black otherwise
        if word["word"].lower() == "you":
            ball_sequence["segments"].append({
                "start_time": word["start"],
                "end_time": word["end"],
                "color": you_color,
                "pixels": pixels
            })
        else:
            ball_sequence["segments"].append({
                "start_time": word["start"],
                "end_time": word["end"],
                "color": background_color,
                "pixels": pixels
            })
        
        # Update current_time
        current_time = word["end"]
    
    # Add final black segment after the last word
    if word_timestamps and current_time < total_duration:
        ball_sequence["segments"].append({
            "start_time": current_time,
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
    
    print(f"Generated {output_path}")
    return output_path

if __name__ == "__main__":
    input_file = "sequence_projects/you_know_me/lyrics_timestamps.json"
    output_file = "sequence_projects/you_know_me/you_only.ball.json"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    generate_you_only_sequence(input_file, output_file)
    
    print("Next steps:")
    print("1. Convert ball sequence to seqdesign:")
    print("   python roocode_sequence_designer_tools/converters/convert_ball_to_seqdesign.py " + 
          f"{output_file} sequence_projects/you_know_me/you_only.seqdesign.json")
    print("2. Compile seqdesign to prg:")
    print("   python roocode_sequence_designer_tools/compile_seqdesign.py " + 
          f"sequence_projects/you_know_me/you_only.seqdesign.json sequence_projects/you_know_me/you_only.prg.json")