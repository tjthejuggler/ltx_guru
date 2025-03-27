"""
Sequence Maker - Test Feedback UI

This module contains tests for the feedback UI elements and submission functionality.
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from sequence_maker.ui.dialogs.llm_chat_window import LLMChatWindow
from sequence_maker.ui.dialogs.llm_chat_dialog import LLMChatDialog
from sequence_maker.managers.preference_manager import PreferenceManager


@pytest.fixture
def app_mock():
    """Create a mock application instance."""
    app = MagicMock()
    app.audio_manager.audio_file = "/path/to/test_song.mp3"
    app.preference_manager = MagicMock(spec=PreferenceManager)
    app.preference_manager.add_feedback.return_value = True
    return app


@pytest.fixture
def chat_window(app_mock, qtbot):
    """Create a chat window instance for testing."""
    window = LLMChatWindow(app_mock)
    qtbot.addWidget(window)
    return window


@pytest.fixture
def chat_dialog(app_mock, qtbot):
    """Create a chat dialog instance for testing."""
    dialog = LLMChatDialog(app_mock)
    qtbot.addWidget(dialog)
    return dialog


def test_feedback_ui_elements_in_window(chat_window):
    """Test that feedback UI elements are properly created in the chat window."""
    # Check that feedback group exists
    assert chat_window.feedback_group is not None
    
    # Check that feedback text field exists
    assert chat_window.feedback_text is not None
    
    # Check that sentiment buttons exist
    assert chat_window.like_button is not None
    assert chat_window.neutral_button is not None
    assert chat_window.dislike_button is not None
    
    # Check that submit button exists
    assert chat_window.submit_feedback_button is not None


def test_feedback_ui_elements_in_dialog(chat_dialog):
    """Test that feedback UI elements are properly created in the chat dialog."""
    # Check that feedback group exists
    assert chat_dialog.feedback_group is not None
    
    # Check that feedback text field exists
    assert chat_dialog.feedback_text is not None
    
    # Check that sentiment buttons exist
    assert chat_dialog.like_button is not None
    assert chat_dialog.neutral_button is not None
    assert chat_dialog.dislike_button is not None
    
    # Check that submit button exists
    assert chat_dialog.submit_feedback_button is not None


def test_submit_feedback_in_window(chat_window, qtbot, monkeypatch):
    """Test submitting feedback in the chat window."""
    # Mock QMessageBox.information to avoid showing dialog
    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.information", lambda *args: None)
    
    # Set feedback text
    chat_window.feedback_text.setText("I like the blue pulses during the chorus")
    
    # Select sentiment
    chat_window.like_button.setChecked(True)
    
    # Click submit button
    qtbot.mouseClick(chat_window.submit_feedback_button, Qt.MouseButton.LeftButton)
    
    # Check that add_feedback was called with correct arguments
    chat_window.app.preference_manager.add_feedback.assert_called_once()
    args = chat_window.app.preference_manager.add_feedback.call_args[1]
    
    assert args["song_identifier"] == "test_song.mp3"
    assert args["feedback_text"] == "I like the blue pulses during the chorus"
    assert args["sentiment"] == 1  # Positive sentiment
    assert "blue" in args["tags"]
    assert "pulse" in args["tags"]


def test_submit_feedback_in_dialog(chat_dialog, qtbot, monkeypatch):
    """Test submitting feedback in the chat dialog."""
    # Mock QMessageBox.information to avoid showing dialog
    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.information", lambda *args: None)
    
    # Set feedback text
    chat_dialog.feedback_text.setText("I dislike the abrupt color transitions")
    
    # Select sentiment
    chat_dialog.dislike_button.setChecked(True)
    
    # Click submit button
    qtbot.mouseClick(chat_dialog.submit_feedback_button, Qt.MouseButton.LeftButton)
    
    # Check that add_feedback was called with correct arguments
    chat_dialog.app.preference_manager.add_feedback.assert_called_once()
    args = chat_dialog.app.preference_manager.add_feedback.call_args[1]
    
    assert args["song_identifier"] == "test_song.mp3"
    assert args["feedback_text"] == "I dislike the abrupt color transitions"
    assert args["sentiment"] == -1  # Negative sentiment
    assert "color" in args["tags"]


def test_empty_feedback_warning(chat_window, qtbot, monkeypatch):
    """Test that a warning is shown when submitting empty feedback."""
    # Mock QMessageBox.warning to avoid showing dialog and track calls
    warning_mock = MagicMock()
    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.warning", warning_mock)
    
    # Leave feedback text empty
    chat_window.feedback_text.clear()
    
    # Click submit button
    qtbot.mouseClick(chat_window.submit_feedback_button, Qt.MouseButton.LeftButton)
    
    # Check that warning was shown
    warning_mock.assert_called_once()
    
    # Check that add_feedback was not called
    chat_window.app.preference_manager.add_feedback.assert_not_called()


def test_feedback_form_cleared_after_submission(chat_window, qtbot, monkeypatch):
    """Test that the feedback form is cleared after successful submission."""
    # Mock QMessageBox.information to avoid showing dialog
    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.information", lambda *args: None)
    
    # Set feedback text
    chat_window.feedback_text.setText("Test feedback")
    
    # Select sentiment
    chat_window.neutral_button.setChecked(True)
    
    # Click submit button
    qtbot.mouseClick(chat_window.submit_feedback_button, Qt.MouseButton.LeftButton)
    
    # Check that form was cleared
    assert chat_window.feedback_text.toPlainText() == ""
    assert not chat_window.like_button.isChecked()
    assert not chat_window.neutral_button.isChecked()
    assert not chat_window.dislike_button.isChecked()