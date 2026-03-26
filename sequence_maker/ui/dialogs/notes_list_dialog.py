"""
Sequence Maker - Notes List Dialog

A popup dialog that shows all timeline notes in a scrollable list.
Each row displays the note color, timestamp, and a short text preview.
Clicking a row opens the note editor.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QWidget, QSizePolicy, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class NotesListDialog(QDialog):
    """
    Dialog that lists every note in the current project.

    Each row shows: [color swatch] [timestamp] [first ~5 words]
    Clicking a row opens the NoteDialog editor for that note.
    """

    def __init__(self, parent, project, timeline_widget):
        """
        Args:
            parent: Parent widget (main window).
            project: The current Project instance.
            timeline_widget: The TimelineWidget, used to open note editors.
        """
        super().__init__(parent)
        self.setWindowTitle("Timeline Notes")
        self.setMinimumSize(400, 300)
        self.resize(460, 380)

        self._project = project
        self._timeline_widget = timeline_widget
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(f"{len(self._project.notes)} note(s)")
        header.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(header)

        # Scrollable list area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(scroll)

        container = QWidget()
        self._list_layout = QVBoxLayout(container)
        self._list_layout.setContentsMargins(4, 4, 4, 4)
        self._list_layout.setSpacing(4)

        notes_sorted = sorted(self._project.notes, key=lambda n: n.time)
        for note in notes_sorted:
            row = self._make_row(note)
            self._list_layout.addWidget(row)

        # Spacer at the bottom so rows stay top-aligned
        self._list_layout.addStretch()
        scroll.setWidget(container)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    # ------------------------------------------------------------------
    def _make_row(self, note):
        """Build a single clickable row widget for *note*."""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        frame.setStyleSheet(
            "QFrame { border: 1px solid #888; border-radius: 4px; padding: 4px; }"
            "QFrame:hover { background-color: #e0e8ff; }"
        )

        row_layout = QHBoxLayout(frame)
        row_layout.setContentsMargins(6, 4, 6, 4)

        # Color swatch
        r, g, b = note.color
        swatch = QLabel()
        swatch.setFixedSize(18, 18)
        swatch.setStyleSheet(
            f"background-color: rgb({r},{g},{b}); border: 1px solid #555; border-radius: 3px;"
        )
        row_layout.addWidget(swatch)

        # Timestamp
        minutes = int(note.time) // 60
        seconds = note.time - minutes * 60
        time_str = f"{minutes:02d}:{seconds:05.2f}"
        time_label = QLabel(time_str)
        time_label.setFixedWidth(70)
        time_label.setStyleSheet("font-family: monospace; font-weight: bold;")
        row_layout.addWidget(time_label)

        # Text preview (first ~5 words)
        words = note.text.split()
        preview = " ".join(words[:5])
        if len(words) > 5:
            preview += " …"
        if not preview:
            preview = "(empty)"
        text_label = QLabel(preview)
        text_label.setStyleSheet("color: #333;")
        text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        row_layout.addWidget(text_label)

        # Make the whole row clickable via mouse release
        frame.mousePressEvent = lambda event, n=note: self._on_row_clicked(n)

        return frame

    # ------------------------------------------------------------------
    def _on_row_clicked(self, note):
        """Open the note editor for *note*, then refresh the list."""
        # Access the TimelineContainer's _edit_note method
        container = self._timeline_widget.timeline_container
        container._edit_note(note)

        # Refresh the dialog to reflect any edits or deletions
        self._refresh()

    def _refresh(self):
        """Rebuild the list after an edit."""
        # Remove all existing rows
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Re-add rows
        notes_sorted = sorted(self._project.notes, key=lambda n: n.time)
        for note in notes_sorted:
            row = self._make_row(note)
            self._list_layout.addWidget(row)
        self._list_layout.addStretch()

        # Update header via parent layout
        header = self.findChild(QLabel)
        if header:
            header.setText(f"{len(self._project.notes)} note(s)")
