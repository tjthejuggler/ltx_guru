"""
Sequence Maker - Preference Manager

This module defines the PreferenceManager class, which handles storing and retrieving
user preferences for the preference learning system.
"""

import os
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path


class PreferenceManager:
    """
    Manages user preferences for the preference learning system.
    
    This manager stores user feedback in a SQLite database and provides methods
    for retrieving and formatting preferences for LLM consumption.
    """
    
    def __init__(self, app):
        """
        Initialize the preference manager.
        
        Args:
            app: The main application instance.
        """
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.PreferenceManager")
        
        # Create preferences database directory and file
        self.db_path = Path.home() / ".sequence_maker" / "preferences.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize the database
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create preferences table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_identifier TEXT,
                feedback_text TEXT,
                sentiment INTEGER,
                tags TEXT,
                created_at TEXT
            )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info(f"Preferences database initialized at {self.db_path}")
        except Exception as e:
            self.logger.error(f"Error initializing preferences database: {e}")
    
    def add_feedback(self, song_identifier, feedback_text, sentiment, tags=None):
        """
        Add user feedback to the database.
        
        Args:
            song_identifier: Identifier for the song (filename or hash)
            feedback_text: User's feedback text
            sentiment: 1 (positive), 0 (neutral), -1 (negative)
            tags: List of tags (e.g., ["beat sync", "color choice"])
            
        Returns:
            bool: Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert tags list to JSON string
            tags_json = json.dumps(tags) if tags else "[]"
            
            # Insert feedback
            cursor.execute(
                "INSERT INTO preferences (song_identifier, feedback_text, sentiment, tags, created_at) VALUES (?, ?, ?, ?, ?)",
                (song_identifier, feedback_text, sentiment, tags_json, datetime.now().isoformat())
            )
            
            conn.commit()
            conn.close()
            self.logger.info(f"Added feedback for {song_identifier}: {feedback_text}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding feedback: {e}")
            return False
    
    def get_preference_summary(self, song_identifier, max_items=5):
        """
        Get a summary of preferences for a song.
        
        Args:
            song_identifier: Identifier for the song
            max_items: Maximum number of feedback items to include
            
        Returns:
            str: Formatted preference summary
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get song-specific preferences
            cursor.execute(
                "SELECT feedback_text, sentiment, tags FROM preferences WHERE song_identifier = ? ORDER BY created_at DESC LIMIT ?",
                (song_identifier, max_items)
            )
            song_preferences = cursor.fetchall()
            
            # Get general preferences if needed
            if len(song_preferences) < max_items:
                cursor.execute(
                    "SELECT feedback_text, sentiment, tags FROM preferences WHERE song_identifier != ? ORDER BY created_at DESC LIMIT ?",
                    (song_identifier, max_items - len(song_preferences))
                )
                general_preferences = cursor.fetchall()
            else:
                general_preferences = []
                
            conn.close()
            
            # Format the summary
            summary = "User Preference Summary (Apply these guidelines where appropriate):\n"
            
            # Add song-specific preferences
            if song_preferences:
                summary += "- Song-specific preferences:\n"
                for feedback, sentiment, tags_json in song_preferences:
                    sentiment_str = "Likes" if sentiment > 0 else "Dislikes" if sentiment < 0 else "Neutral on"
                    summary += f"  - {sentiment_str}: {feedback}\n"
            
            # Add general preferences
            if general_preferences:
                summary += "- General preferences:\n"
                for feedback, sentiment, tags_json in general_preferences:
                    sentiment_str = "Likes" if sentiment > 0 else "Dislikes" if sentiment < 0 else "Neutral on"
                    summary += f"  - {sentiment_str}: {feedback}\n"
                    
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting preference summary: {e}")
            return ""
    
    def get_all_preferences(self, limit=None):
        """
        Get all preferences from the database.
        
        Args:
            limit: Maximum number of preferences to retrieve
            
        Returns:
            list: List of preference dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # This enables column access by name
            cursor = conn.cursor()
            
            if limit:
                cursor.execute("SELECT * FROM preferences ORDER BY created_at DESC LIMIT ?", (limit,))
            else:
                cursor.execute("SELECT * FROM preferences ORDER BY created_at DESC")
                
            rows = cursor.fetchall()
            conn.close()
            
            # Convert rows to dictionaries
            preferences = []
            for row in rows:
                preference = dict(row)
                # Parse tags JSON
                preference['tags'] = json.loads(preference['tags'])
                preferences.append(preference)
                
            return preferences
            
        except Exception as e:
            self.logger.error(f"Error getting all preferences: {e}")
            return []
    
    def get_preferences_for_song(self, song_identifier, limit=None):
        """
        Get preferences for a specific song.
        
        Args:
            song_identifier: Identifier for the song
            limit: Maximum number of preferences to retrieve
            
        Returns:
            list: List of preference dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if limit:
                cursor.execute(
                    "SELECT * FROM preferences WHERE song_identifier = ? ORDER BY created_at DESC LIMIT ?",
                    (song_identifier, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM preferences WHERE song_identifier = ? ORDER BY created_at DESC",
                    (song_identifier,)
                )
                
            rows = cursor.fetchall()
            conn.close()
            
            # Convert rows to dictionaries
            preferences = []
            for row in rows:
                preference = dict(row)
                # Parse tags JSON
                preference['tags'] = json.loads(preference['tags'])
                preferences.append(preference)
                
            return preferences
            
        except Exception as e:
            self.logger.error(f"Error getting preferences for song {song_identifier}: {e}")
            return []
    
    def clear_preferences(self):
        """
        Clear all preferences from the database.
        
        Returns:
            bool: Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM preferences")
            
            conn.commit()
            conn.close()
            self.logger.info("Cleared all preferences from the database")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing preferences: {e}")
            return False