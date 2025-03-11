"""
Sequence Maker - Color Utilities

This module provides utility functions for color manipulation.
"""

import logging
import math


logger = logging.getLogger("SequenceMaker.ColorUtils")


def rgb_to_hsv(r, g, b):
    """
    Convert RGB color to HSV.
    
    Args:
        r (int): Red component (0-255).
        g (int): Green component (0-255).
        b (int): Blue component (0-255).
    
    Returns:
        tuple: (h, s, v) where h is in degrees (0-360) and s, v are in range 0-1.
    """
    # Normalize RGB values
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    
    # Calculate value (max)
    v = max(r, g, b)
    
    # Calculate saturation
    delta = v - min(r, g, b)
    s = 0 if v == 0 else delta / v
    
    # Calculate hue
    h = 0
    if delta != 0:
        if v == r:
            h = 60 * ((g - b) / delta % 6)
        elif v == g:
            h = 60 * ((b - r) / delta + 2)
        else:  # v == b
            h = 60 * ((r - g) / delta + 4)
    
    # Ensure hue is in range 0-360
    h = (h + 360) % 360
    
    return h, s, v


def hsv_to_rgb(h, s, v):
    """
    Convert HSV color to RGB.
    
    Args:
        h (float): Hue in degrees (0-360).
        s (float): Saturation (0-1).
        v (float): Value (0-1).
    
    Returns:
        tuple: (r, g, b) where r, g, b are in range 0-255.
    """
    # Ensure hue is in range 0-360
    h = h % 360
    
    # Calculate chroma, second largest component, and match value
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    # Calculate RGB based on hue
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:  # 300 <= h < 360
        r, g, b = c, 0, x
    
    # Add match value and convert to 0-255 range
    r, g, b = (r + m) * 255, (g + m) * 255, (b + m) * 255
    
    return int(r), int(g), int(b)


def interpolate_color(color1, color2, t):
    """
    Interpolate between two colors.
    
    Args:
        color1 (tuple): First RGB color.
        color2 (tuple): Second RGB color.
        t (float): Interpolation factor (0-1).
    
    Returns:
        tuple: Interpolated RGB color.
    """
    # Clamp t to range 0-1
    t = max(0, min(1, t))
    
    # Interpolate RGB components
    r = int(color1[0] + (color2[0] - color1[0]) * t)
    g = int(color1[1] + (color2[1] - color1[1]) * t)
    b = int(color1[2] + (color2[2] - color1[2]) * t)
    
    # Clamp RGB values to range 0-255
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    
    return r, g, b


def interpolate_color_hsv(color1, color2, t):
    """
    Interpolate between two colors in HSV space.
    
    Args:
        color1 (tuple): First RGB color.
        color2 (tuple): Second RGB color.
        t (float): Interpolation factor (0-1).
    
    Returns:
        tuple: Interpolated RGB color.
    """
    # Clamp t to range 0-1
    t = max(0, min(1, t))
    
    # Convert RGB to HSV
    h1, s1, v1 = rgb_to_hsv(*color1)
    h2, s2, v2 = rgb_to_hsv(*color2)
    
    # Handle hue interpolation (shortest path)
    if abs(h2 - h1) > 180:
        if h1 < h2:
            h1 += 360
        else:
            h2 += 360
    
    # Interpolate HSV components
    h = (h1 + (h2 - h1) * t) % 360
    s = s1 + (s2 - s1) * t
    v = v1 + (v2 - v1) * t
    
    # Convert back to RGB
    return hsv_to_rgb(h, s, v)


def apply_strobe_effect(color, time, frequency=10, duty_cycle=0.5):
    """
    Apply a strobe effect to a color.
    
    Args:
        color (tuple): RGB color.
        time (float): Time in seconds.
        frequency (float, optional): Strobe frequency in Hz. Defaults to 10.
        duty_cycle (float, optional): Duty cycle (0-1). Defaults to 0.5.
    
    Returns:
        tuple: Modified RGB color.
    """
    # Calculate phase within cycle
    phase = (time * frequency) % 1.0
    
    # If in "on" part of cycle, return original color
    if phase < duty_cycle:
        return color
    
    # Otherwise, return black (off)
    return (0, 0, 0)


def apply_fade_effect(color1, color2, time, duration=1.0, easing="linear"):
    """
    Apply a fade effect between two colors.
    
    Args:
        color1 (tuple): Start RGB color.
        color2 (tuple): End RGB color.
        time (float): Time in seconds from start of fade.
        duration (float, optional): Fade duration in seconds. Defaults to 1.0.
        easing (str, optional): Easing function. Defaults to "linear".
    
    Returns:
        tuple: Modified RGB color.
    """
    # Calculate progress (0-1)
    progress = min(1.0, time / duration)
    
    # Apply easing function
    if easing == "ease-in":
        progress = progress * progress
    elif easing == "ease-out":
        progress = 1 - (1 - progress) * (1 - progress)
    elif easing == "ease-in-out":
        progress = 0.5 - 0.5 * math.cos(math.pi * progress)
    
    # Interpolate between colors
    return interpolate_color(color1, color2, progress)


def apply_pulse_effect(color, time, frequency=1, min_brightness=0.2):
    """
    Apply a pulse effect to a color.
    
    Args:
        color (tuple): RGB color.
        time (float): Time in seconds.
        frequency (float, optional): Pulse frequency in Hz. Defaults to 1.
        min_brightness (float, optional): Minimum brightness (0-1). Defaults to 0.2.
    
    Returns:
        tuple: Modified RGB color.
    """
    # Calculate brightness multiplier (oscillates between min_brightness and 1.0)
    brightness = min_brightness + (1.0 - min_brightness) * (0.5 + 0.5 * math.sin(2 * math.pi * frequency * time))
    
    # Apply brightness to color
    r = int(color[0] * brightness)
    g = int(color[1] * brightness)
    b = int(color[2] * brightness)
    
    return (r, g, b)


def apply_rainbow_effect(time, speed=1, saturation=1.0, value=1.0):
    """
    Apply a rainbow effect.
    
    Args:
        time (float): Time in seconds.
        speed (float, optional): Rainbow speed in cycles per second. Defaults to 1.
        saturation (float, optional): Color saturation (0-1). Defaults to 1.0.
        value (float, optional): Color value/brightness (0-1). Defaults to 1.0.
    
    Returns:
        tuple: RGB color.
    """
    # Calculate hue (0-360)
    hue = (time * speed * 360) % 360
    
    # Convert HSV to RGB
    return hsv_to_rgb(hue, saturation, value)


def get_color_name(color):
    """
    Get the name of a color.
    
    Args:
        color (tuple): RGB color.
    
    Returns:
        str: Color name.
    """
    # Define common colors
    common_colors = {
        (255, 0, 0): "Red",
        (255, 165, 0): "Orange",
        (255, 255, 0): "Yellow",
        (0, 255, 0): "Green",
        (0, 255, 255): "Cyan",
        (0, 0, 255): "Blue",
        (255, 0, 255): "Pink",
        (255, 255, 255): "White",
        (0, 0, 0): "Black"
    }
    
    # Check if color is a common color
    for common_color, name in common_colors.items():
        if color == common_color:
            return name
    
    # Return RGB values
    return f"RGB({color[0]}, {color[1]}, {color[2]})"