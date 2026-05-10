"""
Sequence Maker - Marker Model

This module defines the TimelineMarker class, which represents a visual
marker (dotted line) pinned to a specific time position on the timeline.
Markers are purely visual reference points and do not affect sequences.
"""

import uuid
from datetime import datetime


# Basic 6 colors available for markers
MARKER_COLORS = {
    "Red": (255, 0, 0),
    "Green": (0, 255, 0),
    "Blue": (0, 0, 255),
    "Yellow": (255, 255, 0),
    "Cyan": (0, 255, 255),
    "Magenta": (255, 0, 255),
}


class TimelineMarker:
    """
    Represents a visual marker (dotted line) pinned to a specific time on the timeline.

    Attributes:
        id (str): Unique identifier for the marker.
        time (float): Time position in seconds.
        color (tuple): RGB color tuple for the marker line, e.g. (255, 0, 0).
        created (str): ISO timestamp of creation.
    """

    def __init__(self, time=0.0, color=(255, 0, 0)):
        """
        Initialize a new timeline marker.

        Args:
            time (float): Time position in seconds.
            color (tuple): RGB color tuple for the marker line.
        """
        self.id = str(uuid.uuid4())
        self.time = float(time)
        self.color = tuple(color) if color else (255, 0, 0)
        self.created = datetime.now().isoformat()

    def to_dict(self):
        """
        Convert the marker to a dictionary for serialization.

        Returns:
            dict: Marker data as a dictionary.
        """
        return {
            "id": self.id,
            "time": self.time,
            "color": list(self.color),
            "created": self.created,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a marker from a dictionary.

        Args:
            data (dict): Marker data as a dictionary.

        Returns:
            TimelineMarker: A new TimelineMarker instance.
        """
        marker = cls(
            time=data.get("time", 0.0),
            color=tuple(data.get("color", [255, 0, 0])),
        )
        marker.id = data.get("id", marker.id)
        marker.created = data.get("created", marker.created)
        return marker

    def __repr__(self):
        return f"TimelineMarker(time={self.time:.2f}s, color={self.color})"
