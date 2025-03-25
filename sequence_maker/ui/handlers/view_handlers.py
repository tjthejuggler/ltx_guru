"""
Sequence Maker - View Handlers

This module defines the ViewHandlers class, which contains handlers for view-related
operations such as zoom in, zoom out, and zoom fit operations.
"""


class ViewHandlers:
    """View operation handlers for the main window."""
    
    def __init__(self, main_window):
        """
        Initialize view handlers.
        
        Args:
            main_window: The main window instance.
        """
        self.main_window = main_window
        self.app = main_window.app
    
    def on_zoom_in(self):
        """Zoom in on the timeline."""
        if self.main_window.timeline_widget:
            self.main_window.timeline_widget.zoom_in()
    
    def on_zoom_out(self):
        """Zoom out on the timeline."""
        if self.main_window.timeline_widget:
            self.main_window.timeline_widget.zoom_out()
    
    def on_zoom_fit(self):
        """Fit the timeline to the window."""
        if self.main_window.timeline_widget:
            self.main_window.timeline_widget.zoom_fit()