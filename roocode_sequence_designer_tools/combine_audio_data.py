#!/usr/bin/env python3
"""
Combine Audio Data Tool for Roocode Sequence Designer

This script takes multiple audio analysis JSON files and their corresponding
original audio files, combines their analyses into a single timeline,
and outputs a new consolidated audio analysis JSON file.

Timestamps from subsequent audio files are offset by the cumulative duration
of preceding files. Section labels are prefixed to avoid collisions.
"""

import json
import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add parent directory to path for AudioAnalyzer import
# _TOOL_DIR = Path(__file__).resolve().parent # Not needed
# _PROJECT_ROOT = _TOOL_DIR.parent # Not needed
# if str(_PROJECT_ROOT) not in sys.path: # Not needed
    # sys.path.insert(0, str(_PROJECT_ROOT)) # Not needed

try:
    from .tool_utils.audio_analyzer_core import AudioAnalyzer
except ImportError as e:
    print(f"Error importing AudioAnalyzer from .tool_utils.audio_analyzer_core: {e}", file=sys.stderr)
    try:
        from roocode_sequence_designer_tools.tool_utils.audio_analyzer_core import AudioAnalyzer
        print("Fallback import of AudioAnalyzer successful.", file=sys.stderr)
    except ImportError as e_fallback:
        print(f"Fallback import also failed: {e_fallback}", file=sys.stderr)
        print("Ensure the script is run as a module or PYTHONPATH is set.", file=sys.stderr)
        sys.exit(1)


def get_audio_duration(audio_file_path: str, analyzer: AudioAnalyzer) -> float:
    """
    Gets the duration of an audio file using AudioAnalyzer.
    Returns 0.0 if duration cannot be determined.
    """
    try:
        # Analyze audio just for duration, no complex features needed here.
        # AudioAnalyzer's analyze_audio caches, so this might be quick if previously analyzed.
        # However, we only need duration. A more lightweight method would be ideal if available.
        # For now, using existing analyzer.
        analysis_data = analyzer.analyze_audio(audio_file_path, analysis_params={'request_duration': True})
        duration = analysis_data.get("duration_seconds")
        if duration is None:
            print(f"Warning: Could not determine duration for {audio_file_path} from AudioAnalyzer.", file=sys.stderr)
            return 0.0
        return float(duration)
    except Exception as e:
        print(f"Error getting duration for {audio_file_path}: {e}", file=sys.stderr)
        return 0.0


def offset_timestamps(data: Dict[str, Any], offset: float, file_prefix: str) -> Dict[str, Any]:
    """
    Offsets all relevant timestamps in an audio analysis data structure.
    Also prefixes section labels.
    """
    # Fields that typically contain lists of timestamps (floats)
    timestamp_list_fields = ["beat_times", "downbeat_times", "tatums", "beats", "downbeats"] # Added beats/downbeats variations
    # Fields that contain lists of dicts with 'start' and 'end' keys
    interval_list_fields = ["sections"] 
    # Fields that are timeseries (list of [time, value] or list of dicts with 'time' key)
    timeseries_fields = ["energy", "energy_timeseries", "onset_strength", "onset_strength_timeseries", "tempo_timeseries", "chroma_timeseries"]
    
    adjusted_data = json.loads(json.dumps(data)) # Deep copy

    for field in timestamp_list_fields:
        if field in adjusted_data and isinstance(adjusted_data[field], list):
            # Check if elements are numbers before adding offset
            adjusted_data[field] = [ (ts + offset) if isinstance(ts, (int, float)) else ts for ts in adjusted_data[field] ]


    for field in interval_list_fields:
        if field in adjusted_data and isinstance(adjusted_data[field], list):
            for item in adjusted_data[field]:
                if isinstance(item, dict):
                    if "start" in item and isinstance(item["start"], (int,float)):
                        item["start"] += offset
                    if "end" in item and isinstance(item["end"], (int,float)):
                        item["end"] += offset
                    if field == "sections" and "label" in item:
                        item["label"] = f"{file_prefix}-{item['label']}"
    
    for field in timeseries_fields:
        if field in adjusted_data:
            current_field_data = adjusted_data[field]
            if isinstance(current_field_data, list): 
                if current_field_data and isinstance(current_field_data[0], (list, tuple)): 
                     for point in current_field_data:
                        if len(point) > 0 and isinstance(point[0], (int,float)):
                            point[0] += offset
                elif current_field_data and isinstance(current_field_data[0], dict): 
                    for point in current_field_data:
                        if "time" in point and isinstance(point["time"], (int,float)):
                            point["time"] += offset
            elif isinstance(current_field_data, dict) and "times" in current_field_data and isinstance(current_field_data["times"], list):
                current_field_data["times"] = [ (t + offset) if isinstance(t, (int,float)) else t for t in current_field_data["times"]]
    
    lyrics_data_key = None
    if "lyrics_info" in adjusted_data and isinstance(adjusted_data["lyrics_info"], dict):
        lyrics_data_key = "lyrics_info"
    elif "word_timestamps" in adjusted_data and isinstance(adjusted_data["word_timestamps"], list): # if lyrics are top-level
        # Create a temporary lyrics_info structure for uniform processing
        adjusted_data["lyrics_info"] = {"word_timestamps": adjusted_data.pop("word_timestamps")}
        if "raw_lyrics" in adjusted_data: # move raw_lyrics too
            adjusted_data["lyrics_info"]["raw_lyrics"] = adjusted_data.pop("raw_lyrics")
        lyrics_data_key = "lyrics_info"

    if lyrics_data_key and "word_timestamps" in adjusted_data[lyrics_data_key]:
        for word_event in adjusted_data[lyrics_data_key]["word_timestamps"]:
            if isinstance(word_event, dict):
                if "start" in word_event and isinstance(word_event["start"], (int,float)): 
                    word_event["start"] += offset
                if "end" in word_event and isinstance(word_event["end"], (int,float)): 
                    word_event["end"] += offset
    return adjusted_data


