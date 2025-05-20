"""
Utilities for handling different file types in Sequence Maker
"""

import os
import json

# File extension constants
SEQDESIGN_EXT = ".seqdesign.json"
PRG_EXT = ".prg.json"
BALL_EXT = ".ball.json"
LYRICS_EXT = ".lyrics.json"
ANALYSIS_EXT = ".analysis.json"

def get_file_type(file_path):
    """
    Determine the type of a file based on its extension.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File type ("seqdesign", "prg", "ball", "lyrics", "analysis", or "unknown")
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == SEQDESIGN_EXT:
        return "seqdesign"
    elif ext == PRG_EXT:
        return "prg"
    elif ext == BALL_EXT:
        return "ball"
    elif ext == LYRICS_EXT:
        return "lyrics"
    elif ext == ANALYSIS_EXT:
        return "analysis"
    else:
        # Check for special cases
        if ext == ".json":
            if "word_flash_sequence" in file_path:
                return "word_flash"
            elif "lyrics_timestamps" in file_path:
                return "lyrics"
        
        return "unknown"

def is_valid_ball_sequence(file_path):
    """
    Check if a file is a valid ball sequence file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if the file is a valid ball sequence, False otherwise
    """
    if not os.path.isfile(file_path):
        return False
    
    file_type = get_file_type(file_path)
    if file_type == "ball":
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check for required fields
            if "metadata" not in data or "segments" not in data:
                return False
            
            return True
        except:
            return False
    
    return False

def is_valid_seqdesign(file_path):
    """
    Check if a file is a valid sequence design file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if the file is a valid sequence design, False otherwise
    """
    if not os.path.isfile(file_path):
        return False
    
    file_type = get_file_type(file_path)
    if file_type == "seqdesign":
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check for required fields
            if "metadata" not in data or "effects_timeline" not in data:
                return False
            
            return True
        except:
            return False
    
    return False

def is_valid_lyrics_timestamps(file_path):
    """
    Check if a file is a valid lyrics timestamps file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if the file is a valid lyrics timestamps file, False otherwise
    """
    if not os.path.isfile(file_path):
        return False
    
    # Check content rather than just extension
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check for required fields
        if "word_timestamps" not in data:
            return False
        
        return True
    except:
        return False