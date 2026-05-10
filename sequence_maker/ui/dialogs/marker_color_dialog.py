"""
Sequence Maker - Marker Color Picker Dialog

A simple popup dialog that lets the user pick one of 6 basic colors
for a timeline marker.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette

from models.marker import MARKER_COLORS


class MarkerColorDialog(QDialog):
    """
    Dialog for picking a marker color from a set of basic colors.

    Returns the selected color tuple via get_color() after exec().
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose Marker Color")
        self.setModal(True)
        self.setFixedSize(280, 120)

        self._selected_color = None

        layout = QVBoxLayout(self)

        # Instruction label
        label = QLabel("Pick a marker color:")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Color buttons row
        button_row = QHBoxLayout()
        button_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for name, rgb in MARKER_COLORS.items():
            btn = QPushButton(name)
            btn.setFixedSize(80, 36)
            r, g, b = rgb
            # Set button background to the marker color
            btn.setStyleSheet(
                f"QPushButton {{ background-color: rgb({r},{g},{b}); "
                f"color: {'white' if (r + g + b) < 400 else 'black'}; "
                f"font-weight: bold; border: 1px solid #555; border-radius: 4px; }}"
                f"QPushButton:hover {{ border: 2px solid white; }}"
            )
            btn.clicked.connect(lambda checked, c=rgb: self._pick(c))
            button_row.addWidget(btn)

        layout.addLayout(button_row)

    def _pick(self, color):
        """Store the selected color and accept the dialog."""
        self._selected_color = color
        self.accept()

    def get_color(self):
        """Return the selected color tuple, or None if cancelled."""
        return self._selected_color
