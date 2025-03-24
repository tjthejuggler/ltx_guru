"""
Tests for the LLMChatWindow class.
"""

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from ui.dialogs.llm_chat_window import LLMChatWindow


def test_llm_chat_window_creation(qtbot, app_fixture):
    """Test that the LLM chat window can be created."""
    # Create window
    window = LLMChatWindow(app_fixture)
    qtbot.addWidget(window)
    
    # Check window properties
    assert window.windowTitle() == "LLM Chat"
    assert window.isHidden()  # Window should be hidden by default
    
    # Check window flags
    assert window.windowFlags() & Qt.WindowType.Tool
    assert window.windowFlags() & Qt.WindowType.Window


def test_llm_chat_window_show_hide(qtbot, app_fixture):
    """Test that the LLM chat window can be shown and hidden."""
    # Create window
    window = LLMChatWindow(app_fixture)
    qtbot.addWidget(window)
    
    # Show window
    window.show()
    assert window.isVisible()
    
    # Hide window
    window.hide()
    assert window.isHidden()
    
    # Test close event (should hide instead of close)
    window.show()
    window.close()
    assert window.isHidden()  # Window should be hidden, not closed


def test_llm_chat_window_minimize_button(qtbot, app_fixture):
    """Test that the minimize button hides the window."""
    # Create window
    window = LLMChatWindow(app_fixture)
    qtbot.addWidget(window)
    window.show()
    
    # Click minimize button
    qtbot.mouseClick(window.minimize_button, Qt.MouseButton.LeftButton)
    
    # Check that window is hidden
    assert window.isHidden()


def test_llm_chat_window_populate_timeline_list(qtbot, app_fixture, mocker):
    """Test that the timeline list is populated correctly."""
    # Mock project with timelines
    mock_timeline1 = mocker.MagicMock()
    mock_timeline1.name = "Timeline 1"
    
    mock_timeline2 = mocker.MagicMock()
    mock_timeline2.name = "Timeline 2"
    
    mock_project = mocker.MagicMock()
    mock_project.timelines = [mock_timeline1, mock_timeline2]
    
    # Mock project manager
    app_fixture.project_manager.current_project = mock_project
    
    # Create window
    window = LLMChatWindow(app_fixture)
    qtbot.addWidget(window)
    
    # Check timeline list
    assert window.timeline_list.count() == 2
    assert window.timeline_list.item(0).text() == "Ball 1: Timeline 1"
    assert window.timeline_list.item(1).text() == "Ball 2: Timeline 2"


def test_llm_chat_window_send_message(qtbot, app_fixture, mocker):
    """Test sending a message."""
    # Mock LLM manager
    mocker.patch.object(app_fixture.llm_manager, 'send_request', return_value=True)
    mocker.patch.object(app_fixture.llm_manager, 'is_configured', return_value=True)
    
    # Create window
    window = LLMChatWindow(app_fixture)
    qtbot.addWidget(window)
    window.show()
    
    # Set message text
    window.input_text.setPlainText("Test message")
    
    # Click send button
    qtbot.mouseClick(window.send_button, Qt.MouseButton.LeftButton)
    
    # Check that message was added to chat history
    assert len(window.chat_history) == 1
    assert window.chat_history[0][0] == "You"
    assert window.chat_history[0][1] == "Test message"
    
    # Check that input was cleared
    assert window.input_text.toPlainText() == ""
    
    # Check that LLM manager was called
    app_fixture.llm_manager.send_request.assert_called_once()


def test_llm_chat_window_stop_button(qtbot, app_fixture, mocker):
    """Test that the stop button interrupts the LLM request."""
    # Mock LLM manager
    mocker.patch.object(app_fixture.llm_manager, 'interrupt', return_value=True)
    mocker.patch.object(app_fixture.llm_manager, 'is_configured', return_value=True)
    
    # Create window
    window = LLMChatWindow(app_fixture)
    qtbot.addWidget(window)
    window.show()
    
    # Enable stop button and show progress bar
    window.stop_button.setEnabled(True)
    window.progress_bar.setVisible(True)
    
    # Click stop button
    qtbot.mouseClick(window.stop_button, Qt.MouseButton.LeftButton)
    
    # Check that LLM manager was called
    app_fixture.llm_manager.interrupt.assert_called_once()
    
    # Check that stop button was disabled and progress bar hidden
    assert not window.stop_button.isEnabled()
    assert not window.progress_bar.isVisible()