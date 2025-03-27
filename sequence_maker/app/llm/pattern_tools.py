"""
Sequence Maker - Pattern Tools for LLM

This module defines pattern tools for the LLM integration, allowing the LLM
to create music-synchronized color patterns based on audio analysis.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
from utils.color_utils import resolve_color_name


class PatternTools:
    """
    Provides pattern tools for LLM integration.
    
    This class extends the LLMToolManager with tools for creating music-synchronized
    color patterns, including beat patterns and section themes.
    """
    
    def __init__(self, app):
        """
        Initialize the pattern tools.
        
        Args:
            app: The main application instance.
        """
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.PatternTools")
    
    @property
    def pattern_functions(self) -> List[Dict[str, Any]]:
        """
        Get the pattern function definitions.
        
        Returns:
            list: List of pattern function definitions.
        """
        return [
            {
                "name": "apply_beat_pattern",
                "description": "Apply a color pattern synchronized to beats in a specified time range",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timeline_index": {
                            "type": "integer",
                            "description": "Index of the timeline to add segments to"
                        },
                        "start_time": {
                            "type": "number",
                            "description": "Start time in seconds"
                        },
                        "end_time": {
                            "type": "number",
                            "description": "End time in seconds"
                        },
                        "pattern_type": {
                            "type": "string",
                            "enum": ["pulse", "toggle", "fade_in", "fade_out"],
                            "description": "Type of pattern to apply"
                        },
                        "colors": {
                            "type": "array",
                            "description": "List of colors to use in the pattern (RGB arrays or color names)",
                            "items": {
                                "oneOf": [
                                    {
                                        "type": "array",
                                        "description": "RGB color values (0-255)",
                                        "items": {
                                            "type": "integer",
                                            "minimum": 0,
                                            "maximum": 255
                                        },
                                        "minItems": 3,
                                        "maxItems": 3
                                    },
                                    {
                                        "type": "string",
                                        "description": "Color name (e.g., 'red', 'green', 'blue', etc.)"
                                    }
                                ]
                            },
                            "minItems": 1
                        },
                        "section_label": {
                            "type": "string",
                            "description": "Optional section label to limit pattern to a specific section"
                        },
                        "beat_type": {
                            "type": "string",
                            "enum": ["all", "downbeat"],
                            "description": "Type of beats to use (all beats or only downbeats)"
                        },
                        "duration": {
                            "type": "number",
                            "description": "Duration of each color segment in seconds"
                        }
                    },
                    "required": ["timeline_index", "pattern_type", "colors"],
                    "additionalProperties": False
                }
            },
            {
                "name": "apply_section_theme",
                "description": "Apply color themes to different sections of the song",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timeline_index": {
                            "type": "integer",
                            "description": "Index of the timeline to add segments to"
                        },
                        "section_themes": {
                            "type": "array",
                            "description": "List of section themes",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "section_label": {
                                        "type": "string",
                                        "description": "Label of the section (e.g., 'Intro', 'Verse 1', 'Chorus 1')"
                                    },
                                    "base_color": {
                                        "oneOf": [
                                            {
                                                "type": "array",
                                                "description": "RGB color values (0-255)",
                                                "items": {
                                                    "type": "integer",
                                                    "minimum": 0,
                                                    "maximum": 255
                                                },
                                                "minItems": 3,
                                                "maxItems": 3
                                            },
                                            {
                                                "type": "string",
                                                "description": "Color name (e.g., 'red', 'green', 'blue', etc.)"
                                            }
                                        ],
                                        "description": "Base color for the section"
                                    },
                                    "energy_mapping": {
                                        "type": "string",
                                        "enum": ["brightness", "saturation", "none"],
                                        "description": "How to map energy to color properties"
                                    }
                                },
                                "required": ["section_label", "base_color"],
                                "additionalProperties": False
                            }
                        },
                        "default_color": {
                            "oneOf": [
                                {
                                    "type": "array",
                                    "description": "RGB color values (0-255)",
                                    "items": {
                                        "type": "integer",
                                        "minimum": 0,
                                        "maximum": 255
                                    },
                                    "minItems": 3,
                                    "maxItems": 3
                                },
                                {
                                    "type": "string",
                                    "description": "Color name (e.g., 'red', 'green', 'blue', etc.)"
                                }
                            ],
                            "description": "Default color for sections without a theme"
                        }
                    },
                    "required": ["timeline_index", "section_themes"],
                    "additionalProperties": False
                }
            }
        ]
    
    def register_handlers(self, tool_manager):
        """
        Register handlers for pattern tools with the tool manager.
        
        Args:
            tool_manager: The LLMToolManager instance.
        """
        tool_manager.register_action_handler("apply_beat_pattern", self._handle_apply_beat_pattern)
        tool_manager.register_action_handler("apply_section_theme", self._handle_apply_section_theme)
    
    def _resolve_color_name(self, color_input) -> List[int]:
        """
        Resolve a color name to RGB values.
        
        Args:
            color_input: Color name or RGB values.
            
        Returns:
            list: RGB values.
        """
        # If already RGB values, return as is
        if isinstance(color_input, list) and len(color_input) == 3:
            return color_input
        
        # If string, try to resolve as color name
        if isinstance(color_input, str):
            return resolve_color_name(color_input)
        
        # Default to white if invalid
        return [255, 255, 255]
    
    def _handle_apply_beat_pattern(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the apply_beat_pattern action.
        
        Args:
            parameters: Action parameters.
            
        Returns:
            dict: Result of the action.
        """
        if not hasattr(self.app, 'audio_analysis_manager') or not hasattr(self.app, 'timeline_manager'):
            return {"error": "Required managers not available"}
        
        # Extract parameters
        timeline_index = parameters.get("timeline_index")
        start_time = parameters.get("start_time")
        end_time = parameters.get("end_time")
        pattern_type = parameters.get("pattern_type")
        colors_input = parameters.get("colors", [])
        section_label = parameters.get("section_label")
        beat_type = parameters.get("beat_type", "all")
        duration = parameters.get("duration", 0.25)  # Default to 0.25 seconds
        
        # Validate parameters
        if timeline_index is None:
            return {"error": "timeline_index is required"}
        
        if not pattern_type:
            return {"error": "pattern_type is required"}
        
        if not colors_input:
            return {"error": "colors is required"}
        
        # Resolve colors
        colors = [self._resolve_color_name(color) for color in colors_input]
        
        # Determine time range
        if section_label:
            # Get section details
            section = self.app.audio_analysis_manager.get_section_by_label(section_label)
            if not section:
                # Get analysis data to list available sections
                analysis_data = self.app.audio_analysis_manager.load_analysis()
                if analysis_data and "sections" in analysis_data:
                    available_sections = [s["label"] for s in analysis_data["sections"]]
                    return {
                        "error": f"Section '{section_label}' not found",
                        "available_sections": available_sections
                    }
                return {"error": f"Section '{section_label}' not found"}
            
            # Use section time range
            start_time = section["start"] if start_time is None else max(start_time, section["start"])
            end_time = section["end"] if end_time is None else min(end_time, section["end"])
        else:
            # Use provided time range or full song
            if start_time is None or end_time is None:
                analysis_data = self.app.audio_analysis_manager.load_analysis()
                if not analysis_data:
                    return {"error": "No audio analysis available"}
                
                start_time = 0 if start_time is None else start_time
                end_time = analysis_data.get("duration_seconds", 0) if end_time is None else end_time
        
        # Get beats in range
        beats = self.app.audio_analysis_manager.get_beats_in_range(start_time, end_time, beat_type)
        if not beats:
            return {
                "error": f"No {beat_type} beats found in the specified time range",
                "start_time": start_time,
                "end_time": end_time
            }
        
        # Apply pattern based on type
        segments_created = []
        
        if pattern_type == "pulse":
            segments_created = self._apply_pulse_pattern(timeline_index, beats, colors, duration)
        elif pattern_type == "toggle":
            segments_created = self._apply_toggle_pattern(timeline_index, beats, colors, duration)
        elif pattern_type == "fade_in":
            segments_created = self._apply_fade_in_pattern(timeline_index, beats, colors, duration)
        elif pattern_type == "fade_out":
            segments_created = self._apply_fade_out_pattern(timeline_index, beats, colors, duration)
        else:
            return {"error": f"Unknown pattern type: {pattern_type}"}
        
        return {
            "pattern_type": pattern_type,
            "timeline_index": timeline_index,
            "start_time": start_time,
            "end_time": end_time,
            "beat_count": len(beats),
            "colors_used": colors,
            "segments_created": len(segments_created),
            "segments": segments_created
        }
    
    def _apply_pulse_pattern(self, timeline_index: int, beats: List[float], colors: List[List[int]], duration: float) -> List[Dict[str, Any]]:
        """
        Apply a pulse pattern to the timeline.
        
        This pattern creates a short color segment at each beat.
        
        Args:
            timeline_index: Index of the timeline.
            beats: List of beat timestamps.
            colors: List of colors to use.
            duration: Duration of each segment.
            
        Returns:
            list: List of created segments.
        """
        segments_created = []
        
        for i, beat in enumerate(beats):
            # Get color (cycle through colors)
            color = colors[i % len(colors)]
            
            # Create segment
            segment = self.app.timeline_manager.create_segment(
                timeline_index,
                beat,
                beat + duration,
                color
            )
            
            if segment:
                segments_created.append({
                    "start_time": beat,
                    "end_time": beat + duration,
                    "color": color
                })
        
        return segments_created
    
    def _apply_toggle_pattern(self, timeline_index: int, beats: List[float], colors: List[List[int]], duration: float) -> List[Dict[str, Any]]:
        """
        Apply a toggle pattern to the timeline.
        
        This pattern alternates between colors, with each color lasting until the next beat.
        
        Args:
            timeline_index: Index of the timeline.
            beats: List of beat timestamps.
            colors: List of colors to use.
            duration: Not used in this pattern.
            
        Returns:
            list: List of created segments.
        """
        segments_created = []
        
        for i in range(len(beats) - 1):
            # Get color (cycle through colors)
            color = colors[i % len(colors)]
            
            # Create segment from this beat to the next
            segment = self.app.timeline_manager.create_segment(
                timeline_index,
                beats[i],
                beats[i + 1],
                color
            )
            
            if segment:
                segments_created.append({
                    "start_time": beats[i],
                    "end_time": beats[i + 1],
                    "color": color
                })
        
        # Add final segment if there are beats
        if beats:
            color = colors[(len(beats) - 1) % len(colors)]
            
            # Use the same duration as the previous segment
            if len(beats) > 1:
                last_duration = beats[-1] - beats[-2]
            else:
                last_duration = duration
            
            segment = self.app.timeline_manager.create_segment(
                timeline_index,
                beats[-1],
                beats[-1] + last_duration,
                color
            )
            
            if segment:
                segments_created.append({
                    "start_time": beats[-1],
                    "end_time": beats[-1] + last_duration,
                    "color": color
                })
        
        return segments_created
    
    def _apply_fade_in_pattern(self, timeline_index: int, beats: List[float], colors: List[List[int]], duration: float) -> List[Dict[str, Any]]:
        """
        Apply a fade-in pattern to the timeline.
        
        This pattern creates segments that fade in from black to the target color.
        
        Args:
            timeline_index: Index of the timeline.
            beats: List of beat timestamps.
            colors: List of colors to use.
            duration: Duration of each segment.
            
        Returns:
            list: List of created segments.
        """
        segments_created = []
        
        for i, beat in enumerate(beats):
            # Get color (cycle through colors)
            color = colors[i % len(colors)]
            
            # Create a series of segments with increasing brightness
            steps = 5  # Number of steps in the fade
            step_duration = duration / steps
            
            for step in range(steps):
                # Calculate brightness factor (0 to 1)
                brightness = (step + 1) / steps
                
                # Apply brightness to color
                faded_color = [int(c * brightness) for c in color]
                
                # Calculate segment times
                start_time = beat + (step * step_duration)
                end_time = beat + ((step + 1) * step_duration)
                
                # Create segment
                segment = self.app.timeline_manager.create_segment(
                    timeline_index,
                    start_time,
                    end_time,
                    faded_color
                )
                
                if segment:
                    segments_created.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "color": faded_color
                    })
        
        return segments_created
    
    def _apply_fade_out_pattern(self, timeline_index: int, beats: List[float], colors: List[List[int]], duration: float) -> List[Dict[str, Any]]:
        """
        Apply a fade-out pattern to the timeline.
        
        This pattern creates segments that fade out from the target color to black.
        
        Args:
            timeline_index: Index of the timeline.
            beats: List of beat timestamps.
            colors: List of colors to use.
            duration: Duration of each segment.
            
        Returns:
            list: List of created segments.
        """
        segments_created = []
        
        for i, beat in enumerate(beats):
            # Get color (cycle through colors)
            color = colors[i % len(colors)]
            
            # Create a series of segments with decreasing brightness
            steps = 5  # Number of steps in the fade
            step_duration = duration / steps
            
            for step in range(steps):
                # Calculate brightness factor (1 to 0)
                brightness = 1 - (step / steps)
                
                # Apply brightness to color
                faded_color = [int(c * brightness) for c in color]
                
                # Calculate segment times
                start_time = beat + (step * step_duration)
                end_time = beat + ((step + 1) * step_duration)
                
                # Create segment
                segment = self.app.timeline_manager.create_segment(
                    timeline_index,
                    start_time,
                    end_time,
                    faded_color
                )
                
                if segment:
                    segments_created.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "color": faded_color
                    })
        
        return segments_created
    
    def _handle_apply_section_theme(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the apply_section_theme action.
        
        Args:
            parameters: Action parameters.
            
        Returns:
            dict: Result of the action.
        """
        if not hasattr(self.app, 'audio_analysis_manager') or not hasattr(self.app, 'timeline_manager'):
            return {"error": "Required managers not available"}
        
        # Extract parameters
        timeline_index = parameters.get("timeline_index")
        section_themes = parameters.get("section_themes", [])
        default_color_input = parameters.get("default_color", [255, 255, 255])  # Default to white
        
        # Validate parameters
        if timeline_index is None:
            return {"error": "timeline_index is required"}
        
        if not section_themes:
            return {"error": "section_themes is required"}
        
        # Resolve default color
        default_color = self._resolve_color_name(default_color_input)
        
        # Get analysis data
        analysis_data = self.app.audio_analysis_manager.load_analysis()
        if not analysis_data:
            return {"error": "No audio analysis available"}
        
        # Get all sections
        all_sections = analysis_data.get("sections", [])
        if not all_sections:
            return {"error": "No sections found in audio analysis"}
        
        # Apply themes to sections
        segments_created = []
        sections_themed = []
        
        for section in all_sections:
            section_label = section["label"]
            start_time = section["start"]
            end_time = section["end"]
            
            # Find theme for this section
            theme = next((t for t in section_themes if t.get("section_label") == section_label), None)
            
            if theme:
                # Get base color
                base_color = self._resolve_color_name(theme.get("base_color"))
                
                # Get energy mapping
                energy_mapping = theme.get("energy_mapping", "none")
                
                # Apply theme based on energy mapping
                if energy_mapping != "none":
                    segments = self._apply_energy_mapped_theme(
                        timeline_index, section, base_color, energy_mapping
                    )
                    segments_created.extend(segments)
                else:
                    # Just use base color for the whole section
                    segment = self.app.timeline_manager.create_segment(
                        timeline_index,
                        start_time,
                        end_time,
                        base_color
                    )
                    
                    if segment:
                        segments_created.append({
                            "start_time": start_time,
                            "end_time": end_time,
                            "color": base_color
                        })
                
                sections_themed.append({
                    "section_label": section_label,
                    "base_color": base_color,
                    "energy_mapping": energy_mapping
                })
            else:
                # Use default color
                segment = self.app.timeline_manager.create_segment(
                    timeline_index,
                    start_time,
                    end_time,
                    default_color
                )
                
                if segment:
                    segments_created.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "color": default_color
                    })
        
        return {
            "timeline_index": timeline_index,
            "sections_themed": sections_themed,
            "default_color": default_color,
            "segments_created": len(segments_created),
            "segments": segments_created
        }
    
    def _apply_energy_mapped_theme(self, timeline_index: int, section: Dict[str, Any], base_color: List[int], energy_mapping: str) -> List[Dict[str, Any]]:
        """
        Apply an energy-mapped theme to a section.
        
        Args:
            timeline_index: Index of the timeline.
            section: Section data.
            base_color: Base color for the section.
            energy_mapping: How to map energy to color properties.
            
        Returns:
            list: List of created segments.
        """
        segments_created = []
        
        # Get energy data
        analysis_data = self.app.audio_analysis_manager.load_analysis()
        if not analysis_data or "energy_timeseries" not in analysis_data:
            # Fallback to base color if energy data not available
            segment = self.app.timeline_manager.create_segment(
                timeline_index,
                section["start"],
                section["end"],
                base_color
            )
            
            if segment:
                segments_created.append({
                    "start_time": section["start"],
                    "end_time": section["end"],
                    "color": base_color
                })
            
            return segments_created
        
        # Get energy data within section
        energy_data = analysis_data["energy_timeseries"]
        energy_times = energy_data["times"]
        energy_values = energy_data["values"]
        
        # Find energy values within section
        section_energy_times = []
        section_energy_values = []
        
        for i, t in enumerate(energy_times):
            if section["start"] <= t < section["end"]:
                section_energy_times.append(t)
                section_energy_values.append(energy_values[i])
        
        if not section_energy_times:
            # Fallback to base color if no energy data in section
            segment = self.app.timeline_manager.create_segment(
                timeline_index,
                section["start"],
                section["end"],
                base_color
            )
            
            if segment:
                segments_created.append({
                    "start_time": section["start"],
                    "end_time": section["end"],
                    "color": base_color
                })
            
            return segments_created
        
        # Normalize energy values to 0-1 range
        min_energy = min(section_energy_values)
        max_energy = max(section_energy_values)
        
        if max_energy > min_energy:
            normalized_energy = [(e - min_energy) / (max_energy - min_energy) for e in section_energy_values]
        else:
            normalized_energy = [0.5] * len(section_energy_values)
        
        # Create segments based on energy mapping
        for i in range(len(section_energy_times) - 1):
            start_time = section_energy_times[i]
            end_time = section_energy_times[i + 1]
            energy = normalized_energy[i]
            
            # Apply energy mapping
            if energy_mapping == "brightness":
                # Map energy to brightness (0.2-1.0 range to avoid complete darkness)
                brightness = 0.2 + (energy * 0.8)
                color = [int(c * brightness) for c in base_color]
            elif energy_mapping == "saturation":
                # Map energy to saturation
                # Convert RGB to HSV, modify saturation, convert back to RGB
                color = self._adjust_saturation(base_color, energy)
            else:
                color = base_color
            
            # Create segment
            segment = self.app.timeline_manager.create_segment(
                timeline_index,
                start_time,
                end_time,
                color
            )
            
            if segment:
                segments_created.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "color": color
                })
        
        # Add final segment if needed
        if section_energy_times:
            start_time = section_energy_times[-1]
            end_time = section["end"]
            energy = normalized_energy[-1]
            
            # Apply energy mapping
            if energy_mapping == "brightness":
                brightness = 0.2 + (energy * 0.8)
                color = [int(c * brightness) for c in base_color]
            elif energy_mapping == "saturation":
                color = self._adjust_saturation(base_color, energy)
            else:
                color = base_color
            
            # Create segment
            segment = self.app.timeline_manager.create_segment(
                timeline_index,
                start_time,
                end_time,
                color
            )
            
            if segment:
                segments_created.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "color": color
                })
        
        return segments_created
    
    def _adjust_saturation(self, rgb: List[int], saturation: float) -> List[int]:
        """
        Adjust the saturation of an RGB color.
        
        Args:
            rgb: RGB color values.
            saturation: Saturation value (0-1).
            
        Returns:
            list: Adjusted RGB color values.
        """
        # Simple saturation adjustment (not true HSV conversion)
        # Find the average value
        avg = sum(rgb) / 3
        
        # Adjust each component towards the average based on saturation
        # saturation=1 means no change, saturation=0 means grayscale
        adjusted = [
            int(avg + (saturation * (c - avg)))
            for c in rgb
        ]
        
        # Ensure values are in valid range
        return [max(0, min(255, c)) for c in adjusted]