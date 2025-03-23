"""
Sequence Maker - Lyrics Widget

This module defines the LyricsWidget class, which displays and manages lyrics.
"""

import logging
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QTextEdit, QSplitter, QProgressBar,
    QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QRectF, QPoint
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QFontMetrics

class LyricsEditDialog(QDialog):
    """
    Dialog for editing lyrics in JSON format.
    
    This dialog allows the user to edit the lyrics data in JSON format,
    which can be useful for manual corrections or adjustments.
    
    The dialog has two modes:
    - Lyrics mode: Edit only the lyrics text
    - Timestamps mode: Edit both lyrics text and timestamps
    
    Attributes:
        lyrics_data: The lyrics data to edit.
        mode: The edit mode ("lyrics" or "timestamps").
    """
    
    def __init__(self, lyrics_data, mode="timestamps", parent=None):
        """
        Initialize the lyrics edit dialog.
        
        Args:
            lyrics_data: The lyrics data to edit.
            mode: The edit mode ("lyrics" or "timestamps").
            parent: The parent widget.
        """
        super().__init__(parent)
        
        self.lyrics_data = lyrics_data
        self.mode = mode
        
        # Set window title based on mode
        if mode == "lyrics":
            self.setWindowTitle("Edit Lyrics Text")
        else:
            self.setWindowTitle("Edit Lyrics Timestamps")
        
        self.setMinimumSize(800, 600)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add instructions label
        if mode == "lyrics":
            instructions = "Edit the lyrics text only. Timestamps will be regenerated when you click OK."
        else:
            instructions = "Edit both lyrics text and timestamps. Format: MM:SS.ss"
        
        instruction_label = QLabel(instructions)
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        # Create text editor
        self.text_editor = QTextEdit()
        self.text_editor.setFont(QFont("Courier New", 10))  # Monospace font for JSON
        layout.addWidget(self.text_editor)
        
        # Create button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Load lyrics data into text editor
        self._load_lyrics_data()
    
    def _load_lyrics_data(self):
        """Load the lyrics data into the text editor."""
        if not self.lyrics_data:
            self.text_editor.setText("{}")
            return
        
        # Convert lyrics data to JSON
        lyrics_dict = self.lyrics_data.to_dict()
        
        if self.mode == "lyrics":
            # For lyrics mode, only include the lyrics text
            simplified_dict = {
                "song_name": lyrics_dict.get("song_name", ""),
                "artist_name": lyrics_dict.get("artist_name", ""),
                "lyrics_text": lyrics_dict.get("lyrics_text", "")
            }
            
            # Create a custom formatted JSON string with proper newlines
            # Start with the opening brace
            json_text = "{\n"
            
            # Add song_name with proper indentation
            json_text += '  "song_name": ' + json.dumps(simplified_dict["song_name"]) + ",\n"
            
            # Add artist_name with proper indentation
            json_text += '  "artist_name": ' + json.dumps(simplified_dict["artist_name"]) + ",\n"
            
            # Add lyrics_text with proper indentation, but handle newlines specially
            lyrics_text = simplified_dict["lyrics_text"]
            # Replace literal \n with actual newlines
            lyrics_text = lyrics_text.replace("\\n", "\n")
            
            # Format the lyrics text as a JSON string but with actual newlines
            lyrics_json = json.dumps(lyrics_text)
            # Remove the surrounding quotes
            lyrics_json = lyrics_json[1:-1]
            # Replace escaped newlines with actual newlines and proper indentation
            lyrics_json = lyrics_json.replace("\\n", "\n    ")
            
            # Add the formatted lyrics text to the JSON
            json_text += '  "lyrics_text": "' + lyrics_json + '"\n'
            
            # Close the JSON object
            json_text += "}"
        else:
            # For timestamps mode, only include the word timestamps with formatted timestamps
            word_timestamps = []
            if "word_timestamps" in lyrics_dict:
                for word_ts in lyrics_dict["word_timestamps"]:
                    ts_entry = {
                        "word": word_ts.get("word", ""),
                        "start": word_ts.get("start", 0.0),
                        "end": word_ts.get("end", 0.0)
                    }
                    
                    # Add formatted timestamps for readability
                    if "start" in word_ts:
                        start_min, start_sec = divmod(word_ts["start"], 60)
                        ts_entry["start_formatted"] = f"{int(start_min):02d}:{start_sec:05.2f}"
                    if "end" in word_ts:
                        end_min, end_sec = divmod(word_ts["end"], 60)
                        ts_entry["end_formatted"] = f"{int(end_min):02d}:{end_sec:05.2f}"
                    
                    word_timestamps.append(ts_entry)
            
            # Only include the word timestamps for the timestamps mode
            timestamps_dict = {"word_timestamps": word_timestamps}
            
            # Convert to formatted JSON
            json_text = json.dumps(timestamps_dict, indent=2)
        
        self.text_editor.setText(json_text)
    
    def get_edited_lyrics(self):
        """
        Get the edited lyrics data.
        
        Returns:
            The edited lyrics data, or None if the JSON is invalid.
        """
        try:
            # Get JSON text from editor
            json_text = self.text_editor.toPlainText()
            
            if self.mode == "lyrics":
                try:
                    # Try to parse the JSON normally first
                    edited_dict = json.loads(json_text)
                except json.JSONDecodeError:
                    # If that fails, we might have our custom format with actual newlines
                    # Let's try to parse it manually
                    import re
                    edited_dict = {}
                    
                    # Extract song_name
                    song_name_match = re.search(r'"song_name":\s*"([^"]*)"', json_text)
                    if song_name_match:
                        edited_dict["song_name"] = song_name_match.group(1)
                    
                    # Extract artist_name
                    artist_name_match = re.search(r'"artist_name":\s*"([^"]*)"', json_text)
                    if artist_name_match:
                        edited_dict["artist_name"] = artist_name_match.group(1)
                    
                    # Extract lyrics_text - this is trickier because it can contain newlines
                    # We'll look for the start of the lyrics_text field and then extract until the closing quote
                    lyrics_start_match = re.search(r'"lyrics_text":\s*"', json_text)
                    if lyrics_start_match:
                        start_pos = lyrics_start_match.end()
                        # Find the closing quote that's not escaped
                        lyrics_text = ""
                        i = start_pos
                        while i < len(json_text):
                            if json_text[i] == '"' and (i == 0 or json_text[i-1] != '\\'):
                                break
                            lyrics_text += json_text[i]
                            i += 1
                        
                        # Replace any escaped quotes
                        lyrics_text = lyrics_text.replace('\\"', '"')
                        edited_dict["lyrics_text"] = lyrics_text
            else:
                # For timestamps mode, parse JSON normally
                edited_dict = json.loads(json_text)
            
            if self.mode == "lyrics":
                # For lyrics mode, we only update the lyrics text
                if self.lyrics_data:
                    # Create a copy of the original lyrics
                    from models.lyrics import Lyrics
                    lyrics = Lyrics.from_dict(self.lyrics_data.to_dict())
                    
                    # Update only the text fields
                    lyrics.song_name = edited_dict.get("song_name", lyrics.song_name)
                    lyrics.artist_name = edited_dict.get("artist_name", lyrics.artist_name)
                    
                    # Get the new lyrics text
                    new_lyrics_text = edited_dict.get("lyrics_text", lyrics.lyrics_text)
                    
                    # Store the original lyrics text to check if it changed
                    # Normalize both texts for comparison (replace all whitespace sequences with a single space)
                    import re
                    self.original_lyrics_text = lyrics.lyrics_text
                    normalized_original = re.sub(r'\s+', ' ', self.original_lyrics_text.strip())
                    normalized_new = re.sub(r'\s+', ' ', new_lyrics_text.strip())
                    self.lyrics_text_changed = (normalized_new != normalized_original)
                    
                    print(f"[LyricsWidget] Original lyrics: '{normalized_original}'")
                    print(f"[LyricsWidget] New lyrics: '{normalized_new}'")
                    print(f"[LyricsWidget] Lyrics changed: {self.lyrics_text_changed}")
                    
                    # Update the lyrics text
                    lyrics.lyrics_text = new_lyrics_text
                    
                    # Clear timestamps only if lyrics text changed
                    if self.lyrics_text_changed:
                        lyrics.word_timestamps = []
                    
                    return lyrics
                else:
                    # Create new lyrics with just the text
                    from models.lyrics import Lyrics
                    lyrics = Lyrics()
                    lyrics.song_name = edited_dict.get("song_name", "")
                    lyrics.artist_name = edited_dict.get("artist_name", "")
                    lyrics.lyrics_text = edited_dict.get("lyrics_text", "")
                    
                    # For new lyrics, only consider them changed if they're not empty
                    self.original_lyrics_text = ""
                    import re
                    normalized_new = re.sub(r'\s+', ' ', edited_dict.get("lyrics_text", "").strip())
                    self.lyrics_text_changed = (normalized_new != "")
                    
                    print(f"[LyricsWidget] New lyrics (new object): '{normalized_new}'")
                    print(f"[LyricsWidget] Lyrics changed (new object): {self.lyrics_text_changed}")
                    
                    return lyrics
            else:
                # For timestamps mode, we update the word timestamps
                if self.lyrics_data:
                    # Create a copy of the original lyrics
                    from models.lyrics import Lyrics
                    lyrics = Lyrics.from_dict(self.lyrics_data.to_dict())
                    
                    # Update only the word timestamps
                    if "word_timestamps" in edited_dict:
                        # Remove formatted timestamps
                        word_timestamps = []
                        for word_ts in edited_dict["word_timestamps"]:
                            ts_dict = {
                                "word": word_ts.get("word", ""),
                                "start": word_ts.get("start", 0.0),
                                "end": word_ts.get("end", 0.0)
                            }
                            word_timestamps.append(ts_dict)
                        
                        # Create new WordTimestamp objects
                        from models.lyrics import WordTimestamp
                        lyrics.word_timestamps = [
                            WordTimestamp.from_dict(ts_dict) for ts_dict in word_timestamps
                        ]
                    
                    return lyrics
                else:
                    # Should not happen for timestamps mode
                    return None
        except Exception as e:
            print(f"Error parsing lyrics JSON: {e}")
            import traceback
            traceback.print_exc()
            return None


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
        self.scroll_area = None  # Will be set by LyricsWidget
        
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
        
        # Find the current word to scroll to it
        current_word_rect = None
        for timestamp, word_rect, time_rect in self.word_rects:
            if timestamp.start <= position <= timestamp.end:
                current_word_rect = word_rect
                break
        
        # If we found a current word, ensure it's visible in the scroll area
        if current_word_rect and hasattr(self, 'scroll_area'):
            # Get the center of the word rectangle
            center_x = current_word_rect.x() + current_word_rect.width() / 2
            center_y = current_word_rect.y() + current_word_rect.height() / 2
            
            # Ensure the word is visible with some margin
            margin = 50  # Pixels of margin around the word
            self.scroll_area.ensureVisible(int(center_x), int(center_y), margin, margin)
        
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
                        # Format time as mm:ss
                        start_min, start_sec = divmod(timestamp.start, 60)
                        end_min, end_sec = divmod(timestamp.end, 60)
                        time_text = f"{int(start_min):02d}:{start_sec:05.2f}-{int(end_min):02d}:{end_sec:05.2f}"
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
            # Format time as mm:ss
            start_min, start_sec = divmod(timestamp.start, 60)
            end_min, end_sec = divmod(timestamp.end, 60)
            time_text = f"{int(start_min):02d}:{start_sec:05.2f}-{int(end_min):02d}:{end_sec:05.2f}"
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
        
        # Create header layout
        self.header_layout = QHBoxLayout()
        self.main_layout.addLayout(self.header_layout)
        
        # Create status layout
        self.status_layout = QHBoxLayout()
        self.header_layout.addLayout(self.status_layout, 1)  # Give status layout stretch factor
        
        # Create status label
        self.status_label = QLabel("Ready")
        self.status_layout.addWidget(self.status_label)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 3)  # 3 steps: identify, fetch lyrics, align
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.status_layout.addWidget(self.progress_bar)
        
        # Create buttons layout
        self.buttons_layout = QHBoxLayout()
        self.header_layout.addLayout(self.buttons_layout)
        
        # Create edit lyrics button
        self.edit_lyrics_button = QPushButton("Edit Lyrics")
        self.edit_lyrics_button.setToolTip("Edit lyrics text (timestamps will be regenerated)")
        self.edit_lyrics_button.clicked.connect(self._on_edit_lyrics_button_clicked)
        self.edit_lyrics_button.setEnabled(False)  # Disable until lyrics are loaded
        self.buttons_layout.addWidget(self.edit_lyrics_button)
        
        # Create edit timestamps button
        self.edit_timestamps_button = QPushButton("Edit Timestamps")
        self.edit_timestamps_button.setToolTip("Edit lyrics timestamps")
        self.edit_timestamps_button.clicked.connect(self._on_edit_timestamps_button_clicked)
        self.edit_timestamps_button.setEnabled(False)  # Disable until lyrics are loaded
        self.buttons_layout.addWidget(self.edit_timestamps_button)
        
        # Create lyrics display area
        self.lyrics_scroll = QScrollArea()
        self.lyrics_scroll.setWidgetResizable(True)
        self.lyrics_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.lyrics_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.main_layout.addWidget(self.lyrics_scroll)
        
        # Create custom lyrics display widget
        self.lyrics_display = LyricsDisplayWidget(self.app)
        self.lyrics_scroll.setWidget(self.lyrics_display)
        
        # Store a reference to the scroll area in the display widget
        self.lyrics_display.scroll_area = self.lyrics_scroll
        
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
    def _on_edit_lyrics_button_clicked(self):
        """Handle Edit Lyrics button click."""
        print("[LyricsWidget] Edit Lyrics button clicked")
        self.logger.info("Edit Lyrics button clicked")
        
        # Check if we have lyrics data
        if not hasattr(self.app.project_manager.current_project, 'lyrics') or not self.app.project_manager.current_project.lyrics:
            print("[LyricsWidget] No lyrics data to edit")
            self.logger.warning("No lyrics data to edit")
            return
        
        # Create and show the edit dialog in lyrics mode
        dialog = LyricsEditDialog(self.app.project_manager.current_project.lyrics, "lyrics", self)
        result = dialog.exec()
        
        # If the user accepted the changes, update the lyrics
        if result == QDialog.DialogCode.Accepted:
            edited_lyrics = dialog.get_edited_lyrics()
            if edited_lyrics:
                print("[LyricsWidget] Updating lyrics with edited data")
                self.logger.info("Updating lyrics with edited data")
                
                # Update the project's lyrics
                self.app.project_manager.current_project.lyrics = edited_lyrics
                
                # Check if lyrics text has changed
                lyrics_changed = getattr(dialog, 'lyrics_text_changed', False)
                
                # If lyrics have changed and we have a lyrics manager and audio file
                if lyrics_changed and hasattr(self.app, 'lyrics_manager') and self.app.audio_manager.audio_file:
                    # Ask user if they want to reprocess the lyrics
                    from PyQt6.QtWidgets import QMessageBox
                    response = QMessageBox.question(
                        self,
                        "Reprocess Lyrics",
                        "The lyrics text has changed. Do you want to reprocess the lyrics to update the timestamps?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.Yes
                    )
                    
                    if response == QMessageBox.StandardButton.Yes:
                        print("[LyricsWidget] Regenerating timestamps for edited lyrics")
                        self.logger.info("Regenerating timestamps for edited lyrics")
                        
                        # Ask user if they want to use conservative alignment
                        use_conservative = self._show_conservative_alignment_dialog()
                        
                        # Update status
                        self.update_status("Processing edited lyrics...", 0)
                        
                        # Skip song identification and go directly to lyrics alignment
                        # We'll implement this by setting the lyrics directly in the project
                        # and then calling the alignment function
                        
                        # First, update the project's lyrics
                        self.app.project_manager.current_project.lyrics = edited_lyrics
                        
                        # Then, align the lyrics with the audio
                        if hasattr(self.app.lyrics_manager, 'align_lyrics_directly'):
                            print(f"[LyricsWidget] Calling align_lyrics_directly (conservative={use_conservative})")
                            self.app.lyrics_manager.align_lyrics_directly(
                                self.app.audio_manager.audio_file,
                                edited_lyrics,
                                conservative=use_conservative
                            )
                        else:
                            # Fallback to process_audio if align_lyrics_directly doesn't exist
                            print(f"[LyricsWidget] Falling back to process_audio (conservative={use_conservative})")
                            self.app.lyrics_manager.process_audio(
                                self.app.audio_manager.audio_file,
                                conservative=use_conservative
                            )
                    else:
                        # Just update the display with the edited lyrics
                        self.update_lyrics(edited_lyrics)
                else:
                    # Just update the display with the edited lyrics
                    self.update_lyrics(edited_lyrics)
                
                # Mark the project as modified
                self.app.project_manager.project_changed.emit()
            else:
                print("[LyricsWidget] Failed to parse edited lyrics")
                self.logger.warning("Failed to parse edited lyrics")
    
    def _on_edit_timestamps_button_clicked(self):
        """Handle Edit Timestamps button click."""
        print("[LyricsWidget] Edit Timestamps button clicked")
        self.logger.info("Edit Timestamps button clicked")
        
        # Check if we have lyrics data
        if not hasattr(self.app.project_manager.current_project, 'lyrics') or not self.app.project_manager.current_project.lyrics:
            print("[LyricsWidget] No lyrics data to edit")
            self.logger.warning("No lyrics data to edit")
            return
        
        # Check if we have timestamps
        if not hasattr(self.app.project_manager.current_project.lyrics, 'word_timestamps') or not self.app.project_manager.current_project.lyrics.word_timestamps:
            print("[LyricsWidget] No timestamps to edit")
            self.logger.warning("No timestamps to edit")
            return
        
        # Create and show the edit dialog in timestamps mode
        dialog = LyricsEditDialog(self.app.project_manager.current_project.lyrics, "timestamps", self)
        result = dialog.exec()
        
        # If the user accepted the changes, update the lyrics
        if result == QDialog.DialogCode.Accepted:
            edited_lyrics = dialog.get_edited_lyrics()
            if edited_lyrics:
                print("[LyricsWidget] Updating lyrics with edited timestamps")
                self.logger.info("Updating lyrics with edited timestamps")
                
                # Update the project's lyrics
                self.app.project_manager.current_project.lyrics = edited_lyrics
                
                # Update the display
                self.update_lyrics(edited_lyrics)
                
                # Mark the project as modified
                self.app.project_manager.project_changed.emit()
            else:
                print("[LyricsWidget] Failed to parse edited timestamps")
                self.logger.warning("Failed to parse edited timestamps")
                self.logger.warning("Failed to parse edited lyrics")
    
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
        
        # Ask user if they want to use conservative alignment
        use_conservative = self._show_conservative_alignment_dialog()
        
        # Update status
        self.update_status("Starting lyrics processing...", 0)
        
        # Process audio with conservative parameter
        print(f"[LyricsWidget] Calling lyrics_manager.process_audio (conservative={use_conservative})")
        self.app.lyrics_manager.process_audio(
            self.app.audio_manager.audio_file,
            conservative=use_conservative
        )
        
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
        
    def _show_conservative_alignment_dialog(self):
        """
        Show a dialog asking if the user wants to use conservative alignment.
        
        Returns:
            bool: True if conservative alignment should be used, False otherwise.
        """
        from PyQt6.QtWidgets import QMessageBox
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Alignment Options")
        msg_box.setText("Do you want to use conservative alignment?")
        msg_box.setInformativeText(
            "Conservative alignment instructs Gentle to stay as close as possible to your provided lyrics "
            "and avoid skipping words. This often significantly improves accuracy."
        )
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
        
        result = msg_box.exec()
        return result == QMessageBox.StandardButton.Yes
    
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
                
                # Enable both edit buttons
                self.edit_lyrics_button.setEnabled(True)
                self.edit_timestamps_button.setEnabled(True)
            else:
                print("[LyricsWidget] No word timestamps available")
                # Create a simple lyrics object with just the text
                self.lyrics_display.set_lyrics(lyrics_data)
                
                # Enable only the lyrics edit button
                self.edit_lyrics_button.setEnabled(True)
                self.edit_timestamps_button.setEnabled(False)
        else:
            print("[LyricsWidget] No lyrics text available")
            self.lyrics_display.set_lyrics(None)
            
            # Disable both edit buttons
            self.edit_lyrics_button.setEnabled(False)
            self.edit_timestamps_button.setEnabled(False)