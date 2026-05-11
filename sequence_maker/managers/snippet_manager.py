"""
Sequence Maker - Snippet Manager

This module defines the SnippetManager class, which manages snippet
creation, storage, and application to timelines.
"""

import json
import logging
from pathlib import Path
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

    # Path where persistent snippets are stored
    SNIPPETS_FILE = Path.home() / ".sequence_maker" / "snippets.json"

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

        # Load persisted snippets from disk (before connecting auto-save
        # so the load itself doesn't trigger a redundant write).
        self.load_snippets()

        # Auto-save whenever snippets are added, removed, or modified.
        self.snippet_added.connect(lambda _s: self.save_snippets())
        self.snippet_removed.connect(lambda _s: self.save_snippets())
        self.snippet_modified.connect(lambda _s: self.save_snippets())

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

    def _get_end_of_word_duration(self, position, max_duration):
        """
        Calculate the effective duration for an "end_of_word" snippet.

        Finds the very next time any timestamped lyric word ends after
        ``position``.  If the position is in the middle of a word, that
        word's end is used.  If the position is before a word, that
        word's end is used.  The result is clamped to ``max_duration``.
        If no word end is found after position, falls back to
        ``max_duration``.

        Args:
            position: The insertion start time in seconds.
            max_duration: Maximum allowed duration (snippet.duration).

        Returns:
            float: Effective duration in seconds.
        """
        project = self.app.project_manager.current_project
        if not project or not hasattr(project, 'lyrics') or not project.lyrics:
            return max_duration

        word_timestamps = getattr(project.lyrics, 'word_timestamps', [])
        if not word_timestamps:
            return max_duration

        # Find the first word whose end time is > position.
        # This covers both cases:
        #   - position is mid-word → that word's end is the next end
        #   - position is before a word → that word's end is the next end
        for wt in word_timestamps:
            if wt.start is None or wt.end is None:
                continue
            if wt.end > position:
                effective = wt.end - position
                # Clamp to max_duration
                effective = min(effective, max_duration)
                if effective <= 0:
                    continue
                self.logger.info(
                    f"End-of-word: next word end '{wt.word}' at "
                    f"{wt.end:.2f}s, effective duration {effective:.2f}s"
                )
                return effective

        # No word end found after position — fall back to max_duration
        self.logger.info("End-of-word: no word end found after position, using max duration")
        return max_duration

    def _get_beginning_of_word_duration(self, position, max_duration):
        """
        Calculate the effective duration for a "beginning_of_word" snippet.

        Finds the very next time any timestamped lyric word begins after
        ``position``.  The result is clamped to ``max_duration``.
        If no word start is found after position, falls back to
        ``max_duration``.

        Args:
            position: The insertion start time in seconds.
            max_duration: Maximum allowed duration (snippet.duration).

        Returns:
            float: Effective duration in seconds.
        """
        project = self.app.project_manager.current_project
        if not project or not hasattr(project, 'lyrics') or not project.lyrics:
            return max_duration

        word_timestamps = getattr(project.lyrics, 'word_timestamps', [])
        if not word_timestamps:
            return max_duration

        # Find the first word whose start time is > position.
        for wt in word_timestamps:
            if wt.start is None or wt.end is None:
                continue
            if wt.start > position:
                effective = wt.start - position
                # Clamp to max_duration
                effective = min(effective, max_duration)
                if effective <= 0:
                    continue
                self.logger.info(
                    f"Beginning-of-word: next word start '{wt.word}' at "
                    f"{wt.start:.2f}s, effective duration {effective:.2f}s"
                )
                return effective

        # No word start found after position — fall back to max_duration
        self.logger.info("Beginning-of-word: no word start found after position, using max duration")
        return max_duration

    def get_effective_duration(self, snippet, position):
        """
        Return the effective duration for a snippet at a given position.

        For "timed" mode this is simply ``snippet.duration``.
        For "end_of_word" mode this is the distance from ``position`` to
        the very next word end, clamped to ``snippet.duration``.
        For "beginning_of_word" mode this is the distance from
        ``position`` to the very next word start, clamped to
        ``snippet.duration``.

        This is a public wrapper so callers (e.g. MainWindow) can
        calculate the effective duration without actually applying the
        snippet.

        Args:
            snippet: The snippet.
            position: Start time in seconds.

        Returns:
            float: Effective duration in seconds.
        """
        duration_mode = getattr(snippet, 'duration_mode', Snippet.DURATION_MODE_TIMED)
        if duration_mode == Snippet.DURATION_MODE_END_OF_WORD:
            return self._get_end_of_word_duration(position, snippet.duration)
        if duration_mode == Snippet.DURATION_MODE_BEGINNING_OF_WORD:
            return self._get_beginning_of_word_duration(position, snippet.duration)
        return snippet.duration

    def apply_snippet(self, snippet, position):
        """
        Apply a snippet to the main timelines at the given position.

        This overwrites any existing segments in the time range
        ``[position, position + effective_duration]`` for each enabled ball
        timeline. Anything outside that window — both before ``position``
        and after ``position + effective_duration`` — is preserved exactly.

        When the snippet's ``duration_mode`` is:

        - ``"end_of_word"``: effective duration extends from ``position``
          to the very next time any word ends (clamped to
          ``snippet.duration`` as a maximum).
        - ``"beginning_of_word"``: effective duration extends from
          ``position`` to the very next time any word begins (clamped to
          ``snippet.duration`` as a maximum).
        - ``"timed"`` (default): the fixed ``snippet.duration`` is used.

        Args:
            snippet: The snippet to apply.
            position: Start time in seconds.
        """
        if not self.app.project_manager.current_project:
            self.logger.warning("No project loaded, cannot apply snippet")
            return

        project = self.app.project_manager.current_project
        main_timelines = project.timelines

        # Determine effective duration based on duration_mode
        snippet_duration = self.get_effective_duration(snippet, position)

        if snippet_duration <= 0:
            self.logger.warning(
                f"Snippet '{snippet.name}' has non-positive duration "
                f"{snippet_duration}; skipping apply."
            )
            return

        modified_timelines = []
        for i, snippet_timeline in enumerate(snippet.timelines):
            # Skip if ball is not enabled for this snippet
            if i >= len(snippet.ball_enabled) or not snippet.ball_enabled[i]:
                continue

            # Skip if main timeline doesn't exist
            if i >= len(main_timelines):
                continue

            main_timeline = main_timelines[i]
            modified_timelines.append(main_timeline)
            end_position = position + snippet_duration

            # Trim/split existing segments that overlap with the snippet range
            # so that original colors are preserved outside [position, end_position].
            #
            # IMPORTANT: We deliberately do NOT route remove/add through
            # ``timeline_manager`` here. Each ``timeline_manager.add_segment``
            # / ``remove_segment`` call pushes a new state onto the
            # undo-stack, which would cause a single snippet apply to consume
            # *many* undo slots — and Ctrl+Z would only revert the very last
            # sub-step rather than the whole snippet. Callers that want the
            # snippet apply to be undoable must call
            # ``undo_manager.save_state("apply_snippet")`` BEFORE invoking
            # ``apply_snippet`` (see ``MainWindow.keyPressEvent``); after that
            # we mutate the timeline in-place so the entire apply is exactly
            # one entry on the undo stack.
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

        # Notify the UI that the affected timelines changed so the timeline
        # widget repaints immediately. We deliberately emit ONE
        # ``timeline_modified`` signal per affected timeline (rather than
        # per-segment add/remove) — that's enough to trigger a full repaint
        # without going through ``timeline_manager.add_segment`` /
        # ``remove_segment`` (which would each call ``save_state`` and
        # pollute the undo stack — see the long comment above).
        tm = getattr(self.app, 'timeline_manager', None)
        if tm is not None:
            for tl in modified_timelines:
                try:
                    tm.timeline_modified.emit(tl)
                except Exception:
                    # Defensive: never let a UI-refresh failure break apply.
                    self.logger.exception(
                        "Failed to emit timeline_modified for timeline %r",
                        getattr(tl, 'name', '<unknown>'),
                    )
            # Also notify the project manager so anything listening to
            # project_changed (autosave, dirty-flag, etc.) updates too.
            pm = getattr(self.app, 'project_manager', None)
            if pm is not None and hasattr(pm, 'project_changed'):
                try:
                    pm.project_changed.emit()
                except Exception:
                    self.logger.exception("Failed to emit project_changed")

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

    # ------------------------------------------------------------------
    # Persistence: save / load snippets to ~/.sequence_maker/snippets.json
    # ------------------------------------------------------------------

    def save_snippets(self):
        """
        Persist all snippets to disk as JSON.

        The file is written to ``~/.sequence_maker/snippets.json`` using
        each snippet's ``to_dict()`` serialisation.  A write is a full
        overwrite — the file always reflects the current in-memory list.
        """
        try:
            self.SNIPPETS_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = [s.to_dict() for s in self.snippets]
            with open(self.SNIPPETS_FILE, "w") as f:
                json.dump(data, f, indent=2)
                f.flush()
            self.logger.debug(
                f"Saved {len(self.snippets)} snippet(s) to {self.SNIPPETS_FILE}"
            )
        except Exception as e:
            self.logger.error(f"Error saving snippets: {e}")

    def load_snippets(self):
        """
        Load persisted snippets from disk, replacing the in-memory list.

        If the file does not exist or is corrupt, the snippet list is left
        empty and the error is logged (not raised).
        """
        if not self.SNIPPETS_FILE.exists():
            self.logger.debug("No snippets file found; starting with empty list")
            return

        try:
            with open(self.SNIPPETS_FILE, "r") as f:
                data = json.load(f)

            if not isinstance(data, list):
                self.logger.warning("Snippets file is not a list; ignoring it")
                return

            self.snippets = []
            for item in data:
                try:
                    snippet = Snippet.from_dict(item)
                    self.snippets.append(snippet)
                except Exception as inner:
                    self.logger.warning(
                        f"Skipping malformed snippet: {inner}"
                    )

            self.logger.info(
                f"Loaded {len(self.snippets)} snippet(s) from {self.SNIPPETS_FILE}"
            )
        except Exception as e:
            self.logger.error(f"Error loading snippets: {e}")
