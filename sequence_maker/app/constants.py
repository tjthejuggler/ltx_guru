"""
Sequence Maker - Constants Module

This module defines application-wide constants.
"""

# Application information
APP_NAME = "Sequence Maker"
APP_VERSION = "0.1.0"
APP_AUTHOR = "LTX Guru"

# File extensions
PROJECT_FILE_EXTENSION = ".smproj"
JSON_FILE_EXTENSION = ".json"
PRG_FILE_EXTENSION = ".prg"
AUDIO_FILE_EXTENSIONS = [".mp3", ".wav", ".ogg"]

# Timeline constants
MIN_TIMELINE_DURATION = 1  # seconds
MAX_TIMELINE_DURATION = 3600  # seconds (1 hour)
MIN_REFRESH_RATE = 1  # Hz
MAX_REFRESH_RATE = 1000  # Hz
MIN_PIXELS = 1
MAX_PIXELS = 4

# Color constants
DEFAULT_COLORS = [
    (255, 0, 0),      # Red
    (255, 165, 0),    # Orange
    (255, 255, 0),    # Yellow
    (0, 255, 0),      # Green
    (0, 255, 255),    # Cyan
    (0, 0, 255),      # Blue
    (255, 0, 255),    # Pink
    (255, 255, 255),  # White
    (0, 0, 0)         # Black
]

COLOR_NAMES = [
    "Red",
    "Orange",
    "Yellow",
    "Green",
    "Cyan",
    "Blue",
    "Pink",
    "White",
    "Black"
]

# Effect constants
EFFECT_TYPES = [
    "strobe",
    "fade",
    "pulse",
    "rainbow"
]

# Ball control constants
BALL_DISCOVERY_TIMEOUT = 5  # seconds
BALL_CONTROL_PORT = 41412
BALL_BROADCAST_IDENTIFIER = "NPLAYLTXBALL"

# Audio constants
AUDIO_SAMPLE_RATE = 44100  # Hz
AUDIO_CHANNELS = 2
AUDIO_BUFFER_SIZE = 1024
AUDIO_FORMAT = "mp3"

# UI constants
TIMELINE_HEIGHT = 100  # pixels
TIMELINE_SEGMENT_MIN_WIDTH = 5  # pixels
BALL_VISUALIZATION_SIZE = 50  # pixels
ZOOM_STEP = 1.2  # Zoom factor per step
MAX_ZOOM = 100.0
MIN_ZOOM = 0.01

# Autosave constants
AUTOSAVE_INTERVAL = 300  # seconds (5 minutes)
MAX_AUTOSAVE_FILES = 5

# Key mapping constants
DEFAULT_KEY_MAPPING = {
    # Ball 1 keys (top row)
    "q": {"color": (255, 0, 0), "timelines": [0]},      # Red
    "w": {"color": (255, 165, 0), "timelines": [0]},    # Orange
    "e": {"color": (255, 255, 0), "timelines": [0]},    # Yellow
    "r": {"color": (0, 255, 0), "timelines": [0]},      # Green
    "t": {"color": (0, 255, 255), "timelines": [0]},    # Cyan
    "y": {"color": (0, 0, 255), "timelines": [0]},      # Blue
    "u": {"color": (255, 0, 255), "timelines": [0]},    # Pink
    "i": {"color": (255, 255, 255), "timelines": [0]},  # White
    "o": {"color": (0, 0, 0), "timelines": [0]},        # Black
    
    # Ball 2 keys (middle row)
    "a": {"color": (255, 0, 0), "timelines": [1]},      # Red
    "s": {"color": (255, 165, 0), "timelines": [1]},    # Orange
    "d": {"color": (255, 255, 0), "timelines": [1]},    # Yellow
    "f": {"color": (0, 255, 0), "timelines": [1]},      # Green
    "g": {"color": (0, 255, 255), "timelines": [1]},    # Cyan
    "h": {"color": (0, 0, 255), "timelines": [1]},      # Blue
    "j": {"color": (255, 0, 255), "timelines": [1]},    # Pink
    "k": {"color": (255, 255, 255), "timelines": [1]},  # White
    "l": {"color": (0, 0, 0), "timelines": [1]},        # Black
    
    # Ball 3 keys (bottom row)
    "z": {"color": (255, 0, 0), "timelines": [2]},      # Red
    "x": {"color": (255, 165, 0), "timelines": [2]},    # Orange
    "c": {"color": (255, 255, 0), "timelines": [2]},    # Yellow
    "v": {"color": (0, 255, 0), "timelines": [2]},      # Green
    "b": {"color": (0, 255, 255), "timelines": [2]},    # Cyan
    "n": {"color": (0, 0, 255), "timelines": [2]},      # Blue
    "m": {"color": (255, 0, 255), "timelines": [2]},    # Pink
    ",": {"color": (255, 255, 255), "timelines": [2]},  # White
    ".": {"color": (0, 0, 0), "timelines": [2]},        # Black
    
    # All balls keys (number row)
    "1": {"color": (255, 0, 0), "timelines": [0, 1, 2]},      # Red
    "2": {"color": (255, 165, 0), "timelines": [0, 1, 2]},    # Orange
    "3": {"color": (255, 255, 0), "timelines": [0, 1, 2]},    # Yellow
    "4": {"color": (0, 255, 0), "timelines": [0, 1, 2]},      # Green
    "5": {"color": (0, 255, 255), "timelines": [0, 1, 2]},    # Cyan
    "6": {"color": (0, 0, 255), "timelines": [0, 1, 2]},      # Blue
    "7": {"color": (255, 0, 255), "timelines": [0, 1, 2]},    # Pink
    "8": {"color": (255, 255, 255), "timelines": [0, 1, 2]},  # White
    "9": {"color": (0, 0, 0), "timelines": [0, 1, 2]}         # Black
}

# Effect modifier keys
EFFECT_MODIFIERS = {
    "shift": "strobe",
    "ctrl": "fade",
    "alt": "custom"
}

# LLM constants
DEFAULT_LLM_TEMPERATURE = 0.7
DEFAULT_LLM_MAX_TOKENS = 1000