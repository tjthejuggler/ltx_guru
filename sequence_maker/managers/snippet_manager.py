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

        # Snippet-mode is a tri-state value:
        #   "off"   -> hotkeys add colors as usual (snippet apply disabled)
        #   "begin" -> snippet is inserted starting AT the position marker
        #   "end"   -> snippet ends AT the position marker (so it's inserted
        #              starting at position - snippet.duration)
        # Stored as a string; the setter coerces legacy bool values too so
        # any code that still does `snippet_mode = True/False` keeps working.
        self._snippet_mode = "off"

        # Snippet-local undo/redo stacks (list of snippet to_dict() snapshots)
        self._snippet_undo_stack = []
        self._snippet_redo_stack = []

    # Allowed values for snippet_mode
    SNIPPET_MODE_VALUES = ("off", "begin", "end")

    @property
    def snippet_mode(self):
        """
        Tri-state snippet mode:
          - "off"   : hotkeys add colors normally
          - "begin" : snippet starts at the position marker
          - "end"   : snippet ends at the position marker

        Truthiness still works ("off" is falsy, "begin"/"end" are truthy)
        because non-empty strings are truthy and "off" is handled by the
        explicit checks in calling code. For safety also keep an explicit
        ``is_active`` helper (see :pymeth:`is_snippet_mode_active`).
        """
        return self._snippet_mode

    @snippet_mode.setter
    def snippet_mode(self, value):
        # Backwards-compat: accept bools (True -> "begin", False -> "off")
        if isinstance(value, bool):
            self._snippet_mode = "begin" if value else "off"
            return
        if isinstance(value, str) and value in self.SNIPPET_MODE_VALUES:
            self._snippet_mode = value
            return
        # Unknown value -> turn it off rather than raise (defensive).
        self.logger.warning(f"Invalid snippet_mode value {value!r}; setting to 'off'")
        self._snippet_mode = "off"

    def is_snippet_mode_active(self):
        """Return True if snippet_mode is in any active state (not 'off')."""
        return self._snippet_mode in ("begin", "end")

    def cycle_snippet_mode(self):
        """
        Advance snippet_mode through the cycle off -> begin -> end -> off.

        Returns:
            str: The new mode value.
        """
        order = self.SNIPPET_MODE_VALUES  # ("off", "begin", "end")
        try:
            idx = order.index(self._snippet_mode)
        except ValueError:
            idx = -1
        self._snippet_mode = order[(idx + 1) % len(order)]
        return self._snippet_mode

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
        ``[position, position + snippet.duration]`` for each enabled ball
        timeline. Anything outside that window — both before ``position``
        and after ``position + snippet.duration`` — is preserved exactly.

        Args:
            snippet: The snippet to apply.
            position: Start time in seconds.
        """
        if not self.app.project_manager.current_project:
            self.logger.warning("No project loaded, cannot apply snippet")
            return

        project = self.app.project_manager.current_project
        main_timelines = project.timelines

        # Always use the user-configured snippet.duration. ``get_duration()``
        # also returns this now, but be explicit so the apply range is
        # obviously bounded by the snippet's own length.
        snippet_duration = snippet.duration
        if snippet_duration <= 0:
            self.logger.warning(
                f"Snippet '{snippet.name}' has non-positive duration "
                f"{snippet_duration}; skipping apply."
            )
            return

        for i, snippet_timeline in enumerate(snippet.timelines):
            # Skip if ball is not enabled for this snippet
            if i >= len(snippet.ball_enabled) or not snippet.ball_enabled[i]:
                continue

            # Skip if main timeline doesn't exist
            if i >= len(main_timelines):
                continue

            main_timeline = main_timelines[i]
            end_position = position + snippet_duration

            # Trim/split existing segments that overlap with the snippet range
            # so that original colors are preserved outside [position, end_position].
            tm = getattr(self.app, 'timeline_manager', None)
            segments_to_remove = []
            segments_to_add = []

            for seg in main_timeline.segments:
                # No overlap — skip
                if seg.start_time >= end_position or seg.end_time <= position:
                    continue

                # Case 1: segment completely contained within snippet range → remove
                if seg.start_time >= position and seg.end_time <= end_position:
                    segments_to_remove.append(seg)

                # Case 2: segment starts before, ends within → trim end
                elif seg.start_time < position and seg.end_time <= end_position:
                    seg.end_time = position

                # Case 3: segment starts within, ends after → trim start
                elif seg.start_time >= position and seg.end_time > end_position:
                    seg.start_time = end_position

                # Case 4: segment completely contains snippet range → split
                elif seg.start_time < position and seg.end_time > end_position:
                    # Create a new segment for the portion after the snippet
                    after_seg = TimelineSegment(
                        start_time=end_position,
                        end_time=seg.end_time,
                        color=seg.color,
                        pixels=seg.pixels,
                        end_color=seg.end_color,
                    )
                    for effect in seg.effects:
                        after_seg.effects.append(effect)
                    segments_to_add.append(after_seg)
                    # Trim original to the portion before the snippet
                    seg.end_time = position

            for seg in segments_to_remove:
                if tm:
                    tm.remove_segment(main_timeline, seg)
                else:
                    main_timeline.remove_segment(seg)

            for seg in segments_to_add:
                main_timeline.add_segment(seg)

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

        Fills from ``position`` to the end of the snippet duration, replacing any
        overlapping segments. The new segment is *strictly* clamped to
        ``[position, snippet.duration]`` — segments must never extend past the
        snippet's configured duration. (The main-timeline editor uses
        ``Timeline.add_color_at_time``, but that helper extends the new
        segment open-endedly to the next segment or +3600s, which would let
        a single colour swallow far more than the snippet's duration.)

        Args:
            timeline_index: Index of the snippet timeline.
            color: RGB color tuple.
            position: Start position in seconds within the snippet (usually 0.0).
            create_fade: Whether to create a fade segment (start colour = colour
                of the previous segment, end colour = ``color``).
        """
        if not self.current_snippet:
            return

        snippet = self.current_snippet
        if timeline_index >= len(snippet.timelines):
            return

        timeline = snippet.timelines[timeline_index]
        duration = snippet.duration

        start_time = max(0.0, position)
        end_time = duration  # Hard-clamped to the snippet's configured length

        if start_time >= duration:
            # The user clicked past the snippet's end — nothing to add.
            return

        # Determine the start colour for a fade (the colour of whatever was
        # playing immediately before this position).
        fade_start_color = color
        if create_fade:
            segs_before = [s for s in timeline.segments if s.end_time <= start_time]
            if segs_before:
                prev_seg = max(segs_before, key=lambda s: s.end_time)
                fade_start_color = prev_seg.color

        # Splice the new segment into the snippet's timeline directly,
        # mirroring the overlap rules used by ``apply_snippet`` so behaviour
        # is consistent.
        new_seg = TimelineSegment(
            start_time=start_time,
            end_time=end_time,
            color=(fade_start_color if create_fade else color),
            pixels=4,
            end_color=(color if create_fade else None),
        )

        segments_to_remove = []
        for seg in timeline.segments:
            # No overlap → keep
            if seg.start_time >= end_time or seg.end_time <= start_time:
                continue
            # Fully inside [start_time, end_time] → drop
            if seg.start_time >= start_time and seg.end_time <= end_time:
                segments_to_remove.append(seg)
            # Starts before, ends inside → trim end
            elif seg.start_time < start_time and seg.end_time <= end_time:
                seg.end_time = start_time
            # Starts inside, ends after → can't happen (end_time == duration is
            # the timeline's hard ceiling) but handled defensively
            elif seg.start_time >= start_time and seg.end_time > end_time:
                seg.start_time = end_time
            # Fully contains the new segment → split
            elif seg.start_time < start_time and seg.end_time > end_time:
                after_seg = TimelineSegment(
                    start_time=end_time,
                    end_time=seg.end_time,
                    color=seg.color,
                    pixels=seg.pixels,
                    end_color=seg.end_color,
                )
                timeline.add_segment(after_seg)
                seg.end_time = start_time

        for seg in segments_to_remove:
            timeline.remove_segment(seg)

        timeline.add_segment(new_seg)

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
        """
        Set the duration for a snippet.

        Also clamps any existing internal segments so they cannot extend
        past the new duration — important when shrinking a snippet.
        """
        snippet.duration = max(0.1, duration)
        snippet._clamp_segments_to_duration()
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
