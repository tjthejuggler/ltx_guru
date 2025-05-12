#!/usr/bin/env python3
"""
Multiple Balls Example

This script demonstrates how to create color sequences for multiple juggling balls
using the AudioAnalyzer and SequenceGenerator classes.
"""

import os
import sys
import logging
import json
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_analyzer import AudioAnalyzer
from sequence_generator import SequenceGenerator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MultipleBallsExample")

def main():
    # Check if an audio file path was provided
    if len(sys.argv) < 2:
        logger.error("Please provide an audio file path as a command line argument")
        print("Usage: python multiple_balls.py /path/to/audio.mp3")
        return
    
    audio_file_path = sys.argv[1]
    
    # Initialize the analyzer and generator
    analyzer = AudioAnalyzer()
    generator = SequenceGenerator()
    
    # Analyze the audio file
    logger.info(f"Analyzing audio file: {audio_file_path}")
    analysis_data = analyzer.analyze_audio(audio_file_path)
    
    # Print basic metadata
    print("\n=== Song Metadata ===")
    print(f"Title: {analysis_data['song_title']}")
    print(f"Duration: {analysis_data['duration_seconds']:.2f} seconds")
    print(f"Estimated Tempo: {analysis_data['estimated_tempo']:.2f} BPM")
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Get beats and sections
    beats = analysis_data['beats']
    sections = analysis_data['sections']
    energy_data = analyzer.get_feature_timeseries("energy")
    
    print(f"\n=== Creating Sequences for Multiple Balls ===")
    print(f"Using {len(beats)} beats and {len(sections)} sections")
    
    # Create sequences for three balls
    sequences = []
    
    # Ball 1: Beat-synchronized pulse pattern with warm colors
    print("\nCreating sequence for Ball 1: Beat-synchronized pulse pattern with warm colors")
    ball1_sequence = generator.apply_beat_pattern(
        beats=beats,
        pattern_type="pulse",
        colors=["red", "orange", "yellow"],
        duration=0.25
    )
    sequences.append(ball1_sequence)
    
    # Ball 2: Beat-synchronized toggle pattern with cool colors
    print("\nCreating sequence for Ball 2: Beat-synchronized toggle pattern with cool colors")
    ball2_sequence = generator.apply_beat_pattern(
        beats=beats,
        pattern_type="toggle",
        colors=["green", "cyan", "blue"]
    )
    sequences.append(ball2_sequence)
    
    # Ball 3: Section-based themes
    print("\nCreating sequence for Ball 3: Section-based themes with energy mapping")
    
    # Define section themes
    section_themes = [
        {
            "section_label": "Intro",
            "base_color": "purple",
            "energy_mapping": "brightness"
        },
        {
            "section_label": "Verse 1",
            "base_color": "magenta",
            "energy_mapping": "saturation"
        },
        {
            "section_label": "Chorus 1",
            "base_color": "white",
            "energy_mapping": "none"
        },
        {
            "section_label": "Verse 2",
            "base_color": "magenta",
            "energy_mapping": "saturation"
        },
        {
            "section_label": "Chorus 2",
            "base_color": "white",
            "energy_mapping": "none"
        },
        {
            "section_label": "Bridge",
            "base_color": "purple",
            "energy_mapping": "brightness"
        },
        {
            "section_label": "Chorus 3",
            "base_color": "white",
            "energy_mapping": "none"
        },
        {
            "section_label": "Outro",
            "base_color": "purple",
            "energy_mapping": "brightness"
        }
    ]
    
    ball3_sequence = generator.apply_section_theme(
        sections=sections,
        section_themes=section_themes,
        default_color="black",
        energy_data=energy_data
    )
    sequences.append(ball3_sequence)
    
    # Save sequences to JSON files
    for i, sequence in enumerate(sequences):
        output_path = output_dir / f"ball_{i+1}.json"
        generator.save_sequence_to_json(sequence, output_path)
        print(f"Sequence for Ball {i+1} saved to {output_path}")
    
    # Create a visualization of the sequences
    print("\nCreating visualization of the sequences...")
    
    # Create a simple text-based visualization
    visualization_path = output_dir / "sequence_visualization.txt"
    
    with open(visualization_path, 'w') as f:
        f.write(f"Sequence Visualization for {analysis_data['song_title']}\n")
        f.write("=" * 80 + "\n\n")
        
        # Determine the time range to visualize (first 30 seconds or full duration if shorter)
        max_time = min(30.0, analysis_data['duration_seconds'])
        time_step = 0.5  # 0.5 second intervals
        
        # Write header
        f.write(f"Time (s) | Ball 1 | Ball 2 | Ball 3 |\n")
        f.write("-" * 40 + "\n")
        
        # Write visualization
        current_time = 0.0
        while current_time <= max_time:
            # Find colors for each ball at this time
            colors = []
            
            for sequence in sequences:
                # Find the segment that contains this time
                color = "      "  # Default empty color
                
                for segment in sequence:
                    if segment['start_time'] <= current_time < segment['end_time']:
                        # Convert RGB to a simple color name or code
                        rgb = segment['color']
                        if rgb == [255, 0, 0]:
                            color = "  RED "
                        elif rgb == [0, 255, 0]:
                            color = " GREEN"
                        elif rgb == [0, 0, 255]:
                            color = " BLUE "
                        elif rgb == [255, 255, 0]:
                            color = "YELLOW"
                        elif rgb == [0, 255, 255]:
                            color = " CYAN "
                        elif rgb == [255, 0, 255]:
                            color = "MAGENT"
                        elif rgb == [255, 165, 0]:
                            color = "ORANGE"
                        elif rgb == [128, 0, 128]:
                            color = "PURPLE"
                        elif rgb == [255, 255, 255]:
                            color = "WHITE "
                        elif rgb == [0, 0, 0]:
                            color = "BLACK "
                        else:
                            # Use RGB code for other colors
                            r, g, b = rgb
                            color = f"{r:02X}{g:02X}{b:02X}"
                        break
                
                colors.append(color)
            
            # Write line
            f.write(f"{current_time:7.1f} | {colors[0]} | {colors[1]} | {colors[2]} |\n")
            
            # Increment time
            current_time += time_step
        
        # Write footer
        f.write("\nNote: This is a simplified visualization. The actual sequences contain more detailed color information.\n")
    
    print(f"Visualization saved to {visualization_path}")
    
    # Create a combined visualization showing all balls together
    print("\nCreating a combined sequence for all balls...")
    
    # For this example, we'll create a simple alternating pattern
    # In a real application, you might want to create more complex combinations
    
    combined_sequence = []
    
    # Determine the time range (use the full duration)
    max_time = analysis_data['duration_seconds']
    
    # Create segments that alternate between balls every 4 beats
    beat_groups = []
    for i in range(0, len(beats), 4):
        if i + 3 < len(beats):
            beat_groups.append((beats[i], beats[i+3]))
    
    # If there are no complete groups, use the whole duration
    if not beat_groups:
        beat_groups = [(0, max_time)]
    
    # Create alternating segments
    ball_index = 0
    for start, end in beat_groups:
        # Find segments from the current ball that fall within this range
        ball_sequence = sequences[ball_index]
        
        for segment in ball_sequence:
            if segment['start_time'] >= start and segment['end_time'] <= end:
                combined_sequence.append(segment)
        
        # Move to the next ball
        ball_index = (ball_index + 1) % len(sequences)
    
    # Sort the combined sequence by start time
    combined_sequence.sort(key=lambda x: x['start_time'])
    
    # Save the combined sequence
    combined_output_path = output_dir / "combined_sequence.json"
    generator.save_sequence_to_json(combined_sequence, combined_output_path)
    print(f"Combined sequence saved to {combined_output_path}")
    
    print("\nAll sequences created successfully!")
    print(f"Output files are in the '{output_dir}' directory")

if __name__ == "__main__":
    main()