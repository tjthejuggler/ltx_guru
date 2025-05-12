"""
LTX Sequence Maker for Roo Agents

A toolkit for Roo agents to create color sequences for LTX juggling balls based on music analysis.
"""

__version__ = "0.1.0"
__author__ = "Roo Code"

from .audio_analyzer import AudioAnalyzer, LyricsProcessor
from .sequence_generator import SequenceGenerator

__all__ = [
    'AudioAnalyzer',
    'LyricsProcessor',
    'SequenceGenerator'
]