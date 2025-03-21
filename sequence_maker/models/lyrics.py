"""
Sequence Maker - Lyrics Model

This module defines the Lyrics class, which represents lyrics data.
"""

import logging

class WordTimestamp:
    """
    Class representing a word with its start and end timestamps.
    
    Attributes:
        word (str): The word text.
        start (float): Start time in seconds.
        end (float): End time in seconds.
    """
    
    def __init__(self, word, start, end):
        """
        Initialize a WordTimestamp.
        
        Args:
            word (str): The word text.
            start (float): Start time in seconds.
            end (float): End time in seconds.
        """
        self.word = word
        self.start = start
        self.end = end
    
    def to_dict(self):
        """
        Convert to dictionary.
        
        Returns:
            dict: Dictionary representation.
        """
        return {
            "word": self.word,
            "start": self.start,
            "end": self.end
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create from dictionary.
        
        Args:
            data (dict): Dictionary representation.
            
        Returns:
            WordTimestamp: New instance.
        """
        return cls(
            word=data.get("word", ""),
            start=data.get("start", 0.0),
            end=data.get("end", 0.0)
        )


class Lyrics:
    """
    Class representing lyrics data.
    
    Attributes:
        song_name (str): Name of the song.
        artist_name (str): Name of the artist.
        lyrics_text (str): Full lyrics text.
        word_timestamps (list): List of WordTimestamp objects.
    """
    
    def __init__(self):
        """Initialize a Lyrics object."""
        self.logger = logging.getLogger("SequenceMaker.Lyrics")
        
        self.song_name = ""
        self.artist_name = ""
        self.lyrics_text = ""
        self.word_timestamps = []
    
    def to_dict(self):
        """
        Convert to dictionary.
        
        Returns:
            dict: Dictionary representation.
        """
        return {
            "song_name": self.song_name,
            "artist_name": self.artist_name,
            "lyrics_text": self.lyrics_text,
            "word_timestamps": [wt.to_dict() for wt in self.word_timestamps]
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create from dictionary.
        
        Args:
            data (dict): Dictionary representation.
            
        Returns:
            Lyrics: New instance.
        """
        lyrics = cls()
        
        lyrics.song_name = data.get("song_name", "")
        lyrics.artist_name = data.get("artist_name", "")
        lyrics.lyrics_text = data.get("lyrics_text", "")
        
        # Parse word timestamps
        word_timestamps_data = data.get("word_timestamps", [])
        lyrics.word_timestamps = [
            WordTimestamp.from_dict(wt_data) for wt_data in word_timestamps_data
        ]
        
        return lyrics
    
    def add_word_timestamp(self, word, start, end):
        """
        Add a word timestamp.
        
        Args:
            word (str): The word text.
            start (float): Start time in seconds.
            end (float): End time in seconds.
        """
        self.word_timestamps.append(WordTimestamp(word, start, end))
    
    def get_word_at_time(self, time):
        """
        Get the word at a specific time.
        
        Args:
            time (float): Time in seconds.
            
        Returns:
            WordTimestamp or None: The word at the specified time, or None if not found.
        """
        for word_timestamp in self.word_timestamps:
            if word_timestamp.start <= time <= word_timestamp.end:
                return word_timestamp
        
        return None