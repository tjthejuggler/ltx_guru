#!/usr/bin/env python3
"""
Pattern Templates Tool for Sequence Designer

This tool implements "Parameterized Meta-Effects" or "Pattern Templates" that allow
users to define high-level patterns like "WarningThenEvent" which get expanded
into multiple concrete effects during compilation.

Pattern templates provide a way to encapsulate common, complex temporal relationships
and behaviors into reusable, configurable units.
"""

import json
import argparse
import os
import sys
from typing import Dict, Any, List, Tuple, Optional, Union

def load_synced_lyrics(lyrics_file_path: str) -> Dict[str, Any]:
    """
    Load synced lyrics from a .synced_lyrics.json file.
    
    Args:
        lyrics_file_path: Path to the .synced_lyrics.json file
        
    Returns:
        Dict containing the parsed lyrics data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        with open(lyrics_file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Lyrics file not found: {lyrics_file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in lyrics file: {lyrics_file_path}")
        print(f"Details: {str(e)}")
        sys.exit(1)

def find_word_timestamps(lyrics_data: Dict[str, Any], target_word: str, case_sensitive: bool = False) -> List[float]:
    """
    Find all timestamps for a specific word in the lyrics data.
    
    Args:
        lyrics_data: The loaded synced lyrics data
        target_word: The word to search for
        case_sensitive: Whether to perform case-sensitive matching
        
    Returns:
        List of timestamps (in seconds) where the word occurs
    """
    timestamps = []
    word_timestamps = lyrics_data.get("word_timestamps", [])
    
    search_word = target_word if case_sensitive else target_word.lower()
    
    for word_entry in word_timestamps:
        word_text = word_entry.get("word", "")
        if not case_sensitive:
            word_text = word_text.lower()
        
        if word_text == search_word:
            start_time = word_entry.get("start")
            if start_time is not None:
                timestamps.append(float(start_time))
    
    return timestamps

def expand_warning_then_event_pattern(pattern_config: Dict[str, Any], lyrics_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Expand a "WarningThenEvent" pattern into concrete effect objects.
    
    Args:
        pattern_config: The pattern configuration
        lyrics_data: Optional synced lyrics data for lyric-based triggers
        
    Returns:
        List of concrete effect objects to be added to effects_timeline
    """
    effects = []
    
    # Extract pattern parameters
    params = pattern_config.get("params", {})
    trigger_type = params.get("trigger_type", "lyric")
    warning_offset_seconds = params.get("warning_offset_seconds", -1.0)
    event_definition = params.get("event_definition", {})
    warning_definition = params.get("warning_definition", {})
    target_ball_strategy = params.get("target_ball_selection_strategy", "round_robin")
    
    # Get trigger timestamps based on trigger type
    trigger_timestamps = []
    
    if trigger_type == "lyric":
        trigger_lyric = params.get("trigger_lyric")
        if not trigger_lyric:
            print("Error: trigger_lyric is required for lyric trigger type")
            return effects
        
        if not lyrics_data:
            print("Error: lyrics_data is required for lyric trigger type")
            return effects
        
        case_sensitive = params.get("case_sensitive", False)
        trigger_timestamps = find_word_timestamps(lyrics_data, trigger_lyric, case_sensitive)
        
    elif trigger_type == "custom_times":
        custom_times = params.get("custom_times", [])
        trigger_timestamps = [float(t) for t in custom_times]
        
    elif trigger_type == "beat_number":
        # This would require audio analysis data - placeholder for now
        print("Warning: beat_number trigger type not yet implemented")
        return effects
    
    if not trigger_timestamps:
        print(f"Warning: No trigger timestamps found for pattern")
        return effects
    
    # Generate effects for each trigger timestamp
    ball_counter = 0  # For round-robin ball selection
    
    for i, trigger_time in enumerate(trigger_timestamps):
        # Determine target ball based on strategy
        if target_ball_strategy == "round_robin":
            # Cycle through balls 1, 2, 3, 4
            target_ball = (ball_counter % 4) + 1
            ball_counter += 1
        elif target_ball_strategy == "ball_1":
            target_ball = 1
        elif target_ball_strategy == "ball_2":
            target_ball = 2
        elif target_ball_strategy == "ball_3":
            target_ball = 3
        elif target_ball_strategy == "ball_4":
            target_ball = 4
        elif target_ball_strategy == "random":
            # For now, use modulo - could be enhanced with actual randomization
            target_ball = (i % 4) + 1
        else:
            target_ball = 1  # Default fallback
        
        # Create warning effect
        warning_start_time = trigger_time + warning_offset_seconds
        if warning_start_time >= 0:  # Only create warning if it's not before the start
            warning_effect = {
                "id": f"warning_{pattern_config.get('id', 'pattern')}_{i}",
                "type": warning_definition.get("type", "solid_color"),
                "description": f"Warning effect for pattern trigger at {trigger_time}s",
                "timing": {
                    "start_seconds": warning_start_time,
                    "duration_seconds": warning_definition.get("params", {}).get("duration_seconds", 0.3)
                },
                "params": warning_definition.get("params", {}),
                "target_ball": target_ball
            }
            effects.append(warning_effect)
        
        # Create main event effect
        main_effect = {
            "id": f"event_{pattern_config.get('id', 'pattern')}_{i}",
            "type": event_definition.get("type", "solid_color"),
            "description": f"Main event for pattern trigger at {trigger_time}s",
            "timing": {
                "start_seconds": trigger_time,
                "duration_seconds": event_definition.get("params", {}).get("duration_seconds", 0.5)
            },
            "params": event_definition.get("params", {}),
            "target_ball": target_ball
        }
        effects.append(main_effect)
    
    return effects

