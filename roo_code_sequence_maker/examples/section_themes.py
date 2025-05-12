#!/usr/bin/env python3
"""
Section Themes Example

This script demonstrates how to create section-based color themes
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
logger = logging.getLogger("SectionThemesExample")

def main():
    # Check if an audio file path was provided
    if len(sys.argv) < 2:
        logger.error("Please provide an audio file path as a command line argument")
        print("Usage: python section_themes.py /path/to/audio.mp3")
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
    
    # Print section information
    print("\n=== Section Information ===")
    sections = analysis_data['sections']
    print(f"Total Sections: {len(sections)}")
    
    for section in sections:
        print(f"- {section['label']}: {section['start']:.2f}s to {section['end']:.2f}s (Duration: {section['end'] - section['start']:.2f}s)")
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Get energy data
    energy_data = analyzer.get_feature_timeseries("energy")
    
    print("\n=== Creating Section Themes ===")
    
    # Example 1: Basic section themes without energy mapping
    print("\nCreating basic section themes (no energy mapping)...")
    
    # Define section themes
    basic_section_themes = [
        {
            "section_label": "Intro",
            "base_color": "blue",
            "energy_mapping": "none"
        },
        {
            "section_label": "Verse 1",
            "base_color": "green",
            "energy_mapping": "none"
        },
        {
            "section_label": "Chorus 1",
            "base_color": "red",
            "energy_mapping": "none"
        },
        {
            "section_label": "Verse 2",
            "base_color": "green",
            "energy_mapping": "none"
        },
        {
            "section_label": "Chorus 2",
            "base_color": "red",
            "energy_mapping": "none"
        },
        {
            "section_label": "Bridge",
            "base_color": "purple",
            "energy_mapping": "none"
        },
        {
            "section_label": "Chorus 3",
            "base_color": "red",
            "energy_mapping": "none"
        },
        {
            "section_label": "Outro",
            "base_color": "blue",
            "energy_mapping": "none"
        }
    ]
    
    # Apply section themes
    basic_theme_segments = generator.apply_section_theme(
        sections=sections,
        section_themes=basic_section_themes,
        default_color="white"
    )
    
    # Save basic theme
    basic_output_path = output_dir / "basic_section_theme.json"
    generator.save_sequence_to_json(basic_theme_segments, basic_output_path)
    print(f"Basic section theme saved to {basic_output_path}")
    
    # Print first few segments
    print("First few segments:")
    for i, segment in enumerate(basic_theme_segments[:min(5, len(basic_theme_segments))]):
        print(f"  {i+1}: {segment['start_time']:.2f}s to {segment['end_time']:.2f}s, Color: {segment['color']}")
    
    # Example 2: Section themes with brightness energy mapping
    print("\nCreating section themes with brightness energy mapping...")
    
    # Define section themes with brightness mapping
    brightness_section_themes = [
        {
            "section_label": "Intro",
            "base_color": "blue",
            "energy_mapping": "brightness"
        },
        {
            "section_label": "Verse 1",
            "base_color": "green",
            "energy_mapping": "brightness"
        },
        {
            "section_label": "Chorus 1",
            "base_color": "red",
            "energy_mapping": "brightness"
        },
        {
            "section_label": "Verse 2",
            "base_color": "green",
            "energy_mapping": "brightness"
        },
        {
            "section_label": "Chorus 2",
            "base_color": "red",
            "energy_mapping": "brightness"
        },
        {
            "section_label": "Bridge",
            "base_color": "purple",
            "energy_mapping": "brightness"
        },
        {
            "section_label": "Chorus 3",
            "base_color": "red",
            "energy_mapping": "brightness"
        },
        {
            "section_label": "Outro",
            "base_color": "blue",
            "energy_mapping": "brightness"
        }
    ]
    
    # Apply section themes with brightness mapping
    brightness_theme_segments = generator.apply_section_theme(
        sections=sections,
        section_themes=brightness_section_themes,
        default_color="white",
        energy_data=energy_data
    )
    
    # Save brightness theme
    brightness_output_path = output_dir / "brightness_section_theme.json"
    generator.save_sequence_to_json(brightness_theme_segments, brightness_output_path)
    print(f"Brightness section theme saved to {brightness_output_path}")
    
    # Example 3: Section themes with saturation energy mapping
    print("\nCreating section themes with saturation energy mapping...")
    
    # Define section themes with saturation mapping
    saturation_section_themes = [
        {
            "section_label": "Intro",
            "base_color": "blue",
            "energy_mapping": "saturation"
        },
        {
            "section_label": "Verse 1",
            "base_color": "green",
            "energy_mapping": "saturation"
        },
        {
            "section_label": "Chorus 1",
            "base_color": "red",
            "energy_mapping": "saturation"
        },
        {
            "section_label": "Verse 2",
            "base_color": "green",
            "energy_mapping": "saturation"
        },
        {
            "section_label": "Chorus 2",
            "base_color": "red",
            "energy_mapping": "saturation"
        },
        {
            "section_label": "Bridge",
            "base_color": "purple",
            "energy_mapping": "saturation"
        },
        {
            "section_label": "Chorus 3",
            "base_color": "red",
            "energy_mapping": "saturation"
        },
        {
            "section_label": "Outro",
            "base_color": "blue",
            "energy_mapping": "saturation"
        }
    ]
    
    # Apply section themes with saturation mapping
    saturation_theme_segments = generator.apply_section_theme(
        sections=sections,
        section_themes=saturation_section_themes,
        default_color="white",
        energy_data=energy_data
    )
    
    # Save saturation theme
    saturation_output_path = output_dir / "saturation_section_theme.json"
    generator.save_sequence_to_json(saturation_theme_segments, saturation_output_path)
    print(f"Saturation section theme saved to {saturation_output_path}")
    
    # Example 4: Mixed energy mapping
    print("\nCreating section themes with mixed energy mapping...")
    
    # Define section themes with mixed mapping
    mixed_section_themes = [
        {
            "section_label": "Intro",
            "base_color": "blue",
            "energy_mapping": "brightness"
        },
        {
            "section_label": "Verse 1",
            "base_color": "green",
            "energy_mapping": "saturation"
        },
        {
            "section_label": "Chorus 1",
            "base_color": "red",
            "energy_mapping": "none"
        },
        {
            "section_label": "Verse 2",
            "base_color": "green",
            "energy_mapping": "saturation"
        },
        {
            "section_label": "Chorus 2",
            "base_color": "red",
            "energy_mapping": "none"
        },
        {
            "section_label": "Bridge",
            "base_color": "purple",
            "energy_mapping": "brightness"
        },
        {
            "section_label": "Chorus 3",
            "base_color": "red",
            "energy_mapping": "none"
        },
        {
            "section_label": "Outro",
            "base_color": "blue",
            "energy_mapping": "brightness"
        }
    ]
    
    # Apply section themes with mixed mapping
    mixed_theme_segments = generator.apply_section_theme(
        sections=sections,
        section_themes=mixed_section_themes,
        default_color="white",
        energy_data=energy_data
    )
    
    # Save mixed theme
    mixed_output_path = output_dir / "mixed_section_theme.json"
    generator.save_sequence_to_json(mixed_theme_segments, mixed_output_path)
    print(f"Mixed section theme saved to {mixed_output_path}")
    
    print("\nAll section themes created successfully!")
    print(f"Output files are in the '{output_dir}' directory")

if __name__ == "__main__":
    main()