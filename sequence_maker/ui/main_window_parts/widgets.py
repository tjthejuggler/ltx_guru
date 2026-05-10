"""
Sequence Maker - Main Window Widgets

This module contains functions for creating and managing widgets in the main window.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel,
    QLineEdit, QPushButton, QStackedWidget, QToolButton, QFrame
)
from PyQt6.QtCore import Qt
from utils.ui_utils import get_app_attr
from app.constants import (
    EDITOR_DOCK_HEIGHT, EDITOR_BUTTON_HEIGHT, DEFAULT_SPLITTER_SIZES
)
from ui.timeline_widget import TimelineWidget
from ui.ball_widget import BallWidget
from ui.audio_widget import AudioWidget
from ui.snippet_widget import SnippetWidget


def create_widgets(main_window):
    """Create all widgets for the main window."""
    create_dock_widgets(main_window)  # Create dock widgets first
    create_central_widget(main_window)  # Then create central widget


def create_central_widget(main_window):
    """Create the central widget for the main window."""
    # Create central widget
    main_window.central_widget = QWidget()
    main_window.setCentralWidget(main_window.central_widget)
    
    # Create main layout
    main_window.main_layout = QVBoxLayout(main_window.central_widget)
    main_window.main_layout.setContentsMargins(0, 0, 0, 0)
    main_window.main_layout.setSpacing(0)  # No spacing
    
    # Add editor at the top (always visible)
    main_window.main_layout.addWidget(main_window.editor_dock, 0)  # 0 stretch factor to minimize space
    
    # Create splitter for timeline and ball visualization
    main_window.main_splitter = QSplitter(Qt.Orientation.Vertical)
    main_window.main_layout.addWidget(main_window.main_splitter)
    
    # Create timeline widget
    main_window.timeline_widget = TimelineWidget(main_window.app, main_window)
    main_window.main_splitter.addWidget(main_window.timeline_widget)
    
    # Create ball widget. 2026-05-06: instead of taking up its own pane in the
    # main vertical splitter, the BallWidget now lives on the right-hand side
    # of the main toolbar (created in menus.create_toolbars), saving a chunk
    # of vertical space in the central area.
    main_window.ball_widget = BallWidget(main_window.app, main_window)
    if hasattr(main_window, "main_toolbar"):
        main_window.main_toolbar.addWidget(main_window.ball_widget)
    else:
        # Fallback (shouldn't happen — toolbars are created before widgets)
        main_window.main_splitter.addWidget(main_window.ball_widget)
    
    # Create audio widget (which now includes the lyrics timeline above the
    # audio visualization, so no separate lyrics pane is needed in the splitter)
    main_window.audio_widget = AudioWidget(main_window.app, main_window)
    main_window.main_splitter.addWidget(main_window.audio_widget)
    
    # Create snippet widget
    main_window.snippet_widget = SnippetWidget(main_window.app, main_window)
    main_window.main_splitter.addWidget(main_window.snippet_widget)
    
    # Set initial splitter sizes (add 0 for snippet widget - it starts collapsed)
    sizes = list(DEFAULT_SPLITTER_SIZES)
    sizes.append(0)  # snippet widget (collapsed by default)
    main_window.main_splitter.setSizes(sizes)


def create_dock_widgets(main_window):
    """Create dock widgets for the main window."""
    # Create editor dock widget - always visible, ultra-compact layout
    # This will be used for both segment editing and boundary editing
    main_window.editor_dock = QWidget()
    main_window.editor_dock.setFixedHeight(EDITOR_BUTTON_HEIGHT + 10)  # Reduced height to remove gap
    main_window.editor_layout = QHBoxLayout(main_window.editor_dock)
    main_window.editor_layout.setContentsMargins(5, 0, 5, 0)  # Minimal margins
    main_window.editor_layout.setSpacing(5)  # Minimal spacing
    
    # Create a stacked widget to switch between segment and boundary editing modes
    main_window.editor_stack = QStackedWidget()
    main_window.editor_layout.addWidget(main_window.editor_stack)
    
    # Create segment editor widget
    main_window.segment_editor_widget = QWidget()
    main_window.segment_editor_widget_layout = QHBoxLayout(main_window.segment_editor_widget)
    main_window.segment_editor_widget_layout.setContentsMargins(0, 0, 0, 0)  # No margins
    main_window.segment_editor_widget_layout.setSpacing(5)  # Minimal spacing
    
    # Create segment start time field
    main_window.segment_start_label = QLabel("Start:")
    main_window.segment_editor_widget_layout.addWidget(main_window.segment_start_label)
    
    main_window.segment_start_edit = QLineEdit()
    main_window.segment_start_edit.setMinimumWidth(80)
    main_window.segment_editor_widget_layout.addWidget(main_window.segment_start_edit)
    
    # Create segment end time field
    main_window.segment_end_label = QLabel("End:")
    main_window.segment_editor_widget_layout.addWidget(main_window.segment_end_label)
    
    main_window.segment_end_edit = QLineEdit()
    main_window.segment_end_edit.setMinimumWidth(80)
    main_window.segment_editor_widget_layout.addWidget(main_window.segment_end_edit)
    
    # Create segment color field
    main_window.segment_color_label = QLabel("RGB:")  # Changed from "Color:" to "RGB:"
    main_window.segment_editor_widget_layout.addWidget(main_window.segment_color_label)
    
    main_window.segment_color_edit = QLineEdit()
    main_window.segment_color_edit.setMinimumWidth(120)  # Wider for color values
    main_window.segment_editor_widget_layout.addWidget(main_window.segment_color_edit)
    
    # Create apply and cancel buttons (now next to the input fields)
    main_window.segment_apply_button = QPushButton("Apply")
    main_window.segment_apply_button.setFixedHeight(EDITOR_BUTTON_HEIGHT)
    main_window.segment_editor_widget_layout.addWidget(main_window.segment_apply_button)
    
    main_window.segment_cancel_button = QPushButton("Cancel")
    main_window.segment_cancel_button.setFixedHeight(EDITOR_BUTTON_HEIGHT)
    main_window.segment_editor_widget_layout.addWidget(main_window.segment_cancel_button)
    
    # Add spacer to prevent stretching across the whole width
    main_window.segment_editor_widget_layout.addStretch(1)
    
    # Add segment editor to stack
    main_window.editor_stack.addWidget(main_window.segment_editor_widget)
    
    # Create boundary editor widget
    main_window.boundary_editor_widget = QWidget()
    main_window.boundary_editor_widget_layout = QHBoxLayout(main_window.boundary_editor_widget)
    main_window.boundary_editor_widget_layout.setContentsMargins(0, 0, 0, 0)  # No margins
    main_window.boundary_editor_widget_layout.setSpacing(5)  # Minimal spacing
    
    # Create boundary time field
    main_window.boundary_time_label = QLabel("Time:")
    main_window.boundary_editor_widget_layout.addWidget(main_window.boundary_time_label)
    
    main_window.boundary_time_edit = QLineEdit()
    main_window.boundary_time_edit.setMinimumWidth(120)
    main_window.boundary_editor_widget_layout.addWidget(main_window.boundary_time_edit)
    
    # Create apply and cancel buttons (next to the input field)
    main_window.boundary_apply_button = QPushButton("Apply")
    main_window.boundary_apply_button.setFixedHeight(EDITOR_BUTTON_HEIGHT)
    main_window.boundary_editor_widget_layout.addWidget(main_window.boundary_apply_button)
    
    main_window.boundary_cancel_button = QPushButton("Cancel")
    main_window.boundary_cancel_button.setFixedHeight(EDITOR_BUTTON_HEIGHT)
    main_window.boundary_editor_widget_layout.addWidget(main_window.boundary_cancel_button)
    
    # Add spacer to prevent stretching across the whole width
    main_window.boundary_editor_widget_layout.addStretch(1)
    
    # Add boundary editor to stack
    main_window.editor_stack.addWidget(main_window.boundary_editor_widget)
    
    # Hide the editor by default
    main_window.editor_dock.hide()