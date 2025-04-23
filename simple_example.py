#!/usr/bin/env python3
"""
Simple example demonstrating audio analysis and color sequence generation.

This script:
1. Analyzes an audio file using librosa
2. Extracts beats and sections
3. Creates a beat-synchronized color pattern
4. Saves the resulting color sequence to a JSON file

Usage:
    python simple_example.py /path/to/your/audio.mp3
"""

import sys
import json
import os
import numpy as np
import librosa
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_audio(audio_file_path):
    """
    Analyze audio file to extract musical features.
    
    Args:
        audio_file_path: Path to audio file
        
    Returns:
        dict: Analysis data
    """
    print(f"Loading audio file: {audio_file_path}")
    
    # Load audio using librosa
    try:
        audio_data, sample_rate = librosa.load(audio_file_path, sr=None)
    except Exception as e:
        print(f"Error loading audio file: {e}")
        return None
    
    print("Extracting features...")
    
    # Basic features
    duration = librosa.get_duration(y=audio_data, sr=sample_rate)
    tempo, beat_frames = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
    beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate)
    
    # Derive downbeats (assuming 4/4 time signature)
    downbeats = beat_times[::4]  # Every 4th beat
    
    # Segment analysis for section detection
    mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate)
    segment_boundaries = librosa.segment.agglomerative(mfcc, 8)  # 8 segments
    segment_times = librosa.frames_to_time(segment_boundaries, sr=sample_rate)
    
    # Create labeled sections
    sections = []
    section_labels = ["Intro", "Verse 1", "Chorus 1", "Verse 2", "Chorus 2", "Bridge", "Chorus 3", "Outro"]
    for i in range(len(segment_times) - 1):
        label = section_labels[i] if i < len(section_labels) else f"Section {i+1}"
        sections.append({
            "label": label,
            "start_time": float(segment_times[i]),
            "end_time": float(segment_times[i+1])
        })
    
    # Energy and onset strength
    rms = librosa.feature.rms(y=audio_data)[0]
    onset_env = librosa.onset.onset_strength(y=audio_data, sr=sample_rate)
    
    # Convert numpy arrays to lists for JSON serialization
    times = librosa.times_like(rms, sr=sample_rate)
    
    # Create analysis data structure
    analysis_data = {
        "song_title": os.path.basename(audio_file_path),
        "duration_seconds": float(duration),
        "estimated_tempo": float(tempo),
        "time_signature_guess": "4/4",
        "beats": [float(t) for t in beat_times],
        "downbeats": [float(t) for t in downbeats],
        "sections": sections,
        "energy_timeseries": {
            "times": [float(t) for t in times],
            "values": [float(v) for v in rms]
        }
    }
    
    return analysis_data

def get_beats_in_range(analysis_data, start_time, end_time, beat_type="all"):
    """
    Get beats within a time range.
    
    Args:
        analysis_data: Analysis data
        start_time: Start time in seconds
        end_time: End time in seconds
        beat_type: Type of beats to get ("all" or "downbeat")
        
    Returns:
        list: Beat times within the range
    """
    if not analysis_data:
        return []
    
    if beat_type == "downbeat":
        beats = analysis_data.get("downbeats", [])
    else:
        beats = analysis_data.get("beats", [])
    
    return [beat for beat in beats if start_time <= beat < end_time]

def resolve_color_name(color_input):
    """
    Resolve a color name to RGB values.
    
    Args:
        color_input: Color name or RGB values.
        
    Returns:
        list: RGB values.
    """
    # Color name to RGB mapping
    color_map = {
        "red": [255, 0, 0],
        "green": [0, 255, 0],
        "blue": [0, 0, 255],
        "yellow": [255, 255, 0],
        "cyan": [0, 255, 255],
        "magenta": [255, 0, 255],
        "white": [255, 255, 255],
        "black": [0, 0, 0],
        "orange": [255, 165, 0],
        "purple": [128, 0, 128],
        "pink": [255, 192, 203],
        "brown": [165, 42, 42],
        "gray": [128, 128, 128],
        "grey": [128, 128, 128]
    }
    
    # If already RGB values, return as is
    if isinstance(color_input, list) and len(color_input) == 3:
        return color_input
    
    # If string, try to resolve as color name
    if isinstance(color_input, str):
        return color_map.get(color_input.lower(), [255, 255, 255])  # Default to white if not found
    
    # Default to white if invalid
    return [255, 255, 255]

