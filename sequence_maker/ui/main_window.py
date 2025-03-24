"""
Sequence Maker - Main Window

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
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QFont, QPixmap, QImage

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
        
        self.logger = logging.getLogger("SequenceMaker.MainWindow")
        self.app = app
        
        # Set window properties
        self.setWindowTitle("Sequence Maker")
        self.setMinimumSize(1200, 800)
        
        # Create APIs
        self.context_api = AppContextAPI(app)
        self.timeline_action_api = TimelineActionAPI(app)
        self.audio_action_api = AudioActionAPI(app)
        
        # Create LLM chat window
        self.llm_chat_window = None  # Will be created after UI setup
        self.audio_action_api = AudioActionAPI(app)
        
        # Create actions
        self._create_actions()
        
        # Create UI
        self._create_ui()
        
        # Create menus
        self._create_menus()
        
        # Create toolbars
        self._create_toolbars()
        
        # Create status bar
        self._create_status_bar()
        
        # Connect signals
        self._connect_signals()
        
        # Load settings
        self._load_settings()
        
        # Set up timer for periodic updates
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(100)  # Update every 100ms
        
        # Set up timer for cursor position updates
        self.cursor_timer = QTimer(self)
        self.cursor_timer.timeout.connect(self._update_cursor_position)
        self.cursor_timer.start(50)  # Update every 50ms
        
        # Create LLM chat window
        self._create_llm_chat_window()
        
        # Initialize UI state
        self._update_ui()
        
        self.logger.info("Main window initialized")
    
    def _create_actions(self):
        """Create actions for the main window."""
        # File actions
        self.new_action = QAction("&New", self)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.setStatusTip("Create a new project")
        self.new_action.triggered.connect(self._on_new)
        
        self.open_action = QAction("&Open...", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.setStatusTip("Open an existing project")
        self.open_action.triggered.connect(self._on_open)
        
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setStatusTip("Save the current project")
        self.save_action.triggered.connect(self._on_save)
        
        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_as_action.setStatusTip("Save the current project with a new name")
        self.save_as_action.triggered.connect(self._on_save_as)
        
        self.load_audio_action = QAction("Load &Audio...", self)
        self.load_audio_action.setStatusTip("Load an audio file")
        self.load_audio_action.triggered.connect(self._on_load_audio)
        
        self.export_json_action = QAction("Export to &JSON...", self)
        self.export_json_action.setStatusTip("Export timelines to JSON files")
        self.export_json_action.triggered.connect(self._on_export_json)
        
        self.export_prg_action = QAction("Export to &PRG...", self)
        self.export_prg_action.setStatusTip("Export timelines to PRG files")
        self.export_prg_action.triggered.connect(self._on_export_prg)
        
        self.version_history_action = QAction("&Version History...", self)
        self.version_history_action.setStatusTip("View and restore project versions")
        self.version_history_action.triggered.connect(self._on_version_history)
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.setStatusTip("Exit the application")
        self.exit_action.triggered.connect(self.close)
        
        # Edit actions
        self.undo_action = QAction("&Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.setStatusTip("Undo the last action")
        self.undo_action.triggered.connect(self._on_undo)
        self.undo_action.setEnabled(False)
        
        self.redo_action = QAction("&Redo", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.setStatusTip("Redo the last undone action")
        self.redo_action.triggered.connect(self._on_redo)
        self.redo_action.setEnabled(False)
        
        # View actions
        self.zoom_in_action = QAction("Zoom &In", self)
        self.zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        self.zoom_in_action.setStatusTip("Zoom in on the timeline")
        self.zoom_in_action.triggered.connect(self._on_zoom_in)
        
        self.zoom_out_action = QAction("Zoom &Out", self)
        self.zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        self.zoom_out_action.setStatusTip("Zoom out on the timeline")
        self.zoom_out_action.triggered.connect(self._on_zoom_out)
        
        self.zoom_fit_action = QAction("&Fit to Window", self)
        self.zoom_fit_action.setShortcut("Ctrl+0")
        self.zoom_fit_action.setStatusTip("Fit the timeline to the window")
        self.zoom_fit_action.triggered.connect(self._on_zoom_fit)
        
        # Timeline actions
        self.add_timeline_action = QAction("&Add Timeline", self)
        self.add_timeline_action.setStatusTip("Add a new timeline")
        self.add_timeline_action.triggered.connect(self._on_add_timeline)
        
        self.remove_timeline_action = QAction("&Remove Timeline", self)
        self.remove_timeline_action.setStatusTip("Remove the selected timeline")
        self.remove_timeline_action.triggered.connect(self._on_remove_timeline)
        
        self.duplicate_timeline_action = QAction("&Duplicate Timeline", self)
        self.duplicate_timeline_action.setStatusTip("Duplicate the selected timeline")
        self.duplicate_timeline_action.triggered.connect(self._on_duplicate_timeline)
        
        # Tools actions
        self.key_mapping_action = QAction("&Key Mapping...", self)
        self.key_mapping_action.setStatusTip("Configure key mappings")
        self.key_mapping_action.triggered.connect(self._on_key_mapping)
        
        self.connect_balls_action = QAction("&Connect Balls", self)
        self.connect_balls_action.setStatusTip("Connect to juggling balls")
        self.connect_balls_action.triggered.connect(self._on_connect_balls)
        self.connect_balls_action.setCheckable(True)
        
        self.llm_chat_action = QAction("&LLM Chat...", self)
        self.llm_chat_action.setStatusTip("Open LLM chat interface")
        self.llm_chat_action.triggered.connect(self._on_llm_chat)
        
        self.llm_diagnostics_action = QAction("LLM &Diagnostics...", self)
        self.llm_diagnostics_action.setStatusTip("View LLM performance metrics and diagnostics")
        self.llm_diagnostics_action.triggered.connect(self._on_llm_diagnostics)
        
        self.process_lyrics_action = QAction("Process &Lyrics...", self)
        self.process_lyrics_action.setStatusTip("Process lyrics for the current audio")
        self.process_lyrics_action.triggered.connect(self._on_process_lyrics)
        
        # Playback actions
        self.play_action = QAction("&Play", self)
        self.play_action.setShortcut("Space")
        self.play_action.setStatusTip("Play the audio")
        self.play_action.triggered.connect(self._on_play)
        
        self.pause_action = QAction("P&ause", self)
        self.pause_action.setShortcut("Space")
        self.pause_action.setStatusTip("Pause the audio")
        self.pause_action.triggered.connect(self._on_pause)
        self.pause_action.setVisible(False)  # Initially hidden
        
        self.stop_action = QAction("&Stop", self)
        self.stop_action.setShortcut("Escape")
        self.stop_action.setStatusTip("Stop the audio")
        self.stop_action.triggered.connect(self._on_stop)
        
        # Help actions
        self.about_action = QAction("&About", self)
        self.about_action.setStatusTip("Show information about the application")
        self.about_action.triggered.connect(self._on_about)
        
        self.help_action = QAction("&Help", self)
        self.help_action.setStatusTip("Show help")
        self.help_action.triggered.connect(self._on_help)
    
    def _create_menus(self):
        """Create menus for the main window."""
        # Create menu bar
        self.menubar = self.menuBar()
        
        # File menu
        self.file_menu = self.menubar.addMenu("&File")
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        
        # Recent projects submenu
        self.recent_projects_menu = self.file_menu.addMenu("Recent Projects")
        self._update_recent_projects_menu()
        
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.load_audio_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.export_json_action)
        self.file_menu.addAction(self.export_prg_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.version_history_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        
        # Edit menu
        self.edit_menu = self.menubar.addMenu("&Edit")
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
        self.view_menu = self.menubar.addMenu("&View")
        self.view_menu.addAction(self.zoom_in_action)
        self.view_menu.addAction(self.zoom_out_action)
        self.view_menu.addAction(self.zoom_fit_action)
        
        # Timeline menu
        self.timeline_menu = self.menubar.addMenu("&Timeline")
        self.timeline_menu.addAction(self.add_timeline_action)
        self.timeline_menu.addAction(self.remove_timeline_action)
        self.timeline_menu.addAction(self.duplicate_timeline_action)
        
        # Tools menu
        self.tools_menu = self.menubar.addMenu("&Tools")
        self.tools_menu.addAction(self.key_mapping_action)
        self.tools_menu.addAction(self.connect_balls_action)
        self.tools_menu.addAction(self.llm_chat_action)
        self.tools_menu.addAction(self.llm_diagnostics_action)
        self.tools_menu.addAction(self.process_lyrics_action)
        
        # Playback menu
        self.playback_menu = self.menubar.addMenu("&Playback")
        self.playback_menu.addAction(self.play_action)
        self.playback_menu.addAction(self.pause_action)
        self.playback_menu.addAction(self.stop_action)
        
        # Help menu
        self.help_menu = self.menubar.addMenu("&Help")
        self.help_menu.addAction(self.about_action)
        self.help_menu.addAction(self.help_action)
    
    def _create_ui(self):
        """Create the user interface."""
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create splitter
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_layout.addWidget(self.splitter)
        
        # Create timeline widget
        self.timeline_widget = TimelineWidget(self.app, self)
        self.splitter.addWidget(self.timeline_widget)
        
        # Create audio widget
        self.audio_widget = AudioWidget(self.app, self)
        self.splitter.addWidget(self.audio_widget)
        
        # Create lyrics widget
        self.lyrics_widget = LyricsWidget(self.app, self)
        self.splitter.addWidget(self.lyrics_widget)
        
        # Set splitter sizes
        self.splitter.setSizes([400, 200, 100])
    
    def _create_toolbars(self):
        """Create toolbars for the main window."""
        # File toolbar
        self.file_toolbar = self.addToolBar("File")
        self.file_toolbar.addAction(self.new_action)
        self.file_toolbar.addAction(self.open_action)
        self.file_toolbar.addAction(self.save_action)
        
        # Edit toolbar
        self.edit_toolbar = self.addToolBar("Edit")
        self.edit_toolbar.addAction(self.undo_action)
        self.edit_toolbar.addAction(self.redo_action)
        
        # View toolbar
        self.view_toolbar = self.addToolBar("View")
        self.view_toolbar.addAction(self.zoom_in_action)
        self.view_toolbar.addAction(self.zoom_out_action)
        self.view_toolbar.addAction(self.zoom_fit_action)
        
        # Add LLM Chat button to view toolbar
        self.llm_chat_toolbar_button = QPushButton("LLM Chat")
        self.llm_chat_toolbar_button.setToolTip("Open LLM chat interface")
        self.llm_chat_toolbar_button.clicked.connect(self._on_llm_chat)
        self.view_toolbar.addWidget(self.llm_chat_toolbar_button)
        
        # Playback toolbar
        self.playback_toolbar = self.addToolBar("Playback")
        self.playback_toolbar.addAction(self.play_action)
        self.playback_toolbar.addAction(self.pause_action)
        self.playback_toolbar.addAction(self.stop_action)
    
    def _create_status_bar(self):
        """Create status bar for the main window."""
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        
        # Create ball widget
        self.ball_widget = BallWidget(self.app, self)
        self.ball_widget.setFixedHeight(BALL_VISUALIZATION_SIZE)
        self.statusbar.addWidget(self.ball_widget)
        
        # Create cursor position label
        self.cursor_position_label = QLabel("Cursor: 00:00.00")
        self.statusbar.addPermanentWidget(self.cursor_position_label)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Connect undo manager signals
        if self.app.undo_manager:
            self.app.undo_manager.can_undo_changed.connect(self.undo_action.setEnabled)
            self.app.undo_manager.can_redo_changed.connect(self.redo_action.setEnabled)
        
        # Connect timeline manager signals
        self.app.timeline_manager.position_changed.connect(self._on_position_changed)
        
        # Connect audio manager signals
        self.app.audio_manager.playback_started.connect(self._on_playback_started)
        self.app.audio_manager.playback_paused.connect(self._on_playback_paused)
        self.app.audio_manager.playback_stopped.connect(self._on_playback_stopped)
        
        # Connect LLM manager signals
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
    
    def _update_ui(self):
        """Update the user interface."""
        # Update timeline widget
        self.timeline_widget.update()
        
        # Update audio widget
        self.audio_widget.update()
        
        # Update ball widget
        self.ball_widget.update()
    
    def _update_cursor_position(self):
        """Update the cursor position label."""
        position = self.app.timeline_manager.position
        
        # Format position as MM:SS.ss
        minutes = int(position / 60)
        seconds = position % 60
        self.cursor_position_label.setText(f"Cursor: {minutes:02d}:{seconds:05.2f}")
    
    def _update_recent_projects_menu(self):
        """Update the recent projects menu."""
        # Clear menu
        self.recent_projects_menu.clear()
        
        # Get recent projects
        recent_projects = self.app.config.get_recent_projects()
        
        # Add actions for each recent project
        for project in recent_projects:
            action = QAction(os.path.basename(project), self)
            action.setData(project)
            action.triggered.connect(self._on_recent_project)
            self.recent_projects_menu.addAction(action)
        
        # Add separator and clear action if there are recent projects
        if recent_projects:
            self.recent_projects_menu.addSeparator()
            clear_action = QAction("Clear Recent Projects", self)
            clear_action.triggered.connect(self._on_clear_recent_projects)
            self.recent_projects_menu.addAction(clear_action)
    
    def _create_llm_chat_window(self):
        """Create the LLM chat window."""
        if self.llm_chat_window is None:
            self.llm_chat_window = LLMChatWindow(self.app, self)
            
            # Hide by default
            self.llm_chat_window.hide()
    
    def _on_llm_chat(self):
        """Handle LLM Chat action."""
        # Create the LLM chat window if it doesn't exist
        if self.llm_chat_window is None:
            self._create_llm_chat_window()
        
        # Show the chat window if it's hidden, otherwise bring it to front
        if self.llm_chat_window.isHidden():
            self.llm_chat_window.show()
        else:
            self.llm_chat_window.raise_()
            self.llm_chat_window.activateWindow()
    
    def _on_llm_diagnostics(self):
        """Handle LLM Diagnostics action."""
        # Create and show the LLM diagnostics dialog
        dialog = LLMDiagnosticsDialog(self.app, self)
        dialog.exec()
    
    def _on_version_history(self):
        """Handle Version History action."""
        # Check if a project is loaded
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
        dialog = VersionHistoryDialog(self.app, self)
        dialog.exec()