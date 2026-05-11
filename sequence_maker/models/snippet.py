"""
Sequence Maker - Snippet Model

This module defines the Snippet class, which represents a reusable
color pattern that can be applied to timelines via a hotkey.
"""

import logging
from datetime import datetime
from models.timeline import Timeline
from models.segment import TimelineSegment


class Snippet:
    """
    Represents a snippet - a reusable color pattern with a hotkey.

    A snippet contains mini-timelines (one per ball) that define color
    changes over a short duration. When the hotkey is pressed, the
    snippet's segments are applied to the main timelines starting at
    the current position marker, overwriting any existing segments
    in that time range.

    Attributes:
        name: Display name for the snippet.
        hotkey: A single letter or number that triggers the snippet with Shift.
        duration: Length of the snippet in seconds (used directly when
            duration_mode is "timed"; used as a max/preview length for the
            mini-timeline editor when duration_mode is "end_of_word").
        duration_mode: How the snippet's duration is determined when applied.
            "timed" — use the fixed ``duration`` value.
            "end_of_word" — extend from the insertion position until the end
            of the next timestamped lyric word (clamped to ``duration`` max).
        timelines: List of Timeline objects (one per ball).
        ball_enabled: List of bools indicating which balls are included.
    """

    # Valid hotkey characters
    VALID_HOTKEYS = list("abcdefghijklmnopqrstuvwxyz0123456789")

    # Valid duration modes
    DURATION_MODE_TIMED = "timed"
    DURATION_MODE_END_OF_WORD = "end_of_word"
    DURATION_MODE_BEGINNING_OF_WORD = "beginning_of_word"
    DURATION_MODE_VALUES = (DURATION_MODE_TIMED, DURATION_MODE_END_OF_WORD, DURATION_MODE_BEGINNING_OF_WORD)

    def __init__(self, name="New Snippet", hotkey="", duration=2.0, num_balls=3,
                 duration_mode="timed"):
        """
        Initialize a new snippet.

        Args:
            name: Display name.
            hotkey: Single letter/number for Shift+hotkey trigger.
            duration: Duration in seconds.
            num_balls: Number of ball timelines to create.
            duration_mode: "timed" or "end_of_word".
        """
        self.logger = logging.getLogger("SequenceMaker.Snippet")

        self.name = name
        self.hotkey = hotkey.lower() if hotkey else ""
        self.duration = duration
        self.duration_mode = duration_mode if duration_mode in self.DURATION_MODE_VALUES else self.DURATION_MODE_TIMED
        self.created = datetime.now().isoformat()
        self.modified = self.created

        # Create timelines - one per ball
        self.timelines = []
        self.ball_enabled = []
        for i in range(num_balls):
            timeline = Timeline(name=f"Ball {i + 1}", default_pixels=4)
            self.timelines.append(timeline)
            self.ball_enabled.append(True)

    def to_dict(self):
        """Convert the snippet to a dictionary for serialization."""
        self.modified = datetime.now().isoformat()

        return {
            "name": self.name,
            "hotkey": self.hotkey,
            "duration": self.duration,
            "durationMode": self.duration_mode,
            "created": self.created,
            "modified": self.modified,
            "timelines": [t.to_dict() for t in self.timelines],
            "ballEnabled": self.ball_enabled,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a snippet from a dictionary."""
        snippet = cls(
            name=data.get("name", "Unnamed Snippet"),
            hotkey=data.get("hotkey", ""),
            duration=data.get("duration", 2.0),
            duration_mode=data.get("durationMode", Snippet.DURATION_MODE_TIMED),
        )

        snippet.created = data.get("created", datetime.now().isoformat())
        snippet.modified = data.get("modified", snippet.created)

        # Load timelines
        snippet.timelines = []
        for timeline_data in data.get("timelines", []):
            timeline = Timeline.from_dict(timeline_data)
            snippet.timelines.append(timeline)

        # Load ball enabled flags
        snippet.ball_enabled = data.get("ballEnabled", [True] * len(snippet.timelines))

        # Ensure ball_enabled matches timelines count
        while len(snippet.ball_enabled) < len(snippet.timelines):
            snippet.ball_enabled.append(True)

        # Defensive: clamp any segments that escaped past the configured
        # duration (legacy snippets created before the duration-clamp fix
        # could have segments extending up to 3600s due to the old
        # ``add_color_at_time`` behaviour).
        snippet._clamp_segments_to_duration()

        return snippet

    def _clamp_segments_to_duration(self):
        """
        Trim any internal segments so they never extend past ``self.duration``.

        Segments fully past the duration are removed; segments overlapping
        the boundary have their ``end_time`` set to ``self.duration``.
        """
        for timeline in self.timelines:
            kept = []
            for seg in timeline.segments:
                if seg.start_time >= self.duration:
                    # Entirely past the snippet — drop it
                    continue
                if seg.end_time > self.duration:
                    seg.end_time = self.duration
                kept.append(seg)
            timeline.segments = kept

    def get_duration(self):
        """
        Get the snippet's duration in seconds.

        A snippet's duration is *always* the user-configured ``self.duration``.
        Internal segments must never extend past it; if they do (e.g. a buggy
        legacy snippet loaded from disk) callers are expected to clamp them.
        Returning the configured duration here keeps the apply-to-timeline
        logic deterministic and prevents a runaway segment from making the
        snippet "swallow" the entire main timeline.
        """
        return self.duration

    def set_ball_count(self, count):
        """Adjust the number of ball timelines."""
        while len(self.timelines) < count:
            idx = len(self.timelines)
            timeline = Timeline(name=f"Ball {idx + 1}", default_pixels=4)
            self.timelines.append(timeline)
            self.ball_enabled.append(True)
        # Don't remove timelines, just disable extras
        while len(self.ball_enabled) < len(self.timelines):
            self.ball_enabled.append(True)

    def is_valid_hotkey(cls, hotkey):
        """Check if a hotkey character is valid."""
        return hotkey.lower() in cls.VALID_HOTKEYS
