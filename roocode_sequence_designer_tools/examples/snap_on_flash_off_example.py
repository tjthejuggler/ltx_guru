#!/usr/bin/env python3
"""
Example script demonstrating the snap_on_flash_off effect.

This script creates a simple example of the snap_on_flash_off effect
and prints the resulting segments to the console.
"""

from roocode_sequence_designer_tools.effect_implementations import apply_snap_on_flash_off_effect

def main():
    """Run the example."""
    print("Snap-On Flash-Off Effect Example:")
    
    # Example metadata
    example_metadata = {"default_pixels": 4}
    
    # Example snap_on_flash_off effect
    snap_on_flash_off_params = {
        "pre_base_color": {"name": "blue"},
        "target_color": {"name": "white"},
        "post_base_color": {"name": "blue"},
        "fade_out_duration": 1.5,
        "steps_per_second": 10
    }
    
    # Apply the effect from 0.0 to 2.0 seconds
    snap_on_flash_off_segments = apply_snap_on_flash_off_effect(
        0.0, 2.0, snap_on_flash_off_params, example_metadata
    )
    
    print(f"Snap-on flash-off segments: {len(snap_on_flash_off_segments)} segments generated")
    
    # Print the first segment (the flash)
    if snap_on_flash_off_segments:
        print(f"Flash segment: {snap_on_flash_off_segments[0]}")
    
    # Print the first few fade segments
    if len(snap_on_flash_off_segments) > 1:
        print("\nFade segments:")
        for i, segment in enumerate(snap_on_flash_off_segments[1:4]):
            print(f"  Fade segment {i}: {segment}")
        
        if len(snap_on_flash_off_segments) > 5:
            print(f"  ... {len(snap_on_flash_off_segments) - 5} more fade segments ...")
    
    # Example with different parameters
    print("\nAnother example with different colors:")
    
    highlight_params = {
        "pre_base_color": {"rgb": [50, 0, 50]},  # Dark purple
        "target_color": {"rgb": [255, 255, 0]},  # Yellow
        "post_base_color": {"rgb": [50, 0, 50]},  # Dark purple
        "fade_out_duration": 0.8,
        "steps_per_second": 20
    }
    
    # Apply the effect from 0.0 to 1.0 seconds
    highlight_segments = apply_snap_on_flash_off_effect(
        0.0, 1.0, highlight_params, example_metadata
    )
    
    print(f"Generated {len(highlight_segments)} segments")
    
    # Print the first segment (the flash)
    if highlight_segments:
        print(f"Flash segment: {highlight_segments[0]}")
    
    # Print the first few fade segments
    if len(highlight_segments) > 1:
        print("\nFade segments:")
        for i, segment in enumerate(highlight_segments[1:3]):
            print(f"  Fade segment {i}: {segment}")
        
        if len(highlight_segments) > 4:
            print(f"  ... {len(highlight_segments) - 4} more fade segments ...")

if __name__ == "__main__":
    main()