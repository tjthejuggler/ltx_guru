"""
Sequence Maker - View Actions

This module defines the ViewActions class, which contains view-related actions
for the main window, such as zoom in, zoom out, and zoom fit actions.
"""

from PyQt6.QtGui import QAction, QKeySequence


class ViewActions:
    """View-related actions for the main window."""
    
    def __init__(self, main_window):
        """
        Initialize view actions.
        
        Args:
            main_window: The main window instance.
        """
        self.main_window = main_window
        self.app = main_window.app
        self._create_actions()
    
    def _create_actions(self):
        """Create view-related actions."""
        # Zoom In action
        self.zoom_in_action = QAction("Zoom &In", self.main_window)
        self.zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        self.zoom_in_action.setStatusTip("Zoom in on the timeline")
        self.zoom_in_action.triggered.connect(self.main_window._on_zoom_in)
        
        # Zoom Out action
        self.zoom_out_action = QAction("Zoom &Out", self.main_window)
        self.zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        self.zoom_out_action.setStatusTip("Zoom out on the timeline")
        self.zoom_out_action.triggered.connect(self.main_window._on_zoom_out)
        
        # Zoom Fit action
        self.zoom_fit_action = QAction("&Fit to Window", self.main_window)
        self.zoom_fit_action.setShortcut("Ctrl+0")
        self.zoom_fit_action.setStatusTip("Fit the timeline to the window")
        self.zoom_fit_action.triggered.connect(self.main_window._on_zoom_fit)