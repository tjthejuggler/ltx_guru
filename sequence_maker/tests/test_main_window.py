"""
Sequence Maker - Functional/UI Tests for Main Window

This module contains functional and UI tests for the main window of the Sequence Maker application.
"""

import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QFileDialog, QMessageBox


def test_playback_starts_audio(qtbot, app_fixture, main_window_fixture, monkeypatch):
    """
    Test that playback starts audio correctly.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        main_window_fixture: The main_window_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Mock the audio manager's play method
    monkeypatch.setattr(app_fixture.audio_manager, 'play', MagicMock())
    
    # Trigger the play action
    main_window_fixture._on_play()
    
    # Check that the audio manager's play method was called
    app_fixture.audio_manager.play.assert_called_once()
    
    # Check that the play action is hidden and the pause action is visible
    assert not main_window_fixture.play_action.isVisible()
    assert main_window_fixture.pause_action.isVisible()


def test_pause_stops_audio(qtbot, app_fixture, main_window_fixture, monkeypatch):
    """
    Test that pause stops audio correctly.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        main_window_fixture: The main_window_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Mock the audio manager's pause method
    monkeypatch.setattr(app_fixture.audio_manager, 'pause', MagicMock())
    
    # Trigger the pause action
    main_window_fixture._on_pause()
    
    # Check that the audio manager's pause method was called
    app_fixture.audio_manager.pause.assert_called_once()
    
    # Check that the pause action is hidden and the play action is visible
    assert not main_window_fixture.pause_action.isVisible()
    assert main_window_fixture.play_action.isVisible()


def test_stop_resets_audio(qtbot, app_fixture, main_window_fixture, monkeypatch):
    """
    Test that stop resets audio correctly.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        main_window_fixture: The main_window_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Mock the audio manager's stop method
    monkeypatch.setattr(app_fixture.audio_manager, 'stop', MagicMock())
    
    # Trigger the stop action
    main_window_fixture._on_stop()
    
    # Check that the audio manager's stop method was called
    app_fixture.audio_manager.stop.assert_called_once()
    
    # Check that the pause action is hidden and the play action is visible
    assert not main_window_fixture.pause_action.isVisible()
    assert main_window_fixture.play_action.isVisible()


def test_new_project_creation(qtbot, app_fixture, main_window_fixture, monkeypatch):
    """
    Test creating a new project.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        main_window_fixture: The main_window_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Mock the check_unsaved_changes method to return True (no unsaved changes)
    monkeypatch.setattr(main_window_fixture, '_check_unsaved_changes', MagicMock(return_value=True))
    
    # Mock the project manager's new_project method
    monkeypatch.setattr(app_fixture.project_manager, 'new_project', MagicMock())
    
    # Trigger the new action
    main_window_fixture._on_new()
    
    # Check that the project manager's new_project method was called
    app_fixture.project_manager.new_project.assert_called_once()


def test_open_project(qtbot, app_fixture, main_window_fixture, monkeypatch):
    """
    Test opening a project.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        main_window_fixture: The main_window_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create a temporary project file
    with tempfile.NamedTemporaryFile(suffix=".smproj", delete=False) as temp_file:
        project_path = temp_file.name
    
    try:
        # Mock the check_unsaved_changes method to return True (no unsaved changes)
        monkeypatch.setattr(main_window_fixture, '_check_unsaved_changes', MagicMock(return_value=True))
        
        # Mock the QFileDialog.getOpenFileName method to return our temporary file
        monkeypatch.setattr(QFileDialog, 'getOpenFileName', MagicMock(return_value=(project_path, "Sequence Maker Project (*.smproj)")))
        
        # Mock the project manager's load_project method
        monkeypatch.setattr(app_fixture.project_manager, 'load_project', MagicMock())
        
        # Trigger the open action
        main_window_fixture._on_open()
        
        # Check that the project manager's load_project method was called with the correct path
        app_fixture.project_manager.load_project.assert_called_once_with(project_path)
    finally:
        # Clean up the temporary file
        if os.path.exists(project_path):
            os.unlink(project_path)


def test_save_project(qtbot, app_fixture, main_window_fixture, monkeypatch):
    """
    Test saving a project.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        main_window_fixture: The main_window_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Set a file path for the current project
    app_fixture.project_manager.current_project.file_path = "/path/to/project.smproj"
    
    # Mock the project manager's save_project method
    monkeypatch.setattr(app_fixture.project_manager, 'save_project', MagicMock(return_value=True))
    
    # Trigger the save action
    main_window_fixture._on_save()
    
    # Check that the project manager's save_project method was called
    app_fixture.project_manager.save_project.assert_called_once()


