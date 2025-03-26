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


def test_create_segment_for_word_function(qtbot, app_fixture, mocker):
    """Test the create_segment_for_word orchestrator function."""
    # Create mock word timestamps result
    word_timestamps_result = {
        "success": True,
        "word_timestamps": [
            {
                "word": "test",
                "start": 1.0,
                "end": 1.5,
                "duration": 0.5,
                "formatted_start": "00:01.00",
                "formatted_end": "00:01.50"
            },
            {
                "word": "test",
                "start": 5.0,
                "end": 5.5,
                "duration": 0.5,
                "formatted_start": "00:05.00",
                "formatted_end": "00:05.50"
            }
        ],
        "count": 2
    }
    
    # Mock the _handle_get_word_timestamps method to return our test data
    mocker.patch.object(
        app_fixture.llm_manager,
        '_handle_get_word_timestamps',
        return_value=word_timestamps_result
    )
    
    # Mock the timeline_action_api.create_segment method
    mocker.patch.object(
        app_fixture.timeline_action_api,
        'create_segment',
        return_value={"success": True, "segment": {"start_time": 1.0, "end_time": 1.5, "color": [0, 0, 255]}}
    )
    
    # Mock the timeline_manager to have 3 timelines
    mocker.patch.object(app_fixture.timeline_manager, 'timelines', [mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock()])
    mocker.patch.object(app_fixture.timeline_manager, 'get_timeline', return_value=mocker.MagicMock())
    
    # Create parameters for the function
    parameters = {
        "word": "test",
        "color": "blue",
        "balls": "all"
    }
    
    # Call the function
    result = app_fixture.llm_manager._handle_create_segment_for_word(parameters)
    
    # Check the result
    assert result["success"] is True
    assert "Created 6 segment(s)" in result["message"]  # 2 occurrences × 3 balls = 6 segments
    assert len(result["details"]) == 6
    
    # Check that get_word_timestamps was called with the correct parameters
    app_fixture.llm_manager._handle_get_word_timestamps.assert_called_once_with({"word": "test"})
    
    # Check that create_segment was called for each occurrence and each ball
    assert app_fixture.timeline_action_api.create_segment.call_count == 6
    
    # Test with color as RGB array
    parameters = {
        "word": "test",
        "color": [255, 0, 0],
        "balls": [0, 1]  # Only apply to first two balls
    }
    
    # Reset mocks
    app_fixture.llm_manager._handle_get_word_timestamps.reset_mock()
    app_fixture.timeline_action_api.create_segment.reset_mock()
    
    # Call the function again
    result = app_fixture.llm_manager._handle_create_segment_for_word(parameters)
    
    # Check the result
    assert result["success"] is True
    assert "Created 4 segment(s)" in result["message"]  # 2 occurrences × 2 balls = 4 segments
    assert len(result["details"]) == 4
    
    # Check that create_segment was called with the correct parameters
    first_call_args = app_fixture.timeline_action_api.create_segment.call_args_list[0][0][0]
    assert first_call_args["timeline_index"] == 0
    assert first_call_args["start_time"] == 1.0
    assert first_call_args["end_time"] == 1.5
    assert first_call_args["color"] == [255, 0, 0]