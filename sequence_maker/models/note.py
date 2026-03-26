"""
Sequence Maker - Note Model

This module defines the TimelineNote class, which represents a note
attached to a specific time position on the timeline.
"""

import uuid
from datetime import datetime


class TimelineNote:
    """
    Represents a note pinned to a specific time on the timeline.

    Attributes:
        id (str): Unique identifier for the note.
        time (float): Time position in seconds.
        text (str): Note content text.
        color (tuple): RGB color tuple for the note marker, e.g. (255, 255, 0).
        created (str): ISO timestamp of creation.
        modified (str): ISO timestamp of last modification.
    """

    def __init__(self, time=0.0, text="", color=(255, 255, 0)):
        """
        Initialize a new timeline note.

        Args:
            time (float): Time position in seconds.
            text (str): Note content text.
            color (tuple): RGB color tuple for the note marker.
        """
        self.id = str(uuid.uuid4())
        self.time = float(time)
        self.text = str(text)
        self.color = tuple(color) if color else (255, 255, 0)
        self.created = datetime.now().isoformat()
        self.modified = self.created

    def to_dict(self):
        """
        Convert the note to a dictionary for serialization.

        Returns:
            dict: Note data as a dictionary.
        """
        self.modified = datetime.now().isoformat()
        return {
            "id": self.id,
            "time": self.time,
            "text": self.text,
            "color": list(self.color),
            "created": self.created,
            "modified": self.modified,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a note from a dictionary.

        Args:
            data (dict): Note data as a dictionary.

        Returns:
            TimelineNote: A new TimelineNote instance.
        """
        note = cls(
            time=data.get("time", 0.0),
            text=data.get("text", ""),
            color=tuple(data.get("color", [255, 255, 0])),
        )
        note.id = data.get("id", note.id)
        note.created = data.get("created", note.created)
        note.modified = data.get("modified", note.modified)
        return note

    def __repr__(self):
        preview = self.text[:30] + "..." if len(self.text) > 30 else self.text
        return f"TimelineNote(time={self.time:.2f}s, text='{preview}')"
