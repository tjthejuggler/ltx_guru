"""
Sequence Maker - Sequence Swap Manager

Watches for new sequences delivered by the Roocode Sequence Designer mode.
When a new .smproj file is placed in the swap inbox, this manager:
1. Auto-saves the current project
2. Loads the new sequence into the GUI
3. Displays the sequence description

The swap inbox is: ~/.sequence_maker/sequence_swap_inbox.json

The inbox JSON format:
{
    "smproj_path": "/absolute/path/to/new_sequence.smproj",
    "description": "Human-readable description of the sequence",
    "timestamp": "2026-04-03T17:30:00",
    "version_name": "v1_beat_sync"
}
"""

import json
import logging
import os
from pathlib import Path

from PyQt6.QtCore import QObject, QFileSystemWatcher, pyqtSignal


SWAP_INBOX_DIR = Path.home() / ".sequence_maker"
SWAP_INBOX_FILE = SWAP_INBOX_DIR / "sequence_swap_inbox.json"


class SequenceSwapManager(QObject):
    """
    Manages hot-swapping sequences from the Roocode Sequence Designer.

    Watches the swap inbox file for changes. When the Sequence Designer
    writes a new entry, this manager auto-saves the current project and
    loads the new sequence.

    Signals:
        sequence_swapped(str): Emitted with the sequence description after
                               a successful swap.
        swap_failed(str): Emitted with an error message if the swap fails.
    """

    sequence_swapped = pyqtSignal(str)  # description
    swap_failed = pyqtSignal(str)       # error message

    def __init__(self, app):
        """
        Initialize the sequence swap manager.

        Args:
            app: The main application instance (SequenceMakerApp).
        """
        super().__init__()
        self.logger = logging.getLogger("SequenceMaker.SequenceSwapManager")
        self.app = app

        # Track the last processed timestamp to avoid re-processing
        self._last_processed_timestamp = None

        # Ensure inbox directory exists
        SWAP_INBOX_DIR.mkdir(parents=True, exist_ok=True)

        # Create the inbox file if it doesn't exist
        if not SWAP_INBOX_FILE.exists():
            self._write_empty_inbox()

        # Set up file watcher
        self._watcher = QFileSystemWatcher()
        self._watcher.addPath(str(SWAP_INBOX_FILE))
        self._watcher.fileChanged.connect(self._on_inbox_changed)

        self.logger.info(f"Sequence swap manager initialized, watching: {SWAP_INBOX_FILE}")

    def _write_empty_inbox(self):
        """Write an empty inbox file."""
        try:
            with open(SWAP_INBOX_FILE, 'w') as f:
                json.dump({}, f)
        except Exception as e:
            self.logger.error(f"Failed to create inbox file: {e}")

    def _on_inbox_changed(self, path):
        """Handle inbox file changes."""
        self.logger.info("Swap inbox changed, checking for new sequence...")

        # Re-add the watch (QFileSystemWatcher drops the path after some edits)
        if str(SWAP_INBOX_FILE) not in self._watcher.files():
            self._watcher.addPath(str(SWAP_INBOX_FILE))

        try:
            if not SWAP_INBOX_FILE.exists():
                return

            with open(SWAP_INBOX_FILE, 'r') as f:
                data = json.load(f)

            # Validate required fields
            smproj_path = data.get("smproj_path")
            description = data.get("description", "")
            timestamp = data.get("timestamp", "")

            if not smproj_path:
                self.logger.debug("Inbox is empty or has no smproj_path, ignoring.")
                return

            # Skip if we already processed this timestamp
            if timestamp and timestamp == self._last_processed_timestamp:
                self.logger.debug("Already processed this inbox entry, skipping.")
                return

            # Validate the .smproj file exists
            if not os.path.exists(smproj_path):
                error_msg = f"Sequence file not found: {smproj_path}"
                self.logger.error(error_msg)
                self.swap_failed.emit(error_msg)
                return

            self.logger.info(f"Loading new sequence from: {smproj_path}")
            self.logger.info(f"Description: {description}")

            # Step 1: Auto-save current project
            self._auto_save_current()

            # Step 2: Load the new project
            try:
                self.app.project_manager.load_project(smproj_path)
                self.logger.info("New sequence loaded successfully.")
            except Exception as e:
                error_msg = f"Failed to load sequence: {e}"
                self.logger.error(error_msg)
                self.swap_failed.emit(error_msg)
                return

            # Step 3: Mark as processed
            self._last_processed_timestamp = timestamp

            # Step 4: Emit success signal with description
            self.sequence_swapped.emit(description)

        except json.JSONDecodeError as e:
            self.logger.warning(f"Invalid JSON in swap inbox: {e}")
        except Exception as e:
            error_msg = f"Error processing swap inbox: {e}"
            self.logger.error(error_msg)
            self.swap_failed.emit(error_msg)

    def _auto_save_current(self):
        """Auto-save the current project before swapping."""
        try:
            project = self.app.project_manager.current_project
            if project and project.file_path:
                self.logger.info(f"Auto-saving current project: {project.file_path}")
                self.app.project_manager.save_project()
            elif project:
                # Project exists but has no file path — save to autosave dir
                from datetime import datetime
                autosave_dir = SWAP_INBOX_DIR / "pre_swap_backups"
                autosave_dir.mkdir(parents=True, exist_ok=True)
                backup_name = f"pre_swap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.smproj"
                backup_path = str(autosave_dir / backup_name)
                self.logger.info(f"Auto-saving unsaved project to: {backup_path}")
                self.app.project_manager.save_project(backup_path)
        except Exception as e:
            self.logger.warning(f"Auto-save before swap failed: {e}")

    def cleanup(self):
        """Clean up the file watcher."""
        if self._watcher:
            self._watcher.removePath(str(SWAP_INBOX_FILE))
