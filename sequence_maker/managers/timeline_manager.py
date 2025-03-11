"""
Sequence Maker - Timeline Manager

This module defines the TimelineManager class, which handles timeline operations.
"""

import logging
from PyQt6.QtCore import QObject, pyqtSignal

from models.timeline import Timeline
from models.segment import TimelineSegment
from models.effect import Effect


class TimelineManager(QObject):
    """
    Manages timeline operations such as adding, removing, and modifying timelines and segments.
    
    Signals:
        timeline_added: Emitted when a timeline is added.
        timeline_removed: Emitted when a timeline is removed.
        timeline_modified: Emitted when a timeline is modified.
        segment_added: Emitted when a segment is added.
        segment_removed: Emitted when a segment is removed.
        segment_modified: Emitted when a segment is modified.
        segment_selected: Emitted when a segment is selected.
        position_changed: Emitted when the current position changes.
    """
    
    # Signals
    timeline_added = pyqtSignal(object)
    timeline_removed = pyqtSignal(object)
    timeline_modified = pyqtSignal(object)
    segment_added = pyqtSignal(object, object)  # timeline, segment
    segment_removed = pyqtSignal(object, object)  # timeline, segment
    segment_modified = pyqtSignal(object, object)  # timeline, segment
    segment_selected = pyqtSignal(object, object)  # timeline, segment
    position_changed = pyqtSignal(float)
    
    def __init__(self, app):
        """
        Initialize the timeline manager.
        
        Args:
            app: The main application instance.
        """
        super().__init__()
        
        self.logger = logging.getLogger("SequenceMaker.TimelineManager")
        self.app = app
        
        # Current position
        self.position = 0.0
        
        # Selected segment
        self.selected_timeline = None
        self.selected_segment = None
        
        # Undo manager
        self.undo_manager = None
    
    def set_undo_manager(self, undo_manager):
        """
        Set the undo manager.
        
        Args:
            undo_manager: The undo manager instance.
        """
        self.undo_manager = undo_manager
    
    def get_timelines(self):
        """
        Get all timelines from the current project.
        
        Returns:
            list: List of timelines, or an empty list if no project is loaded.
        """
        if not self.app.project_manager.current_project:
            return []
        
        return self.app.project_manager.current_project.timelines
    
    def get_timeline(self, index):
        """
        Get a timeline by index.
        
        Args:
            index (int): Timeline index.
        
        Returns:
            Timeline: The timeline at the specified index, or None if the index is out of range.
        """
        timelines = self.get_timelines()
        if 0 <= index < len(timelines):
            return timelines[index]
        return None
    
    def add_timeline(self, name=None, default_pixels=None):
        """
        Add a new timeline to the current project.
        
        Args:
            name (str, optional): Timeline name. If None, a default name will be generated.
            default_pixels (int, optional): Default number of pixels. If None, uses the project default.
        
        Returns:
            Timeline: The new timeline, or None if no project is loaded.
        """
        if not self.app.project_manager.current_project:
            self.logger.warning("Cannot add timeline: No project loaded")
            return None
        
        project = self.app.project_manager.current_project
        
        # Generate default name if none provided
        if name is None:
            timeline_count = len(project.timelines)
            name = f"Ball {timeline_count + 1}"
        
        # Use project default pixels if none provided
        if default_pixels is None:
            default_pixels = project.default_pixels
        
        # Create new timeline
        timeline = Timeline(name=name, default_pixels=default_pixels)
        
        # Add to project
        project.add_timeline(timeline)
        
        # Record for undo
        if self.undo_manager:
            self.undo_manager.add_action(
                "add_timeline",
                timeline=timeline,
                undo_func=self.remove_timeline,
                redo_func=self.add_timeline_object
            )
        
        # Emit signal
        self.timeline_added.emit(timeline)
        
        return timeline
    
    def add_timeline_object(self, timeline):
        """
        Add an existing timeline object to the current project.
        
        Args:
            timeline (Timeline): Timeline to add.
        
        Returns:
            Timeline: The added timeline, or None if no project is loaded.
        """
        if not self.app.project_manager.current_project:
            self.logger.warning("Cannot add timeline: No project loaded")
            return None
        
        # Add to project
        self.app.project_manager.current_project.add_timeline(timeline)
        
        # Emit signal
        self.timeline_added.emit(timeline)
        
        return timeline
    
    def remove_timeline(self, timeline):
        """
        Remove a timeline from the current project.
        
        Args:
            timeline (Timeline): Timeline to remove.
        
        Returns:
            bool: True if the timeline was removed, False otherwise.
        """
        if not self.app.project_manager.current_project:
            self.logger.warning("Cannot remove timeline: No project loaded")
            return False
        
        project = self.app.project_manager.current_project
        
        # Check if the timeline exists in the project
        if timeline not in project.timelines:
            self.logger.warning("Cannot remove timeline: Timeline not found in project")
            return False
        
        # Record for undo
        if self.undo_manager:
            timeline_index = project.timelines.index(timeline)
            self.undo_manager.add_action(
                "remove_timeline",
                timeline=timeline,
                timeline_index=timeline_index,
                undo_func=self.insert_timeline,
                redo_func=self.remove_timeline
            )
        
        # Remove from project
        success = project.remove_timeline(timeline)
        
        if success:
            # Clear selection if the selected timeline was removed
            if self.selected_timeline == timeline:
                self.clear_selection()
            
            # Emit signal
            self.timeline_removed.emit(timeline)
        
        return success
    
    def insert_timeline(self, timeline, timeline_index):
        """
        Insert a timeline at a specific index.
        
        Args:
            timeline (Timeline): Timeline to insert.
            timeline_index (int): Index to insert at.
        
        Returns:
            Timeline: The inserted timeline, or None if no project is loaded.
        """
        if not self.app.project_manager.current_project:
            self.logger.warning("Cannot insert timeline: No project loaded")
            return None
        
        project = self.app.project_manager.current_project
        
        # Insert at the specified index
        project.timelines.insert(timeline_index, timeline)
        
        # Emit signal
        self.timeline_added.emit(timeline)
        
        return timeline
    
    def duplicate_timeline(self, timeline):
        """
        Duplicate a timeline.
        
        Args:
            timeline (Timeline): Timeline to duplicate.
        
        Returns:
            Timeline: The new timeline, or None if no project is loaded.
        """
        if not self.app.project_manager.current_project:
            self.logger.warning("Cannot duplicate timeline: No project loaded")
            return None
        
        # Create a new timeline with the same properties
        new_timeline = Timeline(
            name=f"{timeline.name} (Copy)",
            default_pixels=timeline.default_pixels
        )
        
        # Copy segments
        for segment in timeline.segments:
            new_segment = TimelineSegment(
                start_time=segment.start_time,
                end_time=segment.end_time,
                color=segment.color,
                pixels=segment.pixels
            )
            
            # Copy effects
            for effect in segment.effects:
                new_segment.add_effect(effect.copy())
            
            new_timeline.add_segment(new_segment)
        
        # Add to project
        self.app.project_manager.current_project.add_timeline(new_timeline)
        
        # Record for undo
        if self.undo_manager:
            self.undo_manager.add_action(
                "add_timeline",
                timeline=new_timeline,
                undo_func=self.remove_timeline,
                redo_func=self.add_timeline_object
            )
        
        # Emit signal
        self.timeline_added.emit(new_timeline)
        
        return new_timeline
    
    def rename_timeline(self, timeline, name):
        """
        Rename a timeline.
        
        Args:
            timeline (Timeline): Timeline to rename.
            name (str): New name.
        
        Returns:
            bool: True if the timeline was renamed, False otherwise.
        """
        if not timeline:
            self.logger.warning("Cannot rename timeline: No timeline provided")
            return False
        
        # Record for undo
        if self.undo_manager:
            old_name = timeline.name
            self.undo_manager.add_action(
                "rename_timeline",
                timeline=timeline,
                old_name=old_name,
                new_name=name,
                undo_func=lambda t, n: self.rename_timeline(t, n),
                redo_func=lambda t, n: self.rename_timeline(t, n)
            )
        
        # Rename the timeline
        timeline.name = name
        
        # Emit signal
        self.timeline_modified.emit(timeline)
        
        return True
    
    def add_segment(self, timeline, start_time, end_time, color, pixels=None):
        """
        Add a segment to a timeline.
        
        Args:
            timeline (Timeline): Timeline to add the segment to.
            start_time (float): Start time in seconds.
            end_time (float): End time in seconds.
            color (tuple): RGB color tuple.
            pixels (int, optional): Number of pixels. If None, uses the timeline default.
        
        Returns:
            TimelineSegment: The new segment, or None if the timeline is invalid.
        """
        if not timeline:
            self.logger.warning("Cannot add segment: No timeline provided")
            return None
        
        # Use timeline default pixels if none provided
        if pixels is None:
            pixels = timeline.default_pixels
        
        # Create new segment
        segment = TimelineSegment(
            start_time=start_time,
            end_time=end_time,
            color=color,
            pixels=pixels
        )
        
        # Add to timeline
        timeline.add_segment(segment)
        
        # Record for undo
        if self.undo_manager:
            self.undo_manager.add_action(
                "add_segment",
                timeline=timeline,
                segment=segment,
                undo_func=self.remove_segment,
                redo_func=self.add_segment_object
            )
        
        # Emit signal
        self.segment_added.emit(timeline, segment)
        
        return segment
    
    def add_segment_object(self, timeline, segment):
        """
        Add an existing segment object to a timeline.
        
        Args:
            timeline (Timeline): Timeline to add the segment to.
            segment (TimelineSegment): Segment to add.
        
        Returns:
            TimelineSegment: The added segment, or None if the timeline is invalid.
        """
        if not timeline:
            self.logger.warning("Cannot add segment: No timeline provided")
            return None
        
        # Add to timeline
        timeline.add_segment(segment)
        
        # Emit signal
        self.segment_added.emit(timeline, segment)
        
        return segment
    
    def remove_segment(self, timeline, segment):
        """
        Remove a segment from a timeline.
        
        Args:
            timeline (Timeline): Timeline to remove the segment from.
            segment (TimelineSegment): Segment to remove.
        
        Returns:
            bool: True if the segment was removed, False otherwise.
        """
        if not timeline:
            self.logger.warning("Cannot remove segment: No timeline provided")
            return False
        
        # Check if the segment exists in the timeline
        if segment not in timeline.segments:
            self.logger.warning("Cannot remove segment: Segment not found in timeline")
            return False
        
        # Record for undo
        if self.undo_manager:
            self.undo_manager.add_action(
                "remove_segment",
                timeline=timeline,
                segment=segment,
                undo_func=self.add_segment_object,
                redo_func=self.remove_segment
            )
        
        # Remove from timeline
        success = timeline.remove_segment(segment)
        
        if success:
            # Clear selection if the selected segment was removed
            if self.selected_segment == segment:
                self.clear_selection()
            
            # Emit signal
            self.segment_removed.emit(timeline, segment)
        
        return success
    
    def modify_segment(self, timeline, segment, start_time=None, end_time=None, color=None, pixels=None):
        """
        Modify a segment.
        
        Args:
            timeline (Timeline): Timeline containing the segment.
            segment (TimelineSegment): Segment to modify.
            start_time (float, optional): New start time. If None, keeps the current start time.
            end_time (float, optional): New end time. If None, keeps the current end time.
            color (tuple, optional): New color. If None, keeps the current color.
            pixels (int, optional): New pixel count. If None, keeps the current pixel count.
        
        Returns:
            bool: True if the segment was modified, False otherwise.
        """
        if not timeline or not segment:
            self.logger.warning("Cannot modify segment: No timeline or segment provided")
            return False
        
        # Check if the segment exists in the timeline
        if segment not in timeline.segments:
            self.logger.warning("Cannot modify segment: Segment not found in timeline")
            return False
        
        # Record for undo
        if self.undo_manager:
            old_start_time = segment.start_time
            old_end_time = segment.end_time
            old_color = segment.color
            old_pixels = segment.pixels
            
            self.undo_manager.add_action(
                "modify_segment",
                timeline=timeline,
                segment=segment,
                old_start_time=old_start_time,
                old_end_time=old_end_time,
                old_color=old_color,
                old_pixels=old_pixels,
                new_start_time=start_time if start_time is not None else old_start_time,
                new_end_time=end_time if end_time is not None else old_end_time,
                new_color=color if color is not None else old_color,
                new_pixels=pixels if pixels is not None else old_pixels,
                undo_func=self._undo_modify_segment,
                redo_func=self._redo_modify_segment
            )
        
        # Modify the segment
        modified = False
        
        if start_time is not None and segment.start_time != start_time:
            segment.start_time = start_time
            modified = True
        
        if end_time is not None and segment.end_time != end_time:
            segment.end_time = end_time
            modified = True
        
        if color is not None and segment.color != color:
            segment.color = color
            modified = True
        
        if pixels is not None and segment.pixels != pixels:
            segment.pixels = pixels
            modified = True
        
        if modified:
            # Emit signal
            self.segment_modified.emit(timeline, segment)
        
        return modified
    
    def _undo_modify_segment(self, timeline, segment, old_start_time, old_end_time, old_color, old_pixels, **kwargs):
        """Undo a segment modification."""
        return self.modify_segment(
            timeline=timeline,
            segment=segment,
            start_time=old_start_time,
            end_time=old_end_time,
            color=old_color,
            pixels=old_pixels
        )
    
    def _redo_modify_segment(self, timeline, segment, new_start_time, new_end_time, new_color, new_pixels, **kwargs):
        """Redo a segment modification."""
        return self.modify_segment(
            timeline=timeline,
            segment=segment,
            start_time=new_start_time,
            end_time=new_end_time,
            color=new_color,
            pixels=new_pixels
        )
    
    def add_effect_to_segment(self, timeline, segment, effect_type, parameters=None):
        """
        Add an effect to a segment.
        
        Args:
            timeline (Timeline): Timeline containing the segment.
            segment (TimelineSegment): Segment to add the effect to.
            effect_type (str): Effect type.
            parameters (dict, optional): Effect parameters. If None, uses default parameters.
        
        Returns:
            Effect: The new effect, or None if the segment is invalid.
        """
        if not timeline or not segment:
            self.logger.warning("Cannot add effect: No timeline or segment provided")
            return None
        
        # Check if the segment exists in the timeline
        if segment not in timeline.segments:
            self.logger.warning("Cannot add effect: Segment not found in timeline")
            return None
        
        # Create new effect
        effect = Effect(effect_type=effect_type, parameters=parameters)
        
        # Record for undo
        if self.undo_manager:
            self.undo_manager.add_action(
                "add_effect",
                timeline=timeline,
                segment=segment,
                effect=effect,
                undo_func=self.remove_effect_from_segment,
                redo_func=self.add_effect_object_to_segment
            )
        
        # Add to segment
        segment.add_effect(effect)
        
        # Emit signal
        self.segment_modified.emit(timeline, segment)
        
        return effect
    
    def add_effect_object_to_segment(self, timeline, segment, effect):
        """
        Add an existing effect object to a segment.
        
        Args:
            timeline (Timeline): Timeline containing the segment.
            segment (TimelineSegment): Segment to add the effect to.
            effect (Effect): Effect to add.
        
        Returns:
            Effect: The added effect, or None if the segment is invalid.
        """
        if not timeline or not segment:
            self.logger.warning("Cannot add effect: No timeline or segment provided")
            return None
        
        # Check if the segment exists in the timeline
        if segment not in timeline.segments:
            self.logger.warning("Cannot add effect: Segment not found in timeline")
            return None
        
        # Add to segment
        segment.add_effect(effect)
        
        # Emit signal
        self.segment_modified.emit(timeline, segment)
        
        return effect
    
    def remove_effect_from_segment(self, timeline, segment, effect):
        """
        Remove an effect from a segment.
        
        Args:
            timeline (Timeline): Timeline containing the segment.
            segment (TimelineSegment): Segment to remove the effect from.
            effect (Effect): Effect to remove.
        
        Returns:
            bool: True if the effect was removed, False otherwise.
        """
        if not timeline or not segment:
            self.logger.warning("Cannot remove effect: No timeline or segment provided")
            return False
        
        # Check if the segment exists in the timeline
        if segment not in timeline.segments:
            self.logger.warning("Cannot remove effect: Segment not found in timeline")
            return False
        
        # Check if the effect exists in the segment
        if effect not in segment.effects:
            self.logger.warning("Cannot remove effect: Effect not found in segment")
            return False
        
        # Record for undo
        if self.undo_manager:
            self.undo_manager.add_action(
                "remove_effect",
                timeline=timeline,
                segment=segment,
                effect=effect,
                undo_func=self.add_effect_object_to_segment,
                redo_func=self.remove_effect_from_segment
            )
        
        # Remove from segment
        success = segment.remove_effect(effect)
        
        if success:
            # Emit signal
            self.segment_modified.emit(timeline, segment)
        
        return success
    
    def select_segment(self, timeline, segment):
        """
        Select a segment.
        
        Args:
            timeline (Timeline): Timeline containing the segment.
            segment (TimelineSegment): Segment to select.
        """
        # Deselect current segment
        if self.selected_segment:
            self.selected_segment.selected = False
        
        # Select new segment
        self.selected_timeline = timeline
        self.selected_segment = segment
        
        if segment:
            segment.selected = True
        
        # Emit signal
        self.segment_selected.emit(timeline, segment)
    
    def clear_selection(self):
        """Clear the current segment selection."""
        # Deselect current segment
        if self.selected_segment:
            self.selected_segment.selected = False
        
        # Clear selection
        self.selected_timeline = None
        self.selected_segment = None
        
        # Emit signal
        self.segment_selected.emit(None, None)
    
    def set_position(self, position):
        """
        Set the current position.
        
        Args:
            position (float): Position in seconds.
        """
        if position < 0:
            position = 0
        
        self.position = position
        
        # Emit signal
        self.position_changed.emit(position)
    
    def add_color_at_position(self, timeline_index, color, pixels=None):
        """
        Add a color at the current position.
        
        Args:
            timeline_index (int): Timeline index.
            color (tuple): RGB color tuple.
            pixels (int, optional): Number of pixels. If None, uses the timeline default.
        
        Returns:
            TimelineSegment: The new or modified segment, or None if the timeline is invalid.
        """
        self.logger.debug(f"Adding color {color} at position {self.position} to timeline {timeline_index}")
        
        timeline = self.get_timeline(timeline_index)
        if not timeline:
            self.logger.warning(f"Cannot add color: Timeline {timeline_index} not found")
            return None
        
        # Add color at current position
        self.logger.debug(f"Calling timeline.add_color_at_time with position={self.position}, color={color}")
        segment = timeline.add_color_at_time(self.position, color, pixels)
        self.logger.debug(f"Created segment: {segment}")
        
        # Record for undo
        if self.undo_manager:
            self.undo_manager.add_action(
                "add_color",
                timeline=timeline,
                segment=segment,
                position=self.position,
                color=color,
                pixels=pixels,
                undo_func=self.remove_segment,
                redo_func=self.add_segment_object
            )
        
        # Emit signal
        self.segment_added.emit(timeline, segment)
        
        return segment
    
    def get_color_at_position(self, timeline_index):
        """
        Get the color at the current position.
        
        Args:
            timeline_index (int): Timeline index.
        
        Returns:
            tuple: RGB color tuple, or None if no color is defined at the current position.
        """
        timeline = self.get_timeline(timeline_index)
        if not timeline:
            return None
        
        return timeline.get_color_at_time(self.position)