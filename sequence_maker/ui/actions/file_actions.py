"""
Sequence Maker - File Actions

This module defines the FileActions class, which contains file-related actions
for the main window, such as new, open, save, and export actions.
"""

from PyQt6.QtGui import QAction, QKeySequence


class FileActions:
    """File-related actions for the main window."""
    
    def __init__(self, main_window):
        """
        Initialize file actions.
        
        Args:
            main_window: The main window instance.
        """
        self.main_window = main_window
        self.app = main_window.app
        self._create_actions()
    
    def _create_actions(self):
        """Create file-related actions."""
        # New action
        self.new_action = QAction("&New", self.main_window)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.setStatusTip("Create a new project")
        self.new_action.triggered.connect(self.main_window._on_new)
        
        # Open action
        self.open_action = QAction("&Open...", self.main_window)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.setStatusTip("Open an existing project")
        self.open_action.triggered.connect(self.main_window._on_open)
        
        # Save action
        self.save_action = QAction("&Save", self.main_window)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setStatusTip("Save the current project")
        self.save_action.triggered.connect(self.main_window._on_save)
        
        # Save As action
        self.save_as_action = QAction("Save &As...", self.main_window)
        self.save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_as_action.setStatusTip("Save the current project with a new name")
        self.save_as_action.triggered.connect(self.main_window._on_save_as)
        
        # Load Audio action
        self.load_audio_action = QAction("Load &Audio...", self.main_window)
        self.load_audio_action.setStatusTip("Load an audio file")
        self.load_audio_action.triggered.connect(self.main_window._on_load_audio)
        
        # Export actions
        self.export_json_action = QAction("Export to &JSON...", self.main_window)
        self.export_json_action.setStatusTip("Export timeline to JSON format")
        self.export_json_action.triggered.connect(self.main_window._on_export_json)
        
        self.export_prg_action = QAction("Export to &PRG...", self.main_window)
        self.export_prg_action.setStatusTip("Export timeline to PRG format")
        self.export_prg_action.triggered.connect(self.main_window._on_export_prg)
        
        # Version history action
        self.version_history_action = QAction("&Version History...", self.main_window)
        self.version_history_action.setStatusTip("View and restore previous versions")
        self.version_history_action.triggered.connect(self.main_window._on_version_history)
        
        # Exit action
        self.exit_action = QAction("E&xit", self.main_window)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.setStatusTip("Exit the application")
        self.exit_action.triggered.connect(self.main_window.close)
        
        # Ball sequence actions
        self.import_ball_sequence_action = QAction("Import Ball Sequence...", self.main_window)
        self.import_ball_sequence_action.setStatusTip("Import a ball sequence file")
        self.import_ball_sequence_action.triggered.connect(
            self.main_window.file_handler.on_import_ball_sequence
        )
        
        self.export_ball_sequence_action = QAction("Export Ball Sequence...", self.main_window)
        self.export_ball_sequence_action.setStatusTip("Export timeline to ball sequence format")
        self.export_ball_sequence_action.triggered.connect(
            self.main_window.file_handler.on_export_ball_sequence
        )
        
        self.import_lyrics_timestamps_action = QAction("Import Lyrics Timestamps...", self.main_window)
        self.import_lyrics_timestamps_action.setStatusTip("Import lyrics timestamps and convert to a timeline")
        self.import_lyrics_timestamps_action.triggered.connect(
            self.main_window.file_handler.on_import_lyrics_timestamps
        )