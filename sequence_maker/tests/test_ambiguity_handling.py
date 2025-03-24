"""
Sequence Maker - Tests for Ambiguity Handling

This module contains tests for the ambiguity handling functionality.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QObject, pyqtSignal

# Add the parent directory to the path so we can import the sequence_maker modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from managers.llm_manager import LLMManager


class TestLLMManager:
    """Tests for the LLMManager class."""
    
    @pytest.fixture
    def app_mock(self):
        """Create a mock app object."""
        app = MagicMock()
        app.config.get.return_value = "test"
        return app
    
    @pytest.fixture
    def llm_manager(self, app_mock):
        """Create an LLMManager instance."""
        manager = LLMManager(app_mock)
        # Mock the logger to avoid actual logging
        manager.logger = MagicMock()
        return manager
    
    def test_handle_ambiguity_detection(self, llm_manager):
        """Test that ambiguity is correctly detected in responses."""
        # Create a signal spy to capture emitted signals
        ambiguity_spy = MagicMock()
        llm_manager.llm_ambiguity.connect(ambiguity_spy)
        
        # Test with ambiguous response
        prompt = "Create a sequence for the music"
        ambiguous_response = "Your request is ambiguous. I'm not sure if you want:\n1. A color sequence\n2. A timing sequence\nPlease clarify."
        
        # Call the method
        result = llm_manager._handle_ambiguity(prompt, ambiguous_response)
        
        # Check that ambiguity was detected
        assert result is True
        
        # Check that the signal was emitted with correct arguments
        ambiguity_spy.assert_called_once()
        args = ambiguity_spy.call_args[0]
        assert args[0] == prompt  # First arg should be the prompt
        assert isinstance(args[1], list)  # Second arg should be a list of suggestions
        assert len(args[1]) > 0  # Should have at least one suggestion
        
        # Reset the mock
        ambiguity_spy.reset_mock()
        
        # Test with non-ambiguous response
        clear_response = "I'll create a color sequence for you with red, green, and blue."
        
        # Call the method
        result = llm_manager._handle_ambiguity(prompt, clear_response)
        
        # Check that ambiguity was not detected
        assert result is False
        
        # Check that the signal was not emitted
        ambiguity_spy.assert_not_called()
    
    def test_extract_suggestions(self, llm_manager):
        """Test that suggestions are correctly extracted from ambiguous responses."""
        # Test with numbered list
        numbered_response = "Your request is ambiguous. I'm not sure if you want:\n1. A color sequence\n2. A timing sequence\nPlease clarify."
        suggestions = llm_manager._extract_suggestions(numbered_response)
        assert len(suggestions) == 2
        assert "A color sequence" in suggestions
        assert "A timing sequence" in suggestions
        
        # Test with bulleted list
        bulleted_response = "Your request is ambiguous. I'm not sure if you want:\n- A color sequence\n- A timing sequence\nPlease clarify."
        suggestions = llm_manager._extract_suggestions(bulleted_response)
        assert len(suggestions) == 2
        assert "A color sequence" in suggestions
        assert "A timing sequence" in suggestions
        
        # Test with mixed list
        mixed_response = "Your request is ambiguous. I'm not sure if you want:\n1. A color sequence\n- A timing sequence\nPlease clarify."
        suggestions = llm_manager._extract_suggestions(mixed_response)
        assert len(suggestions) == 2
        assert "A color sequence" in suggestions
        assert "A timing sequence" in suggestions
        
        # Test with no list
        no_list_response = "Your request is ambiguous. Please provide more details."
        suggestions = llm_manager._extract_suggestions(no_list_response)
        assert len(suggestions) == 1
        assert "Please provide more specific instructions." in suggestions


class TestAmbiguityResolutionDialog:
    """Tests for the AmbiguityResolutionDialog class."""
    
    @pytest.fixture
    def dialog(self, qtbot):
        """Create an AmbiguityResolutionDialog instance."""
        from ui.dialogs.ambiguity_resolution_dialog import AmbiguityResolutionDialog
        
        prompt = "Create a sequence for the music"
        suggestions = ["A color sequence", "A timing sequence"]
        dialog = AmbiguityResolutionDialog(prompt, suggestions)
        qtbot.addWidget(dialog)
        return dialog
    
    def test_dialog_initialization(self, dialog):
        """Test that the dialog is correctly initialized."""
        # Check that the dialog has the correct title
        assert dialog.windowTitle() == "Clarify Instructions"
        
        # Check that the prompt is displayed
        assert dialog.prompt_text.toPlainText() == "Create a sequence for the music"
        
        # Check that the suggestions are displayed
        assert dialog.suggestions_list.count() == 2
        assert dialog.suggestions_list.item(0).text() == "A color sequence"
        assert dialog.suggestions_list.item(1).text() == "A timing sequence"
    
    def test_select_suggestion(self, dialog, qtbot):
        """Test selecting a suggestion."""
        # Create a signal spy to capture emitted signals
        resolution_spy = MagicMock()
        dialog.resolution_selected.connect(resolution_spy)
        
        # Select the first suggestion
        dialog.suggestions_list.setCurrentRow(0)
        
        # Click the select button
        qtbot.mouseClick(dialog.select_button, Qt.MouseButton.LeftButton)
        
        # Check that the signal was emitted with the correct argument
        resolution_spy.assert_called_once_with("A color sequence")
        
        # Check that the dialog was accepted
        assert dialog.result() == QDialog.DialogCode.Accepted
    
    def test_custom_clarification(self, dialog, qtbot):
        """Test providing a custom clarification."""
        # Create a signal spy to capture emitted signals
        resolution_spy = MagicMock()
        dialog.resolution_selected.connect(resolution_spy)
        
        # Enter a custom clarification
        dialog.custom_text.setPlainText("I want a color sequence that changes with the beat")
        
        # Click the custom button
        qtbot.mouseClick(dialog.custom_button, Qt.MouseButton.LeftButton)
        
        # Check that the signal was emitted with the correct argument
        resolution_spy.assert_called_once_with("I want a color sequence that changes with the beat")
        
        # Check that the dialog was accepted
        assert dialog.result() == QDialog.DialogCode.Accepted


class TestLLMChatDialog:
    """Tests for the LLMChatDialog integration with ambiguity handling."""
    
    @pytest.fixture
    def app_mock(self):
        """Create a mock app object."""
        app = MagicMock()
        app.config.get.return_value = "test"
        app.llm_manager = MagicMock()
        app.project_manager = MagicMock()
        app.project_manager.current_project = None
        app.audio_manager = MagicMock()
        app.audio_manager.audio_file = None
        return app
    
    @pytest.fixture
    def dialog(self, qtbot, app_mock):
        """Create an LLMChatDialog instance."""
        from ui.dialogs.llm_chat_dialog import LLMChatDialog
        
        # Patch the AppContextAPI to avoid actual API calls
        with patch('ui.dialogs.llm_chat_dialog.AppContextAPI'):
            dialog = LLMChatDialog(app_mock)
            qtbot.addWidget(dialog)
            return dialog
    
    def test_ambiguity_handling(self, dialog, qtbot, monkeypatch):
        """Test that ambiguity is correctly handled."""
        # Mock the AmbiguityResolutionDialog
        ambiguity_dialog_mock = MagicMock()
        ambiguity_dialog_mock.exec.return_value = QDialog.DialogCode.Accepted
        
        # Create a resolution signal that can be connected to
        class ResolutionSignal(QObject):
            signal = pyqtSignal(str)
        resolution_signal = ResolutionSignal()
        
        # Set up the mock to return the signal
        ambiguity_dialog_mock.resolution_selected = resolution_signal.signal
        
        # Patch the AmbiguityResolutionDialog constructor to return our mock
        monkeypatch.setattr('ui.dialogs.llm_chat_dialog.AmbiguityResolutionDialog', lambda *args, **kwargs: ambiguity_dialog_mock)
        
        # Call the ambiguity handler
        prompt = "Create a sequence for the music"
        suggestions = ["A color sequence", "A timing sequence"]
        dialog._on_llm_ambiguity(prompt, suggestions)
        
        # Check that the dialog was created with the correct arguments
        ambiguity_dialog_mock.exec.assert_called_once()
        
        # Simulate resolution selection
        resolution = "I want a color sequence that changes with the beat"
        resolution_signal.signal.emit(resolution)
        
        # Check that the resolution was added to the chat history
        assert any("You (clarification)" in sender and resolution in message for sender, message in dialog.chat_history)
        
        # Check that a new request was sent to the LLM
        dialog.app.llm_manager.send_request.assert_called_once()
        assert dialog.app.llm_manager.send_request.call_args[0][0] == resolution