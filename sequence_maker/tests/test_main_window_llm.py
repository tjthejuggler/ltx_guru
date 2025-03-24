"""
Sequence Maker - Tests for LLM integration in Main Window

This module contains tests for the LLM chat window integration in the main window.
"""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import Qt


def test_llm_chat_window_creation(qtbot, app_fixture, main_window_fixture):
    """
    Test that the LLM chat window is created correctly.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app fixture
        main_window_fixture: The main window fixture
    """
    # Check that the LLM chat window was created
    assert main_window_fixture.llm_chat_window is not None
    
    # Check that it's hidden by default
    assert main_window_fixture.llm_chat_window.isHidden()


def test_llm_chat_action_shows_window(qtbot, app_fixture, main_window_fixture):
    """
    Test that the LLM chat action shows the window.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app fixture
        main_window_fixture: The main window fixture
    """
    # Ensure window is hidden
    main_window_fixture.llm_chat_window.hide()
    
    # Trigger the LLM chat action
    main_window_fixture._on_llm_chat()
    
    # Check that the window is now visible
    assert main_window_fixture.llm_chat_window.isVisible()


def test_llm_chat_action_raises_existing_window(qtbot, app_fixture, main_window_fixture, mocker):
    """
    Test that the LLM chat action raises an existing window.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app fixture
        main_window_fixture: The main window fixture
        mocker: The pytest-mock fixture
    """
    # Show the window
    main_window_fixture.llm_chat_window.show()
    
    # Mock the raise_ and activateWindow methods
    mocker.patch.object(main_window_fixture.llm_chat_window, 'raise_')
    mocker.patch.object(main_window_fixture.llm_chat_window, 'activateWindow')
    
    # Trigger the LLM chat action
    main_window_fixture._on_llm_chat()
    
    # Check that raise_ and activateWindow were called
    main_window_fixture.llm_chat_window.raise_.assert_called_once()
    main_window_fixture.llm_chat_window.activateWindow.assert_called_once()


def test_llm_chat_toolbar_button(qtbot, app_fixture, main_window_fixture, mocker):
    """
    Test that the LLM chat toolbar button works correctly.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app fixture
        main_window_fixture: The main window fixture
        mocker: The pytest-mock fixture
    """
    # Mock the _on_llm_chat method
    mocker.patch.object(main_window_fixture, '_on_llm_chat')
    
    # Click the toolbar button
    qtbot.mouseClick(main_window_fixture.llm_chat_toolbar_button, Qt.MouseButton.LeftButton)
    
    # Check that _on_llm_chat was called
    main_window_fixture._on_llm_chat.assert_called_once()