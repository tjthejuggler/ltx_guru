#!/usr/bin/env python3
"""
Audio Analyzer for LTX Sequence Maker

This module provides comprehensive audio analysis capabilities for creating
color sequences synchronized with music. It extracts musical features like
beats, sections, and energy levels from audio files.
"""

import os
import json
import logging
import hashlib
from pathlib import Path
import tempfile
import subprocess
import requests
from typing import Dict, List, Tuple, Union, Optional, Any

try:
    import librosa
    import numpy as np
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("Warning: librosa not available. Install with 'pip install librosa'")


class AudioAnalyzer:
    """
    Comprehensive audio analysis tool for extracting musical features from audio files.
    """
    
    def __init__(self, cache_dir=None):
        """Initialize the audio analyzer."""
        self.logger = logging.getLogger("AudioAnalyzer")
        
        # Create analysis cache directory
        if cache_dir:
            self.analysis_cache_dir = Path(cache_dir)
        else:
            self.analysis_cache_dir = Path.home() / ".ltx_sequence_maker" / "analysis_cache"
        
        self.analysis_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Current analysis data and path
        self.current_analysis_data = None
        self.current_analysis_path = None
        self.current_audio_path = None
        
        # Check if librosa is available
        if not LIBROSA_AVAILABLE:
            self.logger.warning("Librosa not available. Audio analysis functionality will be limited.")
    
    def analyze_audio(self, audio_file_path):
        """Analyze audio file to extract musical features."""
        # Check if file exists
        if not os.path.exists(audio_file_path):
            self.logger.error(f"Audio file not found: {audio_file_path}")
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        # Store the current audio path
        self.current_audio_path = audio_file_path
        
        # Generate analysis file path based on audio file path
        analysis_path = self._get_analysis_path_for_audio(audio_file_path)
        self.current_analysis_path = analysis_path
        
        # Check if analysis already exists and is recent
        if os.path.exists(analysis_path):
            audio_mtime = os.path.getmtime(audio_file_path)
            analysis_mtime = os.path.getmtime(analysis_path)
            
            if analysis_mtime >= audio_mtime:
                self.logger.info(f"Using existing analysis from {analysis_path}")
                try:
                    with open(analysis_path, 'r') as f:
                        analysis_data = json.load(f)
                        self.current_analysis_data = analysis_data
                        return analysis_data
                except Exception as e:
                    self.logger.warning(f"Error loading existing analysis, will recreate: {e}")
        
        # Load audio using librosa
        try:
            self.logger.info(f"Loading audio for analysis: {audio_file_path}")
            audio_data, sample_rate = librosa.load(audio_file_path, sr=None)
        except Exception as e:
            self.logger.error(f"Error loading audio file: {e}")
            raise RuntimeError(f"Error loading audio file: {e}")
        
        # Extract features
        self.logger.info("Performing comprehensive audio analysis...")
        analysis_data = self._extract_features(audio_data, sample_rate, audio_file_path)
        
        # Save to JSON
        try:
            with open(analysis_path, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            self.logger.info(f"Analysis saved to {analysis_path}")
        except Exception as e:
            self.logger.error(f"Error saving analysis data: {e}")
        
        # Store the current analysis data
        self.current_analysis_data = analysis_data
        
        return analysis_data
    
    def _extract_features(self, audio_data, sample_rate, audio_file_path=None):
        """Extract musical features from audio data."""
        # Basic features
        duration = librosa.get_duration(y=audio_data, sr=sample_rate)
        tempo, beat_frames = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
        beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate)
        
        # Derive downbeats (assuming 4/4 time signature)
        downbeats = beat_times[::4]  # Every 4th beat
        
        # Segment analysis for section detection
        mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate)
        segment_boundaries = librosa.segment.agglomerative(mfcc, 8)  # 8 segments
        segment_times = librosa.frames_to_time(segment_boundaries, sr=sample_rate)
        
        # Create labeled sections
        sections = []
        section_labels = ["Intro", "Verse 1", "Chorus 1", "Verse 2", "Chorus 2", "Bridge", "Chorus 3", "Outro"]
        for i in range(len(segment_times) - 1):
            label = section_labels[i] if i < len(section_labels) else f"Section {i+1}"
            sections.append({
                "label": label,
                "start": float(segment_times[i]),
                "end": float(segment_times[i+1])
            })
        
        # Energy and onset strength
        rms = librosa.feature.rms(y=audio_data)[0]
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=sample_rate)
        
        # Convert numpy arrays to lists for JSON serialization
        times = librosa.times_like(rms, sr=sample_rate)
        
        # Create analysis data structure
        return {
            "song_title": os.path.basename(audio_file_path) if audio_file_path else "Unknown",
            "duration_seconds": float(duration),
            "estimated_tempo": float(tempo),
            "time_signature_guess": "4/4",
            "beats": [float(t) for t in beat_times],
            "downbeats": [float(t) for t in downbeats],
            "sections": sections,
            "energy_timeseries": {
                "times": [float(t) for t in times],
                "values": [float(v) for v in rms]
            },
            "onset_strength_timeseries": {
                "times": [float(t) for t in librosa.times_like(onset_env, sr=sample_rate)],
                "values": [float(v) for v in onset_env]
            }
        }
    
    def _get_analysis_path_for_audio(self, audio_file_path):
        """Generate a path for the analysis JSON based on the audio file path."""
        # Create a hash of the audio path to use as filename
        path_hash = hashlib.md5(str(audio_file_path).encode()).hexdigest()
        return self.analysis_cache_dir / f"{path_hash}_analysis.json"
    
    def get_beats_in_range(self, start_time, end_time, beat_type="all"):
        """Get beats within a time range."""
        if not self.current_analysis_data:
            raise ValueError("No analysis data available. Call analyze_audio() first.")
        
        if beat_type == "downbeat":
            beats = self.current_analysis_data.get("downbeats", [])
        else:
            beats = self.current_analysis_data.get("beats", [])
        
        return [beat for beat in beats if start_time <= beat < end_time]
    
    def get_section_by_label(self, section_label):
        """Get a section by its label."""
        if not self.current_analysis_data:
            raise ValueError("No analysis data available. Call analyze_audio() first.")
        
        for section in self.current_analysis_data.get("sections", []):
            if section["label"] == section_label:
                return section
        
        return None
    
    def get_feature_timeseries(self, feature_name):
        """Get the entire timeseries for a feature."""
        if not self.current_analysis_data:
            raise ValueError("No analysis data available. Call analyze_audio() first.")
        
        # Map feature name to data structure
        feature_map = {
            "energy": "energy_timeseries",
            "onset_strength": "onset_strength_timeseries"
        }
        
        feature_key = feature_map.get(feature_name)
        if not feature_key or feature_key not in self.current_analysis_data:
            raise ValueError(f"Unknown feature: {feature_name}")
        
        return self.current_analysis_data[feature_key]


