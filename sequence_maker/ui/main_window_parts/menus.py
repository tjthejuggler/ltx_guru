"""
Sequence Maker - Main Window Menus

This module contains functions for creating and managing menus in the main window.
"""

from PyQt6.QtWidgets import QLabel, QLineEdit
from PyQt6.QtCore import Qt


class _PositionLineEdit(QLineEdit):
    """QLineEdit that passes arrow-key events up to the parent window."""

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            # Let the main window handle scrubbing
            self.clearFocus()
            parent = self.window()
            if parent:
                parent.keyPressEvent(event)
        else:
            super().keyPressEvent(event)


def create_menus(main_window):
    """Create all menus for the main window."""
    create_file_menu(main_window)
    create_edit_menu(main_window)
    create_view_menu(main_window)
    create_timeline_menu(main_window)
    create_playback_menu(main_window)
    create_tools_menu(main_window)
    create_help_menu(main_window)


def create_file_menu(main_window):
    """Create the file menu."""
    main_window.file_menu = main_window.menuBar().addMenu("&File")
    main_window.file_menu.addAction(main_window.new_action)
    main_window.file_menu.addAction(main_window.open_action)
    main_window.file_menu.addAction(main_window.save_action)
    main_window.file_menu.addAction(main_window.save_as_action)
    main_window.file_menu.addSeparator()
    # Import submenu
    main_window.import_menu = main_window.file_menu.addMenu("Import")
    main_window.import_menu.addAction(main_window.import_ball_sequence_action)
    main_window.import_menu.addAction(main_window.import_lyrics_timestamps_action)
    
    # Export submenu
    main_window.export_menu = main_window.file_menu.addMenu("Export")
    main_window.export_menu.addAction(main_window.export_json_action)
    main_window.export_menu.addAction(main_window.export_prg_action)
    main_window.export_menu.addAction(main_window.export_ball_sequence_action)
    main_window.export_menu.addSeparator()
    main_window.export_menu.addAction(main_window.export_buddy_action)
    
    
    # Ball IP configuration
    main_window.file_menu.addSeparator()
    main_window.file_menu.addAction(main_window.ball_ips_action)

    # Recent files submenu
    main_window.recent_files_menu = main_window.file_menu.addMenu("Recent Files")
    main_window._update_recent_files_menu()
    
    main_window.file_menu.addSeparator()
    main_window.file_menu.addAction(main_window.exit_action)


def create_edit_menu(main_window):
    """Create the edit menu."""
    main_window.edit_menu = main_window.menuBar().addMenu("&Edit")
    main_window.edit_menu.addAction(main_window.undo_action)
    main_window.edit_menu.addAction(main_window.redo_action)
    main_window.edit_menu.addSeparator()
    main_window.edit_menu.addAction(main_window.cut_action)
    main_window.edit_menu.addAction(main_window.copy_action)
    main_window.edit_menu.addAction(main_window.paste_action)
    main_window.edit_menu.addAction(main_window.delete_action)
    main_window.edit_menu.addAction(main_window.select_all_action)
    main_window.edit_menu.addSeparator()
    main_window.edit_menu.addAction(main_window.preferences_action)


def create_view_menu(main_window):
    """Create the view menu."""
    main_window.view_menu = main_window.menuBar().addMenu("&View")
    main_window.view_menu.addAction(main_window.zoom_in_action)
    main_window.view_menu.addAction(main_window.zoom_out_action)
    main_window.view_menu.addAction(main_window.zoom_fit_action)
    main_window.view_menu.addSeparator()
    main_window.view_menu.addAction(main_window.toggle_ball_view_action)
    main_window.view_menu.addAction(main_window.toggle_audio_view_action)
    main_window.view_menu.addAction(main_window.toggle_lyrics_view_action)


def create_timeline_menu(main_window):
    """Create the timeline menu."""
    main_window.timeline_menu = main_window.menuBar().addMenu("&Timeline")
    main_window.timeline_menu.addAction(main_window.edit_segment_action)
    main_window.timeline_menu.addAction(main_window.delete_segment_action)
    main_window.timeline_menu.addSeparator()
    main_window.timeline_menu.addAction(main_window.split_segment_action)
    main_window.timeline_menu.addAction(main_window.merge_segments_action)
    main_window.timeline_menu.addSeparator()
    main_window.timeline_menu.addAction(main_window.clear_timeline_action)
    main_window.timeline_menu.addSeparator()
    main_window.timeline_menu.addAction(main_window.view_jsons_action)


