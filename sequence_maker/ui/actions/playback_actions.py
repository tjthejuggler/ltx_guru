"""
Sequence Maker - Playback Actions

This module defines the PlaybackActions class, which contains playback-related actions
for the main window, such as play, pause, and stop actions.
"""

from PyQt6.QtGui import QAction, QKeySequence


class PlaybackActions:
    """Playback-related actions for the main window."""
    
    def __init__(self, main_window):
        """
        Initialize playback actions.
        
        Args:
            main_window: The main window instance.
        """
        self.main_window = main_window
        self.app = main_window.app
        self._create_actions()
    
    def _create_actions(self):
        """Create playback-related actions."""
        # Play action
        self.play_action = QAction("&Play", self.main_window)
        self.play_action.setShortcut(QKeySequence("Space"))
        self.play_action.setStatusTip("Play audio")
        self.play_action.triggered.connect(self.main_window._on_play)
        
        # Pause action
        self.pause_action = QAction("P&ause", self.main_window)
        self.pause_action.setShortcut(QKeySequence("Space"))
        self.pause_action.setStatusTip("Pause audio")
        self.pause_action.triggered.connect(self.main_window._on_pause)
        self.pause_action.setVisible(False)  # Hide initially
        
        # Stop action
        self.stop_action = QAction("&Stop", self.main_window)
        self.stop_action.setShortcut(QKeySequence("Escape"))
        self.stop_action.setStatusTip("Stop audio")
        self.stop_action.triggered.connect(self.main_window._on_stop)