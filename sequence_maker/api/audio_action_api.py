"""
Sequence Maker - Audio Action API

This module defines the AudioActionAPI class, which provides an API for LLM to control audio playback.
"""

import logging


class AudioActionAPI:
    """
    Provides an API for LLM to control audio playback.
    """
    
    def __init__(self, app):
        """
        Initialize the audio action API.
        
        Args:
            app: The main application instance.
        """
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.AudioActionAPI")
        
        # Register action handlers with the LLM manager
        self.app.llm_manager.register_action_handler("play_audio", self.play)
        self.app.llm_manager.register_action_handler("pause_audio", self.pause)
        self.app.llm_manager.register_action_handler("stop_audio", self.stop)
        self.app.llm_manager.register_action_handler("seek_audio", self.seek)
        self.app.llm_manager.register_action_handler("set_volume", self.set_volume)
    
    def play(self, parameters=None):
        """
        Start or resume audio playback.
        
        Args:
            parameters (dict, optional): Not used, but included for consistency.
        
        Returns:
            dict: Result of the operation.
        """
        try:
            success = self.app.audio_manager.play()
            return {"success": success}
        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
            return {"success": False, "error": str(e)}
    
    def pause(self, parameters=None):
        """
        Pause audio playback.
        
        Args:
            parameters (dict, optional): Not used, but included for consistency.
        
        Returns:
            dict: Result of the operation.
        """
        try:
            success = self.app.audio_manager.pause()
            return {"success": success}
        except Exception as e:
            self.logger.error(f"Error pausing audio: {e}")
            return {"success": False, "error": str(e)}
    
    def stop(self, parameters=None):
        """
        Stop audio playback.
        
        Args:
            parameters (dict, optional): Not used, but included for consistency.
        
        Returns:
            dict: Result of the operation.
        """
        try:
            success = self.app.audio_manager.stop()
            return {"success": success}
        except Exception as e:
            self.logger.error(f"Error stopping audio: {e}")
            return {"success": False, "error": str(e)}
    
    def seek(self, parameters):
        """
        Seek to a specific position in the audio.
        
        Args:
            parameters (dict): Parameters for the action.
                - position (float): Position in seconds.
        
        Returns:
            dict: Result of the operation.
        """
        try:
            # Extract parameters
            position = parameters.get("position")
            
            # Validate parameters
            if position is None:
                return {"success": False, "error": "Missing required parameters"}
            
            success = self.app.audio_manager.seek(position)
            return {"success": success, "position": position}
        except Exception as e:
            self.logger.error(f"Error seeking audio: {e}")
            return {"success": False, "error": str(e)}
    
    def set_volume(self, parameters):
        """
        Set the playback volume.
        
        Args:
            parameters (dict): Parameters for the action.
                - volume (float): Volume level (0.0 to 1.0).
        
        Returns:
            dict: Result of the operation.
        """
        try:
            # Extract parameters
            volume = parameters.get("volume")
            
            # Validate parameters
            if volume is None:
                return {"success": False, "error": "Missing required parameters"}
            
            # Ensure volume is in valid range
            volume = max(0.0, min(volume, 1.0))
            
            success = self.app.audio_manager.set_volume(volume)
            return {"success": success, "volume": volume}
        except Exception as e:
            self.logger.error(f"Error setting volume: {e}")
            return {"success": False, "error": str(e)}