class LyricsProcessor:
    """Processor for lyrics alignment with audio."""
    
    def __init__(self, api_keys_path=None):
        """Initialize the lyrics processor."""
        self.logger = logging.getLogger("LyricsProcessor")
        self.current_lyrics_data = None
        self._load_api_keys(api_keys_path)
    
    def _load_api_keys(self, api_keys_path=None):
        """Load API keys from config file."""
        # Define the path to the API keys file
        if api_keys_path:
            api_keys_path = api_keys_path
        else:
            api_keys_path = os.path.expanduser("~/.ltx_sequence_maker/api_keys.json")
        
        # Initialize default empty keys
        self.acr_access_key = ""
        self.acr_secret_key = ""
        self.acr_host = ""
        self.genius_api_key = ""
        
        # Try to load keys from file
        if os.path.exists(api_keys_path):
            try:
                with open(api_keys_path, 'r') as f:
                    keys = json.load(f)
                
                self.acr_access_key = keys.get("acr_access_key", "")
                self.acr_secret_key = keys.get("acr_secret_key", "")
                self.acr_host = keys.get("acr_host", "")
                self.genius_api_key = keys.get("genius_api_key", "")
                
                self.logger.info("Loaded API keys from config file")
            except Exception as e:
                self.logger.error(f"Error loading API keys: {e}")
    
    def process_audio(self, audio_path, lyrics_text=None, conservative=False):
        """Process audio to extract and align lyrics."""
        # Implementation details omitted for brevity
        # This would include song identification, lyrics fetching, and alignment
        pass
    
    def get_words_in_range(self, start_time, end_time):
        """Get words within a time range."""
        if not self.current_lyrics_data:
            raise ValueError("No lyrics data available. Call process_audio() first.")
        
        word_timestamps = self.current_lyrics_data.get("word_timestamps", [])
        
        return [word for word in word_timestamps if start_time <= word["start"] < end_time]


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    analyzer = AudioAnalyzer()
    
    # Analyze an audio file
    # analysis_data = analyzer.analyze_audio("/path/to/your/audio.mp3")
    
    # Get beats in a specific range
    # beats = analyzer.get_beats_in_range(0, 30)  # Get beats in the first 30 seconds
