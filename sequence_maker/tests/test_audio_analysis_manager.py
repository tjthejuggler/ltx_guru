"""
Sequence Maker - Tests for AudioAnalysisManager

This module contains tests for the AudioAnalysisManager class.
"""

import os
import json
import pytest
import tempfile
import numpy as np
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

# Import the AudioAnalysisManager class
from sequence_maker.managers.audio_analysis_manager import AudioAnalysisManager


# Use the fixture from conftest.py
@pytest.fixture
def audio_analysis_manager_with_temp_dir(audio_analysis_manager_fixture, monkeypatch):
    """
    Fixture that provides an AudioAnalysisManager instance with a temporary directory.
    
    Args:
        audio_analysis_manager_fixture: The audio_analysis_manager_fixture from conftest.py
        monkeypatch: The monkeypatch fixture from pytest
        
    Returns:
        An AudioAnalysisManager instance with a temporary directory
    """
    # Mock the analysis cache directory
    with tempfile.TemporaryDirectory() as temp_dir:
        monkeypatch.setattr(audio_analysis_manager_fixture, 'analysis_cache_dir', Path(temp_dir))
        yield audio_analysis_manager_fixture


def test_initialization(audio_analysis_manager_with_temp_dir):
    """
    Test that the AudioAnalysisManager initializes correctly.
    
    Args:
        audio_analysis_manager_with_temp_dir: The audio_analysis_manager_with_temp_dir fixture
    """
    manager = audio_analysis_manager_with_temp_dir
    
    # Check that the manager was initialized correctly
    assert manager.app is not None
    assert manager.logger is not None
    assert manager.analysis_cache_dir is not None
    assert manager.current_analysis_path is None


def test_get_analysis_path_for_audio(audio_analysis_manager_with_temp_dir):
    """
    Test that the _get_analysis_path_for_audio method works correctly.
    
    Args:
        audio_analysis_manager_with_temp_dir: The audio_analysis_manager_with_temp_dir fixture
    """
    manager = audio_analysis_manager_with_temp_dir
    
    # Test with a valid audio file path
    audio_path = "/path/to/test_audio.mp3"
    analysis_path = manager._get_analysis_path_for_audio(audio_path)
    
    # Check that the path is in the cache directory
    assert analysis_path.parent == manager.analysis_cache_dir
    
    # Check that the filename contains a hash of the audio path
    import hashlib
    path_hash = hashlib.md5(str(audio_path).encode()).hexdigest()
    assert path_hash in analysis_path.name
    
    # Test with None
    analysis_path = manager._get_analysis_path_for_audio(None)
    assert analysis_path.name == "unknown_audio_analysis.json"


@patch('librosa.load')
@patch('librosa.get_duration')
@patch('librosa.beat.beat_track')
@patch('librosa.frames_to_time')
@patch('librosa.feature.mfcc')
@patch('librosa.segment.agglomerative')
@patch('librosa.feature.rms')
@patch('librosa.onset.onset_strength')
@patch('librosa.feature.chroma_stft')
@patch('librosa.feature.spectral_contrast')
@patch('librosa.feature.spectral_centroid')
@patch('librosa.feature.spectral_rolloff')
@patch('librosa.feature.zero_crossing_rate')
@patch('librosa.times_like')
def test_extract_features(mock_times_like, mock_zcr, mock_rolloff, mock_centroid,
                          mock_contrast, mock_chroma, mock_onset, mock_rms,
                          mock_agglomerative, mock_mfcc, mock_frames_to_time,
                          mock_beat_track, mock_duration, mock_load,
                          audio_analysis_manager_with_temp_dir):
    """
    Test that the _extract_features method works correctly.
    
    Args:
        Various mocked librosa functions
        audio_analysis_manager_with_temp_dir: The audio_analysis_manager_with_temp_dir fixture
    """
    manager = audio_analysis_manager_with_temp_dir
    
    # Set up mocks
    mock_load.return_value = (np.zeros(1000), 44100)
    mock_duration.return_value = 60.0
    mock_beat_track.return_value = (120.0, np.array([100, 200, 300, 400]))
    mock_frames_to_time.side_effect = [
        np.array([1.0, 2.0, 3.0, 4.0]),  # beat_times
        np.array([0.0, 15.0, 30.0, 45.0, 60.0])  # segment_times
    ]
    mock_mfcc.return_value = np.zeros((20, 100))
    mock_agglomerative.return_value = np.array([0, 15, 30, 45, 60])
    mock_rms.return_value = [np.array([0.1, 0.2, 0.3])]
    mock_onset.return_value = np.array([0.5, 0.6, 0.7])
    mock_chroma.return_value = np.zeros((12, 3))
    mock_contrast.return_value = np.zeros((7, 3))
    mock_centroid.return_value = [np.array([0.1, 0.2, 0.3])]
    mock_rolloff.return_value = [np.array([0.4, 0.5, 0.6])]
    mock_zcr.return_value = [np.array([0.01, 0.02, 0.03])]
    mock_times_like.return_value = np.array([10.0, 20.0, 30.0])
    
    # Call the method
    audio_data = np.zeros(1000)
    sample_rate = 44100
    audio_file_path = "/path/to/test_audio.mp3"
    result = manager._extract_features(audio_data, sample_rate, audio_file_path)
    
    # Check the result
    assert isinstance(result, dict)
    assert result["song_title"] == "test_audio.mp3"
    assert result["duration_seconds"] == 60.0
    assert result["estimated_tempo"] == 120.0
    assert result["time_signature_guess"] == "4/4"
    assert len(result["beats"]) == 4
    assert len(result["downbeats"]) == 1  # Every 4th beat
    assert len(result["sections"]) == 4  # 5 segment times -> 4 sections
    assert "energy_timeseries" in result
    assert "onset_strength_timeseries" in result
    assert "chroma_features" in result
    assert "spectral_contrast" in result
    assert "spectral_centroid" in result
    assert "spectral_rolloff" in result
    assert "zero_crossing_rate" in result


