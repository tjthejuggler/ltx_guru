"""
Sequence Maker - Utility Handlers

This module defines the UtilityHandlers class, which contains utility functions
for the main window, such as time and color parsing/formatting.
"""

import re
from PyQt6.QtGui import QColor


class UtilityHandlers:
    """Utility functions for the main window."""
    
    def __init__(self, main_window):
        """
        Initialize utility handlers.
        
        Args:
            main_window: The main window instance.
        """
        self.main_window = main_window
        self.app = main_window.app
    
    def _parse_time_from_text(self, text):
        """
        Parse time from text.
        
        Args:
            text (str): Text to parse.
        
        Returns:
            float: Time in seconds, or None if parsing failed.
        """
        # Remove any whitespace
        text = text.strip()
        
        # Try to parse as seconds
        try:
            return float(text)
        except ValueError:
            pass
        
        # Try to parse as MM:SS or HH:MM:SS
        time_pattern = r'^(\d+):(\d{1,2})(?::(\d{1,2}))?(?:\.(\d+))?$'
        match = re.match(time_pattern, text)
        
        if match:
            groups = match.groups()
            
            if groups[2] is not None:
                # HH:MM:SS format
                hours = int(groups[0])
                minutes = int(groups[1])
                seconds = int(groups[2])
            else:
                # MM:SS format
                hours = 0
                minutes = int(groups[0])
                seconds = int(groups[1])
            
            # Add fractional seconds if present
            if groups[3] is not None:
                fraction = float(f"0.{groups[3]}")
            else:
                fraction = 0.0
            
            return hours * 3600 + minutes * 60 + seconds + fraction
        
        return None
    
    def _parse_color_from_text(self, text):
        """
        Parse color from text.
        
        Args:
            text (str): Text to parse.
        
        Returns:
            tuple: RGB color tuple, or None if parsing failed.
        """
        # Remove any whitespace
        text = text.strip()
        
        # Try to parse as hex color
        hex_pattern = r'^#?([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$'
        match = re.match(hex_pattern, text)
        
        if match:
            r = int(match.group(1), 16)
            g = int(match.group(2), 16)
            b = int(match.group(3), 16)
            return (r, g, b)
        
        # Try to parse as RGB tuple
        rgb_pattern = r'^rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$'
        match = re.match(rgb_pattern, text)
        
        if match:
            r = min(255, max(0, int(match.group(1))))
            g = min(255, max(0, int(match.group(2))))
            b = min(255, max(0, int(match.group(3))))
            return (r, g, b)
        
        # Try to parse as color name
        color = QColor(text)
        if color.isValid():
            return (color.red(), color.green(), color.blue())
        
        return None
    
    def _format_seconds_to_hms(self, seconds, include_hundredths=True, hide_hours_if_zero=False):
        """
        Format seconds to HH:MM:SS.hh format.
        
        Args:
            seconds (float): Time in seconds.
            include_hundredths (bool, optional): Whether to include hundredths of a second.
            hide_hours_if_zero (bool, optional): Whether to hide hours if they are zero.
        
        Returns:
            str: Formatted time string.
        """
        # Handle negative time
        if seconds < 0:
            return "00:00.00" if include_hundredths else "00:00"
        
        # Calculate hours, minutes, seconds
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        secs = int(seconds % 60)
        
        # Calculate hundredths
        hundredths = int((seconds * 100) % 100)
        
        # Format string
        if hours > 0 or not hide_hours_if_zero:
            if include_hundredths:
                return f"{hours:02d}:{minutes:02d}:{secs:02d}.{hundredths:02d}"
            else:
                return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            if include_hundredths:
                return f"{minutes:02d}:{secs:02d}.{hundredths:02d}"
            else:
                return f"{minutes:02d}:{secs:02d}"