def create_playback_menu(main_window):
    """Create the playback menu."""
    main_window.playback_menu = main_window.menuBar().addMenu("&Playback")
    main_window.playback_menu.addAction(main_window.play_action)
    main_window.playback_menu.addAction(main_window.pause_action)
    main_window.playback_menu.addAction(main_window.stop_action)
    main_window.playback_menu.addSeparator()
    main_window.playback_menu.addAction(main_window.loop_action)


def create_tools_menu(main_window):
    """Create the tools menu."""
    main_window.tools_menu = main_window.menuBar().addMenu("&Tools")
    main_window.tools_menu.addAction(main_window.key_mapping_action)
    
    # Audio tools section
    main_window.tools_menu.addSeparator()
    main_window.tools_menu.addAction(main_window.crop_audio_action)
    
    # Version history
    main_window.tools_menu.addSeparator()
    main_window.tools_menu.addAction(main_window.version_history_action)


def create_help_menu(main_window):
    """Create the help menu."""
    main_window.help_menu = main_window.menuBar().addMenu("&Help")
    main_window.help_menu.addAction(main_window.about_action)


def create_toolbars(main_window):
    """Create toolbars for the main window."""
    # File toolbar
    main_window.file_toolbar = main_window.addToolBar("File")
    main_window.file_toolbar.setObjectName("FileToolbar")
    main_window.file_toolbar.addAction(main_window.new_action)
    main_window.file_toolbar.addAction(main_window.open_action)
    main_window.file_toolbar.addAction(main_window.save_action)
    
    # Edit toolbar
    main_window.edit_toolbar = main_window.addToolBar("Edit")
    main_window.edit_toolbar.setObjectName("EditToolbar")
    main_window.edit_toolbar.addAction(main_window.undo_action)
    main_window.edit_toolbar.addAction(main_window.redo_action)
    
    # Timeline toolbar
    main_window.timeline_toolbar = main_window.addToolBar("Timeline")
    main_window.timeline_toolbar.setObjectName("TimelineToolbar")
    main_window.timeline_toolbar.addAction(main_window.edit_segment_action)
    main_window.timeline_toolbar.addAction(main_window.delete_segment_action)
    
    # Playback toolbar
    main_window.playback_toolbar = main_window.addToolBar("Playback")
    main_window.playback_toolbar.setObjectName("PlaybackToolbar")
    main_window.playback_toolbar.addAction(main_window.play_action)
    main_window.playback_toolbar.addAction(main_window.pause_action)
    main_window.playback_toolbar.addAction(main_window.stop_action)
    main_window.playback_toolbar.addAction(main_window.loop_action)
    
    # Notes toolbar
    main_window.notes_toolbar = main_window.addToolBar("Notes")
    main_window.notes_toolbar.setObjectName("NotesToolbar")
    main_window.notes_toolbar.addAction(main_window.show_notes_action)


def create_statusbar(main_window):
    """Create the status bar for the main window."""
    main_window.statusbar = main_window.statusBar()
    
    # Add project status label (empty by default)
    main_window.project_status_label = QLabel("")
    main_window.statusbar.addWidget(main_window.project_status_label)
    
    # Add sequence description label (shows description from Sequence Designer)
    main_window.sequence_description_label = QLabel("")
    main_window.sequence_description_label.setVisible(False)
    main_window.sequence_description_label.setStyleSheet(
        "QLabel { color: #2196F3; font-style: italic; padding: 0 8px; }"
    )
    main_window.sequence_description_label.setToolTip(
        "Description of the current sequence from Sequence Designer"
    )
    main_window.statusbar.addWidget(main_window.sequence_description_label)
    
    # Add hover info label for segment information
    main_window.hover_info_label = QLabel("")
    main_window.hover_info_label.setVisible(False)
    main_window.statusbar.addWidget(main_window.hover_info_label)
    
    # Add cursor hover position label (shows time when hovering over timelines)
    main_window.cursor_hover_label = QLabel("Cursor: --:--.--)")
    main_window.statusbar.addPermanentWidget(main_window.cursor_hover_label)
    
    # Editable position field — user can type a time and press Enter to seek
    main_window.cursor_position_label = _PositionLineEdit("00:00.00")
    main_window.cursor_position_label.setFixedWidth(90)
    main_window.cursor_position_label.setToolTip(
        "Current position. Type a time (MM:SS.hh) and press Enter to seek."
    )
    main_window.cursor_position_label.returnPressed.connect(
        main_window._on_position_edit_committed
    )
    main_window.statusbar.addPermanentWidget(main_window.cursor_position_label)