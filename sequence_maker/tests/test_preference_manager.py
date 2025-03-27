"""
Sequence Maker - Tests for PreferenceManager

This module contains tests for the PreferenceManager class.
"""

import os
import json
import pytest
import sqlite3
import tempfile
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
from datetime import datetime

# Import the PreferenceManager class
from sequence_maker.managers.preference_manager import PreferenceManager


# Fixture for PreferenceManager with a temporary database
@pytest.fixture
def preference_manager_with_temp_db(app_fixture, monkeypatch):
    """
    Fixture that provides a PreferenceManager instance with a temporary database.
    
    Args:
        app_fixture: The app_fixture fixture from conftest.py
        monkeypatch: The monkeypatch fixture from pytest
        
    Returns:
        A PreferenceManager instance with a temporary database
    """
    # Create a temporary directory for the database
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a PreferenceManager instance
        manager = PreferenceManager(app_fixture)
        
        # Override the database path
        temp_db_path = Path(temp_dir) / "test_preferences.db"
        monkeypatch.setattr(manager, 'db_path', temp_db_path)
        
        # Re-initialize the database with the new path
        manager._init_db()
        
        yield manager


def test_initialization(preference_manager_with_temp_db):
    """
    Test that the PreferenceManager initializes correctly.
    
    Args:
        preference_manager_with_temp_db: The preference_manager_with_temp_db fixture
    """
    manager = preference_manager_with_temp_db
    
    # Check that the manager was initialized correctly
    assert manager.app is not None
    assert manager.logger is not None
    assert manager.db_path is not None
    
    # Check that the database was created
    assert manager.db_path.exists()


def test_add_feedback(preference_manager_with_temp_db):
    """
    Test that the add_feedback method works correctly.
    
    Args:
        preference_manager_with_temp_db: The preference_manager_with_temp_db fixture
    """
    manager = preference_manager_with_temp_db
    
    # Add feedback
    song_identifier = "test_song.mp3"
    feedback_text = "I like the blue pulses during the chorus"
    sentiment = 1
    tags = ["chorus", "pulse", "blue"]
    
    result = manager.add_feedback(song_identifier, feedback_text, sentiment, tags)
    
    # Check that the feedback was added successfully
    assert result is True
    
    # Verify the feedback was stored in the database
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM preferences WHERE song_identifier = ?", (song_identifier,))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[1] == song_identifier
    assert row[2] == feedback_text
    assert row[3] == sentiment
    assert json.loads(row[4]) == tags


def test_get_preference_summary_empty(preference_manager_with_temp_db):
    """
    Test that the get_preference_summary method works correctly with no preferences.
    
    Args:
        preference_manager_with_temp_db: The preference_manager_with_temp_db fixture
    """
    manager = preference_manager_with_temp_db
    
    # Get preference summary for a song with no preferences
    summary = manager.get_preference_summary("nonexistent_song.mp3")
    
    # Check that the summary is empty
    assert "User Preference Summary" in summary
    assert "Song-specific preferences" not in summary
    assert "General preferences" not in summary


def test_get_preference_summary_with_preferences(preference_manager_with_temp_db):
    """
    Test that the get_preference_summary method works correctly with preferences.
    
    Args:
        preference_manager_with_temp_db: The preference_manager_with_temp_db fixture
    """
    manager = preference_manager_with_temp_db
    
    # Add song-specific preferences
    song_identifier = "test_song.mp3"
    manager.add_feedback(song_identifier, "I like the blue pulses during the chorus", 1, ["chorus", "pulse", "blue"])
    manager.add_feedback(song_identifier, "The transition to the verse is too abrupt", -1, ["transition", "verse"])
    
    # Add general preferences
    manager.add_feedback("other_song.mp3", "Slow color fades during verses", 1, ["verse", "fade", "color"])
    
    # Get preference summary
    summary = manager.get_preference_summary(song_identifier)
    
    # Check that the summary contains the expected preferences
    assert "User Preference Summary" in summary
    assert "Song-specific preferences" in summary
    assert "Likes: I like the blue pulses during the chorus" in summary
    assert "Dislikes: The transition to the verse is too abrupt" in summary
    assert "General preferences" in summary
    assert "Likes: Slow color fades during verses" in summary


