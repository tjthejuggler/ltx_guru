"""
Sequence Maker - Boundary Handlers

This module defines the BoundaryHandlers class, which contains handlers for boundary-related
operations such as editing boundary properties and applying changes to boundaries.
"""


class BoundaryHandlers:
    """Boundary operation handlers for the main window."""
    
    def __init__(self, main_window):
        """
        Initialize boundary handlers.
        
        Args:
            main_window: The main window instance.
        """
        self.main_window = main_window
        self.app = main_window.app
    
    def show_boundary_editor(self, timeline, time, left_segment, right_segment):
        """
        Show the boundary editor.
        
        Args:
            timeline: The timeline containing the boundary.
            time: The time position of the boundary.
            left_segment: The segment to the left of the boundary.
            right_segment: The segment to the right of the boundary.
        """
        # Show boundary editor UI
        self.main_window.boundary_editor_widget.setVisible(True)
        
        # Set current boundary
        self.main_window.current_boundary_timeline = timeline
        self.main_window.current_boundary_time = time
        self.main_window.current_boundary_segments = (left_segment, right_segment)
        
        # Update editor fields
        self.main_window.boundary_time_edit.setText(
            self.main_window.utility_handlers._format_seconds_to_hms(time)
        )
    
    def hide_boundary_editor(self):
        """Hide the boundary editor."""
        self.main_window.boundary_editor_widget.setVisible(False)
        self.main_window.current_boundary_timeline = None
        self.main_window.current_boundary_time = None
        self.main_window.current_boundary_segments = (None, None)
    
    def on_boundary_time_changed(self):
        """Handle boundary time changed."""
        if (not self.main_window.current_boundary_timeline or
                self.main_window.current_boundary_time is None or
                not all(self.main_window.current_boundary_segments)):
            return
        
        # Get text from edit field
        text = self.main_window.boundary_time_edit.toPlainText()
        
        # Parse time
        time_value = self.main_window.utility_handlers._parse_time_from_text(text)
        
        if time_value is not None:
            # Get current boundary info
            timeline = self.main_window.current_boundary_timeline
            left_segment, right_segment = self.main_window.current_boundary_segments
            
            # Save state for undo
            if self.app.undo_manager:
                self.app.undo_manager.save_state("modify_boundary")
            
            # Update segments
            self.app.timeline_manager.modify_segment(
                timeline,
                left_segment,
                end_time=time_value
            )
            
            self.app.timeline_manager.modify_segment(
                timeline,
                right_segment,
                start_time=time_value
            )
            
            # Update current boundary time
            self.main_window.current_boundary_time = time_value
    
    def on_boundary_time_apply(self):
        """Apply boundary time."""
        self.on_boundary_time_changed()