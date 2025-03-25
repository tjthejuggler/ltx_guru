"""
Sequence Maker - LLM Action Dispatcher

This module provides a dispatcher for LLM actions.
"""

import logging

from ui.handlers.file_handlers import FileHandlers
from ui.handlers.edit_handlers import EditHandlers
from ui.handlers.view_handlers import ViewHandlers
from ui.handlers.timeline_handlers import TimelineHandlers
from ui.handlers.playback_handlers import PlaybackHandlers
from ui.handlers.tools_handlers import ToolsHandlers
from ui.handlers.segment_handlers import SegmentHandlers
from ui.handlers.boundary_handlers import BoundaryHandlers
from ui.handlers.utility_handlers import UtilityHandlers


class LLMActionDispatcher:
    """
    Dispatcher for LLM actions.
    
    This class handles the dispatching of LLM actions to the appropriate handlers.
    """
    
    def __init__(self, window):
        """
        Initialize the LLM action dispatcher.
        
        Args:
            window: The main window instance
        """
        self.window = window
        self.logger = logging.getLogger("SequenceMaker.LLMActionDispatcher")
        
        # Initialize handlers
        self.file_handlers = FileHandlers(window)
        self.edit_handlers = EditHandlers(window)
        self.view_handlers = ViewHandlers(window)
        self.timeline_handlers = TimelineHandlers(window)
        self.playback_handlers = PlaybackHandlers(window)
        self.tools_handlers = ToolsHandlers(window)
        self.segment_handlers = SegmentHandlers(window)
        self.boundary_handlers = BoundaryHandlers(window)
        self.utility_handlers = UtilityHandlers(window)
        
        # Create action map
        self.action_map = {
            # Segment actions
            "create_segment": self.segment_handlers.handle_create_segment,
            "modify_segment": self.segment_handlers.handle_modify_segment,
            "delete_segment": self.segment_handlers.handle_delete_segment,
            "set_default_color": self.segment_handlers.handle_set_default_color,
            "add_effect": self.segment_handlers.handle_add_effect,
            "create_segments_batch": self.segment_handlers.handle_create_segments_batch,
            
            # Timeline actions
            "clear_timeline": self.timeline_handlers.handle_clear_timeline,
            
            # Playback actions
            "play_audio": self.playback_handlers.handle_play_audio,
            "pause_audio": self.playback_handlers.handle_pause_audio,
            "stop_audio": self.playback_handlers.handle_stop_audio,
            "seek_audio": self.playback_handlers.handle_seek_audio,
            "set_volume": self.playback_handlers.handle_set_volume,
        }
    
    def dispatch(self, action_type, parameters):
        """
        Dispatch an LLM action to the appropriate handler.
        
        Args:
            action_type (str): The type of action to dispatch
            parameters (dict): The parameters for the action
        """
        if action_type in self.action_map:
            self.action_map[action_type](parameters)
        else:
            self.logger.warning(f"Unknown LLM action type: {action_type}")