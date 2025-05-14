#!/usr/bin/env python3
"""
Example script demonstrating how to handle large audio analysis reports.

This script shows how to:
1. Check the size of an existing report
2. Generate a report with time range filtering
3. Generate a report with feature selection
4. Extract lyrics with time range filtering

Usage:
    python handling_large_reports_example.py <audio_file_path>
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent.parent))


def check_report_size(report_path):
    """Check the size of an existing report."""
    print("\n=== Checking Report Size ===")
    cmd = [
        "python", "-m", "roocode_sequence_designer_tools.check_report_size",
        report_path
    ]
    subprocess.run(cmd)


def generate_time_filtered_report(audio_path, output_dir, start_time, end_time):
    """Generate a report with time range filtering."""
    print(f"\n=== Generating Report for Time Range {start_time}-{end_time}s ===")
    os.makedirs(output_dir, exist_ok=True)
    cmd = [
        "python", "-m", "roocode_sequence_designer_tools.audio_analysis_report",
        audio_path,
        "--output-dir", output_dir,
        "--start-time", str(start_time),
        "--end-time", str(end_time)
    ]
    subprocess.run(cmd)
    return os.path.join(output_dir, "analysis_report.json")


def generate_feature_filtered_report(audio_path, output_dir, features):
    """Generate a report with feature selection."""
    print(f"\n=== Generating Report with Selected Features: {features} ===")
    os.makedirs(output_dir, exist_ok=True)
    cmd = [
        "python", "-m", "roocode_sequence_designer_tools.audio_analysis_report",
        audio_path,
        "--output-dir", output_dir,
        "--features", features
    ]
    subprocess.run(cmd)
    return os.path.join(output_dir, "analysis_report.json")


def extract_lyrics(audio_path, output_path, start_time=None, end_time=None):
    """Extract lyrics with optional time range filtering."""
    print("\n=== Extracting Lyrics ===")
    cmd = [
        "python", "-m", "roocode_sequence_designer_tools.extract_lyrics",
        audio_path,
        "--output", output_path,
        "--format-text",
        "--include-timestamps"
    ]
    
    if start_time is not None and end_time is not None:
        cmd.extend(["--start-time", str(start_time), "--end-time", str(end_time)])
        print(f"Time range: {start_time}-{end_time}s")
    
    subprocess.run(cmd)
    return output_path


def main():
    """Main function to demonstrate handling large reports."""
    parser = argparse.ArgumentParser(description="Demonstrate handling large audio analysis reports.")
    parser.add_argument("audio_file_path", help="Path to the audio file to analyze")
    
    args = parser.parse_args()
    audio_path = args.audio_file_path
    
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found: {audio_path}")
        sys.exit(1)
    
    # Create output directory
    base_dir = os.path.dirname(audio_path)
    output_base_dir = os.path.join(base_dir, "report_examples")
    os.makedirs(output_base_dir, exist_ok=True)
    
    # Step 1: Generate a complete report
    print("\n=== Generating Complete Report ===")
    complete_report_dir = os.path.join(output_base_dir, "complete")
    os.makedirs(complete_report_dir, exist_ok=True)
    cmd = [
        "python", "-m", "roocode_sequence_designer_tools.audio_analysis_report",
        audio_path,
        "--output-dir", complete_report_dir
    ]
    subprocess.run(cmd)
    complete_report_path = os.path.join(complete_report_dir, "analysis_report.json")
    
    # Step 2: Check the size of the complete report
    check_report_size(complete_report_path)
    
    # Step 3: Generate a time-filtered report (first 60 seconds)
    time_filtered_report_dir = os.path.join(output_base_dir, "time_filtered")
    time_filtered_report_path = generate_time_filtered_report(
        audio_path, time_filtered_report_dir, 0, 60
    )
    
    # Step 4: Check the size of the time-filtered report
    check_report_size(time_filtered_report_path)
    
    # Step 5: Generate a feature-filtered report (beats and sections only)
    feature_filtered_report_dir = os.path.join(output_base_dir, "feature_filtered")
    feature_filtered_report_path = generate_feature_filtered_report(
        audio_path, feature_filtered_report_dir, "beats,sections"
    )
    
    # Step 6: Check the size of the feature-filtered report
    check_report_size(feature_filtered_report_path)
    
    # Step 7: Extract lyrics for the first 60 seconds
    lyrics_output_path = os.path.join(output_base_dir, "lyrics.json")
    extract_lyrics(audio_path, lyrics_output_path, 0, 60)
    
    print("\n=== Example Complete ===")
    print(f"All reports and outputs have been saved to: {output_base_dir}")
    print("\nRecommendation: Use these more focused reports instead of the complete report to avoid context overflow.")


if __name__ == "__main__":
    main()