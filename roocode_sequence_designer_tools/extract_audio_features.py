#!/usr/bin/env python3
"""
Extract Audio Features CLI Tool

This script extracts audio features from an audio file using the AudioAnalyzer class
and outputs the results in JSON format. It can be used to extract specific features
like beat times, downbeat times, sections, duration, etc.
"""

import json
import argparse
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import the AudioAnalyzer
sys.path.append(str(Path(__file__).parent.parent))

try:
    from roo_code_sequence_maker.audio_analyzer import AudioAnalyzer
except ImportError:
    # Try direct import if package is not installed
    try:
        sys.path.append(str(Path(__file__).parent.parent / "roo-code-sequence-maker"))
        from audio_analyzer import AudioAnalyzer
    except ImportError:
        print("Error: Could not import AudioAnalyzer. Make sure roo-code-sequence-maker is installed or in the correct path.")
        sys.exit(1)


def main():
    """Main function to parse arguments and extract audio features."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Extract audio features from an audio file.")
    parser.add_argument("audio_file_path", help="Path to the input audio file")
    parser.add_argument(
        "--features",
        required=True,
        help="Comma-separated list of features to extract (e.g., beat_times,downbeat_times,sections,duration)"
    )
    parser.add_argument(
        "--output",
        help="Path for the output JSON file. If not provided, print JSON to stdout"
    )
    parser.add_argument(
        "--include_lyrics",
        action="store_true",
        help="Include lyrics information in the output (song title, artist name, and word timestamps)"
    )
    parser.add_argument(
        "--conservative_lyrics_alignment",
        action="store_true",
        help="Use conservative alignment for lyrics processing"
    )
    parser.add_argument(
        "--lyrics_text",
        help="User-provided lyrics text to use instead of automatic identification"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate audio file
    if not os.path.exists(args.audio_file_path):
        print(f"Error: Audio file not found: {args.audio_file_path}", file=sys.stderr)
        sys.exit(1)
    
    # Initialize AudioAnalyzer
    analyzer = AudioAnalyzer()
    
    try:
        # Prepare analysis parameters
        analysis_params = {}
        
        # Add lyrics parameters if requested
        if args.include_lyrics:
            analysis_params['request_lyrics'] = True
            
            if args.conservative_lyrics_alignment:
                analysis_params['conservative_lyrics_alignment'] = True
                
            if args.lyrics_text:
                analysis_params['user_provided_lyrics'] = args.lyrics_text
        
        # Analyze audio
        analysis_data = analyzer.analyze_audio(args.audio_file_path, analysis_params=analysis_params)
        
        # Parse requested features
        requested_features = args.features.split(',')
        output_data = {}
        
        # Feature key mapping (from AudioAnalyzer keys to output keys)
        feature_key_mapping = {
            "duration": "duration_seconds",
            "duration_seconds": "duration_seconds",
            "beat_times": "beat_times",
            "beats": "beat_times",
            "downbeat_times": "downbeat_times",
            "downbeats": "downbeat_times",
            "sections": "sections",
            "bpm": "estimated_tempo",
            "tempo": "estimated_tempo",
            "key": "time_signature_guess",
            "lyrics": "lyrics_info",
            "lyrics_info": "lyrics_info"
        }
        
        # Extract requested features
        for feature_key in requested_features:
            feature_key = feature_key.strip()
            
            # Map the feature key to the corresponding key in analysis_data
            analysis_key = None
            output_key = None
            
            # Direct mapping for common features
            if feature_key.lower() == "beat_times":
                analysis_key = "beats"
                output_key = "beat_times"
            elif feature_key.lower() == "downbeat_times":
                analysis_key = "downbeats"
                output_key = "downbeat_times"
            elif feature_key.lower() == "duration":
                analysis_key = "duration_seconds"
                output_key = "duration_seconds"
            elif feature_key.lower() in ["bpm", "tempo"]:
                analysis_key = "estimated_tempo"
                output_key = "estimated_tempo"
            elif feature_key.lower() == "key":
                analysis_key = "time_signature_guess"
                output_key = "time_signature_guess"
            elif feature_key.lower() == "sections":
                analysis_key = "sections"
                output_key = "sections"
            else:
                # Try to find in the mapping
                for key, value in feature_key_mapping.items():
                    if feature_key.lower() == key.lower():
                        analysis_key = key
                        output_key = value
                        break
            
            # If no mapping found, try using the key directly
            if analysis_key is None:
                analysis_key = feature_key
                output_key = feature_key
            
            # Extract the feature if available
            if analysis_key in analysis_data:
                # Handle special cases
                if analysis_key == "beats":
                    output_data["beat_times"] = analysis_data["beats"]
                    if not analysis_data["beats"]:
                        print(f"Note: Feature '{feature_key}' is available but contains no data (empty list)", file=sys.stderr)
                elif analysis_key == "downbeats":
                    output_data["downbeat_times"] = analysis_data["downbeats"]
                    if not analysis_data["downbeats"]:
                        print(f"Note: Feature '{feature_key}' is available but contains no data (empty list)", file=sys.stderr)
                else:
                    output_data[output_key] = analysis_data[analysis_key]
            else:
                # Special handling for lyrics if requested
                if feature_key.lower() == "lyrics" and args.include_lyrics and "lyrics_info" in analysis_data:
                    lyrics_info = analysis_data["lyrics_info"]
                    
                    # Extract song title and artist name if available
                    if lyrics_info.get("song_title"):
                        output_data["song_title"] = lyrics_info["song_title"]
                    
                    if lyrics_info.get("artist_name"):
                        output_data["artist_name"] = lyrics_info["artist_name"]
                    
                    # Always include word timestamps, even if empty
                    output_data["lyrics_word_timestamps"] = lyrics_info.get("word_timestamps", [])
                else:
                    print(f"Warning: Feature '{feature_key}' not available in analysis data", file=sys.stderr)
        
        # Output results
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    json.dump(output_data, f, indent=4)
                print(f"Audio features saved to {args.output}")
            except Exception as e:
                print(f"Error writing to output file: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            # Print to stdout
            print(json.dumps(output_data, indent=4))
            
            # If lyrics were requested but not included in features, add a note
            if args.include_lyrics and "lyrics_word_timestamps" not in output_data:
                print("\nNote: Lyrics processing was requested but 'lyrics' was not in the features list.", file=sys.stderr)
                print("To include lyrics in the output, add 'lyrics' to the --features parameter.", file=sys.stderr)
                
                # If lyrics were requested but not in features list, add them anyway
                if "lyrics_info" in analysis_data:
                    lyrics_info = analysis_data["lyrics_info"]
                    
                    # Extract song title and artist name if available
                    if lyrics_info.get("song_title"):
                        output_data["song_title"] = lyrics_info["song_title"]
                    
                    if lyrics_info.get("artist_name"):
                        output_data["artist_name"] = lyrics_info["artist_name"]
                    
                    # Always include word timestamps, even if empty
                    output_data["lyrics_word_timestamps"] = lyrics_info.get("word_timestamps", [])
    
    except Exception as e:
        print(f"Error analyzing audio: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()