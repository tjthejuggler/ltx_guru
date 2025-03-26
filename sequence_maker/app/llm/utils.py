"""
Sequence Maker - LLM Utilities

This module provides utility functions for LLM integration.
"""

import logging
from datetime import datetime


def format_time(seconds):
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


def format_timestamp(timestamp=None):
    """
    Format a timestamp for logging.
    
    Args:
        timestamp (datetime, optional): Timestamp to format. If None, uses current time.
        
    Returns:
        str: Formatted timestamp string.
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text, max_length=100, suffix="..."):
    """
    Truncate text to a maximum length.
    
    Args:
        text (str): Text to truncate.
        max_length (int, optional): Maximum length.
        suffix (str, optional): Suffix to add to truncated text.
        
    Returns:
        str: Truncated text.
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def setup_logger(name, level=logging.INFO):
    """
    Set up a logger with the specified name and level.
    
    Args:
        name (str): Logger name.
        level (int, optional): Logging level.
        
    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create console handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger


def safe_json_loads(json_str, default=None):
    """
    Safely load JSON string.
    
    Args:
        json_str (str): JSON string to load.
        default (any, optional): Default value to return if loading fails.
        
    Returns:
        any: Loaded JSON data or default value.
    """
    import json
    
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default