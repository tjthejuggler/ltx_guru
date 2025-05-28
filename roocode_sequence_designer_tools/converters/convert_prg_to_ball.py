#!/usr/bin/env python3
"""
Convert PRG-JSON (.prg.json) to standardized Ball Sequence format (.ball.json)
"""

import json
import os
import argparse
from typing import Dict, Any, List, Tuple, Optional # Added Optional

def convert_prg_to_ball(input_prg_path: str, output_ball_path: str, audio_file_path: Optional[str] = None) -> None:
    """
    Convert a .prg.json file to a .ball.json file.

    Args:
        input_prg_path (str): Path to input .prg.json file.
        output_ball_path (str): Path to output .ball.json file.
        audio_file_path (str, optional): Relative path to the audio file for metadata.
    """
    try:
        with open(input_prg_path, 'r') as f:
            prg_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input PRG file not found: {input_prg_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from PRG file: {input_prg_path}")
        return

    default_pixels = prg_data.get("default_pixels", 3) 
    refresh_rate = prg_data.get("refresh_rate", 50) 
    total_duration_units = prg_data.get("end_time", 0)
    total_duration_seconds = total_duration_units / refresh_rate if refresh_rate > 0 else 0

    sequence_dict = prg_data.get("sequence", {})
    
    sorted_time_units = sorted([int(k) for k in sequence_dict.keys()])

    ball_segments: List[Dict[str, Any]] = []

    for i, start_units in enumerate(sorted_time_units):
        segment_prg = sequence_dict[str(start_units)] 
        
        start_time_sec = start_units / refresh_rate
        
        if i + 1 < len(sorted_time_units):
            end_units = sorted_time_units[i+1]
        else:
            end_units = total_duration_units
            
        end_time_sec = end_units / refresh_rate
        
        if end_time_sec > start_time_sec:
            ball_segments.append({
                "start_time": round(start_time_sec, 3), 
                "end_time": round(end_time_sec, 3),
                "color": segment_prg.get("color", [0, 0, 0]),
                "pixels": segment_prg.get("pixels", default_pixels)
            })

    ball_sequence_data = {
        "metadata": {
            "name": os.path.splitext(os.path.basename(output_ball_path))[0],
            "default_pixels": default_pixels,
            "refresh_rate": refresh_rate,
            "total_duration": round(total_duration_seconds, 3),
            "audio_file": audio_file_path if audio_file_path else ""
        },
        "segments": ball_segments
    }

    output_dir = os.path.dirname(output_ball_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(output_ball_path, 'w') as f:
        json.dump(ball_sequence_data, f, indent=2)
    
    print(f"Successfully converted {input_prg_path} to {output_ball_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert .prg.json to .ball.json format.")
    parser.add_argument("input_prg_file", help="Path to input .prg.json file.")
    parser.add_argument("output_ball_file", help="Path to output .ball.json file.")
    parser.add_argument("--audio-file", help="Optional: Relative path to the audio file for metadata.", default=None)
    
    args = parser.parse_args()
    
    audio_file_arg = args.audio_file
    if not audio_file_arg:
        base_input_name = os.path.splitext(args.input_prg_file)[0] # Get base name without .prg.json
        seqdesign_path = base_input_name + ".seqdesign.json"
        if os.path.exists(seqdesign_path):
            try:
                with open(seqdesign_path, 'r') as sd_f:
                    sd_data = json.load(sd_f)
                    # The .seqdesign.json schema uses 'audio_file_path' if it's relative to the project,
                    # or 'audio_file' as per my earlier schema generation.
                    # Let's check for both, prioritizing 'audio_file_path' as per schema
                    # then 'audio_file' as a fallback from what I recall generating.
                    # The schema uses "audio_file_path" for relative paths, but the .ball.json format uses "audio_file".
                    # For now, I'll assume if .seqdesign.json has "audio_file_path", that's the one to use.
                    # Or if it's just "audio_file" from an older schema.
                    # The current .seqdesign.json schema uses "audio_file_path".
                    # My .ball.json schema indicates "audio_file".
                    # The .seqdesign.json I *generated* for "you_know_me" used "audio_file".
                    # Let's prioritize "audio_file" from the seqdesign for now as that's what I generated.
                    inferred_audio_path = sd_data.get("metadata", {}).get("audio_file")
                    if not inferred_audio_path: # Fallback to audio_file_path if audio_file is not present
                         inferred_audio_path = sd_data.get("metadata", {}).get("audio_file_path")

                    if inferred_audio_path:
                         audio_file_arg = inferred_audio_path
            except Exception: 
                pass 

    convert_prg_to_ball(args.input_prg_file, args.output_ball_file, audio_file_arg)

if __name__ == "__main__":
    main()