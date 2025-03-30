"""
Sequence Maker - LLM Chat Window

This module defines the LLMChatWindow class, which provides a floating interface for interacting with LLMs.
"""

import logging
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QProgressBar, QMessageBox,
    QSplitter, QListWidget, QListWidgetItem, QGroupBox,
    QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor

from api.app_context_api import AppContextAPI
from ui.dialogs.ambiguity_resolution_dialog import AmbiguityResolutionDialog


class LLMChatWindow(QWidget):
    """Floating window for interacting with LLMs."""
    
    def __init__(self, app, parent=None):
        """
        Initialize the LLM chat window.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.LLMChatWindow")
        self.app = app
        
        # Set window properties
        self.setWindowTitle("LLM Chat")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.Tool)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        # Create APIs
        self.context_api = AppContextAPI(app)
        
        # Chat properties
        self.chat_history = []
        self.current_streaming_response = ""
        
        # Create UI
        self._create_ui()
        
        # Check if LLM is configured
        self._check_llm_configuration()
        
        # Load chat history from project
        self._load_chat_history()
        
        # Connect signals
        self.app.llm_manager.token_usage_updated.connect(self._on_token_usage_updated)
        self.app.llm_manager.llm_ambiguity.connect(self._on_llm_ambiguity)
        self.app.llm_manager.llm_response_chunk.connect(self._on_response_chunk)
        self.app.llm_manager.llm_function_called.connect(self._on_function_called)
    
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
        
        # Create profile selection
        self.preset_label = QLabel("LLM Profile:")
        self.preset_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.header_layout.addWidget(self.preset_label)
        
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(200)  # Make the dropdown wider
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        self.header_layout.addWidget(self.preset_combo)
        
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
        
        # Add feedback UI elements
        self.feedback_group = QGroupBox("Feedback")
        self.feedback_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.feedback_layout = QVBoxLayout(self.feedback_group)
        
        # Add feedback text field
        self.feedback_text = QTextEdit()
        self.feedback_text.setPlaceholderText("Enter your feedback about the generated sequence...")
        self.feedback_text.setMaximumHeight(60)
        self.feedback_layout.addWidget(self.feedback_text)
        
        # Add sentiment buttons
        self.sentiment_layout = QHBoxLayout()
        self.feedback_layout.addLayout(self.sentiment_layout)
        
        # Create button group for sentiment
        self.sentiment_group = QButtonGroup(self)
        
        # Like button
        self.like_button = QRadioButton("Like")
        self.sentiment_group.addButton(self.like_button, 1)  # 1 for positive sentiment
        self.sentiment_layout.addWidget(self.like_button)
        
        # Neutral button
        self.neutral_button = QRadioButton("Neutral")
        self.sentiment_group.addButton(self.neutral_button, 0)  # 0 for neutral sentiment
        self.sentiment_layout.addWidget(self.neutral_button)
        
        # Dislike button
        self.dislike_button = QRadioButton("Dislike")
        self.sentiment_group.addButton(self.dislike_button, -1)  # -1 for negative sentiment
        self.sentiment_layout.addWidget(self.dislike_button)
        
        self.sentiment_layout.addStretch()
        
        # Add submit button
        self.submit_feedback_button = QPushButton("Submit Feedback")
        self.submit_feedback_button.clicked.connect(self._submit_feedback)
        self.sentiment_layout.addWidget(self.submit_feedback_button)
        
        # Add feedback group to chat layout
        self.chat_layout.addWidget(self.feedback_group)
        
        # Add template selection
        self.template_layout = QHBoxLayout()
        self.chat_layout.addLayout(self.template_layout)
        
        self.template_label = QLabel("Template:")
        self.template_layout.addWidget(self.template_label)
        
        self.template_combo = QComboBox()
        self.template_combo.addItem("None")
        self.template_combo.currentIndexChanged.connect(self._on_template_changed)
        self.template_layout.addWidget(self.template_combo)
        
        self.template_layout.addStretch()
        
        # Add custom instructions button
        self.custom_instructions_button = QPushButton("Custom Instructions")
        self.custom_instructions_button.clicked.connect(self._on_custom_instructions)
        self.template_layout.addWidget(self.custom_instructions_button)
        
        # Add input layout
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
        
        # Add Clear Chat button
        self.clear_chat_button = QPushButton("Clear Chat")
        self.clear_chat_button.clicked.connect(self._on_clear_chat_clicked)
        self.button_layout.addWidget(self.clear_chat_button)
        
        # Add Clear All Timelines button
        self.clear_all_timelines_button = QPushButton("Clear All Timelines")
        self.clear_all_timelines_button.clicked.connect(self._on_clear_all_timelines_clicked)
        self.button_layout.addWidget(self.clear_all_timelines_button)
        
        # Add minimize button
        self.minimize_button = QPushButton("Minimize")
        self.minimize_button.clicked.connect(self.hide)
        self.button_layout.addWidget(self.minimize_button)
        
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
            
            # Load templates
            self._load_templates()
    
    def _load_presets(self):
        """Load LLM profiles from the LLM manager."""
        # Clear preset combo
        self.preset_combo.clear()
        
        # Get profiles from LLM manager
        profiles = self.app.llm_manager.get_profiles()
        active_profile = self.app.llm_manager.get_active_profile()
        
        # Add each profile to the combo
        for profile_id, profile in profiles.items():
            profile_name = profile.get("name", profile_id)
            provider = profile.get("provider", "").capitalize()
            model = profile.get("model", "")
            
            display_text = f"{profile_name} ({provider} - {model})"
            self.preset_combo.addItem(display_text, profile_id)
        
        # Set current index to active profile
        for i in range(self.preset_combo.count()):
            if self.preset_combo.itemData(i) == active_profile:
                self.preset_combo.setCurrentIndex(i)
                break
    
    def _load_templates(self):
        """Load LLM task templates from the current project."""
        if self.app.project_manager.current_project:
            # Clear template combo
            self.template_combo.clear()
            
            # Add "None" option
            self.template_combo.addItem("None")
            
            # Get templates from project
            templates_data = getattr(self.app.project_manager.current_project, "llm_task_templates", [])
            
            # Add templates to combo box
            for template_data in templates_data:
                name = template_data.get("name", "Unnamed")
                self.template_combo.addItem(name)
    
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
    
    def _on_preset_changed(self, index):
        """
        Handle profile selection change.
        
        Args:
            index (int): Selected index.
        """
        if index >= 0 and self.preset_combo.count() > 0:
            profile_id = self.preset_combo.itemData(index)
            profile_name = self.preset_combo.itemText(index)
            self.logger.info(f"Selected profile: {profile_name} (ID: {profile_id})")
            
            # Set active profile in LLM manager
            if profile_id:
                self.app.llm_manager.set_active_profile(profile_id)
    
    def _on_template_changed(self, index):
        """
        Handle template selection change.
        
        Args:
            index (int): Selected index.
        """
        if index > 0 and self.template_combo.count() > 0:  # Skip "None" option
            template_name = self.template_combo.itemText(index)
            self.logger.info(f"Selected template: {template_name}")
            
            # Find template
            if self.app.project_manager.current_project:
                templates_data = getattr(self.app.project_manager.current_project, "llm_task_templates", [])
                
                for template_data in templates_data:
                    if template_data.get("name") == template_name:
                        # Set prompt in input field
                        self.input_text.setText(template_data.get("prompt", ""))
                        break
    
    def _on_custom_instructions(self):
        """Handle Custom Instructions button click."""
        from ui.dialogs.custom_instructions_dialog import CustomInstructionsDialog
        
        # Create and show dialog
        dialog = CustomInstructionsDialog(self.app, self)
        dialog.exec()
    
    def _check_llm_configuration(self):
        """Check if LLM is configured."""
        # Load profiles
        self._load_presets()
        
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
        else:
            # Enable input if LLM is configured
            self.input_text.setEnabled(True)
            self.send_button.setEnabled(True)
    
    def _on_response_chunk(self, chunk):
        """
        Handle a chunk of streaming response.
        
        Args:
            chunk (str): Response chunk.
        """
        # Append chunk to current response
        self.current_streaming_response += chunk
        
        # Update chat history text
        if len(self.chat_history) > 0 and self.chat_history[-1][0] == "Assistant (streaming)":
            # Update existing streaming message
            self.chat_history[-1] = ("Assistant (streaming)", self.current_streaming_response)
        else:
            # Add new streaming message
            self.chat_history.append(("Assistant (streaming)", self.current_streaming_response))
        
        # Update display
        self._update_chat_history()
    
    def _on_function_called(self, function_name, arguments, result):
        """
        Handle a function call.
        
        Args:
            function_name (str): Name of the function.
            arguments (dict): Function arguments.
            result (dict): Result of the function call.
        """
        # Display function call
        self._display_function_call(function_name, arguments, result)
        
        # Add to chat history
        function_description = f"Function call: {function_name}\nArguments: {json.dumps(arguments, indent=2)}\nResult: {json.dumps(result, indent=2)}"
        self._add_message("System", function_description)
    
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
        
        # Reset streaming response
        self.current_streaming_response = ""
        
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
        
        # Determine if we should use streaming
        use_streaming = True  # Default to streaming for better user experience
        
        # Get preset parameters if a preset is selected
        temperature = None
        max_tokens = None
        
        if self.app.project_manager.current_project:
            preset_name = self.preset_combo.currentText()
            if preset_name != "Default":
                # Find preset in project
                presets_data = getattr(self.app.project_manager.current_project, "llm_presets", [])
                for preset_data in presets_data:
                    if preset_data.get("name") == preset_name:
                        # Get preset parameters
                        temperature = preset_data.get("temperature")
                        max_tokens = preset_data.get("max_tokens")
                        
                        # Update active preset in project
                        self.app.project_manager.current_project.llm_active_preset = preset_name
                        self.app.project_manager.project_changed.emit()
                        break
        
        # Send request to LLM
        self.app.llm_manager.send_request(
            prompt=message,
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens,
            use_functions=True,
            stream=use_streaming
        )
    
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
        
        # Add custom instructions if available
        if self.app.project_manager.current_project:
            custom_instructions = getattr(self.app.project_manager.current_project, "llm_custom_instructions", "")
            if custom_instructions:
                system_message += f"\n\nCustom Instructions:\n{custom_instructions}"
        
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
            system_message += f"\nTempo: {self.app.audio_manager.tempo} BPM" if self.app.audio_manager.tempo else ""
            
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
            
            # Add information about enhanced audio analysis if available
            
            # Onset strength (intensity of note onsets)
            if hasattr(self.app.audio_manager, "onset_strength") and self.app.audio_manager.onset_strength is not None:
                system_message += "\n\nEnhanced audio analysis:"
                system_message += "\n- Onset strength analysis available (indicates intensity of note onsets)"
            
            # Spectral contrast (difference between peaks and valleys in the spectrum)
            if hasattr(self.app.audio_manager, "spectral_contrast") and self.app.audio_manager.spectral_contrast is not None:
                system_message += "\n- Spectral contrast analysis available (indicates presence of harmonic vs. percussive elements)"
            
            # Spectral centroid (brightness of the sound)
            if hasattr(self.app.audio_manager, "spectral_centroid") and self.app.audio_manager.spectral_centroid is not None:
                system_message += "\n- Spectral centroid analysis available (indicates brightness/sharpness of the sound)"
            
            # Chroma features (representation of the 12 different pitch classes)
            if hasattr(self.app.audio_manager, "chroma") and self.app.audio_manager.chroma is not None:
                system_message += "\n- Chroma features available (indicates the distribution of pitch classes)"
            
            # RMS energy (volume over time)
            if hasattr(self.app.audio_manager, "rms_energy") and self.app.audio_manager.rms_energy is not None:
                system_message += "\n- RMS energy analysis available (indicates volume/intensity over time)"
            
            # Add musical interpretation guidance
            system_message += "\n\nWhen creating color sequences, you can use this audio analysis to:"
            system_message += "\n- Match color changes to beat times for rhythmic synchronization"
            system_message += "\n- Use brighter colors during high spectral centroid moments (bright/sharp sounds)"
            system_message += "\n- Use more intense colors during high energy moments"
            system_message += "\n- Create color patterns that follow the musical structure"
            system_message += "\n- Use color transitions that match the mood and intensity of the music"
        
        # Add instructions for response format
        system_message += (
            "\n\nWhen suggesting color sequences, please provide specific timestamps and RGB colors. "
            "If asked to generate a complex sequence, you can describe it using this JSON format:\n"
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
            "\n\nIMPORTANT: Only include color changes that are explicitly requested by the user. "
            "Do not add additional color changes at the end of segments or anywhere else unless "
            "specifically asked to do so. Your changes will be added to the existing timeline without "
            "removing what's already there."
            "\n\nIMPORTANT: For creating and modifying light sequences, you should primarily use the `execute_sequence_code` function, which allows you to run Python code in a secure sandbox. This is the preferred method for any sequence generation that involves loops, conditions, randomness, or multiple steps."
            "\n\nYou have access to the following high-level functions for direct actions:"
            "\n1. create_segment_for_word(word, color, balls) - Creates color segments on specified balls during occurrences of a specific word (use this ONLY for simple cases where ALL instances of a word need the SAME color)"
            "\n2. clear_all_timelines(set_black) - Clear all segments from all timelines (all balls)"
            "\n3. play_audio(), pause_audio(), stop_audio(), seek_audio(position) - Control audio playback"
            "\n\nWhen calling these direct functions, ensure you provide ALL required arguments as specified in their descriptions."
            "\n\nFor complex color sequences requiring loops, conditionals, or algorithmic patterns, "
            "use the execute_sequence_code tool to run Python code in a secure sandbox. "
            "This allows you to create intricate patterns that would be difficult with individual function calls. "
            "\n\nIMPORTANT: When using this tool, you MUST call it explicitly like this:"
            "\n```"
            "\nexecute_sequence_code(code=\"\"\""
            "\n# Your Python code here"
            "\nfor i, beat_time in enumerate(BEAT_TIMES):"
            "\n    # More code..."
            "\n\"\"\")"
            "\n```"
            "\nDo NOT just show Python code in your response without calling the tool. The code must be passed as a parameter to execute_sequence_code."
            "\n\nIMPORTANT: Do NOT use `import` statements in your sandbox code. All necessary functions and utilities are already provided."
            "\n\nExample of correct usage for creating a rainbow pattern:"
            "\n```"
            "\nexecute_sequence_code(code=\"\"\""
            "\n# Create a rainbow pattern across all beats"
            "\nfor i, beat_time in enumerate(BEAT_TIMES):"
            "\n    # Calculate hue based on position in beat sequence"
            "\n    hue = (i / len(BEAT_TIMES)) * 360"
            "\n    # Create segments for each ball with different hue offsets"
            "\n    for ball in range(NUM_BALLS):"
            "\n        offset_hue = (hue + (ball * 30)) % 360"
            "\n        ball_color = hsv_to_rgb(offset_hue, 1.0, 1.0)"
            "\n        create_segment(ball, beat_time, beat_time + 0.25, ball_color)"
            "\n\"\"\")"
            "\n```"
            "\nThe sandbox provides these functions:"
            "\n- create_segment(timeline_index, start_time, end_time, color): Creates a segment on the specified timeline"
            "\n- clear_timeline(timeline_index): Clears all segments from the specified timeline"
            "\n- modify_segment(timeline_index, segment_index, start_time, end_time, color): Modifies an existing segment"
            "\n- delete_segment(timeline_index, segment_index): Deletes a segment from the specified timeline"
            "\n- get_word_timestamps(word, start_time, end_time, limit): Gets timestamps for a specific word in the lyrics"
            "\n- get_all_word_timestamps(): Gets timestamps for ALL words in the lyrics (more efficient than calling get_word_timestamps repeatedly)"
            "\n- get_lyrics_info(): Gets general information about the current lyrics"
            "\n- find_first_word(): Finds the first word in the lyrics with its timestamp"
            "\n\nAnd these utilities:"
            "\n- random_color(): Generates a random RGB color"
            "\n- random_float(min_val, max_val): Generates a random float between min_val and max_val"
            "\n- random_randint(a, b): Generates a random integer between a and b (inclusive)"
            "\n- random_choice(seq): Randomly selects an item from a sequence"
            "\n- random_uniform(a, b): Generates a random float between a and b with uniform distribution"
            "\n- interpolate_color(color1, color2, factor): Interpolates between two colors"
            "\n- hsv_to_rgb(h, s, v): Converts HSV color to RGB"
            "\n- rgb_to_hsv(r, g, b): Converts RGB color to HSV"
            "\n- color_from_name(color_name): Converts a color name to RGB values"
            "\n- print(): Logs messages (for debugging)"
            "\n\nIt also provides these variables: BEAT_TIMES, NUM_BALLS, and SONG_DURATION."
            "\n\nIMPORTANT TOOL USAGE GUIDELINES:"
            "\n- Use create_segment_for_word ONLY when you need to make ALL instances of a SINGLE word the SAME color."
            "\n- Use clear_all_timelines() ONLY for clearing ALL timelines at once."
            "\n- Use execute_sequence_code for ALL other sequence creation or modification tasks, especially when you need to:"
            "\n  * Clear a single timeline (use clear_timeline(timeline_index) inside the sandbox)"
            "\n  * Apply DIFFERENT colors to different instances of a word"
            "\n  * Use loops, conditional logic, or generate colors algorithmically"
            "\n  * Create patterns based on beat times or other musical features"
            "\n  * Implement any complex sequence generation logic"
            "\n- Inside execute_sequence_code, use get_all_word_timestamps() to efficiently get ALL word timings at once, then filter as needed."
            "\n- When calling functions directly (not using the sandbox), ensure you provide all required arguments as specified in their descriptions."
            "\n- When a user asks for complex patterns, ALWAYS use the execute_sequence_code tool rather than trying to call functions directly in your response or showing Python code without executing it."
            "\n\nExample - Clearing only Ball 3 (index 2) using the sandbox:"
            "\n```"
            "\nexecute_sequence_code(code=\"clear_timeline(2)\")"
            "\n```"
            "\n\nExample for cycling through colors on word occurrences:"
            "\n```"
            "\nexecute_sequence_code(code=\"\"\""
            "\n# Cycle through colors for each occurrence of a specific word"
            "\n# Define colors to cycle through"
            "\ncolors = ["
            "\n    [255, 0, 0],    # Red"
            "\n    [0, 255, 0],    # Green"
            "\n    [0, 0, 255],    # Blue"
            "\n    [255, 255, 0],  # Yellow"
            "\n    [255, 0, 255],  # Magenta"
            "\n    [0, 255, 255]   # Cyan"
            "\n]"
            "\n"
            "\n# Define the word to search for"
            "\nword = 'love'  # Replace with the desired word"
            "\n"
            "\n# Get all timestamps for the word using the get_all_word_timestamps function"
            "\n# This is more efficient than calling get_word_timestamps repeatedly"
            "\nall_word_timestamps = get_all_word_timestamps()"
            "\n"
            "\n# Filter for the specific word we want"
            "\nword_timestamps = [wt for wt in all_word_timestamps if wt['word'].lower() == word.lower()]"
            "\n"
            "\n# Check if we found any occurrences of the word"
            "\nif not word_timestamps:"
            "\n    print(f\"No occurrences of '{word}' found in the lyrics\")"
            "\n"
            "\n# Create segments with cycling colors"
            "\nfor i, timestamp in enumerate(word_timestamps):"
            "\n    # Get color (cycle through colors)"
            "\n    color_index = i % len(colors)"
            "\n    color = colors[color_index]"
            "\n    "
            "\n    # Create segment on all balls"
            "\n    for ball in range(NUM_BALLS):"
            "\n        create_segment(ball, timestamp['start_time'], timestamp['end_time'], color)"
            "\n\"\"\")"
            "\n```"
            "\n\nWhen asked about lyrics or word timestamps, ALWAYS use these functions to get accurate data. "
            "For example, if asked 'what is the first word in the song?', use the find_first_word() function. "
            "If asked about specific words, use get_word_timestamps() with the word parameter."
            "\n\nIMPORTANT: When the user asks to create a color effect synchronized to a specific word (e.g., 'make the balls blue during the word \"love\"'), "
            "ALWAYS use the create_segment_for_word function. This function handles both finding the word's timing and creating the segments in a single operation. "
            "The color parameter can be either an RGB array [R,G,B] or a color name like 'blue'. "
            "The balls parameter can be 'all' to apply to all balls, or a list of ball indices like [0, 1] to apply to specific balls."
            "\n\nAfter each successful function call, you will receive a summary of the results (e.g., number of segments created, timelines cleared, etc.). "
            "You can use this information to provide more detailed responses to the user and to inform your next actions. "
            "For example, if you create segments for a word but the summary shows 0 segments were created, you might suggest trying a different word or approach."
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
    
    def _display_function_call(self, function_name, arguments, result):
        """
        Display a function call in the chat window.
        
        Args:
            function_name (str): Name of the function.
            arguments (dict): Function arguments.
            result (dict): Result of the function call.
        """
        # Create function call HTML
        html = f"""
        <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin: 5px 0;">
            <div style="font-weight: bold; color: #0066cc;">Function Call: {function_name.replace('_', ' ')}</div>
            <div style="margin: 5px 0; padding: 5px; background-color: #ffffff; border-radius: 3px;">
                <pre style="margin: 0; white-space: pre-wrap;">{json.dumps(arguments, indent=2)}</pre>
            </div>
            <div style="margin-top: 5px;">
                <div style="font-weight: bold; color: #009900;">Result:</div>
                <div style="padding: 5px; background-color: #ffffff; border-radius: 3px;">
                    <pre style="margin: 0; white-space: pre-wrap;">{json.dumps(result, indent=2)}</pre>
                </div>
            </div>
        </div>
        """
        
        # Add to chat history text
        self.chat_history_text.insertHtml(html)
        self.chat_history_text.append("")  # Empty line
        
        # Scroll to bottom
        self.chat_history_text.verticalScrollBar().setValue(
            self.chat_history_text.verticalScrollBar().maximum()
        )
    
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
            
            # Check if message contains thinking content
            if "[Thinking]" in message and "[/Thinking]" in message:
                # Split message into thinking and regular content
                parts = message.split("[/Thinking]", 1)
                thinking_part = parts[0] + "[/Thinking]"
                regular_part = parts[1].strip() if len(parts) > 1 else ""
                
                # Format thinking content with a different style
                self.chat_history_text.setTextColor(QColor(128, 128, 128))  # Gray
                self.chat_history_text.append(thinking_part)
                
                # Format regular content normally
                self.chat_history_text.setTextColor(QColor(0, 0, 0))  # Black
                if regular_part:
                    self.chat_history_text.append(regular_part)
            else:
                # Add message normally
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
        
        # If we were streaming, update the last message
        if len(self.chat_history) > 0 and self.chat_history[-1][0] == "Assistant (streaming)":
            # Replace streaming message with final message
            self.chat_history[-1] = ("Assistant", response_text)
            # Update display
            self._update_chat_history()
        else:
            # Add response to chat history
            self._add_message("Assistant", response_text)
        
        # Reset streaming response
        self.current_streaming_response = ""
        
        # Get confirmation mode
        confirmation_mode = self.confirmation_mode_combo.currentData()
        
        # Parse color sequence
        parsed_result = self.app.llm_manager.parse_color_sequence(response_text)
        
        # Check if sequence was parsed
        if parsed_result:
            # Check if the result is a dictionary mapping timeline indices to sequences
            if isinstance(parsed_result, dict) and all(isinstance(k, int) for k in parsed_result.keys()):
                # This is a timeline-specific format
                timeline_sequences = parsed_result
                
                # Check confirmation mode
                if confirmation_mode == "full" or confirmation_mode == "selective":
                    # Ask if user wants to apply the sequences
                    timeline_names = []
                    for timeline_index in timeline_sequences.keys():
                        timeline = self.app.timeline_manager.get_timeline(timeline_index)
                        if timeline:
                            timeline_names.append(f"Ball {timeline_index + 1}")
                    
                    timeline_str = ", ".join(timeline_names)
                    result = QMessageBox.question(
                        self,
                        "Apply Sequence",
                        f"Do you want to apply the suggested sequences to {timeline_str}?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if result == QMessageBox.StandardButton.Yes:
                        # Apply sequences to each specified timeline
                        for timeline_index, sequence in timeline_sequences.items():
                            self.app.llm_manager.apply_sequence_to_timeline(sequence, timeline_index)
                        
                        # Show success message
                        QMessageBox.information(
                            self,
                            "Sequence Applied",
                            f"The sequences have been applied to {len(timeline_sequences)} timeline(s)."
                        )
                else:  # Auto mode
                    # Apply sequences to each specified timeline automatically
                    for timeline_index, sequence in timeline_sequences.items():
                        self.app.llm_manager.apply_sequence_to_timeline(sequence, timeline_index)
                    
                    # Add info message to chat
                    self._add_message("System", f"Sequences automatically applied to {len(timeline_sequences)} timeline(s).")
            else:
                # This is the legacy format with a single sequence
                sequence = parsed_result
                
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
                
                # Add info message to chat
                self._add_message("System", f"Sequence automatically applied to {len(selected_timelines)} timeline(s).")
    
    def _on_llm_ready(self):
        """Handle LLM ready signal."""
        # Disconnect signal
        self.app.llm_manager.llm_ready.disconnect(self._on_llm_ready)
    
    def _on_clear_chat_clicked(self):
        """Handle Clear Chat button click."""
        # Confirm with user
        result = QMessageBox.question(
            self,
            "Clear Chat History",
            "Are you sure you want to clear the chat history? This will start a fresh conversation.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Clear chat history
            self.chat_history = []
            
            # Reset streaming response
            self.current_streaming_response = ""
            
            # Update chat history display
            self._update_chat_history()
            
            # Save empty chat history to project
            self._save_chat_history()
            
            # Log action
            self.logger.info("Chat history cleared by user")
            
            # Show confirmation
            QMessageBox.information(
                self,
                "Chat Cleared",
                "Chat history has been cleared. You can now start a fresh conversation."
            )
    
    def _on_clear_all_timelines_clicked(self):
        """Handle Clear All Timelines button click."""
        # Confirm with user
        result = QMessageBox.question(
            self,
            "Clear All Timelines",
            "Are you sure you want to clear all timelines? This will remove all segments from all balls.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            try:
                # Get the TimelineActionAPI
                timeline_api = None
                if hasattr(self.app, 'timeline_action_api'):
                    timeline_api = self.app.timeline_action_api
                else:
                    # Import and create if not available
                    from api.timeline_action_api import TimelineActionAPI
                    timeline_api = TimelineActionAPI(self.app)
                
                # Call the clear_all_timelines function directly
                result = timeline_api.clear_all_timelines({"set_black": True})
                
                # Log action
                self.logger.info(f"Clear all timelines executed directly by user: {result}")
                
                # Add message to chat history
                if result.get("success", False):
                    message = (
                        f"All timelines cleared successfully.\n"
                        f"Timelines cleared: {result.get('timelines_cleared', 0)}\n"
                        f"Black segments added: {result.get('set_black', False)}"
                    )
                    self._add_message("System", message)
                    
                    # Show confirmation
                    QMessageBox.information(
                        self,
                        "Timelines Cleared",
                        "All timelines have been cleared successfully."
                    )
                else:
                    error_message = result.get("error", "Unknown error")
                    self._add_message("System", f"Error clearing timelines: {error_message}")
                    
                    # Show error
                    QMessageBox.warning(
                        self,
                        "Error Clearing Timelines",
                        f"An error occurred while clearing timelines: {error_message}"
                    )
            
            except Exception as e:
                self.logger.error(f"Error in _on_clear_all_timelines_clicked: {str(e)}")
                
                # Show error
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An unexpected error occurred: {str(e)}"
                )
    
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
    
    def _submit_feedback(self):
        """Handle feedback submission."""
        # Get feedback text
        feedback_text = self.feedback_text.toPlainText().strip()
        
        # Check if feedback text is empty
        if not feedback_text:
            QMessageBox.warning(
                self,
                "Empty Feedback",
                "Please enter some feedback text before submitting."
            )
            return
        
        # Get selected sentiment
        sentiment = self.sentiment_group.checkedId()
        
        # If no sentiment is selected, default to neutral
        if sentiment not in [1, 0, -1]:
            sentiment = 0
            self.neutral_button.setChecked(True)
        
        # Get song identifier
        song_identifier = ""
        if self.app.audio_manager.audio_file:
            song_identifier = os.path.basename(self.app.audio_manager.audio_file)
        
        # Extract tags from feedback text (simple implementation)
        # This could be enhanced in the future with more sophisticated tag extraction
        tags = []
        
        # Common pattern-related keywords
        pattern_keywords = ["pulse", "toggle", "fade", "beat", "pattern"]
        for keyword in pattern_keywords:
            if keyword in feedback_text.lower():
                tags.append(keyword)
        
        # Common section-related keywords
        section_keywords = ["chorus", "verse", "intro", "outro", "bridge", "section"]
        for keyword in section_keywords:
            if keyword in feedback_text.lower():
                tags.append(keyword)
        
        # Common color-related keywords
        color_keywords = ["red", "green", "blue", "yellow", "purple", "orange", "color"]
        for keyword in color_keywords:
            if keyword in feedback_text.lower():
                tags.append(keyword)
        
        # Submit feedback to preference manager
        success = self.app.preference_manager.add_feedback(
            song_identifier=song_identifier,
            feedback_text=feedback_text,
            sentiment=sentiment,
            tags=tags
        )
        
        if success:
            # Show success message
            QMessageBox.information(
                self,
                "Feedback Submitted",
                "Your feedback has been recorded and will be used to improve future sequences."
            )
            
            # Clear feedback form
            self.feedback_text.clear()
            self.sentiment_group.setExclusive(False)
            self.like_button.setChecked(False)
            self.neutral_button.setChecked(False)
            self.dislike_button.setChecked(False)
            self.sentiment_group.setExclusive(True)
        else:
            # Show error message
            QMessageBox.warning(
                self,
                "Feedback Error",
                "An error occurred while submitting your feedback. Please try again."
            )
    
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Args:
            event: Close event.
        """
        # Hide instead of close
        event.ignore()
        self.hide()
    
    def showEvent(self, event):
        """
        Handle window show event.
        
        Args:
            event: Show event.
        """
        # Update UI when shown
        self._populate_timeline_list()
        
        # Load presets and templates
        self._load_presets()
        self._load_templates()
        
        # Check LLM configuration when window is shown
        # This ensures the UI is updated if settings were changed
        self._check_llm_configuration()
        
        # Call parent method
        super().showEvent(event)