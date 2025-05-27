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
from .tool_utils.cache_manager import CacheManager

# Add parent directory to path so we can import the AudioAnalyzer
# This might need adjustment if tool_utils is not found directly
# For now, assume standard Python path mechanisms work for sibling directories if run as a module
# or that the package structure is correctly set up.
# If running as `python -m roocode_sequence_designer_tools.extract_audio_features ...`
# then relative imports like `.tool_utils` should work.
# If running directly as `python roocode_sequence_designer_tools/extract_audio_features.py ...`
# then sys.path manipulation might be needed if tool_utils isn't in a standard location.

# Given the project structure, let's try to make sure `tool_utils` can be found.
# One way is to ensure the top-level `roocode_sequence_designer_tools` is in PYTHONPATH
# or the script is run as part of a package.

# The CacheManager is imported via relative path.
# AudioAnalyzerCore will now also be imported via relative path from tool_utils.
# No need for sys.path manipulation here if run as a module within the package.
# _TOOL_DIR = Path(__file__).parent # Not needed if imports are relative
# _PROJECT_ROOT = _TOOL_DIR.parent # Not needed
# sys.path.insert(0, str(_PROJECT_ROOT)) # Not needed


try:
    from .tool_utils.audio_analyzer_core import AudioAnalyzer
except ImportError as e:
    print(f"Error importing AudioAnalyzer from .tool_utils.audio_analyzer_core: {e}", file=sys.stderr)
    # This might happen if script is run directly and not as part of the package.
    # Fallback for direct execution if roocode_sequence_designer_tools is in PYTHONPATH
    try:
        from roocode_sequence_designer_tools.tool_utils.audio_analyzer_core import AudioAnalyzer
        print("Fallback import of AudioAnalyzer successful.", file=sys.stderr)
    except ImportError as e_fallback:
        print(f"Fallback import also failed: {e_fallback}", file=sys.stderr)
        print("Ensure the script is run as a module (e.g., python -m roocode_sequence_designer_tools.extract_audio_features) or PYTHONPATH is set.", file=sys.stderr)
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
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Force re-analysis and do not use or save to cache."
    )
    parser.add_argument(
        "--clear-all-cache",
        action="store_true",
        help="Clear all cache entries for this tool and exit."
    )
    
    # Parse arguments
    args = parser.parse_args()

    cache_manager = CacheManager() # Uses default cache dir

    if args.clear_all_cache:
        # Note: This clears the *entire* cache dir, not just for this tool.
        # A more specific clear would require more complex key prefixing/management.
        print("Clearing all cache entries...")
        cache_manager.clear_all_cache()
        sys.exit(0)
            
    # Validate audio file
    if not os.path.exists(args.audio_file_path):
        print(f"Error: Audio file not found: {args.audio_file_path}", file=sys.stderr)
        sys.exit(1)

    # Prepare analysis parameters for cache key and analysis
    requested_features_list = sorted(list(set(f.strip() for f in args.features.split(',')))) # Normalized
    
    tool_params_for_cache = {
        "features": ",".join(requested_features_list), # Use normalized list
    }
    if args.include_lyrics:
        tool_params_for_cache['include_lyrics'] = True
        if args.conservative_lyrics_alignment:
            tool_params_for_cache['conservative_lyrics_alignment'] = True
        if args.lyrics_text: # Content of lyrics text affects output
            tool_params_for_cache['lyrics_text_hash'] = hashlib.md5(args.lyrics_text.encode('utf-8')).hexdigest()


    cache_key = cache_manager.generate_cache_key(
        identifier="extract_audio_features",
        params=tool_params_for_cache,
        file_path_for_hash=args.audio_file_path
    )

    if not args.no_cache:
        cached_data = cache_manager.load_from_cache(cache_key)
        if cached_data:
            print("Loading result from cache.", file=sys.stderr)
            # Output cached data (respecting --output arg or stdout)
            if args.output:
                try:
                    with open(args.output, 'w') as f:
                        json.dump(cached_data, f, indent=4)
                    print(f"Cached audio features saved to {args.output}")
                except Exception as e:
                    print(f"Error writing cached data to output file: {e}", file=sys.stderr)
                    sys.exit(1)
            else:
                print(json.dumps(cached_data, indent=4))
            sys.exit(0)

    # --- Cache miss or --no-cache: Proceed with analysis ---
    print("Cache not used. Performing new analysis...", file=sys.stderr)
    analyzer = AudioAnalyzer()
    
    try:
        # Prepare analysis parameters for AudioAnalyzer
        audio_analyzer_params = {}
        if args.include_lyrics:
            audio_analyzer_params['request_lyrics'] = True
            if args.conservative_lyrics_alignment:
                audio_analyzer_params['conservative_lyrics_alignment'] = True
            if args.lyrics_text:
                audio_analyzer_params['user_provided_lyrics'] = args.lyrics_text
        
        # Analyze audio
        raw_analysis_data = analyzer.analyze_audio(args.audio_file_path, analysis_params=audio_analyzer_params)
        
        # Process features (this part seems to construct `output_data` from `raw_analysis_data`)
        requested_features = args.features.split(',')
        output_data = {} # This will be the data ultimately saved/printed
        
        # Feature key mapping (from AudioAnalyzer keys to output keys)
        feature_key_mapping = {
            "duration": "duration_seconds",
            "duration_seconds": "duration_seconds",
            "beat_times": "beat_times", # User requests "beat_times"
            "beats": "beat_times",       # AudioAnalyzer provides "beats"
            "downbeat_times": "downbeat_times",
            "downbeats": "downbeat_times",
            "sections": "sections",
            "bpm": "estimated_tempo",
            "tempo": "estimated_tempo",
            "key": "time_signature_guess", # This mapping might be too specific if underlying analysis changes
            "lyrics": "lyrics_info", # User requests "lyrics", this maps to internal structure
            "lyrics_info": "lyrics_info" # Internal key
        }
        
        # Extract requested features from raw_analysis_data into output_data
        for feature_request_key in requested_features_list: # Use normalized list
            # Determine the key in raw_analysis_data and the key for output_data
            actual_analysis_key = feature_request_key # Default if no specific mapping
            final_output_key = feature_request_key

            # Apply mapping: user request -> analysis key -> output key
            # Example: user asks for "beat_times"
            # mapped_analysis_key = feature_key_mapping.get(feature_request_key.lower(), feature_request_key)
            # This mapping logic seems a bit convoluted. Let's simplify.
            # We want to populate output_data based on requested_features_list.

            if feature_request_key == "beat_times":
                if "beats" in raw_analysis_data:
                    output_data["beat_times"] = raw_analysis_data["beats"]
            elif feature_request_key == "downbeat_times":
                if "downbeats" in raw_analysis_data:
                    output_data["downbeat_times"] = raw_analysis_data["downbeats"]
            elif feature_request_key == "duration" or feature_request_key == "duration_seconds":
                 if "duration_seconds" in raw_analysis_data:
                    output_data["duration_seconds"] = raw_analysis_data["duration_seconds"]
            elif feature_request_key == "bpm" or feature_request_key == "tempo":
                if "estimated_tempo" in raw_analysis_data:
                    output_data["estimated_tempo"] = raw_analysis_data["estimated_tempo"]
            elif feature_request_key == "key": # This might be 'time_signature_guess' or similar
                if "time_signature_guess" in raw_analysis_data:
                     output_data["time_signature_guess"] = raw_analysis_data["time_signature_guess"]
                elif "key" in raw_analysis_data: # if analyzer actually returns 'key'
                     output_data["key"] = raw_analysis_data["key"]
            elif feature_request_key == "sections":
                if "sections" in raw_analysis_data:
                    output_data["sections"] = raw_analysis_data["sections"]
            elif feature_request_key == "lyrics":
                if args.include_lyrics and "lyrics_info" in raw_analysis_data:
                    lyrics_info_data = raw_analysis_data["lyrics_info"]
                    output_data["lyrics_word_timestamps"] = lyrics_info_data.get("word_timestamps", [])
                    if lyrics_info_data.get("song_title"):
                        output_data["song_title"] = lyrics_info_data["song_title"]
                    if lyrics_info_data.get("artist_name"):
                        output_data["artist_name"] = lyrics_info_data["artist_name"]
            # Add other direct mappings or features as needed
            elif feature_request_key in raw_analysis_data:
                 output_data[feature_request_key] = raw_analysis_data[feature_request_key]
            else:
                print(f"Warning: Requested feature '{feature_request_key}' not found in analysis results.", file=sys.stderr)

        # Save to cache if enabled
        if not args.no_cache:
            print(f"Saving new analysis to cache (key: {cache_key})", file=sys.stderr)
            cache_manager.save_to_cache(cache_key, output_data)

        # Output results (from output_data)
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
            
            # If lyrics were requested but "lyrics" was not in features, and they were processed,
            # this case should be handled by the feature extraction loop now.
            # The old note might still be relevant if `args.include_lyrics` is true but `lyrics` isn't requested.
            if args.include_lyrics and "lyrics" not in requested_features_list and "lyrics_word_timestamps" not in output_data :
                 if "lyrics_info" in raw_analysis_data : # Check if lyrics processing happened
                    print("\nNote: Lyrics processing was enabled via --include_lyrics, "
                          "but 'lyrics' was not in the --features list, so lyrics data was not included in the primary output.", file=sys.stderr)
                    print("To include lyrics data, add 'lyrics' to the --features parameter.", file=sys.stderr)

    except FileNotFoundError:
        # This specific error for audio file should be caught earlier by os.path.exists
        # but if cache_manager.generate_cache_key fails due to it for some reason.
        print(f"Error: Audio file not found: {args.audio_file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error analyzing audio: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()