@patch('os.path.exists')
@patch('os.path.getmtime')
@patch('builtins.open', new_callable=mock_open, read_data='{"test": "data"}')
def test_analyze_audio_with_existing_analysis(mock_open, mock_getmtime, mock_exists,
                                             audio_analysis_manager_with_temp_dir):
    """
    Test that the analyze_audio method uses existing analysis if available.
    
    Args:
        mock_open: Mock for the open function
        mock_getmtime: Mock for os.path.getmtime
        mock_exists: Mock for os.path.exists
        audio_analysis_manager_with_temp_dir: The audio_analysis_manager_with_temp_dir fixture
    """
    manager = audio_analysis_manager_with_temp_dir
    
    # Set up mocks
    mock_exists.return_value = True
    mock_getmtime.side_effect = [100, 200]  # audio_mtime, analysis_mtime
    
    # Call the method
    audio_file_path = "/path/to/test_audio.mp3"
    result = manager.analyze_audio(audio_file_path)
    
    # Check that the existing analysis was used
    assert result == {"test": "data"}
    mock_open.assert_called_once()


@patch('os.path.exists')
def test_load_analysis_with_no_file(mock_exists, audio_analysis_manager_with_temp_dir):
    """
    Test that the load_analysis method handles missing files correctly.
    
    Args:
        mock_exists: Mock for os.path.exists
        audio_analysis_manager_with_temp_dir: The audio_analysis_manager_with_temp_dir fixture
    """
    manager = audio_analysis_manager_with_temp_dir
    
    # Set up mocks
    mock_exists.return_value = False
    
    # Mock the analyze_audio method
    manager.analyze_audio = MagicMock(return_value=None)
    
    # Call the method
    result = manager.load_analysis()
    
    # Check that the result is None
    assert result is None


def test_get_section_by_label(audio_analysis_manager_with_temp_dir):
    """
    Test that the get_section_by_label method works correctly.
    
    Args:
        audio_analysis_manager_with_temp_dir: The audio_analysis_manager_with_temp_dir fixture
    """
    manager = audio_analysis_manager_with_temp_dir
    
    # Mock the load_analysis method
    test_data = {
        "sections": [
            {"label": "Intro", "start": 0.0, "end": 15.0},
            {"label": "Verse 1", "start": 15.0, "end": 30.0},
            {"label": "Chorus 1", "start": 30.0, "end": 45.0}
        ]
    }
    manager.load_analysis = MagicMock(return_value=test_data)
    
    # Test with an existing label
    result = manager.get_section_by_label("Verse 1")
    assert result == {"label": "Verse 1", "start": 15.0, "end": 30.0}
    
    # Test with a non-existent label
    result = manager.get_section_by_label("Bridge")
    assert result is None


def test_get_beats_in_range(audio_analysis_manager_with_temp_dir):
    """
    Test that the get_beats_in_range method works correctly.
    
    Args:
        audio_analysis_manager_with_temp_dir: The audio_analysis_manager_with_temp_dir fixture
    """
    manager = audio_analysis_manager_with_temp_dir
    
    # Mock the load_analysis method
    test_data = {
        "beats": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
        "downbeats": [1.0, 5.0]
    }
    manager.load_analysis = MagicMock(return_value=test_data)
    
    # Test with all beats
    result = manager.get_beats_in_range(2.5, 6.5)
    assert result == [3.0, 4.0, 5.0, 6.0]
    
    # Test with downbeats
    result = manager.get_beats_in_range(0.0, 10.0, beat_type="downbeat")
    assert result == [1.0, 5.0]


def test_get_feature_value_at_time(audio_analysis_manager_with_temp_dir):
    """
    Test that the get_feature_value_at_time method works correctly.
    
    Args:
        audio_analysis_manager_with_temp_dir: The audio_analysis_manager_with_temp_dir fixture
    """
    manager = audio_analysis_manager_with_temp_dir
    
    # Mock the load_analysis method
    test_data = {
        "energy_timeseries": {
            "times": [1.0, 2.0, 3.0],
            "values": [0.1, 0.2, 0.3]
        },
        "chroma_features": {
            "times": [1.0, 2.0, 3.0],
            "values": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        }
    }
    manager.load_analysis = MagicMock(return_value=test_data)
    
    # Test with a single-dimensional feature
    result = manager.get_feature_value_at_time(2.2, "energy")
    assert result == 0.2  # Closest to time 2.0
    
    # Test with a multi-dimensional feature
    result = manager.get_feature_value_at_time(2.2, "chroma")
    assert result == [0.2, 0.5]  # Values at index 1 (time 2.0)
    
    # Test with an unknown feature
    result = manager.get_feature_value_at_time(2.2, "unknown_feature")
    assert result is None