"""
Sequence Maker - Music Data Tools for LLM

This module defines music data tools for the LLM integration, allowing the LLM
to access and analyze audio data through function calling.
"""

import logging
from typing import Dict, List, Any, Optional, Union


class MusicDataTools:
    """
    Provides music data tools for LLM integration.
    
    This class extends the LLMToolManager with tools for accessing and analyzing
    audio data, including song metadata, beats, sections, and audio features.
    """
    
    def __init__(self, app):
        """
        Initialize the music data tools.
        
        Args:
            app: The main application instance.
        """
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.MusicDataTools")
    
    @property
    def music_data_functions(self) -> List[Dict[str, Any]]:
        """
        Get the music data function definitions.
        
        Returns:
            list: List of music data function definitions.
        """
        return [
            {
                "name": "get_song_metadata",
                "description": "Get general metadata about the current song",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "get_beats_in_range",
                "description": "Get beat timestamps within a specified time range",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_time": {
                            "type": "number",
                            "description": "Start time in seconds"
                        },
                        "end_time": {
                            "type": "number",
                            "description": "End time in seconds"
                        },
                        "beat_type": {
                            "type": "string",
                            "enum": ["all", "downbeat"],
                            "description": "Type of beats to retrieve (all beats or only downbeats)"
                        }
                    },
                    "required": ["start_time", "end_time"],
                    "additionalProperties": False
                }
            },
            {
                "name": "get_section_details",
                "description": "Get details about a specific section of the song",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "section_label": {
                            "type": "string",
                            "description": "Label of the section (e.g., 'Intro', 'Verse 1', 'Chorus 1')"
                        }
                    },
                    "required": ["section_label"],
                    "additionalProperties": False
                }
            },
            {
                "name": "get_feature_value_at_time",
                "description": "Get the value of a specific audio feature at a given time",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "time": {
                            "type": "number",
                            "description": "Time in seconds"
                        },
                        "feature_name": {
                            "type": "string",
                            "enum": ["energy", "onset_strength", "chroma", "spectral_contrast", 
                                    "spectral_centroid", "spectral_rolloff", "zero_crossing_rate"],
                            "description": "Name of the feature to retrieve"
                        }
                    },
                    "required": ["time", "feature_name"],
                    "additionalProperties": False
                }
            }
        ]
    
    def register_handlers(self, tool_manager):
        """
        Register handlers for music data tools with the tool manager.
        
        Args:
            tool_manager: The LLMToolManager instance.
        """
        tool_manager.register_action_handler("get_song_metadata", self._handle_get_song_metadata)
        tool_manager.register_action_handler("get_beats_in_range", self._handle_get_beats_in_range)
        tool_manager.register_action_handler("get_section_details", self._handle_get_section_details)
        tool_manager.register_action_handler("get_feature_value_at_time", self._handle_get_feature_value_at_time)
    
    def _handle_get_song_metadata(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the get_song_metadata action.
        
        Args:
            parameters: Action parameters (empty for this action).
            
        Returns:
            dict: Song metadata.
        """
        if not hasattr(self.app, 'audio_analysis_manager'):
            return {"error": "Audio analysis manager not available"}
        
        # Get analysis data
        analysis_data = self.app.audio_analysis_manager.load_analysis()
        if not analysis_data:
            return {"error": "No audio analysis available"}
        
        # Extract metadata
        metadata = {
            "song_title": analysis_data.get("song_title", "Unknown"),
            "duration_seconds": analysis_data.get("duration_seconds", 0),
            "estimated_tempo": analysis_data.get("estimated_tempo", 0),
            "time_signature_guess": analysis_data.get("time_signature_guess", "4/4"),
            "total_beats": len(analysis_data.get("beats", [])),
            "total_downbeats": len(analysis_data.get("downbeats", [])),
            "sections": [section["label"] for section in analysis_data.get("sections", [])]
        }
        
        # Add audio file path if available
        if hasattr(self.app, 'audio_manager') and self.app.audio_manager.audio_file:
            metadata["audio_file"] = self.app.audio_manager.audio_file
        
        return metadata
    
    def _handle_get_beats_in_range(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the get_beats_in_range action.
        
        Args:
            parameters: Action parameters.
            
        Returns:
            dict: Beat timestamps within the specified range.
        """
        if not hasattr(self.app, 'audio_analysis_manager'):
            return {"error": "Audio analysis manager not available"}
        
        # Extract parameters
        start_time = parameters.get("start_time")
        end_time = parameters.get("end_time")
        beat_type = parameters.get("beat_type", "all")
        
        # Validate parameters
        if start_time is None or end_time is None:
            return {"error": "start_time and end_time are required"}
        
        if start_time < 0:
            start_time = 0
        
        # Get beats in range
        beats = self.app.audio_analysis_manager.get_beats_in_range(start_time, end_time, beat_type)
        
        return {
            "start_time": start_time,
            "end_time": end_time,
            "beat_type": beat_type,
            "beats": beats,
            "count": len(beats)
        }
    
    def _handle_get_section_details(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the get_section_details action.
        
        Args:
            parameters: Action parameters.
            
        Returns:
            dict: Section details.
        """
        if not hasattr(self.app, 'audio_analysis_manager'):
            return {"error": "Audio analysis manager not available"}
        
        # Extract parameters
        section_label = parameters.get("section_label")
        
        # Validate parameters
        if not section_label:
            return {"error": "section_label is required"}
        
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
        
        # Get beats within this section
        beats_in_section = self.app.audio_analysis_manager.get_beats_in_range(
            section["start"], section["end"], "all"
        )
        
        # Get downbeats within this section
        downbeats_in_section = self.app.audio_analysis_manager.get_beats_in_range(
            section["start"], section["end"], "downbeat"
        )
        
        # Get average energy in this section
        analysis_data = self.app.audio_analysis_manager.load_analysis()
        avg_energy = None
        if analysis_data and "energy_timeseries" in analysis_data:
            energy_data = analysis_data["energy_timeseries"]
            energy_times = energy_data["times"]
            energy_values = energy_data["values"]
            
            # Find energy values within section
            section_energy_values = [
                energy_values[i] for i, t in enumerate(energy_times)
                if section["start"] <= t < section["end"]
            ]
            
            if section_energy_values:
                avg_energy = sum(section_energy_values) / len(section_energy_values)
        
        # Return section details with additional information
        return {
            "label": section["label"],
            "start_time": section["start"],
            "end_time": section["end"],
            "duration": section["end"] - section["start"],
            "beats": beats_in_section,
            "beat_count": len(beats_in_section),
            "downbeats": downbeats_in_section,
            "downbeat_count": len(downbeats_in_section),
            "average_energy": avg_energy
        }
    
    def _handle_get_feature_value_at_time(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the get_feature_value_at_time action.
        
        Args:
            parameters: Action parameters.
            
        Returns:
            dict: Feature value at the specified time.
        """
        if not hasattr(self.app, 'audio_analysis_manager'):
            return {"error": "Audio analysis manager not available"}
        
        # Extract parameters
        time = parameters.get("time")
        feature_name = parameters.get("feature_name")
        
        # Validate parameters
        if time is None:
            return {"error": "time is required"}
        
        if not feature_name:
            return {"error": "feature_name is required"}
        
        # Get feature value
        value = self.app.audio_analysis_manager.get_feature_value_at_time(time, feature_name)
        if value is None:
            return {"error": f"Feature '{feature_name}' not found or no value at time {time}"}
        
        # Format the response based on feature type
        if feature_name == "chroma":
            # Chroma represents the 12 pitch classes (C, C#, D, etc.)
            pitch_classes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            return {
                "time": time,
                "feature": feature_name,
                "value": value,
                "pitch_classes": {pitch_classes[i]: value[i] for i in range(min(len(value), len(pitch_classes)))}
            }
        elif feature_name == "spectral_contrast":
            # Spectral contrast represents different frequency bands
            bands = ["sub-band", "band-1", "band-2", "band-3", "band-4", "band-5", "band-6"]
            return {
                "time": time,
                "feature": feature_name,
                "value": value,
                "bands": {bands[i]: value[i] for i in range(min(len(value), len(bands)))}
            }
        else:
            # Single value features
            return {
                "time": time,
                "feature": feature_name,
                "value": value
            }