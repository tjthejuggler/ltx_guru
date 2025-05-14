#!/usr/bin/env python3
"""
Comprehensive Audio Analysis Report Generator

This script performs a complete analysis of the provided audio file using all
available audio analysis capabilities in the system. It documents what works
and what doesn't, saving the results to a detailed report file with visualizations.

This tool leverages the existing extract_audio_features.py tool and adds:
1. Comprehensive capability testing
2. Visualization generation
3. Structured reporting
4. Summary output

Usage:
    python -m roocode_sequence_designer_tools.audio_analysis_report <audio_file_path> [--output-dir <dir>]
"""

import os
import sys
import json
import time
import logging
import argparse
import traceback
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Optional, Union, Any

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

# Import the AudioAnalyzer
try:
    from roo_code_sequence_maker.audio_analyzer import AudioAnalyzer
except ImportError as e:
    print(f"Error importing AudioAnalyzer: {e}")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AudioAnalysisReport")

def create_report_file(report_data, output_path):
    """Save the report data to a JSON file."""
    try:
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        logger.info(f"Report saved to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving report: {e}")
        return False

def plot_audio_features(analysis_data, output_dir):
    """Create visualizations of the audio features."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Plot energy over time
        if 'energy_timeseries' in analysis_data:
            energy_data = analysis_data['energy_timeseries']
            plt.figure(figsize=(12, 6))
            plt.plot(energy_data["times"], energy_data["values"])
            plt.title("Energy Over Time")
            plt.xlabel("Time (seconds)")
            plt.ylabel("Energy")
            plt.grid(True)
            
            # Add section markers if available
            if 'sections' in analysis_data:
                for section in analysis_data['sections']:
                    plt.axvline(x=section['start'], color='r', linestyle='--', alpha=0.5)
                    plt.text(section['start'], max(energy_data["values"]) * 0.9, section['label'], rotation=90)
            
            # Add beat markers if available
            if 'beats' in analysis_data:
                for beat in analysis_data['beats'][:50]:  # Limit to first 50 beats
                    plt.axvline(x=beat, color='g', linestyle='-', alpha=0.2)
            
            # Add downbeat markers if available
            if 'downbeats' in analysis_data:
                for downbeat in analysis_data['downbeats'][:20]:  # Limit to first 20 downbeats
                    plt.axvline(x=downbeat, color='b', linestyle='-', alpha=0.3)
            
            # Save the plot
            energy_plot_path = os.path.join(output_dir, "energy_plot.png")
            plt.savefig(energy_plot_path)
            plt.close()
            logger.info(f"Energy plot saved to {energy_plot_path}")
        
        # 2. Plot onset strength over time
        if 'onset_strength_timeseries' in analysis_data:
            onset_data = analysis_data['onset_strength_timeseries']
            plt.figure(figsize=(12, 6))
            plt.plot(onset_data["times"], onset_data["values"])
            plt.title("Onset Strength Over Time")
            plt.xlabel("Time (seconds)")
            plt.ylabel("Onset Strength")
            plt.grid(True)
            
            # Add beat markers if available
            if 'beats' in analysis_data:
                for beat in analysis_data['beats'][:50]:  # Limit to first 50 beats
                    plt.axvline(x=beat, color='g', linestyle='-', alpha=0.2)
            
            # Save the plot
            onset_plot_path = os.path.join(output_dir, "onset_strength_plot.png")
            plt.savefig(onset_plot_path)
            plt.close()
            logger.info(f"Onset strength plot saved to {onset_plot_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating plots: {e}")
        traceback.print_exc()
        return False

def analyze_audio_and_generate_report(
    audio_file_path: str,
    output_dir: Optional[str] = None,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    features: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Analyze audio file and generate a comprehensive report.
    
    Args:
        audio_file_path (str): Path to the audio file to analyze
        output_dir (str, optional): Directory to save the report and visualizations.
            If not provided, uses the directory containing the audio file.
        start_time (float, optional): Start time in seconds for time-range analysis.
            If provided with end_time, only analyzes the specified time range.
        end_time (float, optional): End time in seconds for time-range analysis.
            If provided with start_time, only analyzes the specified time range.
        features (List[str], optional): List of specific features to include in the report.
            If not provided, includes all features.
            
    Returns:
        dict: The generated report data
    """
    # Determine output directory
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(audio_file_path))
    else:
        os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the report data structure
    report = {
        "audio_file": audio_file_path,
        "analysis_timestamp": time.time(),
        "analysis_results": {},
        "issues": [],
        "capabilities": {
            "beat_detection": {"supported": True, "working": False},
            "section_detection": {"supported": True, "working": False},
            "energy_analysis": {"supported": True, "working": False},
            "onset_strength_analysis": {"supported": True, "working": False},
            "tempo_estimation": {"supported": True, "working": False},
            "time_signature_detection": {"supported": True, "working": False},
            "lyrics_processing": {"supported": True, "working": False}
        }
    }
    
    # Add time range information if provided
    if start_time is not None and end_time is not None:
        report["time_range"] = {
            "start_time": start_time,
            "end_time": end_time,
            "duration": end_time - start_time
        }
    
    # Add feature selection information if provided
    if features:
        report["selected_features"] = features
    
    # Initialize the analyzer
    try:
        analyzer = AudioAnalyzer()
        logger.info(f"AudioAnalyzer initialized successfully")
    except Exception as e:
        error_msg = f"Error initializing AudioAnalyzer: {e}"
        logger.error(error_msg)
        report["issues"].append(error_msg)
        create_report_file(report, os.path.join(output_dir, "analysis_report.json"))
        return report
    
    # Analyze the audio file
    try:
        # First try without lyrics processing
        logger.info(f"Analyzing audio file: {audio_file_path}")
        
        # Prepare analysis parameters
        analysis_params = {}
        
        # Analyze the audio
        analysis_data = analyzer.analyze_audio(audio_file_path, analysis_params=analysis_params)
        
        # Filter data by time range if specified
        if start_time is not None and end_time is not None:
            logger.info(f"Filtering analysis data to time range: {start_time}-{end_time} seconds")
            filtered_data = filter_analysis_by_time_range(analysis_data, start_time, end_time)
            analysis_data = filtered_data
        
        # Filter data by selected features if specified
        if features:
            logger.info(f"Filtering analysis data to selected features: {features}")
            filtered_data = filter_analysis_by_features(analysis_data, features)
            analysis_data = filtered_data
        
        # Store the basic analysis results
        report["analysis_results"]["basic_analysis"] = analysis_data
        
        # Check which capabilities are working
        if 'beats' in analysis_data and analysis_data['beats']:
            report["capabilities"]["beat_detection"]["working"] = True
            logger.info(f"Beat detection working: {len(analysis_data['beats'])} beats found")
        else:
            report["issues"].append("Beat detection not working or no beats found")
        
        if 'sections' in analysis_data and analysis_data['sections']:
            report["capabilities"]["section_detection"]["working"] = True
            logger.info(f"Section detection working: {len(analysis_data['sections'])} sections found")
        else:
            report["issues"].append("Section detection not working or no sections found")
        
        if 'energy_timeseries' in analysis_data:
            report["capabilities"]["energy_analysis"]["working"] = True
            logger.info("Energy analysis working")
        else:
            report["issues"].append("Energy analysis not working")
        
        if 'onset_strength_timeseries' in analysis_data:
            report["capabilities"]["onset_strength_analysis"]["working"] = True
            logger.info("Onset strength analysis working")
        else:
            report["issues"].append("Onset strength analysis not working")
        
        if 'estimated_tempo' in analysis_data:
            report["capabilities"]["tempo_estimation"]["working"] = True
            logger.info(f"Tempo estimation working: {analysis_data['estimated_tempo']} BPM")
        else:
            report["issues"].append("Tempo estimation not working")
        
        if 'time_signature_guess' in analysis_data:
            report["capabilities"]["time_signature_detection"]["working"] = True
            logger.info(f"Time signature detection working: {analysis_data['time_signature_guess']}")
        else:
            report["issues"].append("Time signature detection not working")
        
        # Now try with lyrics processing if requested
        if not features or 'lyrics' in features:
            try:
                logger.info("Attempting lyrics processing")
                lyrics_params = {
                    'request_lyrics': True,
                    'conservative_lyrics_alignment': True
                }
                
                lyrics_analysis = analyzer.analyze_audio(audio_file_path, analysis_params=lyrics_params)
                
                if 'lyrics_info' in lyrics_analysis:
                    report["capabilities"]["lyrics_processing"]["working"] = True
                    
                    # Filter lyrics by time range if specified
                    if start_time is not None and end_time is not None and 'word_timestamps' in lyrics_analysis['lyrics_info']:
                        filtered_words = [
                            word for word in lyrics_analysis['lyrics_info']['word_timestamps']
                            if start_time <= word['start'] < end_time
                        ]
                        lyrics_analysis['lyrics_info']['word_timestamps'] = filtered_words
                        logger.info(f"Filtered lyrics to {len(filtered_words)} words in time range")
                    
                    report["analysis_results"]["lyrics_analysis"] = lyrics_analysis['lyrics_info']
                    logger.info("Lyrics processing working")
                else:
                    report["issues"].append("Lyrics processing not working or no lyrics found")
            except Exception as e:
                error_msg = f"Error during lyrics processing: {e}"
                logger.error(error_msg)
                report["issues"].append(error_msg)
        
        # Create visualizations
        plot_dir = os.path.join(output_dir, "plots")
        plot_success = plot_audio_features(analysis_data, plot_dir)
        if plot_success:
            report["visualization_path"] = plot_dir
        else:
            report["issues"].append("Failed to create visualization plots")
        
    except Exception as e:
        error_msg = f"Error analyzing audio: {e}"
        logger.error(error_msg)
        traceback.print_exc()
        report["issues"].append(error_msg)
    
    # Save the report
    report_path = os.path.join(output_dir, "analysis_report.json")
    create_report_file(report, report_path)
    
    return report

