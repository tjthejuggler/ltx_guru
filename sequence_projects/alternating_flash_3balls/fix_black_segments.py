#!/usr/bin/env python3

import json
import sys
from datetime import datetime

def fix_black_segments(input_file, output_file):
    """
    Fix the black segments to start when the color flash ends, not overlap with it.
    """
    
    # Read the input file
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    print(f"Fixing black segments in: {input_file}")
    
    # Process each timeline
    for timeline_idx, timeline in enumerate(data['timelines']):
        timeline_name = timeline['name']
        print(f"\nProcessing {timeline_name}:")
        
        segments = timeline['segments']
        fixed_segments = []
        
        i = 0
        while i < len(segments):
            segment = segments[i]
            
            # Check if this is a color flash (non-black)
            if segment['color'] != [0, 0, 0]:
                # This is a color flash - keep it as is
                fixed_segments.append(segment)
                print(f"  Color flash: {segment['startTime']}s - {segment['endTime']}s")
                
                # Check if the next segment is black and overlaps
                if i + 1 < len(segments):
                    next_segment = segments[i + 1]
                    if next_segment['color'] == [0, 0, 0]:
                        # This is a black segment - fix its start time
                        if next_segment['startTime'] < segment['endTime']:
                            print(f"    Fixing black segment: was {next_segment['startTime']}s, now {segment['endTime']}s")
                            next_segment['startTime'] = segment['endTime']
                        fixed_segments.append(next_segment)
                        i += 2  # Skip both segments as we've processed them
                    else:
                        i += 1  # Only skip the color segment
                else:
                    i += 1  # Only skip the color segment
            else:
                # This is a black segment that wasn't preceded by a color flash
                fixed_segments.append(segment)
                i += 1
        
        # Update the timeline with fixed segments
        timeline['segments'] = fixed_segments
        
        print(f"  Fixed {len(fixed_segments)} segments")
    
    # Update metadata
    data['metadata']['modified'] = datetime.now().isoformat()
    data['metadata']['name'] = "Alternating Flash 3 Balls (0.25s duration - black segments fixed)"
    data['metadata']['description'] = "Fixed black segments to not overlap with color flashes"
    
    # Write the output file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nFixed file saved as: {output_file}")
    
    # Verify the fix by checking a few segments
    print("\nVerification - checking first few segments of Ball 1:")
    ball1_segments = data['timelines'][0]['segments'][:6]
    for i, seg in enumerate(ball1_segments):
        color_name = "RED" if seg['color'] == [255, 0, 0] else "BLACK"
        print(f"  Segment {i+1}: {color_name} from {seg['startTime']}s to {seg['endTime']}s")

if __name__ == "__main__":
    input_file = "sequence_projects/alternating_flash_3balls/alternating_flash_3balls_025s_corrected.smproj"
    output_file = "sequence_projects/alternating_flash_3balls/alternating_flash_3balls_025s_final.smproj"
    
    fix_black_segments(input_file, output_file)