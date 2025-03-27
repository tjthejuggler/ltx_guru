"""
Sequence Maker - Tests for Pattern Tools

This module contains tests for the pattern tools used in LLM integration.
"""

import os
import json
import pytest
from unittest.mock import MagicMock, patch

from sequence_maker.app.llm.pattern_tools import PatternTools


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
            "times": [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0],
            "values": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.8, 0.7]
        }
    }


@pytest.fixture
def pattern_tools(app_fixture, mock_analysis_data):
    """
    Fixture that provides a PatternTools instance with mocked dependencies.
    
    Args:
        app_fixture: The app_fixture fixture
        mock_analysis_data: The mock_analysis_data fixture
        
    Returns:
        PatternTools: A PatternTools instance with mocked dependencies
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
    
    # Create a mock timeline manager
    mock_timeline_manager = MagicMock()
    mock_timeline_manager.create_segment.side_effect = lambda timeline_index, start_time, end_time, color: {
        "timeline_index": timeline_index,
        "start_time": start_time,
        "end_time": end_time,
        "color": color
    }
    
    # Attach the mocks to the app
    app_fixture.audio_analysis_manager = mock_audio_analysis_manager
    app_fixture.timeline_manager = mock_timeline_manager
    
    # Create the pattern tools instance
    tools = PatternTools(app_fixture)
    
    # Mock the _resolve_color_name method to return the input if it's a list, or [255, 0, 0] for "red", etc.
    tools._resolve_color_name = lambda color: (
        color if isinstance(color, list) else 
        [255, 0, 0] if color == "red" else
        [0, 255, 0] if color == "green" else
        [0, 0, 255] if color == "blue" else
        [255, 255, 0] if color == "yellow" else
        [255, 255, 255]  # default to white
    )
    
    return tools


def test_pattern_functions(pattern_tools):
    """
    Test that the pattern_functions property returns the correct function definitions.
    
    Args:
        pattern_tools: The pattern_tools fixture
    """
    functions = pattern_tools.pattern_functions
    
    # Check that all expected functions are defined
    function_names = [f["name"] for f in functions]
    assert "apply_beat_pattern" in function_names
    assert "apply_section_theme" in function_names
    
    # Check that each function has the required properties
    for function in functions:
        assert "name" in function
        assert "description" in function
        assert "parameters" in function


def test_apply_beat_pattern_pulse(pattern_tools):
    """
    Test that the _handle_apply_beat_pattern method works correctly with pulse pattern.
    
    Args:
        pattern_tools: The pattern_tools fixture
    """
    result = pattern_tools._handle_apply_beat_pattern({
        "timeline_index": 0,
        "start_time": 0.0,
        "end_time": 3.0,
        "pattern_type": "pulse",
        "colors": ["red", "green", "blue"],
        "beat_type": "all",
        "duration": 0.2
    })
    
    # Check that the result contains the expected data
    assert result["pattern_type"] == "pulse"
    assert result["timeline_index"] == 0
    assert result["start_time"] == 0.0
    assert result["end_time"] == 3.0
    assert result["beat_count"] == 5  # 0.5, 1.0, 1.5, 2.0, 2.5
    assert len(result["segments_created"]) == 5
    
    # Check that the segments have the correct properties
    for i, segment in enumerate(result["segments"]):
        assert "start_time" in segment
        assert "end_time" in segment
        assert "color" in segment
        assert segment["end_time"] - segment["start_time"] == 0.2  # Duration


def test_apply_beat_pattern_toggle(pattern_tools):
    """
    Test that the _handle_apply_beat_pattern method works correctly with toggle pattern.
    
    Args:
        pattern_tools: The pattern_tools fixture
    """
    result = pattern_tools._handle_apply_beat_pattern({
        "timeline_index": 0,
        "start_time": 0.0,
        "end_time": 3.0,
        "pattern_type": "toggle",
        "colors": ["red", "green"],
        "beat_type": "all"
    })
    
    # Check that the result contains the expected data
    assert result["pattern_type"] == "toggle"
    assert result["timeline_index"] == 0
    assert result["start_time"] == 0.0
    assert result["end_time"] == 3.0
    assert result["beat_count"] == 5  # 0.5, 1.0, 1.5, 2.0, 2.5
    
    # Toggle pattern creates segments between beats, plus one after the last beat
    assert len(result["segments_created"]) == 5
    
    # Check that the segments have the correct properties
    for i in range(len(result["segments"]) - 1):
        segment = result["segments"][i]
        next_segment = result["segments"][i + 1]
        assert segment["end_time"] == next_segment["start_time"]  # Segments should be contiguous


def test_apply_beat_pattern_fade_in(pattern_tools):
    """
    Test that the _handle_apply_beat_pattern method works correctly with fade_in pattern.
    
    Args:
        pattern_tools: The pattern_tools fixture
    """
    result = pattern_tools._handle_apply_beat_pattern({
        "timeline_index": 0,
        "start_time": 0.0,
        "end_time": 1.5,
        "pattern_type": "fade_in",
        "colors": ["red"],
        "beat_type": "all",
        "duration": 0.5
    })
    
    # Check that the result contains the expected data
    assert result["pattern_type"] == "fade_in"
    assert result["timeline_index"] == 0
    assert result["start_time"] == 0.0
    assert result["end_time"] == 1.5
    assert result["beat_count"] == 3  # 0.5, 1.0, 1.5
    
    # Fade in creates multiple segments per beat (5 steps)
    assert len(result["segments_created"]) == 15  # 3 beats * 5 steps
    
    # Check that the segments have the correct properties
    for i in range(0, len(result["segments"]), 5):
        # Check that brightness increases in each step
        for j in range(4):
            current = result["segments"][i + j]["color"][0]  # Red component
            next_val = result["segments"][i + j + 1]["color"][0]
            assert next_val > current  # Brightness should increase


def test_apply_beat_pattern_fade_out(pattern_tools):
    """
    Test that the _handle_apply_beat_pattern method works correctly with fade_out pattern.
    
    Args:
        pattern_tools: The pattern_tools fixture
    """
    result = pattern_tools._handle_apply_beat_pattern({
        "timeline_index": 0,
        "start_time": 0.0,
        "end_time": 1.5,
        "pattern_type": "fade_out",
        "colors": ["red"],
        "beat_type": "all",
        "duration": 0.5
    })
    
    # Check that the result contains the expected data
    assert result["pattern_type"] == "fade_out"
    assert result["timeline_index"] == 0
    assert result["start_time"] == 0.0
    assert result["end_time"] == 1.5
    assert result["beat_count"] == 3  # 0.5, 1.0, 1.5
    
    # Fade out creates multiple segments per beat (5 steps)
    assert len(result["segments_created"]) == 15  # 3 beats * 5 steps
    
    # Check that the segments have the correct properties
    for i in range(0, len(result["segments"]), 5):
        # Check that brightness decreases in each step
        for j in range(4):
            current = result["segments"][i + j]["color"][0]  # Red component
            next_val = result["segments"][i + j + 1]["color"][0]
            assert next_val < current  # Brightness should decrease


def test_apply_beat_pattern_with_section(pattern_tools):
    """
    Test that the _handle_apply_beat_pattern method works correctly with section_label.
    
    Args:
        pattern_tools: The pattern_tools fixture
    """
    result = pattern_tools._handle_apply_beat_pattern({
        "timeline_index": 0,
        "pattern_type": "pulse",
        "colors": ["red"],
        "section_label": "Verse 1",
        "beat_type": "all",
        "duration": 0.2
    })
    
    # Check that the result contains the expected data
    assert result["pattern_type"] == "pulse"
    assert result["timeline_index"] == 0
    assert result["start_time"] == 10.0  # Verse 1 starts at 10.0
    assert result["end_time"] == 30.0  # Verse 1 ends at 30.0
    
    # Check that the segments have the correct properties
    for segment in result["segments"]:
        assert 10.0 <= segment["start_time"] < 30.0  # Within Verse 1


def test_apply_beat_pattern_with_invalid_section(pattern_tools):
    """
    Test that the _handle_apply_beat_pattern method handles invalid section_label.
    
    Args:
        pattern_tools: The pattern_tools fixture
    """
    result = pattern_tools._handle_apply_beat_pattern({
        "timeline_index": 0,
        "pattern_type": "pulse",
        "colors": ["red"],
        "section_label": "Non-existent Section",
        "beat_type": "all",
        "duration": 0.2
    })
    
    # Check that the result contains an error
    assert "error" in result
    assert "available_sections" in result


def test_apply_section_theme(pattern_tools):
    """
    Test that the _handle_apply_section_theme method works correctly.
    
    Args:
        pattern_tools: The pattern_tools fixture
    """
    result = pattern_tools._handle_apply_section_theme({
        "timeline_index": 0,
        "section_themes": [
            {
                "section_label": "Intro",
                "base_color": "red",
                "energy_mapping": "none"
            },
            {
                "section_label": "Verse 1",
                "base_color": "green",
                "energy_mapping": "brightness"
            },
            {
                "section_label": "Chorus 1",
                "base_color": "blue",
                "energy_mapping": "saturation"
            }
        ],
        "default_color": "yellow"
    })
    
    # Check that the result contains the expected data
    assert result["timeline_index"] == 0
    assert len(result["sections_themed"]) == 3
    
    # Check that each section has the correct theme
    section_colors = {theme["section_label"]: theme["base_color"] for theme in result["sections_themed"]}
    assert section_colors["Intro"] == [255, 0, 0]  # red
    assert section_colors["Verse 1"] == [0, 255, 0]  # green
    assert section_colors["Chorus 1"] == [0, 0, 255]  # blue
    
    # Check that segments were created
    assert len(result["segments"]) > 0


def test_apply_section_theme_with_energy_mapping(pattern_tools):
    """
    Test that the _handle_apply_section_theme method works correctly with energy mapping.
    
    Args:
        pattern_tools: The pattern_tools fixture
    """
    result = pattern_tools._handle_apply_section_theme({
        "timeline_index": 0,
        "section_themes": [
            {
                "section_label": "Verse 1",
                "base_color": "red",
                "energy_mapping": "brightness"
            }
        ]
    })
    
    # Check that the result contains the expected data
    assert result["timeline_index"] == 0
    assert len(result["sections_themed"]) == 1
    assert result["sections_themed"][0]["section_label"] == "Verse 1"
    assert result["sections_themed"][0]["energy_mapping"] == "brightness"
    
    # Check that multiple segments were created for the section (energy mapping)
    verse_segments = [s for s in result["segments"] if 10.0 <= s["start_time"] < 30.0]
    assert len(verse_segments) > 1