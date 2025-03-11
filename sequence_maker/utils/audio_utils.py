"""
Sequence Maker - Audio Utilities

This module provides utility functions for audio processing.
"""

import os
import logging
import numpy as np

try:
    import librosa
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False


logger = logging.getLogger("SequenceMaker.AudioUtils")


def load_audio(file_path):
    """
    Load an audio file.
    
    Args:
        file_path (str): Path to the audio file.
    
    Returns:
        tuple: (audio_data, sample_rate) or (None, None) if loading failed.
    """
    if not AUDIO_AVAILABLE:
        logger.warning("Cannot load audio: Audio libraries not available")
        return None, None
    
    try:
        # Load audio file
        audio_data, sample_rate = librosa.load(file_path, sr=None)
        
        logger.info(f"Loaded audio file: {file_path} (sr={sample_rate}, length={len(audio_data)})")
        return audio_data, sample_rate
    
    except Exception as e:
        logger.error(f"Error loading audio file: {e}")
        return None, None


def get_audio_duration(file_path):
    """
    Get the duration of an audio file.
    
    Args:
        file_path (str): Path to the audio file.
    
    Returns:
        float: Duration in seconds, or 0 if loading failed.
    """
    if not AUDIO_AVAILABLE:
        logger.warning("Cannot get audio duration: Audio libraries not available")
        return 0
    
    try:
        # Get duration
        duration = librosa.get_duration(filename=file_path)
        
        logger.info(f"Audio duration: {duration:.2f} seconds")
        return duration
    
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
        return 0


def detect_beats(audio_data, sample_rate, threshold=0.5):
    """
    Detect beats in audio data.
    
    Args:
        audio_data (numpy.ndarray): Audio data.
        sample_rate (int): Sample rate.
        threshold (float, optional): Beat detection threshold. Defaults to 0.5.
    
    Returns:
        tuple: (beat_times, tempo) or (None, None) if detection failed.
    """
    if not AUDIO_AVAILABLE:
        logger.warning("Cannot detect beats: Audio libraries not available")
        return None, None
    
    try:
        # Compute onset strength
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=sample_rate)
        
        # Detect tempo and beats
        tempo, beat_frames = librosa.beat.beat_track(
            onset_envelope=onset_env,
            sr=sample_rate,
            tightness=threshold
        )
        
        # Convert frames to time
        beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate)
        
        logger.info(f"Detected {len(beat_times)} beats, tempo: {tempo:.2f} BPM")
        return beat_times, tempo
    
    except Exception as e:
        logger.error(f"Error detecting beats: {e}")
        return None, None


def compute_spectrum(audio_data, sample_rate):
    """
    Compute the spectrum of audio data.
    
    Args:
        audio_data (numpy.ndarray): Audio data.
        sample_rate (int): Sample rate.
    
    Returns:
        numpy.ndarray: Spectrum data, or None if computation failed.
    """
    if not AUDIO_AVAILABLE:
        logger.warning("Cannot compute spectrum: Audio libraries not available")
        return None
    
    try:
        # Compute short-time Fourier transform
        spectrum = np.abs(librosa.stft(audio_data))
        
        logger.info(f"Computed spectrum with shape: {spectrum.shape}")
        return spectrum
    
    except Exception as e:
        logger.error(f"Error computing spectrum: {e}")
        return None


def get_waveform_at_time(waveform, sample_rate, time, width, height):
    """
    Get a section of the waveform around a specific time.
    
    Args:
        waveform (numpy.ndarray): Waveform data.
        sample_rate (int): Sample rate.
        time (float): Time in seconds.
        width (int): Width of the section in samples.
        height (int): Height of the waveform visualization.
    
    Returns:
        numpy.ndarray: Waveform data, or None if extraction failed.
    """
    if waveform is None:
        return None
    
    try:
        # Convert time to sample index
        center_sample = int(time * sample_rate)
        
        # Calculate start and end samples
        half_width = width // 2
        start_sample = max(0, center_sample - half_width)
        end_sample = min(len(waveform), center_sample + half_width)
        
        # Extract waveform section
        if start_sample < end_sample:
            waveform_section = waveform[start_sample:end_sample]
            
            # Normalize and scale to height
            if len(waveform_section) > 0:
                max_val = max(abs(waveform_section.min()), abs(waveform_section.max()))
                if max_val > 0:
                    waveform_section = waveform_section * (height / 2) / max_val
                
                return waveform_section
        
        return None
    
    except Exception as e:
        logger.error(f"Error extracting waveform section: {e}")
        return None


def get_spectrum_at_time(spectrum, duration, time, width, height):
    """
    Get a section of the spectrum around a specific time.
    
    Args:
        spectrum (numpy.ndarray): Spectrum data.
        duration (float): Duration of the audio in seconds.
        time (float): Time in seconds.
        width (int): Width of the section in frames.
        height (int): Height of the spectrum visualization.
    
    Returns:
        numpy.ndarray: Spectrum data, or None if extraction failed.
    """
    if spectrum is None:
        return None
    
    try:
        # Convert time to frame index
        frame_rate = spectrum.shape[1] / duration
        center_frame = int(time * frame_rate)
        
        # Calculate start and end frames
        half_width = width // 2
        start_frame = max(0, center_frame - half_width)
        end_frame = min(spectrum.shape[1], center_frame + half_width)
        
        # Extract spectrum section
        if start_frame < end_frame:
            spectrum_section = spectrum[:, start_frame:end_frame]
            
            # Normalize and scale to height
            if spectrum_section.size > 0:
                max_val = spectrum_section.max()
                if max_val > 0:
                    spectrum_section = spectrum_section * height / max_val
                
                return spectrum_section
        
        return None
    
    except Exception as e:
        logger.error(f"Error extracting spectrum section: {e}")
        return None


def is_beat_at_time(beat_times, time, tolerance=0.05):
    """
    Check if there is a beat at a specific time.
    
    Args:
        beat_times (numpy.ndarray): Beat times in seconds.
        time (float): Time in seconds.
        tolerance (float, optional): Time tolerance in seconds. Defaults to 0.05.
    
    Returns:
        bool: True if there is a beat at the specified time, False otherwise.
    """
    if beat_times is None:
        return False
    
    try:
        # Check if any beat time is within tolerance of the specified time
        return any(abs(beat_time - time) <= tolerance for beat_time in beat_times)
    
    except Exception as e:
        logger.error(f"Error checking beat at time: {e}")
        return False


def get_beats_in_range(beat_times, start_time, end_time):
    """
    Get all beat times within a time range.
    
    Args:
        beat_times (numpy.ndarray): Beat times in seconds.
        start_time (float): Start time in seconds.
        end_time (float): End time in seconds.
    
    Returns:
        list: List of beat times, or an empty list if no beats are found.
    """
    if beat_times is None:
        return []
    
    try:
        return [
            beat_time for beat_time in beat_times
            if start_time <= beat_time < end_time
        ]
    
    except Exception as e:
        logger.error(f"Error getting beats in range: {e}")
        return []