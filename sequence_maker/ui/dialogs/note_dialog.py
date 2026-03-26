"""
Sequence Maker - Note Dialog

A popup dialog for creating and editing timeline notes.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QColorDialog, QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class NoteDialog(QDialog):
    """
    Dialog for creating or editing a timeline note.

    Shows a text editor and a color picker button.
    """

    def __init__(self, parent=None, text="", color=(255, 255, 0), time_pos=0.0, title="Note"):
        """
        Initialize the note dialog.

        Args:
            parent: Parent widget.
            text (str): Initial note text.
            color (tuple): Initial RGB color tuple.
            time_pos (float): Time position in seconds (for display only).
            title (str): Dialog window title.
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(360, 260)
        self.resize(400, 300)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self._color = tuple(color)
        self._build_ui(text, time_pos)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self, text, time_pos):
        layout = QVBoxLayout(self)

        # Time label
        minutes = int(time_pos) // 60
        seconds = time_pos - minutes * 60
        time_str = f"{minutes:02d}:{seconds:05.2f}"
        time_label = QLabel(f"Time: {time_str}")
        time_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(time_label)

        # Text editor
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(text)
        self.text_edit.setPlaceholderText("Type your note here…")
        self.text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.text_edit)

        # Bottom row: color button + OK / Cancel / Delete
        btn_layout = QHBoxLayout()

        self.color_btn = QPushButton("Color")
        self._update_color_button()
        self.color_btn.clicked.connect(self._pick_color)
        btn_layout.addWidget(self.color_btn)

        btn_layout.addStretch()

        self.delete_btn = QPushButton("Delete Note")
        self.delete_btn.setStyleSheet("color: red;")
        self.delete_btn.clicked.connect(self._on_delete)
        btn_layout.addWidget(self.delete_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _update_color_button(self):
        r, g, b = self._color
        # Choose contrasting text color
        luma = 0.299 * r + 0.587 * g + 0.114 * b
        text_color = "black" if luma > 128 else "white"
        self.color_btn.setStyleSheet(
            f"background-color: rgb({r},{g},{b}); color: {text_color}; "
            f"padding: 4px 12px; border-radius: 3px;"
        )

    def _pick_color(self):
        r, g, b = self._color
        initial = QColor(r, g, b)
        chosen = QColorDialog.getColor(initial, self, "Note Color")
        if chosen.isValid():
            self._color = (chosen.red(), chosen.green(), chosen.blue())
            self._update_color_button()

    def _on_delete(self):
        """Signal deletion by setting a flag and closing."""
        self._deleted = True
        self.done(2)  # Custom result code for delete

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------
    @property
    def note_text(self):
        return self.text_edit.toPlainText()

    @property
    def note_color(self):
        return self._color

    @property
    def deleted(self):
        return getattr(self, "_deleted", False)
