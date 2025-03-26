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
    
    def send_request(self, prompt, system_message=None, temperature=None, max_tokens=None, use_functions=True, stream=False):
        """
        Send a request to the LLM.
        
        Args:
            prompt (str): The prompt to send.
            system_message (str, optional): System message for context.
            temperature (float, optional): Temperature parameter.
            max_tokens (int, optional): Maximum tokens to generate.
            use_functions (bool, optional): Whether to use function calling.
            stream (bool, optional): Whether to stream the response.
            
        Returns:
            bool: True if the request was sent, False otherwise.
        """
        if self.is_processing:
            self.logger.warning("LLM is already processing a request")
            return False
        
        if not self.is_configured():
            self.logger.error("LLM is not configured")
            self.llm_error.emit("LLM is not configured")
            return False
        
        # Use default values from config if not provided
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens if max_tokens is not None else self.config.max_tokens
        
        # Log request details
        self._log_request_details(prompt, system_message, temperature, max_tokens)
        
        # Create API client if not already created
        if self.api_client is None:
            self.api_client = self._create_api_client()
            
            if self.api_client is None:
                self.logger.error("Failed to create API client")
                self.llm_error.emit("Failed to create API client")
                return False
        
        # Save version before operation
        self._save_version_before_operation(prompt)
        
        # Start request thread
        self.is_processing = True
        self.interrupt_requested = False
        self.llm_thinking.emit()
        
        self.request_thread = threading.Thread(
            target=self._request_worker,
            args=(prompt, system_message, temperature, max_tokens, use_functions, stream)
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
    
    def _request_worker(self, prompt, system_message, temperature, max_tokens, use_functions=True, stream=False):
        """
        Worker thread for sending LLM requests.
        
        Args:
            prompt (str): The prompt to send.
            system_message (str, optional): System message for context.
            temperature (float): Temperature parameter.
            max_tokens (int): Maximum tokens to generate.
            use_functions (bool): Whether to use function calling.
            stream (bool): Whether to stream the response.
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
                self._process_response(response, response_text, prompt, start_time, end_time)
                
            else:
                # Non-streaming request
                response = self.api_client.send_request(
                    prompt, system_message, temperature, max_tokens, functions
                )
                
                if self.interrupt_requested:
                    self.logger.info("LLM request interrupted")
                else:
                    # Extract response text
                    response_text = self.response_processor._extract_response_text(response)
                    
                    # Process the response
                    end_time = time.time()
                    self._process_response(response, response_text, prompt, start_time, end_time)
        
        except Exception as e:
            self.logger.error(f"Error in LLM request: {str(e)}")
            self.llm_error.emit(f"Error in LLM request: {str(e)}")
        
        finally:
            self.is_processing = False
            self.llm_ready.emit()
    
    def _process_response(self, response, response_text, prompt, start_time, end_time):
        """
        Process an LLM response.
        
        Args:
            response (dict): The LLM response.
            response_text (str): The extracted response text.
            prompt (str): The original prompt.
            start_time (float): Request start time.
            end_time (float): Request end time.
        """
        # Track token usage
        token_count, cost = self.tracker.track_token_usage(response)
        
        # Track performance metrics
        self.tracker._track_performance_metrics(
            start_time, end_time, len(prompt), len(response_text), token_count
        )
        
        # Check for function calls
        function_name, arguments, result = self.tool_manager._handle_function_call(response)
        
        if function_name:
            # Emit function call signal
            self.llm_function_called.emit(function_name, arguments, result)
            
            # Add function call result to response data
            response_data = {
                "function_call": {
                    "name": function_name,
                    "arguments": arguments,
                    "result": result
                }
            }
            
            # Emit response signal
            self.llm_response_received.emit(response_text, response_data)
            
        else:
            # Check for ambiguity
            is_ambiguous, suggestions = self.response_processor._handle_ambiguity(prompt, response_text)
            
            if is_ambiguous:
                # Emit ambiguity signal
                self.llm_ambiguity.emit(prompt, suggestions)
            
            # Check for actions
            actions = self.response_processor.parse_actions(response_text)
            
            if actions:
                # Add actions to response data
                response_data = {"actions": actions}
                
                # Emit response signal
                self.llm_response_received.emit(response_text, response_data)
                
                # Execute actions
                for action in actions:
                    self.llm_action_requested.emit(action["type"], action["parameters"])
            else:
                # Regular response
                self.llm_response_received.emit(response_text, {})
        
        # Save version after operation
        self._save_version_after_operation(response_text)
    
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