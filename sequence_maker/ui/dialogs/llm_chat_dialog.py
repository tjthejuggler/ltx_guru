"""
Sequence Maker - LLM Chat Dialog

This module defines the LLMChatDialog class, which provides an interface for interacting with LLMs.
"""

import logging
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QProgressBar, QMessageBox,
    QSplitter, QWidget, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor

from api.app_context_api import AppContextAPI
from ui.dialogs.ambiguity_resolution_dialog import AmbiguityResolutionDialog


class LLMChatDialog(QDialog):
    """Dialog for interacting with LLMs."""
    
    def __init__(self, app, parent=None):
        """
        Initialize the LLM chat dialog.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.LLMChatDialog")
        self.app = app
        
        # Set dialog properties
        self.setWindowTitle("LLM Chat")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Create APIs
        self.context_api = AppContextAPI(app)
        
        # Chat properties
        self.chat_history = []
        
        # Create UI
        self._create_ui()
        
        # Check if LLM is configured
        self._check_llm_configuration()
        
        # Load chat history from project
        self._load_chat_history()
        
        # Connect signals
        self.app.llm_manager.token_usage_updated.connect(self._on_token_usage_updated)
        self.app.llm_manager.llm_ambiguity.connect(self._on_llm_ambiguity)
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create header layout
        self.header_layout = QHBoxLayout()
        self.main_layout.addLayout(self.header_layout)
        
        # Create title label
        self.title_label = QLabel("LLM Chat")
        self.title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.header_layout.addWidget(self.title_label)
        
        self.header_layout.addStretch()
        
        # Create model selection
        self.model_label = QLabel("Model:")
        self.header_layout.addWidget(self.model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.addItem("Default")
        self.header_layout.addWidget(self.model_combo)
        
        # Add confirmation mode selection
        self.confirmation_mode_label = QLabel("Confirmation Mode:")
        self.header_layout.addWidget(self.confirmation_mode_label)
        
        self.confirmation_mode_combo = QComboBox()
        self.confirmation_mode_combo.addItem("Full Confirmation", "full")
        self.confirmation_mode_combo.addItem("Selective Confirmation", "selective")
        self.confirmation_mode_combo.addItem("Full Automation", "auto")
        self.confirmation_mode_combo.setCurrentIndex(0)  # Default to full confirmation
        self.header_layout.addWidget(self.confirmation_mode_combo)
        
        # Add token usage display
        self.token_usage_label = QLabel("Tokens: 0 (Cost: $0.00)")
        self.header_layout.addWidget(self.token_usage_label)
        
        # Create splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter, 1)
        
        # Create timeline list
        self.timeline_widget = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_widget)
        
        self.timeline_label = QLabel("Timelines")
        self.timeline_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.timeline_layout.addWidget(self.timeline_label)
        
        self.timeline_list = QListWidget()
        self.timeline_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.timeline_layout.addWidget(self.timeline_list)
        
        self.splitter.addWidget(self.timeline_widget)
        
        # Create chat widget
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        
        self.chat_history_label = QLabel("Chat History")
        self.chat_history_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.chat_layout.addWidget(self.chat_history_label)
        
        self.chat_history_text = QTextEdit()
        self.chat_history_text.setReadOnly(True)
        self.chat_layout.addWidget(self.chat_history_text)
        
        self.input_layout = QHBoxLayout()
        self.chat_layout.addLayout(self.input_layout)
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Type your message here...")
        self.input_text.setMaximumHeight(100)
        self.input_layout.addWidget(self.input_text)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._on_send_clicked)
        self.input_layout.addWidget(self.send_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.input_layout.addWidget(self.stop_button)
        
        self.splitter.addWidget(self.chat_widget)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        self.main_layout.addWidget(self.progress_bar)
        
        # Create button layout
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        
        self.button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.button_layout.addWidget(self.close_button)
        
        # Set splitter sizes
        self.splitter.setSizes([200, 600])
        
        # Populate timeline list
        self._populate_timeline_list()
    
    def _populate_timeline_list(self):
        """Populate the timeline list."""
        # Clear list
        self.timeline_list.clear()
        
        # Check if project is loaded
        if not self.app.project_manager.current_project:
            return
        
        # Add each timeline
        for i, timeline in enumerate(self.app.project_manager.current_project.timelines):
            item = QListWidgetItem(f"Ball {i+1}: {timeline.name}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.timeline_list.addItem(item)
    
    def _load_chat_history(self):
        """Load chat history from the current project."""
        if self.app.project_manager.current_project and hasattr(self.app.project_manager.current_project, "chat_history"):
            # Convert the project's chat history format to our format
            project_history = self.app.project_manager.current_project.chat_history
            
            # Clear current chat history
            self.chat_history = []
            
            # Add each message from the project
            for message in project_history:
                sender = message.get("sender", "Unknown")
                text = message.get("message", "")
                self.chat_history.append((sender, text))
            
            # Update the chat history display
            self._update_chat_history()
    
    def _save_chat_history(self):
        """Save chat history to the current project."""
        if self.app.project_manager.current_project:
            # Convert our chat history format to the project's format
            project_history = []
            
            for sender, message in self.chat_history:
                project_history.append({
                    "sender": sender,
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Update the project's chat history
            self.app.project_manager.current_project.chat_history = project_history
            
            # Mark the project as changed
            self.app.project_manager.project_changed.emit()
    
    def _on_token_usage_updated(self, tokens, cost):
        """
        Handle token usage update.
        
        Args:
            tokens (int): Number of tokens used.
            cost (float): Estimated cost.
        """
        self.token_usage_label.setText(f"Tokens: {tokens} (Cost: ${cost:.2f})")
    
    def _on_stop_clicked(self):
        """Handle Stop button click."""
        # Interrupt the LLM request
        if self.app.llm_manager.interrupt():
            self.logger.info("LLM request interrupted by user")
            
            # Disable stop button
            self.stop_button.setEnabled(False)
            
            # Hide progress bar
            self.progress_bar.setVisible(False)
            
            # Enable input
            self.input_text.setEnabled(True)
            self.send_button.setEnabled(True)
    
    def _check_llm_configuration(self):
        """Check if LLM is configured."""
        if not self.app.llm_manager.is_configured():
            # Show warning
            QMessageBox.warning(
                self,
                "LLM Not Configured",
                "The LLM integration is not properly configured. "
                "Please configure it in the settings dialog."
            )
            
            # Disable input
            self.input_text.setEnabled(False)
            self.send_button.setEnabled(False)
    
    def _on_send_clicked(self):
        """Handle Send button click."""
        # Get message
        message = self.input_text.toPlainText().strip()
        
        # Check if message is empty
        if not message:
            return
        
        # Add message to chat history
        self._add_message("You", message)
        
        # Clear input
        self.input_text.clear()
        
        # Get selected timelines
        selected_timelines = []
        for item in self.timeline_list.selectedItems():
            timeline_index = item.data(Qt.ItemDataRole.UserRole)
            selected_timelines.append(timeline_index)
        
        # Create system message
        system_message = self._create_system_message(selected_timelines)
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        
        # Disable input and enable stop button
        self.input_text.setEnabled(False)
        self.send_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # Connect signals
        self.app.llm_manager.llm_response_received.connect(self._on_llm_response)
        self.app.llm_manager.llm_error.connect(self._on_llm_error)
        self.app.llm_manager.llm_ready.connect(self._on_llm_ready)
        
        # Get confirmation mode
        confirmation_mode = self.confirmation_mode_combo.currentData()
        
        # Send request to LLM
        self.app.llm_manager.send_request(message, system_message, confirmation_mode=confirmation_mode)
    
    def _create_system_message(self, selected_timelines):
        """
        Create a system message for the LLM.
        
        Args:
            selected_timelines (list): List of selected timeline indices.
        
        Returns:
            str: System message.
        """
        # Create base system message
        system_message = (
            "You are an assistant that helps create color sequences for juggling balls. "
            "You can analyze music and suggest color patterns that match the rhythm, mood, and style of the music. "
            "You can directly manipulate timelines, create segments, and change colors based on user instructions. "
            "Your responses should be clear and specific, describing exact colors and timings."
        )
        
        # Get application context
        app_context = self.context_api.get_full_context()
        
        # Add information about the project
        if self.app.project_manager.current_project:
            project = self.app.project_manager.current_project
            
            system_message += f"\n\nCurrent project: {project.name}"
            system_message += f"\nTotal duration: {project.total_duration} seconds"
            system_message += f"\nDefault pixels: {project.default_pixels}"
            system_message += f"\nRefresh rate: {project.refresh_rate} Hz"
            
            # Add information about timelines
            system_message += "\n\nTimelines:"
            for i, timeline in enumerate(project.timelines):
                system_message += f"\n- Ball {i+1}: {timeline.name}"
                if i in selected_timelines:
                    system_message += " (selected)"
                
                # Add segment information for selected timelines
                if i in selected_timelines and timeline.segments:
                    system_message += "\n  Segments:"
                    for j, segment in enumerate(timeline.segments):
                        system_message += f"\n  - Segment {j}: {segment.start_time}s to {segment.end_time}s, Color: {segment.color}"
        
        # Add information about audio
        if self.app.audio_manager.audio_file:
            system_message += f"\n\nAudio file: {os.path.basename(self.app.audio_manager.audio_file)}"
            system_message += f"\nAudio duration: {self.app.audio_manager.duration} seconds"
            
            # Add information about beats if available
            if self.app.audio_manager.beat_times is not None:
                beat_count = len(self.app.audio_manager.beat_times)
                system_message += f"\nDetected beats: {beat_count}"
                
                # Add some beat times as examples
                if beat_count > 0:
                    system_message += "\nBeat times (seconds): "
                    beat_times = self.app.audio_manager.beat_times[:10]  # First 10 beats
                    system_message += ", ".join(f"{time:.2f}" for time in beat_times)
                    if beat_count > 10:
                        system_message += f", ... (and {beat_count - 10} more)"
        
        # Add instructions for response format
        system_message += (
            "\n\nWhen suggesting color sequences, please provide specific timestamps and RGB colors. "
            "You can use the following format:\n"
            "```json\n"
            "{\n"
            '  "sequence": {\n'
            '    "0": {"color": [255, 0, 0]},\n'
            '    "5.2": {"color": [0, 255, 0]},\n'
            '    "10.8": {"color": [0, 0, 255]}\n'
            "  }\n"
            "}\n"
            "```\n"
            "Or you can describe the sequence in plain text, like:\n"
            "- At 0 seconds: Red (255, 0, 0)\n"
            "- At 5.2 seconds: Green (0, 255, 0)\n"
            "- At 10.8 seconds: Blue (0, 0, 255)"
        )
        
        return system_message
    
    def _add_message(self, sender, message):
        """
        Add a message to the chat history.
        
        Args:
            sender (str): Message sender.
            message (str): Message text.
        """
        # Add to chat history
        self.chat_history.append((sender, message))
        
        # Update chat history text
        self._update_chat_history()
        
        # Save chat history to project
        self._save_chat_history()
    
    def _update_chat_history(self):
        """Update the chat history text."""
        # Clear text
        self.chat_history_text.clear()
        
        # Add each message
        for sender, message in self.chat_history:
            # Set text color based on sender
            if sender == "You":
                self.chat_history_text.setTextColor(QColor(0, 0, 255))  # Blue
            else:
                self.chat_history_text.setTextColor(QColor(0, 128, 0))  # Green
            
            # Add sender
            self.chat_history_text.append(f"{sender}:")
            
            # Reset text color
            self.chat_history_text.setTextColor(QColor(0, 0, 0))  # Black
            
            # Add message
            self.chat_history_text.append(message)
            self.chat_history_text.append("")  # Empty line
        
        # Scroll to bottom
        self.chat_history_text.verticalScrollBar().setValue(
            self.chat_history_text.verticalScrollBar().maximum()
        )
    
    def _on_llm_response(self, response_text, response_data):
        """
        Handle LLM response.
        
        Args:
            response_text (str): Response text.
            response_data (dict): Response data.
        """
        # Disconnect signals
        self.app.llm_manager.llm_response_received.disconnect(self._on_llm_response)
        self.app.llm_manager.llm_error.disconnect(self._on_llm_error)
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Disable stop button
        self.stop_button.setEnabled(False)
        
        # Enable input
        self.input_text.setEnabled(True)
        self.send_button.setEnabled(True)
        
        # Add response to chat history
        self._add_message("Assistant", response_text)
        
        # Get confirmation mode
        confirmation_mode = self.confirmation_mode_combo.currentData()
        
        # Parse color sequence (legacy support)
        sequence = self.app.llm_manager.parse_color_sequence(response_text)
        
        # Check if sequence was parsed
        if sequence:
            # Get selected timelines
            selected_timelines = []
            for item in self.timeline_list.selectedItems():
                timeline_index = item.data(Qt.ItemDataRole.UserRole)
                selected_timelines.append(timeline_index)
            
            # If no timelines selected, use the first one
            if not selected_timelines and self.app.project_manager.current_project:
                if len(self.app.project_manager.current_project.timelines) > 0:
                    selected_timelines = [0]
            
            # Check confirmation mode
            if confirmation_mode == "full" or confirmation_mode == "selective":
                # Ask if user wants to apply the sequence
                if selected_timelines:
                    result = QMessageBox.question(
                        self,
                        "Apply Sequence",
                        f"Do you want to apply the suggested sequence to the selected timeline(s)?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if result == QMessageBox.StandardButton.Yes:
                        # Apply sequence to each selected timeline
                        for timeline_index in selected_timelines:
                            self.app.llm_manager.apply_sequence_to_timeline(sequence, timeline_index)
                        
                        # Show success message
                        QMessageBox.information(
                            self,
                            "Sequence Applied",
                            f"The sequence has been applied to {len(selected_timelines)} timeline(s)."
                        )
            else:  # Auto mode
                # Apply sequence to each selected timeline automatically
                for timeline_index in selected_timelines:
                    self.app.llm_manager.apply_sequence_to_timeline(sequence, timeline_index)
                
                # Add info message to chat
                self._add_message("System", f"Sequence automatically applied to {len(selected_timelines)} timeline(s).")
    
    def _on_llm_ready(self):
        """Handle LLM ready signal."""
        # Disconnect signal
        self.app.llm_manager.llm_ready.disconnect(self._on_llm_ready)
    
    def _on_llm_error(self, error_message):
        """
        Handle LLM error.
        
        Args:
            error_message (str): Error message.
        """
        # Disconnect signals
        self.app.llm_manager.llm_response_received.disconnect(self._on_llm_response)
        self.app.llm_manager.llm_error.disconnect(self._on_llm_error)
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Disable stop button
        self.stop_button.setEnabled(False)
        
        # Enable input
        self.input_text.setEnabled(True)
        self.send_button.setEnabled(True)
        
        # Show error message
        QMessageBox.warning(
            self,
            "LLM Error",
            f"An error occurred while communicating with the LLM:\n{error_message}"
        )
    
    def _on_llm_ambiguity(self, prompt, suggestions):
        """
        Handle LLM ambiguity.
        
        Args:
            prompt (str): The original prompt.
            suggestions (list): List of suggested clarifications.
        """
        self.logger.info(f"Handling ambiguity for prompt: {prompt}")
        self.logger.info(f"Suggestions: {suggestions}")
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Disable stop button
        self.stop_button.setEnabled(False)
        
        # Create and show ambiguity resolution dialog
        dialog = AmbiguityResolutionDialog(prompt, suggestions, self)
        
        # Connect resolution signal
        dialog.resolution_selected.connect(self._on_ambiguity_resolved)
        
        # Show dialog
        dialog.exec()
    
    def _on_ambiguity_resolved(self, resolution):
        """
        Handle ambiguity resolution.
        
        Args:
            resolution (str): The selected or custom resolution.
        """
        self.logger.info(f"Ambiguity resolved with: {resolution}")
        
        # Add resolution to chat history
        self._add_message("You (clarification)", resolution)
        
        # Enable input
        self.input_text.setEnabled(True)
        self.send_button.setEnabled(True)
        
        # Get system message
        selected_timelines = []
        for item in self.timeline_list.selectedItems():
            timeline_index = item.data(Qt.ItemDataRole.UserRole)
            selected_timelines.append(timeline_index)
        
        system_message = self._create_system_message(selected_timelines)
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        
        # Disable input and enable stop button
        self.input_text.setEnabled(False)
        self.send_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # Connect signals
        self.app.llm_manager.llm_response_received.connect(self._on_llm_response)
        self.app.llm_manager.llm_error.connect(self._on_llm_error)
        self.app.llm_manager.llm_ready.connect(self._on_llm_ready)
        
        # Get confirmation mode
        confirmation_mode = self.confirmation_mode_combo.currentData()
        
        # Send clarification to LLM
        self.app.llm_manager.send_request(resolution, system_message, confirmation_mode=confirmation_mode)