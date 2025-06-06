"""
Sequence Maker - Fade Effect Dialog

This module defines the FadeEffectDialog class for configuring fade effects.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QColorDialog, QLineEdit, QFormLayout
)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt

class FadeEffectDialog(QDialog):
    """
    Dialog for configuring the start and end colors of a fade effect.
    """
    def __init__(self, initial_start_color=(255,0,0), initial_end_color=None, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("SequenceMaker.FadeEffectDialog")
        self.setWindowTitle("Configure Fade Effect")
        self.setMinimumWidth(350)

        self.start_color = QColor(*initial_start_color)
        if initial_end_color:
            self.end_color = QColor(*initial_end_color)
        else:
            # Default end_color to black if not provided or if segment was solid
            self.end_color = QColor(0,0,0) 

        self._create_ui()

    def _create_ui(self):
        """Create the user interface."""
        self.main_layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        # Start Color
        self.start_color_button = QPushButton()
        self.start_color_button.setToolTip("Click to choose start color")
        self._update_button_color(self.start_color_button, self.start_color)
        self.start_color_button.clicked.connect(self._choose_start_color)
        
        self.start_color_label_display = QLabel(self.start_color.name()) # Show hex
        form_layout.addRow("Start Color:", self.start_color_button)
        form_layout.addRow("", self.start_color_label_display)


        # End Color
        self.end_color_button = QPushButton()
        self.end_color_button.setToolTip("Click to choose end color")
        self._update_button_color(self.end_color_button, self.end_color)
        self.end_color_button.clicked.connect(self._choose_end_color)

        self.end_color_label_display = QLabel(self.end_color.name()) # Show hex
        form_layout.addRow("End Color:", self.end_color_button)
        form_layout.addRow("", self.end_color_label_display)

        self.main_layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        self.main_layout.addLayout(button_layout)

    def _update_button_color(self, button, q_color):
        """Updates the background color of a button to reflect the QColor."""
        palette = button.palette()
        palette.setColor(QPalette.ColorRole.Button, q_color)
        button.setAutoFillBackground(True)
        button.setPalette(palette)
        button.update()
        # Set text to be black or white depending on luminance for visibility
        if q_color.lightnessF() > 0.5:
            button.setStyleSheet("QPushButton { color: black; }")
        else:
            button.setStyleSheet("QPushButton { color: white; }")
        button.setText(q_color.name().upper())


    def _choose_start_color(self):
        """Open QColorDialog to choose the start color."""
        color = QColorDialog.getColor(self.start_color, self, "Choose Start Color")
        if color.isValid():
            self.start_color = color
            self._update_button_color(self.start_color_button, self.start_color)
            self.start_color_label_display.setText(self.start_color.name())


    def _choose_end_color(self):
        """Open QColorDialog to choose the end color."""
        color = QColorDialog.getColor(self.end_color, self, "Choose End Color")
        if color.isValid():
            self.end_color = color
            self._update_button_color(self.end_color_button, self.end_color)
            self.end_color_label_display.setText(self.end_color.name())

    def get_colors(self):
        """
        Get the selected start and end colors.

        Returns:
            tuple: (start_color_rgb_tuple, end_color_rgb_tuple)
        """
        start_rgb = (self.start_color.red(), self.start_color.green(), self.start_color.blue())
        end_rgb = (self.end_color.red(), self.end_color.green(), self.end_color.blue())
        return start_rgb, end_rgb

if __name__ == '__main__':
    # Example usage (for testing the dialog standalone)
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    # Test with initial end_color
    dialog_with_end = FadeEffectDialog(initial_start_color=(255,0,0), initial_end_color=(0,0,255))
    if dialog_with_end.exec():
        start, end = dialog_with_end.get_colors()
        print(f"Selected Start Color: {start}, End Color: {end}")

    # Test without initial end_color (should default to black)
    dialog_no_end = FadeEffectDialog(initial_start_color=(0,255,0))
    if dialog_no_end.exec():
        start, end = dialog_no_end.get_colors()
        print(f"Selected Start Color: {start}, End Color: {end}")
        
    sys.exit()