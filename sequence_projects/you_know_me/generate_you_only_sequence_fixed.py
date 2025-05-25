#!/usr/bin/env python3
"""
Generate a ball sequence where only the word "you" is blue and everything else is black
Fixed version with 100Hz refresh rate and simplified segment structure
"""

import json
import os
import sys

def generate_you_only_sequence(input_path, output_path, you_color=[0, 0, 255], background_color=[0, 0, 0], pixels=4):
    """
    Generate a ball sequence where only the word "you" is blue and everything else is black
    
    Args:
        input_path (str): Path to input lyrics_timestamps.json file
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
        "name": f"{song_title} - {artist_name} - You Only",
        "defaultPixels": pixels,
        "created": "2025-05-21T11:40:00.000000",
        "modified": "2025-05-21T11:40:00.000000",
        "segments": []
    }
    
    # Add initial black segment
    ball_sequence["segments"].append({
        "start_time": 0,
        "end_time": total_duration,
        "color": background_color,
        "pixels": pixels,
        "effects": []
    })
    
    # Add segments only for the "you" words
    for word in word_timestamps:
        if word["word"].lower() == "you":
            # Add blue segment for "you"
            ball_sequence["segments"].append({
                "start_time": word["start"],
                "end_time": word["end"],
                "color": you_color,
                "pixels": pixels,
                "effects": []
            })
    
    # Write output file
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(output_path, 'w') as f:
        json.dump(ball_sequence, f, indent=2)
    
    print(f"Generated {output_path}")
    
    # Also generate the JSON sequence format directly
    json_sequence = {
        "default_pixels": pixels,
        "color_format": "rgb",
        "refresh_rate": 100,  # Use 100Hz refresh rate
        "end_time": int(total_duration * 100),  # Convert to 100Hz units
        "sequence": {}
    }
    
    # Add initial black
    json_sequence["sequence"]["0"] = {
        "color": background_color,
        "pixels": pixels
    }
    
    # Add entries for each "you" word
    for word in word_timestamps:
        if word["word"].lower() == "you":
            # Start of "you" - change to blue
            start_time_units = int(word["start"] * 100)
            json_sequence["sequence"][str(start_time_units)] = {
                "color": you_color,
                "pixels": pixels
            }
            
            # End of "you" - change back to black
            end_time_units = int(word["end"] * 100)
            json_sequence["sequence"][str(end_time_units)] = {
                "color": background_color,
                "pixels": pixels
            }
    
    # Write the JSON sequence file
    json_sequence_path = output_path.replace(".ball.json", ".json_sequence.json")
    with open(json_sequence_path, 'w') as f:
        json.dump(json_sequence, f, indent=2)
    
    print(f"Generated {json_sequence_path}")
    
    return output_path

if __name__ == "__main__":
    input_file = "sequence_projects/you_know_me/lyrics_timestamps.json"
    output_file = "sequence_projects/you_know_me/you_only_fixed.ball.json"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    generate_you_only_sequence(input_file, output_file)
    
    print("Next steps:")
    print("1. Convert ball sequence to seqdesign:")
    print("   python roocode_sequence_designer_tools/converters/convert_ball_to_seqdesign.py " + 
          f"{output_file} sequence_projects/you_know_me/you_only_fixed.seqdesign.json")
    print("2. Compile seqdesign to prg:")
    print("   python -m roocode_sequence_designer_tools.compile_seqdesign " + 
          f"sequence_projects/you_know_me/you_only_fixed.seqdesign.json sequence_projects/you_know_me/you_only_fixed.prg.json")