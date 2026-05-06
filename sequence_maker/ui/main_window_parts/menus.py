"""
Sequence Maker - Main Window Menus

This module contains functions for creating and managing menus in the main window.

2026-05-06: UI compaction pass.
  * Load Audio moved out of the audio widget into the File menu.
  * New Visualization menu hosts the waveform/spectrum/beats/energy
    selection (previously a combo box on the audio widget).
  * The legacy File / Edit / Timeline toolbars have been removed; only the
    consolidated playback toolbar remains, with song name, position display
    and the three simulated balls all sharing one row.
"""

from PyQt6.QtWidgets import QLabel, QLineEdit, QSizePolicy, QWidget
from PyQt6.QtGui import QActionGroup, QAction
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
    create_visualization_menu(main_window)
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
    # Load Audio (moved here 2026-05-06 from the audio widget)
    main_window.file_menu.addAction(main_window.file_actions.load_audio_action)
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


def create_visualization_menu(main_window):
    """Create the audio visualization menu (added 2026-05-06).

    Houses the waveform / spectrum / beats / energy selection that used to
    live in a combo box on the audio widget. Selecting a mode updates
    ``audio_widget.visualization_type`` and triggers a repaint.
    """
    main_window.visualization_menu = main_window.menuBar().addMenu("&Visualization")

    # Use a checkable QActionGroup so only one mode is active at a time.
    main_window.visualization_action_group = QActionGroup(main_window)
    main_window.visualization_action_group.setExclusive(True)

    main_window.visualization_actions = {}
    for label, key in (
        ("&Waveform", "waveform"),
        ("&Spectrum", "spectrum"),
        ("&Beats", "beats"),
        ("&Energy", "energy"),
    ):
        action = QAction(label, main_window)
        action.setCheckable(True)
        action.setStatusTip(f"Show the {key} visualization")
        if key == "waveform":
            action.setChecked(True)

        # Bind via a default-argument lambda so each action keeps its own key.
        action.triggered.connect(
            lambda checked=False, k=key: _on_visualization_mode_selected(main_window, k)
        )

        main_window.visualization_action_group.addAction(action)
        main_window.visualization_menu.addAction(action)
        main_window.visualization_actions[key] = action


def _on_visualization_mode_selected(main_window, mode_key):
    """Apply a visualization mode to the audio widget."""
    if hasattr(main_window, "audio_widget") and main_window.audio_widget is not None:
        main_window.audio_widget.visualization_type = mode_key
        if hasattr(main_window.audio_widget, "visualization"):
            main_window.audio_widget.visualization.update()


def create_timeline_menu(main_window):
    """Create the timeline menu."""
    main_window.timeline_menu = main_window.menuBar().addMenu("&Timeline")
    main_window.timeline_menu.addAction(main_window.edit_segment_action)
    main_window.timeline_menu.addAction(main_window.delete_segment_action)
    main_window.timeline_menu.addSeparator()
    main_window.timeline_menu.addAction(main_window.split_segment_action)
    main_window.timeline_menu.addAction(main_window.merge_segments_action)
    main_window.timeline_menu.addSeparator()
    main_window.timeline_menu.addAction(main_window.set_max_time_action)
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
    """Create the (single) main toolbar.

    2026-05-06: Major compaction. The previous File / Edit / Timeline /
    Playback / Notes toolbars have been collapsed into a single ``MainToolbar``
    that holds:
      * Play / Pause (Pause is hidden until playback starts), Stop, Loop
      * The song-name / position display (moved out of the audio widget)
      * Notes
      * The three simulated balls, right-aligned (added by
        :func:`ui.main_window_parts.widgets.create_widgets`)
    The redundant File/Edit/Timeline buttons were removed because every one
    of those actions is already reachable through the menu bar and through
    keyboard shortcuts (Ctrl+N/O/S/Z/Y, etc).
    """
    main_window.main_toolbar = main_window.addToolBar("Main")
    main_window.main_toolbar.setObjectName("MainToolbar")
    main_window.main_toolbar.setMovable(False)

    # Playback controls
    main_window.main_toolbar.addAction(main_window.play_action)
    main_window.main_toolbar.addAction(main_window.pause_action)
    main_window.main_toolbar.addAction(main_window.stop_action)
    main_window.main_toolbar.addAction(main_window.loop_action)
    main_window.main_toolbar.addSeparator()

    # Song-name label (formerly AudioWidget.title_label)
    main_window.song_name_label = QLabel("No audio loaded")
    main_window.song_name_label.setStyleSheet(
        "QLabel { padding: 0 8px; font-weight: bold; }"
    )
    main_window.song_name_label.setToolTip("Currently loaded audio file")
    main_window.main_toolbar.addWidget(main_window.song_name_label)

    # Position / duration label (formerly AudioWidget.position_label).
    main_window.toolbar_position_label = QLabel("0:00 / 0:00")
    main_window.toolbar_position_label.setStyleSheet(
        "QLabel { padding: 0 8px; font-family: monospace; }"
    )
    main_window.toolbar_position_label.setToolTip(
        "Playback position / total duration"
    )
    main_window.main_toolbar.addWidget(main_window.toolbar_position_label)

    main_window.main_toolbar.addSeparator()

    # Notes
    main_window.main_toolbar.addAction(main_window.show_notes_action)

    # Stretch + ball widget will be appended in widgets.create_widgets() once
    # the BallWidget has been instantiated. We add a stretch spacer here so
    # everything appended afterwards (the balls) sits flush-right.
    main_window.toolbar_stretch_spacer = QWidget()
    main_window.toolbar_stretch_spacer.setSizePolicy(
        QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
    )
    main_window.main_toolbar.addWidget(main_window.toolbar_stretch_spacer)


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