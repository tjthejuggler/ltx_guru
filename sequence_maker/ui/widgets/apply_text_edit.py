"""
Sequence Maker - Apply Text Edit Widget

This module defines the ApplyTextEdit class, which is a custom QTextEdit that
applies changes when Enter is pressed instead of creating a new line.
"""

from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QKeyEvent


class ApplyTextEdit(QTextEdit):
    """
    Custom QTextEdit that applies changes when Enter is pressed instead of creating a new line.
    """
    apply_pressed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Override keyPressEvent to handle Enter key."""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Log the event for debugging
            print(f"Enter key pressed in {self.__class__.__name__}")
            
            # Emit apply_pressed signal instead of inserting a new line
            self.apply_pressed.emit()
            
            # Mark the event as handled
            event.accept()
            
            # Return early to prevent default behavior
            return
        
        # For all other keys, use the default behavior
        super().keyPressEvent(event)