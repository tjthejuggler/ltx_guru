#!/usr/bin/env python3
"""
Core Color Utilities for Roocode Sequence Designer Tools

This module provides utility functions for working with colors.
Originally from roo_code_sequence_maker/utils/color_utils.py, migrated here.
"""

import colorsys
from typing import List, Tuple, Union, Dict

# Define named colors
NAMED_COLORS = {
    "red": [255, 0, 0],
    "green": [0, 255, 0],
    "blue": [0, 0, 255],
    "yellow": [255, 255, 0],
    "cyan": [0, 255, 255],
    "magenta": [255, 0, 255],
    "white": [255, 255, 255],
    "black": [0, 0, 0],
    "orange": [255, 165, 0],
    "purple": [128, 0, 128],
    "pink": [255, 192, 203],
    "brown": [165, 42, 42],
    "gray": [128, 128, 128],
    "grey": [128, 128, 128], # Added alias
    "lime": [0, 255, 0], # Same as green
    "navy": [0, 0, 128],
    "teal": [0, 128, 128],
    "olive": [128, 128, 0],
    "maroon": [128, 0, 0],
    "gold": [255, 215, 0],
    "silver": [192, 192, 192],
    "indigo": [75, 0, 130],
    "violet": [238, 130, 238],
    "turqoise": [64, 224, 208], # Common spelling variation
    "turquoise": [64, 224, 208]
}

def resolve_color(color: Union[str, List[int], Tuple[int, int, int]]) -> List[int]:
    """
    Resolve a color name or RGB array to RGB values.
    
    Args:
        color: Color name or RGB array
        
    Returns:
        list: RGB values [r, g, b]
    """
    if isinstance(color, str):
        # Convert named color to RGB
        color_lower = color.lower()
        if color_lower in NAMED_COLORS:
            return NAMED_COLORS[color_lower]
        else:
            # Try to parse as hex if it looks like one
            if color_lower.startswith('#') and (len(color_lower) == 7 or len(color_lower) == 4):
                try:
                    hex_val = color_lower[1:]
                    if len(hex_val) == 3: # Short hex e.g. #RGB
                        r, g, b = [int(hex_val[i]*2, 16) for i in range(3)]
                    elif len(hex_val) == 6: # Full hex e.g. #RRGGBB
                        r, g, b = [int(hex_val[i:i+2], 16) for i in (0, 2, 4)]
                    else:
                        raise ValueError("Invalid hex length")
                    return [r,g,b]
                except ValueError:
                    pass # Fall through to unknown color warning

            print(f"Warning: Unknown color name or unparsable hex: {color}, using red instead")
            return NAMED_COLORS["red"]
    elif isinstance(color, (list, tuple)) and len(color) == 3:
        # Ensure RGB values are in range 0-255
        return [max(0, min(255, int(c))) for c in color]
    else:
        print(f"Warning: Invalid color format: {color}, using red instead.")
        return NAMED_COLORS["red"]


def rgb_to_hsv(rgb: List[int]) -> Tuple[float, float, float]:
    """
    Convert RGB color to HSV.
    
    Args:
        rgb: RGB color values (0-255)
        
    Returns:
        tuple: HSV values (H, S, V all 0-1)
    """
    r, g, b = rgb
    return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

def hsv_to_rgb(hsv: Tuple[float, float, float]) -> List[int]:
    """
    Convert HSV color to RGB.
    
    Args:
        hsv: HSV color values (H, S, V all 0-1)
        
    Returns:
        list: RGB values (0-255)
    """
    h, s, v = hsv
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return [int(r * 255), int(g * 255), int(b * 255)]

def adjust_brightness(rgb: List[int], factor: float) -> List[int]:
    """
    Adjust the brightness (Value component of HSV) of a color.
    
    Args:
        rgb: RGB color values (0-255)
        factor: Brightness factor. Values > 1 increase brightness, < 1 decrease.
                Resulting V is clamped to [0, 1].
        
    Returns:
        list: Adjusted RGB values (0-255)
    """
    h, s, v = rgb_to_hsv(rgb)
    v = max(0.0, min(1.0, v * factor))
    return hsv_to_rgb((h, s, v))

def adjust_saturation(rgb: List[int], factor: float) -> List[int]:
    """
    Adjust the saturation of a color.
    
    Args:
        rgb: RGB color values (0-255)
        factor: Saturation factor. Values > 1 increase saturation, < 1 decrease.
                Resulting S is clamped to [0, 1].
        
    Returns:
        list: Adjusted RGB values (0-255)
    """
    h, s, v = rgb_to_hsv(rgb)
    s = max(0.0, min(1.0, s * factor))
    return hsv_to_rgb((h, s, v))

