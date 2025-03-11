"""
Sequence Maker - Main Application Class

This module contains the main application class that initializes and coordinates
all components of the Sequence Maker application.
"""

import os
import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication

from app.config import Config
from ui.main_window import MainWindow
from managers.project_manager import ProjectManager
from managers.timeline_manager import TimelineManager
from managers.audio_manager import AudioManager
from managers.ball_manager import BallManager
from managers.llm_manager import LLMManager
from managers.undo_manager import UndoManager


class SequenceMakerApp:
    """Main application class for Sequence Maker."""
    
    def __init__(self, project_file=None, audio_file=None, debug_mode=False):
        """
        Initialize the Sequence Maker application.
        
        Args:
            project_file (str, optional): Path to a project file to load on startup.
            audio_file (str, optional): Path to an audio file to load on startup.
            debug_mode (bool, optional): Enable debug mode. Defaults to False.
        """
        self.debug_mode = debug_mode
        self._setup_logging()
        
        self.logger.info("Initializing Sequence Maker Application")
        
        # Initialize the Qt application
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setApplicationName("Sequence Maker")
        
        # Load configuration
        self.config = Config()
        
        # Initialize managers
        self._init_managers()
        
        # Initialize UI
        self._init_ui()
        
        # Load initial files if provided
        if project_file:
            self.logger.info(f"Loading project file: {project_file}")
            self.project_manager.load_project(project_file)
        elif audio_file:
            self.logger.info(f"Loading audio file: {audio_file}")
            self.audio_manager.load_audio(audio_file)
        else:
            # Create a new untitled project by default
            self.logger.info("Creating new untitled project")
            self.project_manager.new_project("Untitled Project")
    
    def _setup_logging(self):
        """Set up logging configuration."""
        log_level = logging.DEBUG if self.debug_mode else logging.INFO
        
        # Create logs directory if it doesn't exist
        logs_dir = Path.home() / ".sequence_maker" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / "sequence_maker.log"),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("SequenceMaker")
    
    def _init_managers(self):
        """Initialize all application managers."""
        self.logger.info("Initializing application managers")
        
        # Create managers
        self.project_manager = ProjectManager(self)
        self.timeline_manager = TimelineManager(self)
        self.audio_manager = AudioManager(self)
        self.ball_manager = BallManager(self)
        self.llm_manager = LLMManager(self)
        self.undo_manager = UndoManager(self)
        
        # Connect managers as needed
        self.timeline_manager.set_undo_manager(self.undo_manager)
    
    def _init_ui(self):
        """Initialize the user interface."""
        self.logger.info("Initializing user interface")
        
        # Create main window
        self.main_window = MainWindow(self)
        
        # Connect UI signals to managers
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect UI signals to manager slots."""
        # Connect timeline signals
        self.main_window.timeline_widget.position_changed.connect(
            self.timeline_manager.set_position
        )
        
        # Connect audio signals
        self.main_window.audio_widget.play_clicked.connect(
            self.audio_manager.play
        )
        self.main_window.audio_widget.pause_clicked.connect(
            self.audio_manager.pause
        )
        self.main_window.audio_widget.stop_clicked.connect(
            self.audio_manager.stop
        )
        
        # Connect project signals
        self.main_window.new_action.triggered.connect(
            self.project_manager.new_project
        )
        self.main_window.open_action.triggered.connect(
            self.project_manager.load_project
        )
        self.main_window.save_action.triggered.connect(
            self.project_manager.save_project
        )
        
        # Connect ball control signals
        self.main_window.connect_balls_action.triggered.connect(
            self.ball_manager.connect_balls
        )
    
    def run(self):
        """Run the application main loop."""
        self.logger.info("Starting application main loop")
        
        # Show the main window
        self.main_window.show()
        
        # Start autosave timer
        self.project_manager.start_autosave()
        
        # Run the Qt application
        return self.qt_app.exec()
    
    def shutdown(self):
        """Perform cleanup before application shutdown."""
        self.logger.info("Shutting down application")
        
        # Stop autosave
        self.project_manager.stop_autosave()
        
        # Stop audio playback
        self.audio_manager.stop()
        
        # Disconnect from balls
        self.ball_manager.disconnect_balls()
        
        # Save application state
        self.config.save()
        
        self.logger.info("Application shutdown complete")