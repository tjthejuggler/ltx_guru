"""
Sequence Maker - Integration Tests for Audio Functionality

This module contains integration tests for audio functionality in the Sequence Maker application.
"""

import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch


def test_audio_loading_updates_project(app_fixture, test_project_fixture, monkeypatch):
    """
    Test that loading an audio file updates the project state correctly.
    
    Args:
        app_fixture: The app_fixture fixture
        test_project_fixture: The test_project_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create a temporary audio file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        audio_path = temp_file.name
    
    try:
        # Mock the audio loading to avoid actually loading the file
        # This is necessary because we're using a dummy file
        with patch('sequence_maker.managers.audio_manager.AudioManager._load_audio_file') as mock_load:
            # Set up the mock to return a duration
            mock_load.return_value = (None, 120.0)  # 2 minutes duration
            
            # Load the audio file
            app_fixture.audio_manager.load_audio(audio_path)
            
            # Check that the project was updated correctly
            assert test_project_fixture.audio_file == audio_path
            assert test_project_fixture.audio_duration == 120.0
            
            # Check that the audio manager state was updated
            assert app_fixture.audio_manager.audio_file == audio_path
            assert app_fixture.audio_manager.duration == 120.0
    finally:
        # Clean up the temporary file
        if os.path.exists(audio_path):
            os.unlink(audio_path)


def test_audio_playback_controls(app_fixture, qtbot, monkeypatch):
    """
    Test that audio playback controls work correctly.
    
    Args:
        app_fixture: The app_fixture fixture
        qtbot: The qtbot fixture from pytest-qt
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Mock the audio playback methods to avoid actually playing audio
    monkeypatch.setattr(app_fixture.audio_manager, '_play_audio', MagicMock())
    monkeypatch.setattr(app_fixture.audio_manager, '_pause_audio', MagicMock())
    monkeypatch.setattr(app_fixture.audio_manager, '_stop_audio', MagicMock())
    
    # Test play
    app_fixture.audio_manager.play()
    assert app_fixture.audio_manager.is_playing
    app_fixture.audio_manager._play_audio.assert_called_once()
    
    # Test pause
    app_fixture.audio_manager.pause()
    assert not app_fixture.audio_manager.is_playing
    app_fixture.audio_manager._pause_audio.assert_called_once()
    
    # Test stop
    app_fixture.audio_manager.stop()
    assert not app_fixture.audio_manager.is_playing
    app_fixture.audio_manager._stop_audio.assert_called_once()


def test_audio_position_updates(app_fixture, qtbot, monkeypatch):
    """
    Test that audio position updates are correctly propagated.
    
    Args:
        app_fixture: The app_fixture fixture
        qtbot: The qtbot fixture from pytest-qt
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create a signal spy to monitor position_changed signal
    with qtbot.waitSignal(app_fixture.audio_manager.position_changed, timeout=1000) as blocker:
        # Manually emit the position_changed signal
        app_fixture.audio_manager.position_changed.emit(30.0)  # 30 seconds
    
    # Check that the signal was emitted with the correct value
    assert blocker.args == [30.0]
    
    # Check that the timeline position was updated
    assert app_fixture.timeline_manager.position == 30.0


def test_audio_ui_integration(main_window_fixture, audio_manager_fixture, qtbot, monkeypatch):
    """
    Test that the audio UI controls correctly interact with the audio manager.
    
    Args:
        main_window_fixture: The main_window_fixture fixture
        audio_manager_fixture: The audio_manager_fixture fixture
        qtbot: The qtbot fixture from pytest-qt
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Mock the audio manager methods
    monkeypatch.setattr(audio_manager_fixture, 'play', MagicMock())
    monkeypatch.setattr(audio_manager_fixture, 'pause', MagicMock())
    monkeypatch.setattr(audio_manager_fixture, 'stop', MagicMock())
    
    # Test play action
    main_window_fixture.play_action.trigger()
    audio_manager_fixture.play.assert_called_once()
    
    # Test pause action
    main_window_fixture.pause_action.trigger()
    audio_manager_fixture.pause.assert_called_once()
    
    # Test stop action
    main_window_fixture.stop_action.trigger()
    audio_manager_fixture.stop.assert_called_once()


def test_audio_visualization_updates(app_fixture, qtbot, monkeypatch):
    """
    Test that audio visualizations are updated when audio is loaded.
    
    Args:
        app_fixture: The app_fixture fixture
        qtbot: The qtbot fixture from pytest-qt
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create a temporary audio file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        audio_path = temp_file.name
    
    try:
        # Mock the audio loading and visualization methods
        with patch('sequence_maker.managers.audio_manager.AudioManager._load_audio_file') as mock_load, \
             patch('sequence_maker.ui.audio_widget.AudioWidget.update_visualizations') as mock_update:
            
            # Set up the mock to return a duration
            mock_load.return_value = (None, 120.0)  # 2 minutes duration
            
            # Load the audio file
            app_fixture.audio_manager.load_audio(audio_path)
            
            # Check that the visualization update was called
            mock_update.assert_called()
    finally:
        # Clean up the temporary file
        if os.path.exists(audio_path):
            os.unlink(audio_path)