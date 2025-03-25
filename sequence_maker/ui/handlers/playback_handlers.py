"""
Sequence Maker - Playback Handlers

This module defines the PlaybackHandlers class, which contains handlers for playback-related
operations such as play, pause, and stop operations.
"""


class PlaybackHandlers:
    """Playback operation handlers for the main window."""
    
    def __init__(self, main_window):
        """
        Initialize playback handlers.
        
        Args:
            main_window: The main window instance.
        """
        self.main_window = main_window
        self.app = main_window.app
    
    def on_play(self):
        """Play audio."""
        # Start playback
        self.app.audio_manager.play()
        
        # Update UI
        self.main_window._on_playback_started()
    
    def on_pause(self):
        """Pause audio."""
        # Pause playback
        self.app.audio_manager.pause()
        
        # Update UI
        self.main_window._on_playback_paused()
    
    def on_stop(self):
        """Stop audio."""
        # Stop playback
        self.app.audio_manager.stop()
        
        # Update UI
        self.main_window._on_playback_stopped()
    
    def on_playback_started(self):
        """Handle playback started event."""
        # Update UI
        self.main_window.playback_actions.play_action.setVisible(False)
        self.main_window.playback_actions.pause_action.setVisible(True)
        self.main_window.playback_actions.stop_action.setEnabled(True)
    
    def on_playback_paused(self):
        """Handle playback paused event."""
        # Update UI
        self.main_window.playback_actions.play_action.setVisible(True)
        self.main_window.playback_actions.pause_action.setVisible(False)
        self.main_window.playback_actions.stop_action.setEnabled(True)
    
    def on_playback_stopped(self):
        """Handle playback stopped event."""
        # Update UI
        self.main_window.playback_actions.play_action.setVisible(True)
        self.main_window.playback_actions.pause_action.setVisible(False)
        self.main_window.playback_actions.stop_action.setEnabled(False)