"""
Sequence Maker - Main Window (Refactored)

This module defines the MainWindow class, which is the main application window.
"""

import logging
import os
import json
import tempfile
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QMenu, QToolBar, QStatusBar, QFileDialog, QMessageBox,
    QLabel, QTextEdit, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings, QSize, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QFont, QPixmap, QImage, QKeyEvent

from resources.resources import get_icon_path

from ui.timeline_widget import TimelineWidget
from ui.ball_widget import BallWidget
from ui.audio_widget import AudioWidget
from ui.lyrics_widget import LyricsWidget
from ui.widgets.apply_text_edit import ApplyTextEdit

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

from ui.handlers.file_handlers import FileHandlers
from ui.handlers.edit_handlers import EditHandlers
from ui.handlers.view_handlers import ViewHandlers
from ui.handlers.timeline_handlers import TimelineHandlers
from ui.handlers.playback_handlers import PlaybackHandlers
from ui.handlers.tools_handlers import ToolsHandlers
from ui.handlers.segment_handlers import SegmentHandlers
from ui.handlers.boundary_handlers import BoundaryHandlers
from ui.handlers.utility_handlers import UtilityHandlers

from api.app_context_api import AppContextAPI
from api.timeline_action_api import TimelineActionAPI
from api.audio_action_api import AudioActionAPI

