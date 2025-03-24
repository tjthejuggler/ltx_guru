"""
Sequence Maker - LLM Manager

This module defines the LLMManager class, which handles integration with language models.
"""

import logging
import json
import threading
import time
import os
import requests
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

from app.constants import DEFAULT_LLM_TEMPERATURE, DEFAULT_LLM_MAX_TOKENS


class LLMManager(QObject):
    """
    Manages integration with language models for automatic sequence generation.
    
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
        
        # LLM configuration
        self.enabled = app.config.get("llm", "enabled")
        self.provider = app.config.get("llm", "provider")
        self.api_key = app.config.get("llm", "api_key")
        self.model = app.config.get("llm", "model")
        self.temperature = app.config.get("llm", "temperature")
        
        # Request state
        self.is_processing = False
        self.request_thread = None
        self.interrupt_requested = False
        
        # Token tracking
        self.token_usage = 0
        self.estimated_cost = 0.0
        self.token_prices = {
            "openai": {
                "gpt-3.5-turbo": 0.0015,  # per 1K tokens
                "gpt-4": 0.03,  # per 1K tokens
            },
            "anthropic": {
                "claude-2": 0.01,  # per 1K tokens
                "claude-instant": 0.0025,  # per 1K tokens
            },
            "local": {
                "default": 0.0  # Local models are free
            }
        }
        
        # Action handlers
        self.action_handlers = {}
        
        # Function definitions
        self.timeline_functions = [
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
        
        self.audio_functions = [
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
    
    def is_configured(self):
        """
        Check if the LLM is properly configured.
        
        Returns:
            bool: True if configured, False otherwise.
        """
        return (
            self.enabled and
            self.provider and
            self.api_key and
            self.model
        )
    
    def _get_available_functions(self):
        """
        Get the list of available functions for function calling.
        
        Returns:
            list: List of function definitions.
        """
        # Combine all function definitions
        functions = []
        functions.extend(self.timeline_functions)
        functions.extend(self.audio_functions)
        
        return functions
    
    def send_request(self, prompt, system_message=None, temperature=None, max_tokens=None, use_functions=True, stream=False):
        """
        Send a request to the language model.
        
        Args:
            prompt (str): User prompt.
            system_message (str, optional): System message. If None, uses a default message.
            temperature (float, optional): Temperature parameter. If None, uses the configured value.
            max_tokens (int, optional): Maximum tokens in the response. If None, uses the default value.
            use_functions (bool, optional): Whether to use function calling. Default is True.
            stream (bool, optional): Whether to use streaming responses. Default is False.
        
        Returns:
            bool: True if the request was sent, False otherwise.
        """
        if not self.is_configured():
            self.logger.warning("Cannot send request: LLM not configured")
            self.llm_error.emit("LLM not configured")
            return False
        
        if self.is_processing:
            self.logger.warning("Cannot send request: Already processing a request")
            self.llm_error.emit("Already processing a request")
            return False
        
        # Set default system message if not provided
        if system_message is None:
            system_message = (
                "You are an assistant that helps create color sequences for juggling balls. "
                "You can analyze music and suggest color patterns that match the rhythm, mood, and style of the music. "
                "Your responses should be clear and specific, describing exact colors and timings."
            )
        
        # Set default temperature if not provided
        if temperature is None:
            temperature = self.temperature or DEFAULT_LLM_TEMPERATURE
        
        # Set default max_tokens if not provided
        if max_tokens is None:
            max_tokens = DEFAULT_LLM_MAX_TOKENS
        
        # Set processing state
        self.is_processing = True
        
        # Emit thinking signal
        self.llm_thinking.emit()
        
        # Start request thread
        self.request_thread = threading.Thread(
            target=self._request_worker,
            args=(prompt, system_message, temperature, max_tokens, use_functions, stream),
            daemon=True
        )
        self.request_thread.start()
        
        return True
    
    def _log_request_details(self, prompt, system_message, temperature, max_tokens):
        """
        Log detailed information about an LLM request.
        
        Args:
            prompt (str): User prompt.
            system_message (str): System message.
            temperature (float): Temperature parameter.
            max_tokens (int): Maximum tokens in the response.
        """
        self.logger.info(f"LLM Request Details:")
        self.logger.info(f"Provider: {self.provider}")
        self.logger.info(f"Model: {self.model}")
        self.logger.info(f"Temperature: {temperature}")
        self.logger.info(f"Max Tokens: {max_tokens}")
        self.logger.info(f"Prompt Length: {len(prompt)} characters")
        self.logger.info(f"System Message Length: {len(system_message)} characters")
        
        # Log truncated versions of prompt and system message
        max_log_length = 100
        prompt_truncated = prompt[:max_log_length] + "..." if len(prompt) > max_log_length else prompt
        system_truncated = system_message[:max_log_length] + "..." if len(system_message) > max_log_length else system_message
        
        self.logger.info(f"Prompt (truncated): {prompt_truncated}")
        self.logger.info(f"System Message (truncated): {system_truncated}")
    
    def _track_performance_metrics(self, start_time, end_time, prompt_length, response_length, tokens):
        """
        Track performance metrics for an LLM request.
        
        Args:
            start_time (float): Request start time.
            end_time (float): Request end time.
            prompt_length (int): Length of the prompt in characters.
            response_length (int): Length of the response in characters.
            tokens (int): Number of tokens used.
        """
        duration = end_time - start_time
        
        # Log metrics
        self.logger.info(f"LLM Request Performance Metrics:")
        self.logger.info(f"Duration: {duration:.2f} seconds")
        self.logger.info(f"Tokens: {tokens}")
        self.logger.info(f"Tokens per second: {tokens / duration:.2f}")
        self.logger.info(f"Characters per second: {response_length / duration:.2f}")
        
        # Store metrics in project metadata
        if self.app.project_manager.current_project:
            if not hasattr(self.app.project_manager.current_project, "llm_performance_metrics"):
                self.app.project_manager.current_project.llm_performance_metrics = []
            
            self.app.project_manager.current_project.llm_performance_metrics.append({
                "timestamp": datetime.now().isoformat(),
                "duration": duration,
                "tokens": tokens,
                "prompt_length": prompt_length,
                "response_length": response_length,
                "tokens_per_second": tokens / duration,
                "characters_per_second": response_length / duration,
                "model": self.model,
                "provider": self.provider
            })
            
            # Mark project as changed
            self.app.project_manager.project_changed.emit()
            
        self.logger.info(f"Tracked performance metrics: {duration:.2f} seconds, {tokens} tokens")

    def _send_openai_streaming_request(self, prompt, system_message, temperature, max_tokens):
        """
        Send a streaming request to the OpenAI API.
        
        Args:
            prompt (str): User prompt.
            system_message (str): System message.
            temperature (float): Temperature parameter.
            max_tokens (int): Maximum tokens in the response.
        
        Yields:
            str: Chunks of the response text.
        """
        self.logger.info("Sending streaming request to OpenAI API")
        
        try:
            # Prepare request
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
            
            # Send request
            response = requests.post(url, headers=headers, json=data, stream=True, timeout=60)
            
            # Check for errors
            response.raise_for_status()
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    # Remove "data: " prefix
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        line = line[6:]
                    
                    # Skip "[DONE]" message
                    if line == "[DONE]":
                        break
                    
                    try:
                        # Parse JSON
                        chunk = json.loads(line)
                        
                        # Extract content
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            self.logger.error(f"Error in OpenAI streaming request: {e}")
            yield f"Error: {str(e)}"

    def _request_worker(self, prompt, system_message, temperature, max_tokens, use_functions=True, stream=False):
        """
        Worker thread for sending requests to the language model.
        
        Args:
            prompt (str): User prompt.
            system_message (str): System message.
            temperature (float): Temperature parameter.
            max_tokens (int): Maximum tokens in the response.
            use_functions (bool): Whether to use function calling.
            stream (bool): Whether to use streaming responses.
        """
        try:
            # Reset interrupt flag
            self.interrupt_requested = False
            
            # Save project state before LLM operation
            self._save_version_before_operation(prompt)
            
            # Log request details
            self._log_request_details(prompt, system_message, temperature, max_tokens)
            
            # Record start time for performance metrics
            start_time = time.time()
            
            # Prepare functions if needed
            functions = None
            if use_functions and self.provider == "openai":
                functions = self._get_available_functions()
            
            # Handle streaming requests
            if stream and self.provider == "openai":
                # Emit streaming start signal
                self.llm_thinking.emit()
                
                # Initialize response text
                response_text = ""
                
                # Send streaming request
                for chunk in self._send_openai_streaming_request(prompt, system_message, temperature, max_tokens):
                    # Append chunk to response text
                    response_text += chunk
                    
                    # Emit chunk signal
                    self.llm_response_chunk.emit(chunk)
                    
                    # Check if interrupt was requested
                    if self.interrupt_requested:
                        self.logger.info("LLM streaming request was interrupted")
                        return
                
                # Create a mock response for token tracking
                response = {
                    "choices": [{"message": {"content": response_text}}],
                    "usage": {"prompt_tokens": len(prompt) // 4, "completion_tokens": len(response_text) // 4}
                }
                
                # Record end time for performance metrics
                end_time = time.time()
                
                # Process response as normal
                self._process_response(response, response_text, prompt, start_time, end_time)
                
                return
            
            # Prepare request based on provider
            if self.provider == "openai":
                response = self._send_openai_request(prompt, system_message, temperature, max_tokens, functions)
            elif self.provider == "anthropic":
                response = self._send_anthropic_request(prompt, system_message, temperature, max_tokens)
            elif self.provider == "local":
                response = self._send_local_model_request(prompt, system_message, temperature, max_tokens)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
            
            # Record end time for performance metrics
            end_time = time.time()
            
            # Check if interrupt was requested
            if self.interrupt_requested:
                self.logger.info("LLM request was interrupted")
                return
            
            # Process response
            if response:
                # Check for function call
                if use_functions and self.provider == "openai":
                    message = response.get("choices", [{}])[0].get("message", {})
                    if "function_call" in message:
                        # Handle function call
                        result = self._handle_function_call(response)
                        
                        # Extract response text (function call description)
                        function_name = message["function_call"]["name"]
                        arguments = json.loads(message["function_call"]["arguments"])
                        
                        # Create a human-readable description of the function call
                        response_text = f"I'll {function_name.replace('_', ' ')} with the following parameters:\n"
                        response_text += json.dumps(arguments, indent=2)
                        response_text += f"\n\nResult: {json.dumps(result, indent=2)}"
                        
                        # Process response
                        self._process_response(response, response_text, prompt, start_time, end_time)
                        
                        # Emit function call signal
                        self.llm_function_called.emit(function_name, arguments, result)
                        
                        return
                
                # Extract response text
                response_text = self._extract_response_text(response)
                
                # Process response
                self._process_response(response, response_text, prompt, start_time, end_time)
            else:
                self.llm_error.emit("No response from LLM")
        
        except Exception as e:
            self.logger.error(f"Error in LLM request: {e}")
            self.llm_error.emit(f"Error: {str(e)}")
        
        finally:
            # Reset processing state
            self.is_processing = False
            self.interrupt_requested = False
            
            # Emit ready signal
            self.llm_ready.emit()
    
    def _process_response(self, response, response_text, prompt, start_time, end_time):
        """
        Process an LLM response.
        
        Args:
            response (dict): API response.
            response_text (str): Extracted response text.
            prompt (str): Original prompt.
            start_time (float): Request start time.
            end_time (float): Request end time.
        """
        # Track token usage
        self.track_token_usage(response)
        
        # Track performance metrics
        prompt_length = len(prompt)
        response_length = len(response_text)
        tokens = self._get_token_count_from_response(response)
        self._track_performance_metrics(start_time, end_time, prompt_length, response_length, tokens)
        
        # Check for ambiguity in the response
        if not self._handle_ambiguity(prompt, response_text):
            # If not ambiguous, proceed with normal processing
            
            # Parse actions from response
            actions = self.parse_actions(response_text)
            
            # Emit action signals if actions were found
            for action in actions:
                action_type = action.get("action")
                parameters = action.get("parameters", {})
                self.llm_action_requested.emit(action_type, parameters)
            
            # Save project state after LLM operation
            self._save_version_after_operation(response_text)
            
            # Emit response signal
            self.llm_response_received.emit(response_text, response)
    
    def _save_version_before_operation(self, prompt):
        """
        Save project state before an LLM operation.
        
        Args:
            prompt (str): User prompt.
        """
        if hasattr(self.app, 'autosave_manager'):
            # Truncate prompt if too long
            short_prompt = prompt[:30] + "..." if len(prompt) > 30 else prompt
            reason = f"Before LLM: {short_prompt}"
            self.app.autosave_manager.save_version(reason)
    
    def _save_version_after_operation(self, response_text):
        """
        Save project state after an LLM operation.
        
        Args:
            response_text (str): LLM response text.
        """
        if hasattr(self.app, 'autosave_manager'):
            # Extract first line of response
            first_line = response_text.split('\n')[0]
            short_response = first_line[:30] + "..." if len(first_line) > 30 else first_line
            reason = f"After LLM: {short_response}"
            self.app.autosave_manager.save_version(reason)
    
    def _send_openai_request(self, prompt, system_message, temperature, max_tokens, functions=None):
        """
        Send a request to the OpenAI API.
        
        Args:
            prompt (str): User prompt.
            system_message (str): System message.
            temperature (float): Temperature parameter.
            max_tokens (int): Maximum tokens in the response.
            functions (list, optional): List of function definitions.
        
        Returns:
            dict: API response, or None if the request failed.
        """
        self.logger.info("Sending request to OpenAI API")
        
        try:
            # Prepare request
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Add functions if provided
            if functions:
                data["functions"] = functions
                data["function_call"] = "auto"
            
            # Send request
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            # Check for errors
            response.raise_for_status()
            
            # Parse response
            return response.json()
        
        except Exception as e:
            self.logger.error(f"Error in OpenAI request: {e}")
            raise
    
    def _send_anthropic_request(self, prompt, system_message, temperature, max_tokens):
        """
        Send a request to the Anthropic API.
        
        Args:
            prompt (str): User prompt.
            system_message (str): System message.
            temperature (float): Temperature parameter.
            max_tokens (int): Maximum tokens in the response.
        
        Returns:
            dict: API response, or None if the request failed.
        """
        self.logger.info("Sending request to Anthropic API")
        
        try:
            # Prepare request
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            data = {
                "model": self.model,
                "system": system_message,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Send request
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            # Check for errors
            response.raise_for_status()
            
            # Parse response
            return response.json()
        
        except Exception as e:
            self.logger.error(f"Error in Anthropic request: {e}")
            raise
    
    def _send_local_model_request(self, prompt, system_message, temperature, max_tokens):
        """
        Send a request to a local LLM model.
        
        Args:
            prompt (str): User prompt.
            system_message (str): System message.
            temperature (float): Temperature parameter.
            max_tokens (int): Maximum tokens in the response.
        
        Returns:
            dict: API response, or None if the request failed.
        """
        self.logger.info("Sending request to local model")
        
        try:
            # Get local model endpoint from config
            endpoint = self.app.config.get("llm", "local_endpoint")
            
            # Prepare request
            headers = {"Content-Type": "application/json"}
            data = {
                "prompt": prompt,
                "system": system_message,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Send request
            response = requests.post(endpoint, headers=headers, json=data, timeout=60)
            
            # Check for errors
            response.raise_for_status()
            
            # Parse response
            return response.json()
        
        except Exception as e:
            self.logger.error(f"Error in local model request: {e}")
            raise
    
    def _extract_response_text(self, response):
        """
        Extract the response text from the API response.
        
        Args:
            response (dict): API response.
        
        Returns:
            str: Response text.
        """
        try:
            # Extract based on provider
            if self.provider == "openai":
                return response["choices"][0]["message"]["content"]
            elif self.provider == "anthropic":
                return response["content"][0]["text"]
            else:
                return "Unsupported provider"
        
        except Exception as e:
            self.logger.error(f"Error extracting response text: {e}")
            return "Error extracting response"
            
    def _handle_ambiguity(self, prompt, response_text):
        """
        Handle ambiguous instructions.
        
        Args:
            prompt (str): The original prompt.
            response_text (str): The LLM response text.
            
        Returns:
            bool: True if ambiguity was detected and handled, False otherwise.
        """
        # Check for ambiguity markers in response
        ambiguity_markers = ["ambiguous", "unclear", "not clear", "could mean", "multiple interpretations",
                            "need more information", "please clarify", "could you clarify",
                            "need clarification", "not specific enough"]
        
        is_ambiguous = False
        for marker in ambiguity_markers:
            if marker in response_text.lower():
                is_ambiguous = True
                break
                
        if is_ambiguous:
            # Log ambiguity
            self.logger.warning(f"Ambiguous instruction: {prompt}")
            
            # Extract suggestions from response
            suggestions = self._extract_suggestions(response_text)
            
            # Emit ambiguity signal
            self.llm_ambiguity.emit(prompt, suggestions)
            
            return True
        
        return False
    
    def _extract_suggestions(self, response_text):
        """
        Extract suggestions from an ambiguous response.
        
        Args:
            response_text (str): The LLM response text.
            
        Returns:
            list: List of suggested clarifications.
        """
        suggestions = []
        
        # Look for numbered or bulleted lists
        import re
        
        # Match numbered lists (1. Option one)
        numbered_pattern = r"\d+\.\s+(.*?)(?=\n\d+\.|\n\n|$)"
        numbered_matches = re.findall(numbered_pattern, response_text, re.DOTALL)
        
        # Match bulleted lists (- Option one or * Option one)
        bulleted_pattern = r"[-*]\s+(.*?)(?=\n[-*]|\n\n|$)"
        bulleted_matches = re.findall(bulleted_pattern, response_text, re.DOTALL)
        
        # Combine matches
        matches = numbered_matches + bulleted_matches
        
        # Add unique suggestions
        for match in matches:
            suggestion = match.strip()
            if suggestion and suggestion not in suggestions:
                suggestions.append(suggestion)
        
        # If no suggestions were found, create a default one
        if not suggestions:
            suggestions.append("Please provide more specific instructions.")
        
        return suggestions
    
    def parse_color_sequence(self, response_text):
        """
        Parse a color sequence from the LLM response.
        
        Args:
            response_text (str): LLM response text.
        
        Returns:
            list: List of (time, color) tuples, or None if parsing failed.
        """
        try:
            # Look for JSON blocks in the response
            json_blocks = self._extract_json_blocks(response_text)
            
            if json_blocks:
                # Try to parse each JSON block
                for json_block in json_blocks:
                    try:
                        data = json.loads(json_block)
                        
                        # Check if it's a valid sequence
                        if "sequence" in data and isinstance(data["sequence"], dict):
                            # Convert to list of (time, color) tuples
                            sequence = []
                            for time_str, entry in data["sequence"].items():
                                time = float(time_str)
                                color = tuple(entry["color"])
                                sequence.append((time, color))
                            
                            # Sort by time
                            sequence.sort(key=lambda x: x[0])
                            
                            return sequence
                    except:
                        continue
            
            # If no valid JSON blocks, try to parse from text
            return self._parse_sequence_from_text(response_text)
        
        except Exception as e:
            self.logger.error(f"Error parsing color sequence: {e}")
            return None
    
    def _extract_json_blocks(self, text):
        """
        Extract JSON blocks from text.
        
        Args:
            text (str): Text to extract JSON blocks from.
        
        Returns:
            list: List of JSON block strings.
        """
        json_blocks = []
        
        # Look for blocks between ```json and ```
        import re
        json_pattern = r"```json\s*([\s\S]*?)\s*```"
        matches = re.findall(json_pattern, text)
        
        if matches:
            json_blocks.extend(matches)
        
        # Also look for blocks between { and }
        brace_pattern = r"(\{[\s\S]*?\})"
        matches = re.findall(brace_pattern, text)
        
        if matches:
            json_blocks.extend(matches)
        
        return json_blocks
    
    def register_action_handler(self, action_type, handler):
        """
        Register a handler for a specific action type.
        
        Args:
            action_type (str): Action type.
            handler (callable): Function to handle the action.
        """
        self.logger.info(f"Registering handler for action type: {action_type}")
        self.action_handlers[action_type] = handler
    
    def execute_action(self, action_type, parameters):
        """
        Execute an action.
        
        Args:
            action_type (str): Action type.
            parameters (dict): Action parameters.
        
        Returns:
            dict: Result of the action.
        """
        if action_type in self.action_handlers:
            self.logger.info(f"Executing action: {action_type}")
            return self.action_handlers[action_type](parameters)
        else:
            self.logger.warning(f"No handler for action type: {action_type}")
            return {"success": False, "error": f"Unknown action type: {action_type}"}
    
    def _get_token_count_from_response(self, response):
        """
        Extract token count from API response.
        
        Args:
            response (dict): API response.
            
        Returns:
            int: Total token count.
        """
        try:
            # Extract token usage from response based on provider
            if self.provider == "openai":
                prompt_tokens = response.get("usage", {}).get("prompt_tokens", 0)
                completion_tokens = response.get("usage", {}).get("completion_tokens", 0)
                return prompt_tokens + completion_tokens
            elif self.provider == "anthropic":
                return response.get("usage", {}).get("total_tokens", 0)
            else:
                # Estimate tokens for local models (rough approximation)
                system_content = response.get("system", "")
                prompt_content = response.get("prompt", "")
                response_content = self._extract_response_text(response)
                # Rough estimate: 1 token ≈ 4 characters
                return (len(system_content) + len(prompt_content) + len(response_content)) // 4
        except Exception as e:
            self.logger.error(f"Error extracting token count: {e}")
            return 0
            
    def track_token_usage(self, response):
        """
        Track token usage and cost from API response.
        
        Args:
            response (dict): API response.
        """
        try:
            # Get total tokens
            total_tokens = self._get_token_count_from_response(response)
                
            # Update token usage
            self.token_usage += total_tokens
            
            # Calculate cost
            model_price = self.token_prices.get(self.provider, {}).get(self.model, 0)
            cost = (total_tokens / 1000) * model_price
            self.estimated_cost += cost
            
            # Emit signal
            self.token_usage_updated.emit(total_tokens, cost)
            
            # Store in project metadata
            if self.app.project_manager.current_project:
                if not hasattr(self.app.project_manager.current_project, "llm_metadata"):
                    self.app.project_manager.current_project.llm_metadata = {
                        "token_usage": 0,
                        "estimated_cost": 0.0,
                        "interactions": []
                    }
                
                self.app.project_manager.current_project.llm_metadata["token_usage"] += total_tokens
                self.app.project_manager.current_project.llm_metadata["estimated_cost"] += cost
                self.app.project_manager.current_project.llm_metadata["interactions"].append({
                    "timestamp": datetime.now().isoformat(),
                    "tokens": total_tokens,
                    "cost": cost,
                    "model": self.model,
                    "provider": self.provider
                })
                
                # Mark project as changed
                self.app.project_manager.project_changed.emit()
                
            self.logger.info(f"Tracked token usage: {total_tokens} tokens, ${cost:.4f}")
        except Exception as e:
            self.logger.error(f"Error tracking token usage: {e}")
    
    def interrupt(self):
        """
        Interrupt the current LLM request.
        
        Returns:
            bool: True if an interrupt was requested, False if no request is in progress.
        """
        if not self.is_processing:
            return False
        
        self.logger.info("Interrupting LLM request")
        self.interrupt_requested = True
        self.llm_interrupted.emit()
        return True
    
    def _handle_function_call(self, response):
        """
        Handle a function call from the LLM.
        
        Args:
            response (dict): API response containing a function call.
        
        Returns:
            dict: Result of the function call.
        """
        try:
            # Extract function call
            message = response["choices"][0]["message"]
            function_call = message.get("function_call")
            
            if not function_call:
                return {"success": False, "error": "No function call in response"}
            
            # Extract function name and arguments
            function_name = function_call.get("name")
            arguments_str = function_call.get("arguments", "{}")
            
            try:
                arguments = json.loads(arguments_str)
            except json.JSONDecodeError:
                return {"success": False, "error": f"Invalid function arguments: {arguments_str}"}
            
            # Log function call
            self.logger.info(f"Function call: {function_name}({arguments})")
            
            # Execute function
            result = self.execute_action(function_name, arguments)
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error handling function call: {e}")
            return {"success": False, "error": str(e)}
    
    def parse_actions(self, response_text):
        """
        Parse actions from LLM response.
        
        Args:
            response_text (str): LLM response text.
        
        Returns:
            list: List of action objects.
        """
        actions = []
        
        # Look for JSON blocks in the response
        json_blocks = self._extract_json_blocks(response_text)
        
        for json_block in json_blocks:
            try:
                data = json.loads(json_block)
                
                # Check if it's a valid action
                if "action" in data and "parameters" in data:
                    actions.append(data)
            except Exception as e:
                self.logger.debug(f"Failed to parse JSON block as action: {e}")
                continue
        
        return actions
    
    def _parse_sequence_from_text(self, text):
        """
        Parse a color sequence from plain text.
        
        Args:
            text (str): Text to parse.
        
        Returns:
            list: List of (time, color) tuples, or None if parsing failed.
        """
        try:
            sequence = []
            
            # Look for time and color patterns
            import re
            
            # Pattern: "at X seconds: RGB(R, G, B)" or "at X seconds: #RRGGBB"
            time_color_pattern = r"at\s+(\d+(?:\.\d+)?)\s+seconds?:?\s+(?:RGB\((\d+),\s*(\d+),\s*(\d+)\)|#([0-9a-fA-F]{6}))"
            matches = re.findall(time_color_pattern, text)
            
            for match in matches:
                time = float(match[0])
                
                if match[1]:  # RGB format
                    color = (int(match[1]), int(match[2]), int(match[3]))
                else:  # Hex format
                    hex_color = match[4]
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    color = (r, g, b)
                
                sequence.append((time, color))
            
            # Sort by time
            sequence.sort(key=lambda x: x[0])
            
            return sequence if sequence else None
        
        except Exception as e:
            self.logger.error(f"Error parsing sequence from text: {e}")
            return None
    
    def apply_sequence_to_timeline(self, sequence, timeline_index):
        """
        Apply a color sequence to a timeline.
        
        Args:
            sequence (list): List of (time, color) tuples.
            timeline_index (int): Timeline index.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not sequence:
            self.logger.warning("Cannot apply sequence: Empty sequence")
            return False
        
        timeline = self.app.timeline_manager.get_timeline(timeline_index)
        if not timeline:
            self.logger.warning(f"Cannot apply sequence: Timeline {timeline_index} not found")
            return False
        
        # Clear existing segments
        timeline.clear()
        
        # Add segments for each time point
        for i, (time, color) in enumerate(sequence):
            # Determine end time
            if i < len(sequence) - 1:
                end_time = sequence[i + 1][0]
            else:
                end_time = time + 10  # Default duration of 10 seconds for the last segment
            
            # Add segment
            self.app.timeline_manager.add_segment(
                timeline=timeline,
                start_time=time,
                end_time=end_time,
                color=color
            )
        
        return True
    
    def generate_sequence_from_audio(self, timeline_index, prompt=None):
        """
        Generate a color sequence based on the loaded audio.
        
        Args:
            timeline_index (int): Timeline index to apply the sequence to.
            prompt (str, optional): Additional prompt text. If None, uses a default prompt.
        
        Returns:
            bool: True if the request was sent, False otherwise.
        """
        if not self.app.audio_manager.audio_file:
            self.logger.warning("Cannot generate sequence: No audio loaded")
            self.llm_error.emit("No audio loaded")
            return False
        
        # Get audio information
        audio_file = self.app.audio_manager.audio_file
        duration = self.app.audio_manager.duration
        tempo = self.app.audio_manager.tempo
        beat_times = self.app.audio_manager.beat_times
        
        # Create audio description
        audio_description = (
            f"Audio file: {os.path.basename(audio_file)}\n"
            f"Duration: {duration:.2f} seconds\n"
            f"Tempo: {tempo:.2f} BPM\n"
        )
        
        # Add beat information
        if beat_times is not None and len(beat_times) > 0:
            beat_count = len(beat_times)
            beat_description = f"The audio has {beat_count} detected beats at the following times (in seconds):\n"
            beat_description += ", ".join(f"{time:.2f}" for time in beat_times[:20])
            if beat_count > 20:
                beat_description += f", ... (and {beat_count - 20} more)"
            audio_description += beat_description
        
        # Set default prompt if not provided
        if prompt is None:
            prompt = (
                "Create a color sequence for juggling balls that matches this music. "
                "The sequence should follow the rhythm and mood of the music, "
                "with color changes at significant points in the audio."
            )
        
        # Combine prompt with audio description
        full_prompt = f"{prompt}\n\n{audio_description}\n\nPlease provide a JSON sequence with timestamps and RGB colors."
        
        # Send request to LLM
        return self.send_request(
            prompt=full_prompt,
            system_message=(
                "You are an expert in creating color sequences for juggling balls that match music. "
                "You analyze audio descriptions and create sequences of colors that change with the rhythm, "
                "mood, and style of the music. Your responses should include a JSON sequence with timestamps "
                "and RGB colors, formatted like this:\n"
                "```json\n"
                "{\n"
                '  "sequence": {\n'
                '    "0": {"color": [255, 0, 0]},\n'
                '    "5.2": {"color": [0, 255, 0]},\n'
                '    "10.8": {"color": [0, 0, 255]}\n'
                "  }\n"
                "}\n"
                "```\n"
                "The timestamps should match significant points in the music like beats, "
                "and the colors should reflect the mood and energy of the music at those points."
            )
        )