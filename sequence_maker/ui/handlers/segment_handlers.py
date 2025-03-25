"""
Sequence Maker - Segment Handlers

This module defines the SegmentHandlers class, which contains handlers for segment-related
operations such as editing segment properties and applying changes to segments.
"""

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QColor


class SegmentHandlers:
    """Segment operation handlers for the main window."""
    
    def __init__(self, main_window):
        """
        Initialize segment handlers.
        
        Args:
            main_window: The main window instance.
        """
        self.main_window = main_window
        self.app = main_window.app
    
    def show_segment_editor(self, timeline, segment):
        """
        Show the segment editor.
        
        Args:
            timeline: The timeline containing the segment.
            segment: The segment to edit.
        """
        # Show segment editor UI
        self.main_window.segment_editor_widget.setVisible(True)
        
        # Set current segment
        self.main_window.current_segment_timeline = timeline
        self.main_window.current_segment = segment
        
        # Update editor fields
        self.main_window.segment_start_edit.setText(
            self.main_window.utility_handlers._format_seconds_to_hms(segment.start_time)
        )
        self.main_window.segment_end_edit.setText(
            self.main_window.utility_handlers._format_seconds_to_hms(segment.end_time)
        )
        
        # Format color as hex
        r, g, b = segment.color
        color_hex = f"#{r:02x}{g:02x}{b:02x}"
        self.main_window.segment_color_edit.setText(color_hex)
    
    def hide_segment_editor(self):
        """Hide the segment editor."""
        self.main_window.segment_editor_widget.setVisible(False)
        self.main_window.current_segment_timeline = None
        self.main_window.current_segment = None
    
    def on_segment_start_changed(self):
        """Handle segment start time changed."""
        if not self.main_window.current_segment:
            return
        
        # Get text from edit field
        text = self.main_window.segment_start_edit.toPlainText()
        
        # Parse time
        time_value = self.main_window.utility_handlers._parse_time_from_text(text)
        
        if time_value is not None:
            # Update segment
            self.app.timeline_manager.modify_segment(
                self.main_window.current_segment_timeline,
                self.main_window.current_segment,
                start_time=time_value
            )
    
    def on_segment_end_changed(self):
        """Handle segment end time changed."""
        if not self.main_window.current_segment:
            return
        
        # Get text from edit field
        text = self.main_window.segment_end_edit.toPlainText()
        
        # Parse time
        time_value = self.main_window.utility_handlers._parse_time_from_text(text)
        
        if time_value is not None:
            # Update segment
            self.app.timeline_manager.modify_segment(
                self.main_window.current_segment_timeline,
                self.main_window.current_segment,
                end_time=time_value
            )
    
    def on_segment_color_changed(self):
        """Handle segment color changed."""
        if not self.main_window.current_segment:
            return
        
        # Get text from edit field
        text = self.main_window.segment_color_edit.toPlainText()
        
        # Parse color
        color = self.main_window.utility_handlers._parse_color_from_text(text)
        
        if color is not None:
            # Update segment
            self.app.timeline_manager.modify_segment(
                self.main_window.current_segment_timeline,
                self.main_window.current_segment,
                color=color
            )
    
    def on_segment_apply_all(self):
        """Apply segment properties to all segments in the timeline."""
        if not self.main_window.current_segment or not self.main_window.current_segment_timeline:
            return
        
        # Get current segment properties
        color = self.main_window.current_segment.color
        
        # Confirm with user
        reply = QMessageBox.question(
            self.main_window,
            "Apply to All",
            "Are you sure you want to apply this color to all segments in the timeline?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Apply to all segments
        timeline = self.main_window.current_segment_timeline
        
        # Save state for undo
        if self.app.undo_manager:
            self.app.undo_manager.save_state("apply_to_all_segments")
        
        # Apply color to all segments
        for segment in timeline.segments:
            self.app.timeline_manager.modify_segment(
                timeline,
                segment,
                color=color
            )
        
        # Update UI
        self.main_window.timeline_widget.update()
    
    def on_segment_start_apply(self):
        """Apply segment start time."""
        self.on_segment_start_changed()
    
    def on_segment_end_apply(self):
        """Apply segment end time."""
        self.on_segment_end_changed()
    
    def on_segment_color_apply(self):
        """Apply segment color."""
        self.on_segment_color_changed()