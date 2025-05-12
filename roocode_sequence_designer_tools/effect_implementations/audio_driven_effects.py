#!/usr/bin/env python3
"""
Audio-Driven Effects Module for Roocode Sequence Designer Tools

This module provides implementations for audio-driven lighting effects:
- Pulse on Beat: Creates pulses of color that align with detected beats in the audio
- Section Theme from Audio: Applies different color themes based on audio sections
"""

from typing import Dict, List, Tuple, Optional, Any
import ast
import re

# Import color utilities
from roocode_sequence_designer_tools.tool_utils.color_parser import parse_color
from roo_code_sequence_maker.utils.color_utils import rgb_to_hsv, hsv_to_rgb


def apply_pulse_on_beat_effect(
    effect_start_sec: float,
    effect_end_sec: float,
    params: Dict[str, Any],
    metadata: Dict[str, Any],
    audio_analysis_data: Optional[Dict] = None
) -> List[Tuple[float, float, Tuple[int, int, int], int]]:
    """
    Apply a pulse-on-beat effect that creates color pulses aligned with audio beats.
    
    Args:
        effect_start_sec: Start time of the effect in seconds
        effect_end_sec: End time of the effect in seconds
        params: Dictionary of parameters for this effect instance
                Expected to contain:
                - 'color': Color specification for the pulse
                - 'pulse_duration_seconds': Duration of each pulse in seconds
                - 'beat_source': Optional, source of beat times (default: 'all_beats')
                  Can be 'all_beats', 'downbeats', or 'custom_times: [t1, t2, ...]'
        metadata: The metadata section from the .seqdesign.json file
                 Expected to contain 'default_pixels' key
        audio_analysis_data: Audio analysis data containing beat times
    
    Returns:
        A list of segment tuples: [(start_sec, end_sec, color_rgb_tuple, pixels_int), ...]
        Each segment represents a pulse aligned with a beat.
        
        Returns an empty list if no valid beats are found or if audio_analysis_data is missing.
    """
    # Initialize empty segments list
    segments = []
    
    # Check if audio analysis data is available
    if audio_analysis_data is None or not audio_analysis_data:
        print("Cannot apply pulse_on_beat: Audio analysis data is missing.")
        return segments
    
    # Parse the pulse color
    if 'color' not in params:
        print("Cannot apply pulse_on_beat: Missing required 'color' parameter.")
        return segments
    
    try:
        pulse_color_input = params.get('color')
        pulse_rgb = parse_color(pulse_color_input)
    except ValueError as e:
        print(f"Cannot apply pulse_on_beat: Invalid color - {e}")
        return segments
    
    # Get pulse duration
    pulse_duration_seconds = params.get('pulse_duration_seconds')
    if pulse_duration_seconds is None or not isinstance(pulse_duration_seconds, (int, float)) or pulse_duration_seconds <= 0:
        print("Cannot apply pulse_on_beat: Missing or invalid 'pulse_duration_seconds' parameter.")
        return segments
    
    # Get beat source
    beat_source = params.get('beat_source', 'all_beats')
    
    # Retrieve beat times based on the specified source
    beat_times = []
    
    if beat_source == 'all_beats':
        beat_times = audio_analysis_data.get('beat_times', [])
    elif beat_source == 'downbeats':
        beat_times = audio_analysis_data.get('downbeat_times', [])
    elif beat_source.startswith('custom_times:'):
        # Extract the custom times from the string
        try:
            # Extract the list part from the string
            times_str = beat_source.replace('custom_times:', '').strip()
            
            # Handle different list formats
            if re.match(r'^\[.*\]$', times_str):
                # If it's a proper list format, use ast.literal_eval
                beat_times = ast.literal_eval(times_str)
            else:
                # If it's a comma-separated list without brackets
                beat_times = [float(t.strip()) for t in times_str.split(',') if t.strip()]
                
            # Ensure all times are numeric
            beat_times = [float(t) for t in beat_times]
        except (ValueError, SyntaxError) as e:
            print(f"Cannot parse custom beat times: {e}")
            beat_times = []
    else:
        print(f"Unknown beat_source '{beat_source}'. Using empty beat times.")
    
    # Check if we have any beat times
    if not beat_times:
        print(f"No beats found for source '{beat_source}'.")
        return segments
    
    # Get the default pixels from metadata
    if 'default_pixels' not in metadata:
        print("Missing required 'default_pixels' in metadata")
        return segments
    
    pixels = metadata['default_pixels']
    
    # Create segments for each beat
    for beat_t in beat_times:
        pulse_s = beat_t
        pulse_e = beat_t + pulse_duration_seconds
        
        # Only consider pulses that are at least partially within the effect's time window
        if pulse_e > effect_start_sec and pulse_s < effect_end_sec:
            # Clamp the pulse segment to the effect's boundaries
            actual_pulse_s = max(pulse_s, effect_start_sec)
            actual_pulse_e = min(pulse_e, effect_end_sec)
            
            # Only add the segment if it has a positive duration after clamping
            if actual_pulse_e > actual_pulse_s:
                segments.append((actual_pulse_s, actual_pulse_e, pulse_rgb, pixels))
    
    # Sort segments by start time
    segments.sort(key=lambda x: x[0])
    
    return segments


