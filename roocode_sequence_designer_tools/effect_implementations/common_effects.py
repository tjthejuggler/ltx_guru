#!/usr/bin/env python3
"""
Common Effects Module for Roocode Sequence Designer Tools

This module provides implementations for common lighting effects:
- Solid Color: Applies a single color for the entire effect duration
- Fade: Creates a smooth transition between two colors over the effect duration
- Strobe: Creates a flashing effect alternating between two colors at a specified frequency
"""

from typing import Dict, List, Tuple, Optional, Any

# Import color utilities
from roocode_sequence_designer_tools.tool_utils.color_parser import parse_color, interpolate_color


def apply_solid_color_effect(
    effect_start_sec: float,
    effect_end_sec: float,
    params: Dict[str, Any],
    metadata: Dict[str, Any],
    audio_analysis_data=None
) -> List[Tuple[float, float, Tuple[int, int, int], int]]:
    """
    Apply a solid color effect for the specified duration.
    
    Args:
        effect_start_sec: Start time of the effect in seconds
        effect_end_sec: End time of the effect in seconds
        params: Dictionary of parameters for this effect instance
                Expected to contain a 'color' key with a color specification
        metadata: The metadata section from the .seqdesign.json file
                 Expected to contain 'default_pixels' key
        audio_analysis_data: Optional audio analysis data (not used by this effect)
    
    Returns:
        A list containing a single segment tuple: 
        [(start_sec, end_sec, color_rgb_tuple, pixels_int)]
        
        Returns an empty list if effect_end_sec <= effect_start_sec
    """
    # Validate effect duration
    if effect_end_sec <= effect_start_sec:
        return []
    
    # Parse the color from params
    if 'color' not in params:
        raise ValueError("Missing required 'color' parameter for solid_color effect")
    
    color_rgb = parse_color(params['color'])
    
    # Get the default pixels from metadata
    if 'default_pixels' not in metadata:
        raise ValueError("Missing required 'default_pixels' in metadata")
    
    pixels = metadata['default_pixels']
    
    # Create and return a single segment
    return [(effect_start_sec, effect_end_sec, color_rgb, pixels)]


def apply_fade_effect(
    effect_start_sec: float,
    effect_end_sec: float,
    params: Dict[str, Any],
    metadata: Dict[str, Any],
    audio_analysis_data=None
) -> List[Tuple[float, float, Any, int, Optional[str]]]: # Return type changed for fade segment
    """
    Apply a fade effect that transitions between two colors over the specified duration.
    This version prepares a single segment descriptor for native PRG generator fade.
    
    Args:
        effect_start_sec: Start time of the effect in seconds
        effect_end_sec: End time of the effect in seconds
        params: Dictionary of parameters for this effect instance
                Expected to contain:
                - 'color_start': Starting color specification
                - 'color_end': Ending color specification
                - 'steps_per_second': Optional, (Currently NOT USED by this function for PRG generation,
                                      prg_generator.py handles interpolation. Kept for potential
                                      UI/visualizer use or other effect types).
        metadata: The metadata section from the .seqdesign.json file
                 Expected to contain 'default_pixels' key
        audio_analysis_data: Optional audio analysis data (not used by this effect)
    
    Returns:
        A list containing a single segment tuple representing the fade:
        [(start_sec, end_sec, (start_color_rgb, end_color_rgb), pixels_int, "fade")]
        
        Returns an empty list if effect_end_sec <= effect_start_sec
    """
    # Validate effect duration
    effect_duration = effect_end_sec - effect_start_sec
    if effect_duration <= 0:
        return []
    
    # Validate required parameters
    if 'color_start' not in params:
        raise ValueError("Missing required 'color_start' parameter for fade effect")
    if 'color_end' not in params:
        raise ValueError("Missing required 'color_end' parameter for fade effect")
    
    # Parse the start and end colors
    color_start_rgb = parse_color(params['color_start'])
    color_end_rgb = parse_color(params['color_end'])
    
    # Get the default pixels from metadata
    if 'default_pixels' not in metadata:
        raise ValueError("Missing required 'default_pixels' in metadata")
    
    pixels = metadata['default_pixels']
    
    # The 'steps_per_second' parameter is not used here for PRG generation,
    # as prg_generator.py handles the interpolation for native fades.
    # params.get('steps_per_second', 20) # Kept commented for awareness
    
    # Return a single segment representing the entire fade
    # The third element is a tuple of (start_color, end_color)
    # The fifth element is a marker string "fade"
    return [(effect_start_sec, effect_end_sec, (color_start_rgb, color_end_rgb), pixels, "fade")]


