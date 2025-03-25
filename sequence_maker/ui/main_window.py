"""
Sequence Maker - Main Window

This module defines the MainWindow class, which is the main application window.
"""

import logging
import os
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt

from resources.resources import get_icon_path

from ui.timeline_widget import TimelineWidget
from ui.ball_widget import BallWidget
from ui.audio_widget import AudioWidget
from ui.lyrics_widget import LyricsWidget

from ui.dialogs.settings_dialog import SettingsDialog
from ui.dialogs.key_mapping_dialog import KeyMappingDialog
from ui.dialogs.about_dialog import AboutDialog
from ui.dialogs.llm_chat_window import LLMChatWindow
from ui.dialogs.version_history_dialog import VersionHistoryDialog
from ui.dialogs.llm_diagnostics_dialog import LLMDiagnosticsDialog

from ui.actions.file_actions import FileActions
from ui.actions.edit_actions import EditActions
from ui.actions.view_actions import ViewActions
from ui.actions.timeline_actions import TimelineActions
from ui.actions.playback_actions import PlaybackActions
from ui.actions.tools_actions import ToolsActions

from api.app_context_api import AppContextAPI
from api.timeline_action_api import TimelineActionAPI
from api.audio_action_api import AudioActionAPI

from app.constants import (
    DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT, APP_NAME, EDITOR_MODES
)

# Import refactored modules
from ui.main_window_parts.actions import create_actions
from ui.main_window_parts.menus import (
    create_menus, create_toolbars, create_statusbar
)
from ui.main_window_parts.widgets import create_widgets
from ui.main_window_parts.signals import connect_signals
from ui.main_window_parts.handlers import (
    on_new, on_open, on_save, on_save_as, on_load_audio, on_export_json, on_export_prg,
    on_version_history, on_undo, on_redo, on_cut, on_copy, on_paste,
    on_delete, on_select_all, on_preferences, on_zoom_in, on_zoom_out,
    on_zoom_fit, on_play, on_pause, on_stop, on_loop, on_key_mapping,
    on_connect_balls, on_llm_chat, on_llm_diagnostics, on_about
)
from ui.main_window_parts.editors import (
    show_segment_editor, hide_segment_editor, show_boundary_editor,
    hide_boundary_editor, switch_editor_mode
)
from ui.main_window_parts.utilities import (
    format_seconds_to_hms, parse_time_string, parse_color_string,
    format_color_tuple, load_settings, save_settings, update_recent_files_menu,
    open_recent_project, clear_recent_files, check_unsaved_changes, update_ui
)


