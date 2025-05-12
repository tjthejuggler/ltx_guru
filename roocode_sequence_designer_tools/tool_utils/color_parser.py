#!/usr/bin/env python3
"""
Color Parser Module for Roocode Sequence Designer Tools

This module provides robust color parsing and interpolation functionalities.
It supports various color input formats and provides utilities for color manipulation.
"""

import re
from typing import Union, Dict, Tuple, List

# Import utilities from existing color_utils module
from roo_code_sequence_maker.utils.color_utils import (
    NAMED_COLORS,
    rgb_to_hsv,
    hsv_to_rgb
)

def parse_color(color_input: Union[str, Dict]) -> Tuple[int, int, int]:
    """
    Parse a color input in various formats and return an RGB tuple.
    
    Args:
        color_input: Can be:
            - A color name string (e.g., "red", "blue")
            - A hex string (e.g., "#FF0000", "FF0000")
            - A color object dictionary:
                - {"name": "red"}
                - {"hex": "#FF0000"}
                - {"rgb": [255, 0, 0]} (0-255 for each component)
                - {"hsv": [0, 100, 100]} (H: 0-359, S: 0-100, V: 0-100)
    
    Returns:
        Tuple[int, int, int]: An (R, G, B) tuple, where R, G, B are integers from 0 to 255
    
    Raises:
        ValueError: If the color input is invalid or cannot be parsed
    """
    # Handle string inputs (color names or hex)
    if isinstance(color_input, str):
        # Check if it's a named color
        color_name = color_input.lower()
        if color_name in NAMED_COLORS:
            rgb = NAMED_COLORS[color_name]
            return (rgb[0], rgb[1], rgb[2])
        
        # Check if it's a hex color
        hex_pattern = r'^#?([A-Fa-f0-9]{6})$'
        match = re.match(hex_pattern, color_input)
        if match:
            hex_value = match.group(1)
            r = int(hex_value[0:2], 16)
            g = int(hex_value[2:4], 16)
            b = int(hex_value[4:6], 16)
            return (r, g, b)
        
        # If we get here, the string format is invalid
        raise ValueError(f"Invalid color string: {color_input}. Expected a color name or hex value.")
    
    # Handle dictionary inputs
    elif isinstance(color_input, dict):
        # Check for name key
        if "name" in color_input:
            color_name = color_input["name"].lower()
            if color_name in NAMED_COLORS:
                rgb = NAMED_COLORS[color_name]
                return (rgb[0], rgb[1], rgb[2])
            else:
                raise ValueError(f"Unknown color name: {color_name}")
        
        # Check for hex key
        elif "hex" in color_input:
            hex_value = color_input["hex"]
            return parse_color(hex_value)  # Reuse the hex parsing logic
        
        # Check for rgb key
        elif "rgb" in color_input:
            rgb_values = color_input["rgb"]
            if not isinstance(rgb_values, (list, tuple)) or len(rgb_values) != 3:
                raise ValueError(f"Invalid RGB values: {rgb_values}. Expected a list or tuple of 3 integers.")
            
            # Validate and clamp RGB values
            r = max(0, min(255, int(rgb_values[0])))
            g = max(0, min(255, int(rgb_values[1])))
            b = max(0, min(255, int(rgb_values[2])))
            return (r, g, b)
        
        # Check for hsv key
        elif "hsv" in color_input:
            hsv_values = color_input["hsv"]
            if not isinstance(hsv_values, (list, tuple)) or len(hsv_values) != 3:
                raise ValueError(f"Invalid HSV values: {hsv_values}. Expected a list or tuple of 3 values.")
            
            # Validate and normalize HSV values
            h = max(0, min(359, int(hsv_values[0]))) / 359.0  # Convert to 0-1 range
            s = max(0, min(100, int(hsv_values[1]))) / 100.0  # Convert to 0-1 range
            v = max(0, min(100, int(hsv_values[2]))) / 100.0  # Convert to 0-1 range
            
            # Convert HSV to RGB
            rgb = hsv_to_rgb((h, s, v))
            return (rgb[0], rgb[1], rgb[2])
        
        # If we get here, the dictionary format is invalid
        else:
            raise ValueError(f"Invalid color dictionary: {color_input}. Expected keys: 'name', 'hex', 'rgb', or 'hsv'.")
    
    # Handle invalid input types
    else:
        raise ValueError(f"Invalid color input type: {type(color_input)}. Expected string or dictionary.")

