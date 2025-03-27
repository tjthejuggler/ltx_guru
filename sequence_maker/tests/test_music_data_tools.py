"""
Sequence Maker - Tests for Music Data Tools

This module contains tests for the music data tools used in LLM integration.
"""

import os
import json
import pytest
from unittest.mock import MagicMock, patch

from sequence_maker.app.llm.music_data_tools import MusicDataTools


@pytest.fixture
def mock_analysis_data():
    """
    Fixture that provides mock audio analysis data.
    
    Returns:
        dict: Mock analysis data
    """
    return {
        "song_title": "Test Song",
        "duration_seconds": 180.5,
        "estimated_tempo": 120.0,
        "time_signature_guess": "4/4",
        "beats": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
        "downbeats": [0.5, 2.5],
        "sections": [
            {"label": "Intro", "start": 0.0, "end": 10.0},
            {"label": "Verse 1", "start": 10.0, "end": 30.0},
            {"label": "Chorus 1", "start": 30.0, "end": 50.0}
        ],
        "energy_timeseries": {
            "times": [0.0, 1.0, 2.0, 3.0, 4.0],
            "values": [0.1, 0.2, 0.3, 0.4, 0.5]
        },
        "onset_strength_timeseries": {
            "times": [0.0, 1.0, 2.0, 3.0, 4.0],
            "values": [0.05, 0.15, 0.25, 0.35, 0.45]
        },
        "chroma_features": {
            "times": [0.0, 1.0, 2.0, 3.0, 4.0],
            "values": [
                [0.1, 0.2, 0.3, 0.4, 0.5],
                [0.2, 0.3, 0.4, 0.5, 0.6],
                [0.3, 0.4, 0.5, 0.6, 0.7],
                [0.4, 0.5, 0.6, 0.7, 0.8],
                [0.5, 0.6, 0.7, 0.8, 0.9],
                [0.6, 0.7, 0.8, 0.9, 1.0],
                [0.7, 0.8, 0.9, 1.0, 0.9],
                [0.8, 0.9, 1.0, 0.9, 0.8],
                [0.9, 1.0, 0.9, 0.8, 0.7],
                [1.0, 0.9, 0.8, 0.7, 0.6],
                [0.9, 0.8, 0.7, 0.6, 0.5],
                [0.8, 0.7, 0.6, 0.5, 0.4]
            ]
        },
        "spectral_contrast": {
            "times": [0.0, 1.0, 2.0, 3.0, 4.0],
            "values": [
                [0.1, 0.2, 0.3, 0.4, 0.5],
                [0.2, 0.3, 0.4, 0.5, 0.6],
                [0.3, 0.4, 0.5, 0.6, 0.7],
                [0.4, 0.5, 0.6, 0.7, 0.8],
                [0.5, 0.6, 0.7, 0.8, 0.9],
                [0.6, 0.7, 0.8, 0.9, 1.0],
                [0.7, 0.8, 0.9, 1.0, 0.9]
            ]
        },
        "spectral_centroid": {
            "times": [0.0, 1.0, 2.0, 3.0, 4.0],
            "values": [1000, 1100, 1200, 1300, 1400]
        },
        "spectral_rolloff": {
            "times": [0.0, 1.0, 2.0, 3.0, 4.0],
            "values": [2000, 2100, 2200, 2300, 2400]
        },
        "zero_crossing_rate": {
            "times": [0.0, 1.0, 2.0, 3.0, 4.0],
            "values": [0.01, 0.02, 0.03, 0.04, 0.05]
        }
    }


@pytest.fixture
def music_data_tools(app_fixture, mock_analysis_data):
    """
    Fixture that provides a MusicDataTools instance with mocked dependencies.
    
    Args:
        app_fixture: The app_fixture fixture
        mock_analysis_data: The mock_analysis_data fixture
        
    Returns:
        MusicDataTools: A MusicDataTools instance with mocked dependencies
    """
    # Create a mock audio analysis manager
    mock_audio_analysis_manager = MagicMock()
    mock_audio_analysis_manager.load_analysis.return_value = mock_analysis_data
    mock_audio_analysis_manager.get_beats_in_range.side_effect = lambda start, end, beat_type: [
        beat for beat in (
            mock_analysis_data["downbeats"] if beat_type == "downbeat" else mock_analysis_data["beats"]
        ) if start <= beat < end
    ]
    mock_audio_analysis_manager.get_section_by_label.side_effect = lambda label: next(
        (section for section in mock_analysis_data["sections"] if section["label"] == label), None
    )
    mock_audio_analysis_manager.get_feature_value_at_time.side_effect = lambda time, feature_name: (
        _mock_get_feature_value_at_time(mock_analysis_data, time, feature_name)
    )
    
    # Attach the mock audio analysis manager to the app
    app_fixture.audio_analysis_manager = mock_audio_analysis_manager
    
    # Create a mock audio manager
    mock_audio_manager = MagicMock()
    mock_audio_manager.audio_file = "test_audio.mp3"
    app_fixture.audio_manager = mock_audio_manager
    
    # Create the music data tools instance
    tools = MusicDataTools(app_fixture)
    
    return tools


def _mock_get_feature_value_at_time(mock_data, time, feature_name):
    """
    Helper function to mock the get_feature_value_at_time method.
    
    Args:
        mock_data: Mock analysis data
        time: Time in seconds
        feature_name: Name of the feature
        
    Returns:
        Feature value at the specified time
    """
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
    if not feature_key or feature_key not in mock_data:
        return None
    
    feature_data = mock_data[feature_key]
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


