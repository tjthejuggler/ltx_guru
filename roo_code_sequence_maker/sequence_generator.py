#!/usr/bin/env python3
"""
Sequence Generator for LTX Sequence Maker

This module provides tools for creating color sequences for LTX juggling balls
based on audio analysis data. It can create beat-synchronized patterns,
section-based themes, and more.
"""

import os
import json
import logging
import colorsys
from typing import Dict, List, Tuple, Union, Optional, Any

class SequenceGenerator:
    """
    Generator for color sequences synchronized with music.
    
    This class provides methods to create various types of color sequences:
    - Beat-synchronized patterns (pulse, toggle, fade in, fade out)
    - Section-based themes with energy mapping
    - Simple alternating color sequences
    - Word-synchronized color changes
    """
    
    def __init__(self):
        """Initialize the sequence generator."""
        self.logger = logging.getLogger("SequenceGenerator")
        
        # Define named colors
        self.named_colors = {
            "red": [255, 0, 0],
            "green": [0, 255, 0],
            "blue": [0, 0, 255],
            "yellow": [255, 255, 0],
            "cyan": [0, 255, 255],
            "magenta": [255, 0, 255],
            "white": [255, 255, 255],
            "black": [0, 0, 0],
            "orange": [255, 165, 0],
            "purple": [128, 0, 128],
            "pink": [255, 192, 203],
            "brown": [165, 42, 42],
            "gray": [128, 128, 128]
        }
    
    def _resolve_color(self, color: Union[str, List[int]]) -> List[int]:
        """
        Resolve a color name or RGB array to RGB values.
        
        Args:
            color: Color name or RGB array
            
        Returns:
            list: RGB values [r, g, b]
        """
        if isinstance(color, str):
            # Convert named color to RGB
            if color.lower() in self.named_colors:
                return self.named_colors[color.lower()]
            else:
                self.logger.warning(f"Unknown color name: {color}, using red instead")
                return self.named_colors["red"]
        else:
            # Ensure RGB values are in range 0-255
            return [max(0, min(255, int(c))) for c in color]
    
    def apply_beat_pattern(self, beats: List[float], pattern_type: str, colors: List[Union[str, List[int]]], duration: float = 0.25) -> List[Dict[str, Any]]:
        """
        Apply a color pattern synchronized to beats.
        
        Args:
            beats: List of beat timestamps in seconds
            pattern_type: Type of pattern to apply ("pulse", "toggle", "fade_in", "fade_out")
            colors: List of colors to use in the pattern (RGB arrays or color names)
            duration: Duration of each color segment in seconds (default: 0.25)
            
        Returns:
            list: List of segments with start_time, end_time, and color
        """
        # Resolve colors
        resolved_colors = [self._resolve_color(color) for color in colors]
        
        # Create segments based on pattern type
        if pattern_type == "pulse":
            return self._create_pulse_pattern(beats, resolved_colors, duration)
        elif pattern_type == "toggle":
            return self._create_toggle_pattern(beats, resolved_colors)
        elif pattern_type == "fade_in":
            return self._create_fade_in_pattern(beats, resolved_colors, duration)
        elif pattern_type == "fade_out":
            return self._create_fade_out_pattern(beats, resolved_colors, duration)
        else:
            self.logger.warning(f"Unknown pattern type: {pattern_type}, using pulse instead")
            return self._create_pulse_pattern(beats, resolved_colors, duration)
    
    def _create_pulse_pattern(self, beats: List[float], colors: List[List[int]], duration: float) -> List[Dict[str, Any]]:
        """
        Create a pulse pattern with short color segments at each beat.
        
        Args:
            beats: List of beat timestamps in seconds
            colors: List of RGB colors
            duration: Duration of each color segment in seconds
            
        Returns:
            list: List of segments with start_time, end_time, and color
        """
        segments = []
        
        for i, beat in enumerate(beats):
            # Get color for this beat (cycle through colors)
            color = colors[i % len(colors)]
            
            # Create segment
            segments.append({
                "start_time": beat,
                "end_time": beat + duration,
                "color": color
            })
        
        return segments
    
    def _create_toggle_pattern(self, beats: List[float], colors: List[List[int]]) -> List[Dict[str, Any]]:
        """
        Create a toggle pattern that alternates colors between beats.
        
        Args:
            beats: List of beat timestamps in seconds
            colors: List of RGB colors
            
        Returns:
            list: List of segments with start_time, end_time, and color
        """
        segments = []
        
        for i in range(len(beats)):
            # Get color for this beat (cycle through colors)
            color = colors[i % len(colors)]
            
            # Calculate start and end times
            start_time = beats[i]
            end_time = beats[i + 1] if i < len(beats) - 1 else start_time + 1.0
            
            # Create segment
            segments.append({
                "start_time": start_time,
                "end_time": end_time,
                "color": color
            })
        
        return segments
    
    def _create_fade_in_pattern(self, beats: List[float], colors: List[List[int]], duration: float) -> List[Dict[str, Any]]:
        """
        Create a fade-in pattern that fades from black to the target color at each beat.
        
        Args:
            beats: List of beat timestamps in seconds
            colors: List of RGB colors
            duration: Duration of each fade in seconds
            
        Returns:
            list: List of segments with start_time, end_time, and color
        """
        segments = []
        
        for i, beat in enumerate(beats):
            # Get color for this beat (cycle through colors)
            color = colors[i % len(colors)]
            
            # Create fade-in effect with multiple segments
            num_steps = 10
            step_duration = duration / num_steps
            
            for j in range(num_steps):
                # Calculate segment times
                start_time = beat + (j * step_duration)
                end_time = start_time + step_duration
                
                # Calculate color intensity for this step
                intensity = (j + 1) / num_steps
                segment_color = [int(c * intensity) for c in color]
                
                # Add segment
                segments.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "color": segment_color
                })
        
        return segments
    
    def _create_fade_out_pattern(self, beats: List[float], colors: List[List[int]], duration: float) -> List[Dict[str, Any]]:
        """
        Create a fade-out pattern that fades from the target color to black at each beat.
        
        Args:
            beats: List of beat timestamps in seconds
            colors: List of RGB colors
            duration: Duration of each fade in seconds
            
        Returns:
            list: List of segments with start_time, end_time, and color
        """
        segments = []
        
        for i, beat in enumerate(beats):
            # Get color for this beat (cycle through colors)
            color = colors[i % len(colors)]
            
            # Create fade-out effect with multiple segments
            num_steps = 10
            step_duration = duration / num_steps
            
            for j in range(num_steps):
                # Calculate segment times
                start_time = beat + (j * step_duration)
                end_time = start_time + step_duration
                
                # Calculate color intensity for this step
                intensity = 1.0 - (j / num_steps)
                segment_color = [int(c * intensity) for c in color]
                
                # Add segment
                segments.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "color": segment_color
                })
        
        return segments
    
    def apply_section_theme(self, sections: List[Dict[str, Any]], section_themes: List[Dict[str, Any]], 
                           default_color: Union[str, List[int]] = "white", 
                           energy_data: Optional[Dict[str, List[float]]] = None) -> List[Dict[str, Any]]:
        """
        Apply color themes to different sections of the song.
        
        Args:
            sections: List of sections with start and end times
            section_themes: List of section themes
            default_color: Default color for sections without a theme
            energy_data: Energy timeseries data for energy mapping
            
        Returns:
            list: List of segments with start_time, end_time, and color
        """
        segments = []
        
        # Resolve default color
        default_color_rgb = self._resolve_color(default_color)
        
        # Create a map of section labels to themes
        theme_map = {}
        for theme in section_themes:
            theme_map[theme["section_label"]] = theme
        
        # Process each section
        for section in sections:
            label = section["label"]
            start_time = section["start"]
            end_time = section["end"]
            
            # Check if we have a theme for this section
            if label in theme_map:
                theme = theme_map[label]
                base_color = self._resolve_color(theme["base_color"])
                energy_mapping = theme.get("energy_mapping", "none")
                
                # If we have energy data and energy mapping is not "none", create energy-mapped segments
                if energy_data and energy_mapping != "none":
                    # Get energy values within this section
                    times = energy_data["times"]
                    values = energy_data["values"]
                    
                    # Find indices of times within the section
                    section_indices = [i for i, t in enumerate(times) if start_time <= t < end_time]
                    
                    if section_indices:
                        # Create segments based on energy values
                        for i in range(len(section_indices) - 1):
                            idx = section_indices[i]
                            next_idx = section_indices[i + 1]
                            
                            segment_start = times[idx]
                            segment_end = times[next_idx]
                            energy_value = values[idx]
                            
                            # Map energy to color property
                            segment_color = self._apply_energy_mapping(base_color, energy_value, energy_mapping)
                            
                            # Add segment
                            segments.append({
                                "start_time": segment_start,
                                "end_time": segment_end,
                                "color": segment_color
                            })
                        
                        # Add final segment if needed
                        if section_indices:
                            last_idx = section_indices[-1]
                            segment_start = times[last_idx]
                            segment_end = end_time
                            energy_value = values[last_idx]
                            
                            # Map energy to color property
                            segment_color = self._apply_energy_mapping(base_color, energy_value, energy_mapping)
                            
                            # Add segment
                            segments.append({
                                "start_time": segment_start,
                                "end_time": segment_end,
                                "color": segment_color
                            })
                    else:
                        # No energy data points in this section, use base color
                        segments.append({
                            "start_time": start_time,
                            "end_time": end_time,
                            "color": base_color
                        })
                else:
                    # No energy mapping, use base color for the entire section
                    segments.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "color": base_color
                    })
            else:
                # No theme for this section, use default color
                segments.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "color": default_color_rgb
                })
        
        return segments
    
    def _apply_energy_mapping(self, base_color: List[int], energy_value: float, mapping_type: str) -> List[int]:
        """
        Apply energy mapping to a color.
        
        Args:
            base_color: Base RGB color
            energy_value: Energy value (0.0 to 1.0)
            mapping_type: Type of mapping ("brightness" or "saturation")
            
        Returns:
            list: Mapped RGB color
        """
        # Normalize energy value to 0.0-1.0 range
        # Assuming energy values are typically in 0.0-0.5 range
        normalized_energy = min(1.0, energy_value * 2.0)
        
        if mapping_type == "brightness":
            # Map energy to brightness
            # Convert RGB to HSV
            r, g, b = base_color
            h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            
            # Apply energy to value (brightness)
            v = 0.3 + (normalized_energy * 0.7)  # Minimum brightness of 0.3
            
            # Convert back to RGB
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            return [int(r * 255), int(g * 255), int(b * 255)]
            
        elif mapping_type == "saturation":
            # Map energy to saturation
            # Convert RGB to HSV
            r, g, b = base_color
            h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            
            # Apply energy to saturation
            s = 0.3 + (normalized_energy * 0.7)  # Minimum saturation of 0.3
            
            # Convert back to RGB
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            return [int(r * 255), int(g * 255), int(b * 255)]
        
        else:
            # No mapping, return base color
            return base_color
    
    def create_color_sequence(self, duration: float, colors: List[Union[str, List[int]]], segment_duration: float = 1.0) -> List[Dict[str, Any]]:
        """
        Create a simple color sequence with alternating colors.
        
        Args:
            duration: Total duration of the sequence in seconds
            colors: List of colors to use in the sequence (RGB arrays or color names)
            segment_duration: Duration of each color segment in seconds (default: 1.0)
            
        Returns:
            list: List of segments with start_time, end_time, and color
        """
        segments = []
        
        # Resolve colors
        resolved_colors = [self._resolve_color(color) for color in colors]
        
        # Create segments
        current_time = 0.0
        color_index = 0
        
        while current_time < duration:
            # Get color for this segment (cycle through colors)
            color = resolved_colors[color_index % len(resolved_colors)]
            
            # Calculate end time
            end_time = min(current_time + segment_duration, duration)
            
            # Create segment
            segments.append({
                "start_time": current_time,
                "end_time": end_time,
                "color": color
            })
            
            # Update time and color index
            current_time = end_time
            color_index += 1
        
        return segments
    
    def create_word_synchronized_sequence(self, word_timestamps: List[Dict[str, Any]], target_words: List[str], 
                                         target_color: Union[str, List[int]], default_color: Union[str, List[int]], 
                                         duration: float = 0.5) -> List[Dict[str, Any]]:
        """
        Create a sequence that changes color on specific words.
        
        Args:
            word_timestamps: List of word timestamps
            target_words: List of words to trigger color changes
            target_color: Color to use for target words
            default_color: Default color for other words
            duration: Duration of color change in seconds (default: 0.5)
            
        Returns:
            list: List of segments with start_time, end_time, and color
        """
        segments = []
        
        # Resolve colors
        target_color_rgb = self._resolve_color(target_color)
        default_color_rgb = self._resolve_color(default_color)
        
        # Convert target words to lowercase for case-insensitive matching
        target_words_lower = [word.lower() for word in target_words]
        
        # Start with default color
        if word_timestamps:
            first_word = word_timestamps[0]
            if first_word["start"] > 0:
                segments.append({
                    "start_time": 0,
                    "end_time": first_word["start"],
                    "color": default_color_rgb
                })
        
        # Process each word
        for i, word_data in enumerate(word_timestamps):
            word = word_data["word"].lower()
            start_time = word_data["start"]
            
            # Determine if this is a target word
            is_target = word in target_words_lower
            
            # Determine color and duration
            if is_target:
                color = target_color_rgb
                end_time = start_time + duration
            else:
                color = default_color_rgb
                # End time is the start of the next word, or start_time + duration if this is the last word
                end_time = word_timestamps[i + 1]["start"] if i < len(word_timestamps) - 1 else start_time + duration
            
            # Create segment
            segments.append({
                "start_time": start_time,
                "end_time": end_time,
                "color": color
            })
            
            # If this is a target word and not the last word, add a segment with default color until the next word
            if is_target and i < len(word_timestamps) - 1:
                next_start = word_timestamps[i + 1]["start"]
                if end_time < next_start:
                    segments.append({
                        "start_time": end_time,
                        "end_time": next_start,
                        "color": default_color_rgb
                    })
        
        return segments
    
    def save_sequence_to_json(self, segments: List[Dict[str, Any]], output_path: str, pixels: int = 4, refresh_rate: int = 50) -> None:
        """
        Save a sequence to a JSON file.
        
        Args:
            segments: List of segments with start_time, end_time, and color
            output_path: Path to save the JSON file
            pixels: Number of pixels (default: 4)
            refresh_rate: Refresh rate in Hz (default: 50)
        """
        # Create the output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Convert segments to the LTX JSON format
        sequence = {}
        
        for segment in segments:
            start_time = segment["start_time"]
            color = segment["color"]
            
            # Add the color change at the start time
            sequence[str(start_time)] = {"color": color}
        
        # Create the final JSON structure
        data = {
            "pixels": pixels,
            "refresh_rate": refresh_rate,
            "sequence": sequence
        }
        
        # Save to file
        try:
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"Sequence saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Error saving sequence to {output_path}: {e}")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    generator = SequenceGenerator()
    
    # Create a simple color sequence
    sequence = generator.create_color_sequence(
        duration=10.0,
        colors=["red", "green", "blue"],
        segment_duration=1.0
    )
    
    # Save to JSON
    generator.save_sequence_to_json(sequence, "example_sequence.json")