class MainWindow(QMainWindow):
    """
    Main application window for Sequence Maker.
    
    Attributes:
        app: The main application instance.
        timeline_widget: Widget for displaying and editing timelines.
        ball_widget: Widget for displaying ball visualizations.
        audio_widget: Widget for displaying audio visualizations.
    """
    def __init__(self, app):
        """
        Initialize the main window.
        
        Args:
            app: The main application instance.
        """
        super().__init__()
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.MainWindow")
        
        # Initialize UI components
        self._init_ui()
        
        # Initialize action classes
        self.file_actions = FileActions(self)
        self.edit_actions = EditActions(self)
        self.view_actions = ViewActions(self)
        self.timeline_actions = TimelineActions(self)
        self.playback_actions = PlaybackActions(self)
        self.tools_actions = ToolsActions(self)
        
        # Create UI components using refactored modules
        create_actions(self)
        create_menus(self)
        create_toolbars(self)
        create_statusbar(self)
        create_widgets(self)
        load_settings(self)
        connect_signals(self)
        
        # Set window properties
        self.setMinimumSize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        
        # Initialize window title (will be updated in _update_ui)
        self.setWindowTitle(APP_NAME)
        
        # Initialize API
        self.app_context_api = AppContextAPI(self.app)
        self.timeline_action_api = TimelineActionAPI(self.app)
        self.audio_action_api = AudioActionAPI(self.app)
        
        # Update UI to set window title with project name if a project is loaded
        update_ui(self)
        
        # Show the window
        self.show()
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Set the window icon
        icon_path = get_icon_path("sm_app_icon_better.jpeg")
        if icon_path and os.path.exists(icon_path):
            from PyQt6.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))
    
    # Event handlers that delegate to the refactored modules
    def _on_new(self):
        on_new(self)
    
    def _on_open(self):
        on_open(self)
    
    def _on_save(self):
        return on_save(self)
    
    def _on_save_as(self):
        return on_save_as(self)
    
    def _on_load_audio(self):
        on_load_audio(self)
    
    def _on_export_json(self):
        on_export_json(self)
    
    def _on_export_prg(self):
        on_export_prg(self)
    
    def _on_version_history(self):
        on_version_history(self)
    
    def _check_unsaved_changes(self):
        return check_unsaved_changes(self)
    
    def _update_ui(self):
        update_ui(self)
    
    def _on_undo(self):
        on_undo(self)
    
    def _on_redo(self):
        on_redo(self)
    
    def _on_cut(self):
        on_cut(self)
    
    def _on_copy(self):
        on_copy(self)
    
    def _on_paste(self):
        on_paste(self)
    
    def _on_delete(self):
        on_delete(self)
    
    def _on_select_all(self):
        on_select_all(self)
    
    def _on_preferences(self):
        on_preferences(self)
    
    def _on_zoom_in(self):
        on_zoom_in(self)
    
    def _on_zoom_out(self):
        on_zoom_out(self)
    
    def _on_zoom_fit(self):
        on_zoom_fit(self)
    
    def _on_add_timeline(self):
        if hasattr(self.app, 'timeline_manager'):
            self.app.timeline_manager.add_timeline()
            self._update_ui()
    
    def _on_remove_timeline(self):
        if hasattr(self.app, 'timeline_manager'):
            current_timeline = self.app.timeline_manager.get_current_timeline()
            if current_timeline:
                self.app.timeline_manager.remove_timeline(current_timeline.id)
                self._update_ui()
    
    def _on_duplicate_timeline(self):
        if hasattr(self.app, 'timeline_manager'):
            current_timeline = self.app.timeline_manager.get_current_timeline()
            if current_timeline:
                self.app.timeline_manager.duplicate_timeline(current_timeline.id)
                self._update_ui()
    
    def _on_play(self):
        on_play(self)
    
    def _on_pause(self):
        on_pause(self)
    
    def _on_stop(self):
        on_stop(self)
    
    def _on_loop(self, checked):
        on_loop(self, checked)
    
    def _on_playback_started(self):
        """Handle playback started event."""
        # Update UI
        self.play_action.setVisible(False)
        self.pause_action.setVisible(True)
    
    def _on_playback_paused(self):
        """Handle playback paused event."""
        # Update UI
        self.pause_action.setVisible(False)
        self.play_action.setVisible(True)
    
    def _on_playback_stopped(self):
        """Handle playback stopped event."""
        # Update UI
        self.pause_action.setVisible(False)
        self.play_action.setVisible(True)
    
    def _on_key_mapping(self):
        on_key_mapping(self)
    
    def _on_connect_balls(self):
        on_connect_balls(self)
    
    def _on_llm_chat(self):
        on_llm_chat(self)
    
    def _create_llm_chat_window(self):
        self.llm_chat_window = LLMChatWindow(self.app, self)
    
    def _on_llm_diagnostics(self):
        on_llm_diagnostics(self)
    
    def _on_process_lyrics(self):
        if hasattr(self.app, 'lyrics_manager'):
            from ui.dialogs.lyrics_input_dialog import LyricsInputDialog
            dialog = LyricsInputDialog(self.app, self)
            if dialog.exec():
                lyrics_text = dialog.get_lyrics_text()
                self.app.lyrics_manager.process_lyrics(lyrics_text)
    
    def _on_about(self):
        on_about(self)
    
    def _on_help(self):
        # Show help dialog or open help documentation
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Help",
            "Help documentation is not yet implemented.\n\n"
            "Please refer to the README file for basic usage instructions."
        )
    
    def _on_toggle_ball_view(self, checked):
        self.ball_widget.setVisible(checked)
    
    def _on_toggle_audio_view(self, checked):
        self.audio_widget.setVisible(checked)
    
    def _on_toggle_lyrics_view(self, checked):
        if hasattr(self, 'lyrics_widget'):
            self.lyrics_widget.setVisible(checked)
    
    # Editor methods that delegate to the refactored modules
    def show_segment_editor(self, timeline, segment):
        show_segment_editor(self, timeline, segment)
    
    def hide_segment_editor(self):
        hide_segment_editor(self)
    
    def show_boundary_editor(self, timeline, time, left_segment, right_segment):
        show_boundary_editor(self, timeline, time, left_segment, right_segment)
    
    def hide_boundary_editor(self):
        hide_boundary_editor(self)
    
    def switch_editor_mode(self, mode):
        switch_editor_mode(self, mode)
    
    def _switch_to_segment_mode(self):
        self.switch_editor_mode(EDITOR_MODES.SEGMENT)
    
    def _switch_to_boundary_mode(self):
        self.switch_editor_mode(EDITOR_MODES.BOUNDARY)
    
    # Utility methods that delegate to the refactored modules
    def _format_color_tuple(self, color_tuple):
        return format_color_tuple(self, color_tuple)
    
    def _format_seconds_to_hms(self, seconds, include_hundredths=True, hide_hours_if_zero=False):
        return format_seconds_to_hms(self, seconds, include_hundredths, hide_hours_if_zero)
    
    def _parse_time_string(self, time_string):
        return parse_time_string(self, time_string)
    
    def _parse_color_string(self, color_string):
        return parse_color_string(self, color_string)
    
    def _update_recent_files_menu(self):
        update_recent_files_menu(self)
    
    def _open_recent_project(self, project_path):
        open_recent_project(self, project_path)
    
    def _clear_recent_files(self):
        clear_recent_files(self)
    
    def _update_cursor_position(self, position):
        self.cursor_position_label.setText(f"Position: {self._format_seconds_to_hms(position)}")
    
    def update_cursor_hover_position(self, position):
        self.cursor_hover_label.setText(f"Cursor: {self._format_seconds_to_hms(position)}")
        self.cursor_hover_label.setVisible(True)
    
    def clear_cursor_hover_position(self):
        self.cursor_hover_label.setVisible(False)
    
    # Timeline segment methods
    def _on_add_segment(self):
        self.timeline_widget.add_segment()
    
    def _on_edit_segment(self):
        self.timeline_widget.edit_selected_segment()
    
    def _on_delete_segment(self):
        self.timeline_widget.delete_selected_segment()
    
    def _on_split_segment(self):
        self.timeline_widget.split_selected_segment()
    
    def _on_merge_segments(self):
        self.timeline_widget.merge_selected_segments()
    
    def _on_clear_timeline(self):
        self.timeline_widget.clear_timeline()
    
    def _on_segment_apply(self):
        # Get the values from the editor
        start_time_str = self.segment_start_edit.text()
        end_time_str = self.segment_end_edit.text()
        color_str = self.segment_color_edit.text()
        
        # Parse the values
        start_time = self._parse_time_string(start_time_str)
        end_time = self._parse_time_string(end_time_str)
        color = self._parse_color_string(color_str)
        
        # Validate the values
        if start_time is None:
            self.statusBar().showMessage("Invalid start time format", 3000)
            return
        
        if end_time is None:
            self.statusBar().showMessage("Invalid end time format", 3000)
            return
        
        if color is None:
            self.statusBar().showMessage("Invalid color format", 3000)
            return
        
        if start_time >= end_time:
            self.statusBar().showMessage("Start time must be less than end time", 3000)
            return
        
        # Update the segment
        self.current_segment.start_time = start_time
        self.current_segment.end_time = end_time
        self.current_segment.color = color
        
        # Update the timeline by removing and re-adding the segment
        self.current_timeline.remove_segment(self.current_segment)
        self.current_timeline.add_segment(self.current_segment)
        
        # Hide the editor
        self.hide_segment_editor()
        
        # Update the UI
        self._update_ui()
    
    def _on_timeline_selection_changed(self, timeline, segment):
        # Update the status bar with segment info
        if segment:
            color = self._format_color_tuple(segment.color)
            self.statusBar().showMessage(f"Selected segment: {segment.start_time:.2f}s - {segment.end_time:.2f}s ({color})")
        else:
            self.statusBar().clearMessage()
    
    def _on_segment_cancel(self):
        self.hide_segment_editor()
    
    def _on_boundary_time_apply(self):
        # Get the value from the editor
        time_str = self.boundary_time_edit.text()
        
        # Parse the value
        time = self._parse_time_string(time_str)
        
        # Validate the value
        if time is None:
            self.statusBar().showMessage("Invalid time format", 3000)
            return
        
        # Check if the new time is valid
        if self.current_left_segment and time <= self.current_left_segment.start_time:
            self.statusBar().showMessage(
                f"Time must be greater than {self._format_seconds_to_hms(self.current_left_segment.start_time)}",
                3000
            )
            return
        
        if self.current_right_segment and time >= self.current_right_segment.end_time:
            self.statusBar().showMessage(
                f"Time must be less than {self._format_seconds_to_hms(self.current_right_segment.end_time)}",
                3000
            )
            return
        
        # Update the segments
        if self.current_left_segment:
            self.current_left_segment.end_time = time
            # Update the timeline by removing and re-adding the segment
            self.current_timeline.remove_segment(self.current_left_segment)
            self.current_timeline.add_segment(self.current_left_segment)
        
        if self.current_right_segment:
            self.current_right_segment.start_time = time
            # Update the timeline by removing and re-adding the segment
            self.current_timeline.remove_segment(self.current_right_segment)
            self.current_timeline.add_segment(self.current_right_segment)
        
        # Hide the editor
        self.hide_boundary_editor()
        
        # Update the UI
        self._update_ui()
    
    def _on_editor_apply(self):
        # Determine which editor is active and call the appropriate apply method
        if self.editor_stack.currentWidget() == self.segment_editor_widget:
            self._on_segment_apply()
        else:
            self._on_boundary_time_apply()
    
    def _on_editor_cancel(self):
        # Determine which editor is active and call the appropriate cancel method
        if self.editor_stack.currentWidget() == self.segment_editor_widget:
            self._on_segment_cancel()
        else:
            self.hide_boundary_editor()
    
    def _on_llm_action(self, action_type, parameters):
        """Handle LLM action requests."""
        self.logger.info(f"LLM action requested: {action_type}")
        
        # Handle different action types
        if action_type == "add_segment":
            # Extract parameters
            start_time = parameters.get("start_time")
            end_time = parameters.get("end_time")
            color = parameters.get("color")
            
            # Validate parameters
            if start_time is None or end_time is None or color is None:
                self.logger.warning("Missing parameters for add_segment action")
                return
            
            # Add segment
            self.timeline_action_api.add_segment(start_time, end_time, color)
            
        elif action_type == "edit_segment":
            # Extract parameters
            segment_id = parameters.get("segment_id")
            start_time = parameters.get("start_time")
            end_time = parameters.get("end_time")
            color = parameters.get("color")
            
            # Validate parameters
            if segment_id is None:
                self.logger.warning("Missing segment_id for edit_segment action")
                return
            
            # Edit segment
            self.timeline_action_api.edit_segment(segment_id, start_time, end_time, color)
            
        elif action_type == "delete_segment":
            # Extract parameters
            segment_id = parameters.get("segment_id")
            
            # Validate parameters
            if segment_id is None:
                self.logger.warning("Missing segment_id for delete_segment action")
                return
            
            # Delete segment
            self.timeline_action_api.delete_segment(segment_id)
            
        elif action_type == "play_audio":
            # Play audio
            self.audio_action_api.play()
            
        elif action_type == "pause_audio":
            # Pause audio
            self.audio_action_api.pause()
            
        elif action_type == "stop_audio":
            # Stop audio
            self.audio_action_api.stop()
            
        else:
            self.logger.warning(f"Unknown LLM action type: {action_type}")
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        # Get the key
        key = event.key()
        modifiers = event.modifiers()
        
        # Convert key to string representation
        key_text = chr(key).lower() if key >= 32 and key <= 126 else ""
        
        # Check if the key is in the DEFAULT_KEY_MAPPING from constants
        from app.constants import DEFAULT_KEY_MAPPING, EFFECT_MODIFIERS
        
        if key_text in DEFAULT_KEY_MAPPING:
            # Get the mapping
            mapping = DEFAULT_KEY_MAPPING[key_text]
            color = mapping["color"]
            timelines = mapping["timelines"]
            
            # Check for effect modifiers
            effect_type = None
            if modifiers & Qt.KeyboardModifier.ShiftModifier and "shift" in EFFECT_MODIFIERS:
                effect_type = EFFECT_MODIFIERS["shift"]
            elif modifiers & Qt.KeyboardModifier.ControlModifier and "ctrl" in EFFECT_MODIFIERS:
                effect_type = EFFECT_MODIFIERS["ctrl"]
            elif modifiers & Qt.KeyboardModifier.AltModifier and "alt" in EFFECT_MODIFIERS:
                effect_type = EFFECT_MODIFIERS["alt"]
            
            # Add color to each timeline
            for timeline_index in timelines:
                if hasattr(self.app, 'timeline_manager'):
                    segment = self.app.timeline_manager.add_color_at_position(timeline_index, color)
                    
                    # Add effect if specified
                    if effect_type and segment:
                        self.app.timeline_manager.add_effect_to_segment(
                            self.app.timeline_manager.get_timeline(timeline_index),
                            segment,
                            effect_type
                        )
            
            # Update UI
            self._update_ui()
            
            # Consume the event
            event.accept()
            return
        
        # Check for other key mappings (play, pause, etc.)
        key_string = ""
        
        # Add modifiers
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            key_string += "Ctrl+"
        if modifiers & Qt.KeyboardModifier.AltModifier:
            key_string += "Alt+"
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            key_string += "Shift+"
        
        # Add key
        key_string += str(key)
        
        # Check for specific actions
        if key == Qt.Key.Key_Space:
            # Toggle play/pause
            if hasattr(self.app, 'audio_manager') and self.app.audio_manager.is_playing():
                self._on_pause()
            else:
                self._on_play()
            event.accept()
            return
        
        # If we get here, the key wasn't handled, so pass it to the parent
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle window close events."""
        # Check for unsaved changes
        if not self._check_unsaved_changes():
            event.ignore()
            return
        
        # Save settings
        save_settings(self)
        
        # Accept the event
        event.accept()