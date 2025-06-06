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
                existing_segment.color = color
                existing_segment.pixels = pixels
                # If it was a fade, setting a single color here makes it solid
                existing_segment.end_color = None
                existing_segment.segment_type = 'solid'
                return existing_segment
            
            # If the segment contains this time, split it
            # The new segment created by add_color_at_time is always a solid segment
            new_segment = TimelineSegment(
                start_time=time,
                end_time=existing_segment.end_time,
                color=color, # This is the start_color
                pixels=pixels,
                end_color=None # Solid segment
            )
            
            # Update the end time of the existing segment
            # The existing segment properties (color, end_color, type) remain for its new, shorter duration
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
                    color=color, # This is the start_color
                    pixels=pixels,
                    end_color=None # Solid segment
                )
            else:
                # If there's no next segment, create one that extends to the end of the timeline
                # This new segment is solid.
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
                    color=color, # This is the start_color
                    pixels=pixels,
                    end_color=None # Solid segment
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
                        color=other.color, # This is start_color
                        pixels=other.pixels,
                        end_color=other.end_color # Preserve fade if other was a fade
                    )
                    # new_other's segment_type is set by its __init__

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
    
    def to_json_sequence(self): # refresh_rate parameter removed
        """
        Convert the timeline to a JSON sequence for prg_generator.py.
        The output JSON will always have a refresh_rate of 1000 Hz.
        Segment times from .smproj (in seconds) are converted to 1000Hz time units.
        
        This method rounds all timing values to 3 decimal places before conversion
        to prevent ultra-precise floating-point values from causing timing issues
        in the generated PRG files.
                
        Returns:
            dict: JSON sequence data with timings scaled to 1000Hz.
        """
        # Target refresh rate for the output JSON is always 1000Hz
        output_json_refresh_rate = 1000
        
        # Round timing values to 2 decimal places (1/100th second precision) to prevent
        # ultra-precise floating-point values from causing timing issues
        def round_timing(time_value):
            return round(time_value, 2)
        
        # Sort segments by start time
        sorted_segments = sorted(self.segments, key=lambda segment: segment.start_time)
        
        # Create sequence dictionary
        sequence = {}
        
        # Apply timing gap fix to ensure segments don't have exact overlaps
        adjusted_segments = []
        gap_size = 0.01  # 0.01 second gap between segments
        
        for i, segment in enumerate(sorted_segments):
            # Round timing values to prevent ultra-precise floating-point issues
            rounded_start_time = round_timing(segment.start_time)
            rounded_end_time = round_timing(segment.end_time)
            
            
            # Store adjusted segment info for next iteration
            adjusted_segments.append({
                'start_time': rounded_start_time,
                'end_time': rounded_end_time,
                'color': segment.color, # This is start_color
                'end_color': segment.end_color,
                'segment_type': segment.segment_type,
                'pixels': segment.pixels
            })
            
            # Convert time to time units based on the target 1000Hz refresh rate
            time_units = round(rounded_start_time * output_json_refresh_rate)
            time_key = str(time_units)
            
            # Add segment to sequence
            segment_data_for_json = {
                "pixels": segment.pixels
            }
            if segment.segment_type == 'fade' and segment.end_color is not None:
                segment_data_for_json["start_color"] = list(segment.color)
                segment_data_for_json["end_color"] = list(segment.end_color)
            else: # solid
                segment_data_for_json["color"] = list(segment.color)
            
            sequence[time_key] = segment_data_for_json
            
            # Check if there's a gap between this segment and the next one
            # If so, add a black color block at the end of this segment
            next_adjusted_segment = adjusted_segments[i + 1] if i + 1 < len(adjusted_segments) else None
            
            if next_adjusted_segment:
                next_start_time = next_adjusted_segment['start_time']
                # If there's a gap between the end of this segment and the start of the next
                if rounded_end_time < next_start_time:
                    # Add a black color block at the end of this segment
                    end_time_units = round(rounded_end_time * output_json_refresh_rate)
                    end_time_key = str(end_time_units)
                    
                    # Add black color block with the same number of pixels
                    sequence[end_time_key] = {
                        "color": [0, 0, 0],  # Black color
                        "pixels": segment.pixels
                    }
            else:
                # If this is the last segment, add a black color block at its end
                end_time_units = round(rounded_end_time * output_json_refresh_rate)
                end_time_key = str(end_time_units)
                
                # Add black color block with the same number of pixels
                sequence[end_time_key] = {
                    "color": [0, 0, 0],  # Black color
                    "pixels": segment.pixels
                }
        
        # Calculate end time in time units using the maximum end time from adjusted segments
        if adjusted_segments:
            max_end_time = max(seg['end_time'] for seg in adjusted_segments)
            rounded_duration = round_timing(max_end_time)
        else:
            rounded_duration = round_timing(self.get_duration())
        end_time_units = round(rounded_duration * output_json_refresh_rate)
        
        return {
            "default_pixels": self.default_pixels,
            "color_format": "rgb",
            "refresh_rate": output_json_refresh_rate, # Hardcoded to 1000
            "end_time": end_time_units,
            "sequence": sequence
        }