def test_music_data_functions(music_data_tools):
    """
    Test that the music_data_functions property returns the correct function definitions.
    
    Args:
        music_data_tools: The music_data_tools fixture
    """
    functions = music_data_tools.music_data_functions
    
    # Check that all expected functions are defined
    function_names = [f["name"] for f in functions]
    assert "get_song_metadata" in function_names
    assert "get_beats_in_range" in function_names
    assert "get_section_details" in function_names
    assert "get_feature_value_at_time" in function_names
    
    # Check that each function has the required properties
    for function in functions:
        assert "name" in function
        assert "description" in function
        assert "parameters" in function


def test_get_song_metadata(music_data_tools, mock_analysis_data):
    """
    Test that the _handle_get_song_metadata method returns the correct metadata.
    
    Args:
        music_data_tools: The music_data_tools fixture
        mock_analysis_data: The mock_analysis_data fixture
    """
    result = music_data_tools._handle_get_song_metadata({})
    
    # Check that the result contains the expected metadata
    assert result["song_title"] == mock_analysis_data["song_title"]
    assert result["duration_seconds"] == mock_analysis_data["duration_seconds"]
    assert result["estimated_tempo"] == mock_analysis_data["estimated_tempo"]
    assert result["time_signature_guess"] == mock_analysis_data["time_signature_guess"]
    assert result["total_beats"] == len(mock_analysis_data["beats"])
    assert result["total_downbeats"] == len(mock_analysis_data["downbeats"])
    assert result["sections"] == [section["label"] for section in mock_analysis_data["sections"]]
    assert result["audio_file"] == "test_audio.mp3"


def test_get_beats_in_range(music_data_tools, mock_analysis_data):
    """
    Test that the _handle_get_beats_in_range method returns the correct beats.
    
    Args:
        music_data_tools: The music_data_tools fixture
        mock_analysis_data: The mock_analysis_data fixture
    """
    # Test with all beats
    result = music_data_tools._handle_get_beats_in_range({
        "start_time": 1.0,
        "end_time": 3.0,
        "beat_type": "all"
    })
    
    # Check that the result contains the expected beats
    assert result["start_time"] == 1.0
    assert result["end_time"] == 3.0
    assert result["beat_type"] == "all"
    assert result["beats"] == [1.0, 1.5, 2.0, 2.5]
    assert result["count"] == 4
    
    # Test with downbeats
    result = music_data_tools._handle_get_beats_in_range({
        "start_time": 0.0,
        "end_time": 3.0,
        "beat_type": "downbeat"
    })
    
    # Check that the result contains the expected downbeats
    assert result["beat_type"] == "downbeat"
    assert result["beats"] == [0.5, 2.5]
    assert result["count"] == 2
    
    # Test with missing parameters
    result = music_data_tools._handle_get_beats_in_range({})
    assert "error" in result


def test_get_section_details(music_data_tools, mock_analysis_data):
    """
    Test that the _handle_get_section_details method returns the correct section details.
    
    Args:
        music_data_tools: The music_data_tools fixture
        mock_analysis_data: The mock_analysis_data fixture
    """
    # Test with existing section
    result = music_data_tools._handle_get_section_details({
        "section_label": "Verse 1"
    })
    
    # Check that the result contains the expected section details
    assert result["label"] == "Verse 1"
    assert result["start_time"] == 10.0
    assert result["end_time"] == 30.0
    assert result["duration"] == 20.0
    assert "beats" in result
    assert "beat_count" in result
    assert "downbeats" in result
    assert "downbeat_count" in result
    assert "average_energy" in result
    
    # Test with non-existent section
    result = music_data_tools._handle_get_section_details({
        "section_label": "Non-existent Section"
    })
    assert "error" in result
    assert "available_sections" in result
    
    # Test with missing parameters
    result = music_data_tools._handle_get_section_details({})
    assert "error" in result


def test_get_feature_value_at_time(music_data_tools, mock_analysis_data):
    """
    Test that the _handle_get_feature_value_at_time method returns the correct feature values.
    
    Args:
        music_data_tools: The music_data_tools fixture
        mock_analysis_data: The mock_analysis_data fixture
    """
    # Test with energy feature
    result = music_data_tools._handle_get_feature_value_at_time({
        "time": 1.0,
        "feature_name": "energy"
    })
    
    # Check that the result contains the expected feature value
    assert result["time"] == 1.0
    assert result["feature"] == "energy"
    assert result["value"] == 0.2
    
    # Test with chroma feature
    result = music_data_tools._handle_get_feature_value_at_time({
        "time": 2.0,
        "feature_name": "chroma"
    })
    
    # Check that the result contains the expected feature value
    assert result["time"] == 2.0
    assert result["feature"] == "chroma"
    assert "value" in result
    assert "pitch_classes" in result
    assert len(result["pitch_classes"]) == 12
    
    # Test with spectral contrast feature
    result = music_data_tools._handle_get_feature_value_at_time({
        "time": 3.0,
        "feature_name": "spectral_contrast"
    })
    
    # Check that the result contains the expected feature value
    assert result["time"] == 3.0
    assert result["feature"] == "spectral_contrast"
    assert "value" in result
    assert "bands" in result
    
    # Test with missing parameters
    result = music_data_tools._handle_get_feature_value_at_time({})
    assert "error" in result