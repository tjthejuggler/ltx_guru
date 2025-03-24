"""
Sequence Maker - Custom Instructions Dialog

This module defines the CustomInstructionsDialog class, which allows users to edit custom LLM instructions.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QFont, QMessageBox
)
from PyQt6.QtCore import Qt


class CustomInstructionsDialog(QDialog):
    """Dialog for editing custom LLM instructions."""
    
    def __init__(self, app, parent=None):
        """
        Initialize the custom instructions dialog.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.CustomInstructionsDialog")
        
        # Set dialog properties
        self.setWindowTitle("Custom LLM Instructions")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        # Create UI
        self._create_ui()
        
        # Load current instructions
        self._load_instructions()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create header
        self.header_label = QLabel("Custom LLM Instructions")
        self.header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.main_layout.addWidget(self.header_label)
        
        # Create description
        self.description_label = QLabel(
            "Define custom instructions for the LLM. These instructions will be included in the system message."
        )
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)
        
        # Create examples
        self.examples_label = QLabel(
            "Examples:\n"
            "- 'Always use RGB colors in the format [R, G, B]'\n"
            "- 'Prefer creating patterns that match the mood of the music'\n"
            "- 'Use color theory principles when suggesting color combinations'"
        )
        self.examples_label.setStyleSheet("color: #666;")
        self.main_layout.addWidget(self.examples_label)
        
        # Create instructions editor
        self.instructions_editor = QTextEdit()
        self.instructions_editor.setPlaceholderText("Enter custom instructions here...")
        self.main_layout.addWidget(self.instructions_editor)
        
        # Create button layout
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        
        # Create save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._on_save)
        self.button_layout.addWidget(self.save_button)
        
        # Create reset button
        self.reset_button = QPushButton("Reset to Default")
        self.reset_button.clicked.connect(self._on_reset)
        self.button_layout.addWidget(self.reset_button)
        
        # Create cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)
    
    def _load_instructions(self):
        """Load current custom instructions."""
        if self.app.project_manager.current_project:
            # Get custom instructions from project
            custom_instructions = getattr(self.app.project_manager.current_project, "llm_custom_instructions", "")
            self.instructions_editor.setText(custom_instructions)
    
    def _on_save(self):
        """Handle Save button click."""
        if self.app.project_manager.current_project:
            # Get instructions from editor
            instructions = self.instructions_editor.toPlainText()
            
            # Save to project
            self.app.project_manager.current_project.llm_custom_instructions = instructions
            
            # Mark project as changed
            self.app.project_manager.project_changed.emit()
            
            # Log
            self.logger.info("Custom LLM instructions saved")
            
            # Accept dialog
            self.accept()
        else:
            # Show error
            QMessageBox.warning(
                self,
                "No Project",
                "No project is currently loaded. Custom instructions cannot be saved."
            )
    
    def _on_reset(self):
        """Handle Reset to Default button click."""
        # Confirm reset
        result = QMessageBox.question(
            self,
            "Reset Instructions",
            "Are you sure you want to reset the custom instructions to default (empty)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Clear editor
            self.instructions_editor.clear()