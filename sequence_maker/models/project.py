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
                "totalDuration": self.total_duration
            },
            "keyMappings": self.key_mappings,
            "effects": self.effects,
            "timelines": timeline_dicts,
            "audio": {
                "embedded": bool(self.audio_data),
                "filename": os.path.basename(self.audio_file) if self.audio_file else None,
                "duration": self.audio_duration,
                "data": audio_data_b64
            },
            "visualizations": self.visualizations
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
        
        # Set data
        project.key_mappings = data["keyMappings"]
        project.effects = data["effects"]
        
        # Create timelines
        for timeline_data in data["timelines"]:
            timeline = Timeline.from_dict(timeline_data)
            project.timelines.append(timeline)
        
        # Set audio data
        audio = data.get("audio", {})
        if audio.get("embedded") and audio.get("data"):
            project.audio_data = base64.b64decode(audio["data"])
            project.audio_file = audio.get("filename")
            project.audio_duration = audio.get("duration", 0)
        
        # Set visualizations
        project.visualizations = data.get("visualizations", {
            "selected": ["waveform", "beats"],
            "settings": {
                "waveform": {"color": [0, 0, 255], "height": 100},
                "beats": {"color": [255, 0, 0], "threshold": 0.5}
            }
        })
        
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
            audio_data (bytes, optional): Audio file data. If None, the file will be read.
        """
        self.audio_file = file_path
        
        if audio_data:
            self.audio_data = audio_data
        else:
            try:
                with open(file_path, 'rb') as f:
                    self.audio_data = f.read()
            except Exception as e:
                self.logger.error(f"Error reading audio file: {e}")
                self.audio_data = None