def print_report_summary(report):
    """Print a summary of the analysis report to the console."""
    print("\n=== Audio Analysis Report Summary ===")
    print(f"Audio file: {os.path.basename(report['audio_file'])}")
    print("\nCapabilities Status:")
    for capability, status in report["capabilities"].items():
        working_status = "✅ Working" if status["working"] else "❌ Not working"
        print(f"- {capability.replace('_', ' ').title()}: {working_status}")
    
    print(f"\nIssues found: {len(report['issues'])}")
    for i, issue in enumerate(report["issues"]):
        print(f"{i+1}. {issue}")
    
    report_path = os.path.join(os.path.dirname(report['audio_file']), "analysis_report.json")
    print(f"\nFull report saved to: {report_path}")
    if "visualization_path" in report:
        print(f"Visualizations saved to: {report['visualization_path']}")
    
    print("\nAnalysis complete!")

def filter_analysis_by_time_range(analysis_data, start_time, end_time):
    """
    Filter analysis data to a specific time range.
    
    Args:
        analysis_data (dict): The full analysis data
        start_time (float): Start time in seconds
        end_time (float): End time in seconds
        
    Returns:
        dict: Filtered analysis data
    """
    filtered_data = {}
    
    # Copy non-time-series data
    for key in ['song_title', 'duration_seconds', 'estimated_tempo', 'time_signature_guess']:
        if key in analysis_data:
            filtered_data[key] = analysis_data[key]
    
    # Filter beats
    if 'beats' in analysis_data:
        filtered_data['beats'] = [
            beat for beat in analysis_data['beats']
            if start_time <= beat < end_time
        ]
    
    # Filter downbeats
    if 'downbeats' in analysis_data:
        filtered_data['downbeats'] = [
            beat for beat in analysis_data['downbeats']
            if start_time <= beat < end_time
        ]
    
    # Filter sections
    if 'sections' in analysis_data:
        filtered_data['sections'] = [
            section for section in analysis_data['sections']
            if (section['start'] < end_time and section['end'] > start_time)
        ]
    
    # Filter energy timeseries
    if 'energy_timeseries' in analysis_data:
        times = analysis_data['energy_timeseries']['times']
        values = analysis_data['energy_timeseries']['values']
        
        filtered_times = []
        filtered_values = []
        
        for i, t in enumerate(times):
            if start_time <= t < end_time:
                filtered_times.append(t)
                filtered_values.append(values[i])
        
        filtered_data['energy_timeseries'] = {
            'times': filtered_times,
            'values': filtered_values
        }
    
    # Filter onset strength timeseries
    if 'onset_strength_timeseries' in analysis_data:
        times = analysis_data['onset_strength_timeseries']['times']
        values = analysis_data['onset_strength_timeseries']['values']
        
        filtered_times = []
        filtered_values = []
        
        for i, t in enumerate(times):
            if start_time <= t < end_time:
                filtered_times.append(t)
                filtered_values.append(values[i])
        
        filtered_data['onset_strength_timeseries'] = {
            'times': filtered_times,
            'values': filtered_values
        }
    
    return filtered_data

