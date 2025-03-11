"""
Sequence Maker - LLM Manager

This module defines the LLMManager class, which handles integration with language models.
"""

import logging
import json
import threading
import time
import requests
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
    """
    
    # Signals
    llm_response_received = pyqtSignal(str, dict)  # response_text, response_data
    llm_error = pyqtSignal(str)  # error_message
    llm_thinking = pyqtSignal()
    llm_ready = pyqtSignal()
    
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
    
    def send_request(self, prompt, system_message=None, temperature=None, max_tokens=None):
        """
        Send a request to the language model.
        
        Args:
            prompt (str): User prompt.
            system_message (str, optional): System message. If None, uses a default message.
            temperature (float, optional): Temperature parameter. If None, uses the configured value.
            max_tokens (int, optional): Maximum tokens in the response. If None, uses the default value.
        
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
            args=(prompt, system_message, temperature, max_tokens),
            daemon=True
        )
        self.request_thread.start()
        
        return True
    
    def _request_worker(self, prompt, system_message, temperature, max_tokens):
        """
        Worker thread for sending requests to the language model.
        
        Args:
            prompt (str): User prompt.
            system_message (str): System message.
            temperature (float): Temperature parameter.
            max_tokens (int): Maximum tokens in the response.
        """
        try:
            # Prepare request based on provider
            if self.provider == "openai":
                response = self._send_openai_request(prompt, system_message, temperature, max_tokens)
            elif self.provider == "anthropic":
                response = self._send_anthropic_request(prompt, system_message, temperature, max_tokens)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
            
            # Process response
            if response:
                # Extract response text
                response_text = self._extract_response_text(response)
                
                # Emit response signal
                self.llm_response_received.emit(response_text, response)
            else:
                self.llm_error.emit("No response from LLM")
        
        except Exception as e:
            self.logger.error(f"Error in LLM request: {e}")
            self.llm_error.emit(f"Error: {str(e)}")
        
        finally:
            # Reset processing state
            self.is_processing = False
            
            # Emit ready signal
            self.llm_ready.emit()
    
    def _send_openai_request(self, prompt, system_message, temperature, max_tokens):
        """
        Send a request to the OpenAI API.
        
        Args:
            prompt (str): User prompt.
            system_message (str): System message.
            temperature (float): Temperature parameter.
            max_tokens (int): Maximum tokens in the response.
        
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