"""
Sequence Maker - Bulk Swap Dialog

Dialog for bulk swapping colors across the project or a time range.
Supports multiple color pairs that are applied simultaneously so that
swapping red↔green works correctly in a single pass.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QColorDialog, QDialogButtonBox, QGroupBox,
    QRadioButton, QButtonGroup, QDoubleSpinBox, QScrollArea,
    QWidget, QGridLayout, QFrame, QSizePolicy,
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, pyqtSignal

# Standard quick-pick colours (same as zero_key_color_dialog)
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


class ColorPickerPopup(QWidget):
    """A popup widget that shows common + project colors for quick selection."""

    color_selected = pyqtSignal(tuple)  # RGB tuple

    def __init__(self, project_colors=None, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.project_colors = project_colors or []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        # Common colors
        common_label = QLabel("Common Colors")
        common_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        layout.addWidget(common_label)

        common_grid = QGridLayout()
        common_grid.setSpacing(2)
        for i, (rgb, name) in enumerate(QUICK_COLORS):
            btn = QPushButton()
            btn.setFixedSize(32, 24)
            btn.setToolTip(name)
            r, g, b = rgb
            btn.setStyleSheet(
                f"background-color: rgb({r},{g},{b}); "
                f"border: 1px solid #888;"
            )
            btn.clicked.connect(lambda checked, c=rgb: self._pick(c))
            common_grid.addWidget(btn, i // 5, i % 5)
        layout.addLayout(common_grid)

        # Project-specific colors
        if self.project_colors:
            proj_label = QLabel("Project Colors")
            proj_label.setStyleSheet("font-weight: bold; font-size: 11px;")
            layout.addWidget(proj_label)

            proj_grid = QGridLayout()
            proj_grid.setSpacing(2)
            for i, rgb in enumerate(self.project_colors):
                btn = QPushButton()
                btn.setFixedSize(32, 24)
                r, g, b = rgb
                btn.setToolTip(f"({r}, {g}, {b})")
                btn.setStyleSheet(
                    f"background-color: rgb({r},{g},{b}); "
                    f"border: 1px solid #888;"
                )
                btn.clicked.connect(lambda checked, c=rgb: self._pick(c))
                proj_grid.addWidget(btn, i // 5, i % 5)
            layout.addLayout(proj_grid)

        # Custom color button
        custom_btn = QPushButton("Custom…")
        custom_btn.clicked.connect(self._pick_custom)
        layout.addWidget(custom_btn)

    def _pick(self, rgb):
        self.color_selected.emit(rgb)
        self.close()

    def _pick_custom(self):
        color = QColorDialog.getColor(QColor(255, 255, 255), self, "Choose Color")
        if color.isValid():
            self.color_selected.emit((color.red(), color.green(), color.blue()))
        self.close()


class ColorPairRow(QWidget):
    """A single color-pair row: [from_color] → [to_color] [remove]."""

    remove_requested = pyqtSignal(object)  # self

    def __init__(self, from_color=None, to_color=None, project_colors=None, parent=None):
        super().__init__(parent)
        self.from_color = from_color or (255, 0, 0)
        self.to_color = to_color or (0, 255, 0)
        self.project_colors = project_colors or []
        self._popup = None
        self._active_target = None  # 'from' or 'to'
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # From color button
        self.from_btn = QPushButton()
        self.from_btn.setFixedSize(60, 30)
        self.from_btn.clicked.connect(lambda: self._open_picker("from"))
        self._update_btn_style(self.from_btn, self.from_color)
        layout.addWidget(self.from_btn)

        arrow = QLabel("→")
        arrow.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(arrow)

        # To color button
        self.to_btn = QPushButton()
        self.to_btn.setFixedSize(60, 30)
        self.to_btn.clicked.connect(lambda: self._open_picker("to"))
        self._update_btn_style(self.to_btn, self.to_color)
        layout.addWidget(self.to_btn)

        layout.addStretch()

        # Remove button
        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(28, 28)
        remove_btn.setStyleSheet("color: #cc0000; font-weight: bold;")
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(remove_btn)

    def _update_btn_style(self, btn, rgb):
        r, g, b = rgb
        btn.setStyleSheet(
            f"background-color: rgb({r},{g},{b}); "
            f"border: 2px solid #555;"
        )

    def _open_picker(self, target):
        self._active_target = target
        current = self.from_color if target == "from" else self.to_color
        self._popup = ColorPickerPopup(self.project_colors, self)
        self._popup.color_selected.connect(self._on_color_selected)
        # Position popup near the button
        btn = self.from_btn if target == "from" else self.to_btn
        pos = btn.mapToGlobal(btn.rect().bottomLeft())
        self._popup.move(pos)
        self._popup.show()

    def _on_color_selected(self, rgb):
        if self._active_target == "from":
            self.from_color = rgb
            self._update_btn_style(self.from_btn, rgb)
        else:
            self.to_color = rgb
            self._update_btn_style(self.to_btn, rgb)

    def get_pair(self):
        return (self.from_color, self.to_color)


class BulkSwapDialog(QDialog):
    """Dialog for bulk color swapping across timelines."""

    def __init__(self, project_colors=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bulk Color Swap")
        self.setMinimumWidth(450)
        self.project_colors = project_colors or []
        self.pair_rows = []
        self._build_ui()
        # Add one default pair
        self._add_pair()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Scope selection
        scope_group = QGroupBox("Scope")
        scope_layout = QVBoxLayout(scope_group)

        self.scope_group = QButtonGroup(self)
        self.entire_project_radio = QRadioButton("Entire Project")
        self.entire_project_radio.setChecked(True)
        self.time_range_radio = QRadioButton("Time Range")
        self.scope_group.addButton(self.entire_project_radio)
        self.scope_group.addButton(self.time_range_radio)
        scope_layout.addWidget(self.entire_project_radio)
        scope_layout.addWidget(self.time_range_radio)

        # Time range inputs
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Start:"))
        self.start_time_spin = QDoubleSpinBox()
        self.start_time_spin.setRange(0.0, 99999.0)
        self.start_time_spin.setDecimals(2)
        self.start_time_spin.setSuffix(" s")
        self.start_time_spin.setEnabled(False)
        time_layout.addWidget(self.start_time_spin)

        time_layout.addWidget(QLabel("End:"))
        self.end_time_spin = QDoubleSpinBox()
        self.end_time_spin.setRange(0.0, 99999.0)
        self.end_time_spin.setDecimals(2)
        self.end_time_spin.setSuffix(" s")
        self.end_time_spin.setEnabled(False)
        time_layout.addWidget(self.end_time_spin)

        scope_layout.addLayout(time_layout)
        self.time_range_radio.toggled.connect(self._on_scope_changed)
        layout.addWidget(scope_group)

        # Color pairs
        pairs_group = QGroupBox("Color Pairs")
        pairs_layout = QVBoxLayout(pairs_group)

        header = QHBoxLayout()
        header.addWidget(QLabel("From"))
        header.addSpacing(30)
        header.addWidget(QLabel("To"))
        header.addStretch()
        pairs_layout.addLayout(header)

        # Scroll area for pairs
        self.pairs_container = QWidget()
        self.pairs_layout = QVBoxLayout(self.pairs_container)
        self.pairs_layout.setContentsMargins(0, 0, 0, 0)
        self.pairs_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(self.pairs_container)
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(250)
        pairs_layout.addWidget(scroll)

        # Add pair button
        add_btn = QPushButton("+ Add Color Pair")
        add_btn.clicked.connect(self._add_pair)
        pairs_layout.addWidget(add_btn)

        layout.addWidget(pairs_group)

        # OK / Cancel
        bbox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)
        layout.addWidget(bbox)

    def _on_scope_changed(self, checked):
        self.start_time_spin.setEnabled(checked)
        self.end_time_spin.setEnabled(checked)

    def _add_pair(self):
        row = ColorPairRow(project_colors=self.project_colors, parent=self)
        row.remove_requested.connect(self._remove_pair)
        # Insert before the stretch at the end
        self.pairs_layout.insertWidget(
            self.pairs_layout.count() - 1, row
        )
        self.pair_rows.append(row)

    def _remove_pair(self, row):
        if len(self.pair_rows) <= 1:
            return  # Keep at least one pair
        self.pairs_layout.removeWidget(row)
        row.deleteLater()
        self.pair_rows.remove(row)

    def get_config(self):
        """Return the dialog configuration as a dict.

        Returns:
            dict with keys:
                scope: 'entire_project' or 'time_range'
                start_time: float (only if scope == 'time_range')
                end_time: float (only if scope == 'time_range')
                color_pairs: list of (from_rgb, to_rgb) tuples
        """
        config = {
            "scope": (
                "entire_project"
                if self.entire_project_radio.isChecked()
                else "time_range"
            ),
            "color_pairs": [row.get_pair() for row in self.pair_rows],
        }
        if config["scope"] == "time_range":
            config["start_time"] = self.start_time_spin.value()
            config["end_time"] = self.end_time_spin.value()
        return config