def test_get_all_preferences(preference_manager_with_temp_db):
    """
    Test that the get_all_preferences method works correctly.
    
    Args:
        preference_manager_with_temp_db: The preference_manager_with_temp_db fixture
    """
    manager = preference_manager_with_temp_db
    
    # Add preferences
    manager.add_feedback("song1.mp3", "Feedback 1", 1, ["tag1", "tag2"])
    manager.add_feedback("song2.mp3", "Feedback 2", 0, ["tag3"])
    manager.add_feedback("song3.mp3", "Feedback 3", -1, ["tag4", "tag5", "tag6"])
    
    # Get all preferences
    preferences = manager.get_all_preferences()
    
    # Check that all preferences were retrieved
    assert len(preferences) == 3
    
    # Check that the preferences are in the correct order (most recent first)
    assert preferences[0]["feedback_text"] == "Feedback 3"
    assert preferences[1]["feedback_text"] == "Feedback 2"
    assert preferences[2]["feedback_text"] == "Feedback 1"
    
    # Check that the tags were parsed correctly
    assert preferences[0]["tags"] == ["tag4", "tag5", "tag6"]
    assert preferences[1]["tags"] == ["tag3"]
    assert preferences[2]["tags"] == ["tag1", "tag2"]
    
    # Test with limit
    limited_preferences = manager.get_all_preferences(limit=2)
    assert len(limited_preferences) == 2
    assert limited_preferences[0]["feedback_text"] == "Feedback 3"
    assert limited_preferences[1]["feedback_text"] == "Feedback 2"


def test_get_preferences_for_song(preference_manager_with_temp_db):
    """
    Test that the get_preferences_for_song method works correctly.
    
    Args:
        preference_manager_with_temp_db: The preference_manager_with_temp_db fixture
    """
    manager = preference_manager_with_temp_db
    
    # Add preferences for multiple songs
    song_identifier = "test_song.mp3"
    manager.add_feedback(song_identifier, "Feedback 1", 1, ["tag1"])
    manager.add_feedback(song_identifier, "Feedback 2", -1, ["tag2"])
    manager.add_feedback("other_song.mp3", "Feedback 3", 0, ["tag3"])
    
    # Get preferences for a specific song
    preferences = manager.get_preferences_for_song(song_identifier)
    
    # Check that only preferences for the specified song were retrieved
    assert len(preferences) == 2
    assert all(p["song_identifier"] == song_identifier for p in preferences)
    
    # Check that the preferences are in the correct order (most recent first)
    assert preferences[0]["feedback_text"] == "Feedback 2"
    assert preferences[1]["feedback_text"] == "Feedback 1"
    
    # Test with limit
    limited_preferences = manager.get_preferences_for_song(song_identifier, limit=1)
    assert len(limited_preferences) == 1
    assert limited_preferences[0]["feedback_text"] == "Feedback 2"


def test_clear_preferences(preference_manager_with_temp_db):
    """
    Test that the clear_preferences method works correctly.
    
    Args:
        preference_manager_with_temp_db: The preference_manager_with_temp_db fixture
    """
    manager = preference_manager_with_temp_db
    
    # Add preferences
    manager.add_feedback("song1.mp3", "Feedback 1", 1, ["tag1"])
    manager.add_feedback("song2.mp3", "Feedback 2", 0, ["tag2"])
    
    # Verify preferences were added
    assert len(manager.get_all_preferences()) == 2
    
    # Clear preferences
    result = manager.clear_preferences()
    
    # Check that the preferences were cleared successfully
    assert result is True
    assert len(manager.get_all_preferences()) == 0


def test_error_handling(preference_manager_with_temp_db, monkeypatch):
    """
    Test that the PreferenceManager handles errors correctly.
    
    Args:
        preference_manager_with_temp_db: The preference_manager_with_temp_db fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    manager = preference_manager_with_temp_db
    
    # Mock sqlite3.connect to raise an exception
    def mock_connect(*args, **kwargs):
        raise sqlite3.Error("Test error")
    
    monkeypatch.setattr(sqlite3, "connect", mock_connect)
    
    # Test error handling in add_feedback
    result = manager.add_feedback("song.mp3", "Feedback", 1, ["tag"])
    assert result is False
    
    # Test error handling in get_preference_summary
    summary = manager.get_preference_summary("song.mp3")
    assert summary == ""
    
    # Test error handling in get_all_preferences
    preferences = manager.get_all_preferences()
    assert preferences == []
    
    # Test error handling in get_preferences_for_song
    song_preferences = manager.get_preferences_for_song("song.mp3")
    assert song_preferences == []
    
    # Test error handling in clear_preferences
    result = manager.clear_preferences()
    assert result is False