"""
Sequence Maker - LLM Tool Manager

This module defines the LLMToolManager class for managing LLM function definitions and execution.
"""

import logging
import json
from utils.color_utils import resolve_color_name
from .music_data_tools import MusicDataTools
from .pattern_tools import PatternTools
from .sandbox_manager import SandboxManager


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
        self.logger.debug("Initializing LLMToolManager")
        self.app = app
        
        # Action handlers
        self.action_handlers = {}
        
        # Register essential lyrics function handlers
        # Note: get_lyrics_info and get_word_timestamps are kept for sandbox use but not as direct tools
        
        # Register essential orchestrator function handlers
        self.register_action_handler("create_segment_for_word", self._handle_create_segment_for_word)
        self.register_action_handler("clear_all_timelines", self._handle_clear_all_timelines)
        
        # Initialize and register music data tools
        self.music_data_tools = MusicDataTools(app)
        self.music_data_tools.register_handlers(self)
        
        # Initialize and register pattern tools
        self.pattern_tools = PatternTools(app)
        self.pattern_tools.register_handlers(self)
        
        # Initialize sandbox manager for secure code execution
        self.sandbox_manager = SandboxManager(app)
        
        # Register sandbox function handler
        self.register_action_handler("execute_sequence_code", self._handle_execute_sequence_code)
    def register_action_handler(self, action_type, handler):
        """
        Register a handler for a specific action type.
        
        Args:
            action_type (str): The type of action to handle.
            handler (callable): The function to call when this action is requested.
        """
        self.logger.debug(f"Registering handler for action type: {action_type}")
        self.action_handlers[action_type] = handler
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
        self.logger.debug(f"Attempting to execute action: {action_type}")
        self.logger.debug(f"Available handlers: {list(self.action_handlers.keys())}")
        
        if action_type in self.action_handlers:
            try:
                self.logger.debug(f"Executing action: {action_type}")
                result = self.action_handlers[action_type](parameters)
                return result
            except Exception as e:
                self.logger.error(f"Error executing action {action_type}: {str(e)}")
                return {"error": str(e)}
        else:
            self.logger.warning(f"Handler NOT FOUND for action type: {action_type}")
            return {"error": f"No handler registered for action type: {action_type}"}
    
    def _get_available_functions(self):
        """
        Get the list of available functions for the LLM.
        
        Returns:
            list: List of function definitions.
        """
        functions = []
        registered_handlers = set(self.action_handlers.keys())
        self.logger.debug(f"Registered action handlers: {list(registered_handlers)}")
        
        # Add timeline functions if timeline manager is available
        if hasattr(self.app, 'timeline_manager'):
            self.logger.debug("Adding timeline functions")
            # Only add functions that have registered handlers
            timeline_funcs = [f for f in self.timeline_functions if f["name"] in registered_handlers]
            self.logger.debug(f"Adding {len(timeline_funcs)} of {len(self.timeline_functions)} timeline functions")
            functions.extend(timeline_funcs)
        
        # Add audio functions if audio manager is available
        if hasattr(self.app, 'audio_manager'):
            self.logger.debug("Adding audio functions")
            # Only add functions that have registered handlers
            audio_funcs = [f for f in self.audio_functions if f["name"] in registered_handlers]
            self.logger.debug(f"Adding {len(audio_funcs)} of {len(self.audio_functions)} audio functions")
            functions.extend(audio_funcs)
        
        # Add lyrics functions if lyrics manager is available
        if hasattr(self.app, 'lyrics_manager'):
            self.logger.debug("Adding lyrics functions")
            # Only add functions that have registered handlers
            lyrics_funcs = [f for f in self.lyrics_functions if f["name"] in registered_handlers]
            self.logger.debug(f"Adding {len(lyrics_funcs)} of {len(self.lyrics_functions)} lyrics functions")
            functions.extend(lyrics_funcs)
        
        # Add music data functions if audio analysis manager is available
        if hasattr(self.app, 'audio_analysis_manager'):
            self.logger.debug("Adding music data functions")
            # Only add functions that have registered handlers
            music_data_funcs = [f for f in self.music_data_tools.music_data_functions if f["name"] in registered_handlers]
            self.logger.debug(f"Adding {len(music_data_funcs)} of {len(self.music_data_tools.music_data_functions)} music data functions")
            functions.extend(music_data_funcs)
            
            # Add pattern functions if audio analysis manager is available
            self.logger.debug("Adding pattern functions")
            # Only add functions that have registered handlers
            pattern_funcs = [f for f in self.pattern_tools.pattern_functions if f["name"] in registered_handlers]
            self.logger.debug(f"Adding {len(pattern_funcs)} of {len(self.pattern_tools.pattern_functions)} pattern functions")
            functions.extend(pattern_funcs)
        
        # Log all function names being provided to the LLM
        function_names = [f["name"] for f in functions]
        self.logger.debug(f"Available functions for LLM: {function_names}")
        
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
            # Log the response structure to help with debugging
            self.logger.info("=== HANDLING FUNCTION CALL ===")
            self.logger.info(f"Response keys: {list(response.keys())}")
            if "choices" in response:
                self.logger.info(f"Choices count: {len(response['choices'])}")
                if len(response['choices']) > 0:
                    self.logger.info(f"First choice keys: {list(response['choices'][0].keys())}")
                    if "message" in response['choices'][0]:
                        self.logger.info(f"Message keys: {list(response['choices'][0]['message'].keys())}")
                        
                        # Log the content to see if it contains code blocks
                        if "content" in response['choices'][0]['message']:
                            content = response['choices'][0]['message']['content']
                            self.logger.info(f"Message content preview: {content[:100]}...")
                            
                            # Check for code blocks in the content
                            if "```" in content:
                                self.logger.info("Content contains code blocks")
            
            # Extract function call information
            function_call = response["choices"][0]["message"].get("function_call")
            
            self.logger.info(f"Function call extracted: {function_call is not None}")
            
            if not function_call:
                self.logger.info("No function call found in response")
                return None, None, None
            
            function_name = function_call.get("name")
            arguments_str = function_call.get("arguments", "{}")
            
            self.logger.info(f"Function name: {function_name}")
            self.logger.info(f"Arguments string: {arguments_str[:100]}...")
            arguments_str = function_call.get("arguments", "{}")
            
            # Parse arguments
            try:
                # Log the exact string being parsed before attempting to parse it
                self.logger.info(f"Raw arguments string for {function_name} (before parsing): {arguments_str}")
                self.logger.debug(f"Attempting to parse arguments for {function_name}: {arguments_str}")
                arguments = json.loads(arguments_str)
                self.logger.debug(f"Successfully parsed arguments: {arguments}")
                
                # Debug: Check for malformed argument values (e.g., "word=\"you\"" instead of "you")
                for key, value in arguments.items():
                    if isinstance(value, str) and (value.startswith('word=') or value.startswith('color=') or value.startswith('balls=')):
                        self.logger.warning(f"Possible malformed argument value for {key}: {value}")
                        # Try to extract the actual value from the malformed string
                        if '=' in value and value.count('"') >= 2:
                            # Extract the value between quotes
                            extracted_value = value.split('=', 1)[1].strip('"')
                            self.logger.warning(f"Extracted value: {extracted_value}")
                            # Replace the malformed value with the extracted value
                            arguments[key] = extracted_value
                            self.logger.warning(f"Corrected argument: {key}={arguments[key]}")
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON arguments for {function_name}: {arguments_str}. Error: {e}")
                return function_name, {}, {"error": f"Invalid function arguments: {arguments_str}"}
            
            # Execute the function
            result = self.execute_action(function_name, arguments)
            # Add logging to track the result
            self.logger.info(f"Result from execute_action for {function_name}: {result}")
            
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
                "name": "execute_sequence_code",
                "description": "Executes a provided Python code snippet within a secure sandbox to generate complex light sequences. Use this for loops, conditional logic, random colors, or patterns not covered by other tools.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The Python code snippet to execute. Available functions: create_segment(timeline_index, start_time, end_time, color), clear_timeline(timeline_index), modify_segment(timeline_index, segment_index, start_time, end_time, color), delete_segment(timeline_index, segment_index). Available utilities: random_color(), random_float(min_val, max_val), interpolate_color(color1, color2, factor), hsv_to_rgb(h, s, v), rgb_to_hsv(r, g, b), color_from_name(color_name). Available data: BEAT_TIMES (list), NUM_BALLS (int), SONG_DURATION (float)."
                        }
                    },
                    "required": ["code"]
                }
            },
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
                "name": "clear_all_timelines",
                "description": "Clear all segments from all timelines (all balls)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "set_black": {
                            "type": "boolean",
                            "description": "Whether to set all balls to black [0,0,0] (default: true)"
                        }
                    }
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
        # Note: These functions are no longer exposed directly to the LLM
        # They are still available in the sandbox environment
        return []
    
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
    
    def _handle_execute_sequence_code(self, parameters):
        """
        Handle the execute_sequence_code action.
        
        Args:
            parameters (dict): Action parameters.
            
        Returns:
            dict: Result of the action.
        """
        try:
            self.logger.info("=== HANDLING EXECUTE_SEQUENCE_CODE ACTION ===")
            self.logger.debug("Handling execute_sequence_code action")
            
            # Extract code from parameters
            code = parameters.get("code")
            if not code:
                self.logger.warning("No code provided for execute_sequence_code")
                return {"error": "No code provided"}
            
            self.logger.debug(f"Code to execute:\n{code}")
            
            # Prepare available context
            try:
                self.logger.info("Preparing sandbox context")
                available_context = self._prepare_sandbox_context()
                self.logger.debug(f"Prepared sandbox context: {available_context}")
            except Exception as e:
                self.logger.error(f"Error preparing sandbox context: {e}", exc_info=True)
                return {"error": f"Error preparing sandbox context: {str(e)}"}
            
            # Execute code in sandbox
            try:
                self.logger.info("Calling sandbox_manager.execute_sandboxed_code")
                result = self.sandbox_manager.execute_sandboxed_code(code, available_context)
                # Add detailed logging of the raw result
                self.logger.info(f"IMMEDIATE raw result from SandboxManager: {result}")
            except Exception as e:
                self.logger.error(f"Error executing sandboxed code: {e}", exc_info=True)
                result = {
                    "success": False,
                    "error_type": "ExecutionError",
                    "error_message": f"Error executing sandboxed code: {str(e)}"
                }
            
            # Format the result for the LLM
            try:
                self.logger.info("Formatting sandbox result")
                formatted_result = self._format_sandbox_result(result)
                self.logger.info(f"Formatted sandbox result (to be returned): {formatted_result}")
            except Exception as e:
                self.logger.error(f"Error formatting sandbox result: {e}", exc_info=True)
                formatted_result = {
                    "success": False,
                    "error": f"Error formatting sandbox result: {str(e)}"
                }
            
            self.logger.info("=== EXECUTE_SEQUENCE_CODE ACTION COMPLETED ===")
            return formatted_result
        except Exception as e:
            self.logger.error(f"Unexpected error in _handle_execute_sequence_code: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Unexpected error in execute_sequence_code: {str(e)}"
            }
    
    def _prepare_sandbox_context(self):
        """
        Prepare the context data for the sandbox.
        
        Returns:
            dict: Context data for the sandbox.
        """
        self.logger.debug("Preparing sandbox context")
        context = {}
        
        # Add beat times if available
        if hasattr(self.app, 'audio_analysis_manager'):
            self.logger.debug("Audio analysis manager is available")
            
            # Load analysis data which contains beats
            analysis_data = self.app.audio_analysis_manager.load_analysis()
            self.logger.debug(f"Got analysis data: {analysis_data is not None}")
            
            if analysis_data:
                # Extract beats from analysis data
                beats = analysis_data.get("beats", [])
                self.logger.debug(f"Got beats: {beats is not None}, count: {len(beats) if beats else 0}")
                context["BEAT_TIMES"] = beats
                
                # Add song duration
                if "duration_seconds" in analysis_data:
                    context["SONG_DURATION"] = analysis_data["duration_seconds"]
                    self.logger.debug(f"Song duration: {analysis_data['duration_seconds']} seconds")
                else:
                    context["SONG_DURATION"] = 0
                    self.logger.debug("Song duration not available in analysis data, using 0")
            else:
                self.logger.debug("No analysis data available")
                context["BEAT_TIMES"] = []
                context["SONG_DURATION"] = 0
        else:
            self.logger.debug("Audio analysis manager not available")
            context["BEAT_TIMES"] = []
            context["SONG_DURATION"] = 0
        
        # Add number of balls/timelines
        if hasattr(self.app, 'timeline_manager'):
            self.logger.debug("Timeline manager is available")
            timelines = self.app.timeline_manager.get_timelines()
            context["NUM_BALLS"] = len(timelines)
            self.logger.debug(f"Number of balls/timelines: {len(timelines)}")
        else:
            self.logger.debug("Timeline manager not available")
            context["NUM_BALLS"] = 0
        
        self.logger.debug(f"Final sandbox context: {context}")
        return context
    
    def _format_sandbox_result(self, result):
        """
        Format the sandbox execution result for the LLM.
        
        Args:
            result (dict): Sandbox execution result.
            
        Returns:
            dict: Formatted result.
        """
        if not result["success"]:
            # Format error message
            error_type = result.get("error_type", "Error")
            error_message = result.get("error_message", "Unknown error")
            
            formatted_error = {
                "success": False,
                "error": f"{error_type}: {error_message}"
            }
            
            # Include error details if available
            if "error_details" in result:
                formatted_error["error_details"] = result["error_details"]
                self.logger.error(f"Detailed sandbox error: {result['error_details']}")
            
            return formatted_error
        
        # Format success message with detailed summary
        formatted_result = {
            "success": True,
            "message": "Code executed successfully"
        }
        
        # Add variables if available
        if "variables" in result:
            formatted_result["variables"] = result["variables"]
            
            # Try to extract operation counts from variables
            try:
                # Count segments created
                segments_created = 0
                segments_modified = 0
                segments_deleted = 0
                timelines_cleared = 0
                
                # Look for variables that might contain operation results
                for var_name, var_value in result["variables"].items():
                    if isinstance(var_value, list) and len(var_value) > 0:
                        # Check if list items have segment_created key
                        if isinstance(var_value[0], dict) and "segment_created" in var_value[0]:
                            for item in var_value:
                                if item.get("segment_created", False):
                                    segments_created += 1
                        # Check if list items have segment_modified key
                        if isinstance(var_value[0], dict) and "segment_modified" in var_value[0]:
                            for item in var_value:
                                if item.get("segment_modified", False):
                                    segments_modified += 1
                        # Check if list items have segment_deleted key
                        if isinstance(var_value[0], dict) and "segment_deleted" in var_value[0]:
                            for item in var_value:
                                if item.get("segment_deleted", False):
                                    segments_deleted += 1
                        # Check if list items have timeline_cleared key
                        if isinstance(var_value[0], dict) and "timeline_cleared" in var_value[0]:
                            for item in var_value:
                                if item.get("timeline_cleared", False):
                                    timelines_cleared += 1
                
                # Add operation summary to result
                operation_summary = {}
                if segments_created > 0:
                    operation_summary["segments_created"] = segments_created
                if segments_modified > 0:
                    operation_summary["segments_modified"] = segments_modified
                if segments_deleted > 0:
                    operation_summary["segments_deleted"] = segments_deleted
                if timelines_cleared > 0:
                    operation_summary["timelines_cleared"] = timelines_cleared
                
                if operation_summary:
                    formatted_result["operation_summary"] = operation_summary
                    formatted_result["message"] = f"Code executed successfully. {self._format_operation_summary(operation_summary)}"
            except Exception as e:
                self.logger.error(f"Error extracting operation counts: {e}", exc_info=True)
        
        return formatted_result
        
    def _format_operation_summary(self, summary):
        """
        Format an operation summary into a human-readable string.
        
        Args:
            summary (dict): Operation summary.
            
        Returns:
            str: Formatted summary string.
        """
        parts = []
        if "segments_created" in summary:
            parts.append(f"{summary['segments_created']} segments created")
        if "segments_modified" in summary:
            parts.append(f"{summary['segments_modified']} segments modified")
        if "segments_deleted" in summary:
            parts.append(f"{summary['segments_deleted']} segments deleted")
        if "timelines_cleared" in summary:
            parts.append(f"{summary['timelines_cleared']} timelines cleared")
        
        if not parts:
            return "No changes made."
        
        return "Summary: " + ", ".join(parts) + "."
    
    def _handle_clear_all_timelines(self, parameters):
        """
        Handle the clear_all_timelines action.
        
        Args:
            parameters (dict): Action parameters.
            
        Returns:
            dict: Result of the action.
        """
        if not hasattr(self.app, 'timeline_manager'):
            return {"success": False, "error": "Timeline manager not available"}
        
        try:
            # Extract parameters
            set_black = parameters.get("set_black", True)
            
            # Get all timelines
            timeline_manager = self.app.timeline_manager
            timelines = timeline_manager.get_timelines()
            
            # Clear each timeline
            cleared_count = 0
            for i in range(len(timelines)):
                timeline = timeline_manager.get_timeline(i)
                if timeline:
                    timeline.clear()
                    cleared_count += 1
                    
                    # Set to black if requested
                    if set_black:
                        # Create a black segment for the entire duration
                        if hasattr(self.app, 'audio_manager') and self.app.audio_manager.duration > 0:
                            duration = self.app.audio_manager.duration
                            timeline_manager.create_segment(i, 0, duration, [0, 0, 0])
            
            # Emit timeline modified signal
            timeline_manager.timelines_modified.emit()
            
            return {
                "success": True,
                "message": f"Cleared {cleared_count} timelines",
                "timelines_cleared": cleared_count,
                "set_black": set_black
            }
            
        except Exception as e:
            self.logger.error(f"Error in _handle_clear_all_timelines: {e}", exc_info=True)
            return {"success": False, "error": f"Error clearing timelines: {str(e)}"}
    
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