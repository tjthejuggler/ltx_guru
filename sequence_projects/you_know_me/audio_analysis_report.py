#!/usr/bin/env python3
"""
Comprehensive Audio Analysis Report Generator

This script performs a complete analysis of the provided audio file using all
available audio analysis capabilities in the system. It documents what works
and what doesn't, saving the results to a detailed report file.
"""

import os
import sys
import json
import time
import logging
import traceback
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Add parent directories to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent.parent))

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

def main():
    """Main function to analyze audio and generate report."""
    # Define the audio file path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    audio_file_path = os.path.join(current_dir, "lubalin_you_know_me.mp3")
    
    # Check if the audio file exists
    if not os.path.exists(audio_file_path):
        logger.error(f"Audio file not found: {audio_file_path}")
        return
    
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
    
    # Initialize the analyzer
    try:
        analyzer = AudioAnalyzer()
        logger.info(f"AudioAnalyzer initialized successfully")
    except Exception as e:
        error_msg = f"Error initializing AudioAnalyzer: {e}"
        logger.error(error_msg)
        report["issues"].append(error_msg)
        create_report_file(report, os.path.join(current_dir, "analysis_report.json"))
        return
    
    # Analyze the audio file
    try:
        # First try without lyrics processing
        logger.info(f"Analyzing audio file: {audio_file_path}")
        analysis_data = analyzer.analyze_audio(audio_file_path)
        
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
        
        # Now try with lyrics processing
        try:
            logger.info("Attempting lyrics processing")
            lyrics_params = {
                'request_lyrics': True,
                'conservative_lyrics_alignment': True
            }
            
            lyrics_analysis = analyzer.analyze_audio(audio_file_path, analysis_params=lyrics_params)
            
            if 'lyrics_info' in lyrics_analysis:
                report["capabilities"]["lyrics_processing"]["working"] = True
                report["analysis_results"]["lyrics_analysis"] = lyrics_analysis['lyrics_info']
                logger.info("Lyrics processing working")
            else:
                report["issues"].append("Lyrics processing not working or no lyrics found")
        except Exception as e:
            error_msg = f"Error during lyrics processing: {e}"
            logger.error(error_msg)
            report["issues"].append(error_msg)
        
        # Create visualizations
        plot_dir = os.path.join(current_dir, "plots")
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
    report_path = os.path.join(current_dir, "analysis_report.json")
    create_report_file(report, report_path)
    
    # Print summary
    print("\n=== Audio Analysis Report Summary ===")
    print(f"Audio file: {os.path.basename(audio_file_path)}")
    print("\nCapabilities Status:")
    for capability, status in report["capabilities"].items():
        working_status = "✅ Working" if status["working"] else "❌ Not working"
        print(f"- {capability.replace('_', ' ').title()}: {working_status}")
    
    print(f"\nIssues found: {len(report['issues'])}")
    for i, issue in enumerate(report["issues"]):
        print(f"{i+1}. {issue}")
    
    print(f"\nFull report saved to: {report_path}")
    if "visualization_path" in report:
        print(f"Visualizations saved to: {report['visualization_path']}")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()