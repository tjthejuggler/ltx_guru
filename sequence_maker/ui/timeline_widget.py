"""
Sequence Maker - Timeline Widget

This module defines the TimelineWidget class, which displays and allows editing of timelines.
"""

import logging
import math
from PyQt6.QtWidgets import (
    QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QMenu, QToolBar
)
from PyQt6.QtCore import Qt, QRect, QPoint, QSize, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QLinearGradient, QFont,
    QMouseEvent, QWheelEvent, QKeyEvent, QContextMenuEvent
)

from app.constants import TIMELINE_HEIGHT, TIMELINE_SEGMENT_MIN_WIDTH, ZOOM_STEP, MAX_ZOOM, MIN_ZOOM


class TimelineWidget(QWidget):
    """
    Widget for displaying and editing timelines.
    
    Signals:
        position_changed: Emitted when the current position changes.
        selection_changed: Emitted when the selection changes.
        timeline_clicked: Emitted when a timeline is clicked.
        segment_clicked: Emitted when a segment is clicked.
        segment_double_clicked: Emitted when a segment is double-clicked.
        segment_context_menu: Emitted when a segment context menu is requested.
    """
    
    # Signals
    position_changed = pyqtSignal(float)
    selection_changed = pyqtSignal(object, object)  # timeline, segment
    timeline_clicked = pyqtSignal(object, QPoint)  # timeline, position
    segment_clicked = pyqtSignal(object, object, QPoint)  # timeline, segment, position
    segment_double_clicked = pyqtSignal(object, object)  # timeline, segment
    segment_context_menu = pyqtSignal(object, object, QPoint)  # timeline, segment, position
    
    def __init__(self, app, parent=None):
        """
        Initialize the timeline widget.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.TimelineWidget")
        self.app = app
        
        # Widget properties
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Timeline properties
        self.timeline_height = TIMELINE_HEIGHT
        self.timeline_spacing = 10
        self.time_scale = 100.0  # pixels per second
        self.min_segment_width = TIMELINE_SEGMENT_MIN_WIDTH
        
        # Zoom properties
        self.zoom_level = 1.0
        self.min_zoom = MIN_ZOOM
        self.max_zoom = MAX_ZOOM
        self.zoom_step = ZOOM_STEP
        
        # Position and selection
        self.position = 0.0
        self.dragging_position = False
        self.selected_timeline = None
        self.selected_segment = None
        self.selected_boundary = None  # For selecting the line between segments
        self.selected_boundary_time = None  # Time value of the selected boundary
        self.selected_boundary_segments = (None, None)  # (left_segment, right_segment)
        
        # Segment editing
        self.copied_segment = None
        
        # Dragging state variables
        self.dragging_segment = False
        self.drag_start_mouse_pos = None
        self.drag_segment_initial_start_time = None
        self.drag_segment_initial_end_time = None
        
        # Resizing state variables
        self.resizing_segment = False
        self.resize_edge = None  # "left" or "right"
        self.resize_start_mouse_pos = None
        self.resize_segment_initial_start_time = None
        self.resize_segment_initial_end_time = None
        
        # Boundary dragging state variables
        self.dragging_boundary = False
        self.drag_boundary_start_pos = None
        self.drag_boundary_start_time = None
        self.drag_boundary_segments = (None, None)  # (left_segment, right_segment) for boundary dragging
        
        # Create UI
        self._create_ui()
        
        # Connect signals
        self._connect_signals()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create toolbar
        self.toolbar = QToolBar()
        self.main_layout.addWidget(self.toolbar)
        
        # Timeline controls are now handled through the Timeline menu in the main window
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.main_layout.addWidget(self.scroll_area)
        
        # Create timeline container
        self.timeline_container = TimelineContainer(self)
        self.scroll_area.setWidget(self.timeline_container)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Connect timeline manager signals
        self.app.timeline_manager.timeline_added.connect(self._on_timeline_added)
        self.app.timeline_manager.timeline_removed.connect(self._on_timeline_removed)
        self.app.timeline_manager.timeline_modified.connect(self._on_timeline_modified)
        self.app.timeline_manager.segment_added.connect(self._on_segment_added)
        self.app.timeline_manager.segment_removed.connect(self._on_segment_removed)
        self.app.timeline_manager.segment_modified.connect(self._on_segment_modified)
        self.app.timeline_manager.segment_selected.connect(self._on_segment_selected)
        self.app.timeline_manager.position_changed.connect(self._on_position_changed)
        
        # Connect audio manager signals
        self.app.audio_manager.position_changed.connect(self._on_position_changed)
    
    def zoom_in(self):
        """Zoom in on the timeline."""
        self.set_zoom(self.zoom_level * self.zoom_step)
    
    def zoom_out(self):
        """Zoom out on the timeline."""
        self.set_zoom(self.zoom_level / self.zoom_step)
    
    def zoom_fit(self):
        """Fit the timeline to the window."""
        if not self.app.project_manager.current_project:
            return
        
        # Get the sequence length from the project
        sequence_length = self.app.project_manager.current_project.total_duration
        
        # Calculate zoom level to fit the sequence length
        if sequence_length > 0:
            viewport_width = self.scroll_area.viewport().width()
            zoom = viewport_width / (sequence_length * self.time_scale)
            self.set_zoom(zoom)
            
            # Ensure the end of the sequence is visible by scrolling to it
            end_pos_x = int(sequence_length * self.time_scale * self.zoom_level)
            self.scroll_area.horizontalScrollBar().setValue(max(0, end_pos_x - viewport_width))
    
    def set_zoom(self, zoom):
        """
        Set the zoom level.
        
        Args:
            zoom (float): Zoom level.
        """
        # Clamp zoom level
        zoom = max(self.min_zoom, min(self.max_zoom, zoom))
        
        # Save current center position
        viewport_width = self.scroll_area.viewport().width()
        scroll_pos = self.scroll_area.horizontalScrollBar().value()
        center_pos = scroll_pos + viewport_width / 2
        center_time = center_pos / (self.time_scale * self.zoom_level)
        
        # Update zoom level
        self.zoom_level = zoom
        
        # Update timeline container
        self.timeline_container.update_size()
        
        # Restore center position
        new_center_pos = center_time * self.time_scale * self.zoom_level
        new_scroll_pos = new_center_pos - viewport_width / 2
        self.scroll_area.horizontalScrollBar().setValue(int(new_scroll_pos))
        
        # Redraw
        self.timeline_container.update()
    
    def set_position(self, position):
        """
        Set the current position.
        
        Args:
            position (float): Position in seconds.
        """
        if position < 0:
            position = 0
        
        # Log the position change
        self.logger.debug(f"Setting position from {self.position:.2f}s to {position:.2f}s")
        
        # Update position
        self.position = position
        
        # Ensure position marker is visible
        self._ensure_position_visible()
        
        # Force a complete repaint of the timeline container
        self.timeline_container.force_repaint()
        
        # Emit signal
        self.position_changed.emit(position)
    
    def _ensure_position_visible(self):
        """Ensure the current position marker is visible."""
        # Calculate position in pixels
        pos_x = int(self.position * self.time_scale * self.zoom_level)
        
        # Get viewport width
        viewport_width = self.scroll_area.viewport().width()
        
        # Get current scroll position
        scroll_pos = self.scroll_area.horizontalScrollBar().value()
        
        # Log for debugging
        # Show more precision in the position
        self.logger.debug(f"Ensuring position visible: pos_x={pos_x}, scroll_pos={scroll_pos}, viewport_width={viewport_width}, position={self.position:.3f}s")
        
        # If position is 0, always scroll to the beginning
        if self.position == 0.0:
            self.logger.debug("Position is 0, scrolling to beginning")
            self.scroll_area.horizontalScrollBar().setValue(0)
            return
        
        # Check if position is outside visible area
        if pos_x < scroll_pos or pos_x > scroll_pos + viewport_width:
            # Scroll to make position visible
            new_scroll_pos = max(0, pos_x - viewport_width / 2)
            self.logger.debug(f"Position outside visible area, scrolling to {new_scroll_pos}")
            self.scroll_area.horizontalScrollBar().setValue(int(new_scroll_pos))
    
    def select_timeline(self, timeline):
        """
        Select a timeline.
        
        Args:
            timeline: Timeline to select.
        """
        self.selected_timeline = timeline
        self.selected_segment = None
        
        # Update timeline manager
        self.app.timeline_manager.select_segment(timeline, None)
        
        # Emit signal
        self.selection_changed.emit(timeline, None)
        
        # Redraw
        self.timeline_container.update()
    def select_segment(self, timeline, segment):
        """
        Select a segment.
        
        Args:
            timeline: Timeline containing the segment.
            segment: Segment to select.
        """
        # Clear any boundary selection
        self.selected_boundary = False
        self.selected_boundary_time = None
        self.selected_boundary_segments = (None, None)
        
        self.selected_timeline = timeline
        self.selected_segment = segment
        
        # Update timeline manager
        self.app.timeline_manager.select_segment(timeline, segment)
        
        # Emit signal
        self.selection_changed.emit(timeline, segment)
        
        # Show segment editor in main window
        if hasattr(self.app, 'main_window'):
            # Hide boundary editor if visible
            if hasattr(self.app.main_window, 'hide_boundary_editor'):
                self.app.main_window.hide_boundary_editor()
            
            # Show segment editor
            if hasattr(self.app.main_window, 'show_segment_editor'):
                self.app.main_window.show_segment_editor(timeline, segment)
        
        # Redraw
        self.timeline_container.update()
    
    def select_boundary(self, timeline, time, left_segment, right_segment):
        """
        Select a boundary between two segments.
        
        Args:
            timeline: Timeline containing the segments.
            time: Time position of the boundary.
            left_segment: Segment to the left of the boundary.
            right_segment: Segment to the right of the boundary.
        """
        # Check if this boundary is already selected (for toggle behavior)
        if (self.selected_boundary and
            self.selected_boundary_time == time and
            self.selected_boundary_segments == (left_segment, right_segment)):
            # Deselect the boundary
            self.clear_selection()
            return
        
        # Clear any segment selection
        self.selected_segment = None
        
        # Set boundary selection
        self.selected_timeline = timeline
        self.selected_boundary = True
        self.selected_boundary_time = time
        self.selected_boundary_segments = (left_segment, right_segment)
        
        # Update timeline manager - clear segment selection
        self.app.timeline_manager.clear_selection()
        
        # Show boundary editor in main window
        if hasattr(self.app, 'main_window'):
            # Hide segment editor if visible
            if hasattr(self.app.main_window, 'hide_segment_editor'):
                self.app.main_window.hide_segment_editor()
            
            # Show boundary editor
            if hasattr(self.app.main_window, 'show_boundary_editor'):
                self.app.main_window.show_boundary_editor(timeline, time, left_segment, right_segment)
        
        # Emit signal
        self.selection_changed.emit(timeline, None)
        
        # Redraw
        self.timeline_container.update()
    
    def clear_selection(self):
        """Clear the current selection."""
        self.selected_timeline = None
        self.selected_segment = None
        self.selected_boundary = False
        self.selected_boundary_time = None
        self.selected_boundary_segments = (None, None)
        
        # Update timeline manager
        self.app.timeline_manager.clear_selection()
        
        # Hide editors in main window
        if hasattr(self.app, 'main_window'):
            if hasattr(self.app.main_window, 'hide_segment_editor'):
                self.app.main_window.hide_segment_editor()
            if hasattr(self.app.main_window, 'hide_boundary_editor'):
                self.app.main_window.hide_boundary_editor()
        
        # Emit signal
        self.selection_changed.emit(None, None)
        
        # Redraw
        self.timeline_container.update()
    
    def cut_selected_segment(self):
        """Cut the selected segment."""
        if not self.selected_timeline or not self.selected_segment:
            return
        
        # Copy segment
        self.copy_selected_segment()
        
        # Remove segment
        self.app.timeline_manager.remove_segment(self.selected_timeline, self.selected_segment)
    
    def copy_selected_segment(self):
        """Copy the selected segment."""
        if not self.selected_timeline or not self.selected_segment:
            return
        
        # Create a copy of the segment
        self.copied_segment = {
            "start_time": self.selected_segment.start_time,
            "end_time": self.selected_segment.end_time,
            "color": self.selected_segment.color,
            "pixels": self.selected_segment.pixels,
            "effects": [effect.to_dict() for effect in self.selected_segment.effects]
        }
    
    def paste_segment(self):
        """Paste the copied segment."""
        if not self.copied_segment or not self.selected_timeline:
            return
        
        # Calculate paste position
        paste_time = self.position
        duration = self.copied_segment["end_time"] - self.copied_segment["start_time"]
        
        # Create new segment
        self.app.timeline_manager.add_segment(
            timeline=self.selected_timeline,
            start_time=paste_time,
            end_time=paste_time + duration,
            color=self.copied_segment["color"],
            pixels=self.copied_segment["pixels"]
        )
        
        # TODO: Add effects
    
    def delete_selected_segment(self):
        """Delete the selected segment."""
        if not self.selected_timeline or not self.selected_segment:
            return
        
        # Remove segment
        self.app.timeline_manager.remove_segment(self.selected_timeline, self.selected_segment)
    
    def select_all_segments(self):
        """Select all segments in the current timeline."""
        # Not implemented - we only support selecting one segment at a time
        pass
    
    def _on_add_timeline(self):
        """Handle Add Timeline button click."""
        self.app.timeline_manager.add_timeline()
    
    def _on_remove_timeline(self):
        """Handle Remove Timeline button click."""
        if self.selected_timeline:
            self.app.timeline_manager.remove_timeline(self.selected_timeline)
    
    def _on_timeline_added(self, timeline):
        """Handle timeline added signal."""
        # Update timeline container
        self.timeline_container.update_size()
        self.timeline_container.update()
    
    def _on_timeline_removed(self, timeline):
        """Handle timeline removed signal."""
        # Update timeline container
        self.timeline_container.update_size()
        self.timeline_container.update()
    
    def _on_timeline_modified(self, timeline):
        """Handle timeline modified signal."""
        # Update timeline container
        self.timeline_container.update()
    
    def _on_segment_added(self, timeline, segment):
        """Handle segment added signal."""
        # Update timeline container
        self.timeline_container.update()
    
    def _on_segment_removed(self, timeline, segment):
        """Handle segment removed signal."""
        # Update timeline container
        self.timeline_container.update()
    
    def _on_segment_modified(self, timeline, segment):
        """Handle segment modified signal."""
        # Update timeline container
        self.timeline_container.update()
    
    def _on_segment_selected(self, timeline, segment):
        """Handle segment selected signal."""
        # Update selection
        self.selected_timeline = timeline
        self.selected_segment = segment
        
        # Redraw
        self.timeline_container.update()
    
    def _on_position_changed(self, position):
        """Handle position changed signal."""
        # Store old position for partial redraw
        old_position = self.position
        
        # Update position
        self.position = position
        
        # Ensure position marker is visible
        self._ensure_position_visible()
        
        # Calculate old and new position in pixels
        old_pos_x = int(old_position * self.time_scale * self.zoom_level)
        new_pos_x = int(position * self.time_scale * self.zoom_level)
        
        # Only log occasionally to reduce overhead
        if position % 1.0 < 0.02:  # Log approximately once per second
            self.logger.debug(f"Position changed to {position:.3f}s")
        
        # For smoother animation, we'll use a simpler approach:
        # Just force a complete repaint of the timeline container
        # This is more reliable and avoids artifacts with time markers
        self.timeline_container.force_repaint()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        # Undo (Ctrl+Z)
        if event.key() == Qt.Key.Key_Z and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.app.undo_manager.undo()
            event.accept()
            return
        
        # Redo (Ctrl+Shift+Z or Ctrl+Y)
        if ((event.key() == Qt.Key.Key_Z and
             event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier)) or
            (event.key() == Qt.Key.Key_Y and event.modifiers() == Qt.KeyboardModifier.ControlModifier)):
            self.app.undo_manager.redo()
            event.accept()
            return
        
        # Delete key
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected_segment()
            event.accept()
            return
        
        # Cut (Ctrl+X)
        if event.key() == Qt.Key.Key_X and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.cut_selected_segment()
            event.accept()
            return
        
        # Copy (Ctrl+C)
        if event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.copy_selected_segment()
            event.accept()
            return
        
        # Paste (Ctrl+V)
        if event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.paste_segment()
            event.accept()
            return
        
        # Arrow keys for fine adjustment
        if self.selected_timeline and self.selected_segment:
            if event.key() == Qt.Key.Key_Left:
                # Move segment left
                # Use 0.01 increment for finer control (1/100th second precision)
                self.app.timeline_manager.modify_segment(
                    timeline=self.selected_timeline,
                    segment=self.selected_segment,
                    start_time=self.selected_segment.start_time - 0.01,
                    end_time=self.selected_segment.end_time - 0.01
                )
                event.accept()
                return
            
            if event.key() == Qt.Key.Key_Right:
                # Move segment right
                # Use 0.01 increment for finer control (1/100th second precision)
                self.app.timeline_manager.modify_segment(
                    timeline=self.selected_timeline,
                    segment=self.selected_segment,
                    start_time=self.selected_segment.start_time + 0.01,
                    end_time=self.selected_segment.end_time + 0.01
                )
                event.accept()
                return
            
            if event.key() == Qt.Key.Key_Up:
                # Increase segment duration (extend end)
                # Use 0.01 increment for finer control (1/100th second precision)
                self.app.timeline_manager.modify_segment(
                    timeline=self.selected_timeline,
                    segment=self.selected_segment,
                    end_time=self.selected_segment.end_time + 0.01
                )
                event.accept()
                return
            
            if event.key() == Qt.Key.Key_Down:
                # Decrease segment duration (shrink end)
                # Ensure minimum segment duration of 0.02 seconds
                if self.selected_segment.end_time - self.selected_segment.start_time > 0.02:
                    self.app.timeline_manager.modify_segment(
                        timeline=self.selected_timeline,
                        segment=self.selected_segment,
                        end_time=self.selected_segment.end_time - 0.01
                    )
                event.accept()
                return
        
        # Pass event to parent
        super().keyPressEvent(event)


class TimelineContainer(QWidget):
    """
    Container widget for timelines.
    
    This widget is responsible for drawing the timelines and handling mouse events.
    """
    
    def __init__(self, parent):
        """
        Initialize the timeline container.
        
        Args:
            parent: Parent widget (TimelineWidget).
        """
        super().__init__(parent)
        self.parent_widget = parent
        self.app = parent.app
        
        # Set up logger
        self.logger = logging.getLogger("SequenceMaker.TimelineContainer")
        
        # Widget properties
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Enable mouse tracking for cursor position updates
        self.setMouseTracking(True)
        
        # Update size
        # Update size
        self.update_size()
    
    def update_size(self):
        """Update the widget size based on timelines and zoom level."""
        if not self.app.project_manager.current_project:
            return
        
        # Calculate width based on project duration and zoom level
        duration = 0
        for timeline in self.app.project_manager.current_project.timelines:
            timeline_duration = timeline.get_duration()
            if timeline_duration > duration:
                duration = timeline_duration
        
        # Add some padding
        duration += 10.0
        
        # Calculate width
        width = int(duration * self.parent_widget.time_scale * self.parent_widget.zoom_level)
        
        # Calculate height based on number of timelines
        timeline_count = len(self.app.project_manager.current_project.timelines)
        height = (timeline_count * (self.parent_widget.timeline_height + self.parent_widget.timeline_spacing) +
                 self.parent_widget.timeline_spacing)
        
        # Set minimum and maximum size to exactly fit the timelines
        self.setMinimumSize(width, height)
        self.setMaximumHeight(height)  # Prevent extra white space
    
    def force_repaint(self):
        """Force a complete repaint of the timeline container."""
        self.app.logger.debug("Forcing complete repaint of timeline container")
        
        # Schedule a full repaint
        self.update()
        
        # NOTE: Removed processEvents call as it can cause choppy animation
        # from PyQt6.QtCore import QCoreApplication
        # QCoreApplication.processEvents()
    
    def paintEvent(self, event):
        """
        Paint the widget.
        
        Args:
            event: Paint event.
        """
        if not self.app.project_manager.current_project:
            return
        
        # Create painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get the update rect
        update_rect = event.rect()
        
        # Always do a full repaint to avoid artifacts
        # First clear the background
        painter.fillRect(update_rect, QColor(240, 240, 240))
        
        # Draw the time grid
        self._draw_time_grid(painter)
        
        # Draw the timelines
        self._draw_timelines(painter)
        
        # Draw the position marker on top
        self._draw_position_marker(painter)
    
    def _draw_time_grid(self, painter):
        """
        Draw the time grid.
        
        Args:
            painter: QPainter instance.
        """
        # Set pen with brighter color for better visibility on dark background
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        
        # Calculate grid spacing based on zoom level
        zoom = self.parent_widget.zoom_level
        refresh_rate = self.app.project_manager.current_project.refresh_rate
        
        # Adjust grid spacing based on zoom level and refresh rate
        if zoom < 0.1:
            # Very zoomed out - show grid every 60 seconds
            grid_spacing = 60.0
        elif zoom < 0.5:
            # Zoomed out - show grid every 10 seconds
            grid_spacing = 10.0
        elif zoom < 2.0:
            # Normal zoom - show grid every 1 second
            grid_spacing = 1.0
        elif zoom < 10.0:
            # Zoomed in - show grid every 0.1 seconds
            grid_spacing = 0.1
        elif zoom < 50.0:
            # Very zoomed in - show grid every 0.01 seconds
            grid_spacing = 0.01
        else:
            # Extremely zoomed in - show grid every 0.001 seconds
            grid_spacing = 0.001
        
        # Calculate pixel spacing
        pixel_spacing = grid_spacing * self.parent_widget.time_scale * zoom
        
        # Draw vertical grid lines
        width = self.width()
        height = self.height()
        
        # Calculate first grid line
        first_grid_time = math.floor(0 / grid_spacing) * grid_spacing
        first_grid_x = int(first_grid_time * self.parent_widget.time_scale * zoom)
        
        # Draw grid lines
        x = first_grid_x
        while x < width:
            painter.drawLine(int(x), 0, int(x), height)
            # Draw time label with better visibility
            time = x / (self.parent_widget.time_scale * zoom)
            
            # Format time string based on precision needed
            if grid_spacing >= 1.0:
                time_str = f"{int(time)}s"
            elif grid_spacing >= 0.1:
                time_str = f"{time:.1f}s"
            elif grid_spacing >= 0.01:
                time_str = f"{time:.2f}s"
            else:
                time_str = f"{time:.3f}s"
            
            # Use a font with bold weight for better visibility
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            
            # Draw text with a small background for better contrast
            text_rect = painter.fontMetrics().boundingRect(time_str)
            text_rect.moveLeft(int(x) + 2)
            text_rect.moveTop(2)
            text_rect.adjust(-2, -1, 2, 1)  # Add some padding
            
            # Draw background
            painter.fillRect(text_rect, QColor(40, 40, 40, 180))
            
            # Draw text (only once)
            painter.drawText(int(x) + 2, 14, time_str)
            
            # Move to next grid line
            x += pixel_spacing
        
        # Draw sequence end time indicator line
        if self.app.project_manager.current_project:
            sequence_length = self.app.project_manager.current_project.total_duration
            end_x = int(sequence_length * self.parent_widget.time_scale * zoom)
            
            # Draw a dashed vertical line at the sequence end time
            dash_pen = QPen(QColor(255, 255, 0, 180), 2)  # Yellow, semi-transparent
            dash_pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(dash_pen)
            painter.drawLine(end_x, 0, end_x, height)
            
            # Draw a label for the end time
            end_time_str = self._format_time_as_hms(sequence_length)
            
            # Use a font with bold weight for better visibility
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            
            # Draw text with a small background for better contrast
            text_rect = painter.fontMetrics().boundingRect(f"End: {end_time_str}")
            text_rect.moveLeft(end_x - text_rect.width() - 5)
            text_rect.moveTop(height - 20)
            text_rect.adjust(-2, -1, 2, 1)  # Add some padding
            
            # Draw background
            painter.fillRect(text_rect, QColor(40, 40, 40, 180))
            
            # Draw text
            painter.setPen(QPen(QColor(255, 255, 0), 1))
            painter.drawText(end_x - text_rect.width() - 3, height - 8, f"End: {end_time_str}")
    
    def _draw_time_grid_partial(self, painter, update_rect):
        """
        Draw only the part of the time grid that intersects with the update rect.
        
        Args:
            painter: QPainter instance.
            update_rect: The rectangle to update.
        """
        # First clear the background in the update rect to prevent artifacts
        painter.fillRect(update_rect, QColor(240, 240, 240))
        
        # Set pen with brighter color for better visibility on dark background
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        
        # Calculate grid spacing based on zoom level
        zoom = self.parent_widget.zoom_level
        refresh_rate = self.app.project_manager.current_project.refresh_rate
        
        # Adjust grid spacing based on zoom level and refresh rate
        if zoom < 0.1:
            grid_spacing = 60.0
        elif zoom < 0.5:
            grid_spacing = 10.0
        elif zoom < 2.0:
            grid_spacing = 1.0
        elif zoom < 10.0:
            grid_spacing = 0.1
        elif zoom < 50.0:
            grid_spacing = 0.01
        else:
            grid_spacing = 0.001
        
        # Calculate pixel spacing
        pixel_spacing = grid_spacing * self.parent_widget.time_scale * zoom
        
        # Get dimensions
        height = self.height()
        
        # Calculate first grid line that intersects with the update rect
        first_time = update_rect.left() / (self.parent_widget.time_scale * zoom)
        first_grid_time = math.floor(first_time / grid_spacing) * grid_spacing
        first_grid_x = int(first_grid_time * self.parent_widget.time_scale * zoom)
        
        # Draw grid lines that intersect with the update rect
        x = first_grid_x
        while x <= update_rect.right():
            # Only draw if within the update rect
            if update_rect.left() <= x <= update_rect.right():
                painter.drawLine(int(x), 0, int(x), height)
                
                # Draw time label with better visibility
                time = x / (self.parent_widget.time_scale * zoom)
                
                # Format time string based on precision needed
                if grid_spacing >= 1.0:
                    time_str = f"{int(time)}s"
                elif grid_spacing >= 0.1:
                    time_str = f"{time:.1f}s"
                elif grid_spacing >= 0.01:
                    time_str = f"{time:.2f}s"
                else:
                    time_str = f"{time:.3f}s"
                
                # Use a font with bold weight for better visibility
                font = painter.font()
                font.setBold(True)
                painter.setFont(font)
                
                # Draw text with a small background for better contrast
                text_rect = painter.fontMetrics().boundingRect(time_str)
                text_rect.moveLeft(int(x) + 2)
                text_rect.moveTop(2)
                text_rect.adjust(-2, -1, 2, 1)  # Add some padding
                
                # Draw background
                painter.fillRect(text_rect, QColor(40, 40, 40, 180))
                
                # Draw text
                painter.drawText(int(x) + 2, 14, time_str)
            
            # Move to next grid line
            x += pixel_spacing
    
    def _draw_timelines(self, painter):
        """
        Draw the timelines.
        
        Args:
            painter: QPainter instance.
        """
        # Get timelines
        timelines = self.app.project_manager.current_project.timelines
        
        # Draw each timeline
        y = self.parent_widget.timeline_spacing
        for timeline in timelines:
            # Calculate timeline rect
            timeline_rect = QRect(
                0,
                y,
                self.width(),
                self.parent_widget.timeline_height
            )
            
            # Draw timeline background
            if timeline == self.parent_widget.selected_timeline:
                # Selected timeline
                painter.fillRect(timeline_rect, QColor(60, 60, 80))
            else:
                # Normal timeline - black background as requested
                painter.fillRect(timeline_rect, QColor(30, 30, 30))
            
            # Draw timeline border
            painter.setPen(QPen(QColor(180, 180, 180), 1))
            painter.drawRect(timeline_rect)
            
            # Draw timeline name with white text for better visibility on dark background
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawText(
                timeline_rect.adjusted(5, 5, -5, -5),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                timeline.name
            )
            
            # Draw segments
            self._draw_segments(painter, timeline, timeline_rect)
            
            # Move to next timeline
            y += self.parent_widget.timeline_height + self.parent_widget.timeline_spacing
    
    def _draw_timelines_partial(self, painter, update_rect):
        """
        Draw only the parts of timelines that intersect with the update rect.
        
        Args:
            painter: QPainter instance.
            update_rect: The rectangle to update.
        """
        # Get timelines
        timelines = self.app.project_manager.current_project.timelines
        
        # Draw each timeline
        y = self.parent_widget.timeline_spacing
        for timeline in timelines:
            # Calculate timeline rect
            timeline_rect = QRect(
                0,
                y,
                self.width(),
                self.parent_widget.timeline_height
            )
            
            # Check if timeline intersects with update rect
            if timeline_rect.intersects(update_rect):
                # Calculate the intersection rect
                intersection = timeline_rect.intersected(update_rect)
                
                # Draw timeline background for the intersection
                if timeline == self.parent_widget.selected_timeline:
                    # Selected timeline
                    painter.fillRect(intersection, QColor(60, 60, 80))
                else:
                    # Normal timeline
                    painter.fillRect(intersection, QColor(30, 30, 30))
                
                # Draw segments that intersect with the update rect
                self._draw_segments_partial(painter, timeline, timeline_rect, update_rect)
            
            # Move to next timeline
            y += self.parent_widget.timeline_height + self.parent_widget.timeline_spacing
    
    def _draw_segments_partial(self, painter, timeline, timeline_rect, update_rect):
        """
        Draw only the segments of a timeline that intersect with the update rect.
        
        Args:
            painter: QPainter instance.
            timeline: Timeline to draw segments for.
            timeline_rect: Rectangle of the timeline.
            update_rect: The rectangle to update.
        """
        # Get segments
        segments = timeline.segments
        
        # Draw each segment
        for segment in segments:
            # Calculate segment rect
            start_x = int(segment.start_time * self.parent_widget.time_scale * self.parent_widget.zoom_level)
            end_x = int(segment.end_time * self.parent_widget.time_scale * self.parent_widget.zoom_level)
            width = max(self.parent_widget.min_segment_width, end_x - start_x)
            
            segment_rect = QRect(
                start_x,
                timeline_rect.top() + 20,
                width,
                timeline_rect.height() - 30
            )
            
            # Check if segment intersects with update rect
            if segment_rect.intersects(update_rect):
                # Draw segment background
                r, g, b = segment.color
                segment_color = QColor(r, g, b)
                
                # Create gradient
                from PyQt6.QtCore import QPointF
                gradient = QLinearGradient(
                    QPointF(segment_rect.topLeft()),
                    QPointF(segment_rect.bottomLeft())
                )
                gradient.setColorAt(0, segment_color.lighter(120))
                gradient.setColorAt(1, segment_color)
                
                # Fill segment
                painter.fillRect(segment_rect, gradient)
                
                # Draw segment border
                if segment == self.parent_widget.selected_segment:
                    # Selected segment
                    painter.setPen(QPen(QColor(0, 0, 0), 2))
                else:
                    # Normal segment
                    painter.setPen(QPen(QColor(0, 0, 0), 1))
                
                painter.drawRect(segment_rect)
    
    def _draw_segments(self, painter, timeline, timeline_rect):
        """
        Draw the segments of a timeline.
        
        Args:
            painter: QPainter instance.
            timeline: Timeline to draw segments for.
            timeline_rect: Rectangle of the timeline.
        """
        # Get segments
        segments = timeline.segments
        
        # Draw each segment
        for segment in segments:
            # Calculate segment rect
            start_x = int(segment.start_time * self.parent_widget.time_scale * self.parent_widget.zoom_level)
            end_x = int(segment.end_time * self.parent_widget.time_scale * self.parent_widget.zoom_level)
            width = max(self.parent_widget.min_segment_width, end_x - start_x)
            
            segment_rect = QRect(
                start_x,
                timeline_rect.top() + 20,
                width,
                timeline_rect.height() - 30
            )
            
            # Draw segment background
            r, g, b = segment.color
            segment_color = QColor(r, g, b)
            
            # Create gradient
            from PyQt6.QtCore import QPointF
            gradient = QLinearGradient(
                QPointF(segment_rect.topLeft()),
                QPointF(segment_rect.bottomLeft())
            )
            gradient.setColorAt(0, segment_color.lighter(120))
            gradient.setColorAt(1, segment_color)
            
            # Fill segment
            painter.fillRect(segment_rect, gradient)
            
            # Draw segment border
            if segment == self.parent_widget.selected_segment:
                # Selected segment
                painter.setPen(QPen(QColor(255, 255, 255), 2))  # White, 2px wide
            else:
                # Normal segment
                painter.setPen(QPen(QColor(0, 0, 0), 1))  # Black, 1px wide
            
            painter.drawRect(segment_rect)
            
            # Draw bold line for selected boundary
            if self.parent_widget.selected_boundary:
                left_segment, right_segment = self.parent_widget.selected_boundary_segments
                boundary_time = self.parent_widget.selected_boundary_time
                
                # Check if this segment is part of the selected boundary
                if segment == left_segment or segment == right_segment:
                    # Calculate boundary position
                    boundary_x = int(boundary_time * self.parent_widget.time_scale * self.parent_widget.zoom_level)
                    
                    # Draw bold line at boundary - match the height of the segment
                    painter.setPen(QPen(QColor(255, 255, 255), 3))  # White, 3px wide
                    painter.drawLine(
                        boundary_x,
                        segment_rect.top(),  # Start at the top of the segment
                        boundary_x,
                        segment_rect.bottom()  # End at the bottom of the segment
                    )
            
            # Note: Color name labels removed as requested by user
    
    def _draw_position_marker(self, painter):
        """
        Draw the position marker.
        
        Args:
            painter: QPainter instance.
        """
        # Calculate position in pixels
        pos_x = int(self.parent_widget.position * self.parent_widget.time_scale * self.parent_widget.zoom_level)
        
        # Log the position for debugging (reduced logging frequency)
        if self.parent_widget.position % 0.5 < 0.02:  # Log only every ~0.5 seconds
            self.app.logger.debug(f"Drawing position marker at x={pos_x} (position={self.parent_widget.position:.3f}s)")
        
        # Create a semi-transparent red color for the line to avoid obscuring time labels
        line_color = QColor(255, 0, 0, 200)  # Added alpha channel (200/255 opacity)
        
        # Draw position line with a more visible style, but start below the time labels
        painter.setPen(QPen(line_color, 3))  # Increased width for better visibility
        painter.drawLine(pos_x, 20, pos_x, self.height())  # Start at y=20 to avoid time labels
        
        # Draw a small circle at the top of the line for better visibility
        # Use a fully opaque color for the circle to make it stand out
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.drawEllipse(pos_x - 4, 20, 8, 8)  # Position circle at y=20
    
    def _format_time_as_hms(self, seconds):
        """
        Format time in seconds as hours:minutes:seconds.
        
        Args:
            seconds (float): Time in seconds.
            
        Returns:
            str: Formatted time string (HH:MM:SS).
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
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
    
    def _get_timeline_at_pos(self, pos):
        """
        Get the timeline at a specific position.
        
        Args:
            pos: QPoint position.
        
        Returns:
            tuple: (timeline, y_offset) or (None, 0) if no timeline at position.
        """
        if not self.app.project_manager.current_project:
            return None, 0
        
        # Get timelines
        timelines = self.app.project_manager.current_project.timelines
        
        # Check each timeline
        y = self.parent_widget.timeline_spacing
        for timeline in timelines:
            # Calculate timeline rect
            timeline_rect = QRect(
                0,
                y,
                self.width(),
                self.parent_widget.timeline_height
            )
            
            # Check if position is in timeline rect
            if timeline_rect.contains(pos):
                return timeline, pos.y() - y
            
            # Move to next timeline
            y += self.parent_widget.timeline_height + self.parent_widget.timeline_spacing
        
        return None, 0
    
    def _get_segment_at_pos(self, timeline, pos):
        """
        Get the segment at a specific position.
        
        Args:
            timeline: Timeline to check.
            pos: QPoint position.
        
        Returns:
            tuple: (segment, edge, boundary_info) or (None, None, None) if no segment at position.
            edge can be "left", "right", or None.
            boundary_info is (time, left_segment, right_segment) or None.
        """
        if not timeline:
            return None, None, None
        
        # Get segments
        segments = timeline.segments
        
        # Convert position to time
        time = pos.x() / (self.parent_widget.time_scale * self.parent_widget.zoom_level)
        
        # First check for segment edges (prioritize edges over segment bodies)
        edge_threshold = 5  # pixels
        
        # Find segments with edges near the cursor position
        edge_segments = []
        for segment in segments:
            # Calculate segment rect
            start_x = int(segment.start_time * self.parent_widget.time_scale * self.parent_widget.zoom_level)
            end_x = int(segment.end_time * self.parent_widget.time_scale * self.parent_widget.zoom_level)
            
            # Log edge positions for debugging
            self.logger.debug(f"Segment: {segment.start_time:.3f}s-{segment.end_time:.3f}s, " +
                             f"x-coords: {start_x}-{end_x}, mouse at: {pos.x()}")
            
            # Check left edge
            if abs(pos.x() - start_x) <= edge_threshold:
                edge_segments.append((segment, "left", abs(pos.x() - start_x), segment.start_time))
            
            # Check right edge
            if abs(pos.x() - end_x) <= edge_threshold:
                edge_segments.append((segment, "right", abs(pos.x() - end_x), segment.end_time))
        
        # If we found edges, return the closest one
        if edge_segments:
            # Sort by distance (third element in tuple)
            edge_segments.sort(key=lambda x: x[2])
            
            closest_segment = edge_segments[0][0]
            closest_edge = edge_segments[0][1]
            closest_time = edge_segments[0][3]
            
            # Check if this is a boundary between two segments
            if closest_edge == "right":
                # Find if there's a segment that starts exactly where this one ends
                for segment in segments:
                    if segment != closest_segment and abs(segment.start_time - closest_time) < 0.001:
                        # This is a boundary between two segments
                        boundary_info = (closest_time, closest_segment, segment)
                        return closest_segment, closest_edge, boundary_info
            elif closest_edge == "left":
                # Find if there's a segment that ends exactly where this one starts
                for segment in segments:
                    if segment != closest_segment and abs(segment.end_time - closest_time) < 0.001:
                        # This is a boundary between two segments
                        boundary_info = (closest_time, segment, closest_segment)
                        return closest_segment, closest_edge, boundary_info
            
            # Not a boundary, just a regular edge
            return closest_segment, closest_edge, None
        
        # If no edges found, check if position is inside any segment
        for segment in segments:
            start_x = int(segment.start_time * self.parent_widget.time_scale * self.parent_widget.zoom_level)
            end_x = int(segment.end_time * self.parent_widget.time_scale * self.parent_widget.zoom_level)
            
            # Check if position is in segment
            if start_x <= pos.x() <= end_x:
                return segment, None, None
        
        return None, None, None
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events.
        
        Args:
            event: Mouse event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Get timeline at position
            timeline, y_offset = self._get_timeline_at_pos(event.pos())
            
            if timeline:
                # Get segment at position
                segment, edge, boundary_info = self._get_segment_at_pos(timeline, event.pos())
                
                if segment:
                    # Check if clicking on a boundary between segments
                    if boundary_info:
                        # Don't select the boundary on single click, just start dragging it
                        time, left_segment, right_segment = boundary_info
                        
                        # Start dragging boundary
                        self.parent_widget.dragging_boundary = True
                        self.parent_widget.drag_boundary_start_pos = event.pos()
                        self.parent_widget.drag_boundary_start_time = time
                        
                        # Store boundary segments for dragging
                        self.parent_widget.drag_boundary_segments = (left_segment, right_segment)
                        
                        # Log for debugging
                        self.logger.debug(f"Dragging boundary at time {time:.3f}s between segments")
                        
                        # Start drag operation in timeline manager to handle undo/redo properly
                        self.app.timeline_manager.start_drag_operation()
                        
                        # Set cursor
                        self.setCursor(Qt.CursorShape.SizeHorCursor)
                    else:
                        # Select segment
                        self.parent_widget.select_segment(timeline, segment)
                        
                        # Check if clicking on edge
                        if edge:
                            # Start resizing segment
                            self.parent_widget.resizing_segment = True
                            self.parent_widget.resize_edge = edge
                            self.parent_widget.resize_start_mouse_pos = event.pos()
                            
                            # Store initial segment boundaries
                            self.parent_widget.resize_segment_initial_start_time = segment.start_time
                            self.parent_widget.resize_segment_initial_end_time = segment.end_time
                            
                            # Log for debugging
                            self.logger.debug(f"Resizing segment {edge} edge: initial_boundaries={segment.start_time:.3f}s-{segment.end_time:.3f}s")
                            
                            # Start drag operation in timeline manager to handle undo/redo properly
                            self.app.timeline_manager.start_drag_operation()
                            
                            # Set cursor
                            self.setCursor(Qt.CursorShape.SizeHorCursor)
                        else:
                            # Start dragging segment
                            self.parent_widget.dragging_segment = True
                            self.parent_widget.drag_start_mouse_pos = event.pos()
                            self.parent_widget.drag_segment_initial_start_time = segment.start_time
                            self.parent_widget.drag_segment_initial_end_time = segment.end_time
                            
                            # Log for debugging
                            self.logger.debug(f"Dragging segment: initial_boundaries={segment.start_time:.3f}s-{segment.end_time:.3f}s")
                            
                            # Start drag operation in timeline manager to handle undo/redo properly
                            self.app.timeline_manager.start_drag_operation()
                        
                        # Set cursor
                        self.setCursor(Qt.CursorShape.ClosedHandCursor)
                    
                    # Emit signal
                    self.parent_widget.segment_clicked.emit(timeline, segment, event.pos())
                else:
                    # Select timeline
                    self.parent_widget.select_timeline(timeline)
                    
                    # Start dragging position
                    self.parent_widget.dragging_position = True
                    
                    # Update position
                    time = event.pos().x() / (self.parent_widget.time_scale * self.parent_widget.zoom_level)
                    self.parent_widget.set_position(time)
                    
                    # Emit signal
                    self.parent_widget.timeline_clicked.emit(timeline, event.pos())
            else:
                # Clear selection
                self.parent_widget.clear_selection()
                
                # Start dragging position
                self.parent_widget.dragging_position = True
                
                # Update position
                time = event.pos().x() / (self.parent_widget.time_scale * self.parent_widget.zoom_level)
                self.parent_widget.set_position(time)
        
        elif event.button() == Qt.MouseButton.RightButton:
            # Get timeline at position
            timeline, y_offset = self._get_timeline_at_pos(event.pos())
            
            if timeline:
                # Get segment at position
                segment, edge = self._get_segment_at_pos(timeline, event.pos())
                
                if segment:
                    # Select segment
                    self.parent_widget.select_segment(timeline, segment)
                    
                    # Show context menu
                    self._show_segment_context_menu(timeline, segment, event.pos())
                    
                    # Emit signal
                    self.parent_widget.segment_context_menu.emit(timeline, segment, event.pos())
                else:
                    # Select timeline
                    self.parent_widget.select_timeline(timeline)
                    
                    # Show context menu
                    self._show_timeline_context_menu(timeline, event.pos())
            else:
                # Clear selection
                self.parent_widget.clear_selection()
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move events.
        
        Args:
            event: Mouse event.
        """
        # Calculate cursor time position for all cases
        cursor_time = event.pos().x() / (self.parent_widget.time_scale * self.parent_widget.zoom_level)
        
        # Update cursor position in main window
        if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'update_cursor_position'):
            self.app.main_window.update_cursor_position(cursor_time)
            
        if self.parent_widget.dragging_position:
            # Update position
            self.parent_widget.set_position(cursor_time)
        
        elif self.parent_widget.dragging_boundary:
            # Calculate time difference
            time_diff = (
                event.pos().x() - self.parent_widget.drag_boundary_start_pos.x()
            ) / (self.parent_widget.time_scale * self.parent_widget.zoom_level)
            
            # Calculate new time
            new_time = self.parent_widget.drag_boundary_start_time + time_diff
            
            # Log for debugging
            self.logger.debug(f"Dragging boundary: diff={time_diff:.3f}s, new_time={new_time:.3f}s")
            
            # Ensure time is not negative
            if new_time < 0:
                new_time = 0
            
            try:
                # Get the boundary segments from the drag property
                left_segment, right_segment = self.parent_widget.drag_boundary_segments
                
                # Ensure the new time is valid
                # Use a more relaxed condition to allow dragging
                if left_segment and right_segment:
                    # Only constrain by the start of left segment and end of right segment
                    if left_segment.start_time < new_time < right_segment.end_time:
                        # Update left segment end time
                        self.app.timeline_manager.modify_segment(
                            timeline=self.parent_widget.selected_timeline,
                            segment=left_segment,
                            end_time=new_time
                        )
                        
                        # Update right segment start time
                        self.app.timeline_manager.modify_segment(
                            timeline=self.parent_widget.selected_timeline,
                            segment=right_segment,
                            start_time=new_time
                        )
                        
                        # If the boundary is selected, update its time
                        if self.parent_widget.selected_boundary:
                            self.parent_widget.selected_boundary_time = new_time
                            
                            # Update boundary editor if visible
                            if (hasattr(self.app, 'main_window') and
                                hasattr(self.app.main_window, 'boundary_time_input') and
                                hasattr(self.app.main_window, '_format_seconds_to_hms') and
                                hasattr(self.app.main_window, 'boundary_editor_container') and
                                self.app.main_window.boundary_editor_container.isVisible()):
                                
                                # Format time
                                time_str = self.app.main_window._format_seconds_to_hms(
                                    new_time, include_hundredths=True, hide_hours_if_zero=True)
                                
                                # Update input field
                                self.app.main_window.boundary_time_input.setText(time_str)
                                
                                # Update stored boundary time in main window
                                if hasattr(self.app.main_window, 'boundary_editor_time'):
                                    self.app.main_window.boundary_editor_time = new_time
                    
                    # Force a redraw to update the boundary position
                    self.update()
            except Exception as e:
                print(f"Error during boundary drag: {e}")
                
                # Update boundary editor in real-time
                if (hasattr(self.app, 'main_window') and
                    hasattr(self.app.main_window, 'boundary_time_input') and
                    hasattr(self.app.main_window, '_format_seconds_to_hms')):
                    
                    # Format time
                    time_str = self.app.main_window._format_seconds_to_hms(
                        new_time, include_hundredths=True, hide_hours_if_zero=True)
                    
                    # Update input field
                    self.app.main_window.boundary_time_input.setText(time_str)
                    
                    # Update stored boundary time in main window
                    if hasattr(self.app.main_window, 'boundary_editor_time'):
                        self.app.main_window.boundary_editor_time = new_time
            
        elif self.parent_widget.dragging_segment:
            # Calculate time difference based on mouse movement
            time_diff = (
                event.pos().x() - self.parent_widget.drag_start_mouse_pos.x()
            ) / (self.parent_widget.time_scale * self.parent_widget.zoom_level)
            
            # Calculate new start and end times based on initial positions
            new_start_time = self.parent_widget.drag_segment_initial_start_time + time_diff
            new_end_time = self.parent_widget.drag_segment_initial_end_time + time_diff
            
            # Log for debugging
            self.logger.debug(f"Dragging segment: diff={time_diff:.3f}s, new_boundaries={new_start_time:.3f}s-{new_end_time:.3f}s")
            
            # Ensure start time is not negative
            if new_start_time < 0:
                time_shift = -new_start_time
                new_start_time = 0
                new_end_time += time_shift  # Shift end time by same amount to maintain segment duration
            
            # Update segment position (without changing duration!)
            self.app.timeline_manager.modify_segment(
                timeline=self.parent_widget.selected_timeline,
                segment=self.parent_widget.selected_segment,
                start_time=new_start_time,
                end_time=new_end_time
            )
        
        elif self.parent_widget.resizing_segment:
            # Calculate time difference based on mouse movement
            time_diff = (
                event.pos().x() - self.parent_widget.resize_start_mouse_pos.x()
            ) / (self.parent_widget.time_scale * self.parent_widget.zoom_level)
            
            # Log for debugging
            self.logger.debug(f"Resizing {self.parent_widget.resize_edge} edge: diff={time_diff:.3f}s")
            
            # Define minimum segment width
            min_segment_width = 0.05  # Minimum segment width in seconds
            
            # Clearly differentiate edges
            if self.parent_widget.resize_edge == "left":
                # Calculate new start time based on initial start time plus movement
                new_start_time = self.parent_widget.resize_segment_initial_start_time + time_diff
                
                # Log for debugging
                self.logger.debug(f"Left edge: new_start_time={new_start_time:.3f}s, initial_end={self.parent_widget.resize_segment_initial_end_time:.3f}s")
                
                # Prevent collapsing and ensure minimum width
                if new_start_time >= self.parent_widget.resize_segment_initial_end_time - min_segment_width:
                    new_start_time = self.parent_widget.resize_segment_initial_end_time - min_segment_width
                    self.logger.debug(f"Preventing left edge from passing end: capped at {new_start_time:.3f}s")
                
                # Ensure time is not negative
                if new_start_time < 0:
                    new_start_time = 0
                    self.logger.debug(f"Preventing negative start time: capped at 0.000s")
                
                # Update segment with new start time
                self.app.timeline_manager.modify_segment(
                    timeline=self.parent_widget.selected_timeline,
                    segment=self.parent_widget.selected_segment,
                    start_time=new_start_time
                )
                
            elif self.parent_widget.resize_edge == "right":
                # Calculate new end time based on initial end time plus movement
                new_end_time = self.parent_widget.resize_segment_initial_end_time + time_diff
                
                # Log for debugging
                self.logger.debug(f"Right edge: new_end_time={new_end_time:.3f}s, initial_start={self.parent_widget.resize_segment_initial_start_time:.3f}s")
                
                # Prevent collapsing and ensure minimum width
                if new_end_time <= self.parent_widget.resize_segment_initial_start_time + min_segment_width:
                    new_end_time = self.parent_widget.resize_segment_initial_start_time + min_segment_width
                    self.logger.debug(f"Preventing right edge from passing start: capped at {new_end_time:.3f}s")
                
                # Update segment with new end time
                self.app.timeline_manager.modify_segment(
                    timeline=self.parent_widget.selected_timeline,
                    segment=self.parent_widget.selected_segment,
                    end_time=new_end_time
                )
        
        else:
            # Update cursor based on mouse position
            timeline, y_offset = self._get_timeline_at_pos(event.pos())
            
            if timeline:
                segment, edge, boundary_info = self._get_segment_at_pos(timeline, event.pos())
                
                if segment:
                    if boundary_info:
                        # Mouse over boundary between segments
                        self.setCursor(Qt.CursorShape.SizeHorCursor)
                    elif edge:
                        # Mouse over segment edge
                        self.setCursor(Qt.CursorShape.SizeHorCursor)
                    else:
                        # Mouse over segment
                        self.setCursor(Qt.CursorShape.OpenHandCursor)
                    
                    # Display segment information in status bar when hovering over segments
                    # This should work even when a segment is selected
                    if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'statusbar'):
                        
                        # Format start and end times
                        start_time_str = self.app.main_window._format_seconds_to_hms(
                            segment.start_time, include_hundredths=True, hide_hours_if_zero=True)
                        end_time_str = self.app.main_window._format_seconds_to_hms(
                            segment.end_time, include_hundredths=True, hide_hours_if_zero=True)
                        
                        # Format RGB color
                        r, g, b = segment.color
                        color_str = f"RGB({r}, {g}, {b})"
                        
                        # Display in status bar
                        self.app.main_window.statusbar.showMessage(
                            f"Segment: {start_time_str} - {end_time_str} | Color: {color_str}")
                else:
                    # Mouse over timeline
                    self.setCursor(Qt.CursorShape.ArrowCursor)
                    # Clear status bar message
                    if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'statusbar'):
                        self.app.main_window.statusbar.clearMessage()
            else:
                # Mouse not over timeline
                self.setCursor(Qt.CursorShape.ArrowCursor)
                # Clear status bar message
                if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'statusbar'):
                    self.app.main_window.statusbar.clearMessage()
    
    def leaveEvent(self, event):
        """
        Handle mouse leave events.
        
        Args:
            event: Leave event.
        """
        # Clear cursor position when mouse leaves the widget
        if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'update_cursor_position'):
            self.app.main_window.cursor_position_label.setText("Cursor: --:--:--")
        
        # Reset cursor
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
        # Call parent implementation
        super().leaveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events.
        
        Args:
            event: Mouse event.
        """
        # Check if we were dragging or resizing a segment or boundary
        was_dragging = self.parent_widget.dragging_segment
        was_resizing = self.parent_widget.resizing_segment
        was_dragging_boundary = self.parent_widget.dragging_boundary
        
        # Reset all state variables
        # Dragging position
        self.parent_widget.dragging_position = False
        
        # Dragging segment
        self.parent_widget.dragging_segment = False
        self.parent_widget.drag_start_mouse_pos = None
        self.parent_widget.drag_segment_initial_start_time = None
        self.parent_widget.drag_segment_initial_end_time = None
        
        # Resizing segment
        self.parent_widget.resizing_segment = False
        self.parent_widget.resize_edge = None
        self.parent_widget.resize_start_mouse_pos = None
        self.parent_widget.resize_segment_initial_start_time = None
        self.parent_widget.resize_segment_initial_end_time = None
        
        # Boundary dragging
        self.parent_widget.dragging_boundary = False
        self.parent_widget.drag_boundary_start_pos = None
        self.parent_widget.drag_boundary_start_time = None
        self.parent_widget.drag_boundary_segments = (None, None)
        
        # End drag operation in timeline manager if we were dragging or resizing
        if was_dragging or was_resizing or was_dragging_boundary:
            self.app.timeline_manager.end_drag_operation()
            
            # If we were dragging a boundary, make sure the boundary editor is updated
            if was_dragging_boundary and self.parent_widget.selected_boundary:
                try:
                    # Force a redraw to update the boundary position
                    self.update()
                    
                    # Update the boundary editor if it exists
                    if (hasattr(self.app, 'main_window') and
                        hasattr(self.app.main_window, 'show_boundary_editor')):
                        
                        time = self.parent_widget.selected_boundary_time
                        left_segment, right_segment = self.parent_widget.selected_boundary_segments
                        
                        # Update the boundary editor with the new time
                        self.app.main_window.show_boundary_editor(
                            self.parent_widget.selected_timeline,
                            time,
                            left_segment,
                            right_segment
                        )
                except Exception as e:
                    print(f"Error updating boundary after drag: {e}")
        
        # Reset cursor
        self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def mouseDoubleClickEvent(self, event):
        """
        Handle mouse double-click events.
        
        Args:
            event: Mouse event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Get timeline at position
            timeline, y_offset = self._get_timeline_at_pos(event.pos())
            
            if timeline:
                # Get segment at position
                segment, edge, boundary_info = self._get_segment_at_pos(timeline, event.pos())
                
                if segment:
                    # Check if double-clicking on a boundary between segments
                    if boundary_info:
                        # Select the boundary on double-click
                        time, left_segment, right_segment = boundary_info
                        self.parent_widget.select_boundary(timeline, time, left_segment, right_segment)
                    else:
                        # Emit signal for regular segment double-click
                        self.parent_widget.segment_double_clicked.emit(timeline, segment)
                else:
                    # Add segment at position
                    time = event.pos().x() / (self.parent_widget.time_scale * self.parent_widget.zoom_level)
                    
                    # Save state for undo before making any changes
                    if self.app.undo_manager:
                        self.app.undo_manager.save_state("create_segment")
                    
                    # Check if there's an existing segment that contains this time
                    existing_segment = timeline.get_segment_at_time(time)
                    
                    # First modify the existing segment to end at the new segment's start time if needed
                    if existing_segment:
                        self.app.timeline_manager.modify_segment(
                            timeline=timeline,
                            segment=existing_segment,
                            end_time=time
                        )
                    
                    # Create new segment
                    # Use a shorter default duration (0.1s) for better precision
                    new_segment = self.app.timeline_manager.add_segment(
                        timeline=timeline,
                        start_time=time,
                        end_time=time + 0.1,
                        color=(255, 0, 0)  # Default to red
                    )
    
    def wheelEvent(self, event):
        """
        Handle wheel events.
        
        Args:
            event: Wheel event.
        """
        # Check if Ctrl key is pressed
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Zoom in/out
            delta = event.angleDelta().y()
            
            if delta > 0:
                # Zoom in
                self.parent_widget.zoom_in()
            else:
                # Zoom out
                self.parent_widget.zoom_out()
            
            event.accept()
        else:
            # Pass event to parent
            super().wheelEvent(event)
    
    def _show_segment_context_menu(self, timeline, segment, pos):
        """
        Show context menu for a segment.
        
        Args:
            timeline: Timeline containing the segment.
            segment: Segment to show menu for.
            pos: Position to show menu at.
        """
        # Create menu
        menu = QMenu(self)
        
        # Add actions
        cut_action = menu.addAction("Cut")
        cut_action.triggered.connect(self.parent_widget.cut_selected_segment)
        
        copy_action = menu.addAction("Copy")
        copy_action.triggered.connect(self.parent_widget.copy_selected_segment)
        
        paste_action = menu.addAction("Paste")
        paste_action.triggered.connect(self.parent_widget.paste_segment)
        paste_action.setEnabled(self.parent_widget.copied_segment is not None)
        
        menu.addSeparator()
        
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(self.parent_widget.delete_selected_segment)
        
        menu.addSeparator()
        
        # Add color submenu
        color_menu = menu.addMenu("Change Color")
        
        # Add common colors
        for color, name in [
            ((255, 0, 0), "Red"),
            ((255, 165, 0), "Orange"),
            ((255, 255, 0), "Yellow"),
            ((0, 255, 0), "Green"),
            ((0, 255, 255), "Cyan"),
            ((0, 0, 255), "Blue"),
            ((255, 0, 255), "Pink"),
            ((255, 255, 255), "White"),
            ((0, 0, 0), "Black")
        ]:
            action = color_menu.addAction(name)
            action.triggered.connect(
                lambda checked, c=color: self._change_segment_color(c)
            )
        
        # Add custom color action
        color_menu.addSeparator()
        custom_color_action = color_menu.addAction("Custom...")
        custom_color_action.triggered.connect(self._choose_custom_color)
        
        # Add effects submenu
        effects_menu = menu.addMenu("Add Effect")
        
        # Add effect types
        for effect_type in ["strobe", "fade", "pulse", "rainbow"]:
            action = effects_menu.addAction(effect_type.capitalize())
            action.triggered.connect(
                lambda checked, t=effect_type: self._add_segment_effect(t)
            )
        
        # Show menu
        menu.exec(self.mapToGlobal(pos))
    
    def _show_timeline_context_menu(self, timeline, pos):
        """
        Show context menu for a timeline.
        
        Args:
            timeline: Timeline to show menu for.
            pos: Position to show menu at.
        """
        # Create menu
        menu = QMenu(self)
        
        # Add actions
        rename_action = menu.addAction("Rename...")
        rename_action.triggered.connect(
            lambda: self._rename_timeline(timeline)
        )
        
        duplicate_action = menu.addAction("Duplicate")
        duplicate_action.triggered.connect(
            lambda: self.app.timeline_manager.duplicate_timeline(timeline)
        )
        
        menu.addSeparator()
        
        remove_action = menu.addAction("Remove")
        remove_action.triggered.connect(
            lambda: self.app.timeline_manager.remove_timeline(timeline)
        )
        
        # Show menu
        menu.exec(self.mapToGlobal(pos))
    
    def _change_segment_color(self, color):
        """
        Change the color of the selected segment.
        
        Args:
            color: New RGB color tuple.
        """
        if not self.parent_widget.selected_timeline or not self.parent_widget.selected_segment:
            return
        
        # Update segment
        self.app.timeline_manager.modify_segment(
            timeline=self.parent_widget.selected_timeline,
            segment=self.parent_widget.selected_segment,
            color=color
        )
    
    def _choose_custom_color(self):
        """Choose a custom color for the selected segment."""
        if not self.parent_widget.selected_timeline or not self.parent_widget.selected_segment:
            return
        
        # Show color dialog
        from PyQt6.QtWidgets import QColorDialog
        
        # Get current color
        current_color = QColor(*self.parent_widget.selected_segment.color)
        
        # Show dialog
        color = QColorDialog.getColor(current_color, self, "Choose Color")
        
        if color.isValid():
            # Update segment
            self.app.timeline_manager.modify_segment(
                timeline=self.parent_widget.selected_timeline,
                segment=self.parent_widget.selected_segment,
                color=(color.red(), color.green(), color.blue())
            )
    
    def _add_segment_effect(self, effect_type):
        """
        Add an effect to the selected segment.
        
        Args:
            effect_type: Type of effect to add.
        """
        if not self.parent_widget.selected_timeline or not self.parent_widget.selected_segment:
            return
        
        # Add effect
        self.app.timeline_manager.add_effect_to_segment(
            timeline=self.parent_widget.selected_timeline,
            segment=self.parent_widget.selected_segment,
            effect_type=effect_type
        )
    
    def _rename_timeline(self, timeline):
        """
        Rename a timeline.
        
        Args:
            timeline: Timeline to rename.
        """
        # Show input dialog
        from PyQt6.QtWidgets import QInputDialog
        
        # Get new name
        name, ok = QInputDialog.getText(
            self,
            "Rename Timeline",
            "Enter new name:",
            text=timeline.name
        )
        
        if ok and name:
            # Rename timeline
            self.app.timeline_manager.rename_timeline(timeline, name)
