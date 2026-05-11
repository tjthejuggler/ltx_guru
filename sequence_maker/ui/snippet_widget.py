"""
Sequence Maker - Snippet Widget

This module defines the SnippetWidget class, which provides a collapsible
section for creating and editing snippets with mini timelines.
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QCheckBox, QScrollArea, QSpinBox,
    QDoubleSpinBox, QGroupBox, QSizePolicy, QFrame, QMenu, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import (
    QPainter, QColor, QBrush, QPen, QLinearGradient, QFont,
    QMouseEvent
)

from app.constants import DEFAULT_COLORS, COLOR_NAMES


class SnippetTimelineBar(QWidget):
    """
    A mini timeline bar for a single ball within a snippet.
    Displays and allows editing of color segments.
    """

    # Emits (timeline_index, segment_or_None, time_pos)
    segment_clicked = pyqtSignal(int, object, float)
    segment_right_clicked = pyqtSignal(int, object, float)

    def __init__(self, snippet_timeline, timeline_index, parent=None):
        super().__init__(parent)

        self.snippet_timeline = snippet_timeline
        self.timeline_index = timeline_index
        self.time_scale = 80.0  # pixels per second (smaller than main)
        self.bar_height = 30
        self.setFixedHeight(self.bar_height + 4)
        self.setMinimumWidth(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMouseTracking(True)  # needed for cursor changes without button press

        self._selected_segment = None
        self._dragging_position = False

    def get_duration(self):
        """Get the snippet duration from the parent snippet widget."""
        parent = self.parent()
        while parent and not isinstance(parent, SnippetWidget):
            parent = parent.parent()
        if parent and hasattr(parent, 'current_snippet') and parent.current_snippet:
            return parent.current_snippet.duration
        return 2.0

    def set_selected_segment(self, segment):
        """Set the currently selected segment and repaint."""
        self._selected_segment = segment
        self.update()

    def _get_segment_at_time(self, time_pos):
        """Return the segment that contains time_pos, or None."""
        for seg in self.snippet_timeline.segments:
            if seg.start_time <= time_pos <= seg.end_time:
                return seg
        return None

    def _is_near_position_marker(self, x_pixel):
        """Return True if x_pixel is within grab distance (5px) of the position marker."""
        duration = self.get_duration()
        if duration <= 0:
            return False
        snippet_widget = self.parent()
        while snippet_widget and not isinstance(snippet_widget, SnippetWidget):
            snippet_widget = snippet_widget.parent()
        if snippet_widget and hasattr(snippet_widget, '_snippet_position'):
            pos = snippet_widget._snippet_position
            marker_x = int((pos / duration) * self.width())
            return abs(x_pixel - marker_x) <= 5
        return False

    def paintEvent(self, event):
        """Paint the mini timeline segments."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        duration = self.get_duration()
        w = self.width()
        h = self.bar_height

        # Background
        painter.fillRect(0, 0, w, h, QColor(40, 40, 40))

        # Draw segments
        for seg in self.snippet_timeline.segments:
            if duration <= 0:
                continue
            x1 = int((seg.start_time / duration) * w)
            x2 = int((seg.end_time / duration) * w)
            x1 = max(0, min(x1, w))
            x2 = max(0, min(x2, w))

            if x2 <= x1:
                continue

            if seg.segment_type == 'fade' and seg.end_color is not None:
                # Draw fade gradient
                gradient = QLinearGradient(x1, 0, x2, 0)
                start_color = QColor(*seg.color)
                end_color = QColor(*seg.end_color)
                gradient.setColorAt(0, start_color)
                gradient.setColorAt(1, end_color)
                painter.fillRect(x1, 0, x2 - x1, h, QBrush(gradient))
            else:
                # Solid color
                color = QColor(*seg.color)
                painter.fillRect(x1, 0, x2 - x1, h, QBrush(color))

            # Segment border - highlight selected segment with white border
            if seg is self._selected_segment:
                painter.setPen(QPen(QColor(255, 255, 255), 2))
            else:
                painter.setPen(QPen(QColor(80, 80, 80), 1))
            painter.drawRect(x1, 0, x2 - x1, h)

        # Duration marker at end
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.PenStyle.DashLine))
        painter.drawLine(w - 1, 0, w - 1, h)

        # Draw position marker (yellow vertical line)
        if duration > 0:
            snippet_widget = self.parent()
            while snippet_widget and not isinstance(snippet_widget, SnippetWidget):
                snippet_widget = snippet_widget.parent()
            if snippet_widget and hasattr(snippet_widget, '_snippet_position'):
                pos = snippet_widget._snippet_position
                x = int((pos / duration) * w)
                x = max(0, min(x, w - 1))
                painter.setPen(QPen(QColor(255, 220, 0), 2))
                painter.drawLine(x, 0, x, h)

        painter.end()

    def mousePressEvent(self, event):
        """Handle mouse clicks on the timeline."""
        duration = self.get_duration()
        if duration <= 0:
            return

        x = event.position().x()
        time_pos = (x / self.width()) * duration

        if event.button() == Qt.MouseButton.LeftButton:
            # Check proximity to position marker FIRST — takes priority over segments
            if self._is_near_position_marker(x):
                self._dragging_position = True
                self.setCursor(Qt.CursorShape.SizeHorCursor)
                self.segment_clicked.emit(self.timeline_index, None, time_pos)
            else:
                segment = self._get_segment_at_time(time_pos)
                if segment is None:
                    # Clicking empty space: move position marker and start drag
                    self._dragging_position = True
                    self.segment_clicked.emit(self.timeline_index, None, time_pos)
                else:
                    self._dragging_position = False
                    self.segment_clicked.emit(self.timeline_index, segment, time_pos)
        elif event.button() == Qt.MouseButton.RightButton:
            self._dragging_position = False
            segment = self._get_segment_at_time(time_pos)
            self.segment_right_clicked.emit(self.timeline_index, segment, time_pos)

    def mouseMoveEvent(self, event):
        """Handle mouse drag and cursor updates."""
        x = event.position().x()
        if self._dragging_position:
            duration = self.get_duration()
            if duration <= 0:
                return
            time_pos = (x / self.width()) * duration
            time_pos = max(0.0, min(time_pos, duration))
            self.segment_clicked.emit(self.timeline_index, None, time_pos)
        else:
            # Update cursor: show resize cursor when near position marker
            if self._is_near_position_marker(x):
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.unsetCursor()

    def mouseReleaseEvent(self, event):
        """Stop dragging the position marker."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging_position = False


class SnippetWidget(QWidget):
    """
    Collapsible widget for creating and editing snippets.

    Contains mini timelines for each ball, controls for creating/selecting
    snippets, hotkey assignment, and ball inclusion checkboxes.
    """

    snippet_applied = pyqtSignal(object)  # snippet
    editing_mode_changed = pyqtSignal(bool)

    def __init__(self, app, parent=None):
        super().__init__(parent)

        self.logger = logging.getLogger("SequenceMaker.SnippetWidget")
        self.app = app

        self.current_snippet = None
        self._collapsed = False
        self._timeline_bars = []

        # Selected segment state for inline editor
        self._selected_segment = None
        self._selected_timeline_index = None

        # Position marker (seconds within the snippet)
        self._snippet_position = 0.0

        self._create_ui()

    def _create_ui(self):
        """Create the snippet widget UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header (collapsible toggle)
        self.header_widget = QWidget()
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(5, 2, 5, 2)

        self.toggle_button = QPushButton("▼")
        self.toggle_button.setFixedSize(20, 20)
        self.toggle_button.setFlat(True)
        self.toggle_button.clicked.connect(self._toggle_collapse)
        header_layout.addWidget(self.toggle_button)

        self.header_label = QLabel("Snippets")
        self.header_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        header_layout.addWidget(self.header_label)

        header_layout.addStretch()

        # Snippet mode cycle button in header (3 states: OFF / BEGIN / END)
        self.snippet_mode_button = QPushButton("🎵 Snippet Mode: OFF")
        self.snippet_mode_button.setFixedHeight(22)
        self.snippet_mode_button.setCheckable(False)
        self.snippet_mode_button.setToolTip(
            "Cycle Snippet Mode:\n"
            "  OFF   - hotkeys add colors normally\n"
            "  BEGIN - snippet starts at the position marker\n"
            "  END   - snippet ends at the position marker"
        )
        self.snippet_mode_button.clicked.connect(self._on_snippet_mode_clicked)
        header_layout.addWidget(self.snippet_mode_button)

        # New snippet button in header
        self.new_button = QPushButton("+ New")
        self.new_button.setFixedHeight(22)
        self.new_button.clicked.connect(self._on_new_snippet)
        header_layout.addWidget(self.new_button)

        main_layout.addWidget(self.header_widget)

        # Collapsible content
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(5, 2, 5, 5)
        content_layout.setSpacing(4)

        # Top controls row
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(5)

        # Snippet selector
        controls_layout.addWidget(QLabel("Snippet:"))
        self.snippet_combo = QComboBox()
        self.snippet_combo.setMinimumWidth(120)
        self.snippet_combo.currentIndexChanged.connect(self._on_snippet_selected)
        controls_layout.addWidget(self.snippet_combo)

        # Clone button
        self.clone_button = QPushButton("Clone")
        self.clone_button.setFixedHeight(22)
        self.clone_button.setToolTip("Clone the current snippet")
        self.clone_button.clicked.connect(self._on_clone_snippet)
        controls_layout.addWidget(self.clone_button)

        # Delete button
        self.delete_button = QPushButton("Delete")
        self.delete_button.setFixedHeight(22)
        self.delete_button.clicked.connect(self._on_delete_snippet)
        controls_layout.addWidget(self.delete_button)

        controls_layout.addStretch()
        content_layout.addLayout(controls_layout)

        # Snippet properties row
        props_layout = QHBoxLayout()
        props_layout.setSpacing(5)

        # Hotkey
        props_layout.addWidget(QLabel("Hotkey:"))
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setMaxLength(1)
        self.hotkey_edit.setFixedWidth(30)
        self.hotkey_edit.setPlaceholderText("A")
        self.hotkey_edit.textChanged.connect(self._on_hotkey_changed)
        props_layout.addWidget(self.hotkey_edit)

        # Duration mode toggle
        props_layout.addWidget(QLabel("Duration:"))
        self.duration_mode_combo = QComboBox()
        self.duration_mode_combo.addItem("Timed", "timed")
        self.duration_mode_combo.addItem("End of Word", "end_of_word")
        self.duration_mode_combo.addItem("Start of Word", "beginning_of_word")
        self.duration_mode_combo.setFixedWidth(120)
        self.duration_mode_combo.setToolTip(
            "Timed — use the fixed duration below.\n"
            "End of Word — snippet extends until the very next\n"
            "timestamped lyric word ends (clamped to max below).\n"
            "Start of Word — snippet extends until the very next\n"
            "timestamped lyric word begins (clamped to max below)."
        )
        self.duration_mode_combo.currentIndexChanged.connect(self._on_duration_mode_changed)
        props_layout.addWidget(self.duration_mode_combo)

        # Duration spin (enabled only in "timed" mode; in lyric-synced
        # modes it serves as a maximum cap)
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 30.0)
        self.duration_spin.setValue(2.0)
        self.duration_spin.setSingleStep(0.5)
        self.duration_spin.setSuffix("s")
        self.duration_spin.valueChanged.connect(self._on_duration_changed)
        props_layout.addWidget(self.duration_spin)

        # Apply button
        self.apply_button = QPushButton("▶ Apply")
        self.apply_button.setFixedHeight(22)
        self.apply_button.setToolTip("Apply snippet at current position")
        self.apply_button.clicked.connect(self._on_apply_snippet)
        props_layout.addWidget(self.apply_button)

        # Stop editing button
        self.stop_editing_button = QPushButton("✕ Stop Editing")
        self.stop_editing_button.setFixedHeight(22)
        self.stop_editing_button.clicked.connect(self._on_stop_editing)
        props_layout.addWidget(self.stop_editing_button)

        props_layout.addStretch()
        content_layout.addLayout(props_layout)

        # Position marker row
        pos_layout = QHBoxLayout()
        pos_layout.setSpacing(5)

        pos_layout.addWidget(QLabel("Position:"))
        self.position_spin = QDoubleSpinBox()
        self.position_spin.setRange(0.0, 30.0)
        self.position_spin.setValue(0.0)
        self.position_spin.setDecimals(3)
        self.position_spin.setSingleStep(0.1)
        self.position_spin.setSuffix("s")
        self.position_spin.setFixedWidth(90)
        self.position_spin.setToolTip("Position marker - color changes are added here")
        self.position_spin.valueChanged.connect(self._on_position_spin_changed)
        self.position_spin.editingFinished.connect(self._on_position_spin_editing_finished)
        pos_layout.addWidget(self.position_spin)

        pos_layout.addStretch()
        content_layout.addLayout(pos_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        content_layout.addWidget(separator)

        # Mini timelines area
        self.timelines_widget = QWidget()
        self.timelines_layout = QVBoxLayout(self.timelines_widget)
        self.timelines_layout.setContentsMargins(0, 0, 0, 0)
        self.timelines_layout.setSpacing(2)
        content_layout.addWidget(self.timelines_widget)

        # --- Inline segment editor (hidden by default) ---
        self.seg_editor_widget = QWidget()
        self.seg_editor_widget.setVisible(False)
        seg_editor_layout = QHBoxLayout(self.seg_editor_widget)
        seg_editor_layout.setContentsMargins(0, 2, 0, 2)
        seg_editor_layout.setSpacing(5)

        seg_editor_layout.addWidget(QLabel("Seg:"))

        seg_editor_layout.addWidget(QLabel("Start:"))
        self.seg_start_edit = QDoubleSpinBox()
        self.seg_start_edit.setRange(0.0, 30.0)
        self.seg_start_edit.setDecimals(3)
        self.seg_start_edit.setSingleStep(0.1)
        self.seg_start_edit.setSuffix("s")
        self.seg_start_edit.setFixedWidth(80)
        seg_editor_layout.addWidget(self.seg_start_edit)

        seg_editor_layout.addWidget(QLabel("End:"))
        self.seg_end_edit = QDoubleSpinBox()
        self.seg_end_edit.setRange(0.0, 30.0)
        self.seg_end_edit.setDecimals(3)
        self.seg_end_edit.setSingleStep(0.1)
        self.seg_end_edit.setSuffix("s")
        self.seg_end_edit.setFixedWidth(80)
        seg_editor_layout.addWidget(self.seg_end_edit)

        seg_editor_layout.addWidget(QLabel("Color:"))
        self.seg_color_label = QLabel()
        self.seg_color_label.setFixedSize(24, 18)
        self.seg_color_label.setStyleSheet("border: 1px solid #888;")
        seg_editor_layout.addWidget(self.seg_color_label)

        self.seg_apply_btn = QPushButton("Apply")
        self.seg_apply_btn.setFixedHeight(22)
        self.seg_apply_btn.clicked.connect(self._on_snippet_segment_apply)
        seg_editor_layout.addWidget(self.seg_apply_btn)

        self.seg_cancel_btn = QPushButton("Cancel")
        self.seg_cancel_btn.setFixedHeight(22)
        self.seg_cancel_btn.clicked.connect(self._on_snippet_segment_cancel)
        seg_editor_layout.addWidget(self.seg_cancel_btn)

        seg_editor_layout.addStretch()
        content_layout.addWidget(self.seg_editor_widget)

        # Status label (shown when no snippet selected)
        self.status_label = QLabel("Create a new snippet or select an existing one")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: gray; font-style: italic; padding: 10px;")
        content_layout.addWidget(self.status_label)

        main_layout.addWidget(self.content_widget)

        # Initial state
        self._update_ui_state()

    def _toggle_collapse(self):
        """Toggle the collapsible section."""
        self._collapsed = not self._collapsed
        self.content_widget.setVisible(not self._collapsed)
        self.toggle_button.setText("▶" if self._collapsed else "▼")

    def _on_snippet_mode_clicked(self):
        """Cycle snippet mode through OFF → BEGIN → END → OFF."""
        if not hasattr(self.app, 'snippet_manager'):
            return
        new_mode = self.app.snippet_manager.cycle_snippet_mode()
        self._refresh_snippet_mode_button(new_mode)

    def _refresh_snippet_mode_button(self, mode: str):
        """Update the snippet-mode button label/colour based on the current mode."""
        if mode == "begin":
            self.snippet_mode_button.setText("🎵 Snippet Mode: BEGIN")
            # Blue when snippet starts at the position marker.
            self.snippet_mode_button.setStyleSheet(
                "background-color: #2a6496; color: white; font-weight: bold;"
            )
        elif mode == "end":
            self.snippet_mode_button.setText("🎵 Snippet Mode: END")
            # Purple when snippet ends at the position marker — visually distinct from BEGIN.
            self.snippet_mode_button.setStyleSheet(
                "background-color: #7a3ea1; color: white; font-weight: bold;"
            )
        else:
            self.snippet_mode_button.setText("🎵 Snippet Mode: OFF")
            self.snippet_mode_button.setStyleSheet("")

    def _on_new_snippet(self):
        """Create a new snippet."""
        if not hasattr(self.app, 'snippet_manager'):
            return

        snippet = self.app.snippet_manager.create_snippet(
            name=f"Snippet {len(self.app.snippet_manager.snippets) + 1}",
            duration=self.duration_spin.value(),
        )
        self.current_snippet = snippet
        self._refresh_combo()
        self._build_timeline_bars()
        self._update_ui_state()

    def _on_delete_snippet(self):
        """Delete the currently selected snippet."""
        if not self.current_snippet or not hasattr(self.app, 'snippet_manager'):
            return

        self.app.snippet_manager.delete_snippet(self.current_snippet)
        self.current_snippet = None
        self._refresh_combo()
        self._build_timeline_bars()
        self._update_ui_state()

    def _on_snippet_selected(self, index):
        """Handle snippet selection from combo box."""
        if not hasattr(self.app, 'snippet_manager'):
            return

        if index < 0 or index >= len(self.app.snippet_manager.snippets):
            self.current_snippet = None
        else:
            self.current_snippet = self.app.snippet_manager.snippets[index]
            self.app.snippet_manager.select_snippet(self.current_snippet)

        self._load_snippet_properties()
        self._build_timeline_bars()
        self._update_ui_state()

    def _on_hotkey_changed(self, text):
        """Handle hotkey text change."""
        if not self.current_snippet or not hasattr(self.app, 'snippet_manager'):
            return

        # Only allow letters and numbers
        if text and not text.isalnum():
            self.hotkey_edit.setText(text[:-1] if len(text) > 1 else "")
            return

        self.app.snippet_manager.set_snippet_hotkey(self.current_snippet, text)

    def _on_duration_changed(self, value):
        """Handle duration change."""
        if not self.current_snippet or not hasattr(self.app, 'snippet_manager'):
            return

        self.app.snippet_manager.set_snippet_duration(self.current_snippet, value)
        # Repaint timelines
        for bar in self._timeline_bars:
            bar.update()

    def _on_duration_mode_changed(self, index):
        """Handle duration mode toggle between Timed / End of Word / Start of Word."""
        if not self.current_snippet or not hasattr(self.app, 'snippet_manager'):
            return

        mode = self.duration_mode_combo.currentData()
        self.current_snippet.duration_mode = mode
        # In lyric-synced modes the duration spin still serves as a max cap,
        # but we visually indicate it's not the primary duration driver.
        is_timed = (mode == "timed")
        self.duration_spin.setEnabled(is_timed if self.current_snippet else False)
        self.app.snippet_manager.snippet_modified.emit(self.current_snippet)

    def _on_apply_snippet(self):
        """Apply the current snippet at the current position."""
        if not self.current_snippet or not hasattr(self.app, 'snippet_manager'):
            return

        position = self.app.timeline_manager.position
        self.app.snippet_manager.apply_snippet(self.current_snippet, position)
        self.snippet_applied.emit(self.current_snippet)

        # Update main UI
        if hasattr(self.app, 'main_window') and self.app.main_window:
            self.app.main_window._update_ui()

    def _on_stop_editing(self):
        """Stop editing the current snippet."""
        if hasattr(self.app, 'snippet_manager'):
            self.app.snippet_manager.stop_editing()
        self.current_snippet = None
        self.snippet_combo.setCurrentIndex(-1)
        self._clear_segment_selection()
        self._update_ui_state()

    def _on_position_spin_changed(self, value):
        """Handle position spinbox value change - update position marker."""
        if not self.current_snippet:
            return
        duration = self.current_snippet.duration
        self._snippet_position = max(0.0, min(value, duration))
        self._refresh_timeline_bars()

    def _on_position_spin_editing_finished(self):
        """Clear focus from position spinbox when Enter is pressed so hotkeys work again."""
        self.position_spin.clearFocus()

    # ------------------------------------------------------------------
    # Segment selection / inline editor
    # ------------------------------------------------------------------

    def _clear_segment_selection(self):
        """Deselect any selected segment and hide the inline editor."""
        self._selected_segment = None
        self._selected_timeline_index = None
        for bar in self._timeline_bars:
            bar.set_selected_segment(None)
        self.seg_editor_widget.setVisible(False)

    def _select_segment(self, timeline_index, segment):
        """Select a segment and populate the inline editor."""
        self._selected_segment = segment
        self._selected_timeline_index = timeline_index

        # Highlight in the correct bar, clear others
        for i, bar in enumerate(self._timeline_bars):
            bar.set_selected_segment(segment if i == timeline_index else None)

        if segment is not None:
            # Populate editor fields
            self.seg_start_edit.blockSignals(True)
            self.seg_end_edit.blockSignals(True)
            self.seg_start_edit.setValue(segment.start_time)
            self.seg_end_edit.setValue(segment.end_time)
            self.seg_start_edit.blockSignals(False)
            self.seg_end_edit.blockSignals(False)

            # Show color swatch
            color = QColor(*segment.color)
            self.seg_color_label.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #888;"
            )

            self.seg_editor_widget.setVisible(True)
        else:
            self.seg_editor_widget.setVisible(False)

    def _on_timeline_clicked(self, timeline_index, segment, time_pos):
        """Handle left-click on a snippet timeline bar."""
        if not self.current_snippet or not hasattr(self.app, 'snippet_manager'):
            return

        # Activate snippet editing mode
        self.app.snippet_manager.editing = True
        self.editing_mode_changed.emit(True)

        if segment is not None:
            self._select_segment(timeline_index, segment)
        else:
            # Clicked on empty space - move position marker and deselect
            duration = self.current_snippet.duration
            time_pos = max(0.0, min(time_pos, duration))
            self._snippet_position = time_pos
            self.position_spin.blockSignals(True)
            self.position_spin.setValue(time_pos)
            self.position_spin.blockSignals(False)
            self._refresh_timeline_bars()
            self._clear_segment_selection()

    def _on_timeline_right_clicked(self, timeline_index, segment, time_pos):
        """Handle right-click on a snippet timeline bar - show context menu."""
        if not self.current_snippet:
            return

        menu = QMenu(self)

        if segment is not None:
            # Select the segment first so the user sees what they're editing
            self._select_segment(timeline_index, segment)

            # --- Change Color submenu ---
            color_menu = menu.addMenu("Change Color")
            for color_name, color_tuple in zip(COLOR_NAMES, DEFAULT_COLORS):
                action = color_menu.addAction(color_name)
                action.setData(('change_color', timeline_index, segment, color_tuple))

            custom_color_action = color_menu.addAction("Custom Color…")
            custom_color_action.setData(('custom_color', timeline_index, segment, None))

            # --- Add Fade ---
            fade_action = menu.addAction("Add Fade")
            fade_action.setData(('add_fade', timeline_index, segment, None))

            menu.addSeparator()

            # --- Delete ---
            delete_action = menu.addAction("Delete Segment")
            delete_action.setData(('delete', timeline_index, segment, None))
        else:
            # Clicked on empty space - nothing to do
            no_seg_action = menu.addAction("(No segment here)")
            no_seg_action.setEnabled(False)

        chosen = menu.exec(self.mapToGlobal(
            self._timeline_bars[timeline_index].mapTo(self, QPoint(
                int((time_pos / self.current_snippet.duration) * self._timeline_bars[timeline_index].width()),
                self._timeline_bars[timeline_index].height() // 2
            ))
        ))

        if chosen is None or chosen.data() is None:
            return

        action_type, tl_idx, seg, payload = chosen.data()

        if action_type == 'change_color':
            self._apply_segment_color(tl_idx, seg, payload)
        elif action_type == 'custom_color':
            self._choose_custom_segment_color(tl_idx, seg)
        elif action_type == 'add_fade':
            self._add_segment_fade(tl_idx, seg)
        elif action_type == 'delete':
            self._delete_segment(tl_idx, seg)

    # ------------------------------------------------------------------
    # Context menu actions
    # ------------------------------------------------------------------

    def _apply_segment_color(self, timeline_index, segment, color_tuple):
        """Change the color of a snippet segment."""
        if not self.current_snippet:
            return
        timeline = self.current_snippet.timelines[timeline_index]
        segment.color = color_tuple
        if hasattr(self.app, 'snippet_manager'):
            self.app.snippet_manager.snippet_modified.emit(self.current_snippet)
        self._refresh_timeline_bars()
        # Update color swatch if this segment is still selected
        if self._selected_segment is segment:
            color = QColor(*color_tuple)
            self.seg_color_label.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #888;"
            )

    def _choose_custom_segment_color(self, timeline_index, segment):
        """Open color dialog to pick a custom color for a snippet segment."""
        initial = QColor(*segment.color)
        color = QColorDialog.getColor(initial, self, "Choose Segment Color")
        if color.isValid():
            color_tuple = (color.red(), color.green(), color.blue())
            self._apply_segment_color(timeline_index, segment, color_tuple)

    def _add_segment_fade(self, timeline_index, segment):
        """Convert a solid segment to a fade (start color → black end color)."""
        if not self.current_snippet:
            return
        # Set end_color to black as a default fade target; user can change via editor
        segment.end_color = (0, 0, 0)
        segment.segment_type = 'fade'
        if hasattr(self.app, 'snippet_manager'):
            self.app.snippet_manager.snippet_modified.emit(self.current_snippet)
        self._refresh_timeline_bars()

    def _delete_segment(self, timeline_index, segment):
        """Delete a segment from the snippet timeline."""
        if not self.current_snippet:
            return
        timeline = self.current_snippet.timelines[timeline_index]
        timeline.remove_segment(segment)
        if hasattr(self.app, 'snippet_manager'):
            self.app.snippet_manager.snippet_modified.emit(self.current_snippet)
        # Clear selection if we deleted the selected segment
        if self._selected_segment is segment:
            self._clear_segment_selection()
        else:
            self._refresh_timeline_bars()

    # ------------------------------------------------------------------
    # Inline segment editor apply / cancel
    # ------------------------------------------------------------------

    def _on_snippet_segment_apply(self):
        """Apply the inline editor values to the selected segment."""
        if self._selected_segment is None or self._selected_timeline_index is None:
            return
        if not self.current_snippet:
            return

        new_start = self.seg_start_edit.value()
        new_end = self.seg_end_edit.value()

        # Validate
        if new_start >= new_end:
            return
        duration = self.current_snippet.duration
        new_start = max(0.0, min(new_start, duration))
        new_end = max(new_start + 0.01, min(new_end, duration))

        self._selected_segment.start_time = new_start
        self._selected_segment.end_time = new_end

        if hasattr(self.app, 'snippet_manager'):
            self.app.snippet_manager.snippet_modified.emit(self.current_snippet)

        self._refresh_timeline_bars()
        # Re-select to update the editor display
        self._select_segment(self._selected_timeline_index, self._selected_segment)

    def _on_snippet_segment_cancel(self):
        """Cancel segment editing and hide the inline editor."""
        self._clear_segment_selection()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _refresh_combo(self):
        """Refresh the snippet combo box."""
        self.snippet_combo.blockSignals(True)
        self.snippet_combo.clear()

        if hasattr(self.app, 'snippet_manager'):
            for snippet in self.app.snippet_manager.snippets:
                hotkey_str = f" [Shift+{snippet.hotkey}]" if snippet.hotkey else ""
                self.snippet_combo.addItem(f"{snippet.name}{hotkey_str}", snippet)

            # Select current snippet
            if self.current_snippet:
                idx = self.app.snippet_manager.snippets.index(self.current_snippet)
                self.snippet_combo.setCurrentIndex(idx)

        self.snippet_combo.blockSignals(False)

    def _load_snippet_properties(self):
        """Load properties from the current snippet into the UI."""
        if self.current_snippet:
            self.hotkey_edit.blockSignals(True)
            self.duration_spin.blockSignals(True)
            self.duration_mode_combo.blockSignals(True)

            self.hotkey_edit.setText(self.current_snippet.hotkey.upper())
            self.duration_spin.setValue(self.current_snippet.duration)

            # Set duration mode combo
            mode = getattr(self.current_snippet, 'duration_mode', 'timed')
            idx = self.duration_mode_combo.findData(mode)
            if idx >= 0:
                self.duration_mode_combo.setCurrentIndex(idx)
            # Duration spin enabled only in timed mode (when a snippet is selected)
            self.duration_spin.setEnabled(mode == "timed")

            self.hotkey_edit.blockSignals(False)
            self.duration_spin.blockSignals(False)
            self.duration_mode_combo.blockSignals(False)
        else:
            self.hotkey_edit.setText("")
            self.duration_spin.setValue(2.0)
            self.duration_mode_combo.setCurrentIndex(0)
            self.duration_spin.setEnabled(False)

    def _build_timeline_bars(self):
        """Build the mini timeline bars for the current snippet."""
        # Clear existing
        for bar in self._timeline_bars:
            self.timelines_layout.removeWidget(bar)
            bar.deleteLater()
        self._timeline_bars.clear()

        # Also clear any other widgets in the layout (checkbox rows)
        while self.timelines_layout.count():
            item = self.timelines_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Hide inline editor when rebuilding
        self._clear_segment_selection()

        if not self.current_snippet:
            return

        for i, timeline in enumerate(self.current_snippet.timelines):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(4)

            # Ball checkbox
            enabled = self.current_snippet.ball_enabled[i] if i < len(self.current_snippet.ball_enabled) else True
            checkbox = QCheckBox(f"Ball {i + 1}")
            checkbox.setChecked(enabled)
            checkbox.setFixedWidth(70)
            ball_idx = i  # Capture for lambda

            def make_cb(idx):
                def on_checked(state):
                    if self.current_snippet and hasattr(self.app, 'snippet_manager'):
                        self.app.snippet_manager.set_ball_enabled(
                            self.current_snippet, idx, state == Qt.CheckState.Checked.value
                        )
                        self._refresh_timeline_bars()
                return on_checked

            checkbox.checkStateChanged.connect(make_cb(ball_idx))
            row_layout.addWidget(checkbox)

            # Mini timeline bar
            bar = SnippetTimelineBar(timeline, i, self)
            bar.segment_clicked.connect(self._on_timeline_clicked)
            bar.segment_right_clicked.connect(self._on_timeline_right_clicked)
            row_layout.addWidget(bar)
            self._timeline_bars.append(bar)

            self.timelines_layout.addWidget(row_widget)

    def _refresh_timeline_bars(self):
        """Repaint all timeline bars."""
        for bar in self._timeline_bars:
            bar.update()

    def _update_ui_state(self):
        """Update UI state based on whether a snippet is selected."""
        has_snippet = self.current_snippet is not None

        self.hotkey_edit.setEnabled(has_snippet)
        self.duration_mode_combo.setEnabled(has_snippet)
        # Duration spin: enabled only when a snippet is selected AND mode is "timed"
        if has_snippet:
            mode = getattr(self.current_snippet, 'duration_mode', 'timed')
            self.duration_spin.setEnabled(mode == "timed")
        else:
            self.duration_spin.setEnabled(False)
        self.apply_button.setEnabled(has_snippet)
        self.stop_editing_button.setEnabled(has_snippet)
        self.delete_button.setEnabled(has_snippet)
        self.clone_button.setEnabled(has_snippet)
        self.position_spin.setEnabled(has_snippet)
        self.timelines_widget.setVisible(has_snippet)
        self.status_label.setVisible(not has_snippet)

        if not has_snippet:
            self.seg_editor_widget.setVisible(False)

    def _on_clone_snippet(self):
        """Clone the current snippet."""
        if not self.current_snippet or not hasattr(self.app, 'snippet_manager'):
            return

        new_snippet = self.app.snippet_manager.clone_snippet(self.current_snippet)
        self.current_snippet = new_snippet
        self._refresh_combo()
        self._build_timeline_bars()
        self._load_snippet_properties()
        self._update_ui_state()

    def add_color_to_current_snippet(self, timeline_index, color, create_fade=False):
        """
        Add a color segment to the current snippet's timeline.

        Args:
            timeline_index: Which ball timeline (0-based).
            color: RGB color tuple.
            create_fade: Whether to create a fade.
        """
        if not self.current_snippet or not hasattr(self.app, 'snippet_manager'):
            return

        # Use the position marker
        position = self._snippet_position

        self.app.snippet_manager.add_color_to_snippet(
            timeline_index, color, position, create_fade
        )
        self._refresh_timeline_bars()

    def load_snippets(self, snippets_data):
        """
        Load snippets from project data.

        Args:
            snippets_data: List of snippet dictionaries.
        """
        if not hasattr(self.app, 'snippet_manager'):
            return

        from models.snippet import Snippet

        self.app.snippet_manager.snippets.clear()
        for snippet_dict in snippets_data:
            snippet = Snippet.from_dict(snippet_dict)
            self.app.snippet_manager.snippets.append(snippet)

        self.current_snippet = None
        self._refresh_combo()
        self._build_timeline_bars()
        self._update_ui_state()

    def get_snippets_data(self):
        """
        Get snippets as a list of dictionaries for saving.

        Returns:
            list: List of snippet dictionaries.
        """
        if not hasattr(self.app, 'snippet_manager'):
            return []

        return [s.to_dict() for s in self.app.snippet_manager.snippets]
