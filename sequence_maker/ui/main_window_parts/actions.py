"""
Sequence Maker - Main Window Actions

This module contains functions for creating and managing actions in the main window.
"""

from PyQt6.QtGui import QAction, QKeySequence


def create_actions(main_window):
    """Create all actions for the main window."""
    # Initialize action classes
    main_window.file_actions = main_window.file_actions
    main_window.edit_actions = main_window.edit_actions
    main_window.view_actions = main_window.view_actions
    main_window.timeline_actions = main_window.timeline_actions
    main_window.playback_actions = main_window.playback_actions
    main_window.tools_actions = main_window.tools_actions
    
    # Create actions by category
    create_file_actions(main_window)
    create_edit_actions(main_window)
    create_view_actions(main_window)
    create_timeline_actions(main_window)
    create_playback_actions(main_window)
    create_tools_actions(main_window)


def create_file_actions(main_window):
    """Create file-related actions."""
    main_window.new_action = main_window.file_actions.new_action
    main_window.open_action = main_window.file_actions.open_action
    main_window.save_action = main_window.file_actions.save_action
    main_window.save_as_action = main_window.file_actions.save_as_action
    main_window.export_json_action = main_window.file_actions.export_json_action
    main_window.export_prg_action = main_window.file_actions.export_prg_action
    main_window.exit_action = main_window.file_actions.exit_action


def create_edit_actions(main_window):
    """Create edit-related actions."""
    main_window.undo_action = main_window.edit_actions.undo_action
    main_window.redo_action = main_window.edit_actions.redo_action
    main_window.cut_action = main_window.edit_actions.cut_action
    main_window.copy_action = main_window.edit_actions.copy_action
    main_window.paste_action = main_window.edit_actions.paste_action
    main_window.delete_action = main_window.edit_actions.delete_action
    main_window.select_all_action = main_window.edit_actions.select_all_action
    main_window.preferences_action = main_window.edit_actions.preferences_action


def create_view_actions(main_window):
    """Create view-related actions."""
    main_window.zoom_in_action = main_window.view_actions.zoom_in_action
    main_window.zoom_out_action = main_window.view_actions.zoom_out_action
    main_window.zoom_fit_action = main_window.view_actions.zoom_fit_action
    
    # Create toggle view actions
    main_window.toggle_ball_view_action = QAction("Toggle &Ball View", main_window)
    main_window.toggle_ball_view_action.setStatusTip("Toggle ball visualization")
    main_window.toggle_ball_view_action.setCheckable(True)
    main_window.toggle_ball_view_action.setChecked(True)
    main_window.toggle_ball_view_action.triggered.connect(main_window._on_toggle_ball_view)
    
    main_window.toggle_audio_view_action = QAction("Toggle &Audio View", main_window)
    main_window.toggle_audio_view_action.setStatusTip("Toggle audio visualization")
    main_window.toggle_audio_view_action.setCheckable(True)
    main_window.toggle_audio_view_action.setChecked(True)
    main_window.toggle_audio_view_action.triggered.connect(main_window._on_toggle_audio_view)
    
    main_window.toggle_lyrics_view_action = QAction("Toggle &Lyrics View", main_window)
    main_window.toggle_lyrics_view_action.setStatusTip("Toggle lyrics visualization")
    main_window.toggle_lyrics_view_action.setCheckable(True)
    main_window.toggle_lyrics_view_action.setChecked(True)
    main_window.toggle_lyrics_view_action.triggered.connect(main_window._on_toggle_lyrics_view)


def create_timeline_actions(main_window):
    """Create timeline-related actions."""
    # Create segment-related actions
    main_window.add_segment_action = QAction("&Add Segment", main_window)
    main_window.add_segment_action.setStatusTip("Add a new segment")
    main_window.add_segment_action.triggered.connect(main_window._on_add_segment)
    
    main_window.edit_segment_action = QAction("&Edit Segment", main_window)
    main_window.edit_segment_action.setStatusTip("Edit the selected segment")
    main_window.edit_segment_action.triggered.connect(main_window._on_edit_segment)
    
    main_window.delete_segment_action = QAction("&Delete Segment", main_window)
    main_window.delete_segment_action.setStatusTip("Delete the selected segment")
    main_window.delete_segment_action.triggered.connect(main_window._on_delete_segment)
    
    main_window.split_segment_action = QAction("&Split Segment", main_window)
    main_window.split_segment_action.setStatusTip("Split the selected segment")
    main_window.split_segment_action.triggered.connect(main_window._on_split_segment)
    
    main_window.merge_segments_action = QAction("&Merge Segments", main_window)
    main_window.merge_segments_action.setStatusTip("Merge selected segments")
    main_window.merge_segments_action.triggered.connect(main_window._on_merge_segments)
    
    main_window.clear_timeline_action = QAction("&Clear Timeline", main_window)
    main_window.clear_timeline_action.setStatusTip("Clear the timeline")
    main_window.clear_timeline_action.triggered.connect(main_window._on_clear_timeline)


def create_playback_actions(main_window):
    """Create playback-related actions."""
    main_window.play_action = main_window.playback_actions.play_action
    main_window.pause_action = main_window.playback_actions.pause_action
    main_window.stop_action = main_window.playback_actions.stop_action
    
    # Create loop action
    main_window.loop_action = QAction("&Loop", main_window)
    main_window.loop_action.setStatusTip("Toggle audio looping")
    main_window.loop_action.setCheckable(True)
    main_window.loop_action.triggered.connect(main_window._on_loop)


def create_tools_actions(main_window):
    """Create tools-related actions."""
    main_window.key_mapping_action = main_window.tools_actions.key_mapping_action
    main_window.connect_balls_action = main_window.tools_actions.connect_balls_action
    main_window.llm_chat_action = main_window.tools_actions.llm_chat_action
    main_window.llm_diagnostics_action = main_window.tools_actions.llm_diagnostics_action
    
    # Create version history action
    main_window.version_history_action = QAction("&Version History...", main_window)
    main_window.version_history_action.setStatusTip("View and restore previous versions")
    main_window.version_history_action.triggered.connect(main_window._on_version_history)
    
    main_window.about_action = main_window.tools_actions.about_action