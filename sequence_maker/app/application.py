"""
Sequence Maker - Main Application Class

This module contains the main application class that initializes and coordinates
all components of the Sequence Maker application.
"""

import os
import sys
import logging
import time
import tempfile
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QSplashScreen, QProxyStyle, QStyle
from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6.QtCore import Qt, QSize

from app.config import Config
from ui.main_window import MainWindow
from managers.project_manager import ProjectManager
from managers.timeline_manager import TimelineManager
from managers.audio_manager import AudioManager
from managers.ball_manager import BallManager
from managers.llm_manager import LLMManager
from managers.undo_manager import UndoManager
from resources.resources import get_icon_path

# Create a custom style that forces our icon to be used
class CustomIconStyle(QProxyStyle):
    """Custom style that forces our application icon to be used."""
    
    def __init__(self, icon_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_icon = QIcon(icon_path)
    
    def standardIcon(self, standardIcon, option=None, widget=None):
        """Override standard icons to use our custom icon."""
        if standardIcon == QStyle.StandardPixmap.SP_TitleBarMenuButton:
            return self.app_icon
        if standardIcon == QStyle.StandardPixmap.SP_TitleBarNormalButton:
            return self.app_icon
        if standardIcon == QStyle.StandardPixmap.SP_DesktopIcon:
            return self.app_icon
        return super().standardIcon(standardIcon, option, widget)


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
        
        # Set application name for window class matching - MUST match StartupWMClass
        self.qt_app.setApplicationName("SequenceMaker")
        
        # Set desktop filename to match .desktop file name
        self.qt_app.setDesktopFileName("sequence_maker")
        
        # Set application display name
        self.qt_app.setApplicationDisplayName("Sequence Maker")
        
        # Get icon path - use absolute path for better compatibility
        icon_path = get_icon_path("sm_app_icon_better.jpeg")
        self.logger.info(f"Setting application icon from: {icon_path}")
        
        # Create and apply custom style that forces our icon
        custom_style = CustomIconStyle(icon_path)
        self.qt_app.setStyle(custom_style)
        
        # Create icon from the PNG
        self.app_icon = QIcon(icon_path)
        
        # Set multiple sizes for the icon (important for proper display)
        for size in [16, 24, 32, 48, 64, 128, 256]:
            self.app_icon.addPixmap(QPixmap(icon_path).scaled(
                size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        # Set the application icon in multiple ways to ensure it's used
        self.qt_app.setWindowIcon(self.app_icon)
        
        # Set the icon as a property
        self.qt_app.setProperty("windowIcon", self.app_icon)
        
        # Set the icon for all windows
        QIcon.setThemeName("hicolor")
        QIcon.setThemeSearchPaths([os.path.expanduser("~/.local/share/icons"), os.path.expanduser("~/.icons")])
        
        # Create and show splash screen
        splash_pixmap = QPixmap(icon_path).scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio)
        self.logger.info(f"Created splash pixmap with size: {splash_pixmap.width()}x{splash_pixmap.height()}")
        self.splash = QSplashScreen(splash_pixmap)
        self.splash.show()
        
        # Process events to ensure splash screen is displayed
        self.qt_app.processEvents()
        
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
            # Try to load the last opened project
            last_project = self.config.get("general", "last_project")
            if last_project and os.path.exists(last_project):
                self.logger.info(f"Loading last project: {last_project}")
                self.project_manager.load_project(last_project)
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
        # Note: We don't connect open_action directly to load_project because
        # load_project requires a file path parameter, which is handled by _on_open in main_window.py
        self.main_window.new_action.triggered.connect(
            self.project_manager.new_project
        )
        # Don't connect open_action directly to load_project
        # self.main_window.open_action.triggered.connect(
        #     self.project_manager.load_project
        # )
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
        
        # Add a small delay to show the splash screen for a moment
        time.sleep(1.5)
        
        # Show the main window
        self.main_window.show()
        
        # Close the splash screen
        self.splash.finish(self.main_window)
        
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