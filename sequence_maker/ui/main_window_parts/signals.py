"""
Sequence Maker - Main Window Signals

This module contains functions for connecting signals in the main window.
"""


def connect_signals(main_window):
    """Connect all signals for the main window."""
    connect_timeline_signals(main_window)
    connect_audio_signals(main_window)
    connect_project_signals(main_window)
    connect_editor_signals(main_window)


def connect_timeline_signals(main_window):
    """Connect timeline-related signals."""
    # Connect timeline signals
    main_window.timeline_widget.position_changed.connect(main_window._update_cursor_position)
    main_window.timeline_widget.horizontal_scroll_changed.connect(main_window.audio_widget.set_horizontal_scroll_offset)
    
    # Connect zoom changes so lyrics timeline repaints with correct scale
    main_window.audio_widget.connect_zoom_signal()
    
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

        # 2026-05-06: song name and position labels were moved out of
        # AudioWidget onto the main toolbar. Hook them up here so they keep
        # tracking audio state.
        main_window.app.audio_manager.audio_loaded.connect(
            main_window._on_toolbar_audio_loaded
        )
        main_window.app.audio_manager.audio_stopped.connect(
            main_window._on_toolbar_audio_stopped
        )
        main_window.app.audio_manager.position_changed.connect(
            main_window._on_toolbar_position_changed
        )
        # Also follow the timeline manager's position so the label keeps in
        # sync when the user scrubs by clicking on the timeline.
        if hasattr(main_window.app, 'timeline_manager'):
            main_window.app.timeline_manager.position_changed.connect(
                main_window._on_toolbar_position_changed
            )


def connect_project_signals(main_window):
    """Connect project-related signals."""
    # Connect project signals
    main_window.app.project_manager.project_loaded.connect(main_window._update_ui)
    main_window.app.project_manager.project_saved.connect(main_window._update_ui)
    main_window.app.project_manager.project_changed.connect(main_window._update_ui)
    
    # Connect undo/redo signals
    main_window.app.undo_manager.undo_stack_changed.connect(main_window._update_ui)
    main_window.app.undo_manager.redo_stack_changed.connect(main_window._update_ui)
    
    # Connect snippet signals
    # NOTE: Snippets are persisted *globally* in ~/.sequence_maker/snippets.json
    # (loaded on SnippetManager construction), NOT per-project. We deliberately
    # do NOT call snippet_widget.load_snippets() on project_loaded, because that
    # method clears the snippet list and replaces it with the project's snippets
    # field — which would wipe the user's persistent snippets every time a
    # project is opened (including on startup when the last project auto-loads).
    # We only refresh the snippet widget UI so it picks up any project-specific
    # context (e.g. ball count for the per-snippet checkboxes).
    if hasattr(main_window.app, 'snippet_manager') and hasattr(main_window, 'snippet_widget'):
        def _refresh_snippet_widget_on_project_loaded(_project):
            sw = main_window.snippet_widget
            sw.current_snippet = None
            if hasattr(sw, '_refresh_combo'):
                sw._refresh_combo()
            if hasattr(sw, '_build_timeline_bars'):
                sw._build_timeline_bars()
            if hasattr(sw, '_update_ui_state'):
                sw._update_ui_state()
        main_window.app.project_manager.project_loaded.connect(
            _refresh_snippet_widget_on_project_loaded
        )
        main_window.app.snippet_manager.snippet_applied.connect(main_window._update_ui)
        main_window.app.snippet_manager.snippet_modified.connect(main_window._update_ui)


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