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
        
        # Export actions
        self.export_json_action = QAction("Export to &JSON...", self)
        self.export_json_action.setStatusTip("Export timeline to JSON format")
        self.export_json_action.triggered.connect(self._on_export_json)
        
        self.export_prg_action = QAction("Export to &PRG...", self)
        self.export_prg_action.setStatusTip("Export timeline to PRG format")
        self.export_prg_action.triggered.connect(self._on_export_prg)
        
        # Version history action
        self.version_history_action = QAction("&Version History...", self)
        self.version_history_action.setStatusTip("View and restore previous versions")
        self.version_history_action.triggered.connect(self._on_version_history)
        
        # Exit action
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.setStatusTip("Exit the application")
        self.exit_action.triggered.connect(self.close)
        
        # Edit actions
        self.undo_action = QAction("&Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.setStatusTip("Undo the last action")
        self.undo_action.triggered.connect(self._on_undo)
        
        self.redo_action = QAction("&Redo", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.setStatusTip("Redo the last undone action")
        self.redo_action.triggered.connect(self._on_redo)
        
        self.cut_action = QAction("Cu&t", self)
        self.cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        self.cut_action.setStatusTip("Cut the selected items")
        self.cut_action.triggered.connect(self._on_cut)
        
        self.copy_action = QAction("&Copy", self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.setStatusTip("Copy the selected items")
        self.copy_action.triggered.connect(self._on_copy)
        
        self.paste_action = QAction("&Paste", self)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_action.setStatusTip("Paste the copied items")
        self.paste_action.triggered.connect(self._on_paste)
        
        self.delete_action = QAction("&Delete", self)
        self.delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_action.setStatusTip("Delete the selected items")
        self.delete_action.triggered.connect(self._on_delete)
        
        self.select_all_action = QAction("Select &All", self)
        self.select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        self.select_all_action.setStatusTip("Select all items")
        self.select_all_action.triggered.connect(self._on_select_all)
        
        # Preferences action
        self.preferences_action = QAction("&Preferences...", self)
        self.preferences_action.setStatusTip("Edit application preferences")
        self.preferences_action.triggered.connect(self._on_preferences)
        
        # View actions
        self.zoom_in_action = QAction("Zoom &In", self)
        self.zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        self.zoom_in_action.setStatusTip("Zoom in")
        self.zoom_in_action.triggered.connect(self._on_zoom_in)
        
        self.zoom_out_action = QAction("Zoom &Out", self)
        self.zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        self.zoom_out_action.setStatusTip("Zoom out")
        self.zoom_out_action.triggered.connect(self._on_zoom_out)
        
        self.zoom_fit_action = QAction("Zoom &Fit", self)
        self.zoom_fit_action.setStatusTip("Zoom to fit")
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
        
        self.connect_balls_action = QAction("&Connect Balls...", self)
        self.connect_balls_action.setStatusTip("Connect to physical balls")
        self.connect_balls_action.triggered.connect(self._on_connect_balls)
        
        self.llm_chat_action = QAction("&LLM Chat...", self)
        self.llm_chat_action.setStatusTip("Open LLM chat window")
        self.llm_chat_action.triggered.connect(self._on_llm_chat)
        
        self.llm_diagnostics_action = QAction("LLM &Diagnostics...", self)
        self.llm_diagnostics_action.setStatusTip("View LLM diagnostics")
        self.llm_diagnostics_action.triggered.connect(self._on_llm_diagnostics)
        
        self.process_lyrics_action = QAction("Process &Lyrics...", self)
        self.process_lyrics_action.setStatusTip("Process lyrics for timeline")
        self.process_lyrics_action.triggered.connect(self._on_process_lyrics)
        
        # Playback actions
        self.play_action = QAction("&Play", self)
        self.play_action.setShortcut(QKeySequence("Space"))
        self.play_action.setStatusTip("Play audio")
        self.play_action.triggered.connect(self._on_play)
        
        self.pause_action = QAction("P&ause", self)
        self.pause_action.setShortcut(QKeySequence("Space"))
        self.pause_action.setStatusTip("Pause audio")
        self.pause_action.triggered.connect(self._on_pause)
        self.pause_action.setVisible(False)  # Hide initially
        
        self.stop_action = QAction("&Stop", self)
        self.stop_action.setShortcut(QKeySequence("Escape"))
        self.stop_action.setStatusTip("Stop audio")
        self.stop_action.triggered.connect(self._on_stop)
        
        # Help actions
        self.about_action = QAction("&About", self)
        self.about_action.setStatusTip("About Sequence Maker")
        self.about_action.triggered.connect(self._on_about)
        
        self.help_action = QAction("&Help", self)
        self.help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        self.help_action.setStatusTip("Show help")
        self.help_action.triggered.connect(self._on_help)
        
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
            
    def _check_unsaved_changes(self):
        """
        Check if there are unsaved changes and prompt the user.
        
        Returns:
            bool: True if it's safe to proceed, False otherwise.
        """
        if not self.app.project_manager.has_unsaved_changes():
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
            # Update undo/redo actions based on current state
            self.undo_action.setEnabled(self.app.undo_manager.can_undo())
            self.redo_action.setEnabled(self.app.undo_manager.can_redo())
            
            # Connect signals if they exist
            if hasattr(self.app.undo_manager, 'can_undo_changed'):
                self.app.undo_manager.can_undo_changed.connect(self.undo_action.setEnabled)
            if hasattr(self.app.undo_manager, 'can_redo_changed'):
                self.app.undo_manager.can_redo_changed.connect(self.redo_action.setEnabled)
        
        # Connect timeline manager signals
        if hasattr(self.app.timeline_manager, 'position_changed'):
            self.app.timeline_manager.position_changed.connect(self._update_cursor_position)
        
        # Connect audio manager signals
        if hasattr(self.app.audio_manager, 'playback_started'):
            self.app.audio_manager.playback_started.connect(self._on_playback_started)
        if hasattr(self.app.audio_manager, 'playback_paused'):
            self.app.audio_manager.playback_paused.connect(self._on_playback_paused)
        if hasattr(self.app.audio_manager, 'playback_stopped'):
            self.app.audio_manager.playback_stopped.connect(self._on_playback_stopped)
        
        # Connect LLM manager signals
        if hasattr(self.app.llm_manager, 'llm_action_requested'):
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
        recent_projects = self.app.config.get("general", "recent_projects") or []
        
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
    
    def _on_recent_project(self):
        """Handle opening a recent project."""
        # Get the action that triggered this
        action = self.sender()
        if not action:
            return
            
        # Get the project path from the action's data
        project_path = action.data()
        if not project_path:
            return
            
        # Check for unsaved changes
        if not self._check_unsaved_changes():
            return
            
        # Load the project
        self.app.project_manager.load_project(project_path)
        
        # Update UI
        self._update_ui()
    
    def _on_clear_recent_projects(self):
        """Clear the list of recent projects."""
        # Clear the recent projects list in the config
        self.app.config.set("general", "recent_projects", [])
        self.app.config.save()
        
        # Update the menu
        self._update_recent_projects_menu()
    
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
            from sequence_maker.export.json_exporter import export_timeline
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
            from sequence_maker.export.prg_exporter import export_timeline
            export_timeline(timeline, file_path)
            
        # Show success message
        self.statusBar().showMessage(f"Exported PRG to {export_dir}", 3000)
        
    def _on_version_history(self):
        """Show version history dialog."""
        from sequence_maker.ui.dialogs.version_history_dialog import VersionHistoryDialog
        dialog = VersionHistoryDialog(self.app, self)
        dialog.exec()
        
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
        focused_widget = QApplication.focusWidget()
        
        # If it's a text edit widget, use its cut method
        if hasattr(focused_widget, "cut"):
            focused_widget.cut()
        
    def _on_copy(self):
        """Copy the selected items."""
        # Get the currently focused widget
        focused_widget = QApplication.focusWidget()
        
        # If it's a text edit widget, use its copy method
        if hasattr(focused_widget, "copy"):
            focused_widget.copy()
        
    def _on_paste(self):
        """Paste the copied items."""
        # Get the currently focused widget
        focused_widget = QApplication.focusWidget()
        
        # If it's a text edit widget, use its paste method
        if hasattr(focused_widget, "paste"):
            focused_widget.paste()
        
    def _on_delete(self):
        """Delete the selected items."""
        # Get the currently focused widget
        focused_widget = QApplication.focusWidget()
        
        # If it's a text edit widget, use its clear method
        if hasattr(focused_widget, "clear"):
            focused_widget.clear()
            
    def _on_select_all(self):
        """Select all items."""
        # Get the currently focused widget
        focused_widget = QApplication.focusWidget()
        
        # If it's a text edit widget, use its selectAll method
        if hasattr(focused_widget, "selectAll"):
            focused_widget.selectAll()
            
    def _on_preferences(self):
        """Show preferences dialog."""
        from sequence_maker.ui.dialogs.settings_dialog import SettingsDialog
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
            
    def _on_key_mapping(self):
        """Show key mapping dialog."""
        from sequence_maker.ui.dialogs.key_mapping_dialog import KeyMappingDialog
        dialog = KeyMappingDialog(self.app, self)
        dialog.exec()
        
    def _on_connect_balls(self):
        """Connect to physical balls."""
        # Show ball scan dialog
        from sequence_maker.ui.dialogs.ball_scan_dialog import BallScanDialog
        dialog = BallScanDialog(self.app, self)
        dialog.exec()
        
    def _on_process_lyrics(self):
        """Process lyrics for timeline."""
        # Show lyrics input dialog
        from sequence_maker.ui.dialogs.lyrics_input_dialog import LyricsInputDialog
        dialog = LyricsInputDialog(self.app, self)
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
        
    def _on_about(self):
        """Show about dialog."""
        from sequence_maker.ui.dialogs.about_dialog import AboutDialog
        dialog = AboutDialog(self.app, self)
        dialog.exec()
        
    def _on_help(self):
        """Show help."""
        # Open help documentation
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl("https://github.com/yourusername/sequence_maker/wiki"))
        
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
        
    def _on_llm_action(self, action_type, action_data):
        """
        Handle LLM action request.
        
        Args:
            action_type (str): Type of action requested
            action_data (dict): Action data
        """
        # Process the action based on its type
        if action_type == "create_segment":
            # Create a segment
            self.app.timeline_manager.create_segment(action_data)
        elif action_type == "modify_segment":
            # Modify a segment
            self.app.timeline_manager.modify_segment(action_data)
        elif action_type == "delete_segment":
            # Delete a segment
            self.app.timeline_manager.delete_segment(action_data)
        elif action_type == "play_audio":
            # Play audio
            self._on_play()
        elif action_type == "pause_audio":
            # Pause audio
            self._on_pause()
        elif action_type == "stop_audio":
            # Stop audio
            self._on_stop()
            
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