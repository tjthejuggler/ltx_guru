#!/usr/bin/env python3
"""
Split the combined alternating flash sequence into separate per-ball .prg.json files.
"""

import json

def split_prg_to_per_ball():
    """Split the combined .prg.json into separate files for each ball."""
    
    # Load the combined .prg.json file
    with open('alternating_flash_3balls.prg.json', 'r') as f:
        combined_prg = json.load(f)
    
    # Ball color mappings
    ball_colors = {
        1: [255, 0, 0],    # Red
        2: [0, 0, 255],    # Blue  
        3: [0, 255, 0]     # Green
    }
    
    # Create separate sequences for each ball
    for ball_num, ball_color in ball_colors.items():
        # Create a new PRG structure for this ball
        ball_prg = {
            "default_pixels": combined_prg["default_pixels"],
            "refresh_rate": combined_prg["refresh_rate"],
            "end_time": combined_prg["end_time"],
            "color_format": combined_prg["color_format"],
            "sequence": {}
        }
        
        # Filter sequence entries for this ball's color
        for time_unit, entry in combined_prg["sequence"].items():
            if "color" in entry:
                # Check if this entry matches the ball's color
                if entry["color"] == ball_color:
                    # This is a flash for this ball
                    ball_prg["sequence"][time_unit] = entry
                elif entry["color"] == [0, 0, 0]:
                    # This is a black/off state - include it for all balls
                    ball_prg["sequence"][time_unit] = entry
        
        # Write the ball-specific .prg.json file
        output_filename = f"alternating_flash_3balls_Ball_{ball_num}.prg.json"
        with open(output_filename, 'w') as f:
            json.dump(ball_prg, f, indent=2)
        
        print(f"Created {output_filename} with {len(ball_prg['sequence'])} sequence entries")

if __name__ == "__main__":
    split_prg_to_per_ball()
    print("Successfully split combined sequence into per-ball .prg.json files")