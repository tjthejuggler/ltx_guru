"""
Sequence Maker - Local LLM Client

This module defines the client for local LLM models.
"""

import json
import os
import subprocess
import tempfile
from .base_client import BaseLLMClient


class LocalClient(BaseLLMClient):
    """
    Client for local LLM models.
    """
    
    def __init__(self, model_path, model="default", logger=None):
        """
        Initialize the local LLM client.
        
        Args:
            model_path (str): Path to the local model or command to execute.
            model (str, optional): Model identifier (default: "default").
            logger (logging.Logger, optional): Logger instance.
        """
        # For local models, the "api_key" is actually the model path
        super().__init__(model_path, model, logger)
        self.model_path = model_path
    
    def send_request(self, prompt, system_message=None, temperature=0.7, max_tokens=1024, functions=None):
        """
        Send a request to the local LLM.
        
        Args:
            prompt (str): The prompt to send.
            system_message (str, optional): System message for context.
            temperature (float, optional): Temperature parameter.
            max_tokens (int, optional): Maximum tokens to generate.
            functions (list, optional): List of function definitions (may not be supported).
            
        Returns:
            dict: The API response in OpenAI-like format.
        """
        try:
            self.logger.debug(f"Sending request to local model: {self.model}")
            
            # Combine system message and prompt if both provided
            full_prompt = prompt
            if system_message:
                full_prompt = f"{system_message}\n\n{prompt}"
            
            # Create a temporary file for the prompt
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
                temp_file.write(full_prompt)
                temp_file_path = temp_file.name
            
            # Prepare command with parameters
            command = [
                self.model_path,
                "--temp", str(temperature),
                "--tokens", str(max_tokens),
                "--prompt", temp_file_path
            ]
            
            # Execute the command
            self.logger.debug(f"Executing command: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            # Parse the output
            output = result.stdout.strip()
            
            # Create an OpenAI-like response format
            response = {
                "id": "local-completion",
                "object": "chat.completion",
                "created": 0,
                "model": self.model,
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": output
                    },
                    "finish_reason": "stop",
                    "index": 0
                }],
                "usage": {
                    "prompt_tokens": 0,  # Local models don't provide token counts
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error sending request to local model: {str(e)}")
            raise
    
    def send_streaming_request(self, prompt, system_message=None, temperature=0.7, max_tokens=1024, functions=None):
        """
        Send a streaming request to the local LLM.
        
        Note: This implementation doesn't truly stream but returns the full response.
        
        Args:
            prompt (str): The prompt to send.
            system_message (str, optional): System message for context.
            temperature (float, optional): Temperature parameter.
            max_tokens (int, optional): Maximum tokens to generate.
            functions (list, optional): List of function definitions (may not be supported).
            
        Returns:
            generator: A generator yielding the full response.
        """
        self.logger.warning("Streaming not supported for local models. Falling back to non-streaming.")
        response = self.send_request(prompt, system_message, temperature, max_tokens)
        
        # Yield the full response as a single chunk
        content = response["choices"][0]["message"]["content"]
        yield content
        
        # Yield the full response object as the last item
        yield response