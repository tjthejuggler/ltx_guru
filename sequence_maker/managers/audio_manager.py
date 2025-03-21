"""
Sequence Maker - Audio Manager

This module defines the AudioManager class, which handles audio playback and analysis.
"""

import os
import logging
import threading
import time
import tempfile
import numpy as np
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

try:
    import librosa
    import soundfile as sf
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


class AudioManager(QObject):
    """
    Manages audio playback and analysis.
    
    Signals:
        audio_loaded: Emitted when audio is loaded.
        audio_started: Emitted when audio playback starts.
        audio_paused: Emitted when audio playback is paused.
        audio_stopped: Emitted when audio playback stops.
        position_changed: Emitted when the playback position changes.
        analysis_completed: Emitted when audio analysis is completed.
    """
    
    # Signals
    audio_loaded = pyqtSignal(str, float)  # file_path, duration
    audio_started = pyqtSignal()
    audio_paused = pyqtSignal()
    audio_stopped = pyqtSignal()
    position_changed = pyqtSignal(float)  # position
    analysis_completed = pyqtSignal(dict)  # analysis_data
    
    def __init__(self, app):
        """
        Initialize the audio manager.
        
        Args:
            app: The main application instance.
        """
        super().__init__()
        
        self.logger = logging.getLogger("SequenceMaker.AudioManager")
        self.app = app
        
        # Check if audio libraries are available
        if not AUDIO_AVAILABLE:
            self.logger.warning("Audio libraries not available. Audio functionality will be limited.")
        
        # Audio data
        self.audio_file = None
        self.audio_data = None
        self.sample_rate = None
        self.duration = 0
        
        # Audio analysis
        self.waveform = None
        self.beats = None
        self.beat_times = None
        self.tempo = None
        self.spectrum = None
        
        # Playback state
        self.playing = False
        self.paused = False
        self.position = 0.0
        self.volume = app.config.get("audio", "volume")
        
        # Playback thread
        self.playback_thread = None
        self.playback_stop_event = threading.Event()
        
        # PyAudio
        self.pyaudio = None
        self.stream = None
        
        # Initialize PyAudio if available
        if AUDIO_AVAILABLE:
            try:
                self.pyaudio = pyaudio.PyAudio()
            except Exception as e:
                self.logger.error(f"Error initializing PyAudio: {e}")
                self.pyaudio = None
        
        # Connect position_changed signal to timeline_manager's set_position method
        self.position_changed.connect(self._update_timeline_position)
    
    def load_audio(self, file_path):
        """
        Load an audio file.
        
        Args:
            file_path (str): Path to the audio file.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not AUDIO_AVAILABLE:
            self.logger.warning("Cannot load audio: Audio libraries not available")
            return False
        
        self.logger.info(f"Loading audio file: {file_path}")
        
        try:
            # Stop any current playback
            self.stop()
            
            # Load audio file
            self.audio_data, self.sample_rate = librosa.load(file_path, sr=None)
            self.audio_file = file_path
            self.duration = librosa.get_duration(y=self.audio_data, sr=self.sample_rate)
            
            # Reset position
            self.position = 0.0
            
            # Add to recent audio files
            self.app.config.add_recent_audio(file_path)
            
            # Ensure position change is properly propagated
            self.position_changed.emit(self.position)
            self._update_timeline_position(self.position)
            
            # Emit signal
            self.audio_loaded.emit(file_path, self.duration)
            
            # Start analysis in a separate thread
            threading.Thread(target=self._analyze_audio, daemon=True).start()
            
            return True
        except Exception as e:
            self.logger.error(f"Error loading audio file: {e}")
            return False
    
    def load_audio_from_project(self, project):
        """
        Load audio data from a project.
        
        Args:
            project: The project containing audio data.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not AUDIO_AVAILABLE:
            self.logger.warning("Cannot load audio: Audio libraries not available")
            return False
        
        if not project.audio_data:
            self.logger.info("No audio data in project")
            return False
        
        self.logger.info(f"Loading audio from project: {project.name}")
        
        try:
            # Stop any current playback
            self.stop()
            
            # Create a temporary file to write the audio data to
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_path = temp_file.name
                temp_file.write(project.audio_data)
            
            # Load the audio data from the temporary file
            self.audio_data, self.sample_rate = librosa.load(temp_path, sr=None)
            self.audio_file = project.audio_file
            self.duration = librosa.get_duration(y=self.audio_data, sr=self.sample_rate)
            
            # Remove the temporary file
            try:
                os.unlink(temp_path)
            except Exception as e:
                self.logger.warning(f"Could not remove temporary file {temp_path}: {e}")
            
            # Reset position
            self.position = 0.0
            
            # Ensure position change is properly propagated
            self.position_changed.emit(self.position)
            self._update_timeline_position(self.position)
            
            # Emit signal
            self.audio_loaded.emit(project.audio_file or "Embedded Audio", self.duration)
            
            # Start analysis in a separate thread
            threading.Thread(target=self._analyze_audio, daemon=True).start()
            
            return True
        except Exception as e:
            self.logger.error(f"Error loading audio from project: {e}")
            return False
    
    def _analyze_audio(self):
        """Analyze the loaded audio file."""
        if not AUDIO_AVAILABLE or self.audio_data is None:
            return
        
        self.logger.info("Analyzing audio...")
        
        try:
            # Compute waveform
            self.waveform = self.audio_data
            
            # Compute beats
            tempo, beat_frames = librosa.beat.beat_track(y=self.audio_data, sr=self.sample_rate)
            self.tempo = tempo
            self.beat_times = librosa.frames_to_time(beat_frames, sr=self.sample_rate)
            
            # Compute beat strength
            onset_env = librosa.onset.onset_strength(y=self.audio_data, sr=self.sample_rate)
            self.beats = onset_env
            
            # Compute spectrum
            self.spectrum = np.abs(librosa.stft(self.audio_data))
            
            # Create analysis data
            analysis_data = {
                "waveform": self.waveform,
                "beats": self.beats,
                "beat_times": self.beat_times,
                "tempo": self.tempo,
                "spectrum": self.spectrum
            }
            
            self.logger.info("Audio analysis completed")
            
            # Emit signal
            self.analysis_completed.emit(analysis_data)
        except Exception as e:
            self.logger.error(f"Error analyzing audio: {e}")
    
    def play(self):
        """
        Start or resume audio playback.
        
        Returns:
            bool: True if playback started, False otherwise.
        """
        # If already playing, do nothing
        if self.playing and not self.paused:
            return True
        
        # If paused, resume
        if self.paused:
            self.paused = False
            self.logger.info("Resuming playback")
            
            # Update start time to account for the time spent paused
            if hasattr(self, '_pause_time'):
                pause_duration = time.time() - self._pause_time
                if hasattr(self, '_start_time'):
                    self._start_time += pause_duration
            
            self.audio_started.emit()
            return True
        
        self.logger.info("Starting playback")
        
        # Reset stop event
        self.playback_stop_event.clear()
        
        # Set playing state
        self.playing = True
        self.paused = False
        
        # Record start time for position tracking
        self._start_time = time.time()
        
        if AUDIO_AVAILABLE and self.audio_data is not None:
            # Start audio playback thread
            self.playback_thread = threading.Thread(
                target=self._playback_worker,
                daemon=True
            )
            self.playback_thread.start()
        else:
            # Start position update thread even without audio
            self.playback_thread = threading.Thread(
                target=self._position_update_worker,
                daemon=True
            )
            self.playback_thread.start()
        
        # Emit signals
        self.audio_started.emit()
        
        # Emit an immediate position update to ensure UI reflects current position
        self.position_changed.emit(self.position)
        
        return True
    
    def pause(self):
        """
        Pause audio playback.
        
        Returns:
            bool: True if playback paused, False otherwise.
        """
        if not self.playing or self.paused:
            return False
        
        self.logger.info("Pausing audio playback")
        
        # Set paused state
        self.paused = True
        
        # Record pause time for resuming later
        self._pause_time = time.time()
        
        # Emit signal
        self.audio_paused.emit()
        
        return True
    
    def stop(self):
        """
        Stop audio playback.
        
        Returns:
            bool: True if playback stopped, False otherwise.
        """
        if not self.playing:
            self.logger.debug("stop() called but not playing, returning False")
            return False
        
        self.logger.info("Stopping audio playback")
        
        # Set stop event
        self.playback_stop_event.set()
        self.logger.debug("Set playback_stop_event")
        
        # Wait for thread to finish
        if self.playback_thread and self.playback_thread.is_alive():
            self.logger.debug("Waiting for playback thread to finish")
            self.playback_thread.join(timeout=1.0)
        
        # Close stream if open
        if self.stream:
            try:
                self.logger.debug("Closing audio stream")
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                self.logger.error(f"Error closing audio stream: {e}")
            finally:
                self.stream = None
        
        # Reset state
        self.playing = False
        self.paused = False
        self.position = 0.0
        self.logger.debug("Reset state: playing=False, paused=False, position=0.0")
        
        # Directly set the timeline manager position to 0.0
        self.logger.debug("Directly setting timeline manager position to 0.0")
        self.app.timeline_manager.set_position(0.0)
        
        # Emit signals - ensure position change is properly propagated
        self.logger.debug("Emitting position_changed signal with position=0.0")
        self.position_changed.emit(self.position)
        
        # Force an update to the timeline manager position
        self.logger.debug("Forcing update to timeline manager position")
        self._update_timeline_position(self.position)
        
        # Emit audio stopped signal
        self.logger.debug("Emitting audio_stopped signal")
        self.audio_stopped.emit()
        
        self.logger.debug("stop() completed successfully")
        return True
    
    def seek(self, position):
        """
        Seek to a specific position in the audio.
        
        Args:
            position (float): Position in seconds.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if self.audio_data is None:
            return False
        
        # Clamp position to valid range
        position = max(0, min(position, self.duration))
        
        self.logger.info(f"Seeking to position: {position:.2f}s")
        
        # Update position
        self.position = position
        
        # Emit signal - ensure position change is properly propagated
        self.position_changed.emit(position)
        
        # Force an update to the timeline manager position
        self._update_timeline_position(position)
        
        return True
    
    def set_volume(self, volume):
        """
        Set the playback volume.
        
        Args:
            volume (float): Volume level (0.0 to 1.0).
        
        Returns:
            bool: True if successful, False otherwise.
        """
        # Clamp volume to valid range
        volume = max(0.0, min(volume, 1.0))
        
        self.logger.info(f"Setting volume: {volume:.2f}")
        
        # Update volume
        self.volume = volume
        
        # Save to config
        self.app.config.set("audio", "volume", volume)
        
        return True
    
    def get_waveform_at_time(self, time, width, height):
        """
        Get a section of the waveform around a specific time.
        
        Args:
            time (float): Time in seconds.
            width (int): Width of the section in samples.
            height (int): Height of the waveform visualization.
        
        Returns:
            numpy.ndarray: Waveform data, or None if no audio is loaded.
        """
        if self.waveform is None:
            return None
        
        # Convert time to sample index
        center_sample = int(time * self.sample_rate)
        
        # Calculate start and end samples
        half_width = width // 2
        start_sample = max(0, center_sample - half_width)
        end_sample = min(len(self.waveform), center_sample + half_width)
        
        # Extract waveform section
        if start_sample < end_sample:
            waveform_section = self.waveform[start_sample:end_sample]
            
            # Normalize and scale to height
            if len(waveform_section) > 0:
                max_val = max(abs(waveform_section.min()), abs(waveform_section.max()))
                if max_val > 0:
                    waveform_section = waveform_section * (height / 2) / max_val
                
                return waveform_section
        
        return None
    
    def get_spectrum_at_time(self, time, width, height):
        """
        Get a section of the spectrum around a specific time.
        
        Args:
            time (float): Time in seconds.
            width (int): Width of the section in frames.
            height (int): Height of the spectrum visualization.
        
        Returns:
            numpy.ndarray: Spectrum data, or None if no audio is loaded.
        """
        if self.spectrum is None:
            return None
        
        # Convert time to frame index
        frame_rate = self.spectrum.shape[1] / self.duration
        center_frame = int(time * frame_rate)
        
        # Calculate start and end frames
        half_width = width // 2
        start_frame = max(0, center_frame - half_width)
        end_frame = min(self.spectrum.shape[1], center_frame + half_width)
        
        # Extract spectrum section
        if start_frame < end_frame:
            spectrum_section = self.spectrum[:, start_frame:end_frame]
            
            # Normalize and scale to height
            if spectrum_section.size > 0:
                max_val = spectrum_section.max()
                if max_val > 0:
                    spectrum_section = spectrum_section * height / max_val
                
                return spectrum_section
        
        return None
    
    def is_beat_at_time(self, time, tolerance=0.05):
        """
        Check if there is a beat at a specific time.
        
        Args:
            time (float): Time in seconds.
            tolerance (float, optional): Time tolerance in seconds. Defaults to 0.05.
        
        Returns:
            bool: True if there is a beat at the specified time, False otherwise.
        """
        if self.beat_times is None:
            return False
        
        # Check if any beat time is within tolerance of the specified time
        return any(abs(beat_time - time) <= tolerance for beat_time in self.beat_times)
    
    def get_beats_in_range(self, start_time, end_time):
        """
        Get all beat times within a time range.
        
        Args:
            start_time (float): Start time in seconds.
            end_time (float): End time in seconds.
        
        Returns:
            list: List of beat times, or an empty list if no beats are found.
        """
        if self.beat_times is None:
            return []
        
        return [
            beat_time for beat_time in self.beat_times
            if start_time <= beat_time < end_time
        ]
    
    def _position_update_worker(self):
        """Position update worker thread function when no audio is loaded."""
        try:
            # Calculate start position
            start_position = self.position
            
            # Get project total duration
            total_duration = 60  # Default to 60 seconds
            if self.app.project_manager.current_project:
                total_duration = self.app.project_manager.current_project.total_duration
            
            # Use the start time set in the play method
            if not hasattr(self, '_start_time'):
                self._start_time = time.time()
            
            # Update position until stopped or reached the end
            while not self.playback_stop_event.is_set() and self.position < total_duration:
                # Only update position if not paused
                if not self.paused:
                    # Calculate current position based on elapsed time
                    elapsed = time.time() - self._start_time
                    self.position = start_position + elapsed
                    
                    # Emit position signal
                    self.position_changed.emit(self.position)
                
                # Sleep to reduce CPU usage - reduced from 0.05 to 0.016 (~60 FPS)
                time.sleep(0.016)
            
            # Reset state if not stopped manually
            if not self.playback_stop_event.is_set():
                self.playing = False
                self.paused = False
                self.position = 0.0
                
                # Emit signals - ensure position change is properly propagated
                self.position_changed.emit(self.position)
                
                # Force an update to the timeline manager position
                self._update_timeline_position(self.position)
                
                # Emit audio stopped signal
                self.audio_stopped.emit()
        
        except Exception as e:
            self.logger.error(f"Error in position update worker: {e}")
            
            # Reset state
            self.playing = False
            self.paused = False
    
    def _playback_worker(self):
        """Audio playback worker thread function."""
        if not AUDIO_AVAILABLE or self.audio_data is None or self.pyaudio is None:
            self.logger.warning("Cannot start playback worker: Audio not available")
            self.playing = False
            return
        
        try:
            # Calculate start position in samples
            start_sample = int(self.position * self.sample_rate)
            
            # Create audio stream
            self.stream = self.pyaudio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=1024,
                stream_callback=self._audio_callback
            )
            
            # Start stream
            self.stream.start_stream()
            
            # Set current sample
            self._current_sample = start_sample
            
            # Wait until stream is finished or stopped
            while self.stream.is_active() and not self.playback_stop_event.is_set():
                # Only update position if not paused
                if not self.paused:
                    # Update position
                    self.position = self._current_sample / self.sample_rate
                    
                    # Emit position signal (throttled to reduce CPU usage)
                    self.position_changed.emit(self.position)
                    
                    # Check if we've reached the end
                    if self._current_sample >= len(self.audio_data):
                        self.logger.info("Reached end of audio")
                        break
                
                # Sleep to reduce CPU usage - reduced from 0.05 to 0.016 (~60 FPS)
                time.sleep(0.016)
            
            # Close stream
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
            # Reset state if not stopped manually
            if not self.playback_stop_event.is_set():
                self.playing = False
                self.paused = False
                self.position = 0.0
                
                # Emit signals - ensure position change is properly propagated
                self.position_changed.emit(self.position)
                
                # Force an update to the timeline manager position
                self._update_timeline_position(self.position)
                
                # Emit audio stopped signal
                self.audio_stopped.emit()
        
        except Exception as e:
            self.logger.error(f"Error in playback worker: {e}")
            
            # Reset state
            self.playing = False
            self.paused = False
            
            # Close stream if open
            if self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except:
                    pass
                finally:
                    self.stream = None
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """
        PyAudio callback function for streaming audio data.
        
        Args:
            in_data: Input audio data (not used).
            frame_count: Number of frames to process.
            time_info: Time information (not used).
            status: Status flag (not used).
        
        Returns:
            tuple: (audio_data, status_flag)
        """
        if self.paused or self.playback_stop_event.is_set():
            # Return silence when paused
            return (np.zeros(frame_count, dtype=np.float32), pyaudio.paContinue)
        
        # Get current position
        current_sample = self._current_sample
        
        # Check if we've reached the end
        if current_sample >= len(self.audio_data):
            return (np.zeros(frame_count, dtype=np.float32), pyaudio.paComplete)
        
        # Calculate end position
        end_sample = min(current_sample + frame_count, len(self.audio_data))
        
        # Get audio data
        data = self.audio_data[current_sample:end_sample]
        
        # Apply volume
        data = data * self.volume
        
        # Pad with zeros if needed
        if len(data) < frame_count:
            data = np.pad(data, (0, frame_count - len(data)), 'constant')
        
        # Update current sample
        self._current_sample = end_sample
        
        # Convert to float32
        data = data.astype(np.float32)
        
        return (data, pyaudio.paContinue)
    
    def _update_timeline_position(self, position):
        """
        Update the timeline position when the audio position changes.
        
        Args:
            position (float): New position in seconds.
        """
        # Log current positions
        self.logger.debug(f"_update_timeline_position called with position={position:.2f}s, current timeline position={self.app.timeline_manager.position:.2f}s")
        
        # Always update if:
        # - position is 0.0 (stop button was pressed)
        # - playback just started (self.playing is True and not paused)
        # - positions are different beyond threshold
        if (position == 0.0 or
            (self.playing and not self.paused) or
            abs(self.app.timeline_manager.position - position) > 0.005):  # Reduced from 10ms to 5ms threshold
            
            # Only log occasionally to reduce overhead
            if position % 1.0 < 0.02:  # Log approximately once per second
                self.logger.debug(f"Updating timeline position to {position:.2f}s")
            self.app.timeline_manager.set_position(position)
        else:
            # Only log occasionally
            if position % 1.0 < 0.02:
                self.logger.debug(f"Positions are similar, not updating timeline position")
    
    def __del__(self):
        """Clean up resources when the object is destroyed."""
        # Stop playback
        self.stop()
        
        # Terminate PyAudio
        if self.pyaudio:
            self.pyaudio.terminate()