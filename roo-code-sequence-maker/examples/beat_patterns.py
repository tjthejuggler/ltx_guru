#!/usr/bin/env python3
"""
Beat Patterns Example

This script demonstrates how to create beat-synchronized color patterns
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
logger = logging.getLogger("BeatPatternsExample")

def main():
    # Check if an audio file path was provided
    if len(sys.argv) < 2:
        logger.error("Please provide an audio file path as a command line argument")
        print("Usage: python beat_patterns.py /path/to/audio.mp3")
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
    
    # Get beats for the first 30 seconds
    start_time = 0.0
    end_time = 30.0
    beats = analyzer.get_beats_in_range(start_time, end_time)
    
    print(f"\n=== Creating Beat Patterns ===")
    print(f"Using {len(beats)} beats from {start_time}s to {end_time}s")
    
    # Create pulse pattern
    print("\nCreating pulse pattern...")
    pulse_pattern = generator.apply_beat_pattern(
        beats=beats,
        pattern_type="pulse",
        colors=["red", "green", "blue"],
        duration=0.25
    )
    
    # Save pulse pattern
    pulse_output_path = output_dir / "pulse_pattern.json"
    generator.save_sequence_to_json(pulse_pattern, pulse_output_path)
    print(f"Pulse pattern saved to {pulse_output_path}")
    
    # Print first few segments
    print("First 3 segments:")
    for i, segment in enumerate(pulse_pattern[:3]):
        print(f"  {i+1}: {segment['start_time']:.2f}s to {segment['end_time']:.2f}s, Color: {segment['color']}")
    
    # Create toggle pattern
    print("\nCreating toggle pattern...")
    toggle_pattern = generator.apply_beat_pattern(
        beats=beats,
        pattern_type="toggle",
        colors=["yellow", "cyan", "magenta"]
    )
    
    # Save toggle pattern
    toggle_output_path = output_dir / "toggle_pattern.json"
    generator.save_sequence_to_json(toggle_pattern, toggle_output_path)
    print(f"Toggle pattern saved to {toggle_output_path}")
    
    # Print first few segments
    print("First 3 segments:")
    for i, segment in enumerate(toggle_pattern[:3]):
        print(f"  {i+1}: {segment['start_time']:.2f}s to {segment['end_time']:.2f}s, Color: {segment['color']}")
    
    # Create fade-in pattern
    print("\nCreating fade-in pattern...")
    fade_in_pattern = generator.apply_beat_pattern(
        beats=beats,
        pattern_type="fade_in",
        colors=["orange", "purple", "pink"],
        duration=0.5
    )
    
    # Save fade-in pattern
    fade_in_output_path = output_dir / "fade_in_pattern.json"
    generator.save_sequence_to_json(fade_in_pattern, fade_in_output_path)
    print(f"Fade-in pattern saved to {fade_in_output_path}")
    
    # Print first few segments (showing only the first segment of each beat for brevity)
    print("First 3 beats (first segment of each):")
    beat_segments = []
    for segment in fade_in_pattern:
        if any(abs(segment['start_time'] - beat) < 0.01 for beat in beats):
            beat_segments.append(segment)
    
    for i, segment in enumerate(beat_segments[:3]):
        print(f"  {i+1}: {segment['start_time']:.2f}s to {segment['end_time']:.2f}s, Color: {segment['color']}")
    
    # Create fade-out pattern
    print("\nCreating fade-out pattern...")
    fade_out_pattern = generator.apply_beat_pattern(
        beats=beats,
        pattern_type="fade_out",
        colors=["white", "blue", "green"],
        duration=0.5
    )
    
    # Save fade-out pattern
    fade_out_output_path = output_dir / "fade_out_pattern.json"
    generator.save_sequence_to_json(fade_out_pattern, fade_out_output_path)
    print(f"Fade-out pattern saved to {fade_out_output_path}")
    
    # Print first few segments (showing only the first segment of each beat for brevity)
    print("First 3 beats (first segment of each):")
    beat_segments = []
    for segment in fade_out_pattern:
        if any(abs(segment['start_time'] - beat) < 0.01 for beat in beats):
            beat_segments.append(segment)
    
    for i, segment in enumerate(beat_segments[:3]):
        print(f"  {i+1}: {segment['start_time']:.2f}s to {segment['end_time']:.2f}s, Color: {segment['color']}")
    
    # Create a combined pattern using downbeats
    print("\nCreating combined pattern using downbeats...")
    downbeats = analyzer.get_beats_in_range(start_time, end_time, beat_type="downbeat")
    
    # Use pulse pattern for downbeats
    downbeat_pattern = generator.apply_beat_pattern(
        beats=downbeats,
        pattern_type="pulse",
        colors=["red", "yellow", "green", "cyan", "blue", "magenta"],
        duration=0.5
    )
    
    # Save combined pattern
    combined_output_path = output_dir / "combined_pattern.json"
    generator.save_sequence_to_json(downbeat_pattern, combined_output_path)
    print(f"Combined pattern saved to {combined_output_path}")
    
    print("\nAll patterns created successfully!")
    print(f"Output files are in the '{output_dir}' directory")

if __name__ == "__main__":
    main()