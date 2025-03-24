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
        self.resize(1280, 720)
        
        # Set window class name to match desktop entry StartupWMClass
        self.setWindowIconText("SequenceMaker")
        self.setObjectName("SequenceMaker")
        
        # Set window icon - use the PNG version
        icon_path = get_icon_path("sm_app_icon_better.jpeg")
        self.logger.info(f"Setting window icon from: {icon_path}")
        
        # Create icon from the PNG with multiple sizes
        window_icon = QIcon()
        for size in [16, 24, 32, 48, 64, 128, 256]:
            window_icon.addPixmap(QPixmap(icon_path).scaled(
                size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        # Set the window icon
        self.setWindowIcon(window_icon)
        
        # Set window icon as a property
        self.setProperty("windowIcon", window_icon)
        
        # Create UI components
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_status_bar()
        self._create_central_widget()
        
        # Connect signals
        self._connect_signals()
        
        # Restore window state
        self._restore_window_state()
    
    def _create_actions(self):
        """Create actions for menus and toolbars."""
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
        
        self.cut_action = QAction("Cu&t", self)
        self.cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        self.cut_action.setStatusTip("Cut the selected segment")
        self.cut_action.triggered.connect(self._on_cut)
        
        self.copy_action = QAction("&Copy", self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.setStatusTip("Copy the selected segment")
        self.copy_action.triggered.connect(self._on_copy)
        
        self.paste_action = QAction("&Paste", self)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_action.setStatusTip("Paste the copied segment")
        self.paste_action.triggered.connect(self._on_paste)
        
        self.delete_action = QAction("&Delete", self)
        self.delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_action.setStatusTip("Delete the selected segment")
        self.delete_action.triggered.connect(self._on_delete)
        
        self.select_all_action = QAction("Select &All", self)
        self.select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        self.select_all_action.setStatusTip("Select all segments")
        self.select_all_action.triggered.connect(self._on_select_all)
        
        self.preferences_action = QAction("&Preferences...", self)
        self.preferences_action.setStatusTip("Edit application preferences")
        self.preferences_action.triggered.connect(self._on_preferences)
        
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
        self.key_mapping_action.setStatusTip("Configure keyboard mappings")
        self.key_mapping_action.triggered.connect(self._on_key_mapping)
        
        self.connect_balls_action = QAction("&Connect to Balls", self)
        self.connect_balls_action.setStatusTip("Connect to LTX balls")
        self.connect_balls_action.triggered.connect(self._on_connect_balls)
        self.llm_chat_action = QAction("&LLM Chat...", self)
        self.llm_chat_action.setStatusTip("Open LLM chat interface")
        self.llm_chat_action.triggered.connect(self._on_llm_chat)
        
        self.process_lyrics_action = QAction("Process &Lyrics", self)
        self.process_lyrics_action.setStatusTip("Process audio to extract and align lyrics")
        self.process_lyrics_action.triggered.connect(self._on_process_lyrics)
        self.llm_chat_action.triggered.connect(self._on_llm_chat)
        
        # Playback actions
        self.play_action = QAction("&Play", self)
        self.play_action.setShortcut("Space")
        self.play_action.setStatusTip("Start playback")
        self.play_action.triggered.connect(self._on_play)
        
        self.pause_action = QAction("P&ause", self)
        self.pause_action.setShortcut("Space")
        self.pause_action.setStatusTip("Pause playback")
        self.pause_action.triggered.connect(self._on_pause)
        self.pause_action.setVisible(False)
        
        self.stop_action = QAction("&Stop", self)
        self.stop_action.setShortcut("Escape")
        self.stop_action.setStatusTip("Stop playback")
        self.stop_action.triggered.connect(self._on_stop)
        
        # Help actions
        self.about_action = QAction("&About", self)
        self.about_action.setStatusTip("Show information about the application")
        self.about_action.triggered.connect(self._on_about)
        
        self.help_action = QAction("&Help", self)
        self.help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
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
        self.edit_toolbar.addAction(self.cut_action)
        self.edit_toolbar.addAction(self.copy_action)
        self.edit_toolbar.addAction(self.paste_action)
        
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
        
        # Import widgets
        from PyQt6.QtWidgets import QLineEdit, QFrame
        from PyQt6.QtGui import QRegularExpressionValidator
        from PyQt6.QtCore import QRegularExpression
        
        # Create a container widget for the entire status bar to ensure consistent layout
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(5, 0, 5, 0)
        status_layout.setSpacing(10)
        
        # Create ball widget
        self.ball_widget = BallWidget(self.app, self)
        self.ball_widget.setFixedHeight(BALL_VISUALIZATION_SIZE)
        status_layout.addWidget(self.ball_widget)
        
        # Add a spacer to push everything else to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        status_layout.addWidget(spacer)
        
        # Create cursor position label
        self.cursor_position_label = QLabel("Cursor: 00:00.00")
        self.cursor_position_label.setFixedWidth(140)
        self.cursor_position_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.cursor_position_label)
        
        # Add vertical separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        status_layout.addWidget(separator1)
        
        # Add position label and input
        position_label = QLabel("Pos:")
        position_label.setFixedWidth(30)
        status_layout.addWidget(position_label)
        
        # Add editable time input field with HH:MM:SS format
        self.time_input = QLineEdit()
        self.time_input.setFixedWidth(70)
        self.time_input.setText("00:00.00")
        self.time_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Set validator to allow valid time values in MM:SS.SS or HH:MM:SS.SS format
        # This regex allows either:
        # - MM:SS.SS (e.g., 05:30.75)
        # - HH:MM:SS.SS (e.g., 01:05:30.75)
        time_regex = QRegularExpression("^(([0-9]{2}):)?([0-5][0-9]):([0-5][0-9]\\.[0-9]{2})$")
        validator = QRegularExpressionValidator(time_regex)
        self.time_input.setValidator(validator)
        
        # Update width to accommodate the new format
        self.time_input.setFixedWidth(90)
        
        # Connect signal to update position when edited
        self.time_input.editingFinished.connect(self._on_time_input_changed)
        status_layout.addWidget(self.time_input)
        
        # Add vertical separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        status_layout.addWidget(separator2)
        
        # Add sequence length label and input
        length_label = QLabel("Length:")
        length_label.setFixedWidth(50)
        status_layout.addWidget(length_label)
        
        # Add editable sequence length input field with HH:MM:SS format
        self.length_input = QLineEdit()
        self.length_input.setFixedWidth(70)
        self.length_input.setText("00:01:00")  # Default 1 minute
        self.length_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Set validator to only allow valid time values in HH:MM:SS format
        self.length_input.setValidator(validator)  # Reuse the same validator
        status_layout.addWidget(self.length_input)
        
        # Add Apply button (more compact)
        self.apply_length_button = QPushButton("Apply")
        self.apply_length_button.setToolTip("Apply the sequence length")
        self.apply_length_button.setFixedWidth(60)
        self.apply_length_button.clicked.connect(self._on_apply_sequence_length)
        status_layout.addWidget(self.apply_length_button)
        
        # Add the status container to the status bar
        self.statusbar.addPermanentWidget(status_container)
        # Create a hidden position label for compatibility with old code
        self.position_label = QLabel("Position: 0.00s")
        self.position_label.setVisible(False)
        
        # Create segment editor container (initially hidden)
        self.segment_editor_container = QWidget()
        segment_editor_layout = QHBoxLayout(self.segment_editor_container)
        segment_editor_layout.setContentsMargins(5, 0, 5, 0)
        segment_editor_layout.setSpacing(10)
        
        # Create boundary editor container (initially hidden)
        self.boundary_editor_container = QWidget()
        boundary_editor_layout = QHBoxLayout(self.boundary_editor_container)
        boundary_editor_layout.setContentsMargins(5, 0, 5, 0)
        boundary_editor_layout.setSpacing(10)
        
        # Start time editor
        start_time_label = QLabel("Start:")
        start_time_label.setFixedWidth(40)
        segment_editor_layout.addWidget(start_time_label)
        
        self.segment_start_input = QLineEdit()
        self.segment_start_input.setFixedWidth(90)
        self.segment_start_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.segment_start_input.setValidator(validator)  # Reuse the same time validator
        segment_editor_layout.addWidget(self.segment_start_input)
        
        # End time editor
        end_time_label = QLabel("End:")
        end_time_label.setFixedWidth(40)
        segment_editor_layout.addWidget(end_time_label)
        
        self.segment_end_input = QLineEdit()
        self.segment_end_input.setFixedWidth(90)
        self.segment_end_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.segment_end_input.setValidator(validator)  # Reuse the same time validator
        segment_editor_layout.addWidget(self.segment_end_input)
        
        # RGB color editor
        color_label = QLabel("RGB:")
        color_label.setFixedWidth(40)
        segment_editor_layout.addWidget(color_label)
        
        # Create a container for the RGB inputs
        rgb_container = QWidget()
        rgb_layout = QHBoxLayout(rgb_container)
        rgb_layout.setContentsMargins(0, 0, 0, 0)
        rgb_layout.setSpacing(5)
        
        # RGB validators
        rgb_regex = QRegularExpression("^([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$")
        rgb_validator = QRegularExpressionValidator(rgb_regex)
        
        # R input
        self.segment_r_input = QLineEdit()
        self.segment_r_input.setFixedWidth(40)
        self.segment_r_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.segment_r_input.setValidator(rgb_validator)
        rgb_layout.addWidget(self.segment_r_input)
        
        # G input
        self.segment_g_input = QLineEdit()
        self.segment_g_input.setFixedWidth(40)
        self.segment_g_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.segment_g_input.setValidator(rgb_validator)
        rgb_layout.addWidget(self.segment_g_input)
        
        # B input
        self.segment_b_input = QLineEdit()
        self.segment_b_input.setFixedWidth(40)
        self.segment_b_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.segment_b_input.setValidator(rgb_validator)
        rgb_layout.addWidget(self.segment_b_input)
        
        segment_editor_layout.addWidget(rgb_container)
        
        # Apply button
        self.apply_segment_button = QPushButton("Apply")
        self.apply_segment_button.setToolTip("Apply changes to the selected segment")
        self.apply_segment_button.setFixedWidth(60)
        self.apply_segment_button.clicked.connect(self._on_apply_segment_changes)
        segment_editor_layout.addWidget(self.apply_segment_button)
        
        # Boundary time editor
        boundary_time_label = QLabel("Boundary Time:")
        boundary_time_label.setFixedWidth(100)
        boundary_editor_layout.addWidget(boundary_time_label)
        
        self.boundary_time_input = QLineEdit()
        self.boundary_time_input.setFixedWidth(90)
        self.boundary_time_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.boundary_time_input.setValidator(validator)  # Reuse the same time validator
        boundary_editor_layout.addWidget(self.boundary_time_input)
        
        # Apply button
        self.apply_boundary_button = QPushButton("Apply")
        self.apply_boundary_button.setToolTip("Apply changes to the boundary time")
        self.apply_boundary_button.setFixedWidth(60)
        self.apply_boundary_button.clicked.connect(self._on_apply_boundary_changes)
        boundary_editor_layout.addWidget(self.apply_boundary_button)
        
        # Add spacer to push everything to the left
        boundary_spacer = QWidget()
        boundary_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        boundary_editor_layout.addWidget(boundary_spacer)
        
        # Add the segment editor container to the status bar (initially hidden)
        self.statusbar.addWidget(self.segment_editor_container)
        self.segment_editor_container.setVisible(False)
        
        # Add the boundary editor container to the status bar (initially hidden)
        self.statusbar.addWidget(self.boundary_editor_container)
        self.boundary_editor_container.setVisible(False)
        
        # Connect signals for segment editor fields
        self.segment_start_input.editingFinished.connect(self._on_segment_time_changed)
        self.segment_end_input.editingFinished.connect(self._on_segment_time_changed)
        self.segment_r_input.editingFinished.connect(self._on_segment_color_changed)
        self.segment_g_input.editingFinished.connect(self._on_segment_color_changed)
        self.segment_b_input.editingFinished.connect(self._on_segment_color_changed)
        
        # Connect signals for boundary editor fields
        self.boundary_time_input.editingFinished.connect(self._on_boundary_time_changed)
        self.position_label.setVisible(False)
    
    def _create_central_widget(self):
        """Create central widget for the main window."""
        # Create central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create lyrics widget (placed at the top)
        self.lyrics_widget = LyricsWidget(self.app, self)
        self.main_layout.addWidget(self.lyrics_widget, 1)  # 1 = small stretch factor
        
        # Create audio widget (placed directly above timeline)
        self.audio_widget = AudioWidget(self.app, self)
        self.main_layout.addWidget(self.audio_widget, 1)  # 1 = small stretch factor
        
        # Create timeline widget
        self.timeline_widget = TimelineWidget(self.app, self)
        self.main_layout.addWidget(self.timeline_widget, 3)  # 3 = larger stretch factor
        
        # Ball visualization will be added to the status bar
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Connect timeline manager signals
        self.app.timeline_manager.position_changed.connect(self._on_position_changed)
        
        # Connect audio manager signals
        self.app.audio_manager.audio_loaded.connect(self._on_audio_loaded)
        self.app.audio_manager.audio_started.connect(self._on_audio_started)
        self.app.audio_manager.audio_paused.connect(self._on_audio_paused)
        self.app.audio_manager.audio_stopped.connect(self._on_audio_stopped)
        
        # Connect project manager signals
        self.app.project_manager.project_loaded.connect(self._on_project_loaded)
        self.app.project_manager.project_saved.connect(self._on_project_saved)
        self.app.project_manager.project_changed.connect(self._on_project_changed)
        
        # Connect undo manager signals
        self.app.undo_manager.undo_stack_changed.connect(self._update_undo_actions)
        self.app.undo_manager.redo_stack_changed.connect(self._update_undo_actions)
        
        # Connect lyrics manager signals
        if hasattr(self.app, 'lyrics_manager'):
            self.app.lyrics_manager.lyrics_processed.connect(self.lyrics_widget.update_lyrics)
    
    def _restore_window_state(self):
        """Restore window state from settings."""
        settings = QSettings("LTX Guru", "Sequence Maker")
        
        # Restore window geometry
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Restore window state
        state = settings.value("windowState")
        if state:
            self.restoreState(state)
    
    def _save_window_state(self):
        """Save window state to settings."""
        settings = QSettings("LTX Guru", "Sequence Maker")
        
        # Save window geometry
        settings.setValue("geometry", self.saveGeometry())
        
        # Save window state
        settings.setValue("windowState", self.saveState())
    
    def _on_new(self):
        """Handle New action."""
        # Check for unsaved changes
        if self._check_unsaved_changes():
            # Create new project
            project = self.app.project_manager.new_project()
            
            # Force UI refresh
            self.timeline_widget.timeline_container.update_size()
            self.timeline_widget.timeline_container.update()
            
            # Reset position to 0
            self.app.timeline_manager.set_position(0.0)
            
            # Update sequence length input
            self._format_length_input(project.total_duration)
            
            # Update window title
            self._update_window_title()
            
            # Select the first timeline (Ball 1) if available
            if project.timelines and len(project.timelines) > 0:
                self.logger.debug(f"Selecting first timeline: {project.timelines[0].name}")
                self.timeline_widget.select_timeline(project.timelines[0])
                
                # Ensure the timeline widget has focus, not the time input field
                self.timeline_widget.setFocus()
            
            # Show status message
            self.statusbar.showMessage("Created new project", 5000)
            
            # Set a default zoom level for new projects
            self.logger.debug("Setting default zoom level for new project")
            project.zoom_level = 1.0  # Default zoom level
            self.timeline_widget.set_zoom(project.zoom_level)
    
    def _on_open(self):
        """Handle Open action."""
        # Check for unsaved changes
        if not self._check_unsaved_changes():
            return
        
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            self.app.config.get("general", "default_project_dir"),
            f"Sequence Maker Projects (*{PROJECT_FILE_EXTENSION})"
        )
        
        if file_path:
            # Load project
            self.app.project_manager.load_project(file_path)
    
    def _on_save(self):
        """
        Handle Save action.
        
        Returns:
            bool: True if the project was saved successfully, False otherwise.
        """
        # If project has no file path, use Save As
        if not self.app.project_manager.current_project or not self.app.project_manager.current_project.file_path:
            return self._on_save_as()
        else:
            # Save project
            return self.app.project_manager.save_project()
    
    def _on_save_as(self):
        """
        Handle Save As action.
        
        Returns:
            bool: True if the project was saved successfully, False otherwise.
        """
        if not self.app.project_manager.current_project:
            return False
        
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project",
            self.app.config.get("general", "default_project_dir"),
            f"Sequence Maker Projects (*{PROJECT_FILE_EXTENSION})"
        )
        
        if file_path:
            # Add extension if not present
            if not file_path.endswith(PROJECT_FILE_EXTENSION):
                file_path += PROJECT_FILE_EXTENSION
            
            # Save project
            return self.app.project_manager.save_project(file_path)
        
        # User cancelled the save dialog
        return False
    
    def _on_load_audio(self):
        """Handle Load Audio action."""
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Audio",
            "",
            "Audio Files (*.mp3 *.wav *.ogg)"
        )
        
        if file_path:
            # Load audio
            self.app.audio_manager.load_audio(file_path)
    
    def _on_export_json(self):
        """Handle Export to JSON action."""
        if not self.app.project_manager.current_project:
            return
        
        # Show directory dialog
        directory = QFileDialog.getExistingDirectory(
            self,
            "Export to JSON",
            ""
        )
        
        if directory:
            # Export each timeline to JSON
            for i, timeline in enumerate(self.app.project_manager.current_project.timelines):
                # Create JSON data
                json_data = timeline.to_json_sequence()
                
                # Create file path
                file_path = os.path.join(directory, f"{timeline.name.replace(' ', '_')}.json")
                
                # Write to file
                with open(file_path, 'w') as f:
                    json.dump(json_data, f, indent=2)
            
            # Show success message
            QMessageBox.information(
                self,
                "Export Successful",
                f"Exported {len(self.app.project_manager.current_project.timelines)} timelines to JSON."
            )
    
    def _on_export_prg(self):
        """Handle Export to PRG action."""
        if not self.app.project_manager.current_project:
            return
        
        # Show directory dialog
        directory = QFileDialog.getExistingDirectory(
            self,
            "Export to PRG",
            ""
        )
        
        if directory:
            # Export each timeline to PRG
            for i, timeline in enumerate(self.app.project_manager.current_project.timelines):
                # Create JSON data
                json_data = timeline.to_json_sequence()
                
                # Create JSON file path
                json_path = os.path.join(directory, f"{timeline.name.replace(' ', '_')}.json")
                
                # Create PRG file path
                prg_path = os.path.join(directory, f"{timeline.name.replace(' ', '_')}.prg")
                
                # Write JSON to file
                with open(json_path, 'w') as f:
                    json.dump(json_data, f, indent=2)
                
                # Call prg_generator with absolute path
                try:
                    import subprocess
                    import os
                    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
                    prg_generator_path = os.path.join(root_dir, "prg_generator.py")
                    
                    self.logger.debug(f"Using prg_generator at: {prg_generator_path}")
                    
                    subprocess.run(
                        ["python3", prg_generator_path, json_path, prg_path],
                        check=True
                    )
                except Exception as e:
                    self.logger.error(f"Error generating PRG file: {e}")
                    QMessageBox.warning(
                        self,
                        "Export Error",
                        f"Error generating PRG file: {str(e)}"
                    )
                    return
            
            # Show success message
            QMessageBox.information(
                self,
                "Export Successful",
                f"Exported {len(self.app.project_manager.current_project.timelines)} timelines to PRG."
            )
    
    def _on_undo(self):
        """Handle Undo action."""
        self.app.undo_manager.undo()
    
    def _on_redo(self):
        """Handle Redo action."""
        self.app.undo_manager.redo()
    
    def _on_cut(self):
        """Handle Cut action."""
        self.timeline_widget.cut_selected_segment()
    
    def _on_copy(self):
        """Handle Copy action."""
        self.timeline_widget.copy_selected_segment()
    
    def _on_paste(self):
        """Handle Paste action."""
        self.timeline_widget.paste_segment()
    
    def _on_delete(self):
        """Handle Delete action."""
        self.timeline_widget.delete_selected_segment()
    
    def _on_select_all(self):
        """Handle Select All action."""
        self.timeline_widget.select_all_segments()
    
    def _on_preferences(self):
        """Handle Preferences action."""
        dialog = SettingsDialog(self.app, self)
        dialog.exec()
    
    def _on_zoom_in(self):
        """Handle Zoom In action."""
        self.timeline_widget.zoom_in()
    
    def _on_zoom_out(self):
        """Handle Zoom Out action."""
        self.timeline_widget.zoom_out()
    
    def _on_zoom_fit(self):
        """Handle Zoom Fit action."""
        self.timeline_widget.zoom_fit()
        
        # Save the zoom level to the project
        if self.app.project_manager.current_project:
            self.logger.debug(f"Saving zoom level to project: {self.timeline_widget.zoom_level}")
            self.app.project_manager.current_project.zoom_level = self.timeline_widget.zoom_level
            
            # Mark project as changed
            self.app.project_manager.project_changed.emit()
    
    def _on_add_timeline(self):
        """Handle Add Timeline action."""
        self.app.timeline_manager.add_timeline()
    
    def _on_remove_timeline(self):
        """Handle Remove Timeline action."""
        if self.app.timeline_manager.selected_timeline:
            self.app.timeline_manager.remove_timeline(self.app.timeline_manager.selected_timeline)
    
    def _on_duplicate_timeline(self):
        """Handle Duplicate Timeline action."""
        if self.app.timeline_manager.selected_timeline:
            self.app.timeline_manager.duplicate_timeline(self.app.timeline_manager.selected_timeline)
    
    def _on_key_mapping(self):
        """Handle Key Mapping action."""
        dialog = KeyMappingDialog(self.app, self)
        dialog.exec()
    
    def _on_connect_balls(self):
        """Handle Connect to Balls action."""
        self.app.ball_manager.connect_balls()
    
    def _on_llm_chat(self):
        """Handle LLM Chat action."""
        # Open the LLM chat dialog
        from ui.dialogs.llm_chat_dialog import LLMChatDialog
        dialog = LLMChatDialog(self.app, self)
        dialog.exec()
    
    def _on_process_lyrics(self):
        """Handle Process Lyrics action."""
        print("[MainWindow] Process Lyrics action triggered")
        self.logger.info("Process Lyrics action triggered")
        
        # Check if audio is loaded
        if not self.app.audio_manager.audio_file:
            print("[MainWindow] No audio file loaded")
            QMessageBox.warning(
                self,
                "No Audio Loaded",
                "Please load an audio file before processing lyrics."
            )
            return
        
        print(f"[MainWindow] Audio file: {self.app.audio_manager.audio_file}")
        
        # Check if lyrics manager exists
        if not hasattr(self.app, 'lyrics_manager'):
            print("[MainWindow] No lyrics manager found")
            QMessageBox.warning(
                self,
                "Lyrics Manager Not Found",
                "The lyrics manager is not available."
            )
            return
        
        # Update status in lyrics widget
        self.lyrics_widget.update_status("Starting lyrics processing...", 0)
        
        # Process audio to extract and align lyrics
        print("[MainWindow] Calling lyrics_manager.process_audio")
        self.app.lyrics_manager.process_audio(self.app.audio_manager.audio_file)
        
        # Show status message
        self.statusbar.showMessage("Processing audio for lyrics alignment...", 5000)
    
    
    def _on_play(self):
        """Handle Play action."""
        self.app.audio_manager.play()
    
    def _on_pause(self):
        """Handle Pause action."""
        self.app.audio_manager.pause()
    
    def _on_stop(self):
        """Handle Stop action."""
        self.logger.debug("Stop button clicked, calling audio_manager.stop()")
        result = self.app.audio_manager.stop()
        self.logger.debug(f"audio_manager.stop() returned {result}")
        
        # Ensure the timeline position is reset to 0
        self.app.timeline_manager.set_position(0.0)
        
        # Force update of the time input field
        self._format_time_input(0.0)
    
    def _on_about(self):
        """Handle About action."""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def _on_help(self):
        """Handle Help action."""
        # Open help documentation
        pass
    
    def _on_time_input_changed(self):
        """Handle time input field changes."""
        try:
            # Get the time value from the input field
            time_text = self.time_input.text()
            
            # Parse the time components based on format
            parts = time_text.split(':')
            
            if len(parts) == 2:
                # Format is MM:SS.SS
                minutes = int(parts[0])
                seconds = float(parts[1])
                hours = 0
            elif len(parts) == 3:
                # Format is HH:MM:SS.SS
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
            else:
                raise ValueError(f"Invalid time format: {time_text}")
            
            # Convert to seconds
            time_value = hours * 3600 + minutes * 60 + seconds
            
            # Update the position
            self.app.timeline_manager.set_position(time_value)
            
            self.logger.debug(f"Time input changed to {time_text} ({time_value}s)")
        except (ValueError, AttributeError) as e:
            # If the input is not valid, reset to current position
            self.logger.error(f"Invalid time input: {e}")
            self._format_time_input(self.app.timeline_manager.position)
    
    def _format_time_input(self, seconds):
        """Format time in seconds and update the time input field."""
        # Format with hundredths of a second and hide hours if zero
        formatted_time = self._format_seconds_to_hms(seconds, include_hundredths=True, hide_hours_if_zero=True)
        self.time_input.setText(formatted_time)
    
    def update_cursor_position(self, seconds):
        """Update the cursor position label with the given time in seconds."""
        if seconds < 0:
            seconds = 0
        
        # Format with hundredths of a second and hide hours if zero
        formatted_time = self._format_seconds_to_hms(seconds, include_hundredths=True, hide_hours_if_zero=True)
        self.cursor_position_label.setText(f"Cursor: {formatted_time}")
    
    def _on_position_changed(self, position):
        """Handle position changed signal."""
        # Update position label (hidden but kept for compatibility)
        if hasattr(self, 'position_label'):
            self.position_label.setText(f"Position: {position:.2f}s")
        
        # Update time input field with HH:MM:SS format
        # Always update when position is 0 (stop button pressed) or if the field doesn't have focus
        if position == 0.0 or not self.time_input.hasFocus():
            self._format_time_input(position)
    
    def _on_audio_loaded(self, file_path, duration):
        """Handle audio loaded signal."""
        # Update status bar
        self.statusbar.showMessage(f"Loaded audio: {os.path.basename(file_path)}", 5000)
        
        # Update sequence length input to match audio duration
        if self.app.project_manager.current_project:
            # Update project's total duration
            self.app.project_manager.current_project.total_duration = duration
            
            # Update sequence length input
            self._format_length_input(duration)
            
            # Save audio data to project
            if self.app.audio_manager.audio_data is not None:
                # Ensure we use absolute path
                abs_file_path = os.path.abspath(file_path)
                self.logger.debug(f"Saving audio data to project: {abs_file_path}")
                
                try:
                    # Read the audio file as bytes instead of using the NumPy array
                    with open(abs_file_path, 'rb') as f:
                        audio_bytes = f.read()
                    
                    # Save the bytes data to the project
                    self.app.project_manager.current_project.set_audio(
                        abs_file_path,  # Use absolute path
                        audio_bytes
                    )
                    self.app.project_manager.current_project.audio_duration = duration
                    
                    # Log the size of the audio data for debugging
                    self.logger.debug(f"Audio data size: {len(audio_bytes)} bytes")
                    
                    # Mark project as changed
                    self.app.project_manager.project_changed.emit()
                    
                    # Force an immediate save to ensure audio is persisted
                    if self.app.project_manager.current_project.file_path:
                        self.logger.debug("Forcing immediate save to persist audio")
                        self.app.project_manager.save_project()
                except Exception as e:
                    self.logger.error(f"Error saving audio to project: {e}")
            
            # Update project's audio file and data
            self.logger.info(f"Updating project audio data from file: {file_path}")
            self.app.project_manager.current_project.set_audio(file_path)
            
            # Mark project as changed
            self.app.project_manager.project_changed.emit()
    
    def _on_audio_started(self):
        """Handle audio started signal."""
        # Update play/pause actions
        self.play_action.setVisible(False)
        self.pause_action.setVisible(True)
    
    def _on_audio_paused(self):
        """Handle audio paused signal."""
        # Update play/pause actions
        self.play_action.setVisible(True)
        self.pause_action.setVisible(False)
    
    def _on_audio_stopped(self):
        """Handle audio stopped signal."""
        # Update play/pause actions
        self.play_action.setVisible(True)
        self.pause_action.setVisible(False)
    def show_segment_editor(self, timeline, segment):
        """
        Show the segment editor with the given segment's values.
        
        Args:
            timeline: Timeline containing the segment.
            segment: Segment to edit.
        """
        if not segment:
            self.hide_segment_editor()
            return
        
        # Format start and end times
        start_time_str = self._format_seconds_to_hms(
            segment.start_time, include_hundredths=True, hide_hours_if_zero=True)
        end_time_str = self._format_seconds_to_hms(
            segment.end_time, include_hundredths=True, hide_hours_if_zero=True)
        
        # Set values in the editor fields
        self.segment_start_input.setText(start_time_str)
        self.segment_end_input.setText(end_time_str)
        self.segment_r_input.setText(str(segment.color[0]))
        self.segment_g_input.setText(str(segment.color[1]))
        self.segment_b_input.setText(str(segment.color[2]))
        
        # Store references to the timeline and segment
        self.segment_editor_timeline = timeline
        self.segment_editor_segment = segment
        
        # Show the segment editor
        self.segment_editor_container.setVisible(True)
        
        # Clear any status bar message
        self.statusbar.clearMessage()
    def show_boundary_editor(self, timeline, time, left_segment, right_segment):
        """
        Show the boundary editor with the given boundary time.
        
        Args:
            timeline: Timeline containing the segments.
            time: Time position of the boundary.
            left_segment: Segment to the left of the boundary.
            right_segment: Segment to the right of the boundary.
        """
        # Format boundary time
        time_str = self._format_seconds_to_hms(
            time, include_hundredths=True, hide_hours_if_zero=True)
        
        # Set value in the editor field
        self.boundary_time_input.setText(time_str)
        
        # Store references to the timeline and segments
        self.boundary_editor_timeline = timeline
        self.boundary_editor_time = time
        self.boundary_editor_left_segment = left_segment
        self.boundary_editor_right_segment = right_segment
        
        # Show the boundary editor
        self.boundary_editor_container.setVisible(True)
        
        # Hide the segment editor if visible
        self.segment_editor_container.setVisible(False)
        
        # Clear any status bar message
        self.statusbar.clearMessage()
    
    def hide_boundary_editor(self):
        """Hide the boundary editor."""
        self.boundary_editor_container.setVisible(False)
        self.boundary_editor_timeline = None
        self.boundary_editor_time = None
        self.boundary_editor_left_segment = None
        self.boundary_editor_right_segment = None
    
    def _on_boundary_time_changed(self):
        """Handle boundary time input changes."""
        if not hasattr(self, 'boundary_editor_timeline') or not self.boundary_editor_timeline:
            return
        
        try:
            # Parse boundary time
            time_str = self.boundary_time_input.text()
            new_time = self._parse_time_input(time_str)
            
            # Validate time
            if new_time < 0:
                self.logger.warning("Boundary time cannot be negative")
                # Reset to original value
                self.boundary_time_input.setText(self._format_seconds_to_hms(
                    self.boundary_editor_time, include_hundredths=True, hide_hours_if_zero=True))
                return
            
            # Update segments
            if self.boundary_editor_left_segment and self.boundary_editor_right_segment:
                # Update left segment end time
                self.app.timeline_manager.modify_segment(
                    timeline=self.boundary_editor_timeline,
                    segment=self.boundary_editor_left_segment,
                    end_time=new_time
                )
                
                # Update right segment start time
                self.app.timeline_manager.modify_segment(
                    timeline=self.boundary_editor_timeline,
                    segment=self.boundary_editor_right_segment,
                    start_time=new_time
                )
                
                # Update stored boundary time
                self.boundary_editor_time = new_time
                
                # Update the selected boundary time in the timeline widget
                if hasattr(self.timeline_widget, 'selected_boundary_time'):
                    self.timeline_widget.selected_boundary_time = new_time
        except Exception as e:
            self.logger.error(f"Error updating boundary time: {e}")
            # Reset to original value
            self.boundary_time_input.setText(self._format_seconds_to_hms(
                self.boundary_editor_time, include_hundredths=True, hide_hours_if_zero=True))
    
    def _on_apply_boundary_changes(self):
        """Apply boundary time changes."""
        self._on_boundary_time_changed()
    
    def hide_segment_editor(self):
        """Hide the segment editor."""
        """Hide the segment editor."""
        self.segment_editor_container.setVisible(False)
        self.segment_editor_timeline = None
        self.segment_editor_segment = None
    
    def _on_segment_time_changed(self):
        """Handle segment time input changes."""
        if not hasattr(self, 'segment_editor_segment') or not self.segment_editor_segment:
            return
        
        try:
            # Parse start time
            start_time_str = self.segment_start_input.text()
            start_time = self._parse_time_input(start_time_str)
            
            # Parse end time
            end_time_str = self.segment_end_input.text()
            end_time = self._parse_time_input(end_time_str)
            
            # Validate times
            if start_time >= end_time:
                self.logger.warning("Start time must be less than end time")
                # Reset to original values
                self.show_segment_editor(self.segment_editor_timeline, self.segment_editor_segment)
                return
            
            # Update segment
            self.app.timeline_manager.modify_segment(
                timeline=self.segment_editor_timeline,
                segment=self.segment_editor_segment,
                start_time=start_time,
                end_time=end_time
            )
        except Exception as e:
            self.logger.error(f"Error updating segment times: {e}")
            # Reset to original values
            self.show_segment_editor(self.segment_editor_timeline, self.segment_editor_segment)
    
    def _on_segment_color_changed(self):
        """Handle segment color input changes."""
        if not hasattr(self, 'segment_editor_segment') or not self.segment_editor_segment:
            return
        
        try:
            # Parse RGB values
            r = int(self.segment_r_input.text())
            g = int(self.segment_g_input.text())
            b = int(self.segment_b_input.text())
            
            # Validate RGB values
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # Update segment
            self.app.timeline_manager.modify_segment(
                timeline=self.segment_editor_timeline,
                segment=self.segment_editor_segment,
                color=(r, g, b)
            )
        except Exception as e:
            self.logger.error(f"Error updating segment color: {e}")
            # Reset to original values
            self.show_segment_editor(self.segment_editor_timeline, self.segment_editor_segment)
    
    def _on_apply_segment_changes(self):
        """Apply all segment changes at once."""
        if not hasattr(self, 'segment_editor_segment') or not self.segment_editor_segment:
            return
        
        try:
            # Parse start time
            start_time_str = self.segment_start_input.text()
            start_time = self._parse_time_input(start_time_str)
            
            # Parse end time
            end_time_str = self.segment_end_input.text()
            end_time = self._parse_time_input(end_time_str)
            
            # Parse RGB values
            r = int(self.segment_r_input.text())
            g = int(self.segment_g_input.text())
            b = int(self.segment_b_input.text())
            
            # Validate times
            if start_time >= end_time:
                self.logger.warning("Start time must be less than end time")
                # Reset to original values
                self.show_segment_editor(self.segment_editor_timeline, self.segment_editor_segment)
                return
            
            # Validate RGB values
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # Update segment
            self.app.timeline_manager.modify_segment(
                timeline=self.segment_editor_timeline,
                segment=self.segment_editor_segment,
                start_time=start_time,
                end_time=end_time,
                color=(r, g, b)
            )
        except Exception as e:
            self.logger.error(f"Error applying segment changes: {e}")
            # Reset to original values
            self.show_segment_editor(self.segment_editor_timeline, self.segment_editor_segment)
    
    def _parse_time_input(self, time_str):
        """
        Parse a time string in the format MM:SS.SS or HH:MM:SS.SS.
        
        Args:
            time_str (str): Time string to parse.
        
        Returns:
            float: Time in seconds.
        """
        parts = time_str.split(':')
        
        if len(parts) == 2:
            # MM:SS.SS format
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        elif len(parts) == 3:
            # HH:MM:SS.SS format
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        else:
            raise ValueError(f"Invalid time format: {time_str}")
    
    def _on_apply_sequence_length(self):
        """Handle Apply button click for sequence length."""
        """Handle Apply button click for sequence length."""
        if not self.app.project_manager.current_project:
            return
        
        try:
            # Get the time value from the input field in HH:MM:SS format
            time_text = self.length_input.text()
            
            # Parse the time components
            hours, minutes, seconds = map(int, time_text.split(':'))
            
            # Convert to seconds
            new_length = hours * 3600 + minutes * 60 + seconds
            
            # Get the current sequence length
            current_length = self.app.project_manager.current_project.total_duration
            
            # Check if the new length is shorter than the current length
            if new_length < current_length:
                # Show warning message
                response = QMessageBox.warning(
                    self,
                    "Shorten Sequence",
                    f"Shortening the sequence from {self._format_seconds_to_hms(current_length)} to {time_text} "
                    f"will remove all segments after {time_text}. This cannot be undone.\n\n"
                    f"Do you want to continue?",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Cancel
                )
                
                if response == QMessageBox.StandardButton.Cancel:
                    # User cancelled, reset the input field
                    self._format_length_input(current_length)
                    return
                
                # User confirmed, remove segments after the new length
                self._remove_segments_after(new_length)
            
            # Update the project's total duration
            self.app.project_manager.current_project.total_duration = new_length
            
            # Mark project as changed
            self.app.project_manager.project_changed.emit()
            
            # Update the timeline view to show the new end marker
            self.timeline_widget.timeline_container.update()
            
            # Show status message
            self.statusbar.showMessage(f"Sequence length updated to {time_text}", 5000)
            
        except (ValueError, AttributeError) as e:
            # If the input is not valid, reset to current length
            self.logger.error(f"Invalid length input: {e}")
            if self.app.project_manager.current_project:
                self._format_length_input(self.app.project_manager.current_project.total_duration)
    
    def _remove_segments_after(self, time):
        """
        Remove all segments that extend beyond the specified time.
        
        Args:
            time (float): Time in seconds.
        """
        if not self.app.project_manager.current_project:
            return
        
        # Save state for undo
        if self.app.undo_manager:
            self.app.undo_manager.save_state("shorten_sequence")
        
        # Process each timeline
        for timeline in self.app.project_manager.current_project.timelines:
            # Find segments that start after the specified time
            segments_to_remove = [segment for segment in timeline.segments if segment.start_time >= time]
            
            # Remove these segments
            for segment in segments_to_remove:
                timeline.remove_segment(segment)
            
            # Find segments that extend beyond the specified time
            segments_to_modify = [segment for segment in timeline.segments if segment.start_time < time < segment.end_time]
            
            # Truncate these segments
            for segment in segments_to_modify:
                segment.end_time = time
    
    def _format_seconds_to_hms(self, seconds, include_hundredths=False, hide_hours_if_zero=False):
        """
        Format time in seconds as HH:MM:SS or MM:SS.SS.
        
        Args:
            seconds (float): Time in seconds.
            include_hundredths (bool): Whether to include hundredths of a second.
            hide_hours_if_zero (bool): Whether to hide hours if they are zero.
            
        Returns:
            str: Formatted time string.
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        
        if include_hundredths:
            # Format with hundredths of a second
            if hide_hours_if_zero and hours == 0:
                # Format as MM:SS.SS
                return f"{minutes:02d}:{secs:05.2f}"
            else:
                # Format as HH:MM:SS.SS
                return f"{hours:02d}:{minutes:02d}:{secs:05.2f}"
        else:
            # Format without hundredths (original format)
            secs_int = int(secs)
            if hide_hours_if_zero and hours == 0:
                # Format as MM:SS
                return f"{minutes:02d}:{secs_int:02d}"
            else:
                # Format as HH:MM:SS
                return f"{hours:02d}:{minutes:02d}:{secs_int:02d}"
    
    def _format_length_input(self, seconds):
        """Format time in seconds as HH:MM:SS and update the length input field."""
        formatted_time = self._format_seconds_to_hms(seconds)
        self.length_input.setText(formatted_time)
    
    def _on_project_loaded(self, project):
        """Handle project loaded signal."""
        # Update window title (no star since it was just loaded)
        self._update_window_title()
        
        # Update status bar
        self.statusbar.showMessage(f"Loaded project: {project.name}", 5000)
        
        # Update recent projects menu
        self._update_recent_projects_menu()
        
        # Update sequence length input
        self._format_length_input(project.total_duration)
        
        # Select the first timeline (Ball 1) if available
        if project.timelines and len(project.timelines) > 0:
            self.logger.debug(f"Selecting first timeline: {project.timelines[0].name}")
            self.timeline_widget.select_timeline(project.timelines[0])
            
            # Ensure the timeline widget has focus, not the time input field
        
        # Load audio from project if available
        if project.audio_data:
            self.logger.debug("Loading audio from project")
            self.app.audio_manager.load_audio_from_project(project)
        
        # Set the zoom level from the project
        self.logger.debug(f"Setting zoom level from project: {project.zoom_level}")
        self.timeline_widget.set_zoom(project.zoom_level)
    
    def _on_project_saved(self, file_path):
        """Handle project saved signal."""
        # Save the current zoom level to the project
        if self.app.project_manager.current_project:
            self.logger.debug(f"Saving zoom level to project: {self.timeline_widget.zoom_level}")
            self.app.project_manager.current_project.zoom_level = self.timeline_widget.zoom_level
        
        # Update window title (no star since it was just saved)
        self._update_window_title()
        
        # Update status bar
        self.statusbar.showMessage(f"Saved project to: {file_path}", 5000)
        
        # Update recent projects menu
        self._update_recent_projects_menu()
    
    def _update_recent_projects_menu(self):
        """Update the recent projects menu with the latest projects."""
        # Clear existing actions
        self.recent_projects_menu.clear()
        
        # Get recent projects from config
        recent_projects = self.app.config.get("general", "recent_projects")
        
        if not recent_projects:
            # Add a disabled action if no recent projects
            no_projects_action = self.recent_projects_menu.addAction("No Recent Projects")
            no_projects_action.setEnabled(False)
            return
        
        # Add an action for each recent project
        for i, project_path in enumerate(recent_projects):
            # Create a shorter display name
            display_name = os.path.basename(project_path)
            
            # Create action
            action = self.recent_projects_menu.addAction(f"{i+1}. {display_name}")
            action.setData(project_path)
            action.triggered.connect(lambda checked, p=project_path: self._open_recent_project(p))
        
        # Add separator and clear action
        self.recent_projects_menu.addSeparator()
        clear_action = self.recent_projects_menu.addAction("Clear Recent Projects")
        clear_action.triggered.connect(self._clear_recent_projects)
    
    def _open_recent_project(self, project_path):
        """Open a project from the recent projects list."""
        # Check if file exists and is valid
        if not project_path or project_path == "False" or not os.path.exists(project_path):
            # Show error message
            QMessageBox.warning(
                self,
                "File Not Found",
                f"The project file could not be found or is invalid:\n{project_path}"
            )
            
            # Remove from recent projects
            recent_projects = self.app.config.get("general", "recent_projects")
            if project_path in recent_projects:
                recent_projects.remove(project_path)
                self.app.config.set("general", "recent_projects", recent_projects)
                self.app.config.save()
                self._update_recent_projects_menu()
            
            return
        
        # Check for unsaved changes
        if not self._check_unsaved_changes():
            return
        
        # Load project
        self.logger.debug(f"Opening recent project: {project_path}")
        self.app.project_manager.load_project(project_path)
    
    def _clear_recent_projects(self):
        """Clear the recent projects list."""
        # Clear recent projects in config
        self.app.config.set("general", "recent_projects", [])
        self.app.config.save()
        
        # Update menu
        self._update_recent_projects_menu()
    
    def _on_project_changed(self):
        """Handle project changed signal."""
        # Update window title to show unsaved changes
        self._update_window_title()
        
        # Update status bar with a brief message
        self.statusbar.showMessage("Project modified", 2000)
    
    def _update_window_title(self):
        """Update the window title, adding a star if there are unsaved changes."""
        if not self.app.project_manager.current_project:
            self.setWindowTitle("Sequence Maker")
            return
        
        # Get the project name and file path
        project = self.app.project_manager.current_project
        
        # Use the filename from the file_path if available, otherwise use project name
        if project.file_path:
            file_name = os.path.basename(project.file_path)
            # Remove the extension if present
            if file_name.endswith(PROJECT_FILE_EXTENSION):
                file_name = file_name[:-len(PROJECT_FILE_EXTENSION)]
        else:
            file_name = project.name
        
        # Add a star if there are unsaved changes
        unsaved_indicator = "*" if self.app.project_manager.has_unsaved_changes else ""
        
        # Set the window title to "file_name* - Sequence Maker" with optional asterisk
        self.setWindowTitle(f"{file_name}{unsaved_indicator} - Sequence Maker")
    
    def _update_undo_actions(self):
        """Update undo/redo actions based on undo manager state."""
        self.undo_action.setEnabled(self.app.undo_manager.can_undo())
        self.redo_action.setEnabled(self.app.undo_manager.can_redo())
        
        # Update tooltips with action types
        if self.app.undo_manager.can_undo():
            action_type = self.app.undo_manager.get_undo_action_type()
            self.undo_action.setStatusTip(f"Undo {action_type}")
        else:
            self.undo_action.setStatusTip("Undo the last action")
        
        if self.app.undo_manager.can_redo():
            action_type = self.app.undo_manager.get_redo_action_type()
            self.redo_action.setStatusTip(f"Redo {action_type}")
        else:
            self.redo_action.setStatusTip("Redo the last undone action")
    
    def _check_unsaved_changes(self):
        """
        Check if there are unsaved changes and prompt the user to save if needed.
        
        Returns:
            bool: True if the operation should proceed, False if it should be cancelled.
        """
        # If no project or no unsaved changes, proceed
        if not self.app.project_manager.current_project or not self.app.project_manager.has_unsaved_changes:
            return True
        
        # Ask user if they want to save changes
        response = QMessageBox.question(
            self,
            "Save Changes",
            "The current project has unsaved changes. Do you want to save them?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )
        
        if response == QMessageBox.StandardButton.Cancel:
            # User cancelled, don't proceed
            return False
        
        if response == QMessageBox.StandardButton.Save:
            # User wants to save
            if not self.app.project_manager.current_project.file_path:
                # Project has never been saved, show Save As dialog
                return self._on_save_as()
            else:
                # Project has been saved before, use existing path
                return self.app.project_manager.save_project()
        
        # User chose to discard changes, proceed
        return True
    
    def keyPressEvent(self, event):
        """
        Handle key press events.
        
        This method handles key presses for adding color blocks to timelines.
        When a mapped key is pressed, it creates a new color block on the
        appropriate timeline, extending from the current marker to the next
        color block or the end of the timeline.
        
        Args:
            event: Key press event.
        """
        # Get the key text
        key_text = event.text().lower()
        
        # Log the current position
        self.logger.debug(f"Current position in TimelineManager: {self.app.timeline_manager.position}")
        self.logger.debug(f"Current position in TimelineWidget: {self.timeline_widget.position}")
        
        # Check if we have a project and key mappings
        if not self.app.project_manager.current_project:
            # Pass event to parent
            super().keyPressEvent(event)
            return
        
        # Get key mapping from the project
        key_mapping = None
        for mapping_name, mapping in self.app.project_manager.current_project.key_mappings.items():
            if mapping_name == "default":
                from models.key_mapping import KeyMapping
                key_mapping = KeyMapping.from_dict(mapping)
                break
        
        # If no key mapping found, use default
        if not key_mapping:
            from models.key_mapping import KeyMapping
            key_mapping = KeyMapping.create_default()
        
        # Check if the key is mapped
        mapping = key_mapping.get_mapping(key_text)
        if mapping:
            # Get color and timelines
            color = mapping["color"]
            timeline_indices = mapping["timelines"]
            
            # Get the current position from the timeline widget
            position = self.timeline_widget.position
            
            # Update the position in the timeline manager
            self.app.timeline_manager.set_position(position)
            
            # Add color at current position for each timeline
            for timeline_index in timeline_indices:
                # Get the timeline
                timeline = self.app.timeline_manager.get_timeline(timeline_index)
                if timeline:
                    # Use the timeline manager's add_color_at_position method instead of calling add_color_at_time directly
                    # This ensures proper handling of the position and color
                    segment = self.app.timeline_manager.add_color_at_position(timeline_index, color)
            
            # Update status bar
            color_name = self._get_color_name(color)
            self.statusbar.showMessage(f"Added {color_name} at position {position:.2f}s", 3000)
            
            # Event handled
            event.accept()
            return
        
        # Pass event to parent
        super().keyPressEvent(event)
    
    def _get_color_name(self, color):
        """
        Get the name of a color.
        
        Args:
            color: RGB color tuple.
        
        Returns:
            str: Color name.
        """
        # Define common colors
        common_colors = {
            (255, 0, 0): "Red",
            (255, 165, 0): "Orange",
            (255, 255, 0): "Yellow",
            (0, 255, 0): "Green",
            (0, 255, 255): "Cyan",
            (0, 0, 255): "Blue",
            (255, 0, 255): "Pink",
            (255, 255, 255): "White",
            (0, 0, 0): "Black"
        }
        
        # Check if color is a common color
        for common_color, name in common_colors.items():
            if color == common_color:
                return name
        
        # Return RGB values
        return f"RGB({color[0]}, {color[1]}, {color[2]})"
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Check for unsaved changes
        if self._check_unsaved_changes():
            # Save window state
            self._save_window_state()
            
            # Accept the event
            event.accept()
        else:
            # Reject the event
            event.ignore()