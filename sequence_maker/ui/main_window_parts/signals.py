"""
Sequence Maker - Main Window Signals

This module contains functions for connecting signals in the main window.
"""


def connect_signals(main_window):
    """Connect all signals for the main window."""
    connect_timeline_signals(main_window)
    connect_audio_signals(main_window)
    connect_project_signals(main_window)
    connect_llm_signals(main_window)
    connect_editor_signals(main_window)


def connect_timeline_signals(main_window):
    """Connect timeline-related signals."""
    # Connect timeline signals
    main_window.timeline_widget.position_changed.connect(main_window._update_cursor_position)
    main_window.timeline_widget.horizontal_scroll_changed.connect(main_window.audio_widget.set_horizontal_scroll_offset)
    
    # Note: The TimelineWidget doesn't have cursor_hover_position_changed or cursor_hover_exited signals
    # We'll need to implement these in the TimelineWidget class if needed
    # For now, we'll comment these out to avoid errors
    # main_window.timeline_widget.cursor_hover_position_changed.connect(main_window.update_cursor_hover_position)
    # main_window.timeline_widget.cursor_hover_exited.connect(main_window.clear_cursor_hover_position)


def connect_audio_signals(main_window):
    """Connect audio-related signals."""
    # Connect audio signals if audio manager is available
    if hasattr(main_window.app, 'audio_manager'):
        main_window.app.audio_manager.audio_started.connect(main_window._on_playback_started)
        main_window.app.audio_manager.audio_paused.connect(main_window._on_playback_paused)
        main_window.app.audio_manager.audio_stopped.connect(main_window._on_playback_stopped)


def connect_project_signals(main_window):
    """Connect project-related signals."""
    # Connect project signals
    main_window.app.project_manager.project_loaded.connect(main_window._update_ui)
    main_window.app.project_manager.project_saved.connect(main_window._update_ui)
    main_window.app.project_manager.project_changed.connect(main_window._update_ui)
    
    # Connect undo/redo signals
    main_window.app.undo_manager.undo_stack_changed.connect(main_window._update_ui)
    main_window.app.undo_manager.redo_stack_changed.connect(main_window._update_ui)


def connect_llm_signals(main_window):
    """Connect LLM-related signals."""
    # Connect LLM signals if LLM manager is available
    if hasattr(main_window.app, 'llm_manager'):
        main_window.app.llm_manager.llm_action_requested.connect(main_window._on_llm_action)


def connect_editor_signals(main_window):
    """Connect editor-related signals."""
    # Connect segment editor signals
    main_window.segment_apply_button.clicked.connect(main_window._on_segment_apply)
    main_window.segment_cancel_button.clicked.connect(main_window._on_segment_cancel)
    
    # Connect boundary editor signals
    main_window.boundary_apply_button.clicked.connect(main_window._on_boundary_time_apply)
    main_window.boundary_cancel_button.clicked.connect(main_window._on_editor_cancel)
    
    # Connect timeline selection signals
    main_window.timeline_widget.selection_changed.connect(main_window._on_timeline_selection_changed)
    
    # Connect key press signals for segment editor
    main_window.segment_start_edit.returnPressed.connect(main_window._on_editor_apply)
    main_window.segment_end_edit.returnPressed.connect(main_window._on_editor_apply)
    main_window.segment_color_edit.returnPressed.connect(main_window._on_editor_apply)
    
    # Connect key press signals for boundary editor
    main_window.boundary_time_edit.returnPressed.connect(main_window._on_editor_apply)