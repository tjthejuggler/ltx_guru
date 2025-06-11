#!/usr/bin/env python3
"""
Script to modify the alternating flash sequence timing from 0.1s to 0.25s duration
"""

import json
import sys
from pathlib import Path

def modify_segment_timing(segments):
    """
    Modify segments to change flash duration from 0.1s to 0.25s
    """
    modified_segments = []
    
    for segment in segments:
        new_segment = segment.copy()
        
        # Check if this is a colored segment (not black/off)
        color = segment.get('color', [0, 0, 0])
        is_colored = any(c > 0 for c in color)
        
        if is_colored:
            # This is a flash segment - extend duration from 0.1s to 0.25s
            start_time = segment['startTime']
            original_end_time = segment['endTime']
            original_duration = original_end_time - start_time
            
            # If this was a 0.1s flash, make it 0.25s
            if abs(original_duration - 0.1) < 0.01:  # Allow for floating point precision
                new_segment['endTime'] = start_time + 0.25
        
        modified_segments.append(new_segment)
    
    return modified_segments

def adjust_subsequent_timings(segments):
    """
    Adjust all subsequent segment timings to account for the longer flash durations
    """
    adjusted_segments = []
    time_offset = 0.0
    
    for i, segment in enumerate(segments):
        new_segment = segment.copy()
        
        # Apply accumulated time offset
        new_segment['startTime'] = segment['startTime'] + time_offset
        new_segment['endTime'] = segment['endTime'] + time_offset
        
        # Check if this segment's duration was extended
        color = segment.get('color', [0, 0, 0])
        is_colored = any(c > 0 for c in color)
        
        if is_colored:
            original_duration = segment['endTime'] - segment['startTime']
            if abs(original_duration - 0.1) < 0.01:  # This was a 0.1s flash
                # Extend to 0.25s
                new_segment['endTime'] = new_segment['startTime'] + 0.25
                # Add the extra time to the offset for subsequent segments
                time_offset += 0.15  # 0.25 - 0.1 = 0.15s extra
        
        adjusted_segments.append(new_segment)
    
    return adjusted_segments

def modify_project_file(input_file, output_file):
    """
    Load the project file, modify the timing, and save to output file
    """
    with open(input_file, 'r') as f:
        project_data = json.load(f)
    
    # Modify each timeline
    for timeline in project_data.get('timelines', []):
        segments = timeline.get('segments', [])
        modified_segments = adjust_subsequent_timings(segments)
        timeline['segments'] = modified_segments
    
    # Update metadata
    project_data['metadata']['modified'] = "2025-06-10T17:27:31.000000"
    project_data['metadata']['name'] = "Alternating Flash 3 Balls (0.25s duration)"
    project_data['metadata']['description'] = "Modified from PRG files with 0.25s flash duration instead of 0.1s"
    
    # Update total duration in settings (rough estimate)
    if 'settings' in project_data:
        # The sequence will be longer due to extended flash times
        # Original was 120s, with many 0.1s flashes extended to 0.25s
        # Rough estimate: add about 50% more time
        project_data['settings']['totalDuration'] = 180
    
    # Save the modified project
    with open(output_file, 'w') as f:
        json.dump(project_data, f, indent=2)
    
    print(f"Modified project saved to: {output_file}")

if __name__ == "__main__":
    input_file = Path("alternating_flash_3balls_fixed.smproj")
    output_file = Path("alternating_flash_3balls_025s.smproj")
    
    if not input_file.exists():
        print(f"Error: Input file {input_file} not found")
        sys.exit(1)
    
    modify_project_file(input_file, output_file)
    print("Timing modification complete!")