from app.constants import PROJECT_FILE_EXTENSION, AUDIO_FILE_EXTENSIONS, BALL_VISUALIZATION_SIZE


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
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_statusbar()
        self._create_dock_widgets()  # Create dock widgets first
        self._create_central_widget()  # Then create central widget
        self._load_settings()
        self._connect_signals()
        
        # Set window properties
        self.setMinimumSize(800, 600)
        
        # Initialize window title (will be updated in _update_ui)
        self.setWindowTitle("Sequence Maker")
        
        # Initialize API
        self.app_context_api = AppContextAPI(self.app)
        self.timeline_action_api = TimelineActionAPI(self.app)
        self.audio_action_api = AudioActionAPI(self.app)
        
        # Update UI to set window title with project name if a project is loaded
        self._update_ui()
        
        # Show the window
        self.show()
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Set the window icon
        icon_path = get_icon_path("sm_app_icon_better.jpeg")
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
    
    def _create_actions(self):
        """Create actions for menus and toolbars."""
        # Initialize action classes
        self.file_actions = FileActions(self)
        self.edit_actions = EditActions(self)
        self.view_actions = ViewActions(self)
        self.timeline_actions = TimelineActions(self)
        self.playback_actions = PlaybackActions(self)
        self.tools_actions = ToolsActions(self)
        
        # Get actions from action classes
        self.new_action = self.file_actions.new_action
        self.open_action = self.file_actions.open_action
        self.save_action = self.file_actions.save_action
        self.save_as_action = self.file_actions.save_as_action
        self.export_json_action = self.file_actions.export_json_action
        self.export_prg_action = self.file_actions.export_prg_action
        self.exit_action = self.file_actions.exit_action
        
        self.undo_action = self.edit_actions.undo_action
        self.redo_action = self.edit_actions.redo_action
        self.cut_action = self.edit_actions.cut_action
        self.copy_action = self.edit_actions.copy_action
        self.paste_action = self.edit_actions.paste_action
        self.delete_action = self.edit_actions.delete_action
        self.select_all_action = self.edit_actions.select_all_action
        self.preferences_action = self.edit_actions.preferences_action
        self.zoom_in_action = self.view_actions.zoom_in_action
        self.zoom_out_action = self.view_actions.zoom_out_action
        self.zoom_fit_action = self.view_actions.zoom_fit_action
        
        # Create toggle view actions directly
        self.toggle_ball_view_action = QAction("Toggle &Ball View", self)
        self.toggle_ball_view_action.setStatusTip("Toggle ball visualization")
        self.toggle_ball_view_action.setCheckable(True)
        self.toggle_ball_view_action.setChecked(True)
        self.toggle_ball_view_action.triggered.connect(self._on_toggle_ball_view)
        
        self.toggle_audio_view_action = QAction("Toggle &Audio View", self)
        self.toggle_audio_view_action.setStatusTip("Toggle audio visualization")
        self.toggle_audio_view_action.setCheckable(True)
        self.toggle_audio_view_action.setChecked(True)
        self.toggle_audio_view_action.triggered.connect(self._on_toggle_audio_view)
        
        self.toggle_lyrics_view_action = QAction("Toggle &Lyrics View", self)
        self.toggle_lyrics_view_action.setStatusTip("Toggle lyrics visualization")
        self.toggle_lyrics_view_action.setCheckable(True)
        self.toggle_lyrics_view_action.setChecked(True)
        self.toggle_lyrics_view_action.triggered.connect(self._on_toggle_lyrics_view)
        
        # Create segment-related actions directly
        self.add_segment_action = QAction("&Add Segment", self)
        self.add_segment_action.setStatusTip("Add a new segment")
        self.add_segment_action.triggered.connect(self._on_add_segment)
        
        self.edit_segment_action = QAction("&Edit Segment", self)
        self.edit_segment_action.setStatusTip("Edit the selected segment")
        self.edit_segment_action.triggered.connect(self._on_edit_segment)
        
        self.delete_segment_action = QAction("&Delete Segment", self)
        self.delete_segment_action.setStatusTip("Delete the selected segment")
        self.delete_segment_action.triggered.connect(self._on_delete_segment)
        
        self.split_segment_action = QAction("&Split Segment", self)
        self.split_segment_action.setStatusTip("Split the selected segment")
        self.split_segment_action.triggered.connect(self._on_split_segment)
        
        self.merge_segments_action = QAction("&Merge Segments", self)
        self.merge_segments_action.setStatusTip("Merge selected segments")
        self.merge_segments_action.triggered.connect(self._on_merge_segments)
        
        self.clear_timeline_action = QAction("&Clear Timeline", self)
        self.clear_timeline_action.setStatusTip("Clear the timeline")
        self.clear_timeline_action.triggered.connect(self._on_clear_timeline)
        
        self.play_action = self.playback_actions.play_action
        self.pause_action = self.playback_actions.pause_action
        self.stop_action = self.playback_actions.stop_action
        
        # Create loop action directly
        self.loop_action = QAction("&Loop", self)
        self.loop_action.setStatusTip("Toggle audio looping")
        self.loop_action.setCheckable(True)
        self.loop_action.triggered.connect(self._on_loop)
        
        self.key_mapping_action = self.tools_actions.key_mapping_action
        self.connect_balls_action = self.tools_actions.connect_balls_action
        self.llm_chat_action = self.tools_actions.llm_chat_action
        self.llm_diagnostics_action = self.tools_actions.llm_diagnostics_action
        
        # Create version history action directly
        self.version_history_action = QAction("&Version History...", self)
        self.version_history_action.setStatusTip("View and restore previous versions")
        self.version_history_action.triggered.connect(self._on_version_history)
        
        self.about_action = self.tools_actions.about_action
    
    def _create_menus(self):
        """Create menus for the main window."""
        # File menu
        self.file_menu = self.menuBar().addMenu("&File")
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addSeparator()
        
        # Export submenu
        self.export_menu = self.file_menu.addMenu("Export")
        self.export_menu.addAction(self.export_json_action)
        self.export_menu.addAction(self.export_prg_action)
        
        # Recent files submenu
        self.recent_files_menu = self.file_menu.addMenu("Recent Files")
        self._update_recent_files_menu()
        
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        
        # Edit menu
        self.edit_menu = self.menuBar().addMenu("&Edit")
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.cut_action)
        self.edit_menu.addAction(self.copy_action)
        self.edit_menu.addAction(self.paste_action)
        self.edit_menu.addAction(self.delete_action)
        self.edit_menu.addAction(self.select_all_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.preferences_action)
        
        # View menu
        self.view_menu = self.menuBar().addMenu("&View")
        self.view_menu.addAction(self.zoom_in_action)
        self.view_menu.addAction(self.zoom_out_action)
        self.view_menu.addAction(self.zoom_fit_action)
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.toggle_ball_view_action)
        self.view_menu.addAction(self.toggle_audio_view_action)
        self.view_menu.addAction(self.toggle_lyrics_view_action)
        
        # Timeline menu
        self.timeline_menu = self.menuBar().addMenu("&Timeline")
        self.timeline_menu.addAction(self.add_segment_action)
        self.timeline_menu.addAction(self.edit_segment_action)
        self.timeline_menu.addAction(self.delete_segment_action)
        self.timeline_menu.addSeparator()
        self.timeline_menu.addAction(self.split_segment_action)
        self.timeline_menu.addAction(self.merge_segments_action)
        self.timeline_menu.addSeparator()
        self.timeline_menu.addAction(self.clear_timeline_action)
        
        # Playback menu
        self.playback_menu = self.menuBar().addMenu("&Playback")
        self.playback_menu.addAction(self.play_action)
        self.playback_menu.addAction(self.pause_action)
        self.playback_menu.addAction(self.stop_action)
        self.playback_menu.addSeparator()
        self.playback_menu.addAction(self.loop_action)
        
        # Tools menu
        self.tools_menu = self.menuBar().addMenu("&Tools")
        self.tools_menu.addAction(self.key_mapping_action)
        self.tools_menu.addAction(self.llm_chat_action)
        self.tools_menu.addAction(self.llm_diagnostics_action)
        self.tools_menu.addAction(self.version_history_action)
        
        # Help menu
        self.help_menu = self.menuBar().addMenu("&Help")
        self.help_menu.addAction(self.about_action)
    
    def _create_toolbars(self):
        """Create toolbars for the main window."""
        # File toolbar
        self.file_toolbar = self.addToolBar("File")
        self.file_toolbar.setObjectName("FileToolbar")
        self.file_toolbar.addAction(self.new_action)
        self.file_toolbar.addAction(self.open_action)
        self.file_toolbar.addAction(self.save_action)
        
        # Edit toolbar
        self.edit_toolbar = self.addToolBar("Edit")
        self.edit_toolbar.setObjectName("EditToolbar")
        self.edit_toolbar.addAction(self.undo_action)
        self.edit_toolbar.addAction(self.redo_action)
        
        # Timeline toolbar
        self.timeline_toolbar = self.addToolBar("Timeline")
        self.timeline_toolbar.setObjectName("TimelineToolbar")
        self.timeline_toolbar.addAction(self.add_segment_action)
        self.timeline_toolbar.addAction(self.edit_segment_action)
        self.timeline_toolbar.addAction(self.delete_segment_action)
        
        # Playback toolbar
        self.playback_toolbar = self.addToolBar("Playback")
        self.playback_toolbar.setObjectName("PlaybackToolbar")
        self.playback_toolbar.addAction(self.play_action)
        self.playback_toolbar.addAction(self.pause_action)
        self.playback_toolbar.addAction(self.stop_action)
        self.playback_toolbar.addAction(self.loop_action)
    
    def _create_statusbar(self):
        """Create the status bar for the main window."""
        self.statusbar = self.statusBar()
        
        # Add project status label (empty by default)
        self.project_status_label = QLabel("")
        self.statusbar.addWidget(self.project_status_label)
        
        # Add hover info label for segment information
        self.hover_info_label = QLabel("")
        self.hover_info_label.setVisible(False)
        self.statusbar.addWidget(self.hover_info_label)
        
        # Add cursor hover position label (shows time when hovering over timelines)
        self.cursor_hover_label = QLabel("Cursor: --:--.--)")
        self.statusbar.addPermanentWidget(self.cursor_hover_label)
        
        # Add cursor position label with formatted time (on the right side)
        self.cursor_position_label = QLabel("Position: 00:00.00")
        self.statusbar.addPermanentWidget(self.cursor_position_label)
    
    def _create_central_widget(self):
        """Create the central widget for the main window."""
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)  # No spacing
        
        # Add editor at the top (always visible)
        self.main_layout.addWidget(self.editor_dock, 0)  # 0 stretch factor to minimize space
        
        # Create splitter for timeline and ball visualization
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_layout.addWidget(self.main_splitter)
        
        # Create timeline widget
        self.timeline_widget = TimelineWidget(self.app, self)
        self.main_splitter.addWidget(self.timeline_widget)
        
        # Create ball widget
        self.ball_widget = BallWidget(self.app, self)
        self.main_splitter.addWidget(self.ball_widget)
        
        # Create audio widget
        self.audio_widget = AudioWidget(self.app, self)
        self.main_splitter.addWidget(self.audio_widget)
        
        # Create lyrics widget if lyrics manager is available
        if hasattr(self.app, 'lyrics_manager'):
            self.lyrics_widget = LyricsWidget(self.app, self)
            self.main_splitter.addWidget(self.lyrics_widget)
        
        # Set initial splitter sizes
        self.main_splitter.setSizes([300, 200, 200, 200])
    
    def _create_dock_widgets(self):
        """Create dock widgets for the main window."""
        # Create editor dock widget - always visible, ultra-compact layout
        # This will be used for both segment editing and boundary editing
        self.editor_dock = QWidget()
        self.editor_dock.setFixedHeight(30)  # Set fixed height to minimize vertical space
        self.editor_layout = QHBoxLayout(self.editor_dock)
        self.editor_layout.setContentsMargins(5, 0, 5, 0)  # Minimal margins
        self.editor_layout.setSpacing(5)  # Minimal spacing
        
        from PyQt6.QtWidgets import QLineEdit, QStackedWidget  # Import QLineEdit and QStackedWidget
        
        # Create a stacked widget to switch between segment and boundary editing modes
        self.editor_stack = QStackedWidget()
        self.editor_layout.addWidget(self.editor_stack)
        
        # Create segment editor widget
        self.segment_editor_widget = QWidget()
        self.segment_editor_widget_layout = QHBoxLayout(self.segment_editor_widget)
        self.segment_editor_widget_layout.setContentsMargins(0, 0, 0, 0)  # No margins
        self.segment_editor_widget_layout.setSpacing(5)  # Minimal spacing
        
        # Create segment start time field
        self.segment_start_label = QLabel("Start:")
        self.segment_editor_widget_layout.addWidget(self.segment_start_label)
        
        self.segment_start_edit = QLineEdit()
        self.segment_start_edit.setMinimumWidth(80)
        self.segment_editor_widget_layout.addWidget(self.segment_start_edit)
        
        # Create segment end time field
        self.segment_end_label = QLabel("End:")
        self.segment_editor_widget_layout.addWidget(self.segment_end_label)
        
        self.segment_end_edit = QLineEdit()
        self.segment_end_edit.setMinimumWidth(80)
        self.segment_editor_widget_layout.addWidget(self.segment_end_edit)
        
        # Create segment color field
        self.segment_color_label = QLabel("RGB:")  # Changed from "Color:" to "RGB:"
        self.segment_editor_widget_layout.addWidget(self.segment_color_label)
        
        self.segment_color_edit = QLineEdit()
        self.segment_color_edit.setMinimumWidth(120)  # Wider for color values
        self.segment_editor_widget_layout.addWidget(self.segment_color_edit)
        
        # Add segment editor to stack
        self.editor_stack.addWidget(self.segment_editor_widget)
        
        # Create boundary editor widget
        self.boundary_editor_widget = QWidget()
        self.boundary_editor_widget_layout = QHBoxLayout(self.boundary_editor_widget)
        self.boundary_editor_widget_layout.setContentsMargins(0, 0, 0, 0)  # No margins
        self.boundary_editor_widget_layout.setSpacing(5)  # Minimal spacing
        
        # Create boundary time field
        self.boundary_time_label = QLabel("Time:")
        self.boundary_editor_widget_layout.addWidget(self.boundary_time_label)
        
        self.boundary_time_edit = QLineEdit()
        self.boundary_time_edit.setMinimumWidth(120)
        self.boundary_editor_widget_layout.addWidget(self.boundary_time_edit)
        
        # Add boundary editor to stack
        self.editor_stack.addWidget(self.boundary_editor_widget)
        
        # Add spacer to push buttons to the right
        self.editor_layout.addStretch(1)
        
        # Create apply button
        self.editor_apply_button = QPushButton("Apply")
        self.editor_apply_button.setFixedHeight(24)  # Smaller button height
        self.editor_layout.addWidget(self.editor_apply_button)
        
        # Create cancel button
        self.editor_cancel_button = QPushButton("Cancel")
        self.editor_cancel_button.setFixedHeight(24)  # Smaller button height
        self.editor_layout.addWidget(self.editor_cancel_button)
        
        # Connect buttons to appropriate handlers based on current mode
        self.editor_mode = "segment"  # Default mode
        self.editor_apply_button.clicked.connect(self._on_editor_apply)
        self.editor_cancel_button.clicked.connect(self._on_editor_cancel)
        
        # Hide the name field as it's not needed according to user feedback
        # but keep it in the code for future reference
        self.segment_name_edit = QLineEdit()
        self.segment_name_edit.setVisible(False)
        
        # Initialize with empty fields
        self.segment_start_edit.clear()
        self.segment_end_edit.clear()
        self.segment_color_edit.clear()
        self.boundary_time_edit.clear()
        
        # Start in segment mode
        self._switch_to_segment_mode()
        
        # The old boundary editor code has been removed
        # We now use the unified editor with segment and boundary modes
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Connect timeline signals
        self.timeline_widget.position_changed.connect(self._update_cursor_position)
        
        # Connect audio signals
        self.audio_widget.position_changed.connect(self._update_cursor_position)
        
        # Connect project signals
        if hasattr(self.app, 'project_manager'):
            self.app.project_manager.project_changed.connect(self._update_ui)
            self.app.project_manager.project_loaded.connect(self._update_ui)
            self.app.project_manager.project_saved.connect(self._update_ui)
        
        # Connect LLM signals
        if hasattr(self.app, 'llm_manager'):
            self.app.llm_manager.llm_action_requested.connect(self._on_llm_action)
    
    def _load_settings(self):
        """Load application settings."""
        settings = QSettings("SequenceMaker", "SequenceMaker")
        
        # Load window geometry
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Load window state
        state = settings.value("windowState")
        if state:
            self.restoreState(state)
    
    def _save_settings(self):
        """Save application settings."""
        settings = QSettings("SequenceMaker", "SequenceMaker")
        
        # Save window geometry
        settings.setValue("geometry", self.saveGeometry())
        
        # Save window state
        settings.setValue("windowState", self.saveState())
    
    def _update_recent_files_menu(self):
        """Update the recent files menu."""
        # Clear the menu
        self.recent_files_menu.clear()
        
        # Get recent projects from config
        recent_projects = []
        if hasattr(self.app, 'config'):
            recent_projects = self.app.config.get("general", "recent_projects") or []
        
        # Add recent projects to menu
        if recent_projects:
            for project in recent_projects:
                action = QAction(project, self)
                action.triggered.connect(lambda checked, p=project: self._open_recent_project(p))
                self.recent_files_menu.addAction(action)
            
            # Add separator and clear action
            self.recent_files_menu.addSeparator()
            clear_action = QAction("Clear Recent Files", self)
            clear_action.triggered.connect(self._clear_recent_files)
            self.recent_files_menu.addAction(clear_action)
        else:
            # Add empty action
            empty_action = QAction("No Recent Files", self)
            empty_action.setEnabled(False)
            self.recent_files_menu.addAction(empty_action)
    
    def _open_recent_project(self, project_path):
        """Open a recent project."""
        # Check if file exists
        if not os.path.exists(project_path):
            QMessageBox.warning(self, "File Not Found", f"The file {project_path} does not exist.")
            return
        
        # Open the project
        self.app.project_manager.open_project(project_path)
    
    def _clear_recent_files(self):
        """Clear the recent files list."""
        if hasattr(self.app, 'config'):
            self.app.config.set("general", "recent_projects", [])
            self.app.config.save()
            self._update_recent_files_menu()
    def _update_cursor_position(self, position):
        """Update the cursor position label with formatted time."""
        formatted_time = self._format_seconds_to_hms(position, include_hundredths=True, hide_hours_if_zero=True)
        self.cursor_position_label.setText(f"Position: {formatted_time}")
        
    def update_cursor_hover_position(self, position):
        """Update the cursor hover position label with formatted time."""
        formatted_time = self._format_seconds_to_hms(position, include_hundredths=True, hide_hours_if_zero=True)
        self.cursor_hover_label.setText(f"Cursor: {formatted_time}")
        
    def clear_cursor_hover_position(self):
        """Clear the cursor hover position label."""
        self.cursor_hover_label.setText("Cursor: --:--.--")
        
    def _on_new(self):
        """Create a new project."""
        # Check for unsaved changes
        if not self._check_unsaved_changes():
            return
            
        # Create a new project
        self.app.project_manager.new_project()
        
        # Update UI
        self._update_ui()
        
    def _on_open(self):
        """Open an existing project."""
        # Check for unsaved changes
        if not self._check_unsaved_changes():
            return
            
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            self.app.config.get("general", "default_project_dir"),
            "Sequence Maker Project (*.smproj)"
        )
        
        if file_path:
            # Load project
            self.app.project_manager.load_project(file_path)
            
            # Update UI
            self._update_ui()
            
    def _on_save(self):
        """Save the current project."""
        # Check if project has a file path
        if not self.app.project_manager.current_project.file_path:
            # If not, use save as
            return self._on_save_as()
            
        # Save project
        success = self.app.project_manager.save_project()
        
        # Update UI
        if success:
            self.statusBar().showMessage("Project saved", 3000)
            
        return success
        
    def _on_save_as(self):
        """Save the current project with a new name."""
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project As",
            self.app.config.get("general", "default_project_dir"),
            "Sequence Maker Project (*.smproj)"
        )
        
        if file_path:
            # Save project
            success = self.app.project_manager.save_project(file_path)
            
            # Update UI
            if success:
                self.statusBar().showMessage("Project saved", 3000)
                
            return success
            
        return False
        
    def _on_load_audio(self):
        """Load an audio file."""
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Audio",
            self.app.config.get("general", "default_project_dir"),
            "Audio Files (*.mp3 *.wav)"
        )
        
        if file_path:
            # Load audio
            self.app.audio_manager.load_audio(file_path)
            
            # Update UI
            self._update_ui()
            
    def _on_export_json(self):
        """Export timeline to JSON format."""
        # Show directory selection dialog
        export_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            self.app.config.get("general", "default_project_dir")
        )
        
        if not export_dir:
            return
            
        # Export each timeline
        for i, timeline in enumerate(self.app.timeline_manager.timelines):
            # Generate filename
            filename = f"Ball_{i+1}.json"
            file_path = os.path.join(export_dir, filename)
            
            # Export timeline
            from export.json_exporter import export_timeline
            export_timeline(timeline, file_path)
            
        # Show success message
        self.statusBar().showMessage(f"Exported JSON to {export_dir}", 3000)
        
    def _on_export_prg(self):
        """Export timeline to PRG format."""
        # Show directory selection dialog
        export_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            self.app.config.get("general", "default_project_dir")
        )
        
        if not export_dir:
            return
            
        # Export each timeline
        for i, timeline in enumerate(self.app.timeline_manager.timelines):
            # Generate filename
            filename = f"Ball_{i+1}.prg"
            file_path = os.path.join(export_dir, filename)
            
            # Export timeline
            from export.prg_exporter import export_timeline
            export_timeline(timeline, file_path)
            
        # Show success message
        self.statusBar().showMessage(f"Exported PRG to {export_dir}", 3000)
        
    def _on_version_history(self):
        """Handle Version History action."""
        # Check if a project is loaded
        from PyQt6.QtWidgets import QMessageBox
        if not self.app.project_manager.current_project:
            QMessageBox.warning(
                self,
                "No Project Loaded",
                "Please load a project to view version history."
            )
            return
        
        # Check if the project has a file path
        if not self.app.project_manager.current_project.file_path:
            QMessageBox.warning(
                self,
                "Project Not Saved",
                "Please save the project before accessing version history."
            )
            return
        
        # Create and show version history dialog
        from ui.dialogs.version_history_dialog import VersionHistoryDialog
        dialog = VersionHistoryDialog(self.app, self)
        dialog.exec()
        
    def _check_unsaved_changes(self):
        """
        Check if there are unsaved changes and prompt the user.
        
        Returns:
            bool: True if it's safe to proceed, False otherwise.
        """
        if not self.app.project_manager.has_unsaved_changes:
            return True
            
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            "There are unsaved changes. Do you want to save them?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )
        
        if reply == QMessageBox.StandardButton.Save:
            # Save changes
            return self._on_save()
        elif reply == QMessageBox.StandardButton.Discard:
            # Discard changes
            return True
        else:
            # Cancel
            return False
            
    def _update_ui(self):
        """Update the user interface."""
        # Update window title with project name and unsaved changes indicator
        if hasattr(self.app, 'project_manager') and self.app.project_manager.current_project:
            # Get the project name
            if self.app.project_manager.current_project.file_path:
                file_name = os.path.basename(self.app.project_manager.current_project.file_path)
            else:
                file_name = "Untitled"
                
            # Add unsaved changes indicator if needed
            if hasattr(self.app.project_manager, 'has_unsaved_changes') and self.app.project_manager.has_unsaved_changes:
                self.setWindowTitle(f"{file_name} *")
            else:
                self.setWindowTitle(f"{file_name}")
            
            # Clear the project status label since we don't need to show project info there
            self.project_status_label.setText("")
        else:
            self.setWindowTitle("")
            # Clear the project status label even when no project is loaded
            self.project_status_label.setText("")
            
        # Update timeline widget
        self.timeline_widget.update()
        
        # Update audio widget
        self.audio_widget.update()
        
        # Update ball widget
        self.ball_widget.update()
        
    def _on_undo(self):
        """Undo the last action."""
        if self.app.undo_manager.can_undo():
            self.app.undo_manager.undo()
            self._update_ui()
            
    def _on_redo(self):
        """Redo the last undone action."""
        if self.app.undo_manager.can_redo():
            self.app.undo_manager.redo()
            self._update_ui()
            
    def _on_cut(self):
        """Cut the selected items."""
        # Get the currently focused widget
        from PyQt6.QtWidgets import QApplication
        focused_widget = QApplication.focusWidget()
        
        # If it's a text edit widget, use its cut method
        if hasattr(focused_widget, "cut"):
            focused_widget.cut()
        
    def _on_copy(self):
        """Copy the selected items."""
        # Get the currently focused widget
        from PyQt6.QtWidgets import QApplication
        focused_widget = QApplication.focusWidget()
        
        # If it's a text edit widget, use its copy method
        if hasattr(focused_widget, "copy"):
            focused_widget.copy()
        
    def _on_paste(self):
        """Paste the copied items."""
        # Get the currently focused widget
        from PyQt6.QtWidgets import QApplication
        focused_widget = QApplication.focusWidget()
        
        # If it's a text edit widget, use its paste method
        if hasattr(focused_widget, "paste"):
            focused_widget.paste()
        
    def _on_delete(self):
        """Delete the selected items."""
        # Get the currently focused widget
        from PyQt6.QtWidgets import QApplication
        focused_widget = QApplication.focusWidget()
        
        # If it's a text edit widget, use its clear method
        if hasattr(focused_widget, "clear"):
            focused_widget.clear()
            
    def _on_select_all(self):
        """Select all items."""
        # Get the currently focused widget
        from PyQt6.QtWidgets import QApplication
        focused_widget = QApplication.focusWidget()
        
        # If it's a text edit widget, use its selectAll method
        if hasattr(focused_widget, "selectAll"):
            focused_widget.selectAll()
            
    def _on_preferences(self):
        """Show preferences dialog."""
        from ui.dialogs.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.app, self)
        dialog.exec()
        
    def _on_zoom_in(self):
        """Zoom in."""
        # Increase zoom level
        self.timeline_widget.zoom_in()
        
    def _on_zoom_out(self):
        """Zoom out."""
        # Decrease zoom level
        self.timeline_widget.zoom_out()
        
    def _on_zoom_fit(self):
        """Zoom to fit."""
        # Reset zoom level
        self.timeline_widget.zoom_fit()
        
    def _on_add_timeline(self):
        """Add a new timeline."""
        # Add a new timeline
        self.app.timeline_manager.add_timeline()
        
        # Update UI
        self._update_ui()
        
    def _on_remove_timeline(self):
        """Remove the selected timeline."""
        # Get the selected timeline
        selected_timeline = self.timeline_widget.get_selected_timeline()
        
        if selected_timeline:
            # Remove the timeline
            self.app.timeline_manager.remove_timeline(selected_timeline)
            
            # Update UI
            self._update_ui()
        
    def _on_duplicate_timeline(self):
        """Duplicate the selected timeline."""
        # Get the selected timeline
        selected_timeline = self.timeline_widget.get_selected_timeline()
        
        if selected_timeline:
            # Duplicate the timeline
            self.app.timeline_manager.duplicate_timeline(selected_timeline)
            
            # Update UI
            self._update_ui()
            
    def _on_play(self):
        """Play audio."""
        # Play audio
        self.app.audio_manager.play()
        
        # Update UI
        self.play_action.setVisible(False)
        self.pause_action.setVisible(True)
        
    def _on_pause(self):
        """Pause audio."""
        # Pause audio
        self.app.audio_manager.pause()
        
        # Update UI
        self.pause_action.setVisible(False)
        self.play_action.setVisible(True)
        
    def _on_stop(self):
        """Stop audio."""
        # Stop audio
        self.app.audio_manager.stop()
        
        # Update UI
        self.pause_action.setVisible(False)
        self.play_action.setVisible(True)
        
    def _on_loop(self, checked):
        """Toggle audio looping."""
        # Set loop mode
        self.app.audio_manager.set_loop(checked)
        
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
        """Show key mapping dialog."""
        from ui.dialogs.key_mapping_dialog import KeyMappingDialog
        dialog = KeyMappingDialog(self.app, self)
        dialog.exec()
        
    def _on_connect_balls(self):
        """Connect to physical balls."""
        # Show ball scan dialog
        from ui.dialogs.ball_scan_dialog import BallScanDialog
        dialog = BallScanDialog(self.app, self)
        dialog.exec()
        
    def _on_llm_chat(self):
        """Handle LLM Chat action."""
        # Create the LLM chat window if it doesn't exist
        if not hasattr(self, 'llm_chat_window') or self.llm_chat_window is None:
            self._create_llm_chat_window()
        
        # Show the chat window if it's hidden, otherwise bring it to front
        if self.llm_chat_window.isHidden():
            self.llm_chat_window.show()
        else:
            self.llm_chat_window.raise_()
            self.llm_chat_window.activateWindow()
    
    def _create_llm_chat_window(self):
        """Create the LLM chat window."""
        from ui.dialogs.llm_chat_window import LLMChatWindow
        self.llm_chat_window = LLMChatWindow(self.app, self)
        
    def _on_llm_diagnostics(self):
        """Handle LLM Diagnostics action."""
        # Create and show the LLM diagnostics dialog
        from ui.dialogs.llm_diagnostics_dialog import LLMDiagnosticsDialog
        dialog = LLMDiagnosticsDialog(self.app, self)
        dialog.exec()
        
    def _on_process_lyrics(self):
        """Process lyrics for timeline."""
        # Show lyrics input dialog
        from ui.dialogs.lyrics_input_dialog import LyricsInputDialog
        dialog = LyricsInputDialog(self.app, self)
        dialog.exec()
        
    def _on_about(self):
        """Show about dialog."""
        from ui.dialogs.about_dialog import AboutDialog
        dialog = AboutDialog(self.app, self)
        dialog.exec()
        
    def _on_help(self):
        """Show help."""
        # Open help documentation
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl("https://github.com/yourusername/sequence_maker/wiki"))
        
    def _on_toggle_ball_view(self, checked):
        """Toggle ball visualization."""
        if hasattr(self, 'ball_widget'):
            self.ball_widget.setVisible(checked)
            
    def _on_toggle_audio_view(self, checked):
        """Toggle audio visualization."""
        if hasattr(self, 'audio_widget'):
            self.audio_widget.setVisible(checked)
            
    def _on_toggle_lyrics_view(self, checked):
        """Toggle lyrics visualization."""
        if hasattr(self, 'lyrics_widget'):
            self.lyrics_widget.setVisible(checked)
            
    def _format_color_tuple(self, color_tuple):
        """
        Format a color tuple as a string.
        
        Args:
            color_tuple (tuple): RGB color tuple (r, g, b)
            
        Returns:
            str: Formatted color string in the format "r,g,b"
        """
        if not isinstance(color_tuple, tuple) or len(color_tuple) != 3:
            return "255,0,0"  # Default to red if invalid
        
        r, g, b = color_tuple
        return f"{r},{g},{b}"
    
    def _format_seconds_to_hms(self, seconds, include_hundredths=True, hide_hours_if_zero=False):
        """
        Format seconds to HH:MM:SS.ss format.
        
        Args:
            seconds (float): Time in seconds
            include_hundredths (bool): Whether to include hundredths of a second
            hide_hours_if_zero (bool): Whether to hide hours if they are zero
            
        Returns:
            str: Formatted time string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds_val = seconds % 60
        
        if include_hundredths:
            seconds_format = f"{seconds_val:05.2f}"
        else:
            seconds_format = f"{int(seconds_val):02d}"
        
        if hours > 0 or not hide_hours_if_zero:
            return f"{hours:02d}:{minutes:02d}:{seconds_format}"
        else:
            return f"{minutes:02d}:{seconds_format}"
            
    def _on_add_segment(self):
        """Add a new segment."""
        # Get the current cursor position
        cursor_position = self.timeline_widget.position
        
        # Get the selected timeline
        selected_timeline = self.timeline_widget.selected_timeline
        
        if selected_timeline:
            try:
                # Create a new segment at the cursor position
                # Parse the default color
                default_color = self._parse_color_string("#FF0000")  # Red color by default
                
                self.app.timeline_manager.add_segment(
                    timeline=selected_timeline,
                    start_time=cursor_position,
                    end_time=cursor_position + 1.0,  # 1 second duration by default
                    color=default_color
                )
            except ValueError as e:
                # This shouldn't happen with our hardcoded default color, but just in case
                self.logger.error(f"Error parsing default color: {e}")
        else:
            # Show error message
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Timeline Selected", "Please select a timeline first.")
        
        # Update UI
        self._update_ui()
        
    def _on_edit_segment(self):
        """Edit the selected segment."""
        # Get the selected segment
        selected_segment = self.timeline_widget.selected_segment
        
        if selected_segment:
            # Format color tuple as string for display
            color_formatted = self._format_color_tuple(selected_segment.color)
            self.segment_color_edit.setText(color_formatted)
            
            # Format time values for better readability
            start_formatted = self._format_seconds_to_hms(selected_segment.start_time, include_hundredths=True, hide_hours_if_zero=True)
            end_formatted = self._format_seconds_to_hms(selected_segment.end_time, include_hundredths=True, hide_hours_if_zero=True)
            
            self.segment_start_edit.setText(start_formatted)
            self.segment_end_edit.setText(end_formatted)
            
    def _on_delete_segment(self):
        """Delete the selected segment."""
        # Get the selected segment
        selected_segment = self.timeline_widget.selected_segment
        selected_timeline = self.timeline_widget.selected_timeline
        
        if selected_segment and selected_timeline:
            # Delete the segment
            self.app.timeline_manager.delete_segment(selected_timeline, selected_segment)
            
            # Update UI
            self._update_ui()
            
    def _on_split_segment(self):
        """Split the selected segment."""
        # Get the selected segment
        selected_segment = self.timeline_widget.selected_segment
        selected_timeline = self.timeline_widget.selected_timeline
        
        if selected_segment and selected_timeline:
            # Get the cursor position
            cursor_position = self.timeline_widget.position
            
            # Split the segment at the cursor position
            self.app.timeline_manager.split_segment(selected_timeline, selected_segment, cursor_position)
            
            # Update UI
            self._update_ui()
            
    def _on_merge_segments(self):
        """Merge selected segments."""
        # Get the selected segments
        selected_timeline = self.timeline_widget.selected_timeline
        
        # Note: We need to implement a way to select multiple segments
        # For now, we'll just show a message that this feature is not fully implemented
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Not Implemented",
                              "Multiple segment selection is not fully implemented yet.")
        
        # No update needed since we didn't change anything
            
    def _on_clear_timeline(self):
        """Clear the timeline."""
        # Show confirmation dialog
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Clear Timeline",
            "Are you sure you want to clear the timeline?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear the timeline
            self.app.timeline_manager.clear_timeline()
            
            # Update UI
            self._update_ui()
    
    def _parse_color_string(self, color_string):
        """
        Parse a color string into an RGB tuple.
        
        Handles various formats:
        - "red", "green", "blue", etc. (common color names)
        - "#RRGGBB" (hex format)
        - "rgb(r,g,b)" (CSS-style format)
        - "r,g,b" (comma-separated values)
        
        Args:
            color_string (str): Color string to parse
            
        Returns:
            tuple: (r, g, b) color tuple with values in range 0-255
            
        Raises:
            ValueError: If the color string cannot be parsed
        """
        color_string = color_string.strip().lower()
        
        # Common color names
        color_names = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "orange": (255, 165, 0),
            "purple": (128, 0, 128),
            "pink": (255, 192, 203)
        }
        
        if color_string in color_names:
            return color_names[color_string]
        
        # Hex format: #RRGGBB
        if color_string.startswith("#") and len(color_string) == 7:
            try:
                r = int(color_string[1:3], 16)
                g = int(color_string[3:5], 16)
                b = int(color_string[5:7], 16)
                return (r, g, b)
            except ValueError:
                pass
        
        # CSS-style format: rgb(r,g,b)
        if color_string.startswith("rgb(") and color_string.endswith(")"):
            try:
                rgb = color_string[4:-1].split(",")
                if len(rgb) == 3:
                    r = int(rgb[0].strip())
                    g = int(rgb[1].strip())
                    b = int(rgb[2].strip())
                    return (r, g, b)
            except ValueError:
                pass
        
        # Comma-separated values: r,g,b
        if "," in color_string:
            try:
                rgb = color_string.split(",")
                if len(rgb) == 3:
                    r = int(rgb[0].strip())
                    g = int(rgb[1].strip())
                    b = int(rgb[2].strip())
                    return (r, g, b)
            except ValueError:
                pass
        
        # If we get here, we couldn't parse the color string
        raise ValueError(f"Could not parse color string: {color_string}")
    
    def _parse_time_string(self, time_string):
        """
        Parse a time string into seconds.
        
        Handles various formats:
        - "123.45" (seconds as float)
        - "01:23.45" (minutes:seconds.hundredths)
        - "01:23" (minutes:seconds)
        - "01:23:45.67" (hours:minutes:seconds.hundredths)
        
        Args:
            time_string (str): Time string to parse
            
        Returns:
            float: Time in seconds
            
        Raises:
            ValueError: If the time string cannot be parsed
        """
        time_string = time_string.strip()
        
        # Try direct float conversion first
        try:
            return float(time_string)
        except ValueError:
            pass
        
        # Try MM:SS.ss format
        if ":" in time_string:
            parts = time_string.split(":")
            
            if len(parts) == 2:  # MM:SS or MM:SS.ss
                minutes, seconds = parts
                try:
                    return float(minutes) * 60 + float(seconds)
                except ValueError:
                    pass
                    
            elif len(parts) == 3:  # HH:MM:SS or HH:MM:SS.ss
                hours, minutes, seconds = parts
                try:
                    return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
                except ValueError:
                    pass
        
        # If we get here, we couldn't parse the time string
        raise ValueError(f"Could not parse time string: {time_string}")
    
    def _on_segment_apply(self):
        """Handle segment apply button click."""
        # Get segment data from form
        color = self.segment_color_edit.text()
        
        try:
            # Parse time strings
            start = self._parse_time_string(self.segment_start_edit.text())
            end = self._parse_time_string(self.segment_end_edit.text())
            
            # Parse color string
            try:
                parsed_color = self._parse_color_string(color)
            except ValueError:
                # Show error message for invalid color
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Invalid Color Format",
                                   f"Please enter a valid color value.\n\nSupported formats:\n"
                                   f"- Color names (e.g., red, green, blue)\n"
                                   f"- Hex format (e.g., #FF0000)\n"
                                   f"- RGB format (e.g., rgb(255,0,0) or 255,0,0)")
                return
            
            # Get the selected segment and its timeline
            selected_segment = self.timeline_widget.selected_segment
            selected_timeline = self.timeline_widget.selected_timeline
            
            if selected_segment and selected_timeline:
                # Update segment
                self.app.timeline_manager.modify_segment(
                    timeline=selected_timeline,
                    segment=selected_segment,
                    start_time=start,
                    end_time=end,
                    color=parsed_color
                )
            else:
                # Show error message
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "No Selection", "Please select a segment to modify.")
        except ValueError as e:
            # Show error message
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Time Format",
                               f"Please enter a valid time value.\n\nSupported formats:\n"
                               f"- Seconds (e.g., 123.45)\n"
                               f"- Minutes:Seconds (e.g., 01:23.45)\n"
                               f"- Hours:Minutes:Seconds (e.g., 01:23:45.67)")
    
    def _on_segment_cancel(self):
        """Handle segment cancel button click."""
        # Clear segment form
        self.segment_color_edit.clear()
        self.segment_start_edit.clear()
        self.segment_end_edit.clear()
    def _on_boundary_time_apply(self):
        """Handle boundary time apply button click."""
        # Get boundary time from form
        time_text = self.boundary_time_edit.text()
        
        try:
            # Parse time string
            time = self._parse_time_string(time_text)
            
            # Add debug logging
            print("Boundary time apply:")
            print(f"  Has boundary_editor_time: {hasattr(self, 'boundary_editor_time')}")
            print(f"  Has boundary_editor_left_segment: {hasattr(self, 'boundary_editor_left_segment')}")
            print(f"  Has boundary_editor_right_segment: {hasattr(self, 'boundary_editor_right_segment')}")
            print(f"  Has boundary_editor_timeline: {hasattr(self, 'boundary_editor_timeline')}")
            
            if hasattr(self, 'boundary_editor_left_segment'):
                print(f"  Left segment: {self.boundary_editor_left_segment}")
            
            if hasattr(self, 'boundary_editor_right_segment'):
                print(f"  Right segment: {self.boundary_editor_right_segment}")
            
            if hasattr(self, 'boundary_editor_timeline'):
                print(f"  Timeline: {self.boundary_editor_timeline}")
            
            # Update boundary by modifying the segments on either side
            if (hasattr(self, 'boundary_editor_time') and
                hasattr(self, 'boundary_editor_left_segment') and
                hasattr(self, 'boundary_editor_right_segment') and
                hasattr(self, 'boundary_editor_timeline')):
                
                # Get the stored boundary information
                left_segment = self.boundary_editor_left_segment
                right_segment = self.boundary_editor_right_segment
                timeline = self.boundary_editor_timeline  # Use the stored timeline
                
                print(f"  Timeline: {timeline}")
                print(f"  Left segment: {left_segment}")
                print(f"  Right segment: {right_segment}")
                
                if timeline and left_segment and right_segment:
                    # Modify the end time of the left segment
                    self.app.timeline_manager.modify_segment(
                        timeline=timeline,
                        segment=left_segment,
                        end_time=time
                    )
                    
                    # Modify the start time of the right segment
                    self.app.timeline_manager.modify_segment(
                        timeline=timeline,
                        segment=right_segment,
                        start_time=time
                    )
                else:
                    # Show error message
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "No Boundary Selected", "Please select a boundary to modify.")
            else:
                # Show error message
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "No Boundary Selected", "Please select a boundary to modify.")
        except ValueError:
            # Show error message
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Time Format",
                               f"Please enter a valid time value.\n\nSupported formats:\n"
                               f"- Seconds (e.g., 123.45)\n"
                               f"- Minutes:Seconds (e.g., 01:23.45)\n"
                               f"- Hours:Minutes:Seconds (e.g., 01:23:45.67)")
    
    def _on_editor_apply(self):
        """Handle editor apply button click based on current mode."""
        if self.editor_mode == "segment":
            self._on_segment_apply()
        else:  # boundary mode
            self._on_boundary_time_apply()
    
    def _on_editor_cancel(self):
        """Handle editor cancel button click based on current mode."""
        if self.editor_mode == "segment":
            self._on_segment_cancel()
        else:  # boundary mode
            self.boundary_time_edit.clear()
    
    def _switch_to_segment_mode(self):
        """Switch the editor to segment mode."""
        self.editor_mode = "segment"
        self.editor_stack.setCurrentIndex(0)  # Show segment editor
    
    def _switch_to_boundary_mode(self):
        """Switch the editor to boundary mode."""
        self.editor_mode = "boundary"
        self.editor_stack.setCurrentIndex(1)  # Show boundary editor
            
    def show_segment_editor(self, timeline, segment):
        """
        Show the segment editor for the selected segment.
        
        Args:
            timeline: The timeline containing the segment
            segment: The segment to edit
        """
        # Switch to segment mode
        self._switch_to_segment_mode()
        
        # Set the selected segment and timeline
        self.timeline_widget.selected_segment = segment
        self.timeline_widget.selected_timeline = timeline
        
        # Populate the segment editor fields
        self._on_edit_segment()
        
        # Hide hover info label
        if hasattr(self, 'hover_info_label'):
            self.hover_info_label.hide()
        
    def hide_segment_editor(self):
        """Clear the segment editor fields but don't hide it."""
        # Just clear the fields
        self.segment_start_edit.clear()
        self.segment_end_edit.clear()
        self.segment_color_edit.clear()
            
    def show_boundary_editor(self, timeline, time, left_segment, right_segment):
        """
        Show the boundary editor for the selected boundary.
        
        Args:
            timeline: The timeline containing the boundary
            time: The time position of the boundary
            left_segment: The segment to the left of the boundary
            right_segment: The segment to the right of the boundary
        """
        # Switch to boundary mode
        self._switch_to_boundary_mode()
        
        # Hide hover info label
        if hasattr(self, 'hover_info_label'):
            self.hover_info_label.hide()
        
        # Store boundary information
        self.boundary_editor_time = time
        self.boundary_editor_left_segment = left_segment
        self.boundary_editor_right_segment = right_segment
        self.boundary_editor_timeline = timeline  # Store the timeline as well
        
        # Format time
        time_str = self._format_seconds_to_hms(time, include_hundredths=True, hide_hours_if_zero=True)
        
        # Populate boundary editor field
        self.boundary_time_edit.setText(time_str)
        
        # Print debug info
        print(f"Boundary editor initialized with:")
        print(f"  Time: {time}")
        print(f"  Left segment: {left_segment}")
        print(f"  Right segment: {right_segment}")
        print(f"  Timeline: {timeline}")
        
    def hide_boundary_editor(self):
        """Clear the boundary editor fields and switch back to segment mode."""
        # Clear the boundary time field
        self.boundary_time_edit.clear()
        
        # Switch back to segment mode
        self._switch_to_segment_mode()
    
    def _on_llm_action(self, action_type, parameters):
        """Handle LLM action requests."""
        # Initialize handler classes
        file_handlers = FileHandlers(self)
        edit_handlers = EditHandlers(self)
        view_handlers = ViewHandlers(self)
        timeline_handlers = TimelineHandlers(self)
        playback_handlers = PlaybackHandlers(self)
        tools_handlers = ToolsHandlers(self)
        segment_handlers = SegmentHandlers(self)
        boundary_handlers = BoundaryHandlers(self)
        utility_handlers = UtilityHandlers(self)
        
        # Route action to appropriate handler
        if action_type == "create_segment":
            segment_handlers.handle_create_segment(parameters)
        elif action_type == "modify_segment":
            segment_handlers.handle_modify_segment(parameters)
        elif action_type == "delete_segment":
            segment_handlers.handle_delete_segment(parameters)
        elif action_type == "set_default_color":
            segment_handlers.handle_set_default_color(parameters)
        elif action_type == "add_effect":
            segment_handlers.handle_add_effect(parameters)
        elif action_type == "clear_timeline":
            timeline_handlers.handle_clear_timeline(parameters)
        elif action_type == "create_segments_batch":
            segment_handlers.handle_create_segments_batch(parameters)
        elif action_type == "play_audio":
            playback_handlers.handle_play_audio(parameters)
        elif action_type == "pause_audio":
            playback_handlers.handle_pause_audio(parameters)
        elif action_type == "stop_audio":
            playback_handlers.handle_stop_audio(parameters)
        elif action_type == "seek_audio":
            playback_handlers.handle_seek_audio(parameters)
        elif action_type == "set_volume":
            playback_handlers.handle_set_volume(parameters)
        else:
            self.logger.warning(f"Unknown LLM action type: {action_type}")
    
    def keyPressEvent(self, event: QKeyEvent):
        """
        Handle key press events for adding color blocks.
        
        This method handles keyboard input for adding color blocks to the timeline:
        - qwer... keys for ball 1 (timeline 0)
        - asdf... keys for ball 2 (timeline 1)
        - zxcv... keys for ball 3 (timeline 2)
        - Number keys for all balls (all timelines)
        """
        # Get the key text
        key_text = event.text().lower()
        
        # Check if we have a key mapping for this key
        if hasattr(self.app, 'project_manager') and self.app.project_manager.current_project:
            # Get the key mappings from the constants
            from app.constants import DEFAULT_KEY_MAPPING
            
            # Check if the key is in the default key mapping
            if key_text in DEFAULT_KEY_MAPPING:
                # Get the mapping for this key
                mapping = DEFAULT_KEY_MAPPING[key_text]
                
                # Get the color and timelines
                color = mapping["color"]
                timelines = mapping["timelines"]
                
                # Get the current position
                position = self.app.audio_manager.position
                
                # Create a segment at the current position for each timeline
                for timeline_index in timelines:
                    # Get the timelines using the get_timelines method
                    all_timelines = self.app.timeline_manager.get_timelines()
                    
                    # Check if the timeline index is valid
                    if timeline_index < len(all_timelines):
                        timeline = all_timelines[timeline_index]
                        
                        # Find the end time for the new segment
                        # It should be either the end of the timeline or the start of the next segment
                        end_time = self.app.project_manager.current_project.total_duration
                        
                        # Check if there are any segments that start after the current position
                        for segment in timeline.segments:
                            if segment.start_time > position:
                                # Found a segment that starts after the current position
                                # Set the end time to the start of this segment
                                end_time = min(end_time, segment.start_time)
                        
                        # Check if the current position is inside an existing segment
                        segment_to_truncate = None
                        for segment in timeline.segments:
                            if segment.start_time <= position < segment.end_time:
                                # Found a segment that contains the current position
                                segment_to_truncate = segment
                                break
                        
                        # If we found a segment to truncate, modify it to end at the current position
                        if segment_to_truncate:
                            self.app.timeline_manager.modify_segment(
                                timeline=timeline,
                                segment=segment_to_truncate,
                                end_time=position
                            )
                        
                        # Create a segment that extends to the calculated end time
                        self.app.timeline_manager.add_segment(
                            timeline=timeline,
                            start_time=position,
                            end_time=end_time,
                            color=color
                        )
                
                # Accept the event
                event.accept()
                return
        
        # Pass the event to the parent class
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save settings
        self._save_settings()
        
        # Check for unsaved changes
        if self.app.project_manager.has_unsaved_changes:
            # Ask user if they want to save
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Do you want to save your changes before exiting?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                # Save project
                self.app.project_manager.save_project()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                # Discard changes
                event.accept()
            else:
                # Cancel close
                event.ignore()
        else:
            # No unsaved changes
            event.accept()