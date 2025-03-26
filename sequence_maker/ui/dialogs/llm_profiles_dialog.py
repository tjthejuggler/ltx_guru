"""
Sequence Maker - LLM Profiles Dialog

This module defines the LLMProfilesDialog class, which allows users to manage LLM profiles.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QSplitter,
    QWidget, QFormLayout, QComboBox, QDoubleSpinBox, QSpinBox,
    QMessageBox, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont


class LLMProfilesDialog(QDialog):
    """Dialog for managing LLM profiles."""
    
    def __init__(self, app, parent=None):
        """
        Initialize the LLM profiles dialog.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.LLMProfilesDialog")
        
        # Set dialog properties
        self.setWindowTitle("LLM Profiles")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        
        # Profiles
        self.profiles = {}
        self.current_profile_id = None
        
        # Create UI
        self._create_ui()
        
        # Load profiles
        self._load_profiles()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create header
        self.header_label = QLabel("LLM Profiles")
        self.header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.main_layout.addWidget(self.header_label)
        
        # Create description
        self.description_label = QLabel(
            "Manage LLM profiles. Each profile contains settings for a specific LLM provider and model."
        )
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)
        
        # Create splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter, 1)
        
        # Create profile list widget
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        
        self.profile_list = QListWidget()
        self.profile_list.setMinimumWidth(250)
        self.profile_list.currentRowChanged.connect(self._on_profile_selected)
        self.list_layout.addWidget(self.profile_list)
        
        self.list_button_layout = QHBoxLayout()
        self.list_layout.addLayout(self.list_button_layout)
        
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self._on_add_profile)
        self.list_button_layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self._on_remove_profile)
        self.list_button_layout.addWidget(self.remove_button)
        
        self.activate_button = QPushButton("Set Active")
        self.activate_button.clicked.connect(self._on_activate_profile)
        self.list_button_layout.addWidget(self.activate_button)
        
        self.splitter.addWidget(self.list_widget)
        
        # Create profile editor widget
        self.editor_widget = QWidget()
        self.editor_layout = QFormLayout(self.editor_widget)
        
        self.name_edit = QLineEdit()
        self.editor_layout.addRow("Name:", self.name_edit)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "Anthropic", "Local"])
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        self.editor_layout.addRow("Provider:", self.provider_combo)
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.editor_layout.addRow("API Key:", self.api_key_edit)
        
        self.model_edit = QLineEdit()
        self.editor_layout.addRow("Model:", self.model_edit)
        
        self.local_endpoint_edit = QLineEdit()
        self.local_endpoint_edit.setPlaceholderText("http://localhost:8000/v1/completions")
        self.editor_layout.addRow("Local Endpoint:", self.local_endpoint_edit)
        
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(0.7)
        self.editor_layout.addRow("Temperature:", self.temperature_spin)
        
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 8000)
        self.max_tokens_spin.setSingleStep(100)
        self.max_tokens_spin.setValue(1024)
        self.editor_layout.addRow("Max Tokens:", self.max_tokens_spin)
        
        self.top_p_spin = QDoubleSpinBox()
        self.top_p_spin.setRange(0.0, 1.0)
        self.top_p_spin.setSingleStep(0.1)
        self.top_p_spin.setValue(1.0)
        self.editor_layout.addRow("Top P:", self.top_p_spin)
        
        self.frequency_penalty_spin = QDoubleSpinBox()
        self.frequency_penalty_spin.setRange(0.0, 2.0)
        self.frequency_penalty_spin.setSingleStep(0.1)
        self.frequency_penalty_spin.setValue(0.0)
        self.editor_layout.addRow("Frequency Penalty:", self.frequency_penalty_spin)
        
        self.presence_penalty_spin = QDoubleSpinBox()
        self.presence_penalty_spin.setRange(0.0, 2.0)
        self.presence_penalty_spin.setSingleStep(0.1)
        self.presence_penalty_spin.setValue(0.0)
        self.editor_layout.addRow("Presence Penalty:", self.presence_penalty_spin)
        
        # Add Anthropic thinking options
        self.thinking_group = QGroupBox("Anthropic Extended Thinking")
        self.thinking_layout = QFormLayout(self.thinking_group)
        
        self.enable_thinking_check = QCheckBox("Enable Extended Thinking")
        self.enable_thinking_check.stateChanged.connect(self._on_enable_thinking_changed)
        self.thinking_layout.addRow(self.enable_thinking_check)
        
        self.thinking_budget_spin = QSpinBox()
        self.thinking_budget_spin.setRange(1024, 32000)
        self.thinking_budget_spin.setSingleStep(1024)
        self.thinking_budget_spin.setValue(1024)
        self.thinking_budget_spin.setEnabled(False)
        self.thinking_layout.addRow("Thinking Budget (tokens):", self.thinking_budget_spin)
        
        # Add a note about thinking
        thinking_note = QLabel(
            "Extended thinking gives Claude enhanced reasoning capabilities for complex tasks, "
            "while also providing transparency into its step-by-step thought process. "
            "Only available with Anthropic Claude models."
        )
        thinking_note.setWordWrap(True)
        self.thinking_layout.addRow(thinking_note)
        
        self.editor_layout.addRow(self.thinking_group)
        self.thinking_group.setVisible(False)  # Hide by default
        
        self.save_profile_button = QPushButton("Save Profile")
        self.save_profile_button.clicked.connect(self._on_save_profile)
        self.editor_layout.addRow(self.save_profile_button)
        
        self.splitter.addWidget(self.editor_widget)
        
        # Create dialog buttons
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        
        self.button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.button_layout.addWidget(self.close_button)
        
        # Set splitter sizes
        self.splitter.setSizes([300, 500])
        
        # Disable editor initially
        self._set_editor_enabled(False)
    
    def _set_editor_enabled(self, enabled):
        """
        Enable or disable the profile editor.
        
        Args:
            enabled (bool): Whether to enable the editor.
        """
        self.name_edit.setEnabled(enabled)
        self.provider_combo.setEnabled(enabled)
        self.api_key_edit.setEnabled(enabled)
        self.model_edit.setEnabled(enabled)
        self.local_endpoint_edit.setEnabled(enabled)
        self.temperature_spin.setEnabled(enabled)
        self.max_tokens_spin.setEnabled(enabled)
        self.top_p_spin.setEnabled(enabled)
        self.frequency_penalty_spin.setEnabled(enabled)
        self.presence_penalty_spin.setEnabled(enabled)
        self.enable_thinking_check.setEnabled(enabled)
        # Only enable thinking budget if thinking is enabled and checkbox is checked
        if enabled:
            # Qt.CheckState.Checked is 2 in PyQt6
            self.thinking_budget_spin.setEnabled(self.enable_thinking_check.isChecked())
        else:
            self.thinking_budget_spin.setEnabled(False)
        self.save_profile_button.setEnabled(enabled)
    
    def _on_enable_thinking_changed(self, state):
        """
        Handle enable thinking checkbox state change.
        
        Args:
            state (int): Checkbox state.
        """
        # Enable the thinking budget spinner if the checkbox is checked
        # Qt.CheckState.Checked is 2 in PyQt6
        self.thinking_budget_spin.setEnabled(state == 2)
        self.logger.info(f"Thinking checkbox state changed to {state}, budget spinner enabled: {state == 2}")
    
    def _on_provider_changed(self, provider):
        """
        Handle provider change.
        
        Args:
            provider (str): Selected provider.
        """
        # Update model field placeholder based on provider
        if provider == "OpenAI":
            self.model_edit.setPlaceholderText("gpt-4-turbo")
            self.local_endpoint_edit.setEnabled(False)
            self.thinking_group.setVisible(False)
        elif provider == "Anthropic":
            self.model_edit.setPlaceholderText("claude-3-7-sonnet-20250219")
            self.local_endpoint_edit.setEnabled(False)
            self.thinking_group.setVisible(True)
        else:  # Local
            self.model_edit.setPlaceholderText("local-model")
            self.local_endpoint_edit.setEnabled(True)
            self.thinking_group.setVisible(False)
    
    def _load_profiles(self):
        """Load profiles from the LLM manager."""
        # Clear list
        self.profile_list.clear()
        
        # Get profiles from LLM manager
        self.profiles = self.app.llm_manager.get_profiles()
        active_profile = self.app.llm_manager.get_active_profile()
        
        # Add each profile to the list
        for profile_id, profile in self.profiles.items():
            item = QListWidgetItem(profile.get("name", profile_id))
            item.setData(Qt.ItemDataRole.UserRole, profile_id)
            
            # Mark active profile
            if profile_id == active_profile:
                item.setText(f"{profile.get('name', profile_id)} (Active)")
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                
            self.profile_list.addItem(item)
    
    def _on_profile_selected(self, row):
        """
        Handle profile selection.
        
        Args:
            row (int): Selected row index.
        """
        if row >= 0 and row < self.profile_list.count():
            # Get profile ID
            item = self.profile_list.item(row)
            profile_id = item.data(Qt.ItemDataRole.UserRole)
            
            # Save current profile if one is being edited
            if self.current_profile_id:
                self._save_current_profile()
            
            # Set current profile ID
            self.current_profile_id = profile_id
            
            # Get profile
            profile = self.profiles.get(profile_id, {})
            
            # Update editor
            self.name_edit.setText(profile.get("name", ""))
            self.provider_combo.setCurrentText(profile.get("provider", "").capitalize())
            self.api_key_edit.setText(profile.get("api_key", ""))
            self.model_edit.setText(profile.get("model", ""))
            self.local_endpoint_edit.setText(profile.get("local_endpoint", ""))
            self.temperature_spin.setValue(profile.get("temperature", 0.7))
            self.max_tokens_spin.setValue(profile.get("max_tokens", 1024))
            self.top_p_spin.setValue(profile.get("top_p", 1.0))
            self.frequency_penalty_spin.setValue(profile.get("frequency_penalty", 0.0))
            self.presence_penalty_spin.setValue(profile.get("presence_penalty", 0.0))
            
            # Set thinking options
            thinking_enabled = profile.get("enable_thinking", False)
            self.enable_thinking_check.setChecked(thinking_enabled)
            self.thinking_budget_spin.setValue(profile.get("thinking_budget", 1024))
            
            # Make sure the thinking budget spinner is enabled/disabled based on the checkbox
            self.thinking_budget_spin.setEnabled(thinking_enabled)
            
            # Enable editor
            self._set_editor_enabled(True)
            
            # Update local endpoint visibility
            self._on_provider_changed(self.provider_combo.currentText())
        else:
            # Disable editor
            self._set_editor_enabled(False)
            self.current_profile_id = None
    
    def _save_current_profile(self):
        """Save the currently edited profile."""
        if not self.current_profile_id:
            return
            
        # Get profile data
        profile_data = {
            "name": self.name_edit.text(),
            "provider": self.provider_combo.currentText().lower(),
            "api_key": self.api_key_edit.text(),
            "model": self.model_edit.text(),
            "local_endpoint": self.local_endpoint_edit.text(),
            "temperature": self.temperature_spin.value(),
            "max_tokens": self.max_tokens_spin.value(),
            "top_p": self.top_p_spin.value(),
            "frequency_penalty": self.frequency_penalty_spin.value(),
            "presence_penalty": self.presence_penalty_spin.value(),
            "enable_thinking": self.enable_thinking_check.isChecked(),
            "thinking_budget": self.thinking_budget_spin.value()
        }
        
        # Update profile in LLM manager
        self.app.llm_manager.update_profile(self.current_profile_id, **profile_data)
        
        # Update list item
        for i in range(self.profile_list.count()):
            item = self.profile_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == self.current_profile_id:
                is_active = self.current_profile_id == self.app.llm_manager.get_active_profile()
                if is_active:
                    item.setText(f"{profile_data['name']} (Active)")
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                else:
                    item.setText(profile_data["name"])
                    font = item.font()
                    font.setBold(False)
                    item.setFont(font)
                break
    
    def _on_save_profile(self):
        """Handle Save Profile button click."""
        # Save current profile
        self._save_current_profile()
        
        # Show confirmation
        QMessageBox.information(
            self,
            "Profile Saved",
            "The profile has been saved."
        )
    
    def _on_add_profile(self):
        """Handle Add button click."""
        # Create a default name
        name = "New Profile"
        count = 1
        profile_id = f"new_profile_{count}"
        
        # Make sure the name is unique
        while profile_id in self.profiles:
            count += 1
            profile_id = f"new_profile_{count}"
            name = f"New Profile {count}"
        
        # Add profile to LLM manager
        self.app.llm_manager.add_profile(name)
        
        # Reload profiles
        self._load_profiles()
        
        # Select the new profile
        for i in range(self.profile_list.count()):
            item = self.profile_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == profile_id:
                self.profile_list.setCurrentRow(i)
                break
    
    def _on_remove_profile(self):
        """Handle Remove button click."""
        if not self.current_profile_id:
            return
            
        # Don't allow removing the default profile
        if self.current_profile_id == "default":
            QMessageBox.warning(
                self,
                "Cannot Remove Default Profile",
                "The default profile cannot be removed."
            )
            return
            
        # Confirm removal
        result = QMessageBox.question(
            self,
            "Remove Profile",
            f"Are you sure you want to remove the profile '{self.name_edit.text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Remove profile from LLM manager
            self.app.llm_manager.delete_profile(self.current_profile_id)
            
            # Reload profiles
            self._load_profiles()
            
            # Clear editor
            self._set_editor_enabled(False)
            self.current_profile_id = None
    
    def _on_activate_profile(self):
        """Handle Set Active button click."""
        if not self.current_profile_id:
            return
            
        # Set active profile in LLM manager
        self.app.llm_manager.set_active_profile(self.current_profile_id)
        
        # Reload profiles to update display
        self._load_profiles()
        
        # Show confirmation
        QMessageBox.information(
            self,
            "Profile Activated",
            f"The profile '{self.name_edit.text()}' has been set as the active profile."
        )
    
    def accept(self):
        """Handle dialog acceptance."""
        # Save current profile if one is being edited
        if self.current_profile_id:
            self._save_current_profile()
            
        # Accept dialog
        super().accept()