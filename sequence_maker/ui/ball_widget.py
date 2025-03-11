"""
Sequence Maker - Ball Widget

This module defines the BallWidget class, which displays ball visualizations.
"""

import logging
import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient

from app.constants import BALL_VISUALIZATION_SIZE


class BallWidget(QWidget):
    """
    Widget for displaying ball visualizations.
    
    Signals:
        ball_clicked: Emitted when a ball is clicked.
    """
    
    # Signals
    ball_clicked = pyqtSignal(int)  # timeline_index
    
    def __init__(self, app, parent=None):
        """
        Initialize the ball widget.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.BallWidget")
        self.app = app
        
        # Widget properties
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        # Ball properties
        self.ball_size = BALL_VISUALIZATION_SIZE
        self.ball_spacing = 20
        
        # Create UI
        self._create_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Start update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_balls)
        self.update_timer.start(50)  # 20 FPS
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create title label
        self.title_label = QLabel("Ball Visualization")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.title_label)
        
        # Create ball container
        self.ball_container = QWidget()
        self.ball_layout = QHBoxLayout(self.ball_container)
        self.ball_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.ball_container)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.scroll_area)
        
        # Create control buttons
        self.control_layout = QHBoxLayout()
        self.main_layout.addLayout(self.control_layout)
        
        self.connect_button = QPushButton("Connect to Balls")
        self.connect_button.clicked.connect(self._on_connect_clicked)
        self.control_layout.addWidget(self.connect_button)
        
        self.stream_button = QPushButton("Stream Colors")
        self.stream_button.clicked.connect(self._on_stream_clicked)
        self.stream_button.setEnabled(False)
        self.control_layout.addWidget(self.stream_button)
        
        # Create ball widgets
        self._create_ball_widgets()
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Connect timeline manager signals
        self.app.timeline_manager.timeline_added.connect(self._on_timeline_added)
        self.app.timeline_manager.timeline_removed.connect(self._on_timeline_removed)
        self.app.timeline_manager.position_changed.connect(self._on_position_changed)
        
        # Connect ball manager signals
        self.app.ball_manager.ball_discovered.connect(self._on_ball_discovered)
        self.app.ball_manager.ball_lost.connect(self._on_ball_lost)
        self.app.ball_manager.ball_assigned.connect(self._on_ball_assigned)
        self.app.ball_manager.ball_unassigned.connect(self._on_ball_unassigned)
    
    def _create_ball_widgets(self):
        """Create ball widgets for each timeline."""
        # Clear existing ball widgets
        for i in reversed(range(self.ball_layout.count())):
            item = self.ball_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # Create ball widgets for each timeline
        if self.app.project_manager.current_project:
            for i, timeline in enumerate(self.app.project_manager.current_project.timelines):
                # Create ball widget
                ball_widget = BallVisualization(self.app, i, self)
                ball_widget.clicked.connect(self._on_ball_clicked)
                
                # Add to layout
                self.ball_layout.addWidget(ball_widget)
    
    def update_balls(self):
        """Update ball visualizations."""
        # Update each ball widget
        for i in range(self.ball_layout.count()):
            item = self.ball_layout.itemAt(i)
            if item.widget():
                item.widget().update()
    
    def _on_connect_clicked(self):
        """Handle Connect to Balls button click."""
        # Start ball discovery
        self.app.ball_manager.connect_balls()
        
        # Update button
        self.connect_button.setText("Connecting...")
        self.connect_button.setEnabled(False)
        
        # Enable stream button after a delay
        QTimer.singleShot(2000, self._enable_stream_button)
    
    def _enable_stream_button(self):
        """Enable the Stream Colors button."""
        self.connect_button.setText("Connected")
        self.stream_button.setEnabled(True)
    
    def _on_stream_clicked(self):
        """Handle Stream Colors button click."""
        # Check if already streaming
        if self.app.ball_manager.streaming:
            # Stop streaming
            self.app.ball_manager.stop_streaming()
            self.stream_button.setText("Stream Colors")
        else:
            # Start streaming
            self.app.ball_manager.start_streaming()
            self.stream_button.setText("Stop Streaming")
    
    def _on_ball_clicked(self, timeline_index):
        """
        Handle ball click.
        
        Args:
            timeline_index (int): Index of the timeline.
        """
        # Emit signal
        self.ball_clicked.emit(timeline_index)
    
    def _on_timeline_added(self, timeline):
        """
        Handle timeline added signal.
        
        Args:
            timeline: Added timeline.
        """
        # Recreate ball widgets
        self._create_ball_widgets()
    
    def _on_timeline_removed(self, timeline):
        """
        Handle timeline removed signal.
        
        Args:
            timeline: Removed timeline.
        """
        # Recreate ball widgets
        self._create_ball_widgets()
    
    def _on_position_changed(self, position):
        """
        Handle position changed signal.
        
        Args:
            position (float): New position in seconds.
        """
        # Update is handled by the update timer
        pass
    
    def _on_ball_discovered(self, ball):
        """
        Handle ball discovered signal.
        
        Args:
            ball: Discovered ball.
        """
        # Enable stream button
        self.stream_button.setEnabled(True)
        
        # Update connect button
        self.connect_button.setText("Connected")
    
    def _on_ball_lost(self, ball):
        """
        Handle ball lost signal.
        
        Args:
            ball: Lost ball.
        """
        # Update is handled by the update timer
        pass
    
    def _on_ball_assigned(self, ball, timeline_index):
        """
        Handle ball assigned signal.
        
        Args:
            ball: Assigned ball.
            timeline_index (int): Timeline index.
        """
        # Update is handled by the update timer
        pass
    
    def _on_ball_unassigned(self, ball):
        """
        Handle ball unassigned signal.
        
        Args:
            ball: Unassigned ball.
        """
        # Update is handled by the update timer
        pass


class BallVisualization(QFrame):
    """
    Widget for visualizing a ball.
    
    Signals:
        clicked: Emitted when the ball is clicked.
    """
    
    # Signals
    clicked = pyqtSignal(int)  # timeline_index
    
    def __init__(self, app, timeline_index, parent=None):
        """
        Initialize the ball visualization.
        
        Args:
            app: The main application instance.
            timeline_index (int): Index of the timeline.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.app = app
        self.timeline_index = timeline_index
        
        # Widget properties
        self.setFrameShape(QFrame.Shape.Box)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setFixedSize(BALL_VISUALIZATION_SIZE + 20, BALL_VISUALIZATION_SIZE + 40)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create label
        self.label = QLabel(f"Ball {timeline_index + 1}")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)
        
        # Create status label
        self.status_label = QLabel("Not connected")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)
        
        # Effect properties
        self.strobe_state = False
        self.strobe_timer = QTimer(self)
        self.strobe_timer.timeout.connect(self._toggle_strobe)
        
        self.fade_progress = 0.0
        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self._update_fade)
        
        # Update status
        self._update_status()
    
    def sizeHint(self):
        """Get the preferred size of the widget."""
        return QSize(BALL_VISUALIZATION_SIZE + 20, BALL_VISUALIZATION_SIZE + 40)
    
    def paintEvent(self, event):
        """
        Paint the widget.
        
        Args:
            event: Paint event.
        """
        # Call parent paint event
        super().paintEvent(event)
        
        # Create painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get color at current position
        color = self._get_current_color()
        
        # Draw ball
        self._draw_ball(painter, color)
    
    def _draw_ball(self, painter, color):
        """
        Draw the ball.
        
        Args:
            painter: QPainter instance.
            color: RGB color tuple.
        """
        # Calculate ball rect
        ball_rect = self.rect().adjusted(10, 20, -10, -20)
        
        # Create gradient
        center = ball_rect.center()
        gradient = QRadialGradient(
            center.x(), center.y(),
            ball_rect.width() / 2
        )
        
        # Set gradient colors
        if color:
            r, g, b = color
            gradient.setColorAt(0.0, QColor(min(255, r + 50), min(255, g + 50), min(255, b + 50)))
            gradient.setColorAt(0.7, QColor(r, g, b))
            gradient.setColorAt(1.0, QColor(max(0, r - 50), max(0, g - 50), max(0, b - 50)))
        else:
            # Default to gray if no color
            gradient.setColorAt(0.0, QColor(220, 220, 220))
            gradient.setColorAt(0.7, QColor(180, 180, 180))
            gradient.setColorAt(1.0, QColor(120, 120, 120))
        
        # Draw ball
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawEllipse(ball_rect)
        
        # Draw highlight
        highlight_rect = ball_rect.adjusted(int(ball_rect.width() / 4), int(ball_rect.height() / 4), -int(ball_rect.width() / 2), -int(ball_rect.height() / 2))
        highlight_center = highlight_rect.center()
        highlight_gradient = QRadialGradient(
            highlight_center.x(), highlight_center.y(),
            highlight_rect.width() / 2
        )
        highlight_gradient.setColorAt(0.0, QColor(255, 255, 255, 180))
        highlight_gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
        
        painter.setBrush(QBrush(highlight_gradient))
        painter.drawEllipse(highlight_rect)
    
    def _get_current_color(self):
        """
        Get the color at the current position.
        
        Returns:
            tuple: RGB color tuple, or None if no color is defined.
        """
        # Get timeline
        timeline = self._get_timeline()
        if not timeline:
            return None
        
        # Get color at current position
        position = self.app.timeline_manager.position
        color = timeline.get_color_at_time(position)
        
        # Apply effects
        if color:
            # Apply strobe effect
            if self.strobe_timer.isActive() and not self.strobe_state:
                return (0, 0, 0)
            
            # Apply fade effect
            if self.fade_timer.isActive():
                # Interpolate between start and end color
                start_color = self.fade_start_color
                end_color = self.fade_end_color
                progress = self.fade_progress
                
                r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
                
                return (r, g, b)
        
        return color
    
    def _get_timeline(self):
        """
        Get the timeline for this ball.
        
        Returns:
            Timeline: Timeline object, or None if not found.
        """
        if not self.app.project_manager.current_project:
            return None
        
        timelines = self.app.project_manager.current_project.timelines
        if 0 <= self.timeline_index < len(timelines):
            return timelines[self.timeline_index]
        
        return None
    
    def _update_status(self):
        """Update the status label."""
        # Check if a ball is assigned to this timeline
        ball = self.app.ball_manager.get_ball_for_timeline(self.timeline_index)
        
        if ball:
            self.status_label.setText(f"Connected: {ball.ip}")
        else:
            self.status_label.setText("Not connected")
    
    def _toggle_strobe(self):
        """Toggle the strobe state."""
        self.strobe_state = not self.strobe_state
        self.update()
    
    def _update_fade(self):
        """Update the fade progress."""
        self.fade_progress += 0.05
        
        if self.fade_progress >= 1.0:
            self.fade_timer.stop()
            self.fade_progress = 0.0
        
        self.update()
    
    def start_strobe_effect(self, frequency=10):
        """
        Start the strobe effect.
        
        Args:
            frequency (int, optional): Strobe frequency in Hz. Defaults to 10.
        """
        # Stop any active effects
        self.stop_effects()
        
        # Start strobe timer
        self.strobe_timer.start(int(1000 / (frequency * 2)))
    
    def start_fade_effect(self, start_color, end_color, duration=1.0):
        """
        Start the fade effect.
        
        Args:
            start_color: RGB start color tuple.
            end_color: RGB end color tuple.
            duration (float, optional): Fade duration in seconds. Defaults to 1.0.
        """
        # Stop any active effects
        self.stop_effects()
        
        # Set fade properties
        self.fade_start_color = start_color
        self.fade_end_color = end_color
        self.fade_progress = 0.0
        
        # Calculate timer interval
        steps = 20
        interval = int(duration * 1000 / steps)
        
        # Start fade timer
        self.fade_timer.start(interval)
    
    def stop_effects(self):
        """Stop all active effects."""
        self.strobe_timer.stop()
        self.fade_timer.stop()
        self.strobe_state = False
        self.fade_progress = 0.0
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events.
        
        Args:
            event: Mouse event.
        """
        # Emit clicked signal
        self.clicked.emit(self.timeline_index)
        
        # Call parent event handler
        super().mousePressEvent(event)