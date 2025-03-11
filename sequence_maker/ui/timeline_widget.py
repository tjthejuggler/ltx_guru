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
        
        # Segment editing
        self.copied_segment = None
        self.dragging_segment = False
        self.resizing_segment = False
        self.resize_edge = None  # "left" or "right"
        self.drag_start_pos = None
        self.drag_start_time = None
        
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
        
        # Add timeline controls to toolbar
        self.add_timeline_button = QPushButton("Add Timeline")
        self.add_timeline_button.setToolTip("Add a new timeline")
        self.add_timeline_button.clicked.connect(self._on_add_timeline)
        self.toolbar.addWidget(self.add_timeline_button)
        
        self.remove_timeline_button = QPushButton("Remove Timeline")
        self.remove_timeline_button.setToolTip("Remove the selected timeline")
        self.remove_timeline_button.clicked.connect(self._on_remove_timeline)
        self.toolbar.addWidget(self.remove_timeline_button)
        
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
        
        # Get the total duration of the project
        duration = 0
        for timeline in self.app.project_manager.current_project.timelines:
            timeline_duration = timeline.get_duration()
            if timeline_duration > duration:
                duration = timeline_duration
        
        # Add some padding
        duration += 5.0
        
        # Calculate zoom level to fit the duration
        if duration > 0:
            viewport_width = self.scroll_area.viewport().width()
            zoom = viewport_width / (duration * self.time_scale)
            self.set_zoom(zoom)
    
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
        
        # Update position
        self.position = position
        
        # Ensure position marker is visible
        self._ensure_position_visible()
        
        # Update timeline container
        self.timeline_container.update()
        
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
        
        # Check if position is outside visible area
        if pos_x < scroll_pos or pos_x > scroll_pos + viewport_width:
            # Scroll to make position visible
            new_scroll_pos = max(0, pos_x - viewport_width / 2)
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
        self.selected_timeline = timeline
        self.selected_segment = segment
        
        # Update timeline manager
        self.app.timeline_manager.select_segment(timeline, segment)
        
        # Emit signal
        self.selection_changed.emit(timeline, segment)
        
        # Redraw
        self.timeline_container.update()
    
    def clear_selection(self):
        """Clear the current selection."""
        self.selected_timeline = None
        self.selected_segment = None
        
        # Update timeline manager
        self.app.timeline_manager.clear_selection()
        
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
        # Update position
        self.position = position
        
        # Ensure position marker is visible
        self._ensure_position_visible()
        
        # Redraw
        self.timeline_container.update()
    
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
                self.app.timeline_manager.modify_segment(
                    timeline=self.selected_timeline,
                    segment=self.selected_segment,
                    start_time=self.selected_segment.start_time - 0.1,
                    end_time=self.selected_segment.end_time - 0.1
                )
                event.accept()
                return
            
            if event.key() == Qt.Key.Key_Right:
                # Move segment right
                self.app.timeline_manager.modify_segment(
                    timeline=self.selected_timeline,
                    segment=self.selected_segment,
                    start_time=self.selected_segment.start_time + 0.1,
                    end_time=self.selected_segment.end_time + 0.1
                )
                event.accept()
                return
            
            if event.key() == Qt.Key.Key_Up:
                # Increase segment duration (extend end)
                self.app.timeline_manager.modify_segment(
                    timeline=self.selected_timeline,
                    segment=self.selected_segment,
                    end_time=self.selected_segment.end_time + 0.1
                )
                event.accept()
                return
            
            if event.key() == Qt.Key.Key_Down:
                # Decrease segment duration (shrink end)
                if self.selected_segment.end_time - self.selected_segment.start_time > 0.2:
                    self.app.timeline_manager.modify_segment(
                        timeline=self.selected_timeline,
                        segment=self.selected_segment,
                        end_time=self.selected_segment.end_time - 0.1
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
        
        # Widget properties
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
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
        
        # Set minimum size
        self.setMinimumSize(width, height)
    
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
        
        # Draw background
        painter.fillRect(event.rect(), QColor(240, 240, 240))
        
        # Draw time grid
        self._draw_time_grid(painter)
        
        # Draw timelines
        self._draw_timelines(painter)
        
        # Draw position marker
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
        else:
            # Very zoomed in - show grid every 0.01 seconds
            grid_spacing = 0.01
        
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
            if grid_spacing >= 1.0:
                time_str = f"{int(time)}s"
            else:
                time_str = f"{time:.2f}s"
            
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
            painter.drawText(int(x) + 2, 10, time_str)
            
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
                painter.setPen(QPen(QColor(0, 0, 0), 2))
            else:
                # Normal segment
                painter.setPen(QPen(QColor(0, 0, 0), 1))
            
            painter.drawRect(segment_rect)
            
            # Note: Color name labels removed as requested by user
    
    def _draw_position_marker(self, painter):
        """
        Draw the position marker.
        
        Args:
            painter: QPainter instance.
        """
        # Calculate position in pixels
        pos_x = int(self.parent_widget.position * self.parent_widget.time_scale * self.parent_widget.zoom_level)
        
        # Draw position line
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.drawLine(pos_x, 0, pos_x, self.height())
    
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
            tuple: (segment, edge) or (None, None) if no segment at position.
            edge can be "left", "right", or None.
        """
        if not timeline:
            return None, None
        
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
            
            # Check left edge
            if abs(pos.x() - start_x) <= edge_threshold:
                edge_segments.append((segment, "left", abs(pos.x() - start_x)))
            
            # Check right edge
            if abs(pos.x() - end_x) <= edge_threshold:
                edge_segments.append((segment, "right", abs(pos.x() - end_x)))
        
        # If we found edges, return the closest one
        if edge_segments:
            # Sort by distance (third element in tuple)
            edge_segments.sort(key=lambda x: x[2])
            return edge_segments[0][0], edge_segments[0][1]
        
        # If no edges found, check if position is inside any segment
        for segment in segments:
            start_x = int(segment.start_time * self.parent_widget.time_scale * self.parent_widget.zoom_level)
            end_x = int(segment.end_time * self.parent_widget.time_scale * self.parent_widget.zoom_level)
            
            # Check if position is in segment
            if start_x <= pos.x() <= end_x:
                return segment, None
        
        return None, None
    
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
                segment, edge = self._get_segment_at_pos(timeline, event.pos())
                
                if segment:
                    # Select segment
                    self.parent_widget.select_segment(timeline, segment)
                    
                    # Check if clicking on edge
                    if edge:
                        # Start resizing segment
                        self.parent_widget.resizing_segment = True
                        self.parent_widget.resize_edge = edge
                        self.parent_widget.drag_start_pos = event.pos()
                        self.parent_widget.drag_start_time = (
                            segment.start_time if edge == "left" else segment.end_time
                        )
                        
                        # Set cursor
                        self.setCursor(Qt.CursorShape.SizeHorCursor)
                    else:
                        # Start dragging segment
                        self.parent_widget.dragging_segment = True
                        self.parent_widget.drag_start_pos = event.pos()
                        self.parent_widget.drag_start_time = segment.start_time
                        
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
        if self.parent_widget.dragging_position:
            # Update position
            time = event.pos().x() / (self.parent_widget.time_scale * self.parent_widget.zoom_level)
            self.parent_widget.set_position(time)
        
        elif self.parent_widget.dragging_segment:
            # Calculate time difference
            time_diff = (
                event.pos().x() - self.parent_widget.drag_start_pos.x()
            ) / (self.parent_widget.time_scale * self.parent_widget.zoom_level)
            
            # Calculate new start and end times
            new_start_time = self.parent_widget.drag_start_time + time_diff
            new_end_time = self.parent_widget.selected_segment.end_time + time_diff
            
            # Ensure start time is not negative
            if new_start_time < 0:
                time_diff -= new_start_time
                new_start_time = 0
                new_end_time = self.parent_widget.selected_segment.end_time + time_diff
            
            # Update segment
            self.app.timeline_manager.modify_segment(
                timeline=self.parent_widget.selected_timeline,
                segment=self.parent_widget.selected_segment,
                start_time=new_start_time,
                end_time=new_end_time
            )
        
        elif self.parent_widget.resizing_segment:
            # Calculate time difference
            time_diff = (
                event.pos().x() - self.parent_widget.drag_start_pos.x()
            ) / (self.parent_widget.time_scale * self.parent_widget.zoom_level)
            
            # Calculate new time
            new_time = self.parent_widget.drag_start_time + time_diff
            
            # Ensure time is not negative
            if new_time < 0:
                new_time = 0
            
            # Update segment
            if self.parent_widget.resize_edge == "left":
                # Ensure start time is less than end time
                if new_time < self.parent_widget.selected_segment.end_time:
                    # Find any segments that end exactly where this segment starts
                    adjacent_segment = None
                    for segment in self.parent_widget.selected_timeline.segments:
                        if segment != self.parent_widget.selected_segment and abs(segment.end_time - self.parent_widget.selected_segment.start_time) < 0.001:
                            adjacent_segment = segment
                            break
                    
                    # Save state for undo before making any changes
                    if adjacent_segment and self.app.undo_manager:
                        self.app.undo_manager.save_state("resize_segments")
                    
                    # Update the selected segment
                    self.app.timeline_manager.modify_segment(
                        timeline=self.parent_widget.selected_timeline,
                        segment=self.parent_widget.selected_segment,
                        start_time=new_time
                    )
                    
                    # Also update the adjacent segment if it exists
                    if adjacent_segment:
                        self.app.timeline_manager.modify_segment(
                            timeline=self.parent_widget.selected_timeline,
                            segment=adjacent_segment,
                            end_time=new_time
                        )
            else:  # right edge
                # Ensure end time is greater than start time
                if new_time > self.parent_widget.selected_segment.start_time:
                    # Find any segments that start exactly where this segment ends
                    adjacent_segment = None
                    for segment in self.parent_widget.selected_timeline.segments:
                        if segment != self.parent_widget.selected_segment and abs(segment.start_time - self.parent_widget.selected_segment.end_time) < 0.001:
                            adjacent_segment = segment
                            break
                    
                    # Save state for undo before making any changes
                    if adjacent_segment and self.app.undo_manager:
                        self.app.undo_manager.save_state("resize_segments")
                    
                    # Update the selected segment
                    self.app.timeline_manager.modify_segment(
                        timeline=self.parent_widget.selected_timeline,
                        segment=self.parent_widget.selected_segment,
                        end_time=new_time
                    )
                    
                    # Also update the adjacent segment if it exists
                    if adjacent_segment:
                        self.app.timeline_manager.modify_segment(
                            timeline=self.parent_widget.selected_timeline,
                            segment=adjacent_segment,
                            start_time=new_time
                        )
        
        else:
            # Update cursor based on mouse position
            timeline, y_offset = self._get_timeline_at_pos(event.pos())
            
            if timeline:
                segment, edge = self._get_segment_at_pos(timeline, event.pos())
                
                if segment:
                    if edge:
                        # Mouse over segment edge
                        self.setCursor(Qt.CursorShape.SizeHorCursor)
                    else:
                        # Mouse over segment
                        self.setCursor(Qt.CursorShape.OpenHandCursor)
                else:
                    # Mouse over timeline
                    self.setCursor(Qt.CursorShape.ArrowCursor)
            else:
                # Mouse not over timeline
                self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events.
        
        Args:
            event: Mouse event.
        """
        # Reset dragging flags
        self.parent_widget.dragging_position = False
        self.parent_widget.dragging_segment = False
        self.parent_widget.resizing_segment = False
        
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
                segment, edge = self._get_segment_at_pos(timeline, event.pos())
                
                if segment:
                    # Emit signal
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
                    new_segment = self.app.timeline_manager.add_segment(
                        timeline=timeline,
                        start_time=time,
                        end_time=time + 1.0,
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