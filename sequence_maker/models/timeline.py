"""
Sequence Maker - Timeline Model

This module defines the Timeline class, which represents a color timeline for a ball.
"""

import logging
from datetime import datetime

from models.segment import TimelineSegment


class Timeline:
    """
    Represents a color timeline for a ball.
    
    A timeline contains a sequence of color segments that define how a ball's
    color changes over time.
    """
    
    def __init__(self, name="Ball Timeline", default_pixels=4):
        """
        Initialize a new timeline.
        
        Args:
            name (str, optional): Timeline name. Defaults to "Ball Timeline".
            default_pixels (int, optional): Default number of pixels. Defaults to 4.
        """
        self.logger = logging.getLogger("SequenceMaker.Timeline")
        
        self.name = name
        self.default_pixels = default_pixels
        self.segments = []
        self.created = datetime.now().isoformat()
        self.modified = self.created
    
    def to_dict(self):
        """
        Convert the timeline to a dictionary for serialization.
        
        Returns:
            dict: Timeline data as a dictionary.
        """
        # Convert segments to dictionaries
        segment_dicts = [segment.to_dict() for segment in self.segments]
        
        # Update modified timestamp
        self.modified = datetime.now().isoformat()
        
        return {
            "name": self.name,
            "defaultPixels": self.default_pixels,
            "created": self.created,
            "modified": self.modified,
            "segments": segment_dicts
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a timeline from a dictionary.
        
        Args:
            data (dict): Timeline data as a dictionary.
        
        Returns:
            Timeline: A new Timeline instance.
        """
        timeline = cls(
            name=data["name"],
            default_pixels=data["defaultPixels"]
        )
        
        timeline.created = data.get("created", datetime.now().isoformat())
        timeline.modified = data.get("modified", timeline.created)
        
        # Create segments
        for segment_data in data["segments"]:
            segment = TimelineSegment.from_dict(segment_data)
            timeline.segments.append(segment)
        
        return timeline
    
    def add_segment(self, segment):
        """
        Add a segment to the timeline.
        
        Args:
            segment (TimelineSegment): Segment to add.
        """
        self.segments.append(segment)
        self._sort_segments()
    
    def remove_segment(self, segment):
        """
        Remove a segment from the timeline.
        
        Args:
            segment (TimelineSegment): Segment to remove.
        
        Returns:
            bool: True if the segment was removed, False if it wasn't found.
        """
        if segment in self.segments:
            self.segments.remove(segment)
            return True
        return False
    
    def get_segment_at_time(self, time):
        """
        Get the segment at a specific time.
        
        Args:
            time (float): Time in seconds.
        
        Returns:
            TimelineSegment: The segment at the specified time, or None if no segment exists.
        """
        for segment in self.segments:
            if segment.start_time <= time < segment.end_time:
                return segment
        return None
    
    def get_color_at_time(self, time):
        """
        Get the color at a specific time.
        
        Args:
            time (float): Time in seconds.
        
        Returns:
            tuple: RGB color tuple, or None if no color is defined at the specified time.
        """
        segment = self.get_segment_at_time(time)
        if segment:
            return segment.get_color_at_time(time)
        return None
    
    def add_color_at_time(self, time, color, pixels=None):
        """
        Add a color at a specific time.
        
        This will either create a new segment or modify an existing one.
        It ensures there are no overlapping segments by removing or adjusting
        any segments that would overlap with the new one.
        
        Args:
            time (float): Time in seconds.
            color (tuple): RGB color tuple.
            pixels (int, optional): Number of pixels. If None, uses the default.
        
        Returns:
            TimelineSegment: The created or modified segment.
        """
        self.logger.debug(f"Adding color {color} at time {time}")
        
        if pixels is None:
            pixels = self.default_pixels
        
        # Find all segments that might be affected by adding a color at this time
        # First, check if there's a segment that contains this exact time
        existing_segment = self.get_segment_at_time(time)
        self.logger.debug(f"Existing segment at time {time}: {existing_segment}")
        
        if existing_segment:
            # If the segment starts exactly at this time, just update its color
            if existing_segment.start_time == time:
                existing_segment.color = color
                existing_segment.pixels = pixels
                return existing_segment
            
            # If the segment contains this time, split it
            new_segment = TimelineSegment(
                start_time=time,
                end_time=existing_segment.end_time,
                color=color,
                pixels=pixels
            )
            
            # Update the end time of the existing segment
            existing_segment.end_time = time
            
            # Add the new segment
            self.segments.append(new_segment)
            self._sort_segments()
            
            # Now check for any other segments that might overlap with the new segment
            self._remove_overlapping_segments(new_segment)
            
            return new_segment
        else:
            # Find the next segment (if any)
            next_segment = None
            for segment in self.segments:
                if segment.start_time > time:
                    if next_segment is None or segment.start_time < next_segment.start_time:
                        next_segment = segment
            
            self.logger.debug(f"Next segment after time {time}: {next_segment}")
            
            # Create a new segment
            if next_segment:
                self.logger.debug(f"Creating segment from {time} to {next_segment.start_time}")
                new_segment = TimelineSegment(
                    start_time=time,
                    end_time=next_segment.start_time,
                    color=color,
                    pixels=pixels
                )
            else:
                # If there's no next segment, create one that extends to the end of the timeline
                # Use a longer default duration that will likely cover the entire timeline
                end_time = time + 3600  # Default to 1 hour
                
                # Try to find the end of the timeline by looking at the duration of other segments
                if self.segments:
                    max_end_time = max(segment.end_time for segment in self.segments)
                    if max_end_time > time:
                        end_time = max(end_time, max_end_time)
                
                self.logger.debug(f"Creating segment from {time} to {end_time} (end of timeline)")
                new_segment = TimelineSegment(
                    start_time=time,
                    end_time=end_time,  # Extend to the end of the timeline
                    color=color,
                    pixels=pixels
                )
            
            self.segments.append(new_segment)
            self._sort_segments()
            
            # Check for any segments that might overlap with the new segment
            self._remove_overlapping_segments(new_segment)
            
            return new_segment
            
    def _remove_overlapping_segments(self, segment):
        """
        Remove or adjust any segments that overlap with the given segment.
        
        Args:
            segment (TimelineSegment): The segment to check for overlaps with.
        """
        segments_to_remove = []
        
        for other in self.segments:
            # Skip the segment itself
            if other is segment:
                continue
                
            # Check if there's an overlap
            if (other.start_time < segment.end_time and
                other.end_time > segment.start_time):
                
                self.logger.debug(f"Found overlapping segment: {other.start_time}-{other.end_time}")
                
                # If the other segment is completely contained within this segment, remove it
                if (other.start_time >= segment.start_time and
                    other.end_time <= segment.end_time):
                    segments_to_remove.append(other)
                    
                # If the other segment starts before this segment and ends within it,
                # adjust its end time
                elif other.start_time < segment.start_time and other.end_time <= segment.end_time:
                    other.end_time = segment.start_time
                    
                # If the other segment starts within this segment and ends after it,
                # adjust its start time
                elif other.start_time >= segment.start_time and other.end_time > segment.end_time:
                    other.start_time = segment.end_time
                    
                # If the other segment completely contains this segment,
                # split it into two segments
                elif other.start_time < segment.start_time and other.end_time > segment.end_time:
                    # Create a new segment for the part after this segment
                    new_other = TimelineSegment(
                        start_time=segment.end_time,
                        end_time=other.end_time,
                        color=other.color,
                        pixels=other.pixels
                    )
                    
                    # Adjust the end time of the original segment
                    other.end_time = segment.start_time
                    
                    # Add the new segment
                    self.segments.append(new_other)
        
        # Remove segments that need to be removed
        for other in segments_to_remove:
            self.segments.remove(other)
            
        # Sort segments after all modifications
        self._sort_segments()
    
    def clear(self):
        """Clear all segments from the timeline."""
        self.segments = []
    
    def _sort_segments(self):
        """Sort segments by start time."""
        self.segments.sort(key=lambda segment: segment.start_time)
    
    def get_duration(self):
        """
        Get the duration of the timeline.
        
        Returns:
            float: Duration in seconds.
        """
        if not self.segments:
            return 0
        
        return max(segment.end_time for segment in self.segments)
    
    def get_segments_in_range(self, start_time, end_time):
        """
        Get all segments that overlap with a time range.
        
        Args:
            start_time (float): Start time in seconds.
            end_time (float): End time in seconds.
        
        Returns:
            list: List of segments that overlap with the specified range.
        """
        return [
            segment for segment in self.segments
            if segment.end_time > start_time and segment.start_time < end_time
        ]
    
    def to_json_sequence(self, refresh_rate=None):
        """
        Convert the timeline to a JSON sequence for prg_generator.
        
        Args:
            refresh_rate (int, optional): Refresh rate in Hz. If None, uses 100 Hz.
                This determines the timing resolution:
                - refresh_rate=1: Each time unit is 1 second
                - refresh_rate=2: Each time unit is 0.5 seconds
                - refresh_rate=100: Each time unit is 0.01 seconds (1/100th of a second)
        
        Returns:
            dict: JSON sequence data.
        """
        if refresh_rate is None:
            refresh_rate = 100  # Default to 100 Hz for 1/100th second precision
        
        # Sort segments by start time
        sorted_segments = sorted(self.segments, key=lambda segment: segment.start_time)
        
        # Create sequence dictionary
        sequence = {}
        
        for segment in sorted_segments:
            # Convert time to time units based on refresh rate
            # We use round to avoid floating point precision issues
            time_units = round(segment.start_time * refresh_rate)
            time_key = str(time_units)
            
            # Add segment to sequence
            sequence[time_key] = {
                "color": list(segment.color),
                "pixels": segment.pixels
            }
        
        # Calculate end time in time units
        end_time_units = round(self.get_duration() * refresh_rate)
        
        return {
            "default_pixels": self.default_pixels,
            "color_format": "rgb",
            "refresh_rate": refresh_rate,
            "end_time": end_time_units,
            "sequence": sequence
        }