"""
Sequence Maker - Audio Widget

This module defines the AudioWidget class, which displays audio visualizations and controls.
"""

import logging
import os
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSlider, QComboBox, QCheckBox, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient


class AudioWidget(QWidget):
    """
    Widget for displaying audio visualizations and controls.
    
    Signals:
        play_clicked: Emitted when the play button is clicked.
        pause_clicked: Emitted when the pause button is clicked.
        stop_clicked: Emitted when the stop button is clicked.
        position_changed: Emitted when the position slider is moved.
        volume_changed: Emitted when the volume slider is moved.
    """
    
    # Signals
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    position_changed = pyqtSignal(float)
    volume_changed = pyqtSignal(float)
    
    def __init__(self, app, parent=None):
        """
        Initialize the audio widget.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.AudioWidget")
        self.app = app
        
        # Widget properties
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        # Audio properties
        self.audio_file = None
        self.duration = 0
        self.position = 0
        self.playing = False
        self.volume = self.app.config.get("audio", "volume")
        
        # Visualization properties
        self.visualization_type = "waveform"
        self.visualization_height = 200
        self.waveform_color = self.app.config.get("audio", "waveform_color")
        self.beats_color = self.app.config.get("audio", "beats_color")
        
        # Create UI
        self._create_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Start update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_visualization)
        self.update_timer.start(50)  # 20 FPS
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(2)
        
        # Create top control layout
        self.top_layout = QHBoxLayout()
        self.top_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.addLayout(self.top_layout)
        
        # Create title label
        self.title_label = QLabel("Audio Visualization")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.top_layout.addWidget(self.title_label)
        
        # Create visualization type combo box
        self.visualization_combo = QComboBox()
        self.visualization_combo.addItems(["Waveform", "Spectrum", "Beats", "Energy"])
        self.visualization_combo.setCurrentText("Waveform")
        self.visualization_combo.currentTextChanged.connect(self._on_visualization_changed)
        self.top_layout.addWidget(self.visualization_combo)
        
        # Create load audio button
        self.load_button = QPushButton("Load Audio")
        self.load_button.setMaximumWidth(100)
        self.load_button.clicked.connect(self._on_load_clicked)
        self.top_layout.addWidget(self.load_button)
        
        # Create process lyrics button
        self.process_lyrics_button = QPushButton("Process Lyrics")
        self.process_lyrics_button.setMaximumWidth(100)
        self.process_lyrics_button.setToolTip("Process audio to extract and align lyrics")
        self.process_lyrics_button.clicked.connect(self._on_process_lyrics_clicked)
        self.top_layout.addWidget(self.process_lyrics_button)
        
        # Create playback controls
        self.play_button = QPushButton("▶")
        self.play_button.setMaximumWidth(30)
        self.play_button.clicked.connect(self._on_play_clicked)
        self.top_layout.addWidget(self.play_button)
        
        self.pause_button = QPushButton("⏸")
        self.pause_button.setMaximumWidth(30)
        self.pause_button.clicked.connect(self._on_pause_clicked)
        self.pause_button.setEnabled(False)
        self.top_layout.addWidget(self.pause_button)
        
        self.stop_button = QPushButton("⏹")
        self.stop_button.setMaximumWidth(30)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.stop_button.setEnabled(False)
        self.top_layout.addWidget(self.stop_button)
        
        # Create position label
        self.position_label = QLabel("0:00 / 0:00")
        self.position_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.top_layout.addWidget(self.position_label)
        
        # Create visualization widget
        self.visualization = AudioVisualization(self.app, self)
        self.visualization.setMinimumHeight(80)
        self.visualization.setMaximumHeight(120)
        self.main_layout.addWidget(self.visualization)
        
        # Position slider removed as per user request - we'll use the red position marker instead
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Connect audio manager signals
        self.app.audio_manager.audio_loaded.connect(self._on_audio_loaded)
        self.app.audio_manager.audio_started.connect(self._on_audio_started)
        self.app.audio_manager.audio_paused.connect(self._on_audio_paused)
        self.app.audio_manager.audio_stopped.connect(self._on_audio_stopped)
        self.app.audio_manager.position_changed.connect(self._on_position_changed)
        self.app.audio_manager.analysis_completed.connect(self._on_analysis_completed)
        
        # Connect timeline manager signals to ensure position sync with ball timelines
        self.app.timeline_manager.position_changed.connect(self._on_position_changed)
    
    def update_visualization(self):
        """Update the audio visualization."""
        # Update visualization widget
        self.visualization.update()
    
    def _on_load_clicked(self):
        """Handle Load Audio button click."""
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Audio",
            "",
            "Audio Files (*.mp3 *.wav *.ogg)"
        )
        
        if file_path:
            # Load audio
            self.app.audio_manager.load_audio(file_path)
    
    def _on_process_lyrics_clicked(self):
        """Handle Process Lyrics button click."""
        # Check if audio is loaded
        if not self.app.audio_manager.audio_file:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "No Audio Loaded",
                "Please load an audio file before processing lyrics."
            )
            return
        
        # Check if lyrics manager exists
        if not hasattr(self.app, 'lyrics_manager'):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Lyrics Manager Not Found",
                "The lyrics manager is not available."
            )
            return
        
        # Process audio to extract and align lyrics
        self.app.lyrics_manager.process_audio(self.app.audio_manager.audio_file)
    
    def _on_play_clicked(self):
        """Handle Play button click."""
        # Start playback
        self.app.audio_manager.play()
        
        # Emit signal
        self.play_clicked.emit()
    
    def _on_pause_clicked(self):
        """Handle Pause button click."""
        # Pause playback
        self.app.audio_manager.pause()
        
        # Emit signal
        self.pause_clicked.emit()
    
    def _on_stop_clicked(self):
        """Handle Stop button click."""
        # Stop playback
        self.app.audio_manager.stop()
        
        # Emit signal
        self.stop_clicked.emit()
    
    # Position slider methods removed as the slider has been removed
    
    def _on_volume_changed(self, value):
        """
        Handle volume slider changed.
        
        Args:
            value (int): Slider value (0-100).
        """
        # Calculate volume
        volume = value / 100.0
        
        # Set volume
        self.volume = volume
        self.app.audio_manager.set_volume(volume)
        
        # Emit signal
        self.volume_changed.emit(volume)
    
    def _on_visualization_changed(self, text):
        """
        Handle visualization type changed.
        
        Args:
            text (str): Visualization type.
        """
        # Update visualization type
        self.visualization_type = text.lower()
        
        # Update visualization
        self.visualization.update()
    def _on_audio_loaded(self, file_path, duration):
        """
        Handle audio loaded signal.
        
        Args:
            file_path (str): Path to the audio file.
            duration (float): Duration of the audio in seconds.
        """
        # Update audio properties
        self.audio_file = file_path
        self.duration = duration
        
        # Update UI
        self.title_label.setText(f"Audio: {os.path.basename(file_path)}")
        self.play_button.setEnabled(True)
        
        # Update position label
        self._update_position_label(0)
        self._update_position_label(0)
    
    def _on_audio_started(self):
        """Handle audio started signal."""
        # Update UI
        self.playing = True
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
    
    def _on_audio_paused(self):
        """Handle audio paused signal."""
        # Update UI
        self.playing = False
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(True)
    
    def _on_audio_stopped(self):
        """Handle audio stopped signal."""
        # Update UI
        self.playing = False
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        # Reset position
        self.position = 0
        
        # Update position label
        self._update_position_label(0)
    
    def _on_position_changed(self, position):
        """
        Handle position changed signal.
        
        Args:
            position (float): New position in seconds.
        """
        # Update position
        self.position = position
        
        # Update position label
        self._update_position_label(position)
    
    def _on_analysis_completed(self, analysis_data):
        """
        Handle analysis completed signal.
        
        Args:
            analysis_data (dict): Analysis data.
        """
        # Update visualization
        self.visualization.set_analysis_data(analysis_data)
    
    def _update_position_label(self, position):
        """
        Update the position label.
        
        Args:
            position (float): Position in seconds.
        """
        # Format position and duration
        position_str = self._format_time(position)
        duration_str = self._format_time(self.duration)
        
        # Update label
        self.position_label.setText(f"{position_str} / {duration_str}")
    
    def _format_time(self, seconds):
        """
        Format time in seconds to MM:SS format.
        
        Args:
            seconds (float): Time in seconds.
        
        Returns:
            str: Formatted time string.
        """
        minutes = int(seconds / 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"

    def set_horizontal_scroll_offset(self, offset: int):
        """Set the horizontal scroll offset for the visualization."""
        if hasattr(self, 'visualization'):
            self.visualization.horizontal_scroll_offset = offset
            self.visualization.update()


class AudioVisualization(QWidget):
    """Widget for displaying audio visualizations."""
    
    def __init__(self, app, parent=None):
        """
        Initialize the audio visualization.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.app = app
        self.parent_widget = parent
        
        # Widget properties
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(100)
        
        # Enable mouse tracking for hover events
        self.setMouseTracking(True)
        
        # Analysis data
        self.analysis_data = None
        
        # Dragging state
        self.dragging_position = False
        
        # Horizontal scroll offset
        self.horizontal_scroll_offset = 0
    
    def set_analysis_data(self, analysis_data):
        """
        Set the analysis data.
        
        Args:
            analysis_data (dict): Analysis data.
        """
        self.analysis_data = analysis_data
        self.update()
    
    def paintEvent(self, event):
        """
        Paint the widget.
        
        Args:
            event: Paint event.
        """
        # Create painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(event.rect(), QColor(240, 240, 240))
        
        # Draw visualization
        visualization_type = self.parent_widget.visualization_type
        
        if visualization_type == "waveform":
            self._draw_waveform(painter)
        elif visualization_type == "spectrum":
            self._draw_spectrum(painter)
        elif visualization_type == "beats":
            self._draw_beats(painter)
        elif visualization_type == "energy":
            self._draw_energy(painter)
        
        # Draw position marker
        self._draw_position_marker(painter)
    
    def _draw_waveform(self, painter):
        """
        Draw the waveform visualization.
        
        Args:
            painter: QPainter instance.
        """
        if not self.analysis_data or "waveform" not in self.analysis_data:
            # Draw placeholder
            self._draw_placeholder(painter, "No waveform data available")
            return
        
        # Get waveform data
        waveform = self.analysis_data["waveform"]
        
        # Calculate scaling factors
        width = self.width()
        height = self.height()
        center_y = height / 2
        
        # Get timeline zoom level and time scale
        timeline_widget = self.app.main_window.timeline_widget
        zoom_level = timeline_widget.zoom_level
        time_scale = timeline_widget.time_scale
        
        # Set pen
        r, g, b = self.parent_widget.waveform_color
        painter.setPen(QPen(QColor(r, g, b), 1))
        
        # Draw waveform
        if len(waveform) > 0:
            # Calculate visible time range
            duration = self.parent_widget.duration
            if duration > 0:
                # Calculate pixels per second with zoom
                pixels_per_second = time_scale * zoom_level
                
                # Draw waveform based on time scale
                for i in range(width):
                    # Convert pixel position to time, considering scroll offset
                    time_pos = (i + self.horizontal_scroll_offset) / pixels_per_second
                    if time_pos >= duration:
                        # No need to draw beyond the duration
                        pass # Continue to allow drawing the rest of the visible area if scrolled past the end
                    
                    # Get waveform value at time position
                    # Clamp sample_index to avoid going out of bounds
                    sample_index = min(max(0, int(time_pos * len(waveform) / duration)), len(waveform) -1)

                    if sample_index < len(waveform): # Check should be redundant due to clamping but good for safety
                        value = waveform[sample_index]
                        
                        # Draw vertical line for waveform value
                        y1 = center_y - value * center_y * 0.9
                        y2 = center_y + value * center_y * 0.9
                        # Convert numpy.float32 values to integers
                        painter.drawLine(i, int(y1), i, int(y2))
    
    def _draw_spectrum(self, painter):
        """
        Draw the spectrum visualization.
        
        Args:
            painter: QPainter instance.
        """
        if not self.analysis_data or "spectrum" not in self.analysis_data:
            # Draw placeholder
            self._draw_placeholder(painter, "No spectrum data available")
            return
        
        # Get spectrum data
        spectrum = self.analysis_data["spectrum"]
        
        # Calculate scaling factors
        width = self.width()
        height = self.height()
        
        # Draw spectrum
        if spectrum.size > 0:
            # Get current position
            position = self.app.timeline_manager.position
            
            # Get spectrum at current position
            spectrum_at_time = self.app.audio_manager.get_spectrum_at_time(
                position, width, height
            )
            
            if spectrum_at_time is not None:
                # Create gradient
                gradient = QLinearGradient(0, 0, 0, height)
                gradient.setColorAt(0.0, QColor(255, 0, 0))
                gradient.setColorAt(0.5, QColor(255, 255, 0))
                gradient.setColorAt(1.0, QColor(0, 255, 0))
                
                # Draw spectrum
                for i in range(min(width, spectrum_at_time.shape[1])):
                    # Calculate column height
                    col_height = int(np.sum(spectrum_at_time[:, i]) / spectrum_at_time.shape[0])
                    
                    # Draw column
                    painter.fillRect(
                        i, height - col_height, 1, col_height,
                        gradient
                    )
    
    def _draw_beats(self, painter):
        """
        Draw the beats visualization.
        
        Args:
            painter: QPainter instance.
        """
        if not self.analysis_data or "beat_times" not in self.analysis_data:
            # Draw placeholder
            self._draw_placeholder(painter, "No beat data available")
            return
        
        # Get beat data
        beat_times = self.analysis_data["beat_times"]
        
        # Calculate scaling factors
        width = self.width()
        height = self.height()
        
        # Get timeline zoom level and time scale
        timeline_widget = self.app.main_window.timeline_widget
        zoom_level = timeline_widget.zoom_level
        time_scale = timeline_widget.time_scale
        
        # Set pen
        r, g, b = self.parent_widget.beats_color
        painter.setPen(QPen(QColor(r, g, b), 2))
        
        # Draw beats
        if len(beat_times) > 0:
            # Calculate pixels per second with zoom
            pixels_per_second = time_scale * zoom_level
            
            # Draw beat lines
            for beat_time in beat_times:
                x = int(beat_time * pixels_per_second) - self.horizontal_scroll_offset
                if 0 <= x < width:
                    painter.drawLine(x, 0, x, height)
    
    def _draw_energy(self, painter):
        """
        Draw the energy visualization.
        
        Args:
            painter: QPainter instance.
        """
        if not self.analysis_data or "beats" not in self.analysis_data:
            # Draw placeholder
            self._draw_placeholder(painter, "No energy data available")
            return
        
        # Get energy data (using beats as energy)
        energy = self.analysis_data["beats"]
        
        # Calculate scaling factors
        width = self.width()
        height = self.height()
        
        # Set brush
        painter.setBrush(QBrush(QColor(0, 128, 255)))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        
        # Draw energy
        if len(energy) > 0:
            # Downsample energy to match width
            if len(energy) > width:
                # Calculate downsampling factor
                factor = len(energy) / width
                
                # Downsample by taking max in each bin
                downsampled = []
                for i in range(width):
                    start = int(i * factor)
                    end = int((i + 1) * factor)
                    if start < len(energy) and end <= len(energy):
                        segment = energy[start:end]
                        if len(segment) > 0:
                            downsampled.append(max(segment))
                
                # Draw downsampled energy
                for i, value in enumerate(downsampled):
                    x = i
                    bar_height = int(value * height * 0.9)
                    painter.drawRect(x, height - bar_height, 1, bar_height)
            else:
                # Draw full energy
                for i, value in enumerate(energy):
                    x = int(i * width / len(energy))
                    bar_height = int(value * height * 0.9)
                    painter.drawRect(x, height - bar_height, 1, bar_height)
    
    def _draw_position_marker(self, painter):
        """
        Draw the position marker.
        
        Args:
            painter: QPainter instance.
        """
        # Get position
        position = self.parent_widget.position
        
        # Get timeline zoom level and time scale
        timeline_widget = self.app.main_window.timeline_widget
        zoom_level = timeline_widget.zoom_level
        time_scale = timeline_widget.time_scale
        
        # Calculate position in pixels using timeline's scale and adjust for scroll
        pos_x = int(position * time_scale * zoom_level) - self.horizontal_scroll_offset
        
        # Create a semi-transparent red color for the line to match timeline marker
        line_color = QColor(255, 0, 0, 200)  # Added alpha channel (200/255 opacity)
        
        # Draw position line with a more visible style
        painter.setPen(QPen(line_color, 3))  # Increased width for better visibility
        painter.drawLine(pos_x, 0, pos_x, self.height())
        
        # Draw a small circle at the top of the line for better visibility
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.drawEllipse(pos_x - 4, 0, 8, 8)
    
    def _draw_placeholder(self, painter, text):
        """
        Draw a placeholder message.
        
        Args:
            painter: QPainter instance.
            text (str): Placeholder text.
        """
        # Set pen
        painter.setPen(QPen(QColor(128, 128, 128), 1))
        
        # Draw text
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            text
        )
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move events for dragging and cursor changes.
        
        Args:
            event: Mouse event.
        """
        if self.dragging_position:
            # Get timeline zoom level and time scale
            timeline_widget = self.app.main_window.timeline_widget
            zoom_level = timeline_widget.zoom_level
            time_scale = timeline_widget.time_scale
            
            # Calculate time position from mouse x-coordinate
            time = event.pos().x() / (time_scale * zoom_level)
            
            # Clamp time to valid range
            if time < 0:
                time = 0
                
            # Get duration from audio manager to avoid attribute errors
            audio_duration = self.app.audio_manager.duration if hasattr(self.app, 'audio_manager') else 0
            if audio_duration > 0 and time > audio_duration:
                time = audio_duration
            
            # Update cursor hover position in main window
            if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'update_cursor_hover_position'):
                self.app.main_window.update_cursor_hover_position(time)
            
            # Set position in timeline manager (this will update all linked components)
            self.app.timeline_manager.set_position(time)
            
            # Also seek the audio to this position
            self.app.audio_manager.seek(time)
            
            # Set cursor to indicate dragging
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        else:
            # Calculate time position from mouse x-coordinate
            timeline_widget = self.app.main_window.timeline_widget
            zoom_level = timeline_widget.zoom_level
            time_scale = timeline_widget.time_scale
            
            time = event.pos().x() / (time_scale * zoom_level)
            
            # Clamp time to valid range
            if time < 0:
                time = 0
                
            # Get duration from audio manager to avoid attribute errors
            audio_duration = self.app.audio_manager.duration if hasattr(self.app, 'audio_manager') else 0
            if audio_duration > 0 and time > audio_duration:
                time = audio_duration
                
            # Update cursor hover position in main window
            if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'update_cursor_hover_position'):
                self.app.main_window.update_cursor_hover_position(time)
                
            # Change cursor to indicate the visualization is clickable
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Accept the event
        event.accept()
    
    def leaveEvent(self, event):
        """
        Handle mouse leave events.
        
        Args:
            event: Leave event.
        """
        # Clear cursor hover position when mouse leaves the widget
        if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'clear_cursor_hover_position'):
            self.app.main_window.clear_cursor_hover_position()
        
        # Reset cursor
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
        # Call parent implementation
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events to set the position when clicked.
        
        Args:
            event: Mouse event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Get timeline zoom level and time scale
            timeline_widget = self.app.main_window.timeline_widget
            zoom_level = timeline_widget.zoom_level
            time_scale = timeline_widget.time_scale
            
            # Calculate time position from click x-coordinate
            time = event.pos().x() / (time_scale * zoom_level)
            
            # Clamp time to valid range
            if time < 0:
                time = 0
            if self.parent_widget.duration > 0 and time > self.parent_widget.duration:
                time = self.parent_widget.duration
            
            # Set position in timeline manager (this will update all linked components)
            self.app.timeline_manager.set_position(time)
            
            # Also seek the audio to this position
            self.app.audio_manager.seek(time)
            
            # Start dragging
            self.dragging_position = True
            
            # Accept the event
            event.accept()
        else:
            # Pass other buttons to parent
            super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events to end dragging.
        
        Args:
            event: Mouse event.
        """
        if event.button() == Qt.MouseButton.LeftButton and self.dragging_position:
            # End dragging
            self.dragging_position = False
            
            # Reset cursor
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Accept the event
            event.accept()
        else:
            # Pass other buttons to parent
            super().mouseReleaseEvent(event)