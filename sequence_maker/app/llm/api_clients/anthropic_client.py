"""
Sequence Maker - Anthropic LLM Client

This module defines the Anthropic API client for LLM integration.
"""

import json
import re
import requests
from .base_client import BaseLLMClient


class AnthropicClient(BaseLLMClient):
    """
    Anthropic API client for LLM integration.
    """
    
    def __init__(self, api_key, model, logger=None):
        """
        Initialize the Anthropic client.
        
        Args:
            api_key (str): Anthropic API key.
            model (str): Anthropic model name (e.g., "claude-3-opus", "claude-3-sonnet", "claude-3-haiku").
            logger (logging.Logger, optional): Logger instance.
        """
        super().__init__(api_key, model, logger)
        
        # Use the Messages API for Claude 3 models, otherwise use the Complete API
        if "claude-3" in model.lower():
            self.api_url = "https://api.anthropic.com/v1/messages"
            self.use_messages_api = True
        else:
            self.api_url = "https://api.anthropic.com/v1/complete"
            self.use_messages_api = False
    
    def send_request(self, prompt, system_message=None, temperature=0.7, max_tokens=1024, functions=None):
        """
        Send a request to the Anthropic API.
        
        Args:
            prompt (str): The prompt to send.
            system_message (str, optional): System message for context.
            temperature (float, optional): Temperature parameter.
            max_tokens (int, optional): Maximum tokens to generate.
            functions (list, optional): List of function definitions (not supported by Anthropic).
            
        Returns:
            dict: The API response.
        """
        if self.use_messages_api:
            return self._send_messages_request(prompt, system_message, temperature, max_tokens, functions)
        else:
            return self._send_complete_request(prompt, system_message, temperature, max_tokens)
    
    def _send_messages_request(self, prompt, system_message=None, temperature=0.7, max_tokens=1024, functions=None):
        """
        Send a request to the Anthropic Messages API (for Claude 3 models).
        
        Args:
            prompt (str): The prompt to send.
            system_message (str, optional): System message for context.
            temperature (float, optional): Temperature parameter.
            max_tokens (int, optional): Maximum tokens to generate.
            functions (list, optional): List of function definitions (not directly supported by Anthropic).
            
        Returns:
            dict: The API response.
        """
        # If functions are provided, add them to the system message
        if functions and system_message:
            system_message += "\n\nYou have access to the following functions. When appropriate, use them by outputting a code block with a function call like ```python\nfunction_name(arg1, arg2)\n```:\n"
            for func in functions:
                system_message += f"\n{func['name']}: {func['description']}\n"
                if 'parameters' in func:
                    system_message += f"Parameters: {json.dumps(func['parameters'], indent=2)}\n"
        elif functions:
            system_message = "You have access to the following functions. When appropriate, use them by outputting a code block with a function call like ```python\nfunction_name(arg1, arg2)\n```:\n"
            for func in functions:
                system_message += f"\n{func['name']}: {func['description']}\n"
                if 'parameters' in func:
                    system_message += f"Parameters: {json.dumps(func['parameters'], indent=2)}\n"
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Add system message if provided
        if system_message:
            payload["system"] = system_message
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        try:
            self.logger.debug(f"Sending request to Anthropic Messages API: {self.model}")
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"Anthropic API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
            # Convert Anthropic response to a format similar to OpenAI for consistency
            anthropic_response = response.json()
            
            # Extract the response text
            response_text = anthropic_response.get("content", [{}])[0].get("text", "")
            
            # Parse the response text for function calls
            function_call = self._extract_function_call(response_text)
            
            # Create OpenAI-like response
            openai_like_response = {
                "id": anthropic_response.get("id", ""),
                "object": "chat.completion",
                "created": anthropic_response.get("created", 0),
                "model": self.model,
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": anthropic_response.get("stop_reason", "stop"),
                    "index": 0
                }],
                "usage": {
                    "prompt_tokens": anthropic_response.get("usage", {}).get("input_tokens", 0),
                    "completion_tokens": anthropic_response.get("usage", {}).get("output_tokens", 0),
                    "total_tokens": (
                        anthropic_response.get("usage", {}).get("input_tokens", 0) +
                        anthropic_response.get("usage", {}).get("output_tokens", 0)
                    )
                }
            }
            
            # Add function call if found
            if function_call:
                openai_like_response["choices"][0]["message"]["function_call"] = function_call
            
            return openai_like_response
            
        except Exception as e:
            self.logger.error(f"Error sending request to Anthropic API: {str(e)}")
            raise
    
    def _extract_function_call(self, response_text):
        """
        Extract function call from response text.
        
        Args:
            response_text (str): The response text.
            
        Returns:
            dict: Function call information or None if not found.
        """
        # Look for Python code blocks
        python_code_pattern = r"```python\s*([\s\S]*?)\s*```"
        matches = re.findall(python_code_pattern, response_text)
        
        if not matches:
            # Try without language specifier
            code_pattern = r"```\s*([\s\S]*?)\s*```"
            matches = re.findall(code_pattern, response_text)
            
            if not matches:
                return None
        
        # Get the first code block
        code_block = matches[0].strip()
        
        # Parse function call
        function_call_pattern = r"(\w+)\((.*)\)"
        function_match = re.match(function_call_pattern, code_block)
        
        if not function_match:
            return None
        
        function_name = function_match.group(1)
        arguments_str = function_match.group(2)
        
        # Convert arguments to JSON
        try:
            # Handle simple arguments like "word", [0, 255, 0], "all"
            arguments = {}
            
            # Split by commas, but respect nested structures
            args_list = []
            current_arg = ""
            bracket_count = 0
            
            for char in arguments_str:
                if char == ',' and bracket_count == 0:
                    args_list.append(current_arg.strip())
                    current_arg = ""
                else:
                    current_arg += char
                    if char in '[{(':
                        bracket_count += 1
                    elif char in ']})':
                        bracket_count -= 1
            
            if current_arg:
                args_list.append(current_arg.strip())
            
            # Parse function parameters from the function definitions
            if len(args_list) >= 1:
                # For create_segment_for_word("word", [0, 255, 0], "all")
                # args_list would be ["word", [0, 255, 0], "all"]
                
                # Try to convert string literals
                processed_args = []
                for arg in args_list:
                    if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                        # String literal
                        processed_args.append(arg[1:-1])
                    elif arg.lower() == "true":
                        processed_args.append(True)
                    elif arg.lower() == "false":
                        processed_args.append(False)
                    elif arg.lower() == "null" or arg.lower() == "none":
                        processed_args.append(None)
                    elif arg.startswith("[") and arg.endswith("]"):
                        # List literal
                        try:
                            processed_args.append(eval(arg))
                        except:
                            processed_args.append(arg)
                    else:
                        # Try to convert to number
                        try:
                            if "." in arg:
                                processed_args.append(float(arg))
                            else:
                                processed_args.append(int(arg))
                        except:
                            processed_args.append(arg)
                
                # For create_segment_for_word, the parameters are:
                # word, color, balls
                if function_name == "create_segment_for_word" and len(processed_args) >= 2:
                    arguments = {
                        "word": processed_args[0]
                    }
                    
                    if len(processed_args) >= 2:
                        arguments["color"] = processed_args[1]
                    
                    if len(processed_args) >= 3:
                        arguments["balls"] = processed_args[2]
            
            # Convert to JSON string
            arguments_json = json.dumps(arguments)
            
            return {
                "name": function_name,
                "arguments": arguments_json
            }
        except Exception as e:
            self.logger.error(f"Error parsing function arguments: {str(e)}")
            return {
                "name": function_name,
                "arguments": "{}"
            }
    
    def _send_complete_request(self, prompt, system_message=None, temperature=0.7, max_tokens=1024):
        """
        Send a request to the Anthropic Complete API (for Claude 2 and earlier models).
        
        Args:
            prompt (str): The prompt to send.
            system_message (str, optional): System message for context.
            temperature (float, optional): Temperature parameter.
            max_tokens (int, optional): Maximum tokens to generate.
            
        Returns:
            dict: The API response.
        """
        # Anthropic uses a different format than OpenAI
        # They use "\n\nHuman: " and "\n\nAssistant: " to format the conversation
        
        formatted_prompt = f"\n\nHuman: {prompt}\n\nAssistant:"
        
        # Add system message if provided (as part of the human message)
        if system_message:
            formatted_prompt = f"\n\nHuman: {system_message}\n{prompt}\n\nAssistant:"
        
        # Prepare request payload
        payload = {
            "prompt": formatted_prompt,
            "model": self.model,
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature,
            "stop_sequences": ["\n\nHuman:"]
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        try:
            self.logger.debug(f"Sending request to Anthropic Complete API: {self.model}")
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"Anthropic API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
            # Convert Anthropic response to a format similar to OpenAI for consistency
            anthropic_response = response.json()
            
            # Extract the response text
            response_text = anthropic_response.get("completion", "")
            
            # Parse the response text for function calls
            function_call = self._extract_function_call(response_text)
            
            # Create OpenAI-like response
            openai_like_response = {
                "id": anthropic_response.get("id", ""),
                "object": "chat.completion",
                "created": anthropic_response.get("created", 0),
                "model": self.model,
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop",
                    "index": 0
                }],
                "usage": {
                    "prompt_tokens": 0,  # Anthropic doesn't provide token counts in Complete API
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
            
            # Add function call if found
            if function_call:
                openai_like_response["choices"][0]["message"]["function_call"] = function_call
            
            return openai_like_response
            
        except Exception as e:
            self.logger.error(f"Error sending request to Anthropic API: {str(e)}")
            raise
    
    def send_streaming_request(self, prompt, system_message=None, temperature=0.7, max_tokens=1024, functions=None):
        """
        Send a streaming request to the Anthropic API.
        
        Note: Anthropic doesn't support streaming in the same way as OpenAI.
        This method falls back to non-streaming and returns the full response.
        
        Args:
            prompt (str): The prompt to send.
            system_message (str, optional): System message for context.
            temperature (float, optional): Temperature parameter.
            max_tokens (int, optional): Maximum tokens to generate.
            functions (list, optional): List of function definitions (not supported by Anthropic).
            
        Returns:
            generator: A generator yielding the full response.
        """
        self.logger.warning("Streaming not fully supported for Anthropic API. Falling back to non-streaming.")
        response = self.send_request(prompt, system_message, temperature, max_tokens, functions)
        
        # Yield the full response as a single chunk
        content = response["choices"][0]["message"]["content"]
        yield content
        
        # Yield the full response object as the last item
        yield response