def apply_strobe_effect(
    effect_start_sec: float,
    effect_end_sec: float,
    params: Dict[str, Any],
    metadata: Dict[str, Any],
    audio_analysis_data=None
) -> List[Tuple[float, float, Tuple[int, int, int], int]]:
    """
    Apply a strobe effect that alternates between two colors at a specified frequency.
    
    Args:
        effect_start_sec: Start time of the effect in seconds
        effect_end_sec: End time of the effect in seconds
        params: Dictionary of parameters for this effect instance
                Expected to contain:
                - 'color_on': Color specification for the "on" state
                - 'color_off': Color specification for the "off" state
                And either:
                - 'frequency_hz': Frequency of the strobe in Hz (cycles per second)
                Or:
                - 'on_duration_seconds': Duration of the "on" state in seconds
                - 'off_duration_seconds': Duration of the "off" state in seconds
        metadata: The metadata section from the .seqdesign.json file
                 Expected to contain 'default_pixels' key
        audio_analysis_data: Optional audio analysis data (not used by this effect)
    
    Returns:
        A list of segment tuples: [(start_sec, end_sec, color_rgb_tuple, pixels_int), ...]
        Each segment represents either an "on" or "off" state in the strobe sequence.
        
        Returns an empty list if effect_end_sec <= effect_start_sec
    """
    # Initialize segments list
    segments = []
    
    # Validate effect duration
    effect_duration = effect_end_sec - effect_start_sec
    if effect_duration <= 0:
        return segments
    
    # Parse the on and off colors
    color_on_input = params.get('color_on')
    color_off_input = params.get('color_off')
    
    if not color_on_input or not color_off_input:
        print(f"Warning: Missing required 'color_on' or 'color_off' parameter for strobe effect")
        return segments
    
    try:
        color_on_rgb = parse_color(color_on_input)
        color_off_rgb = parse_color(color_off_input)
    except ValueError as e:
        print(f"Warning: {e}")
        return segments
    
    # Determine strobe timing
    cycle_duration_sec = None
    on_duration_seconds = None
    off_duration_seconds = None
    
    # Option 1: Using frequency_hz
    frequency_hz = params.get('frequency_hz')
    if frequency_hz is not None:
        try:
            frequency_hz = float(frequency_hz)
            if frequency_hz > 0:
                cycle_duration_sec = 1.0 / frequency_hz
                on_duration_seconds = cycle_duration_sec / 2.0
                off_duration_seconds = cycle_duration_sec / 2.0
        except (ValueError, TypeError):
            pass
    
    # Option 2: Using explicit on/off durations
    if cycle_duration_sec is None:
        on_duration_seconds = params.get('on_duration_seconds')
        off_duration_seconds = params.get('off_duration_seconds')
        
        try:
            on_duration_seconds = float(on_duration_seconds)
            off_duration_seconds = float(off_duration_seconds)
            if on_duration_seconds > 0 and off_duration_seconds > 0:
                cycle_duration_sec = on_duration_seconds + off_duration_seconds
        except (ValueError, TypeError):
            pass
    
    # Validate timing parameters
    if cycle_duration_sec is None or cycle_duration_sec <= 0:
        print(f"Warning: Invalid timing for strobe effect")
        return segments
    
    # Get the default pixels from metadata
    if 'default_pixels' not in metadata:
        print(f"Warning: Missing required 'default_pixels' in metadata")
        return segments
    
    pixels = metadata['default_pixels']
    
    # Generate the strobe segments
    current_time = effect_start_sec
    
    while current_time < effect_end_sec:
        # On segment
        on_s = current_time
        on_e = min(current_time + on_duration_seconds, effect_end_sec)
        
        if on_e > on_s:
            segments.append((on_s, on_e, color_on_rgb, pixels))
        
        current_time = on_e
        
        if current_time >= effect_end_sec:
            break
        
        # Off segment
        off_s = current_time
        off_e = min(current_time + off_duration_seconds, effect_end_sec)
        
        if off_e > off_s:
            segments.append((off_s, off_e, color_off_rgb, pixels))
        
        current_time = off_e
    
    return segments


if __name__ == "__main__":
    # Example usage
    print("Solid Color Effect Example:")
    
    # Example metadata
    example_metadata = {"default_pixels": 10}
    
    # Example solid color effect
    solid_params = {"color": {"name": "red"}}
    solid_segments = apply_solid_color_effect(0.0, 5.0, solid_params, example_metadata)
    print(f"Solid color segments: {solid_segments}")
    
    print("\nFade Effect Example:")
    
    # Example fade effect
    fade_params = {
        "color_start": {"name": "blue"},
        "color_end": {"name": "green"},
        "steps_per_second": 10
    }
    fade_segments = apply_fade_effect(0.0, 2.0, fade_params, example_metadata)
    print(f"Fade segments: {len(fade_segments)} segments generated")
    for i, segment in enumerate(fade_segments[:3]):
        print(f"  Segment {i}: {segment}")
    if len(fade_segments) > 3:
        print(f"  ... {len(fade_segments) - 3} more segments ...")
    
    print("\nStrobe Effect Example:")
    
    # Example strobe effect
    strobe_params = {
        "color_on": {"name": "white"},
        "color_off": {"name": "black"},
        "frequency_hz": 5  # 5 Hz = 5 cycles per second
    }
    strobe_segments = apply_strobe_effect(0.0, 1.0, strobe_params, example_metadata)
    print(f"Strobe segments: {len(strobe_segments)} segments generated")
    for i, segment in enumerate(strobe_segments):
        print(f"  Segment {i}: {segment}")


