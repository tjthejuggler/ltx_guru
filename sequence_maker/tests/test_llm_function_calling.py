"""
Tests for the LLM function calling implementation.
"""

import pytest
import json
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from ui.dialogs.llm_chat_window import LLMChatWindow


def test_function_call_display(qtbot, app_fixture, mocker):
    """Test that function calls are displayed correctly."""
    # Create window
    window = LLMChatWindow(app_fixture)
    qtbot.addWidget(window)
    window.show()
    
    # Mock function call data
    function_name = "create_segment"
    arguments = {
        "timeline_index": 0,
        "start_time": 1.0,
        "end_time": 2.0,
        "color": [255, 0, 0]
    }
    result = {
        "success": True,
        "segment": {
            "start_time": 1.0,
            "end_time": 2.0,
            "color": [255, 0, 0],
            "pixels": 1
        }
    }
    
    # Call function handler
    window._on_function_called(function_name, arguments, result)
    
    # Check that function call was added to chat history
    assert len(window.chat_history) == 1
    assert window.chat_history[0][0] == "System"
    assert "Function call: create_segment" in window.chat_history[0][1]
    assert json.dumps(arguments, indent=2) in window.chat_history[0][1]
    assert json.dumps(result, indent=2) in window.chat_history[0][1]


def test_streaming_response(qtbot, app_fixture, mocker):
    """Test that streaming responses are handled correctly."""
    # Create window
    window = LLMChatWindow(app_fixture)
    qtbot.addWidget(window)
    window.show()
    
    # Send chunks
    window._on_response_chunk("Hello")
    window._on_response_chunk(" ")
    window._on_response_chunk("world")
    window._on_response_chunk("!")
    
    # Check that streaming message was added to chat history
    assert len(window.chat_history) == 1
    assert window.chat_history[0][0] == "Assistant (streaming)"
    assert window.chat_history[0][1] == "Hello world!"
    
    # Simulate final response
    window._on_llm_response("Hello world! How are you?", {})
    
    # Check that streaming message was replaced with final message
    assert len(window.chat_history) == 1
    assert window.chat_history[0][0] == "Assistant"
    assert window.chat_history[0][1] == "Hello world! How are you?"


def test_send_with_functions(qtbot, app_fixture, mocker):
    """Test sending a message with function calling enabled."""
    # Mock LLM manager
    mocker.patch.object(app_fixture.llm_manager, 'send_request', return_value=True)
    mocker.patch.object(app_fixture.llm_manager, 'is_configured', return_value=True)
    
    # Create window
    window = LLMChatWindow(app_fixture)
    qtbot.addWidget(window)
    window.show()
    
    # Set message text
    window.input_text.setPlainText("Create a red segment from 1 to 2 seconds")
    
    # Click send button
    qtbot.mouseClick(window.send_button, Qt.MouseButton.LeftButton)
    
    # Check that message was added to chat history
    assert len(window.chat_history) == 1
    assert window.chat_history[0][0] == "You"
    assert window.chat_history[0][1] == "Create a red segment from 1 to 2 seconds"
    
    # Check that LLM manager was called with function calling enabled
    app_fixture.llm_manager.send_request.assert_called_once()
    args, kwargs = app_fixture.llm_manager.send_request.call_args
    assert kwargs.get('use_functions') is True
    assert kwargs.get('stream') is True