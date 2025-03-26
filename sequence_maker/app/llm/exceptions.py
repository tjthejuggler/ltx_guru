"""
Sequence Maker - LLM Exceptions

This module defines custom exceptions for LLM integration.
"""


class LLMError(Exception):
    """Base class for LLM-related exceptions."""
    pass


class LLMConfigError(LLMError):
    """Exception raised for configuration errors."""
    pass


class LLMAPIError(LLMError):
    """Exception raised for API communication errors."""
    pass


class LLMTimeoutError(LLMAPIError):
    """Exception raised when an LLM request times out."""
    pass


class LLMRateLimitError(LLMAPIError):
    """Exception raised when hitting API rate limits."""
    pass


class LLMAuthenticationError(LLMAPIError):
    """Exception raised for authentication failures."""
    pass


class LLMFunctionError(LLMError):
    """Exception raised for errors in function calling."""
    pass


class LLMInterruptedError(LLMError):
    """Exception raised when an LLM request is interrupted."""
    pass