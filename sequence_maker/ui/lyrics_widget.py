"""
Sequence Maker - Lyrics Widget

This module defines the LyricsWidget class, which displays and manages lyrics.
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QTextEdit, QSplitter, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QRectF, QPoint
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QFontMetrics

class LyricsDisplayWidget(QWidget):
    """
    Custom widget for displaying lyrics with timestamps.
    
    This widget displays lyrics with word-level timestamps, with the timestamps
    in a smaller font above each word. Words are clickable to move the playback
    position to that word's timestamp.
    
    Attributes:
        app: The main application instance.
        parent: The parent widget.
    """
    
    # Signal emitted when a timestamp is clicked
    timestamp_clicked = pyqtSignal(float)
    
    def __init__(self, app, parent=None):
        """
        Initialize the lyrics display widget.
        
        Args:
            app: The main application instance.
            parent: The parent widget.
        """
        super().__init__(parent)
        
        self.app = app
        self.lyrics_data = None
        self.current_position = 0.0
        
        # Word display properties
        self.word_font = QFont("Arial", 14)  # Larger font for words
        self.time_font = QFont("Arial", 8)   # Smaller font for timestamps
        self.word_spacing = 10               # Horizontal space between words
        self.line_spacing = 40               # Vertical space between lines
        self.time_height = 15                # Height for timestamp display
        self.highlight_color = QColor(255, 255, 0, 100)  # Yellow with transparency
        
        # Layout data
        self.word_rects = []  # List of (word_timestamp, rect) tuples for hit testing
        self.content_height = 0
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Set focus policy to receive key events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def set_lyrics(self, lyrics_data):
        """
        Set the lyrics data to display.
        
        Args:
            lyrics_data: Lyrics data object.
        """
        self.lyrics_data = lyrics_data
        self.word_rects = []
        self.update_layout()
        self.update()
    
    def set_position(self, position):
        """
        Set the current playback position.
        
        Args:
            position (float): Current playback position in seconds.
        """
        self.current_position = position
        self.update()  # Redraw to update highlighting
    
    def update_layout(self):
        """Calculate layout for all words and timestamps."""
        if not self.lyrics_data or not hasattr(self.lyrics_data, 'word_timestamps'):
            self.content_height = 0
            return
        
        self.word_rects = []
        
        # Get font metrics for measurement
        word_metrics = QFontMetrics(self.word_font)
        time_metrics = QFontMetrics(self.time_font)
        
        # Group words by lines
        lines = self.lyrics_data.lyrics_text.split('\n')
        word_index = 0
        total_words = len(self.lyrics_data.word_timestamps)
        
        x = 10  # Starting x position
        y = 30  # Starting y position (allowing space for the first timestamp)
        
        max_width = 0
        
        for line in lines:
            if line.strip():  # Skip empty lines
                words = line.split()
                line_start_x = x
                
                for word in words:
                    if word_index < total_words:
                        timestamp = self.lyrics_data.word_timestamps[word_index]
                        
                        # Calculate word width
                        word_width = word_metrics.horizontalAdvance(timestamp.word)
                        
                        # Calculate timestamp width
                        time_text = f"{timestamp.start:.2f}-{timestamp.end:.2f}"
                        time_width = time_metrics.horizontalAdvance(time_text)
                        
                        # Use the larger of the two widths
                        item_width = max(word_width, time_width)
                        
                        # Create rectangles for the word and timestamp
                        word_rect = QRectF(x, y, item_width, word_metrics.height())
                        time_rect = QRectF(x, y - self.time_height, item_width, self.time_height)
                        
                        # Store the word timestamp and its rectangle for hit testing
                        self.word_rects.append((timestamp, word_rect, time_rect))
                        
                        # Move to the next word position
                        x += item_width + self.word_spacing
                        word_index += 1
                    else:
                        # If we've run out of timestamps, just display the word
                        word_width = word_metrics.horizontalAdvance(word)
                        x += word_width + self.word_spacing
                
                # Track maximum width
                max_width = max(max_width, x)
                
                # Move to the next line
                x = line_start_x
                y += self.line_spacing
            else:
                # Empty line, just add some space
                y += self.line_spacing // 2
        
        # Set the content height
        self.content_height = y + 20  # Add some padding at the bottom
        
        # Set minimum size based on content
        self.setMinimumSize(max_width + 20, self.content_height)
    
    def paintEvent(self, event):
        """
        Paint the lyrics display.
        
        Args:
            event: Paint event.
        """
        if not self.lyrics_data or not hasattr(self.lyrics_data, 'word_timestamps'):
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # Draw each word and its timestamp
        for timestamp, word_rect, time_rect in self.word_rects:
            # Check if this word is the current word
            is_current = timestamp.start <= self.current_position <= timestamp.end
            
            # Highlight current word
            if is_current:
                painter.fillRect(word_rect, self.highlight_color)
            
            # Draw timestamp above the word
            painter.setFont(self.time_font)
            time_text = f"{timestamp.start:.2f}-{timestamp.end:.2f}"
            painter.setPen(QPen(QColor(100, 100, 100)))  # Gray color for timestamps
            painter.drawText(time_rect, Qt.AlignmentFlag.AlignCenter, time_text)
            
            # Draw the word
            painter.setFont(self.word_font)
            painter.setPen(QPen(QColor(0, 0, 0)))  # Black color for words
            painter.drawText(word_rect, Qt.AlignmentFlag.AlignCenter, timestamp.word)
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events.
        
        Args:
            event: Mouse event.
        """
        # Check if a timestamp was clicked
        pos = event.position()
        for timestamp, word_rect, time_rect in self.word_rects:
            # Check if click is within the word or timestamp rect
            if word_rect.contains(pos) or time_rect.contains(pos):
                # Emit signal with the start time of the word
                self.timestamp_clicked.emit(timestamp.start)
                break
        
        super().mousePressEvent(event)
    
    def sizeHint(self):
        """
        Get the suggested size for the widget.
        
        Returns:
            QSize: Suggested size.
        """
        return QSize(600, self.content_height)


