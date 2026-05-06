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
        # Zoom In action.
        # We use the literal "Ctrl+=" shortcut (not QKeySequence.StandardKey.ZoomIn)
        # because StandardKey.ZoomIn maps to "Ctrl++" on Linux, which on a US
        # keyboard literally requires Ctrl+Shift+= - users naturally press Ctrl+=
        # without Shift, so the standard key binding never fires.
        # We deliberately register only ONE shortcut here: registering multiple
        # overlapping shortcuts on the same QAction can make Qt treat them as
        # ambiguous and require a second keypress to disambiguate, which feels
        # laggy.
        self.zoom_in_action = QAction("Zoom &In", self.main_window)
        self.zoom_in_action.setShortcut(QKeySequence("Ctrl+="))
        self.zoom_in_action.setStatusTip("Zoom in on the timeline")
        self.zoom_in_action.triggered.connect(self.main_window._on_zoom_in)

        # Zoom Out action - "Ctrl+-" is unambiguous and matches what most apps use.
        self.zoom_out_action = QAction("Zoom &Out", self.main_window)
        self.zoom_out_action.setShortcut(QKeySequence("Ctrl+-"))
        self.zoom_out_action.setStatusTip("Zoom out on the timeline")
        self.zoom_out_action.triggered.connect(self.main_window._on_zoom_out)
        
        # Zoom Fit action
        self.zoom_fit_action = QAction("&Fit to Window", self.main_window)
        self.zoom_fit_action.setShortcut("Ctrl+0")
        self.zoom_fit_action.setStatusTip("Fit the timeline to the window")
        self.zoom_fit_action.triggered.connect(self.main_window._on_zoom_fit)