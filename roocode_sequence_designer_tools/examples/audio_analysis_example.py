#!/usr/bin/env python3
"""
Example script demonstrating how to use the audio_analysis_report tool.

This script shows how to generate a comprehensive audio analysis report
for a given audio file, both via command line and programmatically.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import the audio analysis report module
from roocode_sequence_designer_tools.audio_analysis_report import (
    analyze_audio_and_generate_report,
    print_report_summary
)

def main():
    """Main function demonstrating the use of the audio analysis report tool."""
    # Check if an audio file path was provided
    if len(sys.argv) < 2:
        print("Please provide an audio file path as a command line argument")
        print("Usage: python audio_analysis_example.py /path/to/audio.mp3")
        return
    
    audio_file_path = sys.argv[1]
    
    # Check if the audio file exists
    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found: {audio_file_path}")
        return
    
    # Create an output directory for the report
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis_output")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Analyzing audio file: {audio_file_path}")
    print(f"Results will be saved to: {output_dir}")
    
    # Generate the report
    report = analyze_audio_and_generate_report(audio_file_path, output_dir)
    
    # Print a summary of the report
    print_report_summary(report)
    
    # Example of how to access specific data from the report
    if report["capabilities"]["beat_detection"]["working"]:
        beats = report["analysis_results"]["basic_analysis"]["beats"]
        print(f"\nExample of accessing data programmatically:")
        print(f"Number of beats detected: {len(beats)}")
        print(f"First 5 beats (seconds): {beats[:5]}")
    
    if report["capabilities"]["tempo_estimation"]["working"]:
        tempo = report["analysis_results"]["basic_analysis"]["estimated_tempo"]
        print(f"Estimated tempo: {tempo} BPM")
    
    print("\nThis example demonstrates both generating a report and accessing its data programmatically.")
    print("For command-line usage, you can also run:")
    print("python -m roocode_sequence_designer_tools.audio_analysis_report <audio_file_path> [--output-dir <dir>]")

if __name__ == "__main__":
    main()