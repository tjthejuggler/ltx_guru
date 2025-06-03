"""
Sequence Maker - Project Model

This module defines the Project class, which represents a sequence maker project.
"""

import os
import json
import base64
import logging
from datetime import datetime
from pathlib import Path

from app.constants import APP_VERSION, PROJECT_FILE_EXTENSION
from models.lyrics import Lyrics
from models.timeline import Timeline
from models.segment import TimelineSegment
from utils.file_type_utils import is_valid_ball_sequence, is_valid_seqdesign


class Project:
    """
    Represents a sequence maker project.
    
    A project contains all the information needed to recreate a sequence,
    including timelines, audio data, key mappings, and settings.
    """
    
    def __init__(self, name="Untitled Project"):
        """
        Initialize a new project.
        
        Args:
            name (str, optional): Project name. Defaults to "Untitled Project".
        """
        self.logger = logging.getLogger("SequenceMaker.Project")
        
        # Project metadata
        self.name = name
        self.created = datetime.now().isoformat()
        self.modified = self.created
        self.description = ""
        self.version = APP_VERSION
        
        # Project settings
        self.default_pixels = 4
        self.refresh_rate = 100  # 100 Hz for 1/100th second precision
        self.total_duration = 60  # seconds
        self.zoom_level = 1.0  # Default zoom level
        
        # Project data
        self.timelines = []
        self.key_mappings = {}
        self.effects = {}
        # Audio data
        self.audio_file = None
        self.audio_data = None
        self.audio_duration = 0
        self.visualizations = {
            "selected": ["waveform", "beats"],
            "settings": {
                "waveform": {"color": [0, 0, 255], "height": 100},
                "beats": {"color": [255, 0, 0], "threshold": 0.5}
            }
        }
        
        # Lyrics data
        self.lyrics = Lyrics()
        
        # LLM data
        self.chat_history = []
        self.llm_metadata = {
            "token_usage": 0,
            "estimated_cost": 0.0,
            "interactions": []
        }
        
        # LLM customization data
        self.llm_custom_instructions = ""
        self.llm_presets = []
        self.llm_task_templates = []
        self.llm_active_preset = "Default"
        
        # File path (None for new projects)
        self.file_path = None
    
    def to_dict(self):
        """
        Convert the project to a dictionary for serialization.
        
        Returns:
            dict: Project data as a dictionary.
        """
        # Convert timelines to dictionaries
        timeline_dicts = [timeline.to_dict() for timeline in self.timelines]
        
        # Encode audio data if present
        audio_data_b64 = None
        if self.audio_data:
            audio_data_b64 = base64.b64encode(self.audio_data).decode('utf-8')
        
        # Update modified timestamp
        self.modified = datetime.now().isoformat()
        
        return {
            "metadata": {
                "version": self.version,
                "created": self.created,
                "modified": self.modified,
                "name": self.name,
                "description": self.description
            },
            "settings": {
                "defaultPixels": self.default_pixels,
                "refreshRate": self.refresh_rate,
                "totalDuration": self.total_duration,
                "zoomLevel": self.zoom_level
            },
            "keyMappings": self.key_mappings,
            "effects": self.effects,
            "timelines": timeline_dicts,
            "audio": {
                "embedded": bool(self.audio_data),
                "filename": self.audio_file if self.audio_file else None,  # Store full path
                "filepath": self.audio_file if self.audio_file else None,  # Add full path for backward compatibility
                "duration": self.audio_duration,
                "data": audio_data_b64
            },
            "visualizations": self.visualizations,
            "lyrics": self.lyrics.to_dict() if self.lyrics else {},
            "chat_history": self.chat_history,
            "llm_metadata": self.llm_metadata,
            "llm_customization": {
                "custom_instructions": self.llm_custom_instructions,
                "presets": self.llm_presets,
                "task_templates": self.llm_task_templates,
                "active_preset": self.llm_active_preset
            }
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a project from a dictionary.
        
        Args:
            data (dict): Project data as a dictionary.
        
        Returns:
            Project: A new Project instance.
        """
        from models.timeline import Timeline
        
        project = cls(name=data["metadata"]["name"])
        
        # Set metadata
        project.created = data["metadata"]["created"]
        project.modified = data["metadata"]["modified"]
        project.description = data["metadata"].get("description", "")
        project.version = data["metadata"]["version"]
        
        # Set settings
        project.default_pixels = data["settings"]["defaultPixels"]
        project.refresh_rate = data["settings"]["refreshRate"]
        project.total_duration = data["settings"]["totalDuration"]
        project.zoom_level = data["settings"].get("zoomLevel", 1.0)  # Default to 1.0 if not present
        
        # Set data
        project.key_mappings = data["keyMappings"]
        project.effects = data["effects"]
        
        # Create timelines
        for timeline_data in data["timelines"]:
            timeline = Timeline.from_dict(timeline_data)
            project.timelines.append(timeline)
        
        # Set audio data
        audio = data.get("audio", {})
        # Always attempt to load audio file path and duration
        project.audio_file = audio.get("filepath") or audio.get("filename")
        project.audio_duration = audio.get("duration", 0)

        if audio.get("embedded") and audio.get("data"):
            try:
                project.audio_data = base64.b64decode(audio["data"])
                # project.audio_file and project.audio_duration are already set
            except Exception as e:
                project.logger.error(f"Error decoding embedded audio data: {e}")
                project.audio_data = None # Ensure audio_data is None if decoding fails
        else:
            # Not embedded, or no data even if embedded flag is true
            project.audio_data = None
        
        # Set visualizations
        project.visualizations = data.get("visualizations", {
            "selected": ["waveform", "beats"],
            "settings": {
                "waveform": {"color": [0, 0, 255], "height": 100},
                "beats": {"color": [255, 0, 0], "threshold": 0.5}
            }
        })
        
        # Set lyrics data
        if "lyrics" in data:
            project.lyrics = Lyrics.from_dict(data["lyrics"])
        
        # Set LLM data
        project.chat_history = data.get("chat_history", [])
        project.llm_metadata = data.get("llm_metadata", {
            "token_usage": 0,
            "estimated_cost": 0.0,
            "interactions": []
        })
        
        # Set LLM customization data
        llm_customization = data.get("llm_customization", {})
        project.llm_custom_instructions = llm_customization.get("custom_instructions", "")
        project.llm_presets = llm_customization.get("presets", [])
        project.llm_task_templates = llm_customization.get("task_templates", [])
        project.llm_active_preset = llm_customization.get("active_preset", "Default")
        
        return project
    
    def save(self, file_path=None):
        """
        Save the project to a file.
        
        Args:
            file_path (str, optional): Path to save the project to. If None, uses the current file_path.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if file_path:
            self.file_path = file_path
        
        if not self.file_path:
            self.logger.error("No file path specified for project save")
            return False
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)
        
        # Add file extension if not present
        if not self.file_path.endswith(PROJECT_FILE_EXTENSION):
            self.file_path += PROJECT_FILE_EXTENSION
        
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            
            self.logger.info(f"Project saved to {self.file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving project: {e}")
            return False
    
    @classmethod
    def load(cls, file_path):
        """
        Load a project from a file.
        
        Args:
            file_path (str): Path to the project file.
        
        Returns:
            Project: A new Project instance, or None if loading failed.
        """
        logger = logging.getLogger("SequenceMaker.Project")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            project = cls.from_dict(data)
            project.file_path = file_path
            
            logger.info(f"Project loaded from {file_path}")
            return project
        except Exception as e:
            logger.error(f"Error loading project: {e}")
            return None
    
    def add_timeline(self, timeline):
        """
        Add a timeline to the project.
        
        Args:
            timeline: Timeline to add.
        """
        self.timelines.append(timeline)
    
    def remove_timeline(self, timeline):
        """
        Remove a timeline from the project.
        
        Args:
            timeline: Timeline to remove.
        
        Returns:
            bool: True if the timeline was removed, False if it wasn't found.
        """
        if timeline in self.timelines:
            self.timelines.remove(timeline)
            return True
        return False
    
    def get_timeline(self, index):
        """
        Get a timeline by index.
        
        Args:
            index (int): Timeline index.
        
        Returns:
            Timeline: The timeline at the specified index, or None if the index is out of range.
        """
        if 0 <= index < len(self.timelines):
            return self.timelines[index]
        return None
    
    def set_audio(self, file_path, audio_data=None):
        """
        Set the project's audio file.
        
        Args:
            file_path (str): Path to the audio file.
            audio_data (bytes or numpy.ndarray, optional): Audio file data. If None, the file will be read.
                If a numpy array is provided, the file will be read instead.
        """
        self.audio_file = file_path
        
        # Handle the case where audio_data is a NumPy array
        import numpy as np
        if isinstance(audio_data, np.ndarray):
            self.logger.warning("NumPy array provided as audio_data, reading file instead")
            audio_data = None
        
        if audio_data is not None:
            self.audio_data = audio_data
        else:
            try:
                with open(file_path, 'rb') as f:
                    self.audio_data = f.read()
            except Exception as e:
                self.logger.error(f"Error reading audio file: {e}")
                self.audio_data = None
    
    def set_lyrics(self, song_name=None, artist_name=None, lyrics_text=None, word_timestamps=None):
        """
        Set the project's lyrics data.
        
        Args:
            song_name (str, optional): Song name. Defaults to None.
            artist_name (str, optional): Artist name. Defaults to None.
            lyrics_text (str, optional): Lyrics text. Defaults to None.
            word_timestamps (list, optional): List of word timestamps. Defaults to None.
        """
        if not hasattr(self, 'lyrics') or self.lyrics is None:
            self.lyrics = Lyrics()
            
        if song_name is not None:
            self.lyrics.song_name = song_name
            
        if artist_name is not None:
            self.lyrics.artist_name = artist_name
            
        if lyrics_text is not None:
            self.lyrics.lyrics_text = lyrics_text
            
        if word_timestamps is not None:
            self.lyrics.word_timestamps = word_timestamps
    
    def import_ball_sequence(self, file_path):
        """
        Import a ball sequence file.
        
        Args:
            file_path (str): Path to the ball sequence file
            
        Returns:
            Timeline: The imported timeline, or None if import failed
        """
        if not is_valid_ball_sequence(file_path):
            return None
        
        try:
            with open(file_path, 'r') as f:
                ball_data = json.load(f)
            
            # Create a new timeline
            timeline = Timeline(
                name=ball_data.get("metadata", {}).get("name", "Imported Ball"),
                default_pixels=ball_data.get("metadata", {}).get("default_pixels", 4)
            )
            
            # Add segments to timeline
            for segment in ball_data.get("segments", []):
                timeline_segment = TimelineSegment(
                    start_time=segment["start_time"],
                    end_time=segment["end_time"],
                    color=tuple(segment["color"]),
                    pixels=segment["pixels"]
                )
                timeline.add_segment(timeline_segment)
            
            # Add timeline to project
            self.add_timeline(timeline)
            
            return timeline
        except Exception as e:
            print(f"Error importing ball sequence: {str(e)}")
            return None