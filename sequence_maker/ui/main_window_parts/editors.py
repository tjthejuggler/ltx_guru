"""
Sequence Maker - Main Window Editors

This module contains functions for managing editors in the main window.
"""

from app.constants import EDITOR_MODES


def show_segment_editor(main_window, timeline, segment):
    """Show the segment editor for the given timeline and segment."""
    # Switch to segment mode
    main_window.switch_editor_mode(EDITOR_MODES["segment"])
    
    # Store the current timeline and segment
    main_window.current_timeline = timeline
    main_window.current_segment = segment
    
    # Set the segment start and end times
    main_window.segment_start_edit.setText(main_window._format_seconds_to_hms(segment.start_time))
    main_window.segment_end_edit.setText(main_window._format_seconds_to_hms(segment.end_time))
    
    # Set the segment color
    main_window.segment_color_edit.setText(main_window._format_color_tuple(segment.color))
    
    # Show the editor
    main_window.editor_dock.show()
    
    # Focus the start time field
    main_window.segment_start_edit.setFocus()
    main_window.segment_start_edit.selectAll()


def hide_segment_editor(main_window):
    """Hide the segment editor."""
    # Clear the current timeline and segment
    main_window.current_timeline = None
    main_window.current_segment = None
    
    # Hide the editor
    main_window.editor_dock.hide()
    
    # Clear the segment start and end times
    main_window.segment_start_edit.clear()
    main_window.segment_end_edit.clear()
    
    # Clear the segment color
    main_window.segment_color_edit.clear()


def show_boundary_editor(main_window, timeline, time, left_segment, right_segment):
    """Show the boundary editor for the given timeline and time."""
    # Switch to boundary mode
    main_window.switch_editor_mode(EDITOR_MODES["boundary"])
    
    # Store the current timeline, time, and segments
    main_window.current_timeline = timeline
    main_window.current_boundary_time = time
    main_window.current_left_segment = left_segment
    main_window.current_right_segment = right_segment
    
    # Set the boundary time
    main_window.boundary_time_edit.setText(main_window._format_seconds_to_hms(time))
    
    # Show the editor
    main_window.editor_dock.show()
    
    # Focus the time field
    main_window.boundary_time_edit.setFocus()
    main_window.boundary_time_edit.selectAll()
    
    # Update status bar with boundary info
    if left_segment and right_segment:
        left_color = main_window._format_color_tuple(left_segment.color)
        right_color = main_window._format_color_tuple(right_segment.color)
        main_window.statusBar().showMessage(
            f"Editing boundary between segments: "
            f"{left_segment.start_time:.2f}s-{left_segment.end_time:.2f}s ({left_color}) and "
            f"{right_segment.start_time:.2f}s-{right_segment.end_time:.2f}s ({right_color})"
        )
    elif left_segment:
        left_color = main_window._format_color_tuple(left_segment.color)
        main_window.statusBar().showMessage(
            f"Editing end of segment: {left_segment.start_time:.2f}s-{left_segment.end_time:.2f}s ({left_color})"
        )
    elif right_segment:
        right_color = main_window._format_color_tuple(right_segment.color)
        main_window.statusBar().showMessage(
            f"Editing start of segment: {right_segment.start_time:.2f}s-{right_segment.end_time:.2f}s ({right_color})"
        )


def hide_boundary_editor(main_window):
    """Hide the boundary editor."""
    # Clear the current timeline, time, and segments
    main_window.current_timeline = None
    main_window.current_boundary_time = None
    main_window.current_left_segment = None
    main_window.current_right_segment = None
    
    # Hide the editor
    main_window.editor_dock.hide()
    
    # Clear the boundary time
    main_window.boundary_time_edit.clear()
    
    # Clear status bar
    main_window.statusBar().clearMessage()


def switch_editor_mode(main_window, mode):
    """Switch the editor mode."""
    if mode == EDITOR_MODES["segment"]:
        switch_to_segment_mode(main_window)
    elif mode == EDITOR_MODES["boundary"]:
        switch_to_boundary_mode(main_window)


def switch_to_segment_mode(main_window):
    """Switch to segment editing mode."""
    main_window.editor_stack.setCurrentWidget(main_window.segment_editor_widget)


def switch_to_boundary_mode(main_window):
    """Switch to boundary editing mode."""
    main_window.editor_stack.setCurrentWidget(main_window.boundary_editor_widget)