"""
Sequence Maker - Audio Analysis Manager

This module defines the AudioAnalysisManager class, which handles comprehensive audio analysis
using librosa and stores results in a structured JSON format.
"""

import os
import json
import logging
import hashlib
from pathlib import Path

try:
    import librosa
    import numpy as np
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False


class AudioAnalysisManager:
    """
    Manages comprehensive audio analysis and caching of analysis results.
    
    This manager performs detailed audio analysis using librosa and stores the results
    in JSON format for later use by LLM tools and other components.
    """
    
    def __init__(self, app):
        """
        Initialize the audio analysis manager.
        
        Args:
            app: The main application instance.
        """
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.AudioAnalysisManager")
        
        # Create analysis cache directory
        self.analysis_cache_dir = Path.home() / ".sequence_maker" / "analysis_cache"
        self.analysis_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Current analysis path
        self.current_analysis_path = None
        
        # Check if librosa is available
        if not LIBROSA_AVAILABLE:
            self.logger.warning("Librosa not available. Audio analysis functionality will be limited.")
    
    def analyze_audio(self, audio_file_path=None):
        """
        Analyze audio file to extract musical features.
        
        Args:
            audio_file_path: Path to audio file (uses currently loaded audio if None)
            
        Returns:
            dict: Analysis data
        """
        # Use current audio if path not provided
        if audio_file_path is None and hasattr(self.app, 'audio_manager'):
            audio_data = self.app.audio_manager.audio_data
            sample_rate = self.app.audio_manager.sample_rate
            audio_file_path = self.app.audio_manager.audio_file
            
            if audio_data is None or sample_rate is None:
                self.logger.warning("No audio data available in audio manager")
                return None
        else:
            # Check if file exists
            if not audio_file_path or not os.path.exists(audio_file_path):
                self.logger.error(f"Audio file not found: {audio_file_path}")
                return None
                
            # Load audio using librosa
            try:
                self.logger.info(f"Loading audio for analysis: {audio_file_path}")
                audio_data, sample_rate = librosa.load(audio_file_path, sr=None)
            except Exception as e:
                self.logger.error(f"Error loading audio file: {e}")
                return None
        
        # Generate analysis file path based on audio file path
        analysis_path = self._get_analysis_path_for_audio(audio_file_path)
        self.current_analysis_path = analysis_path
        
        # Check if analysis already exists and is recent
        if os.path.exists(analysis_path):
            audio_mtime = os.path.getmtime(audio_file_path) if audio_file_path else 0
            analysis_mtime = os.path.getmtime(analysis_path)
            
            if analysis_mtime >= audio_mtime:
                self.logger.info(f"Using existing analysis from {analysis_path}")
                try:
                    with open(analysis_path, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    self.logger.warning(f"Error loading existing analysis, will recreate: {e}")
        
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
        
        return analysis_data
    
    def _extract_features(self, audio_data, sample_rate, audio_file_path=None):
        """
        Extract musical features from audio data.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio
            audio_file_path: Path to the audio file (for metadata)
            
        Returns:
            dict: Analysis data
        """
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
        
        # Spectral features
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
        spectral_contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sample_rate)
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
        
        # Zero crossing rate (useful for distinguishing voiced from unvoiced speech)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)[0]
        
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
            },
            "chroma_features": {
                "times": [float(t) for t in librosa.times_like(chroma[0], sr=sample_rate)],
                "values": [[float(v) for v in row] for row in chroma]
            },
            "spectral_contrast": {
                "times": [float(t) for t in librosa.times_like(spectral_contrast[0], sr=sample_rate)],
                "values": [[float(v) for v in row] for row in spectral_contrast]
            },
            "spectral_centroid": {
                "times": [float(t) for t in librosa.times_like(spectral_centroid, sr=sample_rate)],
                "values": [float(v) for v in spectral_centroid]
            },
            "spectral_rolloff": {
                "times": [float(t) for t in librosa.times_like(spectral_rolloff, sr=sample_rate)],
                "values": [float(v) for v in spectral_rolloff]
            },
            "zero_crossing_rate": {
                "times": [float(t) for t in librosa.times_like(zero_crossing_rate, sr=sample_rate)],
                "values": [float(v) for v in zero_crossing_rate]
            }
        }
    
    def _get_analysis_path_for_audio(self, audio_file_path):
        """
        Generate a path for the analysis JSON based on the audio file path.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Path: Path to the analysis JSON file
        """
        if not audio_file_path:
            return self.analysis_cache_dir / "unknown_audio_analysis.json"
        
        # Create a hash of the audio path to use as filename
        path_hash = hashlib.md5(str(audio_file_path).encode()).hexdigest()
        return self.analysis_cache_dir / f"{path_hash}_analysis.json"
    
    def get_analysis_path(self):
        """
        Get the path to the current analysis JSON.
        
        Returns:
            Path: Path to the current analysis JSON file
        """
        return self.current_analysis_path
    
    def load_analysis(self):
        """
        Load the current analysis data from JSON.
        
        Returns:
            dict: Analysis data, or None if no analysis is available
        """
        if not self.current_analysis_path or not os.path.exists(self.current_analysis_path):
            # Try to analyze current audio if available
            if hasattr(self.app, 'audio_manager') and self.app.audio_manager.audio_file:
                return self.analyze_audio()
            return None
        
        try:
            with open(self.current_analysis_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading analysis data: {e}")
            return None
    
    def analyze_current_audio(self):
        """
        Analyze the currently loaded audio in the audio manager.
        
        Returns:
            dict: Analysis data, or None if no audio is loaded
        """
        if not hasattr(self.app, 'audio_manager') or not self.app.audio_manager.audio_file:
            self.logger.warning("No audio loaded in audio manager")
            return None
        
        return self.analyze_audio(self.app.audio_manager.audio_file)
    
    def get_section_by_label(self, section_label):
        """
        Get a section by its label.
        
        Args:
            section_label: Label of the section to find
            
        Returns:
            dict: Section data, or None if not found
        """
        analysis_data = self.load_analysis()
        if not analysis_data:
            return None
        
        for section in analysis_data.get("sections", []):
            if section["label"] == section_label:
                return section
        
        return None
    
    def get_beats_in_range(self, start_time, end_time, beat_type="all"):
        """
        Get beats within a time range.
        
        Args:
            start_time: Start time in seconds
            end_time: End time in seconds
            beat_type: Type of beats to get ("all" or "downbeat")
            
        Returns:
            list: Beat times within the range
        """
        analysis_data = self.load_analysis()
        if not analysis_data:
            return []
        
        if beat_type == "downbeat":
            beats = analysis_data.get("downbeats", [])
        else:
            beats = analysis_data.get("beats", [])
        
        return [beat for beat in beats if start_time <= beat < end_time]
    
    def get_feature_value_at_time(self, time, feature_name):
        """
        Get the value of a feature at a specific time.
        
        Args:
            time: Time in seconds
            feature_name: Name of the feature
            
        Returns:
            float or list: Feature value at the specified time
        """
        analysis_data = self.load_analysis()
        if not analysis_data:
            return None
        
        # Map feature name to data structure
        feature_map = {
            "energy": "energy_timeseries",
            "onset_strength": "onset_strength_timeseries",
            "chroma": "chroma_features",
            "spectral_contrast": "spectral_contrast",
            "spectral_centroid": "spectral_centroid",
            "spectral_rolloff": "spectral_rolloff",
            "zero_crossing_rate": "zero_crossing_rate"
        }
        
        feature_key = feature_map.get(feature_name)
        if not feature_key or feature_key not in analysis_data:
            return None
        
        feature_data = analysis_data[feature_key]
        times = feature_data["times"]
        values = feature_data["values"]
        
        # Find closest time index
        closest_idx = min(range(len(times)), key=lambda i: abs(times[i] - time))
        
        # Get value at that time
        if feature_name in ["chroma", "spectral_contrast"]:
            # These are multi-dimensional features
            return [row[closest_idx] for row in values]
        else:
            return values[closest_idx]