def create_pulse_pattern(beats, colors, duration):
    """
    Create a pulse pattern.
    
    This pattern creates a short color segment at each beat.
    
    Args:
        beats: List of beat timestamps.
        colors: List of colors to use.
        duration: Duration of each segment.
        
    Returns:
        list: List of segments.
    """
    segments = []
    
    for i, beat in enumerate(beats):
        # Get color (cycle through colors)
        color = colors[i % len(colors)]
        
        # Create segment
        segments.append({
            "start_time": beat,
            "end_time": beat + duration,
            "color": color
        })
    
    return segments

def create_toggle_pattern(beats, colors, duration):
    """
    Create a toggle pattern.
    
    This pattern alternates between colors, with each color lasting until the next beat.
    
    Args:
        beats: List of beat timestamps.
        colors: List of colors to use.
        duration: Not used in this pattern.
        
    Returns:
        list: List of segments.
    """
    segments = []
    
    for i in range(len(beats) - 1):
        # Get color (cycle through colors)
        color = colors[i % len(colors)]
        
        # Create segment from this beat to the next
        segments.append({
            "start_time": beats[i],
            "end_time": beats[i + 1],
            "color": color
        })
    
    # Add final segment if there are beats
    if beats:
        color = colors[(len(beats) - 1) % len(colors)]
        
        # Use the same duration as the previous segment
        if len(beats) > 1:
            last_duration = beats[-1] - beats[-2]
        else:
            last_duration = duration
        
        segments.append({
            "start_time": beats[-1],
            "end_time": beats[-1] + last_duration,
            "color": color
        })
    
    return segments

def visualize_color_sequence(segments, output_file):
    """
    Visualize a color sequence as a timeline.
    
    Args:
        segments: List of segments with start_time, end_time, and color.
        output_file: Path to save the visualization.
    """
    if not segments:
        print("No segments to visualize")
        return
    
    # Determine the total duration
    end_time = max(segment["end_time"] for segment in segments)
    
    # Create a figure
    fig, ax = plt.subplots(figsize=(12, 3))
    
    # Plot each segment
    for segment in segments:
        start = segment["start_time"]
        end = segment["end_time"]
        color = [c/255 for c in segment["color"]]  # Convert 0-255 to 0-1 for matplotlib
        
        ax.axvspan(start, end, color=color, alpha=0.7)
    
    # Set the limits and labels
    ax.set_xlim(0, end_time)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Time (seconds)")
    ax.set_yticks([])
    ax.set_title("Color Sequence Timeline")
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Visualization saved to {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_example.py /path/to/your/audio.mp3")
        return
    
    audio_file_path = sys.argv[1]
    
    # Check if the audio file exists
    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found: {audio_file_path}")
        return
    
    # Step 1: Analyze the audio file
    analysis_data = analyze_audio(audio_file_path)
    
    if not analysis_data:
        print("Failed to analyze audio file.")
        return
    
    print("Audio analysis complete!")
    print(f"Song title: {analysis_data.get('song_title', 'Unknown')}")
    print(f"Duration: {analysis_data.get('duration_seconds', 0):.2f} seconds")
    print(f"Tempo: {analysis_data.get('estimated_tempo', 0):.2f} BPM")
    
    # Step 2: Get beats in a range (first 30 seconds)
    start_time = 0
    end_time = min(30, analysis_data.get('duration_seconds', 0))
    
    beats = get_beats_in_range(analysis_data, start_time, end_time, "all")
    print(f"Found {len(beats)} beats in the first {end_time:.2f} seconds")
    
    # Step 3: Create a beat-synchronized color pattern
    colors = [resolve_color_name(color) for color in ["red", "green", "blue"]]
    
    # Create a pulse pattern
    pulse_segments = create_pulse_pattern(beats, colors, 0.25)
    print(f"Created {len(pulse_segments)} pulse pattern segments")
    
    # Create a toggle pattern
    toggle_segments = create_toggle_pattern(beats, colors, 0.25)
    print(f"Created {len(toggle_segments)} toggle pattern segments")
    
    # Step 4: Save the color sequences to JSON files
    pulse_file = "pulse_pattern.json"
    with open(pulse_file, "w") as f:
        json.dump(pulse_segments, f, indent=2)
    print(f"Pulse pattern saved to {pulse_file}")
    
    toggle_file = "toggle_pattern.json"
    with open(toggle_file, "w") as f:
        json.dump(toggle_segments, f, indent=2)
    print(f"Toggle pattern saved to {toggle_file}")
    
    # Step 5: Visualize the color sequences
    try:
        visualize_color_sequence(pulse_segments, "pulse_pattern.png")
        visualize_color_sequence(toggle_segments, "toggle_pattern.png")
    except Exception as e:
        print(f"Error creating visualizations: {e}")
    
    print("Simple example complete!")

if __name__ == "__main__":
    main()