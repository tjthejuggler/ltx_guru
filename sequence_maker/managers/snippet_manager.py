"""
Sequence Maker - Snippet Manager

This module defines the SnippetManager class, which manages snippet
creation, storage, and application to timelines.
"""

import logging
from PyQt6.QtCore import QObject, pyqtSignal

from models.snippet import Snippet
from models.segment import TimelineSegment


class SnippetManager(QObject):
    """
    Manages snippet operations: create, delete, edit, and apply.

    Signals:
        snippet_added: Emitted when a snippet is added.
        snippet_removed: Emitted when a snippet is removed.
        snippet_modified: Emitted when a snippet is modified.
        snippet_applied: Emitted when a snippet is applied to timelines.
        editing_changed: Emitted when snippet editing mode changes.
    """

    snippet_added = pyqtSignal(object)
    snippet_removed = pyqtSignal(object)
    snippet_modified = pyqtSignal(object)
    snippet_applied = pyqtSignal(str)  # snippet name
    editing_changed = pyqtSignal(bool)  # True = editing snippet

    def __init__(self, app):
        """
        Initialize the snippet manager.

        Args:
            app: The main application instance.
        """
        super().__init__()

        self.logger = logging.getLogger("SequenceMaker.SnippetManager")
        self.app = app

        # List of all snippets
        self.snippets = []

        # Currently selected/edited snippet (None if not editing)
        self.current_snippet = None

        # Whether we're in snippet editing mode
        self._editing = False

        # Whether keyboard keys apply snippets by hotkey (instead of adding colors)
        self._snippet_mode = False

        # Snippet-local undo/redo stacks (list of snippet to_dict() snapshots)
        self._snippet_undo_stack = []
        self._snippet_redo_stack = []

    @property
    def snippet_mode(self):
        """Whether keyboard keys apply snippets by hotkey (instead of adding colors)."""
        return self._snippet_mode

    @snippet_mode.setter
    def snippet_mode(self, value):
        self._snippet_mode = bool(value)

    @property
    def editing(self):
        """Whether we're currently editing a snippet."""
        return self._editing

    @editing.setter
    def editing(self, value):
        """Set editing mode and emit signal."""
        if self._editing != value:
            self._editing = value
            self.editing_changed.emit(value)

    def create_snippet(self, name="New Snippet", hotkey="", duration=2.0):
        """
        Create a new snippet and start editing it.

        Args:
            name: Display name for the snippet.
            hotkey: Hotkey character (letter or number).
            duration: Duration in seconds.

        Returns:
            Snippet: The newly created snippet.
        """
        # Ensure unique hotkey
        if hotkey:
            hotkey = hotkey.lower()
            existing = self.get_snippet_by_hotkey(hotkey)
            if existing:
                self.logger.warning(f"Hotkey '{hotkey}' already in use by snippet '{existing.name}'")
                hotkey = ""

        snippet = Snippet(name=name, hotkey=hotkey, duration=duration)
        self.snippets.append(snippet)
        self.current_snippet = snippet
        self.editing = True
        self.snippet_added.emit(snippet)
        self.logger.info(f"Created snippet '{name}' with hotkey '{hotkey}'")
        return snippet

    def delete_snippet(self, snippet):
        """
        Delete a snippet.

        Args:
            snippet: The snippet to delete.
        """
        if snippet in self.snippets:
            self.snippets.remove(snippet)
            if self.current_snippet == snippet:
                self.current_snippet = None
                self.editing = False
            self.snippet_removed.emit(snippet)
            self.logger.info(f"Deleted snippet '{snippet.name}'")

    def select_snippet(self, snippet):
        """
        Select a snippet for editing.

        Args:
            snippet: The snippet to select, or None to deselect.
        """
        self.current_snippet = snippet
        if snippet:
            self.editing = True
        else:
            self.editing = False
        self.snippet_modified.emit(snippet)

    def get_snippet_by_hotkey(self, hotkey):
        """
        Find a snippet by its hotkey.

        Args:
            hotkey: The hotkey character (case-insensitive).

        Returns:
            Snippet or None.
        """
        hotkey = hotkey.lower()
        for snippet in self.snippets:
            if snippet.hotkey == hotkey:
                return snippet
        return None

    def apply_snippet(self, snippet, position):
        """
        Apply a snippet to the main timelines at the given position.

        This overwrites any existing segments in the time range
        [position, position + snippet.get_duration()] for each
        enabled ball timeline.

        Args:
            snippet: The snippet to apply.
            position: Start time in seconds.
        """
        if not self.app.project_manager.current_project:
            self.logger.warning("No project loaded, cannot apply snippet")
            return

        project = self.app.project_manager.current_project
        main_timelines = project.timelines
        snippet_duration = snippet.get_duration()

        for i, snippet_timeline in enumerate(snippet.timelines):
            # Skip if ball is not enabled for this snippet
            if i >= len(snippet.ball_enabled) or not snippet.ball_enabled[i]:
                continue

            # Skip if main timeline doesn't exist
            if i >= len(main_timelines):
                continue

            main_timeline = main_timelines[i]
            end_position = position + snippet_duration

            # Remove existing segments that overlap with the snippet range
            # Use timeline_manager so signals are emitted and UI updates
            tm = getattr(self.app, 'timeline_manager', None)
            segments_to_remove = []
            for seg in main_timeline.segments:
                # Check for overlap
                if seg.start_time < end_position and seg.end_time > position:
                    segments_to_remove.append(seg)

            for seg in segments_to_remove:
                if tm:
                    tm.remove_segment(main_timeline, seg)
                else:
                    main_timeline.remove_segment(seg)

            # Add snippet segments, offset by position
            for seg in snippet_timeline.segments:
                new_start = seg.start_time + position
                new_end = seg.end_time + position

                # Clamp to snippet duration
                if new_start >= end_position:
                    continue
                if new_end > end_position:
                    new_end = end_position

                if tm:
                    tm.add_segment(
                        main_timeline,
                        new_start,
                        new_end,
                        seg.color,
                        pixels=seg.pixels,
                    )
                else:
                    new_seg = TimelineSegment(
                        start_time=new_start,
                        end_time=new_end,
                        color=seg.color,
                        pixels=seg.pixels,
                        end_color=seg.end_color,
                    )
                    for effect in seg.effects:
                        new_seg.effects.append(effect)
                    main_timeline.add_segment(new_seg)

        self.snippet_applied.emit(snippet.name)
        self.logger.info(
            f"Applied snippet '{snippet.name}' at position {position:.2f}s "
            f"(duration {snippet_duration:.2f}s)"
        )

    def add_color_to_snippet(self, timeline_index, color, position, create_fade=False):
        """
        Add a color segment to the current snippet's timeline.

        Fills from `position` to the end of the snippet duration, replacing any
        overlapping segments (same behaviour as the main timeline editor).

        Args:
            timeline_index: Index of the snippet timeline.
            color: RGB color tuple.
            position: Start position in seconds within the snippet (usually 0.0).
            create_fade: Whether to create a fade segment.
        """
        if not self.current_snippet:
            return

        snippet = self.current_snippet
        if timeline_index >= len(snippet.timelines):
            return

        timeline = snippet.timelines[timeline_index]
        duration = snippet.duration

        start_time = max(0.0, position)
        end_time = duration

        if start_time >= duration:
            return

        if create_fade:
            # Find the colour of the segment immediately before position for the fade start
            prev_color = color
            segs_before = [s for s in timeline.segments if s.end_time <= start_time]
            if segs_before:
                prev_seg = max(segs_before, key=lambda s: s.end_time)
                prev_color = prev_seg.color

            segment = TimelineSegment(
                start_time=start_time,
                end_time=end_time,
                color=prev_color,
                pixels=4,
                end_color=color,
            )
        else:
            segment = TimelineSegment(
                start_time=start_time,
                end_time=end_time,
                color=color,
                pixels=4,
            )

        # Use Timeline.add_color_at_time which handles overlap removal cleanly
        timeline.add_color_at_time(start_time, color)
        # If it was a fade we need to replace the segment that was just added
        if create_fade:
            # Remove the solid segment add_color_at_time created and add the fade
            segs_at = [s for s in timeline.segments if s.start_time == start_time]
            for s in segs_at:
                timeline.remove_segment(s)
            timeline.add_segment(segment)

        self.snippet_modified.emit(snippet)

    def set_snippet_hotkey(self, snippet, hotkey):
        """
        Set the hotkey for a snippet, ensuring uniqueness.

        Args:
            snippet: The snippet to update.
            hotkey: New hotkey character.
        """
        hotkey = hotkey.lower() if hotkey else ""

        # Check uniqueness
        if hotkey:
            existing = self.get_snippet_by_hotkey(hotkey)
            if existing and existing != snippet:
                self.logger.warning(f"Hotkey '{hotkey}' already in use")
                return False

        snippet.hotkey = hotkey
        self.snippet_modified.emit(snippet)
        return True

    def set_snippet_duration(self, snippet, duration):
        """Set the duration for a snippet."""
        snippet.duration = max(0.1, duration)
        self.snippet_modified.emit(snippet)

    def set_ball_enabled(self, snippet, ball_index, enabled):
        """Enable or disable a ball in a snippet."""
        if ball_index < len(snippet.ball_enabled):
            snippet.ball_enabled[ball_index] = enabled
            self.snippet_modified.emit(snippet)

    def clone_snippet(self, snippet):
        """
        Clone a snippet, creating a deep copy with a new name.

        Args:
            snippet: The snippet to clone.

        Returns:
            The new cloned snippet.
        """
        import copy
        new_snippet = copy.deepcopy(snippet)
        new_snippet.name = f"{snippet.name} (copy)"
        new_snippet.hotkey = ""  # Clear hotkey to avoid conflicts
        self.snippets.append(new_snippet)
        self.current_snippet = new_snippet
        self.editing = True
        self.snippet_added.emit(new_snippet)
        self.logger.info(f"Cloned snippet '{snippet.name}' -> '{new_snippet.name}'")
        return new_snippet

    def save_snippet_state(self):
        """Save the current snippet's state to the undo stack (call before modifying)."""
        if not self.current_snippet:
            return
        import copy
        state = self.current_snippet.to_dict()
        self._snippet_undo_stack.append(state)
        # Clear redo stack on new action
        self._snippet_redo_stack.clear()

    def undo_snippet(self):
        """Undo the last snippet edit. Returns True if undo was performed."""
        if not self._snippet_undo_stack or not self.current_snippet:
            return False
        import copy
        # Save current state to redo stack
        self._snippet_redo_stack.append(self.current_snippet.to_dict())
        # Restore previous state
        prev_state = self._snippet_undo_stack.pop()
        from models.snippet import Snippet
        restored = Snippet.from_dict(prev_state)
        self.current_snippet.timelines = restored.timelines
        self.snippet_modified.emit(self.current_snippet)
        return True

    def redo_snippet(self):
        """Redo the last undone snippet edit. Returns True if redo was performed."""
        if not self._snippet_redo_stack or not self.current_snippet:
            return False
        # Save current state to undo stack
        self._snippet_undo_stack.append(self.current_snippet.to_dict())
        # Restore redo state
        next_state = self._snippet_redo_stack.pop()
        from models.snippet import Snippet
        restored = Snippet.from_dict(next_state)
        self.current_snippet.timelines = restored.timelines
        self.snippet_modified.emit(self.current_snippet)
        return True

    def clear_snippet_undo_history(self):
        """Clear snippet undo/redo stacks (call when switching snippets)."""
        self._snippet_undo_stack.clear()
        self._snippet_redo_stack.clear()

    def stop_editing(self):
        """Stop editing the current snippet."""
        self.current_snippet = None
        self.editing = False

    def get_hotkey_map(self):
        """
        Get a mapping of hotkeys to snippets.

        Returns:
            dict: {hotkey_char: snippet}
        """
        return {s.hotkey: s for s in self.snippets if s.hotkey}