def interpolate_color(color1_rgb: Tuple[int, int, int], color2_rgb: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """
    Interpolate between two RGB colors.
    
    Args:
        color1_rgb: An (R, G, B) tuple for the first color
        color2_rgb: An (R, G, B) tuple for the second color
        factor: A float between 0.0 and 1.0. A factor of 0.0 returns color1_rgb, and 1.0 returns color2_rgb
    
    Returns:
        Tuple[int, int, int]: An (R, G, B) tuple representing the interpolated color
    
    Raises:
        ValueError: If the factor is not between 0.0 and 1.0, or if the color tuples are invalid
    """
    # Validate inputs
    if not isinstance(color1_rgb, (tuple, list)) or len(color1_rgb) != 3:
        raise ValueError(f"Invalid first color: {color1_rgb}. Expected a tuple or list of 3 integers.")
    
    if not isinstance(color2_rgb, (tuple, list)) or len(color2_rgb) != 3:
        raise ValueError(f"Invalid second color: {color2_rgb}. Expected a tuple or list of 3 integers.")
    
    if not 0.0 <= factor <= 1.0:
        raise ValueError(f"Invalid factor: {factor}. Expected a value between 0.0 and 1.0.")
    
    # Perform linear interpolation for each channel
    r = round(color1_rgb[0] * (1 - factor) + color2_rgb[0] * factor)
    g = round(color1_rgb[1] * (1 - factor) + color2_rgb[1] * factor)
    b = round(color1_rgb[2] * (1 - factor) + color2_rgb[2] * factor)
    
    # Clamp values to ensure they're in the valid range
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    
    return (r, g, b)

if __name__ == "__main__":
    # Example usage
    print("Color parsing examples:")
    
    # Parse color name
    rgb = parse_color("red")
    print(f"'red' -> {rgb}")
    
    # Parse hex color
    rgb = parse_color("#00FF00")
    print(f"'#00FF00' -> {rgb}")
    
    # Parse color dictionary with name
    rgb = parse_color({"name": "blue"})
    print(f"{{'name': 'blue'}} -> {rgb}")
    
    # Parse color dictionary with hex
    rgb = parse_color({"hex": "#FFFF00"})
    print(f"{{'hex': '#FFFF00'}} -> {rgb}")
    
    # Parse color dictionary with RGB
    rgb = parse_color({"rgb": [255, 0, 255]})
    print(f"{{'rgb': [255, 0, 255]}} -> {rgb}")
    
    # Parse color dictionary with HSV
    rgb = parse_color({"hsv": [180, 100, 100]})
    print(f"{{'hsv': [180, 100, 100]}} -> {rgb}")
    
    print("\nColor interpolation examples:")
    
    # Interpolate between red and blue
    red = (255, 0, 0)
    blue = (0, 0, 255)
    
    # 0% interpolation (all red)
    rgb = interpolate_color(red, blue, 0.0)
    print(f"0% between {red} and {blue} -> {rgb}")
    
    # 25% interpolation
    rgb = interpolate_color(red, blue, 0.25)
    print(f"25% between {red} and {blue} -> {rgb}")
    
    # 50% interpolation
    rgb = interpolate_color(red, blue, 0.5)
    print(f"50% between {red} and {blue} -> {rgb}")
    
    # 75% interpolation
    rgb = interpolate_color(red, blue, 0.75)
    print(f"75% between {red} and {blue} -> {rgb}")
    
    # 100% interpolation (all blue)
    rgb = interpolate_color(red, blue, 1.0)
    print(f"100% between {red} and {blue} -> {rgb}")