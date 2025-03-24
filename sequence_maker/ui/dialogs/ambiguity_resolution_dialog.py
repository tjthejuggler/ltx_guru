"""
Sequence Maker - Ambiguity Resolution Dialog

This module defines the AmbiguityResolutionDialog class, which provides an interface for resolving
ambiguous instructions from the LLM.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal


class AmbiguityResolutionDialog(QDialog):
    """Dialog for resolving ambiguous instructions."""
    
    resolution_selected = pyqtSignal(str)
    
    def __init__(self, prompt, suggestions, parent=None):
        """
        Initialize the ambiguity resolution dialog.
        
        Args:
            prompt (str): The original prompt.
            suggestions (list): List of suggested clarifications.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.AmbiguityResolutionDialog")
        self.prompt = prompt
        self.suggestions = suggestions
        
        # Set dialog properties
        self.setWindowTitle("Clarify Instructions")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create header
        self.header_label = QLabel("Please clarify your instructions")
        self.header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.main_layout.addWidget(self.header_label)
        
        # Create description
        self.description_label = QLabel(
            "Your instructions were a bit ambiguous. Please select one of the following options or provide a clarification."
        )
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)
        
        # Create prompt display
        self.prompt_label = QLabel("Your original instruction:")
        self.main_layout.addWidget(self.prompt_label)
        
        self.prompt_text = QTextEdit()
        self.prompt_text.setReadOnly(True)
        self.prompt_text.setText(self.prompt)
        self.prompt_text.setMaximumHeight(80)
        self.main_layout.addWidget(self.prompt_text)
        
        # Create suggestions list
        self.suggestions_label = QLabel("Suggested clarifications:")
        self.main_layout.addWidget(self.suggestions_label)
        
        self.suggestions_list = QListWidget()
        for suggestion in self.suggestions:
            item = QListWidgetItem(suggestion)
            self.suggestions_list.addItem(item)
        self.main_layout.addWidget(self.suggestions_list)
        
        # Create custom clarification input
        self.custom_label = QLabel("Or provide your own clarification:")
        self.main_layout.addWidget(self.custom_label)
        
        self.custom_text = QTextEdit()
        self.custom_text.setMaximumHeight(80)
        self.main_layout.addWidget(self.custom_text)
        
        # Create button layout
        self.button_layout = QHBoxLayout()
        
        # Create select button
        self.select_button = QPushButton("Use Selected")
        self.select_button.clicked.connect(self._on_select_clicked)
        self.button_layout.addWidget(self.select_button)
        
        # Create custom button
        self.custom_button = QPushButton("Use Custom")
        self.custom_button.clicked.connect(self._on_custom_clicked)
        self.button_layout.addWidget(self.custom_button)
        
        # Create cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)
        
        self.main_layout.addLayout(self.button_layout)
    
    def _on_select_clicked(self):
        """Handle Select button click."""
        # Get selected item
        selected_items = self.suggestions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self,
                "No Suggestion Selected",
                "Please select a suggestion or provide a custom clarification."
            )
            return
        
        # Get selected suggestion
        suggestion = selected_items[0].text()
        
        # Emit signal
        self.resolution_selected.emit(suggestion)
        
        # Accept dialog
        self.accept()
    
    def _on_custom_clicked(self):
        """Handle Custom button click."""
        # Get custom text
        custom_text = self.custom_text.toPlainText().strip()
        if not custom_text:
            QMessageBox.warning(
                self,
                "No Custom Clarification",
                "Please enter a custom clarification or select a suggestion."
            )
            return
        
        # Emit signal
        self.resolution_selected.emit(custom_text)
        
        # Accept dialog
        self.accept()