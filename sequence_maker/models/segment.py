"""
Sequence Maker - Segment Model

This module defines the TimelineSegment class, which represents a color segment in a timeline.
"""

import logging


class TimelineSegment:
    """
    Represents a color segment in a timeline.
    
    A segment has a start time, end time, color, and optional effects.
    """
    
    def __init__(self, start_time=0.0, end_time=1.0, color=(255, 0, 0), pixels=4):
        """
        Initialize a new timeline segment.
        
        Args:
            start_time (float, optional): Start time in seconds. Defaults to 0.0.
            end_time (float, optional): End time in seconds. Defaults to 1.0.
            color (tuple, optional): RGB color tuple. Defaults to (255, 0, 0) (red).
            pixels (int, optional): Number of pixels. Defaults to 4.
        """
        self.logger = logging.getLogger("SequenceMaker.TimelineSegment")
        
        self.start_time = start_time
        self.end_time = end_time
        self.color = color
        self.pixels = pixels
        self.effects = []
        self.selected = False
    
    def to_dict(self):
        """
        Convert the segment to a dictionary for serialization.
        
        Returns:
            dict: Segment data as a dictionary.
        """
        # Convert effects to dictionaries
        effect_dicts = [effect.to_dict() for effect in self.effects]
        
        return {
            "startTime": self.start_time,
            "endTime": self.end_time,
            "color": list(self.color),
            "pixels": self.pixels,
            "effects": effect_dicts
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a segment from a dictionary.
        
        Args:
            data (dict): Segment data as a dictionary.
        
        Returns:
            TimelineSegment: A new TimelineSegment instance.
        """
        from models.effect import Effect
        
        segment = cls(
            start_time=data["startTime"],
            end_time=data["endTime"],
            color=tuple(data["color"]),
            pixels=data["pixels"]
        )
        
        # Create effects
        for effect_data in data.get("effects", []):
            effect = Effect.from_dict(effect_data)
            segment.effects.append(effect)
        
        return segment
    
    def get_duration(self):
        """
        Get the duration of the segment.
        
        Returns:
            float: Duration in seconds.
        """
        return self.end_time - self.start_time
    
    def contains_time(self, time):
        """
        Check if the segment contains a specific time.
        
        Args:
            time (float): Time in seconds.
        
        Returns:
            bool: True if the segment contains the specified time, False otherwise.
        """
        return self.start_time <= time < self.end_time
    
    def get_color_at_time(self, time):
        """
        Get the color at a specific time, taking effects into account.
        
        Args:
            time (float): Time in seconds.
        
        Returns:
            tuple: RGB color tuple, or None if the time is outside the segment.
        """
        if not self.contains_time(time):
            return None
        
        # If there are no effects, return the base color
        if not self.effects:
            return self.color
        
        # Apply effects to the base color
        color = self.color
        for effect in self.effects:
            color = effect.apply(color, time - self.start_time, self.get_duration())
        
        return color
    
    def add_effect(self, effect):
        """
        Add an effect to the segment.
        
        Args:
            effect: Effect to add.
        """
        self.effects.append(effect)
    
    def remove_effect(self, effect):
        """
        Remove an effect from the segment.
        
        Args:
            effect: Effect to remove.
        
        Returns:
            bool: True if the effect was removed, False if it wasn't found.
        """
        if effect in self.effects:
            self.effects.remove(effect)
            return True
        return False
    
    def clear_effects(self):
        """Clear all effects from the segment."""
        self.effects = []
    
    def resize(self, start_time=None, end_time=None):
        """
        Resize the segment.
        
        Args:
            start_time (float, optional): New start time. If None, keeps the current start time.
            end_time (float, optional): New end time. If None, keeps the current end time.
        
        Returns:
            bool: True if the resize was successful, False otherwise.
        """
        # Validate new times
        if start_time is not None and end_time is not None and start_time >= end_time:
            self.logger.warning("Cannot resize segment: start time must be less than end time")
            return False
        
        # Update times
        if start_time is not None:
            self.start_time = start_time
        
        if end_time is not None:
            self.end_time = end_time
        
        return True
    
    def move(self, offset):
        """
        Move the segment by a time offset.
        
        Args:
            offset (float): Time offset in seconds.
        
        Returns:
            bool: True if the move was successful, False otherwise.
        """
        # Validate new times
        if self.start_time + offset < 0:
            self.logger.warning("Cannot move segment: start time would be negative")
            return False
        
        # Update times
        self.start_time += offset
        self.end_time += offset
        
        return True
    
    def split_at_time(self, time):
        """
        Split the segment at a specific time.
        
        Args:
            time (float): Time in seconds.
        
        Returns:
            tuple: (left_segment, right_segment) if the split was successful, None otherwise.
        """
        if not self.contains_time(time) or time == self.start_time or time == self.end_time:
            self.logger.warning("Cannot split segment: time is outside segment or at boundary")
            return None
        
        # Create left segment (original segment)
        left_segment = self
        left_segment.end_time = time
        
        # Create right segment (new segment)
        right_segment = TimelineSegment(
            start_time=time,
            end_time=self.end_time,
            color=self.color,
            pixels=self.pixels
        )
        
        # Copy effects
        for effect in self.effects:
            right_segment.add_effect(effect.copy())
        
        return (left_segment, right_segment)