def expand_lyric_highlight_pattern(pattern_config: Dict[str, Any], lyrics_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Expand a "LyricHighlight" pattern into concrete effect objects.
    
    Args:
        pattern_config: The pattern configuration
        lyrics_data: Optional synced lyrics data for lyric-based triggers
        
    Returns:
        List of concrete effect objects to be added to effects_timeline
    """
    effects = []
    
    # Extract pattern parameters
    params = pattern_config.get("params", {})
    target_words = params.get("target_words", [])
    effect_definition = params.get("effect_definition", {})
    target_ball_strategy = params.get("target_ball_selection_strategy", "round_robin")
    case_sensitive = params.get("case_sensitive", False)
    
    if not target_words:
        print("Error: target_words is required for LyricHighlight pattern")
        return effects
    
    if not lyrics_data:
        print("Error: lyrics_data is required for LyricHighlight pattern")
        return effects
    
    # Collect all word occurrences with their timestamps
    word_occurrences = []
    for word in target_words:
        timestamps = find_word_timestamps(lyrics_data, word, case_sensitive)
        for timestamp in timestamps:
            word_occurrences.append((timestamp, word))
    
    # Sort by timestamp
    word_occurrences.sort(key=lambda x: x[0])
    
    if not word_occurrences:
        print(f"Warning: No occurrences found for target words: {target_words}")
        return effects
    
    # Generate effects for each word occurrence
    ball_counter = 0  # For round-robin ball selection
    
    for i, (timestamp, word) in enumerate(word_occurrences):
        # Determine target ball based on strategy
        if target_ball_strategy == "round_robin":
            target_ball = (ball_counter % 4) + 1
            ball_counter += 1
        elif target_ball_strategy == "ball_1":
            target_ball = 1
        elif target_ball_strategy == "ball_2":
            target_ball = 2
        elif target_ball_strategy == "ball_3":
            target_ball = 3
        elif target_ball_strategy == "ball_4":
            target_ball = 4
        elif target_ball_strategy == "random":
            target_ball = (i % 4) + 1
        else:
            target_ball = 1  # Default fallback
        
        # Create highlight effect
        highlight_effect = {
            "id": f"highlight_{pattern_config.get('id', 'pattern')}_{word}_{i}",
            "type": effect_definition.get("type", "snap_on_flash_off"),
            "description": f"Highlight effect for word '{word}' at {timestamp}s",
            "timing": {
                "start_seconds": timestamp,
                "duration_seconds": effect_definition.get("params", {}).get("duration_seconds", 0.5)
            },
            "params": effect_definition.get("params", {}),
            "target_ball": target_ball
        }
        effects.append(highlight_effect)
    
    return effects

def expand_beat_sync_pattern(pattern_config: Dict[str, Any], audio_analysis_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Expand a "BeatSync" pattern into concrete effect objects.
    
    Args:
        pattern_config: The pattern configuration
        audio_analysis_data: Optional audio analysis data for beat information
        
    Returns:
        List of concrete effect objects to be added to effects_timeline
    """
    effects = []
    
    # Extract pattern parameters
    params = pattern_config.get("params", {})
    beat_type = params.get("beat_type", "all_beats")
    effect_definition = params.get("effect_definition", {})
    target_ball_strategy = params.get("target_ball_selection_strategy", "round_robin")
    time_window = params.get("time_window", {})
    
    # Get time window
    start_time = time_window.get("start_seconds", 0.0)
    end_time = time_window.get("end_seconds", 300.0)  # Default 5 minutes
    
    # Get beat timestamps (placeholder - would need actual audio analysis)
    beat_timestamps = []
    if audio_analysis_data and "beats" in audio_analysis_data:
        all_beats = audio_analysis_data["beats"]
        if beat_type == "all_beats":
            beat_timestamps = [beat for beat in all_beats if start_time <= beat <= end_time]
        elif beat_type == "downbeats":
            # Would need downbeat detection - for now use every 4th beat
            beat_timestamps = [all_beats[i] for i in range(0, len(all_beats), 4) 
                             if start_time <= all_beats[i] <= end_time]
    
    if not beat_timestamps:
        print(f"Warning: No beat timestamps found for BeatSync pattern")
        return effects
    
    # Generate effects for each beat
    ball_counter = 0  # For round-robin ball selection
    
    for i, beat_time in enumerate(beat_timestamps):
        # Determine target ball based on strategy
        if target_ball_strategy == "round_robin":
            target_ball = (ball_counter % 4) + 1
            ball_counter += 1
        elif target_ball_strategy == "ball_1":
            target_ball = 1
        elif target_ball_strategy == "ball_2":
            target_ball = 2
        elif target_ball_strategy == "ball_3":
            target_ball = 3
        elif target_ball_strategy == "ball_4":
            target_ball = 4
        elif target_ball_strategy == "random":
            target_ball = (i % 4) + 1
        else:
            target_ball = 1  # Default fallback
        
        # Create beat effect
        beat_effect = {
            "id": f"beat_{pattern_config.get('id', 'pattern')}_{i}",
            "type": effect_definition.get("type", "pulse_on_beat"),
            "description": f"Beat sync effect at {beat_time}s",
            "timing": {
                "start_seconds": beat_time,
                "duration_seconds": effect_definition.get("params", {}).get("duration_seconds", 0.1)
            },
            "params": effect_definition.get("params", {}),
            "target_ball": target_ball
        }
        effects.append(beat_effect)
    
    return effects

def expand_pattern_templates(seqdesign_data: Dict[str, Any], lyrics_file_path: Optional[str] = None, audio_analysis_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Expand pattern templates in a seqdesign file into concrete effects.
    
    Args:
        seqdesign_data: The loaded seqdesign.json data
        lyrics_file_path: Optional path to synced lyrics file
        audio_analysis_data: Optional audio analysis data
        
    Returns:
        Modified seqdesign_data with patterns expanded into concrete effects
    """
    # Load lyrics data if provided
    lyrics_data = None
    if lyrics_file_path and os.path.exists(lyrics_file_path):
        lyrics_data = load_synced_lyrics(lyrics_file_path)
    
    # Check if there are pattern templates to expand
    pattern_templates = seqdesign_data.get("pattern_templates", [])
    if not pattern_templates:
        print("No pattern templates found in seqdesign file.")
        return seqdesign_data
    
    # Expand each pattern template
    new_effects = []
    
    for pattern in pattern_templates:
        pattern_type = pattern.get("pattern_type")
        
        if pattern_type == "WarningThenEvent":
            expanded_effects = expand_warning_then_event_pattern(pattern, lyrics_data)
            new_effects.extend(expanded_effects)
            
        elif pattern_type == "LyricHighlight":
            expanded_effects = expand_lyric_highlight_pattern(pattern, lyrics_data)
            new_effects.extend(expanded_effects)
            
        elif pattern_type == "BeatSync":
            expanded_effects = expand_beat_sync_pattern(pattern, audio_analysis_data)
            new_effects.extend(expanded_effects)
            
        else:
            print(f"Warning: Unknown pattern type '{pattern_type}'. Skipping.")
    
    # Add new effects to the effects_timeline
    if "effects_timeline" not in seqdesign_data:
        seqdesign_data["effects_timeline"] = []
    
    seqdesign_data["effects_timeline"].extend(new_effects)
    
    # Remove the pattern_templates section since they've been expanded
    if "pattern_templates" in seqdesign_data:
        del seqdesign_data["pattern_templates"]
    
    print(f"Expanded {len(pattern_templates)} pattern templates into {len(new_effects)} concrete effects.")
    
    return seqdesign_data

def main():
    """Main function for the pattern templates tool."""
    parser = argparse.ArgumentParser(description="Expand pattern templates in a .seqdesign.json file")
    
    parser.add_argument("input_seqdesign_path", 
                        help="Path to the input .seqdesign.json file")
    
    parser.add_argument("output_seqdesign_path", 
                        help="Path for the output .seqdesign.json file with expanded patterns")
    
    parser.add_argument("--lyrics-file", 
                        help="Path to the .synced_lyrics.json file for lyric-based patterns")
    
    parser.add_argument("--audio-analysis", 
                        help="Path to audio analysis data file for beat-based patterns")
    
    args = parser.parse_args()
    
    # Load input file
    try:
        with open(args.input_seqdesign_path, 'r') as f:
            seqdesign_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input_seqdesign_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {args.input_seqdesign_path}")
        print(f"Details: {str(e)}")
        sys.exit(1)
    
    # Load audio analysis data if provided
    audio_analysis_data = None
    if args.audio_analysis and os.path.exists(args.audio_analysis):
        try:
            with open(args.audio_analysis, 'r') as f:
                audio_analysis_data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load audio analysis data: {str(e)}")
    
    # Expand pattern templates
    expanded_seqdesign_data = expand_pattern_templates(
        seqdesign_data, 
        args.lyrics_file, 
        audio_analysis_data
    )
    
    # Write output file
    try:
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(args.output_seqdesign_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(args.output_seqdesign_path, 'w') as f:
            json.dump(expanded_seqdesign_data, f, indent=4)
        
        print(f"Successfully expanded patterns from '{args.input_seqdesign_path}' to '{args.output_seqdesign_path}'")
        
    except Exception as e:
        print(f"Error: Failed to write output file: {args.output_seqdesign_path}")
        print(f"Details: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()