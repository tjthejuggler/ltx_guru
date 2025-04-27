#!/usr/bin/env python3
"""
Basic Audio Analysis Example

This script demonstrates how to use the AudioAnalyzer class to analyze an audio file
and extract musical features like beats, sections, and energy levels.
"""

import os
import sys
import logging
import matplotlib.pyplot as plt
import numpy as np

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_analyzer import AudioAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BasicAnalysisExample")

def main():
    # Check if an audio file path was provided
    if len(sys.argv) < 2:
        logger.error("Please provide an audio file path as a command line argument")
        print("Usage: python basic_analysis.py /path/to/audio.mp3")
        return
    
    audio_file_path = sys.argv[1]
    
    # Initialize the analyzer
    analyzer = AudioAnalyzer()
    
    # Analyze the audio file
    logger.info(f"Analyzing audio file: {audio_file_path}")
    analysis_data = analyzer.analyze_audio(audio_file_path)
    
    # Print basic metadata
    print("\n=== Song Metadata ===")
    print(f"Title: {analysis_data['song_title']}")
    print(f"Duration: {analysis_data['duration_seconds']:.2f} seconds")
    print(f"Estimated Tempo: {analysis_data['estimated_tempo']:.2f} BPM")
    print(f"Time Signature Guess: {analysis_data['time_signature_guess']}")
    
    # Print beat information
    print("\n=== Beat Information ===")
    print(f"Total Beats: {len(analysis_data['beats'])}")
    print(f"Total Downbeats: {len(analysis_data['downbeats'])}")
    
    if len(analysis_data['beats']) > 0:
        print(f"First 5 Beats: {[f'{b:.2f}s' for b in analysis_data['beats'][:5]]}")
    
    # Print section information
    print("\n=== Section Information ===")
    print(f"Total Sections: {len(analysis_data['sections'])}")
    
    for section in analysis_data['sections']:
        print(f"- {section['label']}: {section['start']:.2f}s to {section['end']:.2f}s (Duration: {section['end'] - section['start']:.2f}s)")
    
    # Get beats in a specific range
    start_time = 10.0
    end_time = 20.0
    beats_in_range = analyzer.get_beats_in_range(start_time, end_time)
    
    print(f"\n=== Beats between {start_time}s and {end_time}s ===")
    print(f"Found {len(beats_in_range)} beats")
    if beats_in_range:
        print(f"Beats: {[f'{b:.2f}s' for b in beats_in_range]}")
    
    # Get a specific section
    section_label = "Chorus 1"
    section = analyzer.get_section_by_label(section_label)
    
    print(f"\n=== Section: {section_label} ===")
    if section:
        print(f"Start: {section['start']:.2f}s")
        print(f"End: {section['end']:.2f}s")
        print(f"Duration: {section['end'] - section['start']:.2f}s")
        
        # Get beats in this section
        section_beats = analyzer.get_beats_in_range(section['start'], section['end'])
        print(f"Beats in section: {len(section_beats)}")
    else:
        print(f"Section '{section_label}' not found")
    
    # Plot energy over time
    energy_data = analyzer.get_feature_timeseries("energy")
    
    plt.figure(figsize=(12, 6))
    plt.plot(energy_data["times"], energy_data["values"])
    plt.title("Energy Over Time")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Energy")
    plt.grid(True)
    
    # Add section markers
    for section in analysis_data['sections']:
        plt.axvline(x=section['start'], color='r', linestyle='--', alpha=0.5)
        plt.text(section['start'], max(energy_data["values"]) * 0.9, section['label'], rotation=90)
    
    # Add beat markers
    for beat in analysis_data['beats'][:50]:  # Limit to first 50 beats to avoid cluttering
        plt.axvline(x=beat, color='g', linestyle='-', alpha=0.2)
    
    # Add downbeat markers
    for downbeat in analysis_data['downbeats'][:20]:  # Limit to first 20 downbeats
        plt.axvline(x=downbeat, color='b', linestyle='-', alpha=0.3)
    
    # Save the plot
    output_path = "energy_plot.png"
    plt.savefig(output_path)
    logger.info(f"Energy plot saved to {output_path}")
    
    print(f"\nEnergy plot saved to {output_path}")
    print("Analysis complete!")

if __name__ == "__main__":
    main()