def filter_analysis_by_features(analysis_data, features):
    """
    Filter analysis data to include only specified features.
    
    Args:
        analysis_data (dict): The full analysis data
        features (list): List of feature names to include
        
    Returns:
        dict: Filtered analysis data
    """
    filtered_data = {}
    
    # Map feature names to keys in analysis_data
    feature_map = {
        'beats': 'beats',
        'downbeats': 'downbeats',
        'sections': 'sections',
        'energy': 'energy_timeseries',
        'onset': 'onset_strength_timeseries',
        'tempo': 'estimated_tempo',
        'time_signature': 'time_signature_guess',
        'duration': 'duration_seconds',
        'song_title': 'song_title'
    }
    
    # Include requested features
    for feature in features:
        feature_key = feature_map.get(feature, feature)
        if feature_key in analysis_data:
            filtered_data[feature_key] = analysis_data[feature_key]
    
    # Always include song_title and duration for context
    if 'song_title' in analysis_data and 'song_title' not in filtered_data:
        filtered_data['song_title'] = analysis_data['song_title']
    
    if 'duration_seconds' in analysis_data and 'duration_seconds' not in filtered_data:
        filtered_data['duration_seconds'] = analysis_data['duration_seconds']
    
    return filtered_data

def main():
    """Main function to parse arguments and run the analysis."""
    parser = argparse.ArgumentParser(description="Generate a comprehensive audio analysis report.")
    parser.add_argument("audio_file_path", help="Path to the audio file to analyze")
    parser.add_argument(
        "--output-dir",
        help="Directory to save the report and visualizations. If not provided, uses the directory containing the audio file."
    )
    parser.add_argument(
        "--start-time",
        type=float,
        help="Start time in seconds for time-range analysis"
    )
    parser.add_argument(
        "--end-time",
        type=float,
        help="End time in seconds for time-range analysis"
    )
    parser.add_argument(
        "--features",
        help="Comma-separated list of features to include in the report (e.g., beats,sections,energy,lyrics)"
    )
    parser.add_argument(
        "--check-size-only",
        action="store_true",
        help="Only check the size of an existing report without generating a new one"
    )
    
    args = parser.parse_args()
    
    # Check if we're only checking the size of an existing report
    if args.check_size_only:
        # Import the report size checker
        try:
            from roocode_sequence_designer_tools.check_report_size import check_report_size, print_report_summary as print_size_summary
            
            # Determine the report path
            if os.path.isdir(args.audio_file_path):
                report_path = os.path.join(args.audio_file_path, "analysis_report.json")
            else:
                report_path = args.audio_file_path
            
            # Check the report size
            report_info = check_report_size(report_path)
            
            # Print the summary
            if report_info:
                print_size_summary(report_info)
            else:
                print(f"Error: Could not analyze report at {report_path}")
                sys.exit(1)
            
            # Exit early
            return
        except ImportError:
            logger.error("Could not import check_report_size module. Continuing with normal analysis.")
    
    # Check if the audio file exists
    if not os.path.exists(args.audio_file_path):
        logger.error(f"Audio file not found: {args.audio_file_path}")
        sys.exit(1)
    
    # Parse features if provided
    features = None
    if args.features:
        features = [f.strip() for f in args.features.split(',')]
    
    # Run the analysis
    report = analyze_audio_and_generate_report(
        args.audio_file_path,
        args.output_dir,
        args.start_time,
        args.end_time,
        features
    )
    
    # Print the summary
    print_report_summary(report)

if __name__ == "__main__":
    main()