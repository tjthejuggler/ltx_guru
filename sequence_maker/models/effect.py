"""
Sequence Maker - Effect Model

This module defines the Effect class, which represents a color effect in a timeline segment.
"""

import logging
import math
import copy


class Effect:
    """
    Represents a color effect in a timeline segment.
    
    An effect modifies the base color of a segment based on time.
    """
    
    def __init__(self, effect_type="strobe", parameters=None):
        """
        Initialize a new effect.
        
        Args:
            effect_type (str, optional): Effect type. Defaults to "strobe".
            parameters (dict, optional): Effect parameters. Defaults to None.
        """
        self.logger = logging.getLogger("SequenceMaker.Effect")
        
        self.type = effect_type
        self.parameters = parameters or {}
        
        # Set default parameters based on effect type
        self._set_default_parameters()
    
    def _set_default_parameters(self):
        """Set default parameters based on effect type."""
        if self.type == "strobe":
            self.parameters.setdefault("frequency", 10)  # Hz
            self.parameters.setdefault("duty_cycle", 0.5)  # 0-1
        elif self.type == "fade":
            self.parameters.setdefault("target_color", (0, 0, 0))  # RGB
            self.parameters.setdefault("easing", "linear")  # linear, ease-in, ease-out, ease-in-out
        elif self.type == "pulse":
            self.parameters.setdefault("frequency", 1)  # Hz
            self.parameters.setdefault("min_brightness", 0.2)  # 0-1
        elif self.type == "rainbow":
            self.parameters.setdefault("speed", 1)  # cycles per second
            self.parameters.setdefault("saturation", 1.0)  # 0-1
            self.parameters.setdefault("value", 1.0)  # 0-1
    
    def to_dict(self):
        """
        Convert the effect to a dictionary for serialization.
        
        Returns:
            dict: Effect data as a dictionary.
        """
        return {
            "type": self.type,
            "parameters": self.parameters
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create an effect from a dictionary.
        
        Args:
            data (dict): Effect data as a dictionary.
        
        Returns:
            Effect: A new Effect instance.
        """
        return cls(
            effect_type=data["type"],
            parameters=data["parameters"]
        )
    
    def apply(self, color, time, duration):
        """
        Apply the effect to a color at a specific time.
        
        Args:
            color (tuple): Base RGB color tuple.
            time (float): Time in seconds from the start of the segment.
            duration (float): Duration of the segment in seconds.
        
        Returns:
            tuple: Modified RGB color tuple.
        """
        if self.type == "strobe":
            return self._apply_strobe(color, time)
        elif self.type == "fade":
            return self._apply_fade(color, time, duration)
        elif self.type == "pulse":
            return self._apply_pulse(color, time)
        elif self.type == "rainbow":
            return self._apply_rainbow(time)
        else:
            self.logger.warning(f"Unknown effect type: {self.type}")
            return color
    
    def _apply_strobe(self, color, time):
        """
        Apply a strobe effect.
        
        Args:
            color (tuple): Base RGB color tuple.
            time (float): Time in seconds from the start of the segment.
        
        Returns:
            tuple: Modified RGB color tuple.
        """
        frequency = self.parameters["frequency"]
        duty_cycle = self.parameters["duty_cycle"]
        
        # Calculate the phase within the current cycle
        phase = (time * frequency) % 1.0
        
        # If in the "on" part of the cycle, return the original color
        if phase < duty_cycle:
            return color
        
        # Otherwise, return black (off)
        return (0, 0, 0)
    
    def _apply_fade(self, color, time, duration):
        """
        Apply a fade effect.
        
        Args:
            color (tuple): Base RGB color tuple.
            time (float): Time in seconds from the start of the segment.
            duration (float): Duration of the segment in seconds.
        
        Returns:
            tuple: Modified RGB color tuple.
        """
        target_color = self.parameters["target_color"]
        easing = self.parameters["easing"]
        
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
        r = int(color[0] + (target_color[0] - color[0]) * progress)
        g = int(color[1] + (target_color[1] - color[1]) * progress)
        b = int(color[2] + (target_color[2] - color[2]) * progress)
        
        return (r, g, b)
    
    def _apply_pulse(self, color, time):
        """
        Apply a pulse effect.
        
        Args:
            color (tuple): Base RGB color tuple.
            time (float): Time in seconds from the start of the segment.
        
        Returns:
            tuple: Modified RGB color tuple.
        """
        frequency = self.parameters["frequency"]
        min_brightness = self.parameters["min_brightness"]
        
        # Calculate brightness multiplier (oscillates between min_brightness and 1.0)
        brightness = min_brightness + (1.0 - min_brightness) * (0.5 + 0.5 * math.sin(2 * math.pi * frequency * time))
        
        # Apply brightness to color
        r = int(color[0] * brightness)
        g = int(color[1] * brightness)
        b = int(color[2] * brightness)
        
        return (r, g, b)
    
    def _apply_rainbow(self, time):
        """
        Apply a rainbow effect.
        
        Args:
            time (float): Time in seconds from the start of the segment.
        
        Returns:
            tuple: RGB color tuple.
        """
        speed = self.parameters["speed"]
        saturation = self.parameters["saturation"]
        value = self.parameters["value"]
        
        # Calculate hue (0-360)
        hue = (time * speed * 360) % 360
        
        # Convert HSV to RGB
        return self._hsv_to_rgb(hue, saturation, value)
    
    def _hsv_to_rgb(self, h, s, v):
        """
        Convert HSV color to RGB.
        
        Args:
            h (float): Hue (0-360)
            s (float): Saturation (0-1)
            v (float): Value (0-1)
        
        Returns:
            tuple: RGB color tuple.
        """
        h = h % 360
        h_i = int(h / 60)
        f = h / 60 - h_i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        if h_i == 0:
            r, g, b = v, t, p
        elif h_i == 1:
            r, g, b = q, v, p
        elif h_i == 2:
            r, g, b = p, v, t
        elif h_i == 3:
            r, g, b = p, q, v
        elif h_i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
        
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def copy(self):
        """
        Create a copy of the effect.
        
        Returns:
            Effect: A new Effect instance with the same properties.
        """
        return Effect(
            effect_type=self.type,
            parameters=copy.deepcopy(self.parameters)
        )