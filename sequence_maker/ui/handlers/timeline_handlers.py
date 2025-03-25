"""
Sequence Maker - Timeline Handlers

This module defines the TimelineHandlers class, which contains handlers for timeline-related
operations such as add, remove, and duplicate timeline operations.
"""

from PyQt6.QtWidgets import QInputDialog, QMessageBox


class TimelineHandlers:
    """Timeline operation handlers for the main window."""
    
    def __init__(self, main_window):
        """
        Initialize timeline handlers.
        
        Args:
            main_window: The main window instance.
        """
        self.main_window = main_window
        self.app = main_window.app
    
    def on_add_timeline(self):
        """Add a new timeline."""
        # Get timeline name from user
        name, ok = QInputDialog.getText(
            self.main_window,
            "Add Timeline",
            "Timeline name:",
            text=f"Ball {len(self.app.timeline_manager.get_timelines()) + 1}"
        )
        
        if ok and name:
            # Add timeline
            timeline = self.app.timeline_manager.add_timeline(name)
            
            # Select the new timeline
            if self.main_window.timeline_widget and timeline:
                self.main_window.timeline_widget.select_timeline(timeline)
    
    def on_remove_timeline(self):
        """Remove the selected timeline."""
        # Check if a timeline is selected
        if not self.main_window.timeline_widget.selected_timeline:
            QMessageBox.warning(
                self.main_window,
                "No Timeline Selected",
                "Please select a timeline to remove."
            )
            return
        
        # Confirm removal
        reply = QMessageBox.question(
            self.main_window,
            "Remove Timeline",
            f"Are you sure you want to remove the timeline '{self.main_window.timeline_widget.selected_timeline.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove timeline
            self.app.timeline_manager.remove_timeline(self.main_window.timeline_widget.selected_timeline)
    
    def on_duplicate_timeline(self):
        """Duplicate the selected timeline."""
        # Check if a timeline is selected
        if not self.main_window.timeline_widget.selected_timeline:
            QMessageBox.warning(
                self.main_window,
                "No Timeline Selected",
                "Please select a timeline to duplicate."
            )
            return
        
        # Duplicate timeline
        new_timeline = self.app.timeline_manager.duplicate_timeline(self.main_window.timeline_widget.selected_timeline)
        
        # Select the new timeline
        if self.main_window.timeline_widget and new_timeline:
            self.main_window.timeline_widget.select_timeline(new_timeline)