"""
Sequence Maker - Segment Model

This module defines the TimelineSegment class, which represents a color segment in a timeline.
"""

import logging
from models.effect import Effect


class TimelineSegment:
    """
    Represents a color segment in a timeline.
    
    A segment has a start time, end time, color, and optional effects.
    """
    
    def __init__(self, start_time=0.0, end_time=1.0, color=(255, 0, 0), pixels=4, end_color=None):
        """
        Initialize a new timeline segment.
        
        Args:
            start_time (float, optional): Start time in seconds. Defaults to 0.0.
            end_time (float, optional): End time in seconds. Defaults to 1.0.
            color (tuple, optional): RGB start color tuple. Defaults to (255, 0, 0) (red).
            pixels (int, optional): Number of pixels. Defaults to 4.
            end_color (tuple, optional): RGB end color tuple for fades. Defaults to None.
        """
        self.logger = logging.getLogger("SequenceMaker.TimelineSegment")
        
        # Use properties to enforce timing precision
        self._start_time = self._round_timing(start_time)
        self._end_time = self._round_timing(end_time)
        self.color = color  # Represents start_color for fades
        self.pixels = pixels
        self.end_color = end_color
        if self.end_color is not None:
            self.segment_type = 'fade'
        else:
            self.segment_type = 'solid'
        self.effects = []
        self.selected = False
    
    @staticmethod
    def _round_timing(time_value):
        """
        Round timing values to 2 decimal places (1/100th second precision).
        
        Args:
            time_value (float): Time value in seconds
            
        Returns:
            float: Rounded time value
        """
        return round(float(time_value), 2)
    
    @property
    def start_time(self):
        """Get the start time."""
        return self._start_time
    
    @start_time.setter
    def start_time(self, value):
        """Set the start time with automatic precision rounding."""
        self._start_time = self._round_timing(value)
    
    @property
    def end_time(self):
        """Get the end time."""
        return self._end_time
    
    @end_time.setter
    def end_time(self, value):
        """Set the end time with automatic precision rounding."""
        self._end_time = self._round_timing(value)
    
    def to_dict(self):
        """
        Convert the segment to a dictionary for serialization.
        
        Returns:
            dict: Segment data as a dictionary.
        """
        # Convert effects to dictionaries
        effect_dicts = [effect.to_dict() for effect in self.effects]
        
        data = {
            "startTime": self.start_time,
            "endTime": self.end_time,
            "color": list(self.color),  # This is start_color for fades
            "pixels": self.pixels,
            "effects": effect_dicts,
            "segment_type": self.segment_type
        }
        if self.segment_type == 'fade' and self.end_color is not None:
            data["endColor"] = list(self.end_color)
        return data
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a segment from a dictionary.
        
        Args:
            data (dict): Segment data as a dictionary.
        
        Returns:
            TimelineSegment: A new TimelineSegment instance.
        """
        # Round timing values when loading from dict to fix existing ultra-precise values
        segment = cls(
            start_time=cls._round_timing(data["startTime"]),
            end_time=cls._round_timing(data["endTime"]),
            color=tuple(data["color"]), # This is start_color for fades
            pixels=data["pixels"],
            end_color=tuple(data["endColor"]) if data.get("endColor") else None
        )
        # segment_type is set in __init__ based on end_color,
        # but we can also load it if it was explicitly saved.
        segment.segment_type = data.get("segment_type", segment.segment_type)

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
        
        current_base_color = self.color

        if self.segment_type == 'fade' and self.end_color is not None:
            duration = self.get_duration()
            if duration > 0:
                # Ensure time used for progress calculation is also rounded for consistency
                progress_time = self._round_timing(time)
                progress = (progress_time - self.start_time) / duration
                progress = max(0.0, min(1.0, progress))  # Clamp progress

                r_start, g_start, b_start = self.color
                r_end, g_end, b_end = self.end_color

                r = int(r_start + (r_end - r_start) * progress)
                g = int(g_start + (g_end - g_start) * progress)
                b = int(b_start + (b_end - b_start) * progress)
                current_base_color = (r, g, b)
            else:
                # If duration is 0, use the start color
                current_base_color = self.color
        
        # Apply effects to the (potentially interpolated) base color
        if self.effects:
            # Ensure time passed to effect.apply is relative to segment start
            # and the color is the (potentially interpolated) color
            time_in_segment = self._round_timing(time) - self.start_time
            processed_color = current_base_color
            for effect in self.effects:
                processed_color = effect.apply(processed_color, time_in_segment, self.get_duration())
            return processed_color
        
        return current_base_color
    
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
        # Round timing values before validation
        if start_time is not None:
            start_time = self._round_timing(start_time)
        if end_time is not None:
            end_time = self._round_timing(end_time)
            
        # Validate new times
        if start_time is not None and end_time is not None and start_time >= end_time:
            self.logger.warning("Cannot resize segment: start time must be less than end time")
            return False
        
        # Update times (properties will handle rounding)
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
        # Round the offset
        offset = self._round_timing(offset)
        
        # Validate new times
        if self.start_time + offset < 0:
            self.logger.warning("Cannot move segment: start time would be negative")
            return False
        
        # Update times (properties will handle rounding)
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
        # Round the split time
        time = self._round_timing(time)
        
        if not self.contains_time(time) or time == self.start_time: # Allow split at end_time by creating a zero-duration segment? No, PRG won't like.
            self.logger.warning(f"Cannot split segment: time {time} is outside segment [{self.start_time}, {self.end_time}) or at start boundary.")
            return None
        if time == self.end_time: # Cannot split exactly at end time to create a zero-duration new segment.
             self.logger.warning(f"Cannot split segment: time {time} is at the end boundary.")
             return None

        original_end_time = self.end_time # Store original end_time of self

        # Modify self to become the left segment
        left_segment = self
        left_segment.end_time = time # self.end_time is now 'time'
        
        # Create the new right segment
        right_segment = TimelineSegment(
            start_time=time,
            end_time=original_end_time, # Use the original end_time for the new right segment
            color=self.color,           # Right segment starts with the same base color
            pixels=self.pixels,
            end_color=self.end_color    # And same end_color if it's a fade
        )
        # segment_type will be set correctly by __init__ based on end_color
        
        # Copy effects to the new right segment
        for effect in self.effects: # Iterate over original effects of self (left_segment)
            right_segment.add_effect(effect.copy()) # Effects are copied
        
        # The left_segment (self) keeps its effects.
        # If a fade was split, both now cover part of the original fade duration
        # with the same start and end colors. User can adjust later if needed.
        
        return (left_segment, right_segment)