"""
Sequence Maker - Ball Sequence Dialog
=====================================

Dialog for the new (2026-05-06) "upload + trigger PRG sequences from your
own code" workflow. Three rows, one per timeline slot, each row offering:

* Browse for a .prg file on disk **OR** "Use timeline export" (export the
  current timeline N to a temporary .prg and upload that).
* Upload to the ball at the slot's configured IP.
* Per-row status label.

Below the rows: Play / Stop buttons, plus a "Play with audio" check box.
When "Play with audio" is checked, hitting Play will send PLAY to all
configured balls and immediately start the audio_manager. Hitting Stop
sends STOP and pauses audio.

This dialog assumes ball IPs are already configured via the existing
"Ball IPs..." menu item.
"""

from __future__ import annotations

import logging
import os
import tempfile
from typing import Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox, QDialog, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QSizePolicy, QVBoxLayout, QWidget,
)

logger = logging.getLogger("SequenceMaker.BallSequenceDialog")


# --------------------------------------------------------------------------- #
# Background upload worker (TCP send blocks for ~1s on small files,           #
# longer for big ones; do it off the UI thread).                              #
# --------------------------------------------------------------------------- #
class UploadWorker(QThread):
    finished_with = pyqtSignal(int, bool, str)  # slot_index, ok, message

    def __init__(self, ball_manager, slot_index: int, prg_path: str,
                 filename_on_ball: Optional[str], parent=None):
        super().__init__(parent)
        self.ball_manager = ball_manager
        self.slot_index = slot_index
        self.prg_path = prg_path
        self.filename_on_ball = filename_on_ball

    def run(self):
        try:
            ok = self.ball_manager.upload_prg_to_slot(
                self.slot_index, self.prg_path,
                filename_on_ball=self.filename_on_ball,
            )
            msg = "Upload OK" if ok else "Upload FAILED (see log)"
        except Exception as e:
            ok = False
            msg = f"Exception: {e}"
        self.finished_with.emit(self.slot_index, ok, msg)