def main():
    parser = argparse.ArgumentParser(
        description="Combine multiple audio analysis JSON files into a single timeline."
    )
    parser.add_argument(
        "--analysis-jsons",
        nargs="+",
        required=True,
        help="List of paths to audio analysis JSON files to combine.",
    )
    parser.add_argument(
        "--audio-files",
        nargs="+",
        required=True,
        help="List of paths to the original audio files, in the same order as --analysis-jsons. Used for duration calculation.",
    )
    parser.add_argument(
        "--output-json",
        required=True,
        help="Path to save the combined audio analysis JSON file.",
    )

    args = parser.parse_args()

    if len(args.analysis_jsons) != len(args.audio_files):
        print("Error: The number of analysis JSON files must match the number of audio files.", file=sys.stderr)
        sys.exit(1)

    combined_analysis = {
        "source_files_info": [],
        "beat_times": [], "downbeat_times": [], "sections": [], "tatums": [], "beats": [], "downbeats": [],
        "energy_timeseries": {"times": [], "values": []}, 
        "onset_strength_timeseries": {"times": [], "values": []},
        "lyrics_info": {"word_timestamps": [], "raw_lyrics": ""}, 
        # For list-based timeseries from some formats
        "energy": [], "onset_strength": [], "tempo_timeseries_list": [], "chroma_timeseries_list": [] 
    }
    
    current_time_offset = 0.0
    analyzer = AudioAnalyzer() 

    for i, (json_path, audio_path) in enumerate(zip(args.analysis_jsons, args.audio_files)):
        print(f"Processing {json_path} and {audio_path}...")
        if not os.path.exists(json_path):
            print(f"Error: Analysis JSON file not found: {json_path}", file=sys.stderr)
            continue
        if not os.path.exists(audio_path):
            print(f"Error: Audio file not found: {audio_path}", file=sys.stderr)
            continue

        try:
            with open(json_path, 'r') as f:
                analysis_content = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {json_path}: {e}", file=sys.stderr)
            continue
        
        duration = get_audio_duration(audio_path, analyzer)
        if duration == 0.0:
            # Try to get duration from analysis_content if available
            duration = analysis_content.get("duration_seconds", 0.0)
            if duration == 0.0:
                 print(f"Warning: Could not get duration for {audio_path}. Skipping this file.", file=sys.stderr)
                 continue
            else:
                print(f"Using duration {duration}s from analysis JSON for {audio_path}", file=sys.stderr)


        file_prefix = f"File{i+1}"
        combined_analysis["source_files_info"].append({
            "original_json_path": json_path,
            "original_audio_path": audio_path,
            "duration": duration,
            "offset_applied": current_time_offset,
            "file_prefix_in_combined": file_prefix
        })

        adjusted_content = offset_timestamps(analysis_content, current_time_offset, file_prefix)

        for key, value in adjusted_content.items():
            if key in ["beat_times", "downbeat_times", "sections", "tatums", "beats", "downbeats"]:
                if isinstance(value, list): combined_analysis.setdefault(key, []).extend(value)
            elif key in ["energy_timeseries", "onset_strength_timeseries"] and isinstance(value, dict) and "times" in value:
                if isinstance(value.get("times"), list): combined_analysis[key].setdefault("times", []).extend(value["times"])
                if isinstance(value.get("values"), list): combined_analysis[key].setdefault("values", []).extend(value["values"])
            elif key in ["energy", "onset_strength", "tempo_timeseries_list", "chroma_timeseries_list"] and isinstance(value, list):
                combined_analysis.setdefault(key, []).extend(value)
            elif key == "lyrics_info" and isinstance(value, dict):
                 if "word_timestamps" in value and isinstance(value["word_timestamps"], list):
                     combined_analysis["lyrics_info"].setdefault("word_timestamps", []).extend(value["word_timestamps"])
                 current_raw = combined_analysis["lyrics_info"].get("raw_lyrics", "")
                 new_raw = value.get("raw_lyrics", "")
                 if new_raw:
                     combined_analysis["lyrics_info"]["raw_lyrics"] = f"{current_raw}\n\n--- {file_prefix} ---\n{new_raw}".strip()
                 if "song_title" not in combined_analysis["lyrics_info"] or combined_analysis["lyrics_info"]["song_title"] == "Combined": # take first
                     combined_analysis["lyrics_info"]["song_title"] = value.get("song_title", "Unknown Title")

            elif key not in combined_analysis: # Store other top-level info from the first file as representative.
                 if key not in ["duration_seconds"]: # duration_seconds is per file, not combined sense here.
                    combined_analysis[key] = value 
        
        current_time_offset += duration

    # Consolidate potentially duplicated timeseries keys
    if combined_analysis.get("energy") and not combined_analysis["energy_timeseries"].get("times"): # if list-based energy exists and dict is empty
        energy_list = combined_analysis.pop("energy")
        combined_analysis["energy_timeseries"]["times"] = [p[0] for p in energy_list if isinstance(p, (list,tuple)) and len(p)>0]
        combined_analysis["energy_timeseries"]["values"] = [p[1] for p in energy_list if isinstance(p, (list,tuple)) and len(p)>1]
    
    if combined_analysis.get("onset_strength") and not combined_analysis["onset_strength_timeseries"].get("times"):
        onset_list = combined_analysis.pop("onset_strength")
        combined_analysis["onset_strength_timeseries"]["times"] = [p[0] for p in onset_list if isinstance(p, (list,tuple)) and len(p)>0]
        combined_analysis["onset_strength_timeseries"]["values"] = [p[1] for p in onset_list if isinstance(p, (list,tuple)) and len(p)>1]


    # Sort all time-based lists
    sortable_time_event_keys = ["beat_times", "downbeat_times", "tatums", "beats", "downbeats"]
    for key in sortable_time_event_keys:
        if key in combined_analysis and isinstance(combined_analysis[key], list):
             # Ensure all elements are sortable (e.g. numbers)
            if all(isinstance(x, (int, float)) for x in combined_analysis[key]):
                combined_analysis[key].sort()
            else:
                print(f"Warning: Cannot sort list for key '{key}' due to non-numeric elements.", file=sys.stderr)


    if "sections" in combined_analysis and isinstance(combined_analysis["sections"], list):
        combined_analysis["sections"].sort(key=lambda x: x.get("start", float('inf')))
    
    if "lyrics_info" in combined_analysis and "word_timestamps" in combined_analysis["lyrics_info"]:
        if isinstance(combined_analysis["lyrics_info"]["word_timestamps"], list):
            combined_analysis["lyrics_info"]["word_timestamps"].sort(key=lambda x: x.get("start", float('inf')))
        if not combined_analysis["lyrics_info"].get("song_title"): # if title wasn't set
            combined_analysis["lyrics_info"]["song_title"] = "Combined Audio Tracks"


    timeseries_to_sort = ["energy_timeseries", "onset_strength_timeseries"]
    for key in timeseries_to_sort:
        if key in combined_analysis and isinstance(combined_analysis[key], dict) and \
           "times" in combined_analysis[key] and "values" in combined_analysis[key] and \
           isinstance(combined_analysis[key]["times"], list) and isinstance(combined_analysis[key]["values"], list):
            
            times = combined_analysis[key]["times"]
            values = combined_analysis[key]["values"]
            if len(times) == len(values) and times: # Check if times is not empty
                # Ensure all elements in times are sortable
                if not all(isinstance(t, (int, float)) for t in times):
                    print(f"Warning: Non-sortable elements in 'times' for {key}. Skipping sort.", file=sys.stderr)
                    continue
                try:
                    sorted_pairs = sorted(zip(times, values), key=lambda p: p[0])
                    combined_analysis[key]["times"] = [p[0] for p in sorted_pairs]
                    combined_analysis[key]["values"] = [p[1] for p in sorted_pairs]
                except TypeError as te:
                     print(f"Warning: TypeError while sorting timeseries {key}. Data: times={times[:5]}, values={values[:5]}. Error: {te}", file=sys.stderr)

            elif times: # Non-empty but mismatched lengths
                 print(f"Warning: Mismatch in times ({len(times)}) and values ({len(values)}) for {key} after combining. Not sorting.", file=sys.stderr)


    combined_analysis["total_duration_combined"] = current_time_offset
    final_output_path = args.output_json
    if not final_output_path.endswith(".analysis.json"):
        base = final_output_path.rsplit('.',1)[0] if '.' in final_output_path else final_output_path
        final_output_path = f"{base}.combined.analysis.json"
        print(f"Adjusting output filename to: {final_output_path}", file=sys.stderr)


    try:
        os.makedirs(os.path.dirname(os.path.abspath(final_output_path)), exist_ok=True)
        with open(final_output_path, 'w') as f:
            json.dump(combined_analysis, f, indent=2)
        print(f"Successfully combined audio analysis data to: {final_output_path}")
    except Exception as e:
        print(f"Error writing combined JSON to {final_output_path}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()