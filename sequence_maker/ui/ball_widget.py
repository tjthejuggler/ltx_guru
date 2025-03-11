"""
Sequence Maker - Ball Widget

This module defines the BallWidget class, which displays ball visualizations.
"""

import logging
import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QScrollArea, QFrame, QSlider
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
        self.setMinimumHeight(BALL_VISUALIZATION_SIZE + 30)  # Reduced minimum height
        self.setMaximumHeight(BALL_VISUALIZATION_SIZE + 80)  # Add maximum height
        
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
        
        # Force initial creation of ball widgets
        QTimer.singleShot(100, self._create_ball_widgets)
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.main_layout.setSpacing(0)  # Remove spacing
        
        # Create ball container
        self.ball_container = QWidget()
        self.ball_layout = QHBoxLayout(self.ball_container)
        self.ball_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ball_layout.setContentsMargins(5, 5, 5, 5)  # Minimal margins
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.ball_container)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setMinimumHeight(BALL_VISUALIZATION_SIZE + 10)  # Ensure minimum height
        self.scroll_area.setMaximumHeight(BALL_VISUALIZATION_SIZE + 20)  # Limit maximum height
        self.main_layout.addWidget(self.scroll_area, 1)  # Add stretch factor
        
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
        
        # Create brightness control
        self.brightness_layout = QHBoxLayout()
        self.main_layout.addLayout(self.brightness_layout)
        
        self.brightness_label = QLabel("Brightness:")
        self.brightness_layout.addWidget(self.brightness_label)
        
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 15)  # 0-15 brightness range
        self.brightness_slider.setValue(8)  # Default to mid brightness
        self.brightness_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.brightness_slider.setTickInterval(1)
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        self.brightness_slider.setEnabled(False)  # Disabled until balls are connected
        self.brightness_layout.addWidget(self.brightness_slider)
        
        self.brightness_value_label = QLabel("8")
        self.brightness_layout.addWidget(self.brightness_value_label)
        
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
            timelines = self.app.project_manager.current_project.timelines
            
            # Log the number of timelines for debugging
            self.logger.info(f"Creating ball widgets for {len(timelines)} timelines")
            
            if not timelines:
                # If no timelines exist, create a placeholder message
                placeholder = QLabel("No timelines available. Add timelines to see ball visualizations.")
                placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.ball_layout.addWidget(placeholder)
                return
            
            for i, timeline in enumerate(timelines):
                # Create ball widget
                ball_widget = BallVisualization(self.app, i, self)
                ball_widget.clicked.connect(self._on_ball_clicked)
                
                # Add to layout
                self.ball_layout.addWidget(ball_widget)
                
                # Log the creation of each ball widget
                self.logger.info(f"Created ball widget for timeline {i}: {timeline.name}")
    
    def update_balls(self):
        """Update ball visualizations."""
        # Log update
        self.logger.debug(f"Updating {self.ball_layout.count()} ball visualizations")
        
        # Update each ball widget
        for i in range(self.ball_layout.count()):
            item = self.ball_layout.itemAt(i)
            if item.widget() and isinstance(item.widget(), BallVisualization):
                # Force update to ensure the ball is redrawn
                item.widget().update()
                self.logger.debug(f"Updated ball {i}")
                
        # Ensure the ball container is visible
        if self.ball_container.isHidden():
            self.ball_container.show()
            self.logger.debug("Made ball container visible")
    
    def _on_connect_clicked(self):
        """Handle Connect to Balls button click."""
        # Start ball discovery and show scan dialog
        self.app.ball_manager.connect_balls()
        
        # Update button state based on connected balls
        if self.app.ball_manager.balls:
            self.connect_button.setText("Connected")
            self.stream_button.setEnabled(True)
            self.brightness_slider.setEnabled(True)
            
            # Show a summary of connected balls
            self._show_connected_balls_summary()
        else:
            self.connect_button.setText("Connect to Balls")
            self.connect_button.setEnabled(True)
    
    def _show_connected_balls_summary(self):
        """Show a summary of connected balls."""
        # Get all connected balls
        connected_balls = []
        for timeline_index in range(len(self.app.project_manager.current_project.timelines)):
            ball = self.app.ball_manager.get_ball_for_timeline(timeline_index)
            if ball:
                connected_balls.append((timeline_index, ball))
        
        # If no balls are connected, don't show anything
        if not connected_balls:
            return
        
        # Create summary message
        summary = "Connected Balls:\n\n"
        for timeline_index, ball in connected_balls:
            summary += f"Timeline {timeline_index + 1}: Ball {ball.ip}\n"
        
        # Show message box
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Connected Balls", summary)
    
    def _on_brightness_changed(self, value):
        """
        Handle brightness slider value change.
        
        Args:
            value (int): New brightness value.
        """
        # Update brightness value label
        self.brightness_value_label.setText(str(value))
        
        # Send brightness to all connected balls
        for ball in self.app.ball_manager.balls.values():
            if ball.timeline_index >= 0:  # Only send to balls assigned to timelines
                self.app.ball_manager.send_brightness(ball, value)
    
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
            
            # Inform user that direct color sending is enabled
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Direct Color Mode",
                "Streaming mode disabled. Colors will now be sent directly to balls when they change in the visualization."
            )
        else:
            # Start streaming
            self.app.ball_manager.start_streaming()
            self.stream_button.setText("Stop Streaming")
            
            # Inform user that streaming mode is enabled
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Streaming Mode",
                "Streaming mode enabled. Colors will be continuously sent to balls based on the timeline position."
            )
    
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
        # Log position change
        self.logger.debug(f"Position changed to {position:.2f}s - updating balls")
        
        # Force immediate update of ball visualizations when position changes
        # This ensures balls update during playback
        self.update_balls()
    
    def _on_ball_discovered(self, ball):
        """
        Handle ball discovered signal.
        
        Args:
            ball: Discovered ball.
        """
        # Enable stream button and brightness slider
        self.stream_button.setEnabled(True)
        self.brightness_slider.setEnabled(True)
        
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
        self.logger.info(f"Ball {ball.ip} assigned to timeline {timeline_index}")
        
        # Find the ball visualization widget for this timeline
        for i in range(self.ball_layout.count()):
            item = self.ball_layout.itemAt(i)
            if item.widget() and isinstance(item.widget(), BallVisualization):
                ball_viz = item.widget()
                if ball_viz.timeline_index == timeline_index:
                    # Update the status immediately
                    ball_viz._update_status()
                    ball_viz.update()
                    break
    
    def _on_ball_unassigned(self, ball):
        """
        Handle ball unassigned signal.
        
        Args:
            ball: Unassigned ball.
        """
        self.logger.info(f"Ball {ball.ip} unassigned")
        
        # Since we don't know which timeline this ball was assigned to,
        # update all ball visualizations
        for i in range(self.ball_layout.count()):
            item = self.ball_layout.itemAt(i)
            if item.widget() and isinstance(item.widget(), BallVisualization):
                ball_viz = item.widget()
                ball_viz._update_status()
                ball_viz.update()


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
        
        # Color tracking for physical balls
        self.last_sent_color = None
        
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
        
        # Create painter with high quality rendering
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        
        # Get color at current position
        color = self._get_current_color()
        
        # Log the color for debugging
        if color:
            self.app.logger.debug(f"Ball {self.timeline_index} color: {color}")
        else:
            # If no color is defined, use a default gray
            color = (180, 180, 180)
            
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
            # Enhanced 3D effect with more pronounced highlights and shadows
            gradient.setColorAt(0.0, QColor(min(255, r + 80), min(255, g + 80), min(255, b + 80)))
            gradient.setColorAt(0.5, QColor(r, g, b))
            gradient.setColorAt(1.0, QColor(max(0, r - 80), max(0, g - 80), max(0, b - 80)))
        else:
            # Default to gray if no color, with enhanced 3D effect
            gradient.setColorAt(0.0, QColor(240, 240, 240))
            gradient.setColorAt(0.5, QColor(180, 180, 180))
            gradient.setColorAt(1.0, QColor(100, 100, 100))
        
        # Draw ball with a thin border for definition
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(60, 60, 60, 100), 1))
        painter.drawEllipse(ball_rect)
        
        # Draw highlight (more pronounced)
        highlight_rect = ball_rect.adjusted(
            int(ball_rect.width() / 5),
            int(ball_rect.height() / 5),
            -int(ball_rect.width() / 2),
            -int(ball_rect.height() / 2)
        )
        highlight_center = highlight_rect.center()
        highlight_gradient = QRadialGradient(
            highlight_center.x(), highlight_center.y(),
            highlight_rect.width() / 2
        )
        highlight_gradient.setColorAt(0.0, QColor(255, 255, 255, 220))
        highlight_gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
        
        painter.setBrush(QBrush(highlight_gradient))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
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
            # Return a default grey color if no timeline exists
            self.app.logger.debug(f"Ball {self.timeline_index}: No timeline found")
            return (120, 120, 120)  # Grey color
        
        # Get color at current position
        position = self.app.timeline_manager.position
        self.app.logger.debug(f"Ball {self.timeline_index}: Getting color at position {position}")
        
        color = timeline.get_color_at_time(position)
        self.app.logger.debug(f"Ball {self.timeline_index}: Color at position {position}: {color}")
        
        # Apply effects
        final_color = None
        if color:
            # Apply strobe effect
            if self.strobe_timer.isActive() and not self.strobe_state:
                self.app.logger.debug(f"Ball {self.timeline_index}: Applying strobe effect")
                final_color = (0, 0, 0)
            
            # Apply fade effect
            elif self.fade_timer.isActive():
                self.app.logger.debug(f"Ball {self.timeline_index}: Applying fade effect")
                # Interpolate between start and end color
                start_color = self.fade_start_color
                end_color = self.fade_end_color
                progress = self.fade_progress
                
                r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
                
                final_color = (r, g, b)
            else:
                final_color = color
            
            # Send color to physical ball if connected and color has changed
            self._send_color_to_ball(final_color)
            
            self.app.logger.debug(f"Ball {self.timeline_index}: Using color: {final_color}")
            return final_color
        else:
            # If no color is defined at the current position, use a grey color
            grey_color = (120, 120, 120)  # Grey color
            self.app.logger.debug(f"Ball {self.timeline_index}: Using default grey color: {grey_color}")
            return grey_color
    
    def _send_color_to_ball(self, color):
        """
        Send color to physical ball if connected.
        
        Args:
            color: RGB color tuple.
        """
        # Check if color has changed since last send
        if color == self.last_sent_color:
            return
            
        # Store current color as last sent
        self.last_sent_color = color
        
        # Get ball assigned to this timeline
        ball = self.app.ball_manager.get_ball_for_timeline(self.timeline_index)
        if not ball:
            return
            
        # Send color to ball directly (bypass streaming)
        self.app.ball_manager.send_color(ball, color)
    
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
            # Update the label with the ball's IP address
            self.status_label.setText(f"Connected: {ball.ip}")
            
            # Update the ball label to include the IP
            self.label.setText(f"Ball {self.timeline_index + 1} ({ball.ip})")
            
            # Set a green border to indicate connection
            self.setStyleSheet("QFrame { border: 2px solid green; border-radius: 5px; }")
        else:
            self.status_label.setText("Not connected")
            self.label.setText(f"Ball {self.timeline_index + 1}")
            self.setStyleSheet("")  # Reset style
    
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