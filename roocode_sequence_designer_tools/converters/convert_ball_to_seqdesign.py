#!/usr/bin/env python3
"""
Convert ball.json to seqdesign.json format
"""

import json
import os
import sys
import uuid
import argparse

def convert_ball_to_seqdesign(input_path, output_path):
    """
    Convert ball.json to seqdesign.json format
    
    Args:
        input_path (str): Path to input .ball.json file
        output_path (str): Path to output .seqdesign.json file
    """
    # Load input file
    with open(input_path, 'r') as f:
        ball_data = json.load(f)
    
    # Create sequence design format
    seqdesign = {
        "metadata": {
            "title": ball_data.get("metadata", {}).get("name", "Sequence Design"),
            "total_duration_seconds": ball_data.get("metadata", {}).get("total_duration", 0),
            "target_prg_refresh_rate": ball_data.get("metadata", {}).get("refresh_rate", 50),
            "default_pixels": ball_data.get("metadata", {}).get("default_pixels", 4),
            "audio_file_path": ball_data.get("metadata", {}).get("audio_file", ""),
            "default_base_color": {"name": "black"}
        },
        "effects_timeline": []
    }
    
    # Convert segments to effects
    for segment in ball_data.get("segments", []):
        effect = {
            "id": f"segment_{str(uuid.uuid4())[:8]}",
            "type": "solid_color",
            "description": f"Segment from {segment['start_time']} to {segment['end_time']}",
            "timing": {
                "start_seconds": segment["start_time"],
                "end_seconds": segment["end_time"]
            },
            "params": {
                "color": {"rgb": segment["color"]}
            }
        }
        seqdesign["effects_timeline"].append(effect)
    
    # Write output file
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(output_path, 'w') as f:
        json.dump(seqdesign, f, indent=2)
    
    print(f"Converted {input_path} to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert ball.json to seqdesign.json format")
    parser.add_argument("input_file", help="Path to input .ball.json file")
    parser.add_argument("output_file", help="Path to output .seqdesign.json file")
    
    args = parser.parse_args()
    
    convert_ball_to_seqdesign(args.input_file, args.output_file)

if __name__ == "__main__":
    main()