def apply_section_theme_from_audio_effect(
    effect_start_sec: float,
    effect_end_sec: float,
    params: Dict[str, Any],
    metadata: Dict[str, Any],
    audio_analysis_data: Optional[Dict] = None
) -> List[Tuple[float, float, Tuple[int, int, int], int]]:
    """
    Apply a section-theme effect that assigns different color themes based on audio sections.
    
    Args:
        effect_start_sec: Start time of the effect in seconds
        effect_end_sec: End time of the effect in seconds
        params: Dictionary of parameters for this effect instance
                Expected to contain:
                - 'section_themes': List of theme definitions like
                  {"section_label": "Intro", "base_color": {...}, "energy_mapping": "brightness/saturation/none"}
                - 'default_color_theme': Default color theme to use for sections without a specific theme
        metadata: The metadata section from the .seqdesign.json file
                 Expected to contain 'default_pixels' key
        audio_analysis_data: Audio analysis data containing section information
    
    Returns:
        A list of segment tuples: [(start_sec, end_sec, color_rgb_tuple, pixels_int), ...]
        Each segment represents a section with its assigned color theme.
        
        Returns an empty list if no valid sections are found or if audio_analysis_data is missing.
    """
    # Initialize empty segments list
    segments = []
    
    # Calculate effect duration
    effect_duration = effect_end_sec - effect_start_sec
    if effect_duration <= 0:
        return segments
    
    # Check if audio analysis data is available and contains sections
    if audio_analysis_data is None or 'sections' not in audio_analysis_data or not audio_analysis_data['sections']:
        print("Cannot apply section_theme: Audio section data is missing.")
        return segments
    
    # Get audio sections
    audio_sections = audio_analysis_data['sections']
    
    # Parse section themes parameter
    section_themes_param = params.get('section_themes', [])
    
    # Parse default color theme
    default_color_theme_input = params.get('default_color_theme', {'name': 'grey'})
    try:
        default_theme_rgb = parse_color(default_color_theme_input)
    except ValueError as e:
        print(f"Warning: Could not parse default color theme: {e}. Using grey.")
        default_theme_rgb = (128, 128, 128)  # Grey as fallback
    
    # Create a mapping from section_label to its parsed theme
    parsed_themes = {}
    for theme_def in section_themes_param:
        label = theme_def.get('section_label')
        base_color_input = theme_def.get('base_color')
        if not label or not base_color_input:
            print(f"Warning: Malformed theme definition: {theme_def}. Missing label or base_color.")
            continue
        
        try:
            base_color_rgb = parse_color(base_color_input)
            parsed_themes[label] = {
                'base_color_rgb': base_color_rgb,
                'energy_mapping': theme_def.get('energy_mapping', 'none').lower()
            }
        except ValueError as e:
            print(f"Warning: Could not parse color for section theme '{label}': {e}")
    
    # Get the default pixels from metadata
    if 'default_pixels' not in metadata:
        print("Missing required 'default_pixels' in metadata")
        return segments
    
    pixels = metadata['default_pixels']
    
    # Create segments for each audio section
    for audio_section in audio_sections:
        section_label = audio_section.get('label')
        section_start_time = audio_section.get('start')
        section_end_time = audio_section.get('end')
        
        # Skip sections with missing data
        if section_label is None or section_start_time is None or section_end_time is None:
            continue
        
        # Determine the actual start and end for this segment within the effect's time window
        seg_start_sec = max(effect_start_sec, section_start_time)
        seg_end_sec = min(effect_end_sec, section_end_time)
        
        # Skip if no overlap or zero duration
        if seg_end_sec <= seg_start_sec:
            continue
        
        # Retrieve the theme for this section_label
        current_theme = parsed_themes.get(section_label, {
            'base_color_rgb': default_theme_rgb,
            'energy_mapping': 'none'
        })
        
        base_rgb = current_theme['base_color_rgb']
        energy_map_type = current_theme['energy_mapping']
        
        # For now, we'll implement a simplified version without complex energy mapping
        if energy_map_type != 'none':
            print(f"Warning: Energy mapping type '{energy_map_type}' for section '{section_label}' is not fully implemented yet. Using base color.")
        
        # Add segment with the base color for this section
        segments.append((seg_start_sec, seg_end_sec, base_rgb, pixels))
    
    # Sort segments by start time
    segments.sort(key=lambda x: x[0])
    
    return segments


if __name__ == "__main__":
    # Example usage
    print("Pulse on Beat Effect Example:")
    
    # Example metadata
    example_metadata = {"default_pixels": 10}
    
    # Example audio analysis data
    example_audio_data = {
        "beat_times": [1.0, 2.0, 3.0, 4.0, 5.0],
        "downbeat_times": [1.0, 3.0, 5.0],
        "sections": [
            {"label": "Intro", "start": 0.0, "end": 2.5},
            {"label": "Verse", "start": 2.5, "end": 5.0}
        ]
    }
    
    # Example pulse on beat effect
    pulse_params = {
        "color": {"name": "red"},
        "pulse_duration_seconds": 0.2,
        "beat_source": "all_beats"
    }
    
    pulse_segments = apply_pulse_on_beat_effect(
        1.5, 4.5, pulse_params, example_metadata, example_audio_data
    )
    
    print(f"Pulse on beat segments: {len(pulse_segments)} segments generated")
    for i, segment in enumerate(pulse_segments):
        print(f"  Segment {i}: {segment}")
    
    # Example section theme effect
    print("\nSection Theme Effect Example:")
    
    section_theme_params = {
        "section_themes": [
            {"section_label": "Intro", "base_color": {"name": "blue"}, "energy_mapping": "none"},
            {"section_label": "Verse", "base_color": {"name": "green"}, "energy_mapping": "brightness"}
        ],
        "default_color_theme": {"name": "grey"}
    }
    
    section_segments = apply_section_theme_from_audio_effect(
        0.0, 5.0, section_theme_params, example_metadata, example_audio_data
    )
    
    print(f"Section theme segments: {len(section_segments)} segments generated")
    for i, segment in enumerate(section_segments):
        print(f"  Segment {i}: {segment}")