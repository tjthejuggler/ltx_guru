#!/usr/bin/env python3
"""
Sequence Designer Compiler

This script compiles a .seqdesign.json file into a .prg.json file.
It handles the transformation of designer-friendly effect definitions
into the PRG format required by the Roocode system.
"""

import json
import argparse
import os
import sys
from typing import Dict, Any, List, Tuple, Optional

# Add the project root to sys.path to allow importing roo_code_sequence_maker
# This assumes 'roocode_sequence_designer_tools' is a direct child of the project root,
# and 'roo-code-sequence-maker' is also a direct child of the project root.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Import AudioAnalyzer for audio-dependent effects
from roocode_sequence_designer_tools.tool_utils.audio_analyzer_core import AudioAnalyzer

# Import effect implementations
from roocode_sequence_designer_tools.effect_implementations import common_effects
from roocode_sequence_designer_tools.effect_implementations import audio_driven_effects

# Import color parsing utilities
from roocode_sequence_designer_tools.tool_utils.color_parser import parse_color


def load_seqdesign_json(file_path: str) -> Dict[str, Any]:
    """
    Load and parse the .seqdesign.json file.
    
    Args:
        file_path: Path to the .seqdesign.json file
        
    Returns:
        Dict containing the parsed JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {file_path}")
        print(f"Details: {str(e)}")
        sys.exit(1)


def validate_metadata(metadata: Dict[str, Any]) -> Tuple[int, int, float, Optional[str], Tuple[int, int, int]]:
    """
    Validate and extract required metadata from the Designer-JSON.
    
    Args:
        metadata: The metadata object from the Designer-JSON
        
    Returns:
        Tuple containing:
            - target_prg_refresh_rate: Integer refresh rate (e.g., 100)
            - default_pixels: Integer default pixel count (e.g., 4)
            - total_duration_seconds: Float duration in seconds
            - full_audio_path: String path to audio file or None
            - default_base_rgb: Tuple of (r, g, b) values
            
    Raises:
        ValueError: If required metadata is missing or invalid
    """
    # Validate target_prg_refresh_rate
    if "target_prg_refresh_rate" not in metadata:
        print("Error: Missing required metadata: target_prg_refresh_rate")
        sys.exit(1)
    
    try:
        target_prg_refresh_rate = int(metadata["target_prg_refresh_rate"])
        if target_prg_refresh_rate <= 0:
            raise ValueError("Refresh rate must be positive")
    except (ValueError, TypeError):
        print(f"Error: Invalid target_prg_refresh_rate: {metadata.get('target_prg_refresh_rate')}")
        sys.exit(1)
    
    # Validate default_pixels
    if "default_pixels" not in metadata:
        print("Error: Missing required metadata: default_pixels")
        sys.exit(1)
    
    try:
        default_pixels = int(metadata["default_pixels"])
        if default_pixels <= 0:
            raise ValueError("Default pixels must be positive")
    except (ValueError, TypeError):
        print(f"Error: Invalid default_pixels: {metadata.get('default_pixels')}")
        sys.exit(1)
    
    # Get default_base_color
    default_base_color = metadata.get("default_base_color", {"name": "black"})
    try:
        default_base_rgb = parse_color(default_base_color)
    except ValueError as e:
        print(f"Warning: Invalid default_base_color: {str(e)}")
        print("Using black (0,0,0) as default base color")
        default_base_rgb = (0, 0, 0)
    
    return target_prg_refresh_rate, default_pixels, 0.0, None, default_base_rgb


def calculate_total_duration(metadata: Dict[str, Any], effects_timeline: List[Dict[str, Any]]) -> float:
    """
    Calculate the total duration of the sequence.
    
    Args:
        metadata: The metadata object from the Designer-JSON
        effects_timeline: The effects_timeline array from the Designer-JSON
        
    Returns:
        Float total duration in seconds
    """
    # Check if total_duration_seconds is explicitly defined in metadata
    if "total_duration_seconds" in metadata:
        try:
            duration = float(metadata["total_duration_seconds"])
            if duration < 0:
                print("Warning: Negative total_duration_seconds in metadata, using 0.0")
                return 0.0
            return duration
        except (ValueError, TypeError):
            print(f"Warning: Invalid total_duration_seconds in metadata: {metadata.get('total_duration_seconds')}")
            # Continue to calculate from effects_timeline
    
    # Calculate from effects_timeline
    if not effects_timeline or not isinstance(effects_timeline, list):
        print("Error: Cannot determine total_duration_seconds. No valid metadata.total_duration_seconds and empty or missing effects_timeline.")
        sys.exit(1)
    
    max_end_time = 0.0
    
    for effect in effects_timeline:
        if not isinstance(effect, dict) or "timing" not in effect:
            continue
        
        timing = effect["timing"]
        
        if "end_seconds" in timing:
            try:
                end_time = float(timing["end_seconds"])
                max_end_time = max(max_end_time, end_time)
            except (ValueError, TypeError):
                continue
        elif "start_seconds" in timing and "duration_seconds" in timing:
            try:
                start_time = float(timing["start_seconds"])
                duration = float(timing["duration_seconds"])
                end_time = start_time + duration
                max_end_time = max(max_end_time, end_time)
            except (ValueError, TypeError):
                continue
    
    if max_end_time <= 0:
        print("Error: Could not determine a valid total_duration_seconds from effects_timeline.")
        sys.exit(1)
    
    return max_end_time


def resolve_audio_path(metadata: Dict[str, Any], audio_dir: str) -> Optional[str]:
    """
    Resolve the full path to the audio file.
    
    Args:
        metadata: The metadata object from the Designer-JSON
        audio_dir: The base directory for resolving relative audio paths
        
    Returns:
        String full path to the audio file, or None if no audio file is specified
    """
    relative_audio_path = metadata.get("audio_file_path")
    
    if not relative_audio_path:
        return None
    
    full_audio_path = os.path.join(audio_dir, relative_audio_path)
    
    # Check if the audio file exists
    if not os.path.isfile(full_audio_path):
        print(f"Warning: Audio file not found: {full_audio_path}")
    
    return full_audio_path


def main() -> None:
    """Main function to orchestrate the compilation process."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Compile a .seqdesign.json file into a .prg.json file")
    
    parser.add_argument("input_seqdesign_json_path", 
                        help="Path to the input .seqdesign.json file")
    
    parser.add_argument("output_prg_json_path", 
                        help="Path for the output .prg.json file")
    
    parser.add_argument("--audio-dir", 
                        help="Path to the directory containing the audio file. "
                             "If metadata.audio_file_path in Designer-JSON is relative, "
                             "this path specifies the base directory for resolving it. "
                             "Default: The directory containing the input .seqdesign.json file's parent directory.")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Determine default audio directory if not provided
    if not args.audio_dir:
        # Default is the parent directory of the parent directory of the input file
        # i.e., [SequenceName] directory
        input_file_dir = os.path.dirname(os.path.abspath(args.input_seqdesign_json_path))
        args.audio_dir = os.path.dirname(input_file_dir)
    
    # Load the input .seqdesign.json file
    print(f"Loading input file: {args.input_seqdesign_json_path}")
    seqdesign_data = load_seqdesign_json(args.input_seqdesign_json_path)
    
    # Access the metadata object
    if "metadata" not in seqdesign_data or not isinstance(seqdesign_data["metadata"], dict):
        print("Error: Missing or invalid metadata in input file")
        sys.exit(1)
    
    metadata = seqdesign_data["metadata"]
    
    # Access the effects_timeline array
    effects_timeline = seqdesign_data.get("effects_timeline", [])
    if not isinstance(effects_timeline, list):
        print("Warning: effects_timeline is not a list, using empty list")
        effects_timeline = []
    
    # Validate and extract metadata
    target_prg_refresh_rate, default_pixels, _, _, default_base_rgb = validate_metadata(metadata)
    
    # Calculate total duration
    total_duration_seconds = calculate_total_duration(metadata, effects_timeline)
    
    # Resolve audio file path
    full_audio_path = resolve_audio_path(metadata, args.audio_dir)
    
    # Print processed metadata for debugging
    print(f"Processed metadata:")
    print(f"  Target PRG Refresh Rate: {target_prg_refresh_rate}")
    print(f"  Default Pixels: {default_pixels}")
    print(f"  Total Duration: {total_duration_seconds} seconds")
    print(f"  Audio File: {full_audio_path if full_audio_path else 'None'}")
    print(f"  Default Base Color: RGB{default_base_rgb}")
    
    # Implement Audio Analysis (if needed)
    audio_analysis_data = None
    
    # Define effect types that require audio analysis
    AUDIO_DEPENDENT_EFFECT_TYPES = ["pulse_on_beat", "apply_section_theme_from_audio"]  # Add more as they are implemented
    
    # Determine if audio analysis is needed
    audio_needed = False
    for effect in effects_timeline:
        if isinstance(effect, dict) and "type" in effect:
            if effect["type"] in AUDIO_DEPENDENT_EFFECT_TYPES:
                audio_needed = True
                break
    
    # Perform analysis if needed
    if audio_needed:
        if full_audio_path is not None and os.path.exists(full_audio_path):
            print(f"Audio analysis required. Analyzing {full_audio_path}...")
            analyzer = AudioAnalyzer()
            audio_analysis_data = analyzer.analyze_audio(full_audio_path)
        else:
            audio_file_msg = "Not specified" if full_audio_path is None else full_audio_path
            print(f"Warning: Audio-dependent effects are present, but the audio file '{audio_file_msg}' was not found or specified. These effects may not work as expected.")
    else:
        print("No audio-dependent effects found. Skipping audio analysis.")
    
    # Effect Timeline Processing & Segment Generation
    print("Processing effects timeline and generating segments...")
    
    # Initialize final_segments with a default segment covering the total duration
    processed_metadata = {
        "default_pixels": default_pixels,
        "target_prg_refresh_rate": target_prg_refresh_rate,
        "default_base_rgb": default_base_rgb
        # Add other metadata as needed by effect implementations
    }
    
    # Initialize with a single segment covering the total duration with default color
    final_segments = []
    if total_duration_seconds > 0:
        final_segments = [(0.0, total_duration_seconds, default_base_rgb, default_pixels)]
    
    # Iterate through each effect in the timeline
    for effect_data in effects_timeline:
        if not isinstance(effect_data, dict):
            print(f"Warning: Skipping invalid effect data (not a dictionary): {effect_data}")
            continue
        
        effect_id = effect_data.get('id', 'Unknown')
        
        # Determine Effect Timing
        timing = effect_data.get("timing", {})
        if not isinstance(timing, dict):
            print(f"Warning: Skipping effect '{effect_id}' due to invalid timing format.")
            continue
        
        effect_start_sec = timing.get("start_seconds")
        effect_end_sec = timing.get("end_seconds")
        duration_sec = timing.get("duration_seconds")
        
        # Validate timing
        if effect_start_sec is None:
            print(f"Warning: Skipping effect '{effect_id}' due to missing start_seconds.")
            continue
        
        try:
            effect_start_sec = float(effect_start_sec)
        except (ValueError, TypeError):
            print(f"Warning: Skipping effect '{effect_id}' due to invalid start_seconds: {effect_start_sec}")
            continue
        
        # Calculate end time if missing
        if effect_end_sec is None and duration_sec is not None:
            try:
                duration_sec = float(duration_sec)
                effect_end_sec = effect_start_sec + duration_sec
            except (ValueError, TypeError):
                print(f"Warning: Skipping effect '{effect_id}' due to invalid duration_seconds: {duration_sec}")
                continue
        # Calculate duration if missing
        elif effect_end_sec is not None and duration_sec is None:
            try:
                effect_end_sec = float(effect_end_sec)
                duration_sec = effect_end_sec - effect_start_sec
            except (ValueError, TypeError):
                print(f"Warning: Skipping effect '{effect_id}' due to invalid end_seconds: {effect_end_sec}")
                continue
        # Both end_seconds and duration_seconds are missing
        elif effect_end_sec is None and duration_sec is None:
            print(f"Warning: Skipping effect '{effect_id}' due to missing end_seconds or duration_seconds.")
            continue
        else:
            # Both are provided, ensure effect_end_sec is a float
            try:
                effect_end_sec = float(effect_end_sec)
            except (ValueError, TypeError):
                print(f"Warning: Skipping effect '{effect_id}' due to invalid end_seconds: {effect_end_sec}")
                continue
        
        # Clamp effect timing to be within 0.0 and total_duration_seconds
        effect_start_sec = max(0.0, min(effect_start_sec, total_duration_seconds))
        effect_end_sec = max(0.0, min(effect_end_sec, total_duration_seconds))
        
        # Skip if effect has zero or negative duration after clamping
        if effect_end_sec <= effect_start_sec:
            print(f"Warning: Skipping effect '{effect_id}' due to invalid timing after clamping: start={effect_start_sec}, end={effect_end_sec}")
            continue
        
        # Identify Effect Type and Parameters
        effect_type = effect_data.get("type")
        if effect_type is None:
            print(f"Warning: Skipping effect '{effect_id}' due to missing effect type.")
            continue
        
        effect_params = effect_data.get("params", {})
        if not isinstance(effect_params, dict):
            print(f"Warning: Skipping effect '{effect_id}' due to invalid params format.")
            continue
        
        # Call Effect Implementation Function
        newly_generated_segments_for_this_effect = []
        
        try:
            effect_type_lower = effect_type.lower() # Convert to lowercase for case-insensitive matching

            if effect_type_lower == "solid_color" or effect_type_lower == "solidcolor":
                newly_generated_segments_for_this_effect = common_effects.apply_solid_color_effect(
                    effect_start_sec, effect_end_sec, effect_params, processed_metadata, audio_analysis_data
                )
            elif effect_type_lower == "fade":
                newly_generated_segments_for_this_effect = common_effects.apply_fade_effect(
                    effect_start_sec, effect_end_sec, effect_params, processed_metadata, audio_analysis_data
                )
            elif effect_type_lower == "pulse_on_beat":
                newly_generated_segments_for_this_effect = audio_driven_effects.apply_pulse_on_beat_effect(
                    effect_start_sec, effect_end_sec, effect_params, processed_metadata, audio_analysis_data
                )
            elif effect_type_lower == "strobe":
                if common_effects:  # Check if module was imported
                    newly_generated_segments_for_this_effect = common_effects.apply_strobe_effect(
                        effect_start_sec, effect_end_sec, effect_params, processed_metadata, audio_analysis_data
                    )
                else:  # Should not happen if imports are correct
                    print(f"Warning: common_effects module not available for effect type '{effect_type_lower}'. Skipping.")
            elif effect_type_lower == "apply_section_theme_from_audio":
                if audio_driven_effects:  # Check if module was imported
                    newly_generated_segments_for_this_effect = audio_driven_effects.apply_section_theme_from_audio_effect(
                        effect_start_sec, effect_end_sec, effect_params, processed_metadata, audio_analysis_data
                    )
                else:  # Should not happen if imports are correct
                    print(f"Warning: audio_driven_effects module not available for effect type '{effect_type_lower}'. Skipping.")
            elif effect_type_lower == "snap_on_flash_off":
                if common_effects:  # Check if module was imported
                    newly_generated_segments_for_this_effect = common_effects.apply_snap_on_flash_off_effect(
                        effect_start_sec, effect_end_sec, effect_params, processed_metadata, audio_analysis_data
                    )
                else:  # Should not happen if imports are correct
                    print(f"Warning: common_effects module not available for effect type '{effect_type_lower}'. Skipping.")
            else:
                print(f"Warning: Unknown effect type '{effect_type}' for effect '{effect_id}'. Skipping.") # Original case in warning is fine
                continue
        except Exception as e:
            print(f"Error applying effect '{effect_id}' of type '{effect_type}': {str(e)}")
            continue
        
        # Merge Segments (Core Override Logic)
        for new_segment in newly_generated_segments_for_this_effect:
            # Unpack the new segment (robustly handling optional 5th element for fades)
            segment_type_marker = None
            if len(new_segment) == 5:
                ns, ne, nc_data, np, segment_type_marker = new_segment
            elif len(new_segment) == 4:
                ns, ne, nc_data, np = new_segment
            else:
                print(f"Warning: Skipping invalid segment structure: {new_segment}")
                continue
            
            # Create a temporary list for the updated timeline segments
            temp_final_segments = []
            
            # Process each existing segment
            for old_segment in final_segments:
                old_segment_type_marker = None
                if len(old_segment) == 5:
                    old_s, old_e, old_c_data, old_p, old_segment_type_marker = old_segment
                elif len(old_segment) == 4:
                    old_s, old_e, old_c_data, old_p = old_segment
                else:
                    # Should not happen if final_segments is always maintained correctly
                    temp_final_segments.append(old_segment)
                    continue

                # Case 1: Old segment is completely before new segment
                if old_e <= ns:
                    temp_final_segments.append(old_segment)
                # Case 2: Old segment is completely after new segment
                elif old_s >= ne:
                    temp_final_segments.append(old_segment)
                # Case 3: Old segment overlaps with new segment
                else:
                    # Part of old segment before new segment
                    if old_s < ns:
                        temp_final_segments.append((old_s, ns, old_c_data, old_p) + ((old_segment_type_marker,) if old_segment_type_marker else ()))
                    # Part of old segment after new segment
                    if old_e > ne:
                        temp_final_segments.append((ne, old_e, old_c_data, old_p) + ((old_segment_type_marker,) if old_segment_type_marker else ()))
            
            # Add the new segment itself
            temp_final_segments.append(new_segment)
            
            # Sort by start time
            temp_final_segments.sort(key=lambda x: x[0])
            
            # Clean up segments (merge adjacent identical segments, remove zero-duration segments)
            cleaned_segments = []
            if temp_final_segments:
                current_segment_tuple = temp_final_segments[0]
                
                for next_segment_tuple in temp_final_segments[1:]:
                    # Unpack current segment robustly
                    curr_s, curr_e, curr_c_data, curr_p = current_segment_tuple[:4]
                    curr_type_marker = current_segment_tuple[4] if len(current_segment_tuple) == 5 else None

                    # Unpack next segment robustly
                    next_s, next_e, next_c_data, next_p = next_segment_tuple[:4]
                    next_type_marker = next_segment_tuple[4] if len(next_segment_tuple) == 5 else None
                    
                    # Merge adjacent identical segments (same color/fade, same pixels, same type)
                    if (next_s == curr_e and
                        next_c_data == curr_c_data and
                        next_p == curr_p and
                        next_type_marker == curr_type_marker):
                        # Extend current_segment_tuple's end time
                        current_segment_tuple = (curr_s, next_e, curr_c_data, curr_p) + ((curr_type_marker,) if curr_type_marker else ())
                    else:
                        # Add current segment if it has positive duration
                        if curr_e > curr_s:
                            cleaned_segments.append(current_segment_tuple)
                        current_segment_tuple = next_segment_tuple
                
                # Add the last segment if it has positive duration
                if current_segment_tuple[1] > current_segment_tuple[0]: # Check end_time > start_time
                    cleaned_segments.append(current_segment_tuple)
            
            # Update final_segments with the cleaned segments
            final_segments = cleaned_segments
    
    # Print summary of generated segments
    print(f"Generated {len(final_segments)} segments for the timeline.")
    
    # Implement PRG-JSON Construction
    print("Constructing PRG-JSON data structure...")
    
    # Initialize the PRG-JSON structure
    prg_json_data = {
        "default_pixels": processed_metadata['default_pixels'],
        "refresh_rate": processed_metadata['target_prg_refresh_rate'],
        "end_time": round(total_duration_seconds * processed_metadata['target_prg_refresh_rate']),
        "color_format": "RGB",  # Standardize to RGB
        "sequence": {}
    }
    
    # Populate the sequence dictionary
    for segment_tuple in final_segments:
        # Unpack segment robustly
        start_time_sec, end_time_sec, color_data, pixels_int = segment_tuple[:4]
        segment_type_marker = segment_tuple[4] if len(segment_tuple) == 5 else None
        
        # Convert start_time_sec to start_time_units
        start_time_units = round(start_time_sec * processed_metadata['target_prg_refresh_rate'])
        
        segment_entry = {"pixels": pixels_int}

        if segment_type_marker == "fade":
            start_color_rgb, end_color_rgb = color_data # color_data is a tuple of (start_rgb, end_rgb)
            segment_entry["start_color"] = list(start_color_rgb)
            segment_entry["end_color"] = list(end_color_rgb)
        else: # Solid color
            segment_entry["color"] = list(color_data) # color_data is a single rgb_tuple

        # Add entry to the sequence dictionary
        # The key must be a string representation of start_time_units
        prg_json_data['sequence'][str(start_time_units)] = segment_entry
    
    # Print summary of the PRG-JSON data
    print(f"PRG-JSON construction complete.")
    print(f"  End time: {prg_json_data['end_time']} units")
    print(f"  Sequence entries: {len(prg_json_data['sequence'])}")
    
    # For debugging, print the PRG-JSON data
    print("PRG-JSON data structure:")
    print(json.dumps(prg_json_data, indent=2))
    
    # Write the PRG-JSON data to the output file
    print(f"Writing output to: {args.output_prg_json_path}")
    try:
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(args.output_prg_json_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Write the JSON data to the file
        with open(args.output_prg_json_path, 'w') as f:
            json.dump(prg_json_data, f, indent=4)
        
        print(f"Successfully compiled '{args.input_seqdesign_json_path}' to '{args.output_prg_json_path}'")
    except IOError as e:
        print(f"Error: Failed to write output file: {args.output_prg_json_path}")
        print(f"Details: {str(e)}")
        sys.exit(1)
    except PermissionError as e:
        print(f"Error: Permission denied when writing to: {args.output_prg_json_path}")
        print(f"Details: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unexpected error when writing output file: {args.output_prg_json_path}")
        print(f"Details: {str(e)}")
        sys.exit(1)
    
    print("Compilation completed successfully")


if __name__ == "__main__":
    main()