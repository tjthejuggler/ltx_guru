#!/usr/bin/env python3
"""
Convert word_flash_sequence.json to standardized ball.json format
"""

import json
import os
import sys
import argparse

def convert_word_flash_to_ball(input_path, output_path):
    """
    Convert word_flash_sequence.json to standardized ball.json format
    
    Args:
        input_path (str): Path to input word_flash_sequence.json file
        output_path (str): Path to output .ball.json file
    """
    # Load input file
    with open(input_path, 'r') as f:
        word_flash_data = json.load(f)
    
    # Create ball sequence format
    ball_sequence = {
        "metadata": {
            "name": word_flash_data.get("name", "Ball Sequence"),
            "default_pixels": word_flash_data.get("default_pixels", 4),
            "refresh_rate": word_flash_data.get("refresh_rate", 50),
            "total_duration": word_flash_data.get("total_duration", 0),
            "audio_file": word_flash_data.get("audio_file", "")
        },
        "segments": []
    }
    
    # Extract timeline segments
    if "timelines" in word_flash_data and len(word_flash_data["timelines"]) > 0:
        timeline = word_flash_data["timelines"][0]
        ball_sequence["segments"] = timeline.get("segments", [])
    
    # Write output file
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(output_path, 'w') as f:
        json.dump(ball_sequence, f, indent=2)
    
    print(f"Converted {input_path} to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert word_flash_sequence.json to standardized ball.json format")
    parser.add_argument("input_file", help="Path to input word_flash_sequence.json file")
    parser.add_argument("output_file", help="Path to output .ball.json file")
    
    args = parser.parse_args()
    
    convert_word_flash_to_ball(args.input_file, args.output_file)

if __name__ == "__main__":
    main()