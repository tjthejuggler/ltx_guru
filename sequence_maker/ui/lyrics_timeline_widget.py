"""
Sequence Maker - Lyrics Timeline Widget

Displays lyrics as word boxes on a timeline that lines up with and zooms/scrolls
with the audio and color timelines. Each word box is positioned precisely based on
its start and end timestamps.

Interactions:
- Click a word → seek to its start time
- Click an already-selected word → seek to its end time
- Drag a word → move it in time (shifts both start and end)
- Drag the left edge of a word → resize its start time
- Drag the right edge of a word → resize its end time
- Hover over a word → tooltip with start/end times
- Cursor changes to resize icon when hovering over word edges

All drag/resize changes are persisted to the project's lyrics data and
mark the project as changed.
"""

import logging
from PyQt6.QtWidgets import QWidget, QToolTip, QSizePolicy
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QFontMetrics,
    QMouseEvent
)


class LyricsTimelineWidget(QWidget):
    """
    Timeline-based lyrics display where each word is a box positioned
    precisely at its start/end time, synchronized with the audio and
    color timelines.

    Signals:
        word_clicked: Emitted with a time (float) when a word is clicked.
        lyrics_changed: Emitted when word timestamps are modified by drag/resize.
    """

    word_clicked = pyqtSignal(float)
    lyrics_changed = pyqtSignal()

    # Font size limits (in pixels)
    BASE_FONT_SIZE = 8
    MIN_FONT_SIZE = 5
    MAX_FONT_SIZE = 22

    # Visual constants
    TIMELINE_HEIGHT = 40
    WORD_PADDING = 3  # horizontal padding inside word boxes
    WORD_MARGIN = 1   # horizontal margin between word boxes
    WORD_BORDER_RADIUS = 3
    EDGE_TOLERANCE = 6  # pixels from edge to trigger resize cursor/mode
    WORD_WRAP_MIN_LENGTH = 4  # words longer than 3 chars get split if they don't fit

    # Colors
    BG_COLOR = QColor(30, 30, 30)
    WORD_BG_COLOR = QColor(60, 60, 80)
    WORD_BG_HOVER_COLOR = QColor(80, 80, 110)
    WORD_BG_CURRENT_COLOR = QColor(100, 80, 40)
    WORD_BG_DRAG_COLOR = QColor(80, 60, 120)
    WORD_TEXT_COLOR = QColor(200, 200, 200)
    WORD_TEXT_CURRENT_COLOR = QColor(255, 255, 100)
    POSITION_MARKER_COLOR = QColor(255, 0, 0, 200)
    EDGE_HANDLE_COLOR = QColor(180, 180, 220, 120)

    # Drag modes
    _DRAG_NONE = 0
    _DRAG_MOVE = 1
    _DRAG_RESIZE_START = 2
    _DRAG_RESIZE_END = 3

    def __init__(self, app, parent=None):
        super().__init__(parent)

        self.logger = logging.getLogger("SequenceMaker.LyricsTimelineWidget")
        self.app = app

        # Data
        self._lyrics_data = None
        self._word_timestamps = []

        # State
        self._current_position = 0.0
        self._selected_word = None  # the WordTimestamp currently at playback position
        self._hovered_word = None   # the WordTimestamp under the mouse cursor

        # Drag state
        self._drag_mode = self._DRAG_NONE
        self._drag_word = None      # the WordTimestamp being dragged
        self._drag_start_x = 0      # mouse x at drag start
        self._drag_initial_start = 0.0  # word start time at drag start
        self._drag_initial_end = 0.0    # word end time at drag start
        self._drag_moved = False    # whether the drag actually moved the word

        # Scroll/zoom (synchronized from TimelineWidget)
        self._horizontal_scroll_offset = 0

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)

        # Widget properties
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(self.TIMELINE_HEIGHT)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_lyrics(self, lyrics_data):
        """Set the lyrics data to display."""
        self._lyrics_data = lyrics_data
        self._word_timestamps = []
        if lyrics_data and hasattr(lyrics_data, 'word_timestamps'):
            self._word_timestamps = lyrics_data.word_timestamps
        self._selected_word = None
        self.update()

    def set_position(self, position):
        """Update the current playback position (seconds)."""
        self._current_position = position
        # Determine which word is "current"
        self._selected_word = None
        for wt in self._word_timestamps:
            if wt.start is None or wt.end is None:
                continue
            if wt.start <= position <= wt.end:
                self._selected_word = wt
                break
        self.update()

    def set_horizontal_scroll_offset(self, offset):
        """Set the horizontal scroll offset (from TimelineWidget scroll sync)."""
        self._horizontal_scroll_offset = offset
        self.update()

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------

    def _time_to_x(self, time_seconds):
        """Convert a time in seconds to an x pixel coordinate on this widget."""
        timeline_widget = self.app.main_window.timeline_widget
        time_scale = timeline_widget.time_scale
        zoom_level = timeline_widget.zoom_level
        return time_seconds * time_scale * zoom_level - self._horizontal_scroll_offset

    def _x_to_time(self, x):
        """Convert an x pixel coordinate to time in seconds."""
        timeline_widget = self.app.main_window.timeline_widget
        time_scale = timeline_widget.time_scale
        zoom_level = timeline_widget.zoom_level
        return (x + self._horizontal_scroll_offset) / (time_scale * zoom_level)

    def _font_size(self):
        """Calculate the font size based on current zoom level."""
        timeline_widget = self.app.main_window.timeline_widget
        zoom = timeline_widget.zoom_level
        size = self.BASE_FONT_SIZE * zoom
        return max(self.MIN_FONT_SIZE, min(self.MAX_FONT_SIZE, size))

    def _word_rect(self, word_ts):
        """Calculate the pixel rectangle for a word timestamp."""
        if word_ts.start is None or word_ts.end is None:
            return None
        x_start = self._time_to_x(word_ts.start)
        x_end = self._time_to_x(word_ts.end)
        width = max(1, x_end - x_start - self.WORD_MARGIN)
        y = 2
        height = self.TIMELINE_HEIGHT - 4
        return QRect(int(x_start), y, int(width), height)

    def _edge_at_pos(self, pos, word_ts):
        """
        Check if pos is near the left or right edge of a word box.
        Returns 'left', 'right', or None.
        """
        rect = self._word_rect(word_ts)
        if rect is None:
            return None
        if pos.x() <= rect.left() + self.EDGE_TOLERANCE:
            return 'left'
        if pos.x() >= rect.right() - self.EDGE_TOLERANCE:
            return 'right'
        return None

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _mark_project_changed(self):
        """Mark the project as changed so it gets saved."""
        if hasattr(self.app, 'project_manager') and self.app.project_manager.current_project:
            self.app.project_manager.project_changed.emit()
        self.lyrics_changed.emit()

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # Background
        painter.fillRect(self.rect(), self.BG_COLOR)

        if not self._word_timestamps:
            painter.setPen(QPen(QColor(100, 100, 100)))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No lyrics loaded")
            painter.end()
            return

        font_size = self._font_size()
        word_font = QFont("Arial", int(font_size))
        painter.setFont(word_font)

        for wt in self._word_timestamps:
            if wt.start is None or wt.end is None:
                continue

            rect = self._word_rect(wt)
            if rect is None:
                continue

            # Skip if entirely off-screen
            if rect.right() < 0 or rect.left() > self.width():
                continue

            is_current = (wt is self._selected_word)
            is_hovered = (wt is self._hovered_word)
            is_dragging = (wt is self._drag_word and self._drag_mode != self._DRAG_NONE)

            # Choose background color
            if is_dragging:
                bg_color = self.WORD_BG_DRAG_COLOR
            elif is_current:
                bg_color = self.WORD_BG_CURRENT_COLOR
            elif is_hovered:
                bg_color = self.WORD_BG_HOVER_COLOR
            else:
                bg_color = self.WORD_BG_COLOR

            # Draw word box
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(bg_color))
            painter.drawRoundedRect(rect, self.WORD_BORDER_RADIUS, self.WORD_BORDER_RADIUS)

            # Draw edge handles for hovered/dragged words
            if is_hovered or is_dragging:
                # Left edge handle
                handle_rect_l = QRect(rect.left(), rect.top(), 3, rect.height())
                painter.fillRect(handle_rect_l, self.EDGE_HANDLE_COLOR)
                # Right edge handle
                handle_rect_r = QRect(rect.right() - 3, rect.top(), 3, rect.height())
                painter.fillRect(handle_rect_r, self.EDGE_HANDLE_COLOR)

            # Draw word text — split onto two rows if the word is long
            # enough and doesn't fit on one line
            text_color = self.WORD_TEXT_CURRENT_COLOR if is_current else self.WORD_TEXT_COLOR
            painter.setPen(QPen(text_color))
            text_rect = QRect(
                rect.x() + self.WORD_PADDING,
                rect.y(),
                rect.width() - 2 * self.WORD_PADDING,
                rect.height()
            )
            if font_size >= self.MIN_FONT_SIZE:
                fm = QFontMetrics(word_font)
                word_width = fm.horizontalAdvance(wt.word)
                available_width = text_rect.width()
                if len(wt.word) >= self.WORD_WRAP_MIN_LENGTH and word_width > available_width:
                    # Split the word roughly in half and draw on two rows
                    mid = len(wt.word) // 2
                    top_text = wt.word[:mid]
                    bottom_text = wt.word[mid:]
                    row_height = text_rect.height() // 2
                    top_rect = QRect(text_rect.x(), text_rect.y(), text_rect.width(), row_height)
                    bottom_rect = QRect(text_rect.x(), text_rect.y() + row_height, text_rect.width(), row_height)
                    painter.drawText(top_rect, Qt.AlignmentFlag.AlignCenter, top_text)
                    painter.drawText(bottom_rect, Qt.AlignmentFlag.AlignCenter, bottom_text)
                else:
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, wt.word)

        # Draw position marker
        self._draw_position_marker(painter)

        painter.end()

    def _draw_position_marker(self, painter):
        """Draw the red position marker line."""
        pos_x = int(self._time_to_x(self._current_position))
        if 0 <= pos_x <= self.width():
            painter.setPen(QPen(self.POSITION_MARKER_COLOR, 2))
            painter.drawLine(pos_x, 0, pos_x, self.height())

    # ------------------------------------------------------------------
    # Mouse events
    # ------------------------------------------------------------------

    def _word_at_pos(self, pos):
        """Return the WordTimestamp at the given widget position, or None."""
        for wt in self._word_timestamps:
            if wt.start is None or wt.end is None:
                continue
            rect = self._word_rect(wt)
            if rect and rect.contains(pos):
                return wt
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            wt = self._word_at_pos(pos)
            if wt:
                # Check if near an edge (resize) or center (move or click)
                edge = self._edge_at_pos(pos, wt)

                if edge == 'left':
                    self._drag_mode = self._DRAG_RESIZE_START
                    self._drag_word = wt
                    self._drag_start_x = pos.x()
                    self._drag_initial_start = wt.start
                    self._drag_initial_end = wt.end
                    self._drag_moved = False
                    event.accept()
                    return
                elif edge == 'right':
                    self._drag_mode = self._DRAG_RESIZE_END
                    self._drag_word = wt
                    self._drag_start_x = pos.x()
                    self._drag_initial_start = wt.start
                    self._drag_initial_end = wt.end
                    self._drag_moved = False
                    event.accept()
                    return
                else:
                    # Start a potential drag-move. We'll only actually move
                    # if the mouse moves beyond a small threshold; otherwise
                    # it's a click (seek).
                    self._drag_mode = self._DRAG_MOVE
                    self._drag_word = wt
                    self._drag_start_x = pos.x()
                    self._drag_initial_start = wt.start
                    self._drag_initial_end = wt.end
                    self._drag_moved = False
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()

        # --- Active drag ---
        if self._drag_mode != self._DRAG_NONE and self._drag_word is not None:
            dx = pos.x() - self._drag_start_x
            dt = self._x_to_time(pos.x()) - self._x_to_time(self._drag_start_x)

            if abs(dx) > 2:
                self._drag_moved = True

            if self._drag_mode == self._DRAG_MOVE:
                # Move the whole word (shift both start and end)
                new_start = self._drag_initial_start + dt
                new_end = self._drag_initial_end + dt
                # Don't allow negative times
                if new_start < 0:
                    new_end -= new_start
                    new_start = 0
                self._drag_word.start = new_start
                self._drag_word.end = max(new_start + 0.01, new_end)
                self.update()

            elif self._drag_mode == self._DRAG_RESIZE_START:
                new_start = self._drag_initial_start + dt
                # Clamp: start must be < end, and >= 0
                new_start = max(0, min(new_start, self._drag_word.end - 0.01))
                self._drag_word.start = new_start
                self.update()

            elif self._drag_mode == self._DRAG_RESIZE_END:
                new_end = self._drag_initial_end + dt
                # Clamp: end must be > start
                new_end = max(self._drag_word.start + 0.01, new_end)
                self._drag_word.end = new_end
                self.update()

            # Update tooltip with new times
            wt = self._drag_word
            start_min, start_sec = divmod(wt.start, 60)
            end_min, end_sec = divmod(wt.end, 60)
            tip = (f"{wt.word}\n"
                   f"Start: {int(start_min):02d}:{start_sec:05.2f}\n"
                   f"End:   {int(end_min):02d}:{end_sec:05.2f}")
            QToolTip.showText(event.globalPosition().toPoint(), tip, self)

            event.accept()
            return

        # --- Hover (no drag active) ---
        old_hovered = self._hovered_word
        self._hovered_word = self._word_at_pos(pos)

        if self._hovered_word != old_hovered:
            self.update()

        # Cursor and tooltip
        if self._hovered_word:
            wt = self._hovered_word
            edge = self._edge_at_pos(pos, wt)
            if edge == 'left':
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif edge == 'right':
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.setCursor(Qt.CursorShape.OpenHandCursor)

            start_min, start_sec = divmod(wt.start, 60)
            end_min, end_sec = divmod(wt.end, 60)
            tip = (f"{wt.word}\n"
                   f"Start: {int(start_min):02d}:{start_sec:05.2f}\n"
                   f"End:   {int(end_min):02d}:{end_sec:05.2f}")
            QToolTip.showText(event.globalPosition().toPoint(), tip, self)
        else:
            QToolTip.hideText()
            self.setCursor(Qt.CursorShape.ArrowCursor)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._drag_mode != self._DRAG_NONE and self._drag_word is not None:
                if self._drag_moved:
                    # Persist the change
                    self._mark_project_changed()
                else:
                    # It was a click, not a drag — seek
                    wt = self._drag_word
                    if wt is self._selected_word and wt.end is not None:
                        self.word_clicked.emit(wt.end)
                    else:
                        self.word_clicked.emit(wt.start)

                self._drag_mode = self._DRAG_NONE
                self._drag_word = None
                self._drag_moved = False
                event.accept()
                return

        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        self._hovered_word = None
        QToolTip.hideText()
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
        super().leaveEvent(event)
