"""
Sequence Maker - Lyrics Input Dialog

This module defines the LyricsInputDialog class, which allows users to manually input lyrics.
"""

import logging
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel

class LyricsInputDialog(QDialog):
    """
    Dialog for manual lyrics input.
    
    This dialog is shown when automatic song identification fails, allowing
    the user to manually input lyrics for alignment.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the lyrics input dialog.
        
        Args:
            parent: The parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.LyricsInputDialog")
        
        # Set window properties
        self.setWindowTitle("Manual Lyrics Input")
        self.resize(600, 400)
        
        # Initialize UI
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Add instruction label
        layout.addWidget(QLabel("Song identification failed. Please paste or type the lyrics below:"))
        
        # Add lyrics text area
        self.lyrics_text = QTextEdit()
        self.lyrics_text.setPlaceholderText("Paste or type lyrics here...")
        layout.addWidget(self.lyrics_text)
        
        # Add submit button
        submit_btn = QPushButton("Submit Lyrics")
        submit_btn.clicked.connect(self.accept)
        layout.addWidget(submit_btn)
    
    def get_lyrics(self):
        """
        Get the lyrics entered by the user.
        
        Returns:
            str: The lyrics text.
        """
        return self.lyrics_text.toPlainText()