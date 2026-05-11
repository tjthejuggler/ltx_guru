"""
Sequence Maker - Zero Key Color Configuration Dialog

Allows the user to configure the colors applied to each of the 3 timelines
when the '0' key is pressed.  Each row has quick-pick buttons for the
standard colours plus a "Custom…" button that opens a QColorDialog.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QColorDialog, QDialogButtonBox, QGroupBox,
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt


# Standard quick-pick colours (same as the segment context menu)
QUICK_COLORS = [
    ((255, 0, 0), "Red"),
    ((255, 165, 0), "Orange"),
    ((255, 255, 0), "Yellow"),
    ((0, 255, 0), "Green"),
    ((0, 255, 255), "Cyan"),
    ((0, 0, 255), "Blue"),
    ((255, 0, 255), "Pink"),
    ((255, 255, 255), "White"),
    ((0, 0, 0), "Black"),
]


class ZeroKeyColorDialog(QDialog):
    """Dialog for configuring the '0' hotkey colours per timeline."""

    def __init__(self, current_colors, parent=None):
        """
        Args:
            current_colors: list of 3 items, each an RGB tuple or None.
            parent: parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Configure '0' Key Colors")
        self.setMinimumWidth(500)

        # Work with a mutable copy
        self.colors = list(current_colors)  # [rgb|None, rgb|None, rgb|None]
        self.color_buttons = []  # list of (preview_btn, row_index)

        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        layout = QVBoxLayout(self)

        info = QLabel(
            "Set the colour that each ball timeline will receive when you "
            "press the '0' key.  Leave a row set to <b>None</b> to skip that "
            "timeline."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        for i in range(3):
            group = QGroupBox(f"Ball {i + 1}")
            row = QHBoxLayout(group)

            # Current-colour preview
            preview = QPushButton()
            preview.setFixedSize(40, 30)
            preview.setEnabled(False)
            self._update_preview(preview, self.colors[i])
            row.addWidget(QLabel("Color:"))
            row.addWidget(preview)
            self.color_buttons.append((preview, i))

            # Quick-pick buttons
            for rgb, name in QUICK_COLORS:
                btn = QPushButton(name)
                btn.setFixedHeight(28)
                btn.setStyleSheet(
                    f"background-color: rgb({rgb[0]},{rgb[1]},{rgb[2]}); "
                    f"color: {'#000' if sum(rgb) > 400 else '#fff'};"
                )
                btn.clicked.connect(
                    lambda checked, r=rgb, idx=i: self._set_color(idx, r)
                )
                row.addWidget(btn)

            # Custom colour button
            custom_btn = QPushButton("Custom…")
            custom_btn.setFixedHeight(28)
            custom_btn.clicked.connect(
                lambda checked, idx=i: self._pick_custom(idx)
            )
            row.addWidget(custom_btn)

            # Clear / set to None button
            clear_btn = QPushButton("None")
            clear_btn.setFixedHeight(28)
            clear_btn.setToolTip("Don't set this timeline when '0' is pressed")
            clear_btn.clicked.connect(
                lambda checked, idx=i: self._set_color(idx, None)
            )
            row.addWidget(clear_btn)

            layout.addWidget(group)

        # OK / Cancel
        bbox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)
        layout.addWidget(bbox)

    # -------------------------------------------------------------- helpers
    def _set_color(self, idx, rgb_or_none):
        self.colors[idx] = rgb_or_none
        preview, _ = self.color_buttons[idx]
        self._update_preview(preview, rgb_or_none)

    def _pick_custom(self, idx):
        current = self.colors[idx]
        initial = QColor(*current) if current else QColor(255, 255, 255)
        color = QColorDialog.getColor(initial, self, f"Choose Color for Ball {idx + 1}")
        if color.isValid():
            self._set_color(idx, (color.red(), color.green(), color.blue()))

    @staticmethod
    def _update_preview(btn, rgb_or_none):
        if rgb_or_none is None:
            btn.setStyleSheet("background-color: transparent; border: 1px dashed gray;")
            btn.setText("—")
        else:
            r, g, b = rgb_or_none
            btn.setStyleSheet(
                f"background-color: rgb({r},{g},{b}); "
                f"color: {'#000' if (r + g + b) > 400 else '#fff'}; "
                f"border: 1px solid gray;"
            )
            btn.setText("")

    def get_colors(self):
        """Return the configured colour list (3 items, each RGB tuple or None)."""
        return list(self.colors)