def test_save_as_project(qtbot, app_fixture, main_window_fixture, monkeypatch):
    """
    Test saving a project with a new name.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        main_window_fixture: The main_window_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create a temporary directory for the project
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = os.path.join(temp_dir, "project.smproj")
        
        # Mock the QFileDialog.getSaveFileName method to return our temporary file
        monkeypatch.setattr(QFileDialog, 'getSaveFileName', MagicMock(return_value=(project_path, "Sequence Maker Project (*.smproj)")))
        
        # Mock the project manager's save_project method
        monkeypatch.setattr(app_fixture.project_manager, 'save_project', MagicMock(return_value=True))
        
        # Trigger the save as action
        main_window_fixture._on_save_as()
        
        # Check that the project manager's save_project method was called with the correct path
        app_fixture.project_manager.save_project.assert_called_once_with(project_path)


def test_load_audio(qtbot, app_fixture, main_window_fixture, monkeypatch):
    """
    Test loading an audio file.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        main_window_fixture: The main_window_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create a temporary audio file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        audio_path = temp_file.name
    
    try:
        # Mock the QFileDialog.getOpenFileName method to return our temporary file
        monkeypatch.setattr(QFileDialog, 'getOpenFileName', MagicMock(return_value=(audio_path, "Audio Files (*.mp3 *.wav)")))
        
        # Mock the audio manager's load_audio method
        monkeypatch.setattr(app_fixture.audio_manager, 'load_audio', MagicMock())
        
        # Trigger the load audio action
        main_window_fixture._on_load_audio()
        
        # Check that the audio manager's load_audio method was called with the correct path
        app_fixture.audio_manager.load_audio.assert_called_once_with(audio_path)
    finally:
        # Clean up the temporary file
        if os.path.exists(audio_path):
            os.unlink(audio_path)


def test_export_json(qtbot, app_fixture, main_window_fixture, monkeypatch):
    """
    Test exporting to JSON.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        main_window_fixture: The main_window_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create a temporary directory for the export
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock the QFileDialog.getExistingDirectory method to return our temporary directory
        monkeypatch.setattr(QFileDialog, 'getExistingDirectory', MagicMock(return_value=temp_dir))
        
        # Ensure we have at least one timeline
        if len(app_fixture.timeline_manager.timelines) == 0:
            app_fixture.timeline_manager.add_timeline()
        
        # Mock the json exporter's export_timeline method
        with patch('sequence_maker.export.json_exporter.export_timeline') as mock_export:
            # Trigger the export JSON action
            main_window_fixture._on_export_json()
            
            # Check that the export_timeline method was called
            assert mock_export.call_count > 0


def test_export_prg(qtbot, app_fixture, main_window_fixture, monkeypatch):
    """
    Test exporting to PRG.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        main_window_fixture: The main_window_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create a temporary directory for the export
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock the QFileDialog.getExistingDirectory method to return our temporary directory
        monkeypatch.setattr(QFileDialog, 'getExistingDirectory', MagicMock(return_value=temp_dir))
        
        # Ensure we have at least one timeline
        if len(app_fixture.timeline_manager.timelines) == 0:
            app_fixture.timeline_manager.add_timeline()
        
        # Mock the prg exporter's export_timeline method
        with patch('sequence_maker.export.prg_exporter.export_timeline') as mock_export:
            # Trigger the export PRG action
            main_window_fixture._on_export_prg()
            
            # Check that the export_timeline method was called
            assert mock_export.call_count > 0


def test_about_dialog(qtbot, main_window_fixture, monkeypatch):
    """
    Test showing the about dialog.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        main_window_fixture: The main_window_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Mock the AboutDialog class
    with patch('sequence_maker.ui.dialogs.about_dialog.AboutDialog') as MockAboutDialog:
        # Set up the mock to return a MagicMock instance
        mock_dialog = MagicMock()
        MockAboutDialog.return_value = mock_dialog
        
        # Trigger the about action
        main_window_fixture._on_about()
        
        # Check that the dialog was created and shown
        MockAboutDialog.assert_called_once()
        mock_dialog.exec.assert_called_once()


def test_key_mapping_dialog(qtbot, main_window_fixture, monkeypatch):
    """
    Test showing the key mapping dialog.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        main_window_fixture: The main_window_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Mock the KeyMappingDialog class
    with patch('sequence_maker.ui.dialogs.key_mapping_dialog.KeyMappingDialog') as MockKeyMappingDialog:
        # Set up the mock to return a MagicMock instance
        mock_dialog = MagicMock()
        MockKeyMappingDialog.return_value = mock_dialog
        
        # Trigger the key mapping action
        main_window_fixture._on_key_mapping()
        
        # Check that the dialog was created and shown
        MockKeyMappingDialog.assert_called_once()
        mock_dialog.exec.assert_called_once()