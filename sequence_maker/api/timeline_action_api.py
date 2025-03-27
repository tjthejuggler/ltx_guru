"""
Sequence Maker - Timeline Action API

This module defines the TimelineActionAPI class, which provides an API for LLM to manipulate timelines.
"""

import logging


class TimelineActionAPI:
    """
    Provides an API for LLM to manipulate timelines.
    """
    
    def __init__(self, app):
        """
        Initialize the timeline action API.
        
        Args:
            app: The main application instance.
        """
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.TimelineActionAPI")
        
        # Register action handlers with the LLM manager
        self.app.llm_manager.register_action_handler("create_segment", self.create_segment)
        self.app.llm_manager.register_action_handler("modify_segment", self.modify_segment)
        self.app.llm_manager.register_action_handler("delete_segment", self.delete_segment)
        self.app.llm_manager.register_action_handler("set_default_color", self.set_default_color)
        self.app.llm_manager.register_action_handler("add_effect", self.add_effect)
        self.app.llm_manager.register_action_handler("clear_timeline", self.clear_timeline)
        self.app.llm_manager.register_action_handler("clear_all_timelines", self.clear_all_timelines)
        self.app.llm_manager.register_action_handler("create_segments_batch", self.create_segments_batch)
    
    def create_segment(self, parameters):
        """
        Create a new segment in a timeline.
        
        Args:
            parameters (dict): Parameters for the action.
                - timeline_index (int): Timeline index.
                - start_time (float): Start time in seconds.
                - end_time (float): End time in seconds.
                - color (list): RGB color list [r, g, b].
                - pixels (int, optional): Number of pixels.
        
        Returns:
            dict: Result of the operation.
        """
        try:
            # Save state for undo
            if self.app.undo_manager:
                self.app.undo_manager.save_state("llm_create_segment")
            
            # Extract parameters
            timeline_index = parameters.get("timeline_index")
            start_time = parameters.get("start_time")
            end_time = parameters.get("end_time")
            color = parameters.get("color")
            pixels = parameters.get("pixels")
            
            # Validate parameters
            if timeline_index is None or start_time is None or end_time is None or color is None:
                return {"success": False, "error": "Missing required parameters"}
            
            # Get timeline
            timeline = self.app.timeline_manager.get_timeline(timeline_index)
            if not timeline:
                return {"success": False, "error": f"Timeline {timeline_index} not found"}
            
            # Convert color list to tuple
            color_tuple = tuple(color)
            
            # Create segment
            segment = self.app.timeline_manager.add_segment(
                timeline=timeline,
                start_time=start_time,
                end_time=end_time,
                color=color_tuple,
                pixels=pixels
            )
            
            if segment:
                return {
                    "success": True,
                    "segment": {
                        "start_time": segment.start_time,
                        "end_time": segment.end_time,
                        "color": list(segment.color),
                        "pixels": segment.pixels
                    }
                }
            else:
                return {"success": False, "error": "Failed to create segment"}
        
        except Exception as e:
            self.logger.error(f"Error creating segment: {e}")
            return {"success": False, "error": str(e)}
    
    def modify_segment(self, parameters):
        """
        Modify an existing segment.
        
        Args:
            parameters (dict): Parameters for the action.
                - timeline_index (int): Timeline index.
                - segment_index (int): Segment index.
                - properties (dict): Properties to modify.
                    - start_time (float, optional): New start time.
                    - end_time (float, optional): New end time.
                    - color (list, optional): New RGB color list [r, g, b].
                    - pixels (int, optional): New pixel count.
        
        Returns:
            dict: Result of the operation.
        """
        try:
            # Save state for undo
            if self.app.undo_manager:
                self.app.undo_manager.save_state("llm_modify_segment")
            
            # Extract parameters
            timeline_index = parameters.get("timeline_index")
            segment_index = parameters.get("segment_index")
            properties = parameters.get("properties", {})
            
            # Validate parameters
            if timeline_index is None or segment_index is None:
                return {"success": False, "error": "Missing required parameters"}
            
            # Get timeline
            timeline = self.app.timeline_manager.get_timeline(timeline_index)
            if not timeline:
                return {"success": False, "error": f"Timeline {timeline_index} not found"}
            
            # Get segment
            if segment_index < 0 or segment_index >= len(timeline.segments):
                return {"success": False, "error": f"Segment {segment_index} not found"}
            
            segment = timeline.segments[segment_index]
            
            # Prepare parameters
            start_time = properties.get("start_time")
            end_time = properties.get("end_time")
            
            color = None
            if "color" in properties:
                color = tuple(properties["color"])
            
            pixels = properties.get("pixels")
            
            # Modify segment
            success = self.app.timeline_manager.modify_segment(
                timeline=timeline,
                segment=segment,
                start_time=start_time,
                end_time=end_time,
                color=color,
                pixels=pixels
            )
            
            if success:
                return {
                    "success": True,
                    "segment": {
                        "start_time": segment.start_time,
                        "end_time": segment.end_time,
                        "color": list(segment.color),
                        "pixels": segment.pixels
                    }
                }
            else:
                return {"success": False, "error": "Failed to modify segment"}
        
        except Exception as e:
            self.logger.error(f"Error modifying segment: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_segment(self, parameters):
        """
        Delete a segment from a timeline.
        
        Args:
            parameters (dict): Parameters for the action.
                - timeline_index (int): Timeline index.
                - segment_index (int): Segment index.
        
        Returns:
            dict: Result of the operation.
        """
        try:
            # Save state for undo
            if self.app.undo_manager:
                self.app.undo_manager.save_state("llm_delete_segment")
            
            # Extract parameters
            timeline_index = parameters.get("timeline_index")
            segment_index = parameters.get("segment_index")
            
            # Validate parameters
            if timeline_index is None or segment_index is None:
                return {"success": False, "error": "Missing required parameters"}
            
            # Get timeline
            timeline = self.app.timeline_manager.get_timeline(timeline_index)
            if not timeline:
                return {"success": False, "error": f"Timeline {timeline_index} not found"}
            
            # Get segment
            if segment_index < 0 or segment_index >= len(timeline.segments):
                return {"success": False, "error": f"Segment {segment_index} not found"}
            
            segment = timeline.segments[segment_index]
            
            # Remove segment
            success = self.app.timeline_manager.remove_segment(timeline, segment)
            
            return {"success": success}
        
        except Exception as e:
            self.logger.error(f"Error deleting segment: {e}")
            return {"success": False, "error": str(e)}
    
    def set_default_color(self, parameters):
        """
        Set the default color for a timeline.
        
        Args:
            parameters (dict): Parameters for the action.
                - timeline_index (int): Timeline index.
                - color (list): RGB color list [r, g, b].
        
        Returns:
            dict: Result of the operation.
        """
        try:
            # Save state for undo
            if self.app.undo_manager:
                self.app.undo_manager.save_state("llm_set_default_color")
            
            # Extract parameters
            timeline_index = parameters.get("timeline_index")
            color = parameters.get("color")
            
            # Validate parameters
            if timeline_index is None or color is None:
                return {"success": False, "error": "Missing required parameters"}
            
            # Get timeline
            timeline = self.app.timeline_manager.get_timeline(timeline_index)
            if not timeline:
                return {"success": False, "error": f"Timeline {timeline_index} not found"}
            
            # Convert color list to tuple
            color_tuple = tuple(color)
            
            # Set default color
            timeline.default_pixels = color_tuple
            
            # Emit signal
            self.app.timeline_manager.timeline_modified.emit(timeline)
            
            return {"success": True}
        
        except Exception as e:
            self.logger.error(f"Error setting default color: {e}")
            return {"success": False, "error": str(e)}
    
    def add_effect(self, parameters):
        """
        Add an effect to a segment.
        
        Args:
            parameters (dict): Parameters for the action.
                - timeline_index (int): Timeline index.
                - segment_index (int): Segment index.
                - effect_type (str): Effect type.
                - effect_parameters (dict): Effect parameters.
        
        Returns:
            dict: Result of the operation.
        """
        try:
            # Save state for undo
            if self.app.undo_manager:
                self.app.undo_manager.save_state("llm_add_effect")
            
            # Extract parameters
            timeline_index = parameters.get("timeline_index")
            segment_index = parameters.get("segment_index")
            effect_type = parameters.get("effect_type")
            effect_parameters = parameters.get("effect_parameters", {})
            
            # Validate parameters
            if timeline_index is None or segment_index is None or effect_type is None:
                return {"success": False, "error": "Missing required parameters"}
            
            # Get timeline
            timeline = self.app.timeline_manager.get_timeline(timeline_index)
            if not timeline:
                return {"success": False, "error": f"Timeline {timeline_index} not found"}
            
            # Get segment
            if segment_index < 0 or segment_index >= len(timeline.segments):
                return {"success": False, "error": f"Segment {segment_index} not found"}
            
            segment = timeline.segments[segment_index]
            
            # Create effect
            from models.effect import Effect
            effect = Effect(effect_type=effect_type, parameters=effect_parameters)
            
            # Add effect to segment
            segment.add_effect(effect)
            
            # Emit signal
            self.app.timeline_manager.segment_modified.emit(timeline, segment)
            
            return {"success": True}
        
        except Exception as e:
            self.logger.error(f"Error adding effect: {e}")
            return {"success": False, "error": str(e)}
    
    def clear_timeline(self, parameters):
        """
        Clear all segments from a timeline.
        
        Args:
            parameters (dict): Parameters for the action.
                - timeline_index (int): Timeline index.
        
        Returns:
            dict: Result of the operation.
        """
        try:
            # Save state for undo
            if self.app.undo_manager:
                self.app.undo_manager.save_state("llm_clear_timeline")
            
            # Extract parameters
            timeline_index = parameters.get("timeline_index")
            
            # Validate parameters
            if timeline_index is None:
                return {"success": False, "error": "Missing required parameters"}
            
            # Get timeline
            timeline = self.app.timeline_manager.get_timeline(timeline_index)
            if not timeline:
                return {"success": False, "error": f"Timeline {timeline_index} not found"}
            
            # Clear timeline
            timeline.clear()
            
            # Emit signal
            self.app.timeline_manager.timeline_modified.emit(timeline)
            
            return {"success": True}
        
        except Exception as e:
            self.logger.error(f"Error clearing timeline: {e}")
            return {"success": False, "error": str(e)}
            
    def clear_all_timelines(self, parameters):
        """
        Clear all segments from all timelines.
        
        Args:
            parameters (dict): Parameters for the action.
                - set_black (bool, optional): Whether to set all balls to black [0,0,0] (default: True)
        
        Returns:
            dict: Result of the operation.
        """
        try:
            # Save state for undo
            if self.app.undo_manager:
                self.app.undo_manager.save_state("llm_clear_all_timelines")
            
            # Extract parameters
            set_black = parameters.get("set_black", True)
            
            # Get all timelines
            timelines = []
            if hasattr(self.app.project_manager, 'current_project') and self.app.project_manager.current_project:
                timelines = self.app.project_manager.current_project.timelines
            
            if not timelines:
                return {"success": False, "error": "No timelines found in current project"}
            
            # Clear all timelines
            cleared_count = 0
            for i, timeline in enumerate(timelines):
                # Clear existing segments
                timeline.clear()
                
                # If set_black is True, add a black segment at time 0
                if set_black:
                    black_color = (0, 0, 0)  # Black color
                    
                    # Get project duration
                    duration = 0
                    if hasattr(self.app.project_manager.current_project, 'total_duration'):
                        duration = self.app.project_manager.current_project.total_duration
                    elif hasattr(self.app.audio_manager, 'duration'):
                        duration = self.app.audio_manager.duration
                    
                    if duration > 0:
                        # Add a black segment for the entire duration
                        self.app.timeline_manager.add_segment(
                            timeline=timeline,
                            start_time=0,
                            end_time=duration,
                            color=black_color
                        )
                
                # Emit signal
                self.app.timeline_manager.timeline_modified.emit(timeline)
                cleared_count += 1
            
            return {
                "success": True,
                "timelines_cleared": cleared_count,
                "set_black": set_black
            }
        
        except Exception as e:
            self.logger.error(f"Error clearing all timelines: {e}")
            return {"success": False, "error": str(e)}
    
    def create_segments_batch(self, parameters):
        """
        Create multiple segments in a timeline in a single operation.
        
        Args:
            parameters (dict): Parameters for the action.
                - timeline_index (int): Timeline index.
                - segments (list): List of segment definitions.
                    - start_time (float): Start time in seconds.
                    - end_time (float): End time in seconds.
                    - color (list): RGB color list [r, g, b].
                    - pixels (int, optional): Number of pixels.
        
        Returns:
            dict: Result of the operation.
        """
        try:
            # Save state for undo
            if self.app.undo_manager:
                self.app.undo_manager.save_state("llm_create_segments_batch")
            
            # Extract parameters
            timeline_index = parameters.get("timeline_index")
            segments_data = parameters.get("segments", [])
            
            # Validate parameters
            if timeline_index is None or not segments_data:
                return {"success": False, "error": "Missing required parameters"}
            
            # Get timeline
            timeline = self.app.timeline_manager.get_timeline(timeline_index)
            if not timeline:
                return {"success": False, "error": f"Timeline {timeline_index} not found"}
            
            # Create segments
            created_segments = []
            for segment_data in segments_data:
                start_time = segment_data.get("start_time")
                end_time = segment_data.get("end_time")
                color = segment_data.get("color")
                pixels = segment_data.get("pixels")
                
                if start_time is None or end_time is None or color is None:
                    continue
                
                # Convert color list to tuple
                color_tuple = tuple(color)
                
                # Create segment
                segment = self.app.timeline_manager.add_segment(
                    timeline=timeline,
                    start_time=start_time,
                    end_time=end_time,
                    color=color_tuple,
                    pixels=pixels
                )
                
                if segment:
                    created_segments.append({
                        "start_time": segment.start_time,
                        "end_time": segment.end_time,
                        "color": list(segment.color),
                        "pixels": segment.pixels
                    })
            
            return {
                "success": True,
                "segments_created": len(created_segments),
                "segments": created_segments
            }
        
        except Exception as e:
            self.logger.error(f"Error creating segments batch: {e}")
            return {"success": False, "error": str(e)}