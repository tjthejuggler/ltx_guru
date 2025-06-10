#!/usr/bin/env python3
"""
Generate alternating flash sequence for 3 balls.
Ball 1 (red): flashes at 0.25s, 1.0s, 1.75s, etc.
Ball 2 (blue): flashes at 0.5s, 1.25s, 2.0s, etc.
Ball 3 (green): flashes at 0.75s, 1.5s, 2.25s, etc.
Each flash lasts 0.1 seconds.
Total duration: 2 minutes (120 seconds).
"""

import json
from datetime import datetime

def generate_alternating_flash_sequence():
    """Generate the .seqdesign.json file for alternating 3-ball flash sequence."""
    
    # Sequence parameters
    total_duration = 120.0  # 2 minutes
    flash_duration = 0.1    # 0.1 seconds per flash
    cycle_duration = 0.75   # 0.75 seconds per complete cycle (3 balls × 0.25s)
    
    # Ball configurations
    balls = [
        {"id": "ball1", "color": {"name": "red"}, "offset": 0.25},
        {"id": "ball2", "color": {"name": "blue"}, "offset": 0.5},
        {"id": "ball3", "color": {"name": "green"}, "offset": 0.75}
    ]
    
    # Create metadata
    metadata = {
        "title": "Alternating Flash Sequence - 3 Balls",
        "total_duration_seconds": total_duration,
        "target_prg_refresh_rate": 100,
        "default_pixels": 4,
        "default_base_color": {"name": "black"},
        "num_balls": 3
    }
    
    # Generate effects timeline
    effects_timeline = []
    effect_id_counter = 1
    
    for ball in balls:
        ball_id = ball["id"]
        color = ball["color"]
        initial_offset = ball["offset"]
        
        # Generate flash times for this ball
        current_time = initial_offset
        while current_time < total_duration:
            # Create flash effect
            effect = {
                "id": f"flash_{ball_id}_{effect_id_counter}",
                "type": "solid_color",
                "description": f"Flash {ball_id} {color['name']}",
                "timing": {
                    "start_seconds": current_time,
                    "duration_seconds": flash_duration
                },
                "params": {
                    "color": color,
                    "ball_ids": [ball_id]
                }
            }
            effects_timeline.append(effect)
            effect_id_counter += 1
            
            # Move to next flash time (every 0.75 seconds)
            current_time += cycle_duration
    
    # Sort effects by start time
    effects_timeline.sort(key=lambda x: x["timing"]["start_seconds"])
    
    # Create the complete sequence design
    sequence_design = {
        "metadata": metadata,
        "effects_timeline": effects_timeline
    }
    
    return sequence_design

if __name__ == "__main__":
    # Generate the sequence
    sequence = generate_alternating_flash_sequence()
    
    # Save to file
    output_file = "alternating_flash_3balls.seqdesign.json"
    with open(output_file, 'w') as f:
        json.dump(sequence, f, indent=2)
    
    print(f"Generated {output_file} with {len(sequence['effects_timeline'])} flash effects")
    print(f"Total duration: {sequence['metadata']['total_duration_seconds']} seconds")
    
    # Show first few effects as preview
    print("\nFirst 6 effects:")
    for i, effect in enumerate(sequence['effects_timeline'][:6]):
        start = effect['timing']['start_seconds']
        duration = effect['timing']['duration_seconds']
        end = start + duration
        ball_id = effect['params']['ball_ids'][0]
        color = effect['params']['color']['name']
        print(f"  {i+1}. {ball_id} ({color}): {start}s - {end}s")