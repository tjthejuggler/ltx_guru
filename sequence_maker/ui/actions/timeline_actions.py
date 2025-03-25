"""
Sequence Maker - Timeline Actions

This module defines the TimelineActions class, which contains timeline-related actions
for the main window, such as add, remove, and duplicate timeline actions.
"""

from PyQt6.QtGui import QAction


class TimelineActions:
    """Timeline-related actions for the main window."""
    
    def __init__(self, main_window):
        """
        Initialize timeline actions.
        
        Args:
            main_window: The main window instance.
        """
        self.main_window = main_window
        self.app = main_window.app
        self._create_actions()
    
    def _create_actions(self):
        """Create timeline-related actions."""
        # Add Timeline action
        self.add_timeline_action = QAction("&Add Timeline", self.main_window)
        self.add_timeline_action.setStatusTip("Add a new timeline")
        self.add_timeline_action.triggered.connect(self.main_window._on_add_timeline)
        
        # Remove Timeline action
        self.remove_timeline_action = QAction("&Remove Timeline", self.main_window)
        self.remove_timeline_action.setStatusTip("Remove the selected timeline")
        self.remove_timeline_action.triggered.connect(self.main_window._on_remove_timeline)
        
        # Duplicate Timeline action
        self.duplicate_timeline_action = QAction("&Duplicate Timeline", self.main_window)
        self.duplicate_timeline_action.setStatusTip("Duplicate the selected timeline")
        self.duplicate_timeline_action.triggered.connect(self.main_window._on_duplicate_timeline)