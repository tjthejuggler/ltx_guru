"""
Sequence Maker - Ball IP Dialog

Dialog for entering IP addresses for the three LED balls.
IPs are persisted in the app config under ball_control.ball_ips.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QDialogButtonBox, QFormLayout
)
from PyQt6.QtCore import Qt

logger = logging.getLogger("SequenceMaker.BallIPDialog")


class BallIPDialog(QDialog):
    """Dialog for configuring IP addresses of the three LED balls."""

    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.setWindowTitle("Ball IP Addresses")
        self.setModal(True)
        self.setMinimumWidth(320)
        self._create_ui()
        self._load_ips()

    def _create_ui(self):
        layout = QVBoxLayout(self)

        info = QLabel(
            "Enter the IP address for each ball.\n"
            "Leave blank to disable sending to that ball."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        form = QFormLayout()
        self.ip_edits = []
        for i in range(3):
            edit = QLineEdit()
            edit.setPlaceholderText("e.g. 10.122.252.133")
            form.addRow(f"Ball {i + 1} IP:", edit)
            self.ip_edits.append(edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_ips(self):
        """Load saved IPs from config."""
        ball_ips = self.app.config.get("ball_control", "ball_ips", ["", "", ""])
        for i, edit in enumerate(self.ip_edits):
            if i < len(ball_ips):
                edit.setText(ball_ips[i])

    def _save_and_accept(self):
        """Save IPs to config and close."""
        ball_ips = [edit.text().strip() for edit in self.ip_edits]
        self.app.config.set("ball_control", "ball_ips", ball_ips)
        self.app.config.save()

        # Push IPs into the ball manager controllers
        self.app.ball_manager.set_ball_ips(ball_ips)

        logger.info(f"Ball IPs saved: {ball_ips}")
        self.accept()
