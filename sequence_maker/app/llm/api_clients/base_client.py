"""
Sequence Maker - Base LLM Client

This module defines the abstract base class for LLM API clients.
"""

import abc
import logging


class BaseLLMClient(abc.ABC):
    """
    Abstract base class for LLM API clients.
    
    This class defines the interface that all LLM API clients must implement.
    """
    
    def __init__(self, api_key, model, logger=None):
        """
        Initialize the base LLM client.
        
        Args:
            api_key (str): API key for the LLM provider.
            model (str): Model name to use.
            logger (logging.Logger, optional): Logger instance.
        """
        self.api_key = api_key
        self.model = model
        self.logger = logger or logging.getLogger("SequenceMaker.LLM")
    
    @abc.abstractmethod
    def send_request(self, prompt, system_message=None, temperature=0.7, max_tokens=1024, functions=None):
        """
        Send a request to the LLM API.
        
        Args:
            prompt (str): The prompt to send.
            system_message (str, optional): System message for context.
            temperature (float, optional): Temperature parameter.
            max_tokens (int, optional): Maximum tokens to generate.
            functions (list, optional): List of function definitions.
            
        Returns:
            dict: The API response.
        """
        pass
    
    @abc.abstractmethod
    def send_streaming_request(self, prompt, system_message=None, temperature=0.7, max_tokens=1024, functions=None):
        """
        Send a streaming request to the LLM API.
        
        Args:
            prompt (str): The prompt to send.
            system_message (str, optional): System message for context.
            temperature (float, optional): Temperature parameter.
            max_tokens (int, optional): Maximum tokens to generate.
            functions (list, optional): List of function definitions.
            
        Returns:
            generator: A generator yielding response chunks.
        """
        pass