def apply_snap_on_flash_off_effect(
    effect_start_sec: float,
    effect_end_sec: float,
    params: Dict[str, Any],
    metadata: Dict[str, Any],
    audio_analysis_data=None
) -> List[Tuple[float, float, Tuple[int, int, int], int]]:
    """
    Apply a snap-on-flash-off effect that quickly changes from a pre-base color to a target color,
    then smoothly fades back to a post-base color.
    
    Args:
        effect_start_sec: Start time of the effect in seconds
        effect_end_sec: End time of the effect in seconds
        params: Dictionary of parameters for this effect instance
                Expected to contain:
                - 'pre_base_color': Starting color specification
                - 'target_color': Flash color specification
                - 'post_base_color': Color to fade back to
                - 'fade_out_duration': Duration of the fade-out in seconds
                - 'steps_per_second': Optional, number of steps per second for fade (default: 20)
        metadata: The metadata section from the .seqdesign.json file
                 Expected to contain 'default_pixels' key
        audio_analysis_data: Optional audio analysis data (not used by this effect)
    
    Returns:
        A list of segment tuples: [(start_sec, end_sec, color_rgb_tuple, pixels_int), ...]
        The first segment is the target color flash, followed by segments for the fade back to post-base color.
        
        Returns an empty list if effect_end_sec <= effect_start_sec
    """
    # Validate effect duration
    effect_duration = effect_end_sec - effect_start_sec
    if effect_duration <= 0:
        return []
    
    # Validate required parameters
    if 'pre_base_color' not in params:
        raise ValueError("Missing required 'pre_base_color' parameter for snap_on_flash_off effect")
    if 'target_color' not in params:
        raise ValueError("Missing required 'target_color' parameter for snap_on_flash_off effect")
    if 'post_base_color' not in params:
        raise ValueError("Missing required 'post_base_color' parameter for snap_on_flash_off effect")
    if 'fade_out_duration' not in params:
        raise ValueError("Missing required 'fade_out_duration' parameter for snap_on_flash_off effect")
    
    # Parse the colors
    pre_base_color_rgb = parse_color(params['pre_base_color'])
    target_color_rgb = parse_color(params['target_color'])
    post_base_color_rgb = parse_color(params['post_base_color'])
    
    # Get the fade out duration
    try:
        fade_out_duration = float(params['fade_out_duration'])
        if fade_out_duration <= 0:
            raise ValueError("fade_out_duration must be positive")
    except (ValueError, TypeError):
        raise ValueError(f"Invalid fade_out_duration: {params['fade_out_duration']}")
    
    # Ensure fade_out_duration doesn't exceed the total effect duration
    fade_out_duration = min(fade_out_duration, effect_duration)
    
    # Calculate the flash duration (instant change to target color)
    flash_duration = effect_duration - fade_out_duration
    
    # Get the default pixels from metadata
    if 'default_pixels' not in metadata:
        raise ValueError("Missing required 'default_pixels' in metadata")
    
    pixels = metadata['default_pixels']
    
    # Initialize segments list
    segments = []
    
    # Add the flash segment (target color)
    if flash_duration > 0:
        segments.append((effect_start_sec, effect_start_sec + flash_duration, target_color_rgb, pixels))
    
    # If there's a fade out duration, add fade segments from target color to post-base color
    if fade_out_duration > 0:
        fade_start_sec = effect_start_sec + flash_duration
        
        # Determine the number of steps based on steps_per_second
        steps_per_second = params.get('steps_per_second', 20)
        num_steps = max(2, round(fade_out_duration * steps_per_second))
        
        # Calculate the duration of each step
        step_duration = fade_out_duration / num_steps
        
        # Generate the segments for the fade
        for i in range(num_steps):
            # Calculate the start and end time for this segment
            segment_start = fade_start_sec + (i * step_duration)
            
            # Ensure the last segment ends exactly at effect_end_sec
            if i == num_steps - 1:
                segment_end = effect_end_sec
            else:
                segment_end = fade_start_sec + ((i + 1) * step_duration)
            
            # Calculate the interpolation factor for this step
            factor = i / (num_steps - 1) if num_steps > 1 else 0
            
            # Interpolate the color for this step
            color_rgb = interpolate_color(target_color_rgb, post_base_color_rgb, factor)
            
            # Add the segment to the list
            segments.append((segment_start, segment_end, color_rgb, pixels))
    
    return segments