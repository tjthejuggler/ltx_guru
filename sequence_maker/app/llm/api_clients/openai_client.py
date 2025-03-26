"""
Sequence Maker - OpenAI LLM Client

This module defines the OpenAI API client for LLM integration.
"""

import json
import time
import requests
from .base_client import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    """
    OpenAI API client for LLM integration.
    """
    
    def __init__(self, api_key, model, logger=None):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key (str): OpenAI API key.
            model (str): OpenAI model name (e.g., "gpt-3.5-turbo", "gpt-4").
            logger (logging.Logger, optional): Logger instance.
        """
        super().__init__(api_key, model, logger)
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    def send_request(self, prompt, system_message=None, temperature=0.7, max_tokens=1024, functions=None):
        """
        Send a request to the OpenAI API.
        
        Args:
            prompt (str): The prompt to send.
            system_message (str, optional): System message for context.
            temperature (float, optional): Temperature parameter.
            max_tokens (int, optional): Maximum tokens to generate.
            functions (list, optional): List of function definitions.
            
        Returns:
            dict: The API response.
        """
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # Add user message
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # Add functions if provided
        if functions:
            payload["functions"] = functions
            payload["function_call"] = "auto"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            self.logger.debug(f"Sending request to OpenAI API: {self.model}")
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Error sending request to OpenAI API: {str(e)}")
            raise
    
    def send_streaming_request(self, prompt, system_message=None, temperature=0.7, max_tokens=1024, functions=None):
        """
        Send a streaming request to the OpenAI API.
        
        Args:
            prompt (str): The prompt to send.
            system_message (str, optional): System message for context.
            temperature (float, optional): Temperature parameter.
            max_tokens (int, optional): Maximum tokens to generate.
            functions (list, optional): List of function definitions.
            
        Returns:
            generator: A generator yielding response chunks.
        """
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # Add user message
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        # Add functions if provided
        if functions:
            payload["functions"] = functions
            payload["function_call"] = "auto"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            self.logger.debug(f"Sending streaming request to OpenAI API: {self.model}")
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload),
                stream=True,
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
            # Process the streaming response
            collected_chunks = []
            collected_messages = []
            
            for chunk in response.iter_lines():
                if chunk:
                    chunk = chunk.decode("utf-8")
                    if chunk.startswith("data: "):
                        chunk = chunk[6:]  # Remove "data: " prefix
                    if chunk == "[DONE]":
                        break
                    
                    try:
                        chunk_data = json.loads(chunk)
                        collected_chunks.append(chunk_data)
                        chunk_message = chunk_data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if chunk_message:
                            collected_messages.append(chunk_message)
                            yield chunk_message
                    except json.JSONDecodeError:
                        self.logger.warning(f"Could not parse chunk as JSON: {chunk}")
            
            # Construct the full response object similar to non-streaming API
            full_response = {
                "id": collected_chunks[0].get("id", ""),
                "object": "chat.completion",
                "created": int(time.time()),
                "model": self.model,
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "".join(collected_messages)
                    },
                    "finish_reason": "stop",
                    "index": 0
                }]
            }
            
            # Yield the full response as the last item
            yield full_response
            
        except Exception as e:
            self.logger.error(f"Error sending streaming request to OpenAI API: {str(e)}")
            raise