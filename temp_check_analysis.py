#!/usr/bin/env python3
"""Temporary script to check the structure of the analysis data."""

import sys
import os
from pathlib import Path

# Add parent directory to path so we can import the AudioAnalyzer
sys.path.append(str(Path(__file__).parent))

try:
    sys.path.append(str(Path(__file__).parent / "roo-code-sequence-maker"))
    from audio_analyzer import AudioAnalyzer
except ImportError:
    print("Error: Could not import AudioAnalyzer.")
    sys.exit(1)

# Initialize AudioAnalyzer
analyzer = AudioAnalyzer()

# Analyze audio
audio_file_path = "sequence_maker/tests/resources/test_audio.mp3"
analysis_data = analyzer.analyze_audio(audio_file_path)

# Print the keys in the analysis data
print("Keys in analysis_data:", list(analysis_data.keys()))

# Print some sample values
print("\nSample values:")
for key in analysis_data.keys():
    value = analysis_data[key]
    if isinstance(value, list) and len(value) > 3:
        print(f"{key}: {value[:3]} ... (total: {len(value)})")
    else:
        print(f"{key}: {value}")