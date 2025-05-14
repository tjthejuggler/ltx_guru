#!/usr/bin/env python3
"""
Report Size Checker Tool

This script checks the size of audio analysis report files and provides a summary
without loading the entire content into memory. It helps prevent context overload
when working with large analysis reports.
"""

import os
import sys
import json
import argparse
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ReportSizeChecker")

def format_size(size_bytes):
    """Format file size in a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def check_report_size(report_path):
    """
    Check the size of a report file and provide a summary of its structure.
    
    Args:
        report_path (str): Path to the report file
        
    Returns:
        dict: Report size information
    """
    if not os.path.exists(report_path):
        logger.error(f"Report file not found: {report_path}")
        return None
    
    # Get file size
    file_size = os.path.getsize(report_path)
    file_size_formatted = format_size(file_size)
    
    # Check if file is too large for direct loading
    is_large = file_size > 5 * 1024 * 1024  # Consider files > 5MB as large
    
    result = {
        "file_path": report_path,
        "file_size_bytes": file_size,
        "file_size_formatted": file_size_formatted,
        "is_large": is_large,
        "structure": None,
        "sections_count": None,
        "beats_count": None,
        "has_lyrics": None
    }
    
    # For smaller files, we can load and analyze the structure
    if not is_large:
        try:
            with open(report_path, 'r') as f:
                report_data = json.load(f)
            
            # Extract high-level structure
            if isinstance(report_data, dict):
                result["structure"] = list(report_data.keys())
                
                # Check for analysis results
                if "analysis_results" in report_data:
                    analysis_results = report_data["analysis_results"]
                    if "basic_analysis" in analysis_results:
                        basic_analysis = analysis_results["basic_analysis"]
                        
                        # Count sections and beats
                        if "sections" in basic_analysis:
                            result["sections_count"] = len(basic_analysis["sections"])
                        
                        if "beats" in basic_analysis:
                            result["beats_count"] = len(basic_analysis["beats"])
                
                # Check for lyrics
                if "analysis_results" in report_data and "lyrics_analysis" in report_data["analysis_results"]:
                    result["has_lyrics"] = True
                else:
                    result["has_lyrics"] = False
        except Exception as e:
            logger.error(f"Error analyzing report structure: {e}")
    else:
        # For large files, use a streaming approach to extract key information
        try:
            import ijson  # Incremental JSON parser
            
            sections_count = 0
            beats_count = 0
            has_lyrics = False
            
            with open(report_path, 'rb') as f:
                # Check for sections count
                sections_parser = ijson.items(f, 'analysis_results.basic_analysis.sections.item')
                for _ in sections_parser:
                    sections_count += 1
                
                # Reset file pointer
                f.seek(0)
                
                # Check for beats count
                beats_parser = ijson.items(f, 'analysis_results.basic_analysis.beats.item')
                for _ in beats_parser:
                    beats_count += 1
                
                # Reset file pointer
                f.seek(0)
                
                # Check for lyrics
                for prefix, event, value in ijson.parse(f):
                    if prefix == 'analysis_results.lyrics_analysis':
                        has_lyrics = True
                        break
            
            result["sections_count"] = sections_count
            result["beats_count"] = beats_count
            result["has_lyrics"] = has_lyrics
            
        except ImportError:
            logger.warning("ijson not installed. Cannot analyze large files efficiently.")
            logger.warning("Install with: pip install ijson")
            result["note"] = "File is too large to analyze without ijson. Install ijson for better large file handling."
        except Exception as e:
            logger.error(f"Error analyzing large report: {e}")
    
    return result

def print_report_summary(report_info):
    """Print a summary of the report size information."""
    if not report_info:
        return
    
    print("\n=== Audio Analysis Report Size Summary ===")
    print(f"Report file: {os.path.basename(report_info['file_path'])}")
    print(f"File size: {report_info['file_size_formatted']}")
    
    if report_info['is_large']:
        print("\nWARNING: This report is very large and may cause context overflow if loaded entirely.")
        print("Consider using time-range or feature-specific analysis instead.")
    else:
        print("\nThis report is a reasonable size and should be safe to load.")
    
    # Print structure information if available
    if report_info['structure']:
        print("\nReport structure:")
        for key in report_info['structure']:
            print(f"- {key}")
    
    # Print content summary if available
    print("\nContent summary:")
    if report_info['sections_count'] is not None:
        print(f"- Sections: {report_info['sections_count']}")
    if report_info['beats_count'] is not None:
        print(f"- Beats: {report_info['beats_count']}")
    if report_info['has_lyrics'] is not None:
        print(f"- Contains lyrics: {'Yes' if report_info['has_lyrics'] else 'No'}")
    
    if report_info.get('note'):
        print(f"\nNote: {report_info['note']}")
    
    print("\nRecommendations:")
    if report_info['is_large']:
        print("- Use time-range analysis: python -m roocode_sequence_designer_tools.audio_analysis_report <audio_file> --start-time 0 --end-time 60")
        print("- Use feature-specific analysis: python -m roocode_sequence_designer_tools.audio_analysis_report <audio_file> --features beats,sections")
        if report_info['has_lyrics']:
            print("- Use lyrics-only analysis: python -m roocode_sequence_designer_tools.extract_lyrics <audio_file>")
    else:
        print("- This report can be safely viewed in its entirety.")
    
    print("\nAnalysis complete!")

def main():
    """Main function to parse arguments and check report size."""
    parser = argparse.ArgumentParser(description="Check the size of an audio analysis report file.")
    parser.add_argument("report_path", help="Path to the report file to check")
    
    args = parser.parse_args()
    
    # Check report size
    report_info = check_report_size(args.report_path)
    
    # Print summary
    if report_info:
        print_report_summary(report_info)
    else:
        print(f"Error: Could not analyze report at {args.report_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()