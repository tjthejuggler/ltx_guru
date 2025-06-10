#!/usr/bin/env python3
"""
Generate a proper .smproj file from .prg.json files.

This tool creates a Sequence Maker project file with properly populated timelines
based on the compiled .prg.json files for each ball.
"""

import json
import argparse
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple

def prg_to_segments(prg_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert PRG sequence data to Sequence Maker segments.
    
    Args:
        prg_data: The loaded .prg.json data
        
    Returns:
        List of segment dictionaries for the timeline
    """
    segments = []
    refresh_rate = prg_data.get("refresh_rate", 100)
    sequence = prg_data.get("sequence", {})
    
    # Sort sequence entries by time unit
    sorted_entries = sorted(sequence.items(), key=lambda x: int(x[0]))
    
    current_segment = None
    
    for time_unit_str, entry in sorted_entries:
        time_unit = int(time_unit_str)
        time_seconds = time_unit / refresh_rate
        
        color = entry.get("color", [0, 0, 0])
        pixels = entry.get("pixels", 4)
        
        # If this is the start of a new segment or color change
        if current_segment is None:
            current_segment = {
                "startTime": time_seconds,
                "color": color,
                "pixels": pixels,
                "effects": [],
                "segment_type": "solid"
            }
        elif current_segment["color"] != color:
            # End the current segment and start a new one
            current_segment["endTime"] = time_seconds
            segments.append(current_segment)
            
            current_segment = {
                "startTime": time_seconds,
                "color": color,
                "pixels": pixels,
                "effects": [],
                "segment_type": "solid"
            }
    
    # Close the final segment
    if current_segment is not None:
        # Use the end_time from PRG data
        end_time_units = prg_data.get("end_time", 0)
        current_segment["endTime"] = end_time_units / refresh_rate
        segments.append(current_segment)
    
    return segments

def generate_smproj_from_prg_files(prg_files: List[str], project_name: str, output_path: str) -> None:
    """
    Generate a .smproj file from multiple .prg.json files.
    
    Args:
        prg_files: List of paths to .prg.json files (one per ball)
        project_name: Name for the project
        output_path: Path where to save the .smproj file
    """
    # Load PRG data for each ball
    ball_data = []
    total_duration = 0
    refresh_rate = 100
    
    for i, prg_file in enumerate(prg_files):
        if not os.path.exists(prg_file):
            print(f"Warning: PRG file not found: {prg_file}")
            continue
            
        with open(prg_file, 'r') as f:
            prg_data = json.load(f)
        
        # Extract metadata
        refresh_rate = prg_data.get("refresh_rate", 100)
        end_time_units = prg_data.get("end_time", 0)
        duration = end_time_units / refresh_rate
        total_duration = max(total_duration, duration)
        
        # Convert to segments
        segments = prg_to_segments(prg_data)
        
        ball_data.append({
            "name": f"Ball {i + 1}",
            "segments": segments,
            "default_pixels": prg_data.get("default_pixels", 4)
        })
    
    # Create the .smproj structure
    now = datetime.now().isoformat()
    
    smproj_data = {
        "metadata": {
            "version": "0.1.0",
            "created": now,
            "modified": now,
            "name": project_name,
            "description": f"Generated from PRG files: {', '.join(os.path.basename(f) for f in prg_files)}"
        },
        "settings": {
            "defaultPixels": 4,
            "refreshRate": refresh_rate,
            "totalDuration": int(total_duration),
            "zoomLevel": 1.0
        },
        "keyMappings": {},
        "effects": {},
        "timelines": [],
        "audio": {
            "embedded": False,
            "filename": None,
            "filepath": None,
            "duration": 0,
            "data": None
        },
        "visualizations": {
            "selected": ["waveform", "beats"],
            "settings": {
                "waveform": {"color": [0, 0, 255], "height": 100},
                "beats": {"color": [255, 0, 0], "threshold": 0.5}
            }
        },
        "lyrics": {
            "song_name": "",
            "artist_name": "",
            "lyrics_text": "",
            "word_timestamps": []
        },
        "chat_history": [],
        "llm_metadata": {
            "token_usage": 0,
            "estimated_cost": 0.0,
            "interactions": []
        },
        "llm_customization": {
            "custom_instructions": "",
            "presets": [],
            "task_templates": [],
            "active_preset": "Default"
        }
    }
    
    # Add timelines for each ball
    for ball_info in ball_data:
        timeline = {
            "name": ball_info["name"],
            "defaultPixels": ball_info["default_pixels"],
            "created": now,
            "modified": now,
            "segments": ball_info["segments"]
        }
        smproj_data["timelines"].append(timeline)
    
    # Ensure we have exactly 3 timelines (pad with empty ones if needed)
    while len(smproj_data["timelines"]) < 3:
        ball_num = len(smproj_data["timelines"]) + 1
        empty_timeline = {
            "name": f"Ball {ball_num}",
            "defaultPixels": 4,
            "created": now,
            "modified": now,
            "segments": []
        }
        smproj_data["timelines"].append(empty_timeline)
    
    # Write the .smproj file
    with open(output_path, 'w') as f:
        json.dump(smproj_data, f, indent=2)
    
    print(f"Generated {output_path}")
    print(f"Project: {project_name}")
    print(f"Total duration: {total_duration} seconds")
    print(f"Timelines: {len(smproj_data['timelines'])}")
    for i, timeline in enumerate(smproj_data["timelines"]):
        print(f"  {timeline['name']}: {len(timeline['segments'])} segments")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate .smproj file from .prg.json files")
    
    parser.add_argument("prg_files", nargs="+", help="Paths to .prg.json files (one per ball)")
    parser.add_argument("--project-name", required=True, help="Name for the project")
    parser.add_argument("--output", required=True, help="Output path for .smproj file")
    
    args = parser.parse_args()
    
    generate_smproj_from_prg_files(args.prg_files, args.project_name, args.output)

if __name__ == "__main__":
    main()