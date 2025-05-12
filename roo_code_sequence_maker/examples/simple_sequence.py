#!/usr/bin/env python3
"""
Simple Sequence Example

This script demonstrates how to create a simple color sequence without audio analysis.
This is useful for creating basic patterns or for testing purposes.
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sequence_generator import SequenceGenerator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SimpleSequenceExample")

def main():
    # Initialize the generator
    generator = SequenceGenerator()
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    print("\n=== Creating Simple Color Sequences ===")
    
    # Example 1: Basic alternating colors
    print("\nCreating basic alternating colors sequence...")
    
    basic_sequence = generator.create_color_sequence(
        duration=10.0,  # 10 seconds
        colors=["red", "green", "blue"],
        segment_duration=1.0  # 1 second per color
    )
    
    # Save basic sequence
    basic_output_path = output_dir / "basic_sequence.json"
    generator.save_sequence_to_json(basic_sequence, basic_output_path)
    print(f"Basic sequence saved to {basic_output_path}")
    
    # Print segments
    print("Segments:")
    for i, segment in enumerate(basic_sequence):
        print(f"  {i+1}: {segment['start_time']:.2f}s to {segment['end_time']:.2f}s, Color: {segment['color']}")
    
    # Example 2: Rainbow sequence
    print("\nCreating rainbow sequence...")
    
    rainbow_sequence = generator.create_color_sequence(
        duration=14.0,  # 14 seconds
        colors=["red", "orange", "yellow", "green", "blue", "purple", "magenta"],
        segment_duration=2.0  # 2 seconds per color
    )
    
    # Save rainbow sequence
    rainbow_output_path = output_dir / "rainbow_sequence.json"
    generator.save_sequence_to_json(rainbow_sequence, rainbow_output_path)
    print(f"Rainbow sequence saved to {rainbow_output_path}")
    
    # Example 3: Faster sequence with RGB colors
    print("\nCreating fast RGB sequence...")
    
    # Define RGB colors
    rgb_colors = [
        [255, 0, 0],    # Red
        [0, 255, 0],    # Green
        [0, 0, 255]     # Blue
    ]
    
    fast_sequence = generator.create_color_sequence(
        duration=5.0,  # 5 seconds
        colors=rgb_colors,
        segment_duration=0.25  # 0.25 seconds per color (fast changes)
    )
    
    # Save fast sequence
    fast_output_path = output_dir / "fast_rgb_sequence.json"
    generator.save_sequence_to_json(fast_sequence, fast_output_path)
    print(f"Fast RGB sequence saved to {fast_output_path}")
    
    # Example 4: Gradient-like sequence
    print("\nCreating gradient-like sequence...")
    
    # Define a sequence of colors that form a gradient
    gradient_colors = [
        [255, 0, 0],      # Red
        [255, 127, 0],    # Orange
        [255, 255, 0],    # Yellow
        [127, 255, 0],    # Chartreuse
        [0, 255, 0],      # Green
        [0, 255, 127],    # Spring green
        [0, 255, 255],    # Cyan
        [0, 127, 255],    # Azure
        [0, 0, 255],      # Blue
        [127, 0, 255],    # Violet
        [255, 0, 255],    # Magenta
        [255, 0, 127]     # Rose
    ]
    
    gradient_sequence = generator.create_color_sequence(
        duration=24.0,  # 24 seconds
        colors=gradient_colors,
        segment_duration=2.0  # 2 seconds per color
    )
    
    # Save gradient sequence
    gradient_output_path = output_dir / "gradient_sequence.json"
    generator.save_sequence_to_json(gradient_sequence, gradient_output_path)
    print(f"Gradient sequence saved to {gradient_output_path}")
    
    # Example 5: Custom sequence with varying durations
    print("\nCreating custom sequence with manual segments...")
    
    # For a custom sequence with varying durations, we need to create the segments manually
    custom_segments = [
        {"start_time": 0.0, "end_time": 2.0, "color": [255, 0, 0]},    # Red for 2 seconds
        {"start_time": 2.0, "end_time": 2.5, "color": [0, 0, 0]},      # Black for 0.5 seconds
        {"start_time": 2.5, "end_time": 4.5, "color": [0, 255, 0]},    # Green for 2 seconds
        {"start_time": 4.5, "end_time": 5.0, "color": [0, 0, 0]},      # Black for 0.5 seconds
        {"start_time": 5.0, "end_time": 7.0, "color": [0, 0, 255]},    # Blue for 2 seconds
        {"start_time": 7.0, "end_time": 7.5, "color": [0, 0, 0]},      # Black for 0.5 seconds
        {"start_time": 7.5, "end_time": 8.0, "color": [255, 0, 0]},    # Red for 0.5 seconds
        {"start_time": 8.0, "end_time": 8.5, "color": [0, 255, 0]},    # Green for 0.5 seconds
        {"start_time": 8.5, "end_time": 9.0, "color": [0, 0, 255]},    # Blue for 0.5 seconds
        {"start_time": 9.0, "end_time": 10.0, "color": [255, 255, 255]} # White for 1 second
    ]
    
    # Save custom sequence
    custom_output_path = output_dir / "custom_sequence.json"
    generator.save_sequence_to_json(custom_segments, custom_output_path)
    print(f"Custom sequence saved to {custom_output_path}")
    
    print("\nAll sequences created successfully!")
    print(f"Output files are in the '{output_dir}' directory")
    
    print("\nTo use these sequences with LTX balls:")
    print("1. Copy the JSON files to your LTX balls")
    print("2. Use the LTX app to load and play the sequences")
    print("3. Enjoy your colorful juggling experience!")

if __name__ == "__main__":
    main()