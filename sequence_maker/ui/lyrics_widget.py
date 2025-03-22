"""
Sequence Maker - Lyrics Widget

This module defines the LyricsWidget class, which displays and manages lyrics.
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QTextEdit, QSplitter, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize

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
        
        # Create lyrics container
        self.lyrics_container = QWidget()
        self.lyrics_layout = QVBoxLayout(self.lyrics_container)
        self.lyrics_scroll.setWidget(self.lyrics_container)
        
        # Create lyrics text display
        self.lyrics_text = QTextEdit()
        self.lyrics_text.setReadOnly(True)
        self.lyrics_text.setPlaceholderText("No lyrics available. Process audio to extract lyrics.")
        self.lyrics_layout.addWidget(self.lyrics_text)
        
        # Set minimum height
        self.setMinimumHeight(100)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Connect timeline manager signals
        self.app.timeline_manager.position_changed.connect(self._on_position_changed)
        
        # Connect project manager signals to update lyrics when a project is loaded
        self.app.project_manager.project_loaded.connect(self._on_project_loaded)
    
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
            self.lyrics_text.setText("No lyrics available.")
    
    def _on_position_changed(self, position):
        """
        Handle position changed signal.
        
        Args:
            position (float): Current playback position in seconds.
        """
        # Update highlighted word based on position
        self._highlight_current_word(position)
    
    def _highlight_current_word(self, position):
        """
        Highlight the current word based on playback position.
        
        Args:
            position (float): Current playback position in seconds.
        """
        # Check if we have lyrics data
        if not hasattr(self.app.project_manager.current_project, 'lyrics') or not self.app.project_manager.current_project.lyrics:
            return
        
        # Get the current word
        current_word = None
        for word in self.app.project_manager.current_project.lyrics.word_timestamps:
            if word.start <= position <= word.end:
                current_word = word
                break
        
        # If we found a current word, highlight it
        if current_word:
            # TODO: Implement highlighting logic
            pass
    
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
        
        # Update the lyrics text
        if lyrics_data and hasattr(lyrics_data, 'lyrics_text') and lyrics_data.lyrics_text:
            print(f"[LyricsWidget] Lyrics text available: {len(lyrics_data.lyrics_text)} characters")
            
            # Check if we have word timestamps
            if hasattr(lyrics_data, 'word_timestamps') and lyrics_data.word_timestamps:
                print(f"[LyricsWidget] Word timestamps available: {len(lyrics_data.word_timestamps)} words")
                
                # Create a formatted text with timestamps
                formatted_text = ""
                
                # Group words by lines for better display
                lines = lyrics_data.lyrics_text.split('\n')
                word_index = 0
                total_words = len(lyrics_data.word_timestamps)
                
                for line in lines:
                    if line.strip():  # Skip empty lines
                        line_with_timestamps = ""
                        words = line.split()
                        
                        for word in words:
                            if word_index < total_words:
                                timestamp = lyrics_data.word_timestamps[word_index]
                                # Format: word (start-end)
                                line_with_timestamps += f"{timestamp.word} ({timestamp.start:.2f}-{timestamp.end:.2f}) "
                                word_index += 1
                            else:
                                line_with_timestamps += f"{word} "
                        
                        formatted_text += line_with_timestamps.strip() + "\n"
                    else:
                        formatted_text += "\n"
                
                # Log some of the timestamps for debugging
                if total_words > 0:
                    sample_size = min(5, total_words)
                    print(f"[LyricsWidget] Sample timestamps (first {sample_size} words):")
                    for i in range(sample_size):
                        ts = lyrics_data.word_timestamps[i]
                        print(f"[LyricsWidget]   Word: '{ts.word}', Start: {ts.start:.2f}, End: {ts.end:.2f}")
                
                self.lyrics_text.setText(formatted_text)
            else:
                print("[LyricsWidget] No word timestamps available")
                self.lyrics_text.setText(lyrics_data.lyrics_text)
        else:
            print("[LyricsWidget] No lyrics text available")
            self.lyrics_text.setText("No lyrics available.")