# --------------------------------------------------------------------------- #
# Dialog                                                                      #
# --------------------------------------------------------------------------- #
class BallSequenceDialog(QDialog):
    NUM_SLOTS = 3

    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.setWindowTitle("Ball Sequences (Upload + Play)")
        self.setMinimumWidth(640)

        self._workers: list[Optional[UploadWorker]] = [None] * self.NUM_SLOTS
        self._tempfiles: list[Optional[str]] = [None] * self.NUM_SLOTS

        # Pause realtime UDP color streaming while this dialog is open. The
        # streaming worker (BallManager._streaming_worker) sends a color packet
        # to each ball every ~50ms based on the timeline cursor. Those packets
        # would clobber any onboard PRG playback we trigger from this dialog,
        # producing flicker / wrong colors. Remember whether streaming was
        # active so we can restore it on close.
        # (2026-05-06 fade-bug fix.)
        bm = self.app.ball_manager
        self._streaming_was_active = bool(
            getattr(bm, "streaming_thread", None)
            and bm.streaming_thread.is_alive()
        )
        if self._streaming_was_active:
            try:
                bm.stop_streaming()
                logger.info("BallSequenceDialog: paused color streaming for "
                            "onboard-PRG playback test.")
            except Exception as e:
                logger.error(f"Could not pause streaming on dialog open: {e}")

        self._build_ui()
        self._refresh_ip_labels()

    # --- UI construction -------------------------------------------------- #
    def _build_ui(self):
        layout = QVBoxLayout(self)

        intro = QLabel(
            "Upload a .prg sequence file to each ball, then play/stop them. "
            "Configure ball IPs first via File → Ball IPs."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        grid = QGridLayout()
        grid.setColumnStretch(2, 1)
        layout.addLayout(grid)

        # Header row
        for col, txt in enumerate(["Slot", "IP", "PRG file", "", "", "Status"]):
            lbl = QLabel(f"<b>{txt}</b>")
            grid.addWidget(lbl, 0, col)

        self.ip_labels: list[QLabel] = []
        self.path_edits: list[QLineEdit] = []
        self.browse_btns: list[QPushButton] = []
        self.timeline_btns: list[QPushButton] = []
        self.upload_btns: list[QPushButton] = []
        self.status_labels: list[QLabel] = []

        for i in range(self.NUM_SLOTS):
            row = i + 1
            grid.addWidget(QLabel(f"Ball {i + 1}"), row, 0)

            ip_lbl = QLabel("(no IP)")
            ip_lbl.setMinimumWidth(120)
            self.ip_labels.append(ip_lbl)
            grid.addWidget(ip_lbl, row, 1)

            edit = QLineEdit()
            edit.setPlaceholderText("Path to .prg, or use 'From timeline'")
            self.path_edits.append(edit)
            grid.addWidget(edit, row, 2)

            browse = QPushButton("Browse…")
            browse.clicked.connect(lambda _, idx=i: self._on_browse(idx))
            self.browse_btns.append(browse)
            grid.addWidget(browse, row, 3)

            tlbtn = QPushButton(f"From timeline {i + 1}")
            tlbtn.clicked.connect(lambda _, idx=i: self._on_use_timeline(idx))
            self.timeline_btns.append(tlbtn)
            grid.addWidget(tlbtn, row, 4)

            upload = QPushButton("Upload")
            upload.clicked.connect(lambda _, idx=i: self._on_upload(idx))
            self.upload_btns.append(upload)
            grid.addWidget(upload, row, 5)

            status = QLabel("idle")
            status.setMinimumWidth(120)
            self.status_labels.append(status)
            grid.addWidget(status, row, 6)

        # Bulk upload button
        bulk_row = QHBoxLayout()
        self.upload_all_btn = QPushButton("Upload All (from timelines)")
        self.upload_all_btn.clicked.connect(self._on_upload_all_from_timelines)
        bulk_row.addWidget(self.upload_all_btn)
        bulk_row.addStretch()
        layout.addLayout(bulk_row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        # Play / Stop row
        ctrl_row = QHBoxLayout()
        self.play_btn = QPushButton("▶ PLAY all balls")
        self.play_btn.setStyleSheet("padding:6px 18px; font-weight:bold;")
        self.play_btn.clicked.connect(self._on_play)
        ctrl_row.addWidget(self.play_btn)

        self.stop_btn = QPushButton("■ STOP all balls")
        self.stop_btn.setStyleSheet("padding:6px 18px; font-weight:bold;")
        self.stop_btn.clicked.connect(self._on_stop)
        ctrl_row.addWidget(self.stop_btn)

        ctrl_row.addSpacing(20)
        self.with_audio_chk = QCheckBox("Sync with audio (also start/stop the song)")
        # Default to OFF: pressing PLAY here should ONLY trigger the ball's
        # onboard PRG playback. Auto-playing the song would also advance the
        # main-window timeline cursor and re-engage the realtime UDP color
        # streaming, which fights with the on-ball PRG and produces flicker.
        # The user opts in only when they explicitly want the song too.
        self.with_audio_chk.setChecked(False)
        self.with_audio_chk.setToolTip(
            "If checked, pressing PLAY here also starts the song and advances "
            "the main-window timeline cursor. Leave unchecked to play ONLY "
            "the on-ball PRG sequence (recommended for testing fades)."
        )
        ctrl_row.addWidget(self.with_audio_chk)

        ctrl_row.addStretch()
        layout.addLayout(ctrl_row)

        # Result/status area
        self.summary_label = QLabel("")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("color:#888;")
        layout.addWidget(self.summary_label)

        # Close
        close_row = QHBoxLayout()
        close_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_row.addWidget(close_btn)
        layout.addLayout(close_row)

    # --- Helpers ---------------------------------------------------------- #
    def _refresh_ip_labels(self):
        bm = self.app.ball_manager
        for i in range(self.NUM_SLOTS):
            ip = bm._controllers[i].ip
            self.ip_labels[i].setText(ip if ip else "(no IP)")
            enabled = bool(ip)
            self.upload_btns[i].setEnabled(enabled)

    def _set_status(self, slot: int, txt: str, ok: Optional[bool] = None):
        self.status_labels[slot].setText(txt)
        if ok is True:
            self.status_labels[slot].setStyleSheet("color: #2c8a2c;")
        elif ok is False:
            self.status_labels[slot].setStyleSheet("color: #c83c3c;")
        else:
            self.status_labels[slot].setStyleSheet("")

    def _cleanup_tempfile(self, slot: int):
        path = self._tempfiles[slot]
        if path and os.path.exists(path):
            try:
                os.unlink(path)
            except OSError:
                pass
        self._tempfiles[slot] = None

    # --- Slot actions ----------------------------------------------------- #
    def _on_browse(self, slot: int):
        path, _ = QFileDialog.getOpenFileName(
            self, f"Select .prg for ball {slot + 1}",
            "", "PRG sequences (*.prg);;All files (*)",
        )
        if path:
            self.path_edits[slot].setText(path)
            self._set_status(slot, "ready")

    def _on_use_timeline(self, slot: int):
        """Export the corresponding timeline to a temp .prg."""
        project = self.app.project_manager.current_project
        if not project:
            QMessageBox.warning(self, "No project", "Open or create a project first.")
            return
        if slot >= len(project.timelines):
            QMessageBox.warning(self, "No timeline",
                                f"Project has no timeline {slot + 1}.")
            return
        timeline = project.timelines[slot]

        # Use the existing exporter
        from export.prg_exporter import PRGExporter
        exporter = PRGExporter(self.app)

        # Generate temp path
        fd, tmp_path = tempfile.mkstemp(suffix=f"_Ball_{slot + 1}.prg",
                                        prefix="sm_export_")
        os.close(fd)

        self._set_status(slot, "exporting…")
        try:
            ok = exporter.export_timeline(timeline, tmp_path)
        except Exception as e:
            ok = False
            logger.exception("export failed")
            self._set_status(slot, f"export err: {e}", ok=False)
            return
        if not ok or not os.path.isfile(tmp_path) or os.path.getsize(tmp_path) == 0:
            self._set_status(slot, "export failed", ok=False)
            return

        # Stash for cleanup; clear any previous
        self._cleanup_tempfile(slot)
        self._tempfiles[slot] = tmp_path
        self.path_edits[slot].setText(tmp_path)
        self._set_status(slot, f"exported {os.path.getsize(tmp_path)} B", ok=True)

    def _on_upload(self, slot: int):
        path = self.path_edits[slot].text().strip()
        if not path:
            QMessageBox.warning(self, "No file", "Choose a .prg file first.")
            return
        if not os.path.isfile(path):
            QMessageBox.warning(self, "File missing", f"Not found:\n{path}")
            return
        if self._workers[slot] is not None:
            return  # already uploading

        # Build a stable filename to store on the ball
        project = self.app.project_manager.current_project
        if project and project.name:
            base = "".join(c if (c.isalnum() or c in "._-") else "_"
                           for c in project.name)
            filename_on_ball = f"{base}_Ball_{slot + 1}.prg"
        else:
            filename_on_ball = os.path.basename(path)

        self._set_status(slot, "uploading…")
        self.upload_btns[slot].setEnabled(False)

        worker = UploadWorker(self.app.ball_manager, slot, path, filename_on_ball, self)
        worker.finished_with.connect(self._on_upload_done)
        self._workers[slot] = worker
        worker.start()

    def _on_upload_done(self, slot: int, ok: bool, msg: str):
        self._set_status(slot, msg, ok=ok)
        self.upload_btns[slot].setEnabled(True)
        worker = self._workers[slot]
        if worker is not None:
            worker.deleteLater()
            self._workers[slot] = None

    def _on_upload_all_from_timelines(self):
        """Convenience: export each timeline → upload to its slot."""
        bm = self.app.ball_manager
        any_started = False
        for i in range(self.NUM_SLOTS):
            if not bm._controllers[i].ip:
                continue
            self._on_use_timeline(i)
            # Only upload if export succeeded (path now points to a tmp file)
            if self._tempfiles[i] and os.path.isfile(self._tempfiles[i]):
                self._on_upload(i)
                any_started = True
        if not any_started:
            QMessageBox.information(self, "Nothing to upload",
                                    "No slots have an IP configured, or no timelines exist.")

    # --- Play/Stop -------------------------------------------------------- #
    def _on_play(self):
        bm = self.app.ball_manager
        result = bm.play_balls()
        if not result:
            self.summary_label.setText("No balls configured. Set Ball IPs first.")
            return

        self.summary_label.setText(
            "PLAY sent → " +
            ", ".join(f"{ip}:{'ok' if ok else 'FAIL'}" for ip, ok in result.items())
        )

        if self.with_audio_chk.isChecked():
            try:
                self.app.audio_manager.play()
            except Exception as e:
                logger.error(f"audio_manager.play() failed: {e}")

    def _on_stop(self):
        bm = self.app.ball_manager
        result = bm.stop_balls()
        if not result:
            self.summary_label.setText("No balls configured.")
            return

        self.summary_label.setText(
            "STOP sent → " +
            ", ".join(f"{ip}:{'ok' if ok else 'FAIL'}" for ip, ok in result.items())
        )

        if self.with_audio_chk.isChecked():
            try:
                self.app.audio_manager.pause()
            except Exception as e:
                logger.error(f"audio_manager.pause() failed: {e}")

    # --- Lifecycle -------------------------------------------------------- #
    def closeEvent(self, event):
        # Don't kill running uploads, but free temp files
        for i in range(self.NUM_SLOTS):
            self._cleanup_tempfile(i)

        # Restore realtime UDP color streaming if it was active when we opened.
        if getattr(self, "_streaming_was_active", False):
            try:
                self.app.ball_manager.start_streaming()
                logger.info("BallSequenceDialog: resumed color streaming "
                            "after dialog close.")
            except Exception as e:
                logger.error(f"Could not resume streaming on dialog close: {e}")

        super().closeEvent(event)
        super().closeEvent(event)
