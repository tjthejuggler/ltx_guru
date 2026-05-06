"""
Sequence Maker - Set Max Time Dialog

This module defines the SetMaxTimeDialog class, which lets the user set the
maximum duration (length) of the project's timelines. This controls how far
the timelines extend visually so there isn't a bunch of unused empty space
beyond the end of the song.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QDoubleSpinBox, QSpinBox, QPushButton, QDialogButtonBox, QCheckBox
)
from PyQt6.QtCore import Qt


class SetMaxTimeDialog(QDialog):
    """
    Dialog for setting the maximum project timeline duration.

    The user can enter the duration as either:
      * Total seconds (with 0.01s precision)
      * Minutes + seconds combo

    The two inputs are kept in sync.
    """

    # Hard upper bound (24 hours). Plenty for any song.
    MAX_SECONDS = 24 * 60 * 60
    # Minimum 1 second (we don't want a 0-length timeline).
    MIN_SECONDS = 1.0

    def __init__(self, current_duration, parent=None):
        """
        Initialize the dialog.

        Args:
            current_duration (float): The project's current total duration in seconds.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Set Max Time")
        self.setModal(True)
        self.resize(360, 180)

        # Clamp the incoming value into our allowed range
        clamped = max(self.MIN_SECONDS, min(self.MAX_SECONDS, float(current_duration or 0)))

        self._suppress_sync = False  # avoid feedback loops between the two inputs
        self._build_ui(clamped)

    # ------------------------------------------------------------------ UI

    def _build_ui(self, current_seconds):
        layout = QVBoxLayout(self)

        info_label = QLabel(
            "Set the maximum duration of the project. The timelines will "
            "extend exactly this far. You can change this any time."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        form = QFormLayout()

        # Minutes + seconds combo (the friendly way)
        mm_ss_row = QHBoxLayout()
        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, self.MAX_SECONDS // 60)
        self.minutes_spin.setSuffix(" min")
        self.seconds_spin = QDoubleSpinBox()
        self.seconds_spin.setRange(0.0, 59.99)
        self.seconds_spin.setDecimals(2)
        self.seconds_spin.setSingleStep(1.0)
        self.seconds_spin.setSuffix(" sec")
        mm_ss_row.addWidget(self.minutes_spin)
        mm_ss_row.addWidget(self.seconds_spin)
        mm_ss_row.addStretch(1)
        form.addRow("Duration:", mm_ss_row)

        # Total seconds (the precise way)
        self.total_seconds_spin = QDoubleSpinBox()
        self.total_seconds_spin.setRange(self.MIN_SECONDS, self.MAX_SECONDS)
        self.total_seconds_spin.setDecimals(2)
        self.total_seconds_spin.setSingleStep(1.0)
        self.total_seconds_spin.setSuffix(" sec total")
        form.addRow("Or in seconds:", self.total_seconds_spin)

        layout.addLayout(form)

        # Checkbox: also trim segments past the new max
        self.trim_checkbox = QCheckBox(
            "Also trim/remove timeline segments that extend past the new max"
        )
        self.trim_checkbox.setChecked(False)
        self.trim_checkbox.setToolTip(
            "If checked, segments that go past the new max time will be cut "
            "or removed. If unchecked, only the visible timeline length changes."
        )
        layout.addWidget(self.trim_checkbox)

        # OK / Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Wire up sync between the two inputs
        self.minutes_spin.valueChanged.connect(self._on_mmss_changed)
        self.seconds_spin.valueChanged.connect(self._on_mmss_changed)
        self.total_seconds_spin.valueChanged.connect(self._on_total_changed)

        # Initialise values
        self._set_total_seconds(current_seconds)

    # ------------------------------------------------------------------ sync

    def _on_mmss_changed(self, _):
        if self._suppress_sync:
            return
        total = self.minutes_spin.value() * 60 + self.seconds_spin.value()
        if total < self.MIN_SECONDS:
            total = self.MIN_SECONDS
        self._suppress_sync = True
        try:
            self.total_seconds_spin.setValue(total)
        finally:
            self._suppress_sync = False

    def _on_total_changed(self, value):
        if self._suppress_sync:
            return
        self._suppress_sync = True
        try:
            minutes = int(value // 60)
            seconds = value - minutes * 60
            self.minutes_spin.setValue(minutes)
            self.seconds_spin.setValue(seconds)
        finally:
            self._suppress_sync = False

    def _set_total_seconds(self, value):
        """Set both inputs from a total-seconds value, without recursion."""
        self._suppress_sync = True
        try:
            self.total_seconds_spin.setValue(value)
            minutes = int(value // 60)
            seconds = value - minutes * 60
            self.minutes_spin.setValue(minutes)
            self.seconds_spin.setValue(seconds)
        finally:
            self._suppress_sync = False

    # ------------------------------------------------------------------ API

    def get_max_time(self):
        """Return the user's chosen max time in seconds."""
        return float(self.total_seconds_spin.value())

    def get_trim_segments(self):
        """Return whether the user wants to trim segments past the new max."""
        return self.trim_checkbox.isChecked()
