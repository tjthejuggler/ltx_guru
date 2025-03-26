"""
Sequence Maker - LLM Tool Manager

This module defines the LLMToolManager class for managing LLM function definitions and execution.
"""

import logging
import json
from utils.color_utils import resolve_color_name


class LLMToolManager:
    """
    Manages LLM function definitions and execution.
    """
    
    def __init__(self, app):
        """
        Initialize the LLM tool manager.
        
        Args:
            app: The main application instance.
        """
        self.logger = logging.getLogger("SequenceMaker.LLMToolManager")
        self.app = app
        
        # Action handlers
        self.action_handlers = {}
        
        # Register lyrics function handlers
        self.register_action_handler("get_lyrics_info", self._handle_get_lyrics_info)
        self.register_action_handler("get_word_timestamps", self._handle_get_word_timestamps)
        self.register_action_handler("find_first_word", self._handle_find_first_word)
        
        # Register orchestrator function handlers
        self.register_action_handler("create_segment_for_word", self._handle_create_segment_for_word)
    
    def register_action_handler(self, action_type, handler):
        """
        Register a handler for a specific action type.
        
        Args:
            action_type (str): The type of action to handle.
            handler (callable): The function to call when this action is requested.
        """
        self.action_handlers[action_type] = handler
    
    def execute_action(self, action_type, parameters):
        """
        Execute an action with the given parameters.
        
        Args:
            action_type (str): The type of action to execute.
            parameters (dict): Parameters for the action.
            
        Returns:
            dict: Result of the action.
        """
        if action_type in self.action_handlers:
            try:
                self.logger.debug(f"Executing action: {action_type}")
                result = self.action_handlers[action_type](parameters)
                return result
            except Exception as e:
                self.logger.error(f"Error executing action {action_type}: {str(e)}")
                return {"error": str(e)}
        else:
            self.logger.warning(f"No handler registered for action type: {action_type}")
            return {"error": f"No handler registered for action type: {action_type}"}
    
    def _get_available_functions(self):
        """
        Get the list of available functions for the LLM.
        
        Returns:
            list: List of function definitions.
        """
        functions = []
        
        # Add timeline functions if timeline manager is available
        if hasattr(self.app, 'timeline_manager'):
            functions.extend(self.timeline_functions)
        
        # Add audio functions if audio manager is available
        if hasattr(self.app, 'audio_manager'):
            functions.extend(self.audio_functions)
        
        # Add lyrics functions if lyrics manager is available
        if hasattr(self.app, 'lyrics_manager'):
            functions.extend(self.lyrics_functions)
        
        return functions
    
    def _handle_function_call(self, response):
        """
        Handle a function call from the LLM.
        
        Args:
            response (dict): The LLM response containing the function call.
            
        Returns:
            tuple: (function_name, arguments, result)
        """
        try:
            # Extract function call information
            function_call = response["choices"][0]["message"].get("function_call")
            
            if not function_call:
                return None, None, None
            
            function_name = function_call.get("name")
            arguments_str = function_call.get("arguments", "{}")
            
            # Parse arguments
            try:
                arguments = json.loads(arguments_str)
            except json.JSONDecodeError:
                self.logger.error(f"Invalid function arguments: {arguments_str}")
                return function_name, {}, {"error": "Invalid function arguments"}
            
            # Execute the function
            result = self.execute_action(function_name, arguments)
            
            return function_name, arguments, result
            
        except Exception as e:
            self.logger.error(f"Error handling function call: {str(e)}")
            return None, None, {"error": str(e)}
    
    # Function definitions
    
    @property
    def timeline_functions(self):
        """
        Get the timeline function definitions.
        
        Returns:
            list: List of timeline function definitions.
        """
        return [
            {
                "name": "create_segment_for_word",
                "description": "Creates color segments on specified juggling balls precisely during the occurrences of a specific word in the song lyrics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "word": {
                            "type": "string",
                            "description": "The word in the lyrics to synchronize the color change to"
                        },
                        "color": {
                            "oneOf": [
                                {
                                    "type": "array",
                                    "description": "RGB color values (0-255)",
                                    "items": {
                                        "type": "integer",
                                        "minimum": 0,
                                        "maximum": 255
                                    },
                                    "minItems": 3,
                                    "maxItems": 3
                                },
                                {
                                    "type": "string",
                                    "description": "Color name (e.g., 'red', 'green', 'blue', etc.)"
                                }
                            ],
                            "description": "The RGB color ([R, G, B]) or color name for the segment"
                        },
                        "balls": {
                            "oneOf": [
                                {
                                    "type": "array",
                                    "description": "List of ball indices",
                                    "items": {
                                        "type": "integer",
                                        "minimum": 0
                                    }
                                },
                                {
                                    "type": "string",
                                    "enum": ["all"],
                                    "description": "Apply to all balls"
                                }
                            ],
                            "description": "A list of ball indices or 'all' to apply the segment to"
                        }
                    },
                    "required": ["word", "color"],
                    "additionalProperties": False
                }
            },
            {
                "name": "create_segment",
                "description": "Create a new segment in a timeline",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timeline_index": {
                            "type": "integer",
                            "description": "Index of the timeline to add the segment to"
                        },
                        "start_time": {
                            "type": "number",
                            "description": "Start time of the segment in seconds"
                        },
                        "end_time": {
                            "type": "number",
                            "description": "End time of the segment in seconds"
                        },
                        "color": {
                            "type": "array",
                            "description": "RGB color values (0-255)",
                            "items": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 255
                            },
                            "minItems": 3,
                            "maxItems": 3
                        }
                    },
                    "required": ["timeline_index", "start_time", "end_time", "color"]
                }
            },
            {
                "name": "delete_segment",
                "description": "Delete a segment from a timeline",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timeline_index": {
                            "type": "integer",
                            "description": "Index of the timeline containing the segment"
                        },
                        "segment_index": {
                            "type": "integer",
                            "description": "Index of the segment to delete"
                        }
                    },
                    "required": ["timeline_index", "segment_index"]
                }
            },
            {
                "name": "modify_segment",
                "description": "Modify an existing segment in a timeline",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timeline_index": {
                            "type": "integer",
                            "description": "Index of the timeline containing the segment"
                        },
                        "segment_index": {
                            "type": "integer",
                            "description": "Index of the segment to modify"
                        },
                        "properties": {
                            "type": "object",
                            "properties": {
                                "start_time": {
                                    "type": "number",
                                    "description": "New start time of the segment in seconds"
                                },
                                "end_time": {
                                    "type": "number",
                                    "description": "New end time of the segment in seconds"
                                },
                                "color": {
                                    "type": "array",
                                    "description": "New RGB color values (0-255)",
                                    "items": {
                                        "type": "integer",
                                        "minimum": 0,
                                        "maximum": 255
                                    },
                                    "minItems": 3,
                                    "maxItems": 3
                                }
                            }
                        }
                    },
                    "required": ["timeline_index", "segment_index", "properties"]
                }
            },
            {
                "name": "clear_timeline",
                "description": "Clear all segments from a timeline",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timeline_index": {
                            "type": "integer",
                            "description": "Index of the timeline to clear"
                        }
                    },
                    "required": ["timeline_index"]
                }
            },
            {
                "name": "create_segments_batch",
                "description": "Create multiple segments in a timeline in a single operation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timeline_index": {
                            "type": "integer",
                            "description": "Index of the timeline to add segments to"
                        },
                        "segments": {
                            "type": "array",
                            "description": "List of segment definitions",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "start_time": {
                                        "type": "number",
                                        "description": "Start time of the segment in seconds"
                                    },
                                    "end_time": {
                                        "type": "number",
                                        "description": "End time of the segment in seconds"
                                    },
                                    "color": {
                                        "type": "array",
                                        "description": "RGB color values (0-255)",
                                        "items": {
                                            "type": "integer",
                                            "minimum": 0,
                                            "maximum": 255
                                        },
                                        "minItems": 3,
                                        "maxItems": 3
                                    }
                                },
                                "required": ["start_time", "end_time", "color"]
                            }
                        }
                    },
                    "required": ["timeline_index", "segments"]
                }
            }
        ]
    
    @property
    def audio_functions(self):
        """
        Get the audio function definitions.
        
        Returns:
            list: List of audio function definitions.
        """
        return [
            {
                "name": "play_audio",
                "description": "Play the loaded audio file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_time": {
                            "type": "number",
                            "description": "Start time in seconds (optional)"
                        }
                    }
                }
            },
            {
                "name": "pause_audio",
                "description": "Pause audio playback",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "stop_audio",
                "description": "Stop audio playback",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "seek_audio",
                "description": "Seek to a specific position in the audio",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "position": {
                            "type": "number",
                            "description": "Position in seconds"
                        }
                    },
                    "required": ["position"]
                }
            }
        ]
    
    @property
    def lyrics_functions(self):
        """
        Get the lyrics function definitions.
        
        Returns:
            list: List of lyrics function definitions.
        """
        return [
            {
                "name": "get_lyrics_info",
                "description": "Get information about the current song lyrics",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_word_timestamps",
                "description": "Get timestamps for words in the lyrics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "word": {
                            "type": "string",
                            "description": "Specific word to find (optional). If not provided, returns all word timestamps."
                        },
                        "start_time": {
                            "type": "number",
                            "description": "Start time in seconds for filtering words (optional)"
                        },
                        "end_time": {
                            "type": "number",
                            "description": "End time in seconds for filtering words (optional)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of word timestamps to return (optional)"
                        }
                    }
                }
            },
            {
                "name": "find_first_word",
                "description": "Find the first word in the lyrics",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    # Handler implementations
    
    def _handle_get_lyrics_info(self, parameters):
        """
        Handle the get_lyrics_info action.
        
        Args:
            parameters (dict): Action parameters.
            
        Returns:
            dict: Lyrics information.
        """
        if not hasattr(self.app, 'lyrics_manager'):
            return {"error": "Lyrics manager not available"}
        
        # Check if the project has lyrics data
        if not hasattr(self.app.project_manager, 'current_project') or not self.app.project_manager.current_project:
            return {"error": "No project loaded"}
        
        project = self.app.project_manager.current_project
        if not hasattr(project, 'lyrics') or not project.lyrics:
            return {"error": "No lyrics loaded"}
        
        lyrics = project.lyrics
        
        return {
            "title": lyrics.title,
            "artist": lyrics.artist,
            "text": lyrics.text,
            "word_count": len(lyrics.words) if lyrics.words else 0,
            "has_timestamps": lyrics.has_timestamps(),
            "duration": lyrics.duration if lyrics.has_timestamps() else None
        }
    
    def _handle_get_word_timestamps(self, parameters):
        """
        Handle the get_word_timestamps action.
        
        Args:
            parameters (dict): Action parameters.
            
        Returns:
            dict: Word timestamps.
        """
        if not hasattr(self.app, 'lyrics_manager'):
            return {"error": "Lyrics manager not available"}
        
        # Check if the project has lyrics data
        if not hasattr(self.app.project_manager, 'current_project') or not self.app.project_manager.current_project:
            return {"error": "No project loaded"}
        
        project = self.app.project_manager.current_project
        if not hasattr(project, 'lyrics') or not project.lyrics:
            return {"error": "No lyrics loaded"}
        
        lyrics = project.lyrics
        
        if not hasattr(lyrics, 'word_timestamps') or not lyrics.word_timestamps:
            return {"error": "Lyrics do not have timestamps"}
        
        # Extract parameters
        word = parameters.get("word")
        start_time = parameters.get("start_time")
        end_time = parameters.get("end_time")
        limit = parameters.get("limit")
        
        # Get all words with timestamps
        words_with_timestamps = []
        
        for w in lyrics.word_timestamps:
            if hasattr(w, 'start') and w.start is not None:
                # Filter by word if specified
                if word and hasattr(w, 'word') and w.word.lower() != word.lower():
                    continue
                
                # Filter by time range if specified
                if start_time is not None and w.start < start_time:
                    continue
                if end_time is not None and w.start > end_time:
                    continue
                
                words_with_timestamps.append({
                    "word": w.word if hasattr(w, 'word') else "",
                    "start_time": w.start,
                    "end_time": w.end,
                    "line_index": getattr(w, 'line_index', 0),
                    "word_index": getattr(w, 'word_index', 0)
                })
        
        # Apply limit if specified
        if limit is not None:
            words_with_timestamps = words_with_timestamps[:limit]
        
        return {
            "words": words_with_timestamps,
            "count": len(words_with_timestamps)
        }
    
    def _handle_find_first_word(self, parameters):
        """
        Handle the find_first_word action.
        
        Args:
            parameters (dict): Action parameters.
            
        Returns:
            dict: First word information.
        """
        if not hasattr(self.app, 'lyrics_manager'):
            return {"error": "Lyrics manager not available"}
        
        # Check if the project has lyrics data
        if not hasattr(self.app.project_manager, 'current_project') or not self.app.project_manager.current_project:
            return {"error": "No project loaded"}
        
        project = self.app.project_manager.current_project
        if not hasattr(project, 'lyrics') or not project.lyrics:
            return {"error": "No lyrics loaded"}
        
        lyrics = project.lyrics
        
        if not hasattr(lyrics, 'word_timestamps') or not lyrics.word_timestamps:
            return {"error": "Lyrics do not have timestamps"}
        
        # Find the first word with a timestamp
        first_word = None
        for word in lyrics.word_timestamps:
            if hasattr(word, 'start') and word.start is not None:
                first_word = word
                break
        
        if first_word is None:
            return {"error": "No words with timestamps found"}
        
        return {
            "word": first_word.word if hasattr(first_word, 'word') else "",
            "start_time": first_word.start,
            "end_time": first_word.end,
            "line_index": getattr(first_word, 'line_index', 0),
            "word_index": getattr(first_word, 'word_index', 0)
        }
    
    def _resolve_color_name(self, color_input):
        """
        Resolve a color name to RGB values.
        
        Args:
            color_input: Color name or RGB values.
            
        Returns:
            list: RGB values.
        """
        # If already RGB values, return as is
        if isinstance(color_input, list) and len(color_input) == 3:
            return color_input
        
        # If string, try to resolve as color name
        if isinstance(color_input, str):
            return resolve_color_name(color_input)
        
        # Default to white if invalid
        return [255, 255, 255]
    
    def _handle_create_segment_for_word(self, parameters):
        """
        Handle the create_segment_for_word action.
        
        Args:
            parameters (dict): Action parameters.
            
        Returns:
            dict: Result of the action.
        """
        if not hasattr(self.app, 'lyrics_manager') or not hasattr(self.app, 'timeline_manager'):
            return {"error": "Required managers not available"}
        
        lyrics_manager = self.app.lyrics_manager
        timeline_manager = self.app.timeline_manager
        
        # Check if the project has lyrics data
        if not hasattr(self.app.project_manager, 'current_project') or not self.app.project_manager.current_project:
            return {"error": "No project loaded"}
        
        project = self.app.project_manager.current_project
        if not hasattr(project, 'lyrics') or not project.lyrics:
            return {"error": "No lyrics loaded"}
        
        lyrics = project.lyrics
        
        if not hasattr(lyrics, 'word_timestamps') or not lyrics.word_timestamps:
            return {"error": "Lyrics do not have timestamps"}
        
        # Extract parameters
        word = parameters.get("word")
        color_input = parameters.get("color")
        balls_input = parameters.get("balls", "all")
        
        if not word:
            return {"error": "Word parameter is required"}
        
        if not color_input:
            return {"error": "Color parameter is required"}
        
        # Resolve color
        color = self._resolve_color_name(color_input)
        
        # Get word timestamps directly from lyrics
        word_timestamps = []
        
        for w in lyrics.word_timestamps:
            if hasattr(w, 'word') and w.word.lower() == word.lower() and hasattr(w, 'start') and w.start is not None:
                word_timestamps.append({
                    "word": w.word,
                    "start_time": w.start,
                    "end_time": w.end
                })
        
        if not word_timestamps:
            return {"error": f"No occurrences of word '{word}' found in lyrics"}
        
        # Determine which balls to apply to
        if balls_input == "all":
            # Get all available timelines
            timelines = timeline_manager.get_timelines()
            balls = list(range(len(timelines)))
        else:
            balls = balls_input
        
        # Create segments for each occurrence of the word on each ball
        segments_created = []
        
        timelines = timeline_manager.get_timelines()
        for ball_index in balls:
            if ball_index >= len(timelines):
                continue
            
            for word_info in word_timestamps:
                start_time = word_info["start_time"]
                end_time = word_info["end_time"]
                
                # Get the timeline
                timeline = timeline_manager.get_timeline(ball_index)
                if not timeline:
                    continue
                
                # Set the position to the start time
                timeline_manager.set_position(start_time)
                
                # Create segment using add_color_at_position which handles overlapping segments
                segment = timeline_manager.add_color_at_position(
                    ball_index,
                    color
                )
                
                # Set the end time of the segment
                if segment:
                    segment.end_time = end_time
                
                segments_created.append({
                    "ball_index": ball_index,
                    "start_time": start_time,
                    "end_time": end_time,
                    "color": color,
                    "segment_index": None  # TimelineSegment doesn't have an index attribute
                })
        
        return {
            "word": word,
            "color": color,
            "balls": balls,
            "occurrences": len(word_timestamps),
            "segments_created": segments_created,
            "total_segments": len(segments_created)
        }
    
    def _format_time(self, seconds):
        """
        Format time in seconds to a human-readable string.
        
        Args:
            seconds (float): Time in seconds.
            
        Returns:
            str: Formatted time string.
        """
        minutes = int(seconds // 60)
        seconds = seconds % 60
        return f"{minutes}:{seconds:05.2f}"