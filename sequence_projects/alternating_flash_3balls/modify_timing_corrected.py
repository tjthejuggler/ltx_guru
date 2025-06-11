#!/usr/bin/env python3
"""
Modify timing in alternating flash sequence - CORRECTED VERSION
Changes flash duration from 0.1s to 0.25s while keeping the same trigger interval (0.25s)
Total duration should remain the same (120s)
"""

import json
import sys
from pathlib import Path

def modify_project_file_corrected(input_file, output_file):
    """
    Modify the project file to change flash duration from 0.1s to 0.25s
    while maintaining the same trigger intervals (every 0.25s)
    """
    
    # Read the original file
    with open(input_file, 'r') as f:
        project_data = json.load(f)
    
    print(f"Original total duration: {project_data['settings']['totalDuration']}s")
    
    # Process each timeline
    for timeline_idx, timeline in enumerate(project_data['timelines']):
        timeline_name = timeline['name']
        print(f"\nProcessing {timeline_name}...")
        
        segments = timeline['segments']
        modified_segments = []
        
        for segment in segments:
            start_time = segment['startTime']
            end_time = segment['endTime']
            duration = end_time - start_time
            color = segment['color']
            
            # Check if this is a colored segment (not black/off)
            is_colored = not (color[0] == 0 and color[1] == 0 and color[2] == 0)
            
            if is_colored and abs(duration - 0.1) < 0.001:  # This is a 0.1s flash
                # Change duration to 0.25s
                new_end_time = start_time + 0.25
                segment['endTime'] = new_end_time
                print(f"  Modified flash: {start_time:.3f}s -> {new_end_time:.3f}s (duration: 0.25s)")
            
            modified_segments.append(segment)
        
        # Update the timeline
        timeline['segments'] = modified_segments
    
    # Keep the same total duration (120s)
    project_data['settings']['totalDuration'] = 120
    
    # Update metadata
    project_data['metadata']['name'] = "Alternating Flash 3 Balls (0.25s duration - corrected)"
    project_data['metadata']['description'] = "Modified from PRG files with 0.25s flash duration, same trigger interval"
    project_data['metadata']['modified'] = "2025-06-10T17:29:00.000000"
    
    # Write the modified file
    with open(output_file, 'w') as f:
        json.dump(project_data, f, indent=2)
    
    print(f"\nModified project saved to: {output_file}")
    print(f"Total duration remains: {project_data['settings']['totalDuration']}s")

if __name__ == "__main__":
    input_file = "alternating_flash_3balls_fixed.smproj"
    output_file = "alternating_flash_3balls_025s_corrected.smproj"
    
    modify_project_file_corrected(input_file, output_file)
    print("Correction complete!")