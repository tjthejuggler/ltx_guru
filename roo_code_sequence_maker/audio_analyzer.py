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
import time
from pathlib import Path
import tempfile
import subprocess
import requests
import lyricsgenius
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
    
    This class provides methods to analyze audio files and extract musical features like
    beats, sections, and energy levels. It includes a robust caching mechanism to avoid
    re-analyzing the same audio file unnecessarily.
    
    The caching system works as follows:
    1. Cache keys are generated based on the audio file path, file content hash, and
       analysis parameters.
    2. Cache files are stored in a configurable directory (defaults to
       ~/.ltx_sequence_maker/analysis_cache).
    3. Cache invalidation is based on file modification time and content hash.
    4. Cache files use JSON format for compatibility and readability.
    """
    
    def __init__(self, cache_dir=None, api_keys_path=None):
        """
        Initialize the audio analyzer with optional custom cache directory.
        
        Args:
            cache_dir (str, optional): Custom directory to store analysis cache files.
                If not provided, defaults to ~/.ltx_sequence_maker/analysis_cache.
            api_keys_path (str, optional): Path to the API keys JSON file for lyrics processing.
                If not provided, defaults to standard locations.
        """
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
        
        # Analysis parameters - can be extended in the future
        self.analysis_params = {}
        
        # Store API keys path
        self.api_keys_path = api_keys_path
        
        # Initialize lyrics processor
        self.lyrics_processor = LyricsProcessor(api_keys_path=self.api_keys_path)
        
        # Check if librosa is available
        if not LIBROSA_AVAILABLE:
            self.logger.warning("Librosa not available. Audio analysis functionality will be limited.")
    
    def analyze_audio(self, audio_file_path, force_reanalysis=False, analysis_params=None):
        """
        Analyze audio file to extract musical features.
        
        This method checks if a valid cached analysis exists before performing a new analysis.
        The cache is considered valid if:
        1. The cache file exists
        2. The audio file hasn't been modified since the cache was created
        3. The file content hash matches the one stored in the cache
        4. The analysis parameters match those used to create the cache
        
        Args:
            audio_file_path (str): Path to the audio file to analyze
            force_reanalysis (bool, optional): If True, ignore cache and reanalyze. Defaults to False.
            analysis_params (dict, optional): Additional parameters for analysis. Defaults to None.
                These parameters will be included in the cache key.
                Special parameters:
                - request_lyrics (bool): If True, process lyrics for the audio file
                - conservative_lyrics_alignment (bool): If True, use conservative alignment for lyrics
                - user_provided_lyrics (str): User-provided lyrics text, if available
        
        Returns:
            dict: Analysis data containing musical features
            
        Raises:
            FileNotFoundError: If the audio file doesn't exist
            RuntimeError: If there's an error loading or analyzing the audio file
        """
        # Check if file exists
        if not os.path.exists(audio_file_path):
            self.logger.error(f"Audio file not found: {audio_file_path}")
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        # Store the current audio path and analysis parameters
        self.current_audio_path = audio_file_path
        self.analysis_params = analysis_params or {}
        
        # Calculate file content hash for more robust cache invalidation
        file_hash = self._calculate_file_hash(audio_file_path)
        
        # Generate analysis file path based on audio file path and content hash
        analysis_path = self._get_analysis_path_for_audio(audio_file_path, file_hash, self.analysis_params)
        self.current_analysis_path = analysis_path
        
        # Check if analysis already exists and is valid
        if not force_reanalysis and os.path.exists(analysis_path):
            try:
                # Load the cache file
                with open(analysis_path, 'r') as f:
                    cache_data = json.load(f)
                
                # Validate cache metadata
                cache_valid = self._validate_cache(cache_data, audio_file_path, file_hash)
                
                if cache_valid:
                    self.logger.info(f"Using valid cached analysis from {analysis_path}")
                    analysis_data = cache_data.get("analysis_data", {})
                    self.current_analysis_data = analysis_data
                    return analysis_data
                else:
                    self.logger.info("Cache invalid or outdated, will reanalyze")
            except json.JSONDecodeError as e:
                self.logger.warning(f"Corrupted cache file, will recreate: {e}")
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
        
        # Create cache data structure with metadata
        cache_data = {
            "metadata": {
                "audio_file_path": audio_file_path,
                "file_hash": file_hash,
                "analysis_timestamp": time.time(),
                "file_mtime": os.path.getmtime(audio_file_path),
                "analysis_params": self.analysis_params
            },
            "analysis_data": analysis_data
        }
        
        # Save to JSON
        try:
            with open(analysis_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
            self.logger.info(f"Analysis saved to {analysis_path}")
        except Exception as e:
            self.logger.error(f"Error saving analysis data: {e}")
            # Continue execution even if saving fails
        
        # Store the current analysis data
        self.current_analysis_data = analysis_data
        
        # Process lyrics if requested
        if analysis_params and analysis_params.get('request_lyrics', False):
            self.logger.info("Processing lyrics as requested")
            
            # Extract lyrics parameters
            conservative_alignment = analysis_params.get('conservative_lyrics_alignment', False)
            user_provided_lyrics = analysis_params.get('user_provided_lyrics')
            
            # Process lyrics
            lyrics_data = self.lyrics_processor.process_audio(
                audio_file_path,
                conservative_alignment=conservative_alignment,
                user_provided_lyrics=user_provided_lyrics
            )
            
            # Add lyrics data to analysis data
            analysis_data['lyrics_info'] = lyrics_data
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
    
    def _calculate_file_hash(self, file_path, block_size=65536):
        """
        Calculate a hash of the file content for more robust cache invalidation.
        
        Args:
            file_path (str): Path to the file
            block_size (int, optional): Size of blocks to read. Defaults to 65536.
            
        Returns:
            str: Hexadecimal hash of the file content
        """
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                buf = f.read(block_size)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = f.read(block_size)
            return hasher.hexdigest()
        except Exception as e:
            self.logger.warning(f"Error calculating file hash: {e}")
            # Fall back to using the file path and mtime
            fallback = f"{file_path}_{os.path.getmtime(file_path)}"
            return hashlib.md5(fallback.encode()).hexdigest()
    
    def _get_analysis_path_for_audio(self, audio_file_path, file_hash=None, analysis_params=None):
        """
        Generate a path for the analysis JSON based on the audio file path and content hash.
        
        Args:
            audio_file_path (str): Path to the audio file
            file_hash (str, optional): Hash of the file content. If None, only path is used.
            analysis_params (dict, optional): Analysis parameters to include in the cache key.
            
        Returns:
            Path: Path object for the analysis JSON file
        """
        # Create a hash of the audio path to use as filename
        if file_hash is None:
            # Fallback to just using the path if no hash is provided
            path_hash = hashlib.md5(str(audio_file_path).encode()).hexdigest()
        else:
            # Include file hash and analysis parameters in the cache key
            params_str = json.dumps(analysis_params or {}, sort_keys=True)
            key_components = f"{audio_file_path}_{file_hash}_{params_str}"
            path_hash = hashlib.md5(key_components.encode()).hexdigest()
            
        return self.analysis_cache_dir / f"{path_hash}_analysis.json"
    
    def _validate_cache(self, cache_data, audio_file_path, current_file_hash):
        """
        Validate if the cache is still valid for the given audio file.
        
        Args:
            cache_data (dict): The loaded cache data
            audio_file_path (str): Path to the audio file
            current_file_hash (str): Current hash of the file content
            
        Returns:
            bool: True if the cache is valid, False otherwise
        """
        if not isinstance(cache_data, dict) or "metadata" not in cache_data:
            return False
        
        metadata = cache_data.get("metadata", {})
        
        # Check if the file path matches
        if metadata.get("audio_file_path") != audio_file_path:
            return False
        
        # Check if the file hash matches
        if metadata.get("file_hash") != current_file_hash:
            return False
        
        # Check if the file modification time matches
        cached_mtime = metadata.get("file_mtime")
        current_mtime = os.path.getmtime(audio_file_path)
        
        if cached_mtime is None or current_mtime > cached_mtime:
            return False
        
        # Check if analysis parameters match
        cached_params = metadata.get("analysis_params", {})
        current_params = self.analysis_params or {}
        
        if cached_params != current_params:
            return False
        
        return True
    
    def clear_cache(self, audio_file_path=None):
        """
        Clear the analysis cache.
        
        Args:
            audio_file_path (str, optional): If provided, only clear the cache for this file.
                If None, clear the entire cache directory.
                
        Returns:
            int: Number of cache files removed
        """
        count = 0
        try:
            if audio_file_path:
                # Clear cache only for the specified file
                file_hash = self._calculate_file_hash(audio_file_path)
                cache_path = self._get_analysis_path_for_audio(audio_file_path, file_hash, self.analysis_params)
                
                if os.path.exists(cache_path):
                    os.remove(cache_path)
                    count = 1
                    self.logger.info(f"Cleared cache for {audio_file_path}")
            else:
                # Clear all cache files
                for cache_file in self.analysis_cache_dir.glob("*_analysis.json"):
                    os.remove(cache_file)
                    count += 1
                
                self.logger.info(f"Cleared {count} cache files")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
        
        return count
    
    def get_beats_in_range(self, start_time, end_time, beat_type="all"):
        """
        Get beats within a specified time range.
        
        Args:
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            beat_type (str, optional): Type of beats to retrieve.
                Can be "all" for all beats or "downbeat" for downbeats only.
                Defaults to "all".
                
        Returns:
            list: List of beat times (in seconds) within the specified range
            
        Raises:
            ValueError: If no analysis data is available
        """
        if not self.current_analysis_data:
            raise ValueError("No analysis data available. Call analyze_audio() first.")
        
        if beat_type == "downbeat":
            beats = self.current_analysis_data.get("downbeats", [])
        else:
            beats = self.current_analysis_data.get("beats", [])
        
        return [beat for beat in beats if start_time <= beat < end_time]
    
    def get_section_by_label(self, section_label):
        """
        Get a section by its label.
        
        Args:
            section_label (str): Label of the section to retrieve (e.g., "Chorus 1")
            
        Returns:
            dict: Section data if found, None otherwise
            
        Raises:
            ValueError: If no analysis data is available
        """
        if not self.current_analysis_data:
            raise ValueError("No analysis data available. Call analyze_audio() first.")
        
        for section in self.current_analysis_data.get("sections", []):
            if section["label"] == section_label:
                return section
        
        return None
    
    def get_feature_timeseries(self, feature_name):
        """
        Get the entire timeseries for a feature.
        
        Args:
            feature_name (str): Name of the feature to retrieve.
                Supported features: "energy", "onset_strength"
                
        Returns:
            dict: Dictionary with "times" and "values" keys containing the timeseries data
            
        Raises:
            ValueError: If no analysis data is available or the feature is unknown
        """
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
    
    def get_cache_info(self, audio_file_path=None):
        """
        Get information about the cache.
        
        Args:
            audio_file_path (str, optional): If provided, get info only for this file.
                If None, get info for all cached files.
                
        Returns:
            dict: Dictionary with cache information
        """
        cache_info = {
            "cache_directory": str(self.analysis_cache_dir),
            "cache_files": []
        }
        
        try:
            if audio_file_path:
                # Get info for specific file
                file_hash = self._calculate_file_hash(audio_file_path)
                cache_path = self._get_analysis_path_for_audio(audio_file_path, file_hash, self.analysis_params)
                
                if os.path.exists(cache_path):
                    try:
                        with open(cache_path, 'r') as f:
                            cache_data = json.load(f)
                        
                        metadata = cache_data.get("metadata", {})
                        cache_info["cache_files"].append({
                            "path": str(cache_path),
                            "size": os.path.getsize(cache_path),
                            "created": os.path.getctime(cache_path),
                            "audio_file": metadata.get("audio_file_path", "Unknown"),
                            "analysis_timestamp": metadata.get("analysis_timestamp", 0)
                        })
                    except Exception as e:
                        self.logger.warning(f"Error reading cache file {cache_path}: {e}")
            else:
                # Get info for all cache files
                for cache_file in self.analysis_cache_dir.glob("*_analysis.json"):
                    try:
                        with open(cache_file, 'r') as f:
                            cache_data = json.load(f)
                        
                        metadata = cache_data.get("metadata", {})
                        cache_info["cache_files"].append({
                            "path": str(cache_file),
                            "size": os.path.getsize(cache_file),
                            "created": os.path.getctime(cache_file),
                            "audio_file": metadata.get("audio_file_path", "Unknown"),
                            "analysis_timestamp": metadata.get("analysis_timestamp", 0)
                        })
                    except Exception as e:
                        self.logger.warning(f"Error reading cache file {cache_file}: {e}")
        except Exception as e:
            self.logger.error(f"Error getting cache info: {e}")
        
        return cache_info


class LyricsProcessor:
    """
    Processor for lyrics identification, retrieval, and alignment with audio.
    
    This class provides methods to identify songs, fetch lyrics, and align them
    with audio files. It uses external services like ACRCloud for song identification,
    Genius for lyrics retrieval, and can perform word-level alignment.
    """
    
    def __init__(self, api_keys_path=None):
        """
        Initialize the lyrics processor.
        
        Args:
            api_keys_path (str, optional): Path to the API keys JSON file.
                If not provided, defaults to standard locations.
        """
        self.logger = logging.getLogger("LyricsProcessor")
        self.current_lyrics_data = None
        self._load_api_keys(api_keys_path)
    
    def _load_api_keys(self, api_keys_path=None):
        """
        Load API keys from config file.
        
        Args:
            api_keys_path (str, optional): Path to the API keys JSON file.
                If not provided, tries standard locations.
        """
        # Define the path to the API keys file
        if api_keys_path:
            api_keys_path = api_keys_path
        else:
            # Try standard locations
            standard_paths = [
                os.path.expanduser("~/.ltx_sequence_maker/api_keys.json"),
                os.path.expanduser("~/.config/ltx_sequence_maker/api_keys.json")
            ]
            
            for path in standard_paths:
                if os.path.exists(path):
                    api_keys_path = path
                    break
            else:
                # Default to first path if none exist
                api_keys_path = standard_paths[0]
        
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
                self.logger.warning("Lyrics functionality will be limited without API keys")
        else:
            self.logger.warning(f"API keys file not found at {api_keys_path}")
            self.logger.warning("Lyrics functionality will be limited without API keys")
    
    def _identify_song(self, audio_path: str) -> Optional[Dict]:
        """
        Identify song using ACRCloud.
        
        Args:
            audio_path (str): Path to the audio file.
            
        Returns:
            Optional[Dict]: Dictionary with song info or None if identification failed.
        """
        # Check if we have the required API keys
        if not self.acr_access_key or not self.acr_secret_key or not self.acr_host:
            self.logger.warning("Missing ACRCloud API keys, cannot identify song")
            return None
            
        try:
            import base64
            import hmac
            import time
            from pathlib import Path
            
            # Log the audio path for debugging
            self.logger.info(f"Attempting to identify song from file: {audio_path}")
            
            # Check if file exists
            if not os.path.exists(audio_path):
                self.logger.error(f"File does not exist: {audio_path}")
                return None
            
            # Read audio file
            try:
                with open(audio_path, 'rb') as f:
                    sample_bytes = f.read(10 * 1024 * 1024)  # Read up to 10MB
                    self.logger.info(f"Successfully read {len(sample_bytes)} bytes from file")
            except Exception as e:
                self.logger.error(f"Error reading file: {e}")
                return None
            
            # Prepare request
            http_method = "POST"
            http_uri = "/v1/identify"
            data_type = "audio"
            signature_version = "1"
            timestamp = str(int(time.time()))
            
            # Generate signature
            string_to_sign = http_method + "\n" + http_uri + "\n" + self.acr_access_key + "\n" + data_type + "\n" + signature_version + "\n" + timestamp
            sign = base64.b64encode(hmac.new(self.acr_secret_key.encode('utf-8'), string_to_sign.encode('utf-8'), digestmod=hashlib.sha1).digest()).decode('utf-8')
            
            # Prepare request data
            files = {
                'sample': (os.path.basename(audio_path), sample_bytes),
            }
            
            data = {
                'access_key': self.acr_access_key,
                'data_type': data_type,
                'signature': sign,
                'signature_version': signature_version,
                'timestamp': timestamp,
                'sample_bytes': len(sample_bytes)
            }
            
            # Send request
            url = f"https://{self.acr_host}{http_uri}"
            self.logger.info(f"Sending request to ACRCloud: {url}")
            response = requests.post(url, files=files, data=data)
            
            # Check if request was successful
            if response.status_code != 200:
                self.logger.error(f"ACRCloud API error: {response.status_code}")
                return None
                
            # Parse result
            result_dict = response.json()
            self.logger.info(f"ACRCloud response status: {result_dict.get('status', {}).get('code')}")
            
            # Check if we got a match
            if result_dict.get('status', {}).get('code') == 0:
                # Get the first music result
                music = result_dict.get('metadata', {}).get('music', [])
                
                if music:
                    song = music[0]
                    song_title = song.get('title', '')
                    
                    # Get artist name
                    artists = song.get('artists', [])
                    artist_name = artists[0].get('name', '') if artists else ''
                    
                    self.logger.info(f"Song identified: {song_title} by {artist_name}")
                    return {"title": song_title, "artist": artist_name}
            
            self.logger.warning("No song match found in ACRCloud response")
            return None
        
        except Exception as e:
            self.logger.error(f"Error identifying song: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_lyrics(self, song_name: str, artist_name: str) -> Optional[str]:
        """
        Get lyrics using Genius API.
        
        Args:
            song_name (str): Name of the song.
            artist_name (str): Name of the artist.
            
        Returns:
            Optional[str]: Lyrics text or None if retrieval failed.
        """
        # Check if we have the required API key
        if not self.genius_api_key:
            self.logger.warning("Missing Genius API key, cannot fetch lyrics")
            return None
            
        try:
            # Initialize Genius client with appropriate parameters
            genius = lyricsgenius.Genius(
                self.genius_api_key,
                verbose=False,  # Don't print status messages to stdout
                remove_section_headers=True,  # Remove section headers (e.g. [Chorus]) from lyrics
                skip_non_songs=True,  # Skip non-songs (e.g. track lists)
                excluded_terms=["(Remix)", "(Live)"]  # Exclude remixes and live versions
            )
            
            # Search for the song
            self.logger.info(f"Searching for lyrics: '{song_name}' by '{artist_name}'")
            song = genius.search_song(song_name, artist_name)
            
            # Check if song was found and has lyrics
            if song and song.lyrics:
                self.logger.info(f"Lyrics found for '{song_name}' by '{artist_name}'")
                return song.lyrics
            else:
                self.logger.warning(f"Lyrics not found for '{song_name}' by '{artist_name}' on Genius")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching lyrics: {e}")
            return None
    
    def _align_lyrics(self, audio_path: str, lyrics_text: str, conservative: bool = False) -> List[Dict]:
        """
        Align lyrics with audio using Gentle forced aligner.
        
        Args:
            audio_path (str): Path to the audio file.
            lyrics_text (str): Lyrics text.
            conservative (bool): Whether to use conservative alignment.
                When True, alignment will stay as close as possible to the
                provided lyrics and avoid skipping words.
            
        Returns:
            List[Dict]: List of word timestamps or empty list if alignment failed.
        """
        # Default Gentle server URL - could be made configurable in the future
        gentle_url = "http://localhost:8765/transcriptions?async=false"
        
        # Add conservative parameter if requested
        if conservative:
            gentle_url += "&conservative=true"
            
        self.logger.info(f"Aligning lyrics with audio using Gentle: {audio_path}")
        
        try:
            # Prepare the multipart form data with audio file and transcript
            files = {
                'audio': (os.path.basename(audio_path), open(audio_path, 'rb')),
                'transcript': ('lyrics.txt', lyrics_text.encode('utf-8'))
            }
            
            # Make the request to Gentle server
            self.logger.info(f"Sending request to Gentle server: {gentle_url}")
            response = requests.post(gentle_url, files=files, timeout=120)  # Longer timeout as alignment can take time
            
            # Check if request was successful
            if response.status_code != 200:
                self.logger.error(f"Gentle server error: {response.status_code}")
                return []
            
            # Parse the response
            try:
                result = response.json()
            except json.JSONDecodeError:
                self.logger.error("Failed to parse Gentle response as JSON")
                return []
            
            # Extract word timestamps
            word_timestamps = []
            words = result.get('words', [])
            
            if not words:
                self.logger.warning("No words found in Gentle response")
                return []
            
            # Process each word in the alignment result
            for word_data in words:
                # Only include words that were successfully aligned
                if word_data.get('case') == 'success':
                    word = word_data.get('alignedWord')
                    start = word_data.get('start')
                    end = word_data.get('end')
                    
                    if word and start is not None and end is not None:
                        word_timestamps.append({
                            "word": word,
                            "start": start,
                            "end": end
                        })
            
            self.logger.info(f"Successfully aligned {len(word_timestamps)} words")
            return word_timestamps
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error connecting to Gentle server: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error during lyrics alignment: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            # Ensure files are closed
            if 'files' in locals():
                for f in files.values():
                    if hasattr(f[1], 'close') and not f[1].closed:
                        f[1].close()
    
    def process_audio(self, audio_path: str, conservative_alignment: bool = False, user_provided_lyrics: Optional[str] = None) -> Dict:
        """
        Process audio to extract and align lyrics.
        
        This method orchestrates the song identification, lyrics fetching, and alignment process.
        
        Args:
            audio_path (str): Path to the audio file.
            conservative_alignment (bool): Whether to use conservative alignment.
            user_provided_lyrics (Optional[str]): User-provided lyrics text, if available.
            
        Returns:
            Dict: Dictionary with lyrics information including:
                - song_title: Identified song title or None
                - artist_name: Identified artist name or None
                - raw_lyrics: Lyrics text or None
                - word_timestamps: List of aligned word timestamps or empty list
        """
        self.logger.info(f"Processing audio for lyrics: {audio_path}")
        
        # Initialize result structure
        result = {
            "song_title": None,
            "artist_name": None,
            "raw_lyrics": None,
            "word_timestamps": []
        }
        
        # Store as current lyrics data
        self.current_lyrics_data = result
        
        # If user provided lyrics, use them directly for alignment
        if user_provided_lyrics:
            self.logger.info("Using user-provided lyrics")
            result["raw_lyrics"] = user_provided_lyrics
            
            # Align the lyrics
            word_timestamps = self._align_lyrics(audio_path, user_provided_lyrics, conservative_alignment)
            result["word_timestamps"] = word_timestamps
            
            return result
        
        # Otherwise, try to identify the song
        song_info = self._identify_song(audio_path)
        
        if song_info:
            # Extract song and artist name
            result["song_title"] = song_info.get("title")
            result["artist_name"] = song_info.get("artist")
            
            # Fetch lyrics
            if result["song_title"] and result["artist_name"]:
                lyrics_text = self._get_lyrics(result["song_title"], result["artist_name"])
                result["raw_lyrics"] = lyrics_text
                
                # Align lyrics if available
                if lyrics_text:
                    word_timestamps = self._align_lyrics(audio_path, lyrics_text, conservative_alignment)
                    result["word_timestamps"] = word_timestamps
        
        return result
    
    def get_words_in_range(self, start_time, end_time):
        """
        Get words within a time range.
        
        Args:
            start_time (float): Start time in seconds.
            end_time (float): End time in seconds.
            
        Returns:
            list: List of word timestamps within the specified range.
            
        Raises:
            ValueError: If no lyrics data is available.
        """
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
