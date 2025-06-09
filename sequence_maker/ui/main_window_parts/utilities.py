"""
Sequence Maker - Main Window Utilities

This module contains utility functions for the main window.
"""

import json
import logging
import re
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QSettings
from app.constants import APP_NAME


def format_seconds_to_hms(main_window, seconds, include_hundredths=True, hide_hours_if_zero=False):
    """
    Format seconds to HH:MM:SS.hh format.
    
    Args:
        seconds: The time in seconds.
        include_hundredths: Whether to include hundredths of a second.
        hide_hours_if_zero: Whether to hide hours if they are zero.
        
    Returns:
        A string in the format HH:MM:SS.hh or MM:SS.hh if hide_hours_if_zero is True and hours are 0.
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if include_hundredths:
        whole_seconds = int(seconds)
        hundredths = int((seconds - whole_seconds) * 100)
        
        if hide_hours_if_zero and hours == 0:
            return f"{int(minutes):02d}:{whole_seconds:02d}.{hundredths:02d}"
        else:
            return f"{int(hours):02d}:{int(minutes):02d}:{whole_seconds:02d}.{hundredths:02d}"
    else:
        if hide_hours_if_zero and hours == 0:
            return f"{int(minutes):02d}:{int(seconds):02d}"
        else:
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


def parse_time_string(main_window, time_string):
    """
    Parse a time string in the format HH:MM:SS.hh or MM:SS.hh.
    
    Args:
        time_string: The time string to parse.
        
    Returns:
        The time in seconds, or None if the string could not be parsed.
    """
    # Try to match HH:MM:SS.hh format
    match = re.match(r'^(\d+):(\d+):(\d+)(?:\.(\d+))?$', time_string)
    if match:
        hours, minutes, seconds, hundredths = match.groups()
        total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        if hundredths:
            total_seconds += int(hundredths) / (10 ** len(hundredths))
        return total_seconds
    
    # Try to match MM:SS.hh format
    match = re.match(r'^(\d+):(\d+)(?:\.(\d+))?$', time_string)
    if match:
        minutes, seconds, hundredths = match.groups()
        total_seconds = int(minutes) * 60 + int(seconds)
        if hundredths:
            total_seconds += int(hundredths) / (10 ** len(hundredths))
        return total_seconds
    
    # Try to match SS.hh format
    match = re.match(r'^(\d+)(?:\.(\d+))?$', time_string)
    if match:
        seconds, hundredths = match.groups()
        total_seconds = int(seconds)
        if hundredths:
            total_seconds += int(hundredths) / (10 ** len(hundredths))
        return total_seconds
    
    return None


def parse_color_string(main_window, color_string):
    """
    Parse a color string in the format (R, G, B) or R, G, B.
    
    Args:
        color_string: The color string to parse.
        
    Returns:
        A tuple of (R, G, B) values, or None if the string could not be parsed.
    """
    # Remove parentheses and split by commas
    color_string = color_string.strip()
    if color_string.startswith('(') and color_string.endswith(')'):
        color_string = color_string[1:-1]
    
    # Split by commas
    parts = color_string.split(',')
    if len(parts) != 3:
        return None
    
    # Parse each part as an integer
    try:
        r = int(parts[0].strip())
        g = int(parts[1].strip())
        b = int(parts[2].strip())
        
        # Validate range
        if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
            return (r, g, b)
    except ValueError:
        pass
    
    return None


def format_color_tuple(main_window, color_tuple):
    """
    Format a color tuple as a string.
    
    Args:
        color_tuple: A tuple of (R, G, B) values.
        
    Returns:
        A string in the format (R, G, B).
    """
    if color_tuple is None:
        return ""
    
    r, g, b = color_tuple
    return f"{r}, {g}, {b}"


def load_settings(main_window):
    """Load application settings."""
    settings = QSettings("SequenceMaker", "SequenceMaker")
    
    # Load window geometry
    geometry = settings.value("geometry")
    if geometry:
        main_window.restoreGeometry(geometry)
    
    # Load window state
    state = settings.value("windowState")
    if state:
        main_window.restoreState(state)
    
    # Recent files are handled by app.config, which loads itself.
    # We just need to ensure the menu reflects app.config's state at startup.
    main_window._update_recent_files_menu()


def save_settings(main_window):
    """Save application settings."""
    settings = QSettings("SequenceMaker", "SequenceMaker")
    
    # Save window geometry
    settings.setValue("geometry", main_window.saveGeometry())
    
    # Save window state
    settings.setValue("windowState", main_window.saveState())
    
    # Recent files are handled by app.config.save()
    pass


def update_recent_files_menu(main_window):
    """Update the recent files menu."""
    main_window.recent_files_menu.clear()

    # Get the list directly from app.config
    recent_files_list = main_window.app.config.get("general", "recent_projects", [])

    for file_path in recent_files_list:
        action = main_window.recent_files_menu.addAction(file_path)
        action.triggered.connect(lambda checked, path=file_path: main_window._open_recent_project(path))

    if recent_files_list:
        main_window.recent_files_menu.addSeparator()
        clear_action = main_window.recent_files_menu.addAction("Clear Recent Files")
        clear_action.triggered.connect(main_window._clear_recent_files)
    else:
        # Add a disabled placeholder if the list is empty
        empty_action = main_window.recent_files_menu.addAction("(No Recent Files)")
        empty_action.setEnabled(False)


def open_recent_project(main_window, project_path):
    """Open a recent project."""
    if not main_window._check_unsaved_changes():
        return
    
    try:
        main_window.app.project_manager.load_project(project_path)
        main_window._update_ui()
    except Exception as e:
        logging.error(f"Error loading recent project: {e}")
        QMessageBox.critical(main_window, "Error", f"Failed to load project: {str(e)}")
        
        # If loading fails, remove the project_path from app.config's recent_projects list
        recent_list_from_config = main_window.app.config.get("general", "recent_projects", [])
        if project_path in recent_list_from_config:
            recent_list_from_config.remove(project_path)
            main_window.app.config.set("general", "recent_projects", recent_list_from_config)
            main_window.app.config.save() # Persist the removal
            main_window._update_recent_files_menu() # Update the UI


def clear_recent_files(main_window):
    """Clear the recent files list."""
    main_window.app.config.set("general", "recent_projects", [])
    main_window.app.config.save() # Persist the change
    main_window._update_recent_files_menu()


def check_unsaved_changes(main_window):
    """
    Check if there are unsaved changes and prompt the user to save them.
    
    Returns:
        True if the operation should continue, False if it should be cancelled.
    """
    if main_window.app.project_manager.has_unsaved_changes:
        reply = QMessageBox.question(
            main_window, "Unsaved Changes",
            "There are unsaved changes. Would you like to save them?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )
        
        if reply == QMessageBox.StandardButton.Save:
            return main_window._on_save()
        elif reply == QMessageBox.StandardButton.Cancel:
            return False
    
    return True


def update_ui(main_window):
    """Update the UI based on the current state."""
    # Update window title
    if main_window.app.project_manager.current_project and hasattr(main_window.app.project_manager.current_project, 'file_path') and main_window.app.project_manager.current_project.file_path:
        project_name = main_window.app.project_manager.current_project.file_path.split('/')[-1]
        if main_window.app.project_manager.has_unsaved_changes:
            main_window.setWindowTitle(f"{project_name}* - {APP_NAME}")
        else:
            main_window.setWindowTitle(f"{project_name} - {APP_NAME}")
    else:
        if main_window.app.project_manager.has_unsaved_changes:
            main_window.setWindowTitle(f"Untitled* - {APP_NAME}")
        else:
            main_window.setWindowTitle(f"Untitled - {APP_NAME}")
    
    # Update status bar
    if main_window.app.project_manager.current_project and hasattr(main_window.app.project_manager.current_project, 'file_path') and main_window.app.project_manager.current_project.file_path:
        main_window.project_status_label.setText(f"Project: {main_window.app.project_manager.current_project.file_path}")
    else:
        main_window.project_status_label.setText("Project: Untitled")
    
    # Update undo/redo actions
    main_window.undo_action.setEnabled(main_window.app.undo_manager.can_undo())
    main_window.redo_action.setEnabled(main_window.app.undo_manager.can_redo())
    
    # Update playback actions
    if hasattr(main_window.app, 'audio_manager'):
        is_playing = main_window.app.audio_manager.playing if hasattr(main_window.app.audio_manager, 'playing') else False
        is_paused = main_window.app.audio_manager.paused if hasattr(main_window.app.audio_manager, 'paused') else False
        
        main_window.play_action.setEnabled(not is_playing or is_paused)
        main_window.pause_action.setEnabled(is_playing and not is_paused)
        main_window.stop_action.setEnabled(is_playing or is_paused)
    else:
        main_window.play_action.setEnabled(False)
        main_window.pause_action.setEnabled(False)
        main_window.stop_action.setEnabled(False)
    
    # Update timeline actions
    has_timeline = main_window.app.timeline_manager.selected_timeline is not None
    main_window.clear_timeline_action.setEnabled(has_timeline)
    
    # Update segment actions
    has_segment = hasattr(main_window.timeline_widget, 'selected_segment') and main_window.timeline_widget.selected_segment is not None
    main_window.edit_segment_action.setEnabled(has_segment)
    main_window.delete_segment_action.setEnabled(has_segment)
    main_window.split_segment_action.setEnabled(has_segment)
    
    # Update merge segments action
    # Since there's no get_selected_segments_count method, we'll disable this for now
    # In a real implementation, you would need to track multiple segment selection
    main_window.merge_segments_action.setEnabled(False)
    
    # Update recent files menu
    main_window._update_recent_files_menu()