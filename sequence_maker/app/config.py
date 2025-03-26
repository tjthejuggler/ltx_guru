"""
Sequence Maker - Configuration Module

This module handles loading, saving, and accessing application configuration.
"""

import os
import json
import logging
from pathlib import Path


class Config:
    """Configuration manager for the Sequence Maker application."""
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "general": {
            "autosave_interval": 300,  # seconds
            "max_autosave_files": 5,
            "default_project_dir": str(Path.home() / "SequenceMaker"),
            "recent_projects": [],
            "recent_audio_files": [],
            "last_project": ""
        },
        "timeline": {
            "default_duration": 60,  # seconds
            "default_pixels": 4,
            "default_refresh_rate": 1,
            "default_ball_count": 3,
            "zoom_step": 1.2,
            "timeline_height": 100,
            "segment_min_width": 5
        },
        "audio": {
            "volume": 0.8,
            "loop": False,
            "visualizations": ["waveform", "beats"],
            "beat_detection_threshold": 0.5,
            "waveform_color": [0, 0, 255],
            "beats_color": [255, 0, 0]
        },
        "colors": {
            "default_colors": [
                [255, 0, 0],      # Red
                [255, 165, 0],    # Orange
                [255, 255, 0],    # Yellow
                [0, 255, 0],      # Green
                [0, 255, 255],    # Cyan
                [0, 0, 255],      # Blue
                [255, 0, 255],    # Pink
                [255, 255, 255],  # White
                [0, 0, 0]         # Black
            ]
        },
        "key_mappings": {
            "default_mapping": "standard",
            "mappings": {
                "standard": {
                    "ball_1_keys": ["q", "w", "e", "r", "t", "y", "u", "i", "o"],
                    "ball_2_keys": ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
                    "ball_3_keys": ["z", "x", "c", "v", "b", "n", "m", ",", "."],
                    "all_balls_keys": ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
                }
            },
            "effect_modifiers": {
                "shift": "strobe",
                "ctrl": "fade",
                "alt": "custom"
            }
        },
        "effects": {
            "strobe": {
                "frequency": 10,
                "duty_cycle": 0.5
            },
            "fade": {
                "duration": 1.0
            }
        },
        "ball_control": {
            "discovery_timeout": 5,
            "network_subnet": "192.168.1",
            "port": 41412
        },
        "llm": {
            "enabled": False,
            "provider": "",
            "api_key": "",
            "model": "",
            "temperature": 0.7,
            "active_profile": "default",
            "profiles": {
                "default": {
                    "name": "Default",
                    "provider": "",
                    "api_key": "",
                    "model": "",
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "top_p": 1.0,
                    "frequency_penalty": 0.0,
                    "presence_penalty": 0.0
                }
            }
        },
        "ui": {
            "theme": "system",
            "font_size": 10,
            "window_size": [1280, 720],
            "window_position": [100, 100],
            "timeline_position": "top",
            "ball_visualization_position": "bottom"
        }
    }
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.logger = logging.getLogger("SequenceMaker.Config")
        self.config_dir = Path.home() / ".sequence_maker"
        self.config_file = self.config_dir / "config.json"
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load()
    
    def load(self):
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                
                # Update config with loaded values, preserving defaults for missing keys
                self._update_recursive(self.config, loaded_config)
                self.logger.info("Configuration loaded successfully")
            except Exception as e:
                self.logger.error(f"Error loading configuration: {e}")
                # Keep default configuration
        else:
            self.logger.info("No configuration file found, using defaults")
            # Save default configuration
            self.save()
    
    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def get(self, section, key=None, default=None):
        """
        Get a configuration value.
        
        Args:
            section (str): Configuration section
            key (str, optional): Configuration key within section. If None, returns the entire section.
            default: Default value to return if the key is not found.
        
        Returns:
            The configuration value, or the default value if not found.
        """
        if section not in self.config:
            return default
        
        if key is None:
            return self.config[section]
        
        return self.config[section].get(key, default)
    
    def set(self, section, key, value):
        """
        Set a configuration value.
        
        Args:
            section (str): Configuration section
            key (str): Configuration key within section
            value: Value to set
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
    
    def add_recent_project(self, project_path):
        """
        Add a project to the recent projects list.
        
        Args:
            project_path (str): Path to the project file
        """
        recent = self.config["general"]["recent_projects"]
        
        # Remove if already in list
        if project_path in recent:
            recent.remove(project_path)
        
        # Add to beginning of list
        recent.insert(0, project_path)
        
        # Limit list size
        self.config["general"]["recent_projects"] = recent[:10]
    
    def add_recent_audio(self, audio_path):
        """
        Add an audio file to the recent audio files list.
        
        Args:
            audio_path (str): Path to the audio file
        """
        recent = self.config["general"]["recent_audio_files"]
        
        # Remove if already in list
        if audio_path in recent:
            recent.remove(audio_path)
        
        # Add to beginning of list
        recent.insert(0, audio_path)
        
        # Limit list size
        self.config["general"]["recent_audio_files"] = recent[:10]
    
    def _update_recursive(self, target, source):
        """
        Recursively update a nested dictionary with values from another dictionary.
        
        Args:
            target (dict): Target dictionary to update
            source (dict): Source dictionary with new values
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_recursive(target[key], value)
            else:
                target[key] = value