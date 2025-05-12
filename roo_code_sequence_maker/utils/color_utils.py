#!/usr/bin/env python3
"""
Color Utilities for LTX Sequence Maker

This module provides utility functions for working with colors in the LTX Sequence Maker.
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
    "lime": [0, 255, 0],
    "navy": [0, 0, 128],
    "teal": [0, 128, 128],
    "olive": [128, 128, 0],
    "maroon": [128, 0, 0],
    "gold": [255, 215, 0],
    "silver": [192, 192, 192]
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
            print(f"Warning: Unknown color name: {color}, using red instead")
            return NAMED_COLORS["red"]
    else:
        # Ensure RGB values are in range 0-255
        return [max(0, min(255, int(c))) for c in color]

def rgb_to_hsv(rgb: List[int]) -> Tuple[float, float, float]:
    """
    Convert RGB color to HSV.
    
    Args:
        rgb: RGB color values (0-255)
        
    Returns:
        tuple: HSV values (0-1)
    """
    r, g, b = rgb
    return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

def hsv_to_rgb(hsv: Tuple[float, float, float]) -> List[int]:
    """
    Convert HSV color to RGB.
    
    Args:
        hsv: HSV color values (0-1)
        
    Returns:
        list: RGB values (0-255)
    """
    h, s, v = hsv
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return [int(r * 255), int(g * 255), int(b * 255)]

def adjust_brightness(rgb: List[int], factor: float) -> List[int]:
    """
    Adjust the brightness of a color.
    
    Args:
        rgb: RGB color values (0-255)
        factor: Brightness factor (0-1)
        
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
        factor: Saturation factor (0-1)
        
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
        offset: Hue offset (0-1)
        
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
        steps: Number of steps in the gradient
        
    Returns:
        list: List of RGB colors forming a gradient
    """
    # Resolve colors
    start_rgb = resolve_color(start_color)
    end_rgb = resolve_color(end_color)
    
    # Convert to HSV for better gradients
    start_hsv = rgb_to_hsv(start_rgb)
    end_hsv = rgb_to_hsv(end_rgb)
    
    # Create gradient
    gradient = []
    
    for i in range(steps):
        # Calculate interpolation factor
        factor = i / (steps - 1) if steps > 1 else 0
        
        # Interpolate HSV values
        h = start_hsv[0] + factor * (end_hsv[0] - start_hsv[0])
        s = start_hsv[1] + factor * (end_hsv[1] - start_hsv[1])
        v = start_hsv[2] + factor * (end_hsv[2] - start_hsv[2])
        
        # Convert back to RGB
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
    rainbow = []
    
    for i in range(steps):
        # Calculate hue (0-1)
        hue = i / steps
        
        # Convert HSV to RGB (full saturation and value)
        rgb = hsv_to_rgb((hue, 1.0, 1.0))
        rainbow.append(rgb)
    
    return rainbow

def blend_colors(color1: Union[str, List[int]], color2: Union[str, List[int]], factor: float = 0.5) -> List[int]:
    """
    Blend two colors together.
    
    Args:
        color1: First color (name or RGB)
        color2: Second color (name or RGB)
        factor: Blend factor (0-1), 0 = all color1, 1 = all color2
        
    Returns:
        list: Blended RGB color
    """
    # Resolve colors
    rgb1 = resolve_color(color1)
    rgb2 = resolve_color(color2)
    
    # Blend RGB values
    r = int(rgb1[0] * (1 - factor) + rgb2[0] * factor)
    g = int(rgb1[1] * (1 - factor) + rgb2[1] * factor)
    b = int(rgb1[2] * (1 - factor) + rgb2[2] * factor)
    
    return [r, g, b]

def get_complementary_color(color: Union[str, List[int]]) -> List[int]:
    """
    Get the complementary color.
    
    Args:
        color: Input color (name or RGB)
        
    Returns:
        list: Complementary RGB color
    """
    # Resolve color
    rgb = resolve_color(color)
    
    # Convert to HSV
    h, s, v = rgb_to_hsv(rgb)
    
    # Complementary color has opposite hue
    h = (h + 0.5) % 1.0
    
    # Convert back to RGB
    return hsv_to_rgb((h, s, v))

def get_analogous_colors(color: Union[str, List[int]], angle: float = 0.083, count: int = 3) -> List[List[int]]:
    """
    Get analogous colors.
    
    Args:
        color: Input color (name or RGB)
        angle: Hue angle difference (default: 0.083, which is 30 degrees in the 0-1 range)
        count: Number of colors to generate
        
    Returns:
        list: List of analogous RGB colors
    """
    # Resolve color
    rgb = resolve_color(color)
    
    # Convert to HSV
    h, s, v = rgb_to_hsv(rgb)
    
    # Generate analogous colors
    colors = []
    
    for i in range(count):
        # Calculate hue offset
        offset = (i - count // 2) * angle
        
        # Calculate new hue
        new_h = (h + offset) % 1.0
        
        # Convert back to RGB
        colors.append(hsv_to_rgb((new_h, s, v)))
    
    return colors

def get_triadic_colors(color: Union[str, List[int]]) -> List[List[int]]:
    """
    Get triadic colors.
    
    Args:
        color: Input color (name or RGB)
        
    Returns:
        list: List of three triadic RGB colors
    """
    # Resolve color
    rgb = resolve_color(color)
    
    # Convert to HSV
    h, s, v = rgb_to_hsv(rgb)
    
    # Generate triadic colors (120 degree offsets)
    colors = [
        rgb,
        hsv_to_rgb(((h + 1/3) % 1.0, s, v)),
        hsv_to_rgb(((h + 2/3) % 1.0, s, v))
    ]
    
    return colors

def get_color_name(rgb: List[int]) -> str:
    """
    Get the name of a color that most closely matches the given RGB values.
    
    Args:
        rgb: RGB color values (0-255)
        
    Returns:
        str: Name of the closest matching color
    """
    # Calculate distance to each named color
    min_distance = float('inf')
    closest_name = "unknown"
    
    for name, named_rgb in NAMED_COLORS.items():
        # Calculate Euclidean distance in RGB space
        distance = sum((c1 - c2) ** 2 for c1, c2 in zip(rgb, named_rgb))
        
        if distance < min_distance:
            min_distance = distance
            closest_name = name
    
    return closest_name

if __name__ == "__main__":
    # Example usage
    print("Named colors:")
    for name, rgb in NAMED_COLORS.items():
        print(f"  {name}: {rgb}")
    
    print("\nColor operations:")
    
    # Resolve color
    color = resolve_color("blue")
    print(f"Resolved 'blue' to {color}")
    
    # Adjust brightness
    brighter = adjust_brightness(color, 1.5)
    darker = adjust_brightness(color, 0.5)
    print(f"Brighter blue: {brighter}")
    print(f"Darker blue: {darker}")
    
    # Create gradient
    gradient = create_gradient("red", "blue", 5)
    print("\nRed to blue gradient:")
    for i, rgb in enumerate(gradient):
        print(f"  Step {i+1}: {rgb}")
    
    # Create rainbow
    rainbow = create_rainbow(7)
    print("\nRainbow colors:")
    for i, rgb in enumerate(rainbow):
        print(f"  Color {i+1}: {rgb}")
    
    # Get complementary color
    comp = get_complementary_color("green")
    print(f"\nComplementary color of green: {comp} ({get_color_name(comp)})")
    
    # Get analogous colors
    analogous = get_analogous_colors("red")
    print("\nAnalogous colors of red:")
    for i, rgb in enumerate(analogous):
        print(f"  Color {i+1}: {rgb} ({get_color_name(rgb)})")
    
    # Get triadic colors
    triadic = get_triadic_colors("blue")
    print("\nTriadic colors of blue:")
    for i, rgb in enumerate(triadic):
        print(f"  Color {i+1}: {rgb} ({get_color_name(rgb)})")