class LyricsWidget(QWidget):
    """
    Widget for displaying and managing lyrics.
    
    This widget displays lyrics with word-level timestamps and highlights
    the current word based on the playback position.
    
    Attributes:
        app: The main application instance.
        parent: The parent widget.
    """
    
    # Signals
    process_clicked = pyqtSignal()
    
    def __init__(self, app, parent=None):
        """
        Initialize the lyrics widget.
        
        Args:
            app: The main application instance.
            parent: The parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.LyricsWidget")
        self.app = app
        self.parent = parent
        
        # Initialize UI
        self._init_ui()
        
        # Connect signals
        self._connect_signals()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header layout removed to save space
        
        # Create status layout
        self.status_layout = QHBoxLayout()
        self.main_layout.addLayout(self.status_layout)
        
        # Create status label
        self.status_label = QLabel("Ready")
        self.status_layout.addWidget(self.status_label)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 3)  # 3 steps: identify, fetch lyrics, align
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.status_layout.addWidget(self.progress_bar)
        
        # Create lyrics display area
        self.lyrics_scroll = QScrollArea()
        self.lyrics_scroll.setWidgetResizable(True)
        self.lyrics_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.lyrics_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.main_layout.addWidget(self.lyrics_scroll)
        
        # Create custom lyrics display widget
        self.lyrics_display = LyricsDisplayWidget(self.app)
        self.lyrics_scroll.setWidget(self.lyrics_display)
        
        # Set minimum height
        self.setMinimumHeight(100)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Connect timeline manager signals
        self.app.timeline_manager.position_changed.connect(self._on_position_changed)
        
        # Connect project manager signals to update lyrics when a project is loaded
        self.app.project_manager.project_loaded.connect(self._on_project_loaded)
        
        # Connect lyrics display signals
        self.lyrics_display.timestamp_clicked.connect(self._on_timestamp_clicked)
    
    def _on_project_loaded(self, project):
        """
        Handle project loaded signal.
        
        Args:
            project: The loaded project.
        """
        print("[LyricsWidget] Project loaded, updating lyrics display")
        self.logger.info("Project loaded, updating lyrics display")
        
        # Check if the project has lyrics data
        if project and hasattr(project, 'lyrics') and project.lyrics:
            print(f"[LyricsWidget] Project has lyrics data: {project.lyrics.song_name}")
            self.logger.info(f"Project has lyrics data: {project.lyrics.song_name}")
            
            # Update the lyrics display with the project's lyrics data
            self.update_lyrics(project.lyrics)
        else:
            print("[LyricsWidget] Project has no lyrics data")
            self.logger.info("Project has no lyrics data")
            # Clear the lyrics display
            self.lyrics_display.set_lyrics(None)
    
    def _on_position_changed(self, position):
        """
        Handle position changed signal.
        
        Args:
            position (float): Current playback position in seconds.
        """
        # Update the lyrics display with the new position
        self.lyrics_display.set_position(position)
    
    def _on_timestamp_clicked(self, position):
        """
        Handle timestamp clicked signal.
        
        Args:
            position (float): Position in seconds to seek to.
        """
        print(f"[LyricsWidget] Timestamp clicked: {position:.2f}s")
        self.logger.info(f"Timestamp clicked: {position:.2f}s")
        
        # Set the timeline position
        self.app.timeline_manager.set_position(position)
    
    def _on_process_button_clicked(self):
        """Handle Process Lyrics button click."""
        print("[LyricsWidget] Process Lyrics button clicked")
        self.logger.info("Process Lyrics button clicked")
        
        # Check if audio is loaded
        if not self.app.audio_manager.audio_file:
            print("[LyricsWidget] No audio file loaded")
            self.logger.warning("No audio file loaded")
            return
        
        print(f"[LyricsWidget] Audio file: {self.app.audio_manager.audio_file}")
        
        # Check if lyrics manager exists
        if not hasattr(self.app, 'lyrics_manager'):
            print("[LyricsWidget] No lyrics manager found")
            self.logger.error("No lyrics manager found")
            return
        
        # Update status
        self.update_status("Starting lyrics processing...", 0)
        
        # Process audio
        print("[LyricsWidget] Calling lyrics_manager.process_audio")
        self.app.lyrics_manager.process_audio(self.app.audio_manager.audio_file)
        
        # Emit signal
        print("[LyricsWidget] Emitting process_clicked signal")
        self.process_clicked.emit()
    
    def update_status(self, status_text, step=None):
        """
        Update the status indicator.
        
        Args:
            status_text (str): Status text to display.
            step (int, optional): Current step in the process (0-3).
        """
        print(f"[LyricsWidget] Status update: {status_text}")
        self.logger.info(f"Status update: {status_text}")
        
        # Update status label
        self.status_label.setText(status_text)
        
        # Update progress bar if step is provided
        if step is not None:
            self.progress_bar.setValue(step)
            self.progress_bar.setVisible(True)
        
        # Process events to update UI immediately
        from PyQt6.QtCore import QCoreApplication
        QCoreApplication.processEvents()
    
    def reset_status(self):
        """Reset the status indicator to its initial state."""
        self.status_label.setText("Ready")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
    
    def update_lyrics(self, lyrics_data):
        """
        Update the lyrics display with new lyrics data.
        
        Args:
            lyrics_data: Lyrics data object.
        """
        print("[LyricsWidget] Updating lyrics display")
        self.logger.info("Updating lyrics display")
        
        # Reset status
        self.reset_status()
        
        # Update the lyrics display
        if lyrics_data and hasattr(lyrics_data, 'lyrics_text') and lyrics_data.lyrics_text:
            print(f"[LyricsWidget] Lyrics text available: {len(lyrics_data.lyrics_text)} characters")
            
            # Check if we have word timestamps
            if hasattr(lyrics_data, 'word_timestamps') and lyrics_data.word_timestamps:
                print(f"[LyricsWidget] Word timestamps available: {len(lyrics_data.word_timestamps)} words")
                
                # Log some of the timestamps for debugging
                if len(lyrics_data.word_timestamps) > 0:
                    sample_size = min(5, len(lyrics_data.word_timestamps))
                    print(f"[LyricsWidget] Sample timestamps (first {sample_size} words):")
                    for i in range(sample_size):
                        ts = lyrics_data.word_timestamps[i]
                        print(f"[LyricsWidget]   Word: '{ts.word}', Start: {ts.start:.2f}, End: {ts.end:.2f}")
                
                # Set the lyrics data in the custom display widget
                self.lyrics_display.set_lyrics(lyrics_data)
            else:
                print("[LyricsWidget] No word timestamps available")
                # Create a simple lyrics object with just the text
                self.lyrics_display.set_lyrics(lyrics_data)
        else:
            print("[LyricsWidget] No lyrics text available")
            self.lyrics_display.set_lyrics(None)