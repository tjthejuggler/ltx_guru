"""
Sequence Maker - Integration Tests for Timeline Functionality

This module contains integration tests for timeline functionality in the Sequence Maker application.
"""

import pytest
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QKeyEvent
from unittest.mock import MagicMock, patch


def test_add_color_segment_via_keypress(qtbot, app_fixture, main_window_fixture):
    """
    Test adding a color segment using keypress simulation.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        main_window_fixture: The main_window_fixture fixture
    """
    # Get the timeline manager and the first timeline
    timeline_manager = app_fixture.timeline_manager
    timeline_index = 0
    
    # Ensure we have at least one timeline
    if len(timeline_manager.timelines) == 0:
        timeline_manager.add_timeline()
    
    # Get the initial segment count
    timeline = timeline_manager.get_timeline(timeline_index)
    initial_segment_count = len(timeline.segments)
    
    # Set up key mapping for red color (assuming 'r' is mapped to red)
    # In a real application, this would be loaded from configuration
    app_fixture.project_manager.current_project.key_mappings = {
        'r': {'color': [255, 0, 0], 'name': 'Red'}
    }
    
    # Create a key event for the 'r' key
    key_event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_R, Qt.KeyboardModifier.NoModifier, 'r')
    
    # Send the key event to the main window
    main_window_fixture.keyPressEvent(key_event)
    
    # Get the updated timeline
    timeline = timeline_manager.get_timeline(timeline_index)
    
    # Check that a new segment was added
    assert len(timeline.segments) == initial_segment_count + 1
    
    # Check that the new segment has the correct color
    assert timeline.segments[-1].color == (255, 0, 0)


def test_timeline_segment_selection(qtbot, app_fixture, timeline_widget_fixture):
    """
    Test selecting a segment in the timeline.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        timeline_widget_fixture: The timeline_widget_fixture fixture
    """
    # Get the timeline manager and the first timeline
    timeline_manager = app_fixture.timeline_manager
    timeline_index = 0
    
    # Ensure we have at least one timeline
    if len(timeline_manager.timelines) == 0:
        timeline_manager.add_timeline()
    
    # Add a segment to the timeline
    timeline = timeline_manager.get_timeline(timeline_index)
    timeline_manager.add_segment(timeline_index, 0.0, 1.0, (255, 0, 0))
    
    # Mock the timeline widget's mapFromGlobal method to return a point within the segment
    with patch.object(timeline_widget_fixture, 'mapFromGlobal', return_value=QPoint(100, 50)):
        # Simulate a mouse click on the segment
        qtbot.mouseClick(timeline_widget_fixture, Qt.MouseButton.LeftButton, pos=QPoint(100, 50))
    
    # Check that the segment was selected
    assert timeline_widget_fixture.selected_segment is not None
    assert timeline_widget_fixture.selected_segment.color == (255, 0, 0)


def test_timeline_segment_deletion(qtbot, app_fixture, main_window_fixture):
    """
    Test deleting a segment from the timeline.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        main_window_fixture: The main_window_fixture fixture
    """
    # Get the timeline manager and the first timeline
    timeline_manager = app_fixture.timeline_manager
    timeline_index = 0
    
    # Ensure we have at least one timeline
    if len(timeline_manager.timelines) == 0:
        timeline_manager.add_timeline()
    
    # Add a segment to the timeline
    timeline = timeline_manager.get_timeline(timeline_index)
    timeline_manager.add_segment(timeline_index, 0.0, 1.0, (255, 0, 0))
    
    # Get the initial segment count
    initial_segment_count = len(timeline.segments)
    
    # Select the segment (mock the selection)
    main_window_fixture.timeline_widget.selected_segment = timeline.segments[0]
    main_window_fixture.timeline_widget.selected_timeline = timeline
    
    # Trigger the delete action
    main_window_fixture.delete_action.trigger()
    
    # Check that the segment was deleted
    assert len(timeline.segments) == initial_segment_count - 1


def test_timeline_segment_editing(qtbot, app_fixture, main_window_fixture):
    """
    Test editing a segment in the timeline.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        main_window_fixture: The main_window_fixture fixture
    """
    # Get the timeline manager and the first timeline
    timeline_manager = app_fixture.timeline_manager
    timeline_index = 0
    
    # Ensure we have at least one timeline
    if len(timeline_manager.timelines) == 0:
        timeline_manager.add_timeline()
    
    # Add a segment to the timeline
    timeline = timeline_manager.get_timeline(timeline_index)
    timeline_manager.add_segment(timeline_index, 0.0, 1.0, (255, 0, 0))
    
    # Show the segment editor for the segment
    main_window_fixture.show_segment_editor(timeline, timeline.segments[0])
    
    # Set new values in the segment editor
    main_window_fixture.segment_start_input.setText("00:00.50")
    main_window_fixture.segment_end_input.setText("00:01.50")
    main_window_fixture.segment_r_input.setText("0")
    main_window_fixture.segment_g_input.setText("255")
    main_window_fixture.segment_b_input.setText("0")
    
    # Apply the changes
    main_window_fixture._on_apply_segment_changes()
    
    # Check that the segment was updated
    assert timeline.segments[0].start_time == 0.5
    assert timeline.segments[0].end_time == 1.5
    assert timeline.segments[0].color == (0, 255, 0)


def test_timeline_zooming(qtbot, app_fixture, main_window_fixture):
    """
    Test zooming in and out on the timeline.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        main_window_fixture: The main_window_fixture fixture
    """
    # Get the initial zoom level
    initial_zoom = main_window_fixture.timeline_widget.zoom_level
    
    # Trigger zoom in action
    main_window_fixture.zoom_in_action.trigger()
    
    # Check that the zoom level increased
    assert main_window_fixture.timeline_widget.zoom_level > initial_zoom
    
    # Trigger zoom out action
    main_window_fixture.zoom_out_action.trigger()
    
    # Check that the zoom level decreased back to the initial level
    assert main_window_fixture.timeline_widget.zoom_level == initial_zoom


def test_add_and_remove_timeline(qtbot, app_fixture, main_window_fixture):
    """
    Test adding and removing timelines.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        main_window_fixture: The main_window_fixture fixture
    """
    # Get the initial timeline count
    initial_count = len(app_fixture.timeline_manager.timelines)
    
    # Trigger add timeline action
    main_window_fixture.add_timeline_action.trigger()
    
    # Check that a new timeline was added
    assert len(app_fixture.timeline_manager.timelines) == initial_count + 1
    
    # Select the new timeline
    main_window_fixture.timeline_widget.selected_timeline_index = initial_count
    
    # Trigger remove timeline action
    main_window_fixture.remove_timeline_action.trigger()
    
    # Check that the timeline was removed
    assert len(app_fixture.timeline_manager.timelines) == initial_count