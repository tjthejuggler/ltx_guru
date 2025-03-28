"""
Sequence Maker - LLM Manager

This module defines the LLMManager class, which orchestrates LLM integration.
"""

import logging
import threading
import time
import json
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

from .llm_config import LLMConfig
from .tool_manager import LLMToolManager
from .response_processor import LLMResponseProcessor
from .tracker import LLMTracker
from .api_clients.openai_client import OpenAIClient
from .api_clients.anthropic_client import AnthropicClient
from .api_clients.local_client import LocalClient


class LLMManager(QObject):
    """
    Orchestrates LLM integration by coordinating various components.
    
    Signals:
        llm_response_received: Emitted when a response is received from the LLM.
        llm_error: Emitted when an error occurs during LLM communication.
        llm_thinking: Emitted when the LLM is processing a request.
        llm_ready: Emitted when the LLM is ready for a new request.
        llm_action_requested: Emitted when the LLM requests an action.
        token_usage_updated: Emitted when token usage is updated.
        llm_interrupted: Emitted when an LLM request is interrupted.
    """
    
    # Signals
    llm_response_received = pyqtSignal(str, dict)  # response_text, response_data
    llm_error = pyqtSignal(str)  # error_message
    llm_thinking = pyqtSignal()
    llm_ready = pyqtSignal()
    llm_action_requested = pyqtSignal(str, dict)  # action_type, parameters
    token_usage_updated = pyqtSignal(int, float)  # tokens, cost
    llm_interrupted = pyqtSignal()
    llm_ambiguity = pyqtSignal(str, list)  # prompt, suggestions
    llm_response_chunk = pyqtSignal(str)  # response_chunk
    llm_function_called = pyqtSignal(str, dict, dict)  # function_name, arguments, result
    
    def __init__(self, app):
        """
        Initialize the LLM manager.
        
        Args:
            app: The main application instance.
        """
        super().__init__()
        
        self.logger = logging.getLogger("SequenceMaker.LLMManager")
        self.app = app
        
        # Initialize components
        self.config = LLMConfig(app)
        self.tool_manager = LLMToolManager(app)
        self.response_processor = LLMResponseProcessor(self.logger)
        self.tracker = LLMTracker(app, self.config, self.token_usage_updated)
        
        # Request state
        self.is_processing = False
        self.request_thread = None
        self.interrupt_requested = False
        
        # API client (will be created when needed)
        self.api_client = None
    
    def is_configured(self):
        """
        Check if the LLM is properly configured.
        
        Returns:
            bool: True if configured, False otherwise.
        """
        return self.config.is_configured()
    
    def get_profiles(self):
        """
        Get all available LLM profiles.
        
        Returns:
            dict: Dictionary of profile configurations.
        """
        return self.config.get_profiles()
    
    def get_profile_names(self):
        """
        Get names of all available profiles.
        
        Returns:
            list: List of profile names.
        """
        return self.config.get_profile_names()
    
    def get_active_profile(self):
        """
        Get the active profile name.
        
        Returns:
            str: Name of the active profile.
        """
        return self.config.get_active_profile()
    
    def set_active_profile(self, profile_name):
        """
        Set the active profile.
        
        Args:
            profile_name (str): Name of the profile to activate.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        result = self.config.set_active_profile(profile_name)
        if result:
            # Create a new API client with the updated configuration
            self.api_client = self._create_api_client()
        return result
    
    def add_profile(self, name, provider="", api_key="", model="", temperature=0.7,
                   max_tokens=1024, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
        """
        Add a new LLM profile.
        
        Args:
            name (str): Profile name.
            provider (str): LLM provider.
            api_key (str): API key.
            model (str): Model name.
            temperature (float): Temperature parameter.
            max_tokens (int): Maximum tokens.
            top_p (float): Top-p parameter.
            frequency_penalty (float): Frequency penalty.
            presence_penalty (float): Presence penalty.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.config.add_profile(
            name, provider, api_key, model, temperature,
            max_tokens, top_p, frequency_penalty, presence_penalty
        )
    
    def update_profile(self, profile_id, **kwargs):
        """
        Update an existing LLM profile.
        
        Args:
            profile_id (str): ID of the profile to update.
            **kwargs: Profile settings to update.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        result = self.config.update_profile(profile_id, **kwargs)
        if result and profile_id == self.config.get_active_profile():
            # Create a new API client with the updated configuration
            self.api_client = self._create_api_client()
        return result
    
    def delete_profile(self, profile_id):
        """
        Delete an LLM profile.
        
        Args:
            profile_id (str): ID of the profile to delete.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.config.delete_profile(profile_id)
    
    def reload_configuration(self):
        """
        Reload the LLM configuration from the app config.
        """
        self.config = LLMConfig(self.app)
        self.api_client = self._create_api_client()
    
    def _create_api_client(self):
        """
        Create an API client based on the current configuration.
        
        Returns:
            BaseLLMClient: The API client instance.
        """
        provider = self.config.provider.lower()
        
        if provider == "openai":
            return OpenAIClient(self.config.api_key, self.config.model, self.logger)
        elif provider == "anthropic":
            return AnthropicClient(self.config.api_key, self.config.model, self.logger)
        elif provider == "local":
            return LocalClient(self.config.api_key, self.config.model, self.logger)
        else:
            self.logger.warning(f"Unknown provider: {provider}")
            return None
    
    def send_request(self, prompt, system_message=None, temperature=None, max_tokens=None, use_functions=True, stream=False, retry_count=0):
        """
        Send a request to the LLM.
        
        Args:
            prompt (str): The prompt to send.
            system_message (str, optional): System message for context.
            temperature (float, optional): Temperature parameter.
            max_tokens (int, optional): Maximum tokens to generate.
            use_functions (bool, optional): Whether to use function calling.
            stream (bool, optional): Whether to stream the response.
            retry_count (int, optional): Number of retries attempted so far. Defaults to 0.
            
        Returns:
            bool: True if the request was sent, False otherwise.
        """
        if self.is_processing and retry_count == 0:
            # Only block new requests, not retries
            self.logger.warning("LLM is already processing a request")
            return False
        
        if not self.is_configured():
            self.logger.error("LLM is not configured")
            self.llm_error.emit("LLM is not configured")
            return False
        
        # Use default values from config if not provided
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens if max_tokens is not None else self.config.max_tokens
        
        # Get preference summary if available
        preference_summary = ""
        if hasattr(self.app, 'preference_manager') and hasattr(self.app, 'audio_manager') and self.app.audio_manager.audio_file:
            # Use audio file path as song identifier
            song_identifier = self.app.audio_manager.audio_file
            preference_summary = self.app.preference_manager.get_preference_summary(song_identifier)
            self.logger.info(f"Including preference summary for {song_identifier}")
            self.logger.debug(f"Preference summary: {preference_summary}")
        
        # Prepend preference summary to system message if available
        if preference_summary and system_message:
            system_message = f"{preference_summary}\n\n{system_message}"
        elif preference_summary:
            system_message = preference_summary
        
        # Log request details
        self._log_request_details(prompt, system_message, temperature, max_tokens)
        
        # Create API client if not already created
        if self.api_client is None:
            self.api_client = self._create_api_client()
            
            if self.api_client is None:
                self.logger.error("Failed to create API client")
                self.llm_error.emit("Failed to create API client")
                return False
        
        # Save version before operation (only for initial requests, not retries)
        if retry_count == 0:
            self._save_version_before_operation(prompt)
        
        # Start request thread
        self.is_processing = True
        self.interrupt_requested = False
        self.llm_thinking.emit()
        
        self.request_thread = threading.Thread(
            target=self._request_worker,
            args=(prompt, system_message, temperature, max_tokens, use_functions, stream, retry_count)
        )
        self.request_thread.daemon = True
        self.request_thread.start()
        
        return True
    
    def _log_request_details(self, prompt, system_message, temperature, max_tokens):
        """
        Log details of an LLM request.
        
        Args:
            prompt (str): The prompt to send.
            system_message (str, optional): System message for context.
            temperature (float): Temperature parameter.
            max_tokens (int): Maximum tokens to generate.
        """
        self.logger.info(f"Sending LLM request:")
        self.logger.info(f"  Provider: {self.config.provider}")
        self.logger.info(f"  Model: {self.config.model}")
        self.logger.info(f"  Temperature: {temperature}")
        self.logger.info(f"  Max tokens: {max_tokens}")
        self.logger.debug(f"  System message: {system_message}")
        self.logger.debug(f"  Prompt: {prompt}")
    
    def _send_retry_request(self, retry_prompt, retry_count):
        """
        Send a retry request to the LLM with a corrective prompt.
        
        Args:
            retry_prompt (str): The corrective prompt to send.
            retry_count (int): The current retry count.
        """
        self.logger.info(f"Sending retry request (attempt {retry_count})")
        
        # Use the same parameters as the original request
        system_message = None  # We're including the context in the retry prompt
        temperature = self.config.temperature
        max_tokens = self.config.max_tokens
        use_functions = True
        stream = False
        
        # Send the request
        self.send_request(retry_prompt, system_message, temperature, max_tokens, use_functions, stream)
        
    def _request_worker(self, prompt, system_message, temperature, max_tokens, use_functions=True, stream=False, retry_count=0):
        """
        Worker thread for sending LLM requests.
        
        Args:
            prompt (str): The prompt to send.
            system_message (str, optional): System message for context.
            temperature (float): Temperature parameter.
            max_tokens (int): Maximum tokens to generate.
            use_functions (bool): Whether to use function calling.
            stream (bool): Whether to stream the response.
            retry_count (int, optional): Number of retries attempted so far. Defaults to 0.
        """
        start_time = time.time()
        
        try:
            # Prepare functions if needed
            functions = None
            if use_functions and self.config.provider.lower() == "openai":
                functions = self.tool_manager._get_available_functions()
            
            # Send request
            if stream and self.config.provider.lower() == "openai":
                # Streaming request
                response_text = ""
                response_chunks = []
                
                for chunk in self.api_client.send_streaming_request(
                    prompt, system_message, temperature, max_tokens, functions
                ):
                    if self.interrupt_requested:
                        self.logger.info("LLM request interrupted")
                        break
                    
                    if isinstance(chunk, dict):
                        # This is the full response object (last item)
                        response = chunk
                    else:
                        # This is a text chunk
                        response_text += chunk
                        response_chunks.append(chunk)
                        self.llm_response_chunk.emit(chunk)
                
                # Process the full response
                end_time = time.time()
                self._process_response(response, response_text, prompt, start_time, end_time, retry_count)
                
            else:
                # Non-streaming request
                response = self.api_client.send_request(
                    prompt, system_message, temperature, max_tokens, functions
                )
                
                # Log the complete raw API response for debugging
                self.logger.debug(f"==== RAW API RESPONSE START ====\n{json.dumps(response, indent=2)}\n==== RAW API RESPONSE END ====")
                
                if self.interrupt_requested:
                    self.logger.info("LLM request interrupted")
                else:
                    # Extract response text
                    response_text = self.response_processor._extract_response_text(response)
                    
                    # Process the response
                    end_time = time.time()
                    self._process_response(response, response_text, prompt, start_time, end_time, retry_count)
        
        except Exception as e:
            self.logger.error(f"Error in LLM request: {str(e)}")
            self.llm_error.emit(f"Error in LLM request: {str(e)}")
        
        finally:
            self.is_processing = False
            self.llm_ready.emit()
    
    def _process_response(self, response, response_text, prompt, start_time, end_time, retry_count=0):
        """
        Process an LLM response.
        
        Args:
            response (dict): The LLM response.
            response_text (str): The extracted response text.
            prompt (str): The original prompt.
            start_time (float): Request start time.
            end_time (float): Request end time.
            retry_count (int, optional): Number of retries attempted so far. Defaults to 0.
        """
        try:
            self.logger.info("=== PROCESSING LLM RESPONSE ===")
            # Log the raw LLM API response
            self.logger.debug(f"Raw LLM API Response: {response}")
            
            # Track token usage
            token_count, cost = self.tracker.track_token_usage(response)
            
            # Track performance metrics
            self.tracker._track_performance_metrics(
                start_time, end_time, len(prompt), len(response_text), token_count
            )
            
            # Check for function calls
            self.logger.info("Checking for function calls in response")
            try:
                function_name, arguments, result = self.tool_manager._handle_function_call(response)
                self.logger.info(f"Function call handling result: name={function_name}, has_arguments={arguments is not None}, has_result={result is not None}")
            except Exception as e:
                self.logger.error(f"Error handling function call: {e}", exc_info=True)
                function_name, arguments, result = None, None, {"error": f"Error handling function call: {str(e)}"}
            
            if function_name:
                self.logger.info(f"Processing function call: {function_name}")
                # Log the result received from tool manager
                self.logger.info(f"Result received in LLMManager from tool '{function_name}': {result}")
                
                # Log the result received from tool manager
                self.logger.info(f"Result received in LLMManager from tool '{function_name}': {result}")
                
                # Check explicitly for failure condition BEFORE assuming success
                if result is not None and (result.get('success') is False or 'error' in result):
                    self.logger.warning(f"Function call '{function_name}' failed. Result: {result}")
                    
                    # Only retry if we haven't exceeded the retry limit
                    max_retries = 2  # Limit to 2 retries to prevent infinite loops
                    if retry_count < max_retries:
                        self.logger.info(f"Attempting retry {retry_count + 1} of {max_retries}")
                        
                        # Get a list of available tools
                        available_tools_str = ", ".join(self.tool_manager.action_handlers.keys())
                        self.logger.info(f"Available tools for retry: {available_tools_str}")
                        
                        # Construct a new prompt explaining the failure
                        error_message = result.get('error', 'Unknown error')
                        
                        # Create a more directive retry prompt
                        retry_prompt = (
                            f"Your previous attempt to call function '{function_name}' failed with the error: '{error_message}'. "
                            f"That function is not available or the call was incorrect.\n\n"
                            f"Please use one of these available tools: [{available_tools_str}].\n\n"
                            f"For word-based color changes, use 'create_segment_for_word' with parameters:\n"
                            f"- word: The word in lyrics to synchronize with (e.g., 'you')\n"
                            f"- color: RGB values [R,G,B] or color name (e.g., 'red')\n"
                            f"- balls: 'all' or specific ball indices\n\n"
                            f"For complex sequences, use 'execute_sequence_code' with Python code.\n\n"
                            f"Original request: {prompt}"
                        )
                        
                        self.logger.info(f"Sending retry prompt: {retry_prompt}")
                        
                        # Re-invoke send_request with the corrective prompt
                        # We need to do this in a new thread to avoid blocking
                        threading.Thread(
                            target=self._send_retry_request,
                            args=(retry_prompt, retry_count + 1)
                        ).start()
                        
                        # Return early, as we're handling this with a retry
                        return
                elif result is not None and result.get('success') is True:
                    # This is the SUCCESS path
                    self.logger.info(f"Function call '{function_name}' succeeded.")
                else:
                    # Handle cases where result has an unexpected structure
                    self.logger.warning(f"Unexpected result structure from tool '{function_name}': {result}")
                
                # Emit function call signal
                self.logger.info(f"Emitting function_called signal for {function_name}")
                self.llm_function_called.emit(function_name, arguments, result)
                
                # Add function call result to response data
                response_data = {
                    "function_call": {
                        "name": function_name,
                        "arguments": arguments,
                        "result": result
                    }
                }
                
                # Create a summary message to feed back to the LLM
                summary_message = self._create_result_summary(function_name, arguments, result)
                self.logger.info(f"Result summary message: {summary_message}")
                
                # Log the response data that will be emitted
                self.logger.info(f"Response data to be emitted for function '{function_name}': {response_data}")
                
                # Emit response signal
                self.logger.info(f"Emitting response_received signal with function call data")
                self.llm_response_received.emit(response_text, response_data)
                
            else:
                self.logger.info("No function call detected, checking for ambiguity")
                # Check for ambiguity
                is_ambiguous, suggestions = self.response_processor._handle_ambiguity(prompt, response_text)
                
                if is_ambiguous:
                    # Emit ambiguity signal
                    self.logger.info(f"Ambiguity detected, emitting ambiguity signal with {len(suggestions)} suggestions")
                    self.llm_ambiguity.emit(prompt, suggestions)
                
                # Check for actions
                self.logger.info("Checking for actions in response text")
                actions = self.response_processor.parse_actions(response_text)
                
                if actions:
                    # Add actions to response data
                    self.logger.info(f"Found {len(actions)} actions in response")
                    response_data = {"actions": actions}
                    
                    # Emit response signal
                    self.logger.info("Emitting response_received signal with actions data")
                    self.llm_response_received.emit(response_text, response_data)
                    
                    # Execute actions
                    for action in actions:
                        self.logger.info(f"Emitting action_requested signal for action: {action['type']}")
                        self.llm_action_requested.emit(action["type"], action["parameters"])
                else:
                    # Regular response
                    self.logger.info("No actions found, emitting regular response")
                    self.llm_response_received.emit(response_text, {})
            
            # Save version after operation
            self.logger.info("Saving version after operation")
            self._save_version_after_operation(response_text)
            self.logger.info("=== LLM RESPONSE PROCESSING COMPLETED ===")
        except Exception as e:
            self.logger.error(f"Unexpected error in _process_response: {e}", exc_info=True)
            # Try to emit an error response
            try:
                self.llm_error.emit(f"Error processing LLM response: {str(e)}")
                self.llm_response_received.emit(response_text, {"error": str(e)})
            except:
                pass
    
    def _save_version_before_operation(self, prompt):
        """
        Save a version of the project before an LLM operation.
        
        Args:
            prompt (str): The prompt being sent to the LLM.
        """
        if hasattr(self.app, 'project_manager') and self.app.project_manager.current_project:
            if hasattr(self.app, 'autosave_manager'):
                # Create version metadata
                metadata = {
                    "type": "llm_request",
                    "prompt": prompt,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Save version using autosave_manager
                self.app.autosave_manager.save_version("Before LLM operation")
    
    def _create_result_summary(self, function_name, arguments, result):
        """
        Create a summary of the function call result to feed back to the LLM.
        
        Args:
            function_name (str): The name of the function called.
            arguments (dict): The arguments passed to the function.
            result (dict): The result of the function call.
            
        Returns:
            str: A summary message describing the result.
        """
        # Check if the function call was successful
        if not result.get('success', True):  # Default to True for backward compatibility
            error_message = result.get('error', 'Unknown error')
            return f"Function '{function_name}' failed with error: {error_message}"
        
        # Create a summary based on the function type
        if function_name == "execute_sequence_code":
            # Check if there's an operation summary
            if "operation_summary" in result:
                summary = result["operation_summary"]
                parts = []
                if "segments_created" in summary:
                    parts.append(f"{summary['segments_created']} segments created")
                if "segments_modified" in summary:
                    parts.append(f"{summary['segments_modified']} segments modified")
                if "segments_deleted" in summary:
                    parts.append(f"{summary['segments_deleted']} segments deleted")
                if "timelines_cleared" in summary:
                    parts.append(f"{summary['timelines_cleared']} timelines cleared")
                
                if parts:
                    return f"Code execution completed successfully. Summary: {', '.join(parts)}."
            
            # Default message if no operation summary
            return "Code execution completed successfully."
            
        elif function_name == "create_segment_for_word":
            word = arguments.get("word", "unknown")
            occurrences = result.get("occurrences", 0)
            segments_created = result.get("total_segments", 0)
            return f"Created {segments_created} color segments for {occurrences} occurrences of the word '{word}'."
            
        elif function_name == "clear_all_timelines":
            timelines_cleared = result.get("timelines_cleared", 0)
            set_black = result.get("set_black", False)
            black_msg = " and set to black" if set_black else ""
            return f"Cleared {timelines_cleared} timelines{black_msg}."
            
        # Generic summary for other functions
        return f"Function '{function_name}' executed successfully."
    
    def _save_version_after_operation(self, response_text):
        """
        Save a version of the project after an LLM operation.
        
        Args:
            response_text (str): The response from the LLM.
        """
        if hasattr(self.app, 'project_manager') and self.app.project_manager.current_project:
            if hasattr(self.app, 'autosave_manager'):
                # Create version metadata
                metadata = {
                    "type": "llm_response",
                    "response": response_text[:500] + "..." if len(response_text) > 500 else response_text,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Save version using autosave_manager
                self.app.autosave_manager.save_version("After LLM operation")
    
    def interrupt(self):
        """
        Interrupt the current LLM request.
        """
        if self.is_processing:
            self.logger.info("Interrupting LLM request")
            self.interrupt_requested = True
            self.llm_interrupted.emit()
            
            # Wait for the request thread to finish
            if self.request_thread and self.request_thread.is_alive():
                self.request_thread.join(timeout=2.0)
            
            self.is_processing = False
            self.llm_ready.emit()
    
    def register_action_handler(self, action_type, handler):
        """
        Register a handler for a specific action type.
        
        Args:
            action_type (str): The type of action to handle.
            handler (callable): The function to call when this action is requested.
        """
        self.tool_manager.register_action_handler(action_type, handler)
    
    def execute_action(self, action_type, parameters):
        """
        Execute an action with the given parameters.
        
        Args:
            action_type (str): The type of action to execute.
            parameters (dict): Parameters for the action.
            
        Returns:
            dict: Result of the action.
        """
        return self.tool_manager.execute_action(action_type, parameters)
    
    def parse_color_sequence(self, response_text):
        """
        Parse a color sequence from the response text.
        
        Args:
            response_text (str): The response text.
            
        Returns:
            list: List of color segments.
        """
        return self.response_processor.parse_color_sequence(response_text)
    
    def apply_sequence_to_timeline(self, sequence, timeline_index):
        """
        Apply a color sequence to a timeline.
        
        Args:
            sequence (list): List of color segments.
            timeline_index (int): Index of the timeline to apply to.
            
        Returns:
            int: Number of segments created.
        """
        if not hasattr(self.app, 'timeline_manager'):
            self.logger.error("Timeline manager not available")
            return 0
        
        timeline_manager = self.app.timeline_manager
        
        # Clear the timeline first
        timeline_manager.clear_timeline(timeline_index)
        
        # Add segments
        segments_created = 0
        
        for segment_data in sequence:
            start_time = segment_data.get("start_time")
            end_time = segment_data.get("end_time")
            color = segment_data.get("color")
            
            if start_time is not None and end_time is not None and color is not None:
                # Resolve color if it's a string
                if isinstance(color, str):
                    from utils.color_utils import resolve_color_name
                    color = resolve_color_name(color)
                
                # Create segment
                segment = timeline_manager.create_segment(
                    timeline_index,
                    start_time,
                    end_time,
                    color
                )
                
                if segment:
                    segments_created += 1
        
        return segments_created
    
    def generate_sequence_from_audio(self, timeline_index, prompt=None):
        """
        Generate a color sequence from audio analysis.
        
        Args:
            timeline_index (int): Index of the timeline to apply to.
            prompt (str, optional): Custom prompt for the LLM.
            
        Returns:
            bool: True if the request was sent, False otherwise.
        """
        if not hasattr(self.app, 'audio_manager'):
            self.logger.error("Audio manager not available")
            return False
        
        audio_manager = self.app.audio_manager
        
        # Get audio analysis
        analysis = audio_manager.analyze_audio()
        
        if not analysis:
            self.logger.error("No audio analysis available")
            return False
        
        # Create prompt
        if not prompt:
            prompt = (
                "Create a color sequence for a juggling ball based on the audio analysis below. "
                "The sequence should highlight key moments in the audio with appropriate colors. "
                "Return the sequence as a JSON array of segments, where each segment has a start_time, "
                "end_time, and color (as RGB values or color name).\n\n"
                f"Audio duration: {analysis['duration']:.2f} seconds\n"
                f"Beats: {analysis['beats']}\n"
                f"Tempo: {analysis['tempo']:.2f} BPM\n"
                f"Key: {analysis['key']}\n"
                f"Energy: {analysis['energy']:.2f}\n"
                f"Loudness: {analysis['loudness']:.2f} dB\n"
            )
        
        # Send request
        return self.send_request(prompt)