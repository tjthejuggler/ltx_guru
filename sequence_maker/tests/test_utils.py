"""
Sequence Maker - Unit Tests for Utility Functions

This module contains unit tests for utility functions in the Sequence Maker application.
"""

import pytest
from PyQt6.QtCore import Qt


def test_format_seconds_to_hms(main_window_fixture):
    """
    Test the _format_seconds_to_hms function in MainWindow.
    
    This function should format seconds into a human-readable time string.
    
    Args:
        main_window_fixture: The main_window_fixture fixture
    """
    # Test with include_hundredths=True and hide_hours_if_zero=True
    assert main_window_fixture._format_seconds_to_hms(90.0, True, True) == "01:30.00"
    
    # Test with include_hundredths=True and hide_hours_if_zero=False
    assert main_window_fixture._format_seconds_to_hms(90.0, True, False) == "00:01:30.00"
    
    # Test with hours
    assert main_window_fixture._format_seconds_to_hms(3661.0, True, False) == "01:01:01.00"
    
    # Test with include_hundredths=False
    assert main_window_fixture._format_seconds_to_hms(90.0, False, True) == "01:30"
    
    # Test with zero seconds
    assert main_window_fixture._format_seconds_to_hms(0.0, True, True) == "00:00.00"
    
    # Test with fractional seconds
    assert main_window_fixture._format_seconds_to_hms(90.25, True, True) == "01:30.25"


def test_parse_time_input(main_window_fixture):
    """
    Test the _parse_time_input function in MainWindow.
    
    This function should parse a time string into seconds.
    
    Args:
        main_window_fixture: The main_window_fixture fixture
    """
    # Test MM:SS.SS format
    assert main_window_fixture._parse_time_input("01:30.00") == 90.0
    
    # Test HH:MM:SS.SS format
    assert main_window_fixture._parse_time_input("01:01:01.00") == 3661.0
    
    # Test with fractional seconds
    assert main_window_fixture._parse_time_input("01:30.25") == 90.25
    
    # Test with invalid format (should return None)
    assert main_window_fixture._parse_time_input("invalid") is None


def test_format_time_input(main_window_fixture):
    """
    Test the _format_time_input function in MainWindow.
    
    This function should format seconds into a time string for the time input field.
    
    Args:
        main_window_fixture: The main_window_fixture fixture
    """
    # Test with seconds less than an hour
    assert main_window_fixture._format_time_input(90.0) == "01:30.00"
    
    # Test with seconds more than an hour
    assert main_window_fixture._format_time_input(3661.0) == "01:01:01.00"
    
    # Test with zero seconds
    assert main_window_fixture._format_time_input(0.0) == "00:00.00"
    
    # Test with fractional seconds
    assert main_window_fixture._format_time_input(90.25) == "01:30.25"


def test_format_length_input(main_window_fixture):
    """
    Test the _format_length_input function in MainWindow.
    
    This function should format seconds into a time string for the length input field.
    
    Args:
        main_window_fixture: The main_window_fixture fixture
    """
    # Test with seconds less than an hour
    assert main_window_fixture._format_length_input(90.0) == "00:01:30.00"
    
    # Test with seconds more than an hour
    assert main_window_fixture._format_length_input(3661.0) == "01:01:01.00"
    
    # Test with zero seconds
    assert main_window_fixture._format_length_input(0.0) == "00:00:00.00"
    
    # Test with fractional seconds
    assert main_window_fixture._format_length_input(90.25) == "00:01:30.25"


def test_get_color_name(main_window_fixture):
    """
    Test the _get_color_name function in MainWindow.
    
    This function should return a human-readable name for a color tuple.
    
    Args:
        main_window_fixture: The main_window_fixture fixture
    """
    # Test with red
    assert main_window_fixture._get_color_name((255, 0, 0)) == "Red"
    
    # Test with green
    assert main_window_fixture._get_color_name((0, 255, 0)) == "Green"
    
    # Test with blue
    assert main_window_fixture._get_color_name((0, 0, 255)) == "Blue"
    
    # Test with black
    assert main_window_fixture._get_color_name((0, 0, 0)) == "Black"
    
    # Test with white
    assert main_window_fixture._get_color_name((255, 255, 255)) == "White"
    
    # Test with a color that doesn't have a predefined name
    assert main_window_fixture._get_color_name((100, 100, 100)) == "RGB(100, 100, 100)"