"""
Sequence Maker - Test Fixtures

This module contains pytest fixtures for testing the Sequence Maker application.
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path

# Add the parent directory to the path so we can import the application modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def app_fixture(qtbot, monkeypatch):
    """
    Fixture that provides a SequenceMakerApp instance for testing.
    
    This fixture sets up a test environment with:
    - A temporary directory for test files
    - Mock splash screen to avoid GUI elements during testing
    - Disabled autosave
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        monkeypatch: The monkeypatch fixture from pytest
        
    Returns:
        A configured SequenceMakerApp instance
    """
    from sequence_maker.app.application import SequenceMakerApp
    from PyQt6.QtWidgets import QSplashScreen
    
    # Create a temporary directory for test files
    temp_dir = tempfile.TemporaryDirectory()
    
    # Mock the splash screen to avoid GUI elements during testing
    monkeypatch.setattr(QSplashScreen, "show", lambda self: None)
    monkeypatch.setattr(QSplashScreen, "finish", lambda self, window: None)
    
    # Mock time.sleep to avoid delays during testing
    import time
    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    
    # Create the application with debug mode enabled
    app = SequenceMakerApp(debug_mode=True)
    
    # Disable autosave for testing
    app.project_manager.stop_autosave()
    
    # Add the main window to qtbot
    qtbot.addWidget(app.main_window)
    
    # Yield the app for testing
    yield app
    
    # Clean up
    app.shutdown()
    temp_dir.cleanup()


@pytest.fixture
def main_window_fixture(app_fixture, qtbot):
    """
    Fixture that provides the MainWindow instance for testing.
    
    Args:
        app_fixture: The app_fixture fixture
        qtbot: The qtbot fixture from pytest-qt
        
    Returns:
        The MainWindow instance
    """
    return app_fixture.main_window


@pytest.fixture
def timeline_widget_fixture(main_window_fixture):
    """
    Fixture that provides the TimelineWidget instance for testing.
    
    Args:
        main_window_fixture: The main_window_fixture fixture
        
    Returns:
        The TimelineWidget instance
    """
    return main_window_fixture.timeline_widget


@pytest.fixture
def audio_widget_fixture(main_window_fixture):
    """
    Fixture that provides the AudioWidget instance for testing.
    
    Args:
        main_window_fixture: The main_window_fixture fixture
        
    Returns:
        The AudioWidget instance
    """
    return main_window_fixture.audio_widget


@pytest.fixture
def project_manager_fixture(app_fixture):
    """
    Fixture that provides the ProjectManager instance for testing.
    
    Args:
        app_fixture: The app_fixture fixture
        
    Returns:
        The ProjectManager instance
    """
    return app_fixture.project_manager


@pytest.fixture
def timeline_manager_fixture(app_fixture):
    """
    Fixture that provides the TimelineManager instance for testing.
    
    Args:
        app_fixture: The app_fixture fixture
        
    Returns:
        The TimelineManager instance
    """
    return app_fixture.timeline_manager


@pytest.fixture
def audio_manager_fixture(app_fixture):
    """
    Fixture that provides the AudioManager instance for testing.
    
    Args:
        app_fixture: The app_fixture fixture
        
    Returns:
        The AudioManager instance
    """
    return app_fixture.audio_manager


@pytest.fixture
def audio_analysis_manager_fixture(app_fixture):
    """
    Fixture that provides the AudioAnalysisManager instance for testing.
    
    Args:
        app_fixture: The app_fixture fixture
        
    Returns:
        The AudioAnalysisManager instance
    """
    return app_fixture.audio_analysis_manager


@pytest.fixture
def preference_manager_fixture(app_fixture):
    """
    Fixture that provides the PreferenceManager instance for testing.
    
    Args:
        app_fixture: The app_fixture fixture
        
    Returns:
        The PreferenceManager instance
    """
    return app_fixture.preference_manager


@pytest.fixture
def test_project_fixture(project_manager_fixture):
    """
    Fixture that creates a test project for testing.
    
    Args:
        project_manager_fixture: The project_manager_fixture fixture
        
    Returns:
        A test project
    """
    # Create a new project
    project_manager_fixture.new_project("Test Project")
    
    # Return the current project
    return project_manager_fixture.current_project


@pytest.fixture
def test_audio_file():
    """
    Fixture that provides a path to a test audio file.
    
    For real tests, you would need to create or provide a real audio file.
    This is just a placeholder that returns a non-existent path.
    
    Returns:
        Path to a test audio file
    """
    # In a real test, you would return a path to a real test audio file
    return os.path.join(os.path.dirname(__file__), "resources", "test_audio.mp3")