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
        duration: Length of the snippet in seconds.
        timelines: List of Timeline objects (one per ball).
        ball_enabled: List of bools indicating which balls are included.
    """

    # Valid hotkey characters
    VALID_HOTKEYS = list("abcdefghijklmnopqrstuvwxyz0123456789")

    def __init__(self, name="New Snippet", hotkey="", duration=2.0, num_balls=3):
        """
        Initialize a new snippet.

        Args:
            name: Display name.
            hotkey: Single letter/number for Shift+hotkey trigger.
            duration: Duration in seconds.
            num_balls: Number of ball timelines to create.
        """
        self.logger = logging.getLogger("SequenceMaker.Snippet")

        self.name = name
        self.hotkey = hotkey.lower() if hotkey else ""
        self.duration = duration
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

        return snippet

    def get_duration(self):
        """Get the actual duration based on segments, or the set duration."""
        max_end = 0.0
        for i, timeline in enumerate(self.timelines):
            if self.ball_enabled[i] if i < len(self.ball_enabled) else True:
                for seg in timeline.segments:
                    if seg.end_time > max_end:
                        max_end = seg.end_time
        return max(self.duration, max_end)

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
