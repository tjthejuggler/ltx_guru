"""
Sequence Maker - Application Context API

This module defines the AppContextAPI class, which provides a unified API for accessing
application state data.
"""

import logging
from datetime import datetime


class AppContextAPI:
    """
    Provides a unified API for accessing application state data.
    """
    
    def __init__(self, app):
        """
        Initialize the application context API.
        
        Args:
            app: The main application instance.
        """
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.AppContextAPI")
    
    def get_project_context(self):
        """
        Get the current project context.
        
        Returns:
            dict: Project context data.
        """
        if not self.app.project_manager.current_project:
            return {"error": "No project loaded"}
        
        project = self.app.project_manager.current_project
        
        return {
            "name": project.name,
            "created": project.created,
            "modified": project.modified,
            "description": project.description,
            "version": project.version,
            "default_pixels": project.default_pixels,
            "refresh_rate": project.refresh_rate,
            "total_duration": project.total_duration,
            "zoom_level": project.zoom_level,
            "timeline_count": len(project.timelines),
            "has_audio": bool(project.audio_file),
            "audio_duration": project.audio_duration,
            "has_lyrics": bool(project.lyrics and project.lyrics.lyrics_text)
        }
    
    def get_timeline_context(self, index=None):
        """
        Get timeline context data.
        
        Args:
            index (int, optional): Timeline index. If None, returns data for all timelines.
        
        Returns:
            dict or list: Timeline context data.
        """
        if not self.app.project_manager.current_project:
            return {"error": "No project loaded"}
        
        if index is not None:
            # Get specific timeline
            timeline = self.app.timeline_manager.get_timeline(index)
            if not timeline:
                return {"error": f"Timeline {index} not found"}
            
            return self._get_timeline_data(timeline, index)
        else:
            # Get all timelines
            timelines = []
            for i, timeline in enumerate(self.app.project_manager.current_project.timelines):
                timelines.append(self._get_timeline_data(timeline, i))
            
            return timelines
    
    def _get_timeline_data(self, timeline, index):
        """
        Get data for a specific timeline.
        
        Args:
            timeline: Timeline object.
            index (int): Timeline index.
        
        Returns:
            dict: Timeline data.
        """
        segments = []
        for i, segment in enumerate(timeline.segments):
            segments.append({
                "index": i,
                "start_time": segment.start_time,
                "end_time": segment.end_time,
                "duration": segment.get_duration(),
                "color": list(segment.color),
                "pixels": segment.pixels,
                "effects": [{"type": effect.type, "parameters": effect.parameters} for effect in segment.effects]
            })
        
        return {
            "index": index,
            "name": timeline.name,
            "default_pixels": timeline.default_pixels,
            "created": timeline.created,
            "modified": timeline.modified,
            "segment_count": len(timeline.segments),
            "segments": segments,
            "duration": timeline.get_duration()
        }
    
    def get_audio_context(self):
        """
        Get audio context data.
        
        Returns:
            dict: Audio context data.
        """
        if not self.app.audio_manager.audio_file:
            return {"error": "No audio loaded"}
        
        # Convert numpy arrays to lists for JSON serialization
        beat_times = None
        if self.app.audio_manager.beat_times is not None:
            beat_times = self.app.audio_manager.beat_times.tolist()
        
        return {
            "file": self.app.audio_manager.audio_file,
            "duration": self.app.audio_manager.duration,
            "sample_rate": self.app.audio_manager.sample_rate,
            "tempo": self.app.audio_manager.tempo,
            "beat_count": len(self.app.audio_manager.beat_times) if self.app.audio_manager.beat_times is not None else 0,
            "beat_times": beat_times,
            "is_playing": self.app.audio_manager.playing,
            "is_paused": self.app.audio_manager.paused,
            "current_position": self.app.audio_manager.position
        }
    
    def get_lyrics_context(self):
        """
        Get lyrics context data.
        
        Returns:
            dict: Lyrics context data.
        """
        if not self.app.project_manager.current_project or not self.app.project_manager.current_project.lyrics:
            return {"error": "No lyrics available"}
        
        lyrics = self.app.project_manager.current_project.lyrics
        
        word_timestamps = []
        for wt in lyrics.word_timestamps:
            word_timestamps.append({
                "word": wt.word,
                "start": wt.start,
                "end": wt.end
            })
        
        return {
            "song_name": lyrics.song_name,
            "artist_name": lyrics.artist_name,
            "lyrics_text": lyrics.lyrics_text,
            "word_count": len(lyrics.word_timestamps),
            "word_timestamps": word_timestamps
        }
    
    def get_full_context(self):
        """
        Get the full application context.
        
        Returns:
            dict: Full application context data.
        """
        return {
            "project": self.get_project_context(),
            "timelines": self.get_timeline_context(),
            "audio": self.get_audio_context(),
            "lyrics": self.get_lyrics_context(),
            "current_position": self.app.timeline_manager.position,
            "selected_timeline_index": self.app.timeline_manager.selected_timeline,
            "timestamp": datetime.now().isoformat()
        }