"""
Sequence Maker - LLM Presets Dialog

This module defines the LLMPresetsDialog class, which allows users to manage LLM configuration presets.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QSplitter,
    QWidget, QFormLayout, QComboBox, QDoubleSpinBox, QSpinBox,
    QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

from models.llm_customization import LLMPreset, create_default_presets


class LLMPresetsDialog(QDialog):
    """Dialog for managing LLM configuration presets."""
    
    def __init__(self, app, parent=None):
        """
        Initialize the LLM presets dialog.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.LLMPresetsDialog")
        
        # Set dialog properties
        self.setWindowTitle("LLM Configuration Presets")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        
        # Presets
        self.presets = []
        self.current_preset_index = -1
        
        # Create UI
        self._create_ui()
        
        # Load presets
        self._load_presets()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create header
        self.header_label = QLabel("LLM Configuration Presets")
        self.header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.main_layout.addWidget(self.header_label)
        
        # Create description
        self.description_label = QLabel(
            "Manage configuration presets for LLM providers. Presets allow you to quickly switch between different LLM configurations."
        )
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)
        
        # Create splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter, 1)
        
        # Create preset list widget
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        
        self.preset_list = QListWidget()
        self.preset_list.setMinimumWidth(250)
        self.preset_list.currentRowChanged.connect(self._on_preset_selected)
        self.list_layout.addWidget(self.preset_list)
        
        self.list_button_layout = QHBoxLayout()
        self.list_layout.addLayout(self.list_button_layout)
        
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self._on_add_preset)
        self.list_button_layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self._on_remove_preset)
        self.list_button_layout.addWidget(self.remove_button)
        
        self.reset_button = QPushButton("Reset to Default")
        self.reset_button.clicked.connect(self._on_reset_presets)
        self.list_button_layout.addWidget(self.reset_button)
        
        self.splitter.addWidget(self.list_widget)
        
        # Create preset editor widget
        self.editor_widget = QWidget()
        self.editor_layout = QFormLayout(self.editor_widget)
        
        self.name_edit = QLineEdit()
        self.editor_layout.addRow("Name:", self.name_edit)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "Anthropic", "Local"])
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        self.editor_layout.addRow("Provider:", self.provider_combo)
        
        self.model_edit = QLineEdit()
        self.editor_layout.addRow("Model:", self.model_edit)
        
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(0.7)
        self.editor_layout.addRow("Temperature:", self.temperature_spin)
        
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 8000)
        self.max_tokens_spin.setSingleStep(100)
        self.max_tokens_spin.setValue(1000)
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
        
        self.save_preset_button = QPushButton("Save Preset")
        self.save_preset_button.clicked.connect(self._on_save_preset)
        self.editor_layout.addRow(self.save_preset_button)
        
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
        Enable or disable the preset editor.
        
        Args:
            enabled (bool): Whether to enable the editor.
        """
        self.name_edit.setEnabled(enabled)
        self.provider_combo.setEnabled(enabled)
        self.model_edit.setEnabled(enabled)
        self.temperature_spin.setEnabled(enabled)
        self.max_tokens_spin.setEnabled(enabled)
        self.top_p_spin.setEnabled(enabled)
        self.frequency_penalty_spin.setEnabled(enabled)
        self.presence_penalty_spin.setEnabled(enabled)
        self.save_preset_button.setEnabled(enabled)
    
    def _on_provider_changed(self, provider):
        """
        Handle provider change.
        
        Args:
            provider (str): Selected provider.
        """
        # Update model field placeholder based on provider
        if provider == "OpenAI":
            self.model_edit.setPlaceholderText("gpt-4-turbo")
        elif provider == "Anthropic":
            self.model_edit.setPlaceholderText("claude-3-opus-20240229")
        else:  # Local
            self.model_edit.setPlaceholderText("local-model")
    
    def _load_presets(self):
        """Load presets from the current project."""
        # Clear list
        self.preset_list.clear()
        self.presets = []
        
        if self.app.project_manager.current_project:
            # Get presets from project
            presets_data = getattr(self.app.project_manager.current_project, "llm_presets", None)
            
            if presets_data is None or not presets_data:
                # Create default presets if none exist
                self.presets = create_default_presets()
                self._save_presets()
            else:
                # Load presets from project data
                for preset_data in presets_data:
                    preset = LLMPreset.from_dict(preset_data)
                    self.presets.append(preset)
            
            # Populate list
            for preset in self.presets:
                item = QListWidgetItem(preset.name)
                item.setToolTip(f"{preset.provider.capitalize()} - {preset.model}")
                self.preset_list.addItem(item)
    
    def _save_presets(self):
        """Save presets to the current project."""
        if self.app.project_manager.current_project:
            # Convert presets to dictionaries
            presets_data = [preset.to_dict() for preset in self.presets]
            
            # Save to project
            self.app.project_manager.current_project.llm_presets = presets_data
            
            # Mark project as changed
            self.app.project_manager.project_changed.emit()
            
            # Log
            self.logger.info(f"Saved {len(presets_data)} LLM presets")
    
    def _on_preset_selected(self, row):
        """
        Handle preset selection.
        
        Args:
            row (int): Selected row index.
        """
        if 0 <= row < len(self.presets):
            # Save current preset if one is being edited
            if 0 <= self.current_preset_index < len(self.presets):
                self._save_current_preset()
            
            # Set current preset index
            self.current_preset_index = row
            
            # Get preset
            preset = self.presets[row]
            
            # Update editor
            self.name_edit.setText(preset.name)
            self.provider_combo.setCurrentText(preset.provider.capitalize())
            self.model_edit.setText(preset.model)
            self.temperature_spin.setValue(preset.temperature)
            self.max_tokens_spin.setValue(preset.max_tokens)
            self.top_p_spin.setValue(preset.top_p)
            self.frequency_penalty_spin.setValue(preset.frequency_penalty)
            self.presence_penalty_spin.setValue(preset.presence_penalty)
            
            # Enable editor
            self._set_editor_enabled(True)
        else:
            # Disable editor
            self._set_editor_enabled(False)
            self.current_preset_index = -1
    
    def _save_current_preset(self):
        """Save the currently edited preset."""
        if 0 <= self.current_preset_index < len(self.presets):
            # Get preset
            preset = self.presets[self.current_preset_index]
            
            # Update preset
            preset.name = self.name_edit.text()
            preset.provider = self.provider_combo.currentText().lower()
            preset.model = self.model_edit.text()
            preset.temperature = self.temperature_spin.value()
            preset.max_tokens = self.max_tokens_spin.value()
            preset.top_p = self.top_p_spin.value()
            preset.frequency_penalty = self.frequency_penalty_spin.value()
            preset.presence_penalty = self.presence_penalty_spin.value()
            
            # Update list item
            item = self.preset_list.item(self.current_preset_index)
            item.setText(preset.name)
            item.setToolTip(f"{preset.provider.capitalize()} - {preset.model}")
    
    def _on_save_preset(self):
        """Handle Save Preset button click."""
        # Save current preset
        self._save_current_preset()
        
        # Save presets to project
        self._save_presets()
        
        # Show confirmation
        QMessageBox.information(
            self,
            "Preset Saved",
            "The preset has been saved."
        )
    
    def _on_add_preset(self):
        """Handle Add button click."""
        # Create new preset
        preset = LLMPreset(
            name="New Preset",
            provider="openai",
            model="gpt-4-turbo",
            temperature=0.7,
            max_tokens=1024
        )
        
        # Add to presets
        self.presets.append(preset)
        
        # Add to list
        item = QListWidgetItem(preset.name)
        item.setToolTip(f"{preset.provider.capitalize()} - {preset.model}")
        self.preset_list.addItem(item)
        
        # Select new preset
        self.preset_list.setCurrentRow(len(self.presets) - 1)
    
    def _on_remove_preset(self):
        """Handle Remove button click."""
        if 0 <= self.current_preset_index < len(self.presets):
            # Confirm removal
            result = QMessageBox.question(
                self,
                "Remove Preset",
                f"Are you sure you want to remove the preset '{self.presets[self.current_preset_index].name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if result == QMessageBox.StandardButton.Yes:
                # Remove preset
                self.presets.pop(self.current_preset_index)
                
                # Remove from list
                self.preset_list.takeItem(self.current_preset_index)
                
                # Save presets
                self._save_presets()
                
                # Clear editor
                self.name_edit.clear()
                self.model_edit.clear()
                
                # Disable editor
                self._set_editor_enabled(False)
                self.current_preset_index = -1
    
    def _on_reset_presets(self):
        """Handle Reset to Default button click."""
        # Confirm reset
        result = QMessageBox.question(
            self,
            "Reset Presets",
            "Are you sure you want to reset all presets to default? This will remove any custom presets.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Reset presets
            self.presets = create_default_presets()
            
            # Save presets
            self._save_presets()
            
            # Reload presets
            self._load_presets()
            
            # Clear editor
            self.name_edit.clear()
            self.model_edit.clear()
            
            # Disable editor
            self._set_editor_enabled(False)
            self.current_preset_index = -1
    
    def accept(self):
        """Handle dialog acceptance."""
        # Save current preset if one is being edited
        if 0 <= self.current_preset_index < len(self.presets):
            self._save_current_preset()
        
        # Save presets to project
        self._save_presets()
        
        # Accept dialog
        super().accept()