def adjust_hue(rgb: List[int], offset: float) -> List[int]:
    """
    Adjust the hue of a color.
    
    Args:
        rgb: RGB color values (0-255)
        offset: Hue offset (0-1, where 1.0 is a full 360-degree shift).
        
    Returns:
        list: Adjusted RGB values (0-255)
    """
    h, s, v = rgb_to_hsv(rgb)
    h = (h + offset) % 1.0
    return hsv_to_rgb((h, s, v))

def create_gradient(start_color: Union[str, List[int]], end_color: Union[str, List[int]], steps: int) -> List[List[int]]:
    """
    Create a gradient between two colors.
    
    Args:
        start_color: Starting color (name or RGB)
        end_color: Ending color (name or RGB)
        steps: Number of steps in the gradient. Must be at least 2 for a valid gradient.
        
    Returns:
        list: List of RGB colors forming a gradient. Returns [start_rgb, end_rgb] if steps < 2.
    """
    start_rgb = resolve_color(start_color)
    end_rgb = resolve_color(end_color)
    
    if steps < 2:
        return [start_rgb, end_rgb] if steps == 2 else [start_rgb] # Or handle as error

    # Convert to HSV for potentially smoother hue transitions
    start_hsv = rgb_to_hsv(start_rgb)
    end_hsv = rgb_to_hsv(end_rgb)
    
    gradient = []
    
    # Handle hue wrapping for HSV interpolation (shortest path around color wheel)
    h_start, s_start, v_start = start_hsv
    h_end, s_end, v_end = end_hsv

    delta_h = h_end - h_start
    if delta_h > 0.5:
        h_start += 1.0  # Interpolate "backwards" via the longer path
    elif delta_h < -0.5:
        h_end += 1.0    # Interpolate "forwards" via the longer path
    # Recalculate delta_h for the chosen path
    delta_h = h_end - h_start


    for i in range(steps):
        factor = i / (steps - 1)
        
        h = (h_start + factor * delta_h) % 1.0 # Ensure hue stays in [0,1)
        s = s_start + factor * (s_end - s_start)
        v = v_start + factor * (v_end - v_start)
        
        rgb = hsv_to_rgb((h, s, v))
        gradient.append(rgb)
    
    return gradient

def create_rainbow(steps: int = 12) -> List[List[int]]:
    """
    Create a rainbow gradient.
    
    Args:
        steps: Number of steps in the rainbow
        
    Returns:
        list: List of RGB colors forming a rainbow
    """
    if steps <= 0:
        return []
    rainbow = []
    for i in range(steps):
        hue = i / steps
        rgb = hsv_to_rgb((hue, 1.0, 1.0)) # Full saturation and value for vivid rainbow
        rainbow.append(rgb)
    return rainbow

def blend_colors(color1: Union[str, List[int]], color2: Union[str, List[int]], factor: float = 0.5) -> List[int]:
    """
    Blend two colors together using linear RGB interpolation.
    
    Args:
        color1: First color (name or RGB)
        color2: Second color (name or RGB)
        factor: Blend factor (0-1). 0 = all color1, 0.5 = even mix, 1 = all color2.
        
    Returns:
        list: Blended RGB color, clamped to [0, 255]
    """
    rgb1 = resolve_color(color1)
    rgb2 = resolve_color(color2)
    
    clamped_factor = max(0.0, min(1.0, factor))
    
    r = int(rgb1[0] * (1 - clamped_factor) + rgb2[0] * clamped_factor)
    g = int(rgb1[1] * (1 - clamped_factor) + rgb2[1] * clamped_factor)
    b = int(rgb1[2] * (1 - clamped_factor) + rgb2[2] * clamped_factor)
    
    return [max(0, min(255, val)) for val in [r, g, b]]

def get_complementary_color(color: Union[str, List[int]]) -> List[int]:
    """
    Get the complementary color (hue shifted by 180 degrees).
    
    Args:
        color: Input color (name or RGB)
        
    Returns:
        list: Complementary RGB color
    """
    rgb = resolve_color(color)
    h, s, v = rgb_to_hsv(rgb)
    h_comp = (h + 0.5) % 1.0
    return hsv_to_rgb((h_comp, s, v))

