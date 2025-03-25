"""
Sequence Maker - UI Utilities

This module provides utility functions for UI-related operations.
"""

import logging

logger = logging.getLogger("SequenceMaker.UIUtils")


def parse_time_string(time_string):
    """
    Parse a time string into seconds.
    
    Handles various formats:
    - "123.45" (seconds as float)
    - "01:23.45" (minutes:seconds.hundredths)
    - "01:23" (minutes:seconds)
    - "01:23:45.67" (hours:minutes:seconds.hundredths)
    
    Args:
        time_string (str): Time string to parse
        
    Returns:
        float: Time in seconds
        
    Raises:
        ValueError: If the time string cannot be parsed
    """
    time_string = time_string.strip()
    
    # Try direct float conversion first
    try:
        return float(time_string)
    except ValueError:
        pass
    
    # Try MM:SS.ss format
    if ":" in time_string:
        parts = time_string.split(":")
        
        if len(parts) == 2:  # MM:SS or MM:SS.ss
            minutes, seconds = parts
            try:
                return float(minutes) * 60 + float(seconds)
            except ValueError:
                pass
                
        elif len(parts) == 3:  # HH:MM:SS or HH:MM:SS.ss
            hours, minutes, seconds = parts
            try:
                return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
            except ValueError:
                pass
    
    # If we get here, we couldn't parse the time string
    raise ValueError(f"Could not parse time string: {time_string}")


def format_seconds_to_hms(seconds, include_hundredths=True, hide_hours_if_zero=False):
    """
    Format seconds to HH:MM:SS.ss format.
    
    Args:
        seconds (float): Time in seconds
        include_hundredths (bool): Whether to include hundredths of a second
        hide_hours_if_zero (bool): Whether to hide hours if they are zero
        
    Returns:
        str: Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_val = seconds % 60
    
    if include_hundredths:
        seconds_format = f"{seconds_val:05.2f}"
    else:
        seconds_format = f"{int(seconds_val):02d}"
    
    if hours > 0 or not hide_hours_if_zero:
        return f"{hours:02d}:{minutes:02d}:{seconds_format}"
    else:
        return f"{minutes:02d}:{seconds_format}"


def parse_color_string(color_string):
    """
    Parse a color string into an RGB tuple.
    
    Handles various formats:
    - "red", "green", "blue", etc. (common color names)
    - "#RRGGBB" (hex format)
    - "rgb(r,g,b)" (CSS-style format)
    - "r,g,b" (comma-separated values)
    
    Args:
        color_string (str): Color string to parse
        
    Returns:
        tuple: (r, g, b) color tuple with values in range 0-255
        
    Raises:
        ValueError: If the color string cannot be parsed
    """
    color_string = color_string.strip().lower()
    
    # Common color names
    color_names = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "orange": (255, 165, 0),
        "purple": (128, 0, 128),
        "pink": (255, 192, 203)
    }
    
    if color_string in color_names:
        return color_names[color_string]
    
    # Hex format: #RRGGBB
    if color_string.startswith("#") and len(color_string) == 7:
        try:
            r = int(color_string[1:3], 16)
            g = int(color_string[3:5], 16)
            b = int(color_string[5:7], 16)
            return (r, g, b)
        except ValueError:
            pass
    
    # CSS-style format: rgb(r,g,b)
    if color_string.startswith("rgb(") and color_string.endswith(")"):
        try:
            rgb = color_string[4:-1].split(",")
            if len(rgb) == 3:
                r = int(rgb[0].strip())
                g = int(rgb[1].strip())
                b = int(rgb[2].strip())
                return (r, g, b)
        except ValueError:
            pass
    
    # Comma-separated values: r,g,b
    if "," in color_string:
        try:
            rgb = color_string.split(",")
            if len(rgb) == 3:
                r = int(rgb[0].strip())
                g = int(rgb[1].strip())
                b = int(rgb[2].strip())
                return (r, g, b)
        except ValueError:
            pass
    
    # If we get here, we couldn't parse the color string
    raise ValueError(f"Could not parse color string: {color_string}")


def format_color_tuple(color_tuple):
    """
    Format a color tuple as a string.
    
    Args:
        color_tuple (tuple): RGB color tuple (r, g, b)
        
    Returns:
        str: Formatted color string in the format "r,g,b"
    """
    if not isinstance(color_tuple, tuple) or len(color_tuple) != 3:
        return "255,0,0"  # Default to red if invalid
    
    r, g, b = color_tuple
    return f"{r},{g},{b}"


def get_app_attr(app, attr_name, default=None):
    """
    Safely get an attribute from the app object.
    
    Args:
        app: The application object
        attr_name (str): The name of the attribute to get
        default: The default value to return if the attribute doesn't exist
        
    Returns:
        The attribute value or the default value
    """
    return getattr(app, attr_name, default)