def get_analogous_colors(color: Union[str, List[int]], angle_degrees: float = 30.0, count: int = 3) -> List[List[int]]:
    """
    Get analogous colors (colors adjacent on the color wheel).
    
    Args:
        color: Input color (name or RGB)
        angle_degrees: Hue angle difference in degrees (default: 30 degrees).
        count: Number of colors to generate (odd number recommended to include base color in middle).
        
    Returns:
        list: List of analogous RGB colors, including the original color.
    """
    rgb = resolve_color(color)
    h, s, v = rgb_to_hsv(rgb)
    
    angle_normalized = angle_degrees / 360.0
    colors = []
    
    # Ensure count is at least 1
    count = max(1, count)
    
    # Calculate start offset to center the original color if count is odd
    start_offset_factor = -(count // 2)
    
    for i in range(count):
        offset = (start_offset_factor + i) * angle_normalized
        new_h = (h + offset) % 1.0
        colors.append(hsv_to_rgb((new_h, s, v)))
        
    return colors

def get_triadic_colors(color: Union[str, List[int]]) -> List[List[int]]:
    """
    Get triadic colors (three colors evenly spaced on the color wheel).
    
    Args:
        color: Input color (name or RGB)
        
    Returns:
        list: List of three triadic RGB colors (original, +120deg, +240deg)
    """
    rgb = resolve_color(color)
    h, s, v = rgb_to_hsv(rgb)
    
    colors = [
        rgb, # Original color
        hsv_to_rgb(((h + 1/3) % 1.0, s, v)), # +120 degrees
        hsv_to_rgb(((h + 2/3) % 1.0, s, v))  # +240 degrees
    ]
    return colors

def get_color_name(rgb: List[int], threshold: int = 40) -> str:
    """
    Get the name of a color that most closely matches the given RGB values.
    Returns 'unknown' if no color is close enough within the threshold.
    
    Args:
        rgb: RGB color values (0-255)
        threshold: Maximum Euclidean distance to consider a match.
        
    Returns:
        str: Name of the closest matching color or 'unknown'.
    """
    min_distance = float('inf')
    closest_name = "unknown"
    
    resolved_rgb = resolve_color(rgb) # Ensure input is valid [R,G,B]

    for name, named_rgb in NAMED_COLORS.items():
        distance = sum((c1 - c2) ** 2 for c1, c2 in zip(resolved_rgb, named_rgb))**0.5 # Euclidean distance
        
        if distance < min_distance:
            min_distance = distance
            if distance <= threshold:
                closest_name = name
            else: # if min_distance is already greater than threshold, further colors won't be closer
                if closest_name == "unknown": # Only reset if we haven't found any match yet
                     closest_name = name # store the absolute closest if no one is in threshold
    
    # If even the absolute closest was beyond threshold, and we had set it, reset to unknown
    if min_distance > threshold and closest_name != "unknown":
         # Check if the closest_name was one that passed an earlier threshold check (not possible here)
         # This logic means if nothing is within threshold, return the name of the *absolute* closest color
         # To strictly return "unknown" if nothing is within threshold:
         if closest_name in NAMED_COLORS and sum((c1 - c2) ** 2 for c1, c2 in zip(resolved_rgb, NAMED_COLORS[closest_name]))**0.5 > threshold:
             closest_name = "unknown"


    return closest_name


if __name__ == "__main__":
    # Example usage
    print("Named colors:")
    for name, rgb_val in NAMED_COLORS.items():
        print(f"  {name}: {rgb_val}")
    
    print("\nColor operations:")
    
    # Resolve color
    color_example = resolve_color("blue")
    print(f"Resolved 'blue' to {color_example}")
    color_hex_example = resolve_color("#FF8800")
    print(f"Resolved '#FF8800' to {color_hex_example} ({get_color_name(color_hex_example)})")
    
    # Adjust brightness
    brighter = adjust_brightness(color_example, 1.5)
    darker = adjust_brightness(color_example, 0.5)
    print(f"Brighter blue: {brighter}")
    print(f"Darker blue: {darker}")
    
    # Create gradient
    gradient_example = create_gradient("red", "blue", 5)
    print("\nRed to blue gradient:")
    for i, rgb_val in enumerate(gradient_example):
        print(f"  Step {i+1}: {rgb_val}")
    
    # Create rainbow
    rainbow_example = create_rainbow(7)
    print("\nRainbow colors:")
    for i, rgb_val in enumerate(rainbow_example):
        print(f"  Color {i+1}: {rgb_val}")
    
    # Get complementary color
    comp_example = get_complementary_color("green")
    print(f"\nComplementary color of green: {comp_example} ({get_color_name(comp_example)})")
    
    # Get analogous colors
    analogous_example = get_analogous_colors("red", angle_degrees=30, count=3)
    print("\nAnalogous colors of red (30deg, 3 count):")
    for i, rgb_val in enumerate(analogous_example):
        print(f"  Color {i+1}: {rgb_val} ({get_color_name(rgb_val)})")
    
    # Get triadic colors
    triadic_example = get_triadic_colors("blue")
    print("\nTriadic colors of blue:")
    for i, rgb_val in enumerate(triadic_example):
        print(f"  Color {i+1}: {rgb_val} ({get_color_name(rgb_val)})")

    print(f"\nName for [250,5,5] (threshold 40): {get_color_name([250,5,5])}")
    print(f"Name for [128,128,128] (threshold 10): {get_color_name([128,128,128], threshold=10)}")
    print(f"Name for [130,130,130] (threshold 10): {get_color_name([130,130,130], threshold=10)}") # Should be gray
    print(f"Name for [140,140,140] (threshold 10): {get_color_name([140,140,140], threshold=10)}") # Should be unknown