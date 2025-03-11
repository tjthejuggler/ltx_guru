"""
Sequence Maker - Project Manager

This module defines the ProjectManager class, which handles project operations.
"""

import os
import logging
import threading
import time
from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal

from models.project import Project
from models.timeline import Timeline
from app.constants import PROJECT_FILE_EXTENSION


class ProjectManager(QObject):
    """
    Manages project operations such as creating, loading, and saving projects.
    
    Signals:
        project_loaded: Emitted when a project is loaded.
        project_saved: Emitted when a project is saved.
        project_changed: Emitted when the project is modified.
        autosave_completed: Emitted when an autosave is completed.
    """
    
    # Signals
    project_loaded = pyqtSignal(object)
    project_saved = pyqtSignal(str)
    project_changed = pyqtSignal()
    autosave_completed = pyqtSignal(str)
    
    def __init__(self, app):
        """
        Initialize the project manager.
        
        Args:
            app: The main application instance.
        """
        super().__init__()
        
        self.logger = logging.getLogger("SequenceMaker.ProjectManager")
        self.app = app
        
        # Current project
        self.current_project = None
        
        # Autosave
        self.autosave_interval = app.config.get("general", "autosave_interval")
        self.max_autosave_files = app.config.get("general", "max_autosave_files")
        self.autosave_dir = Path.home() / ".sequence_maker" / "autosave"
        self.autosave_dir.mkdir(parents=True, exist_ok=True)
        self.autosave_thread = None
        self.autosave_stop_event = threading.Event()
    
    def new_project(self, name="Untitled Project"):
        """
        Create a new project.
        
        Args:
            name (str, optional): Project name. Defaults to "Untitled Project".
        
        Returns:
            Project: The new project.
        """
        self.logger.info(f"Creating new project: {name}")
        
        # Create a new project
        project = Project(name=name)
        
        # Set default settings from config
        project.default_pixels = self.app.config.get("timeline", "default_pixels")
        project.refresh_rate = self.app.config.get("timeline", "default_refresh_rate")
        project.total_duration = self.app.config.get("timeline", "default_duration")
        
        # Create default timelines
        default_ball_count = self.app.config.get("timeline", "default_ball_count")
        for i in range(default_ball_count):
            timeline = Timeline(name=f"Ball {i+1}", default_pixels=project.default_pixels)
            project.add_timeline(timeline)
        
        # Set as current project
        self.current_project = project
        
        # Emit signal
        self.project_changed.emit()
        
        # Save initial state for undo
        if self.app.undo_manager:
            self.app.undo_manager.save_state("new_project")
        
        return project
    
    def load_project(self, file_path):
        """
        Load a project from a file.
        
        Args:
            file_path (str): Path to the project file.
        
        Returns:
            Project: The loaded project, or None if loading failed.
        """
        self.logger.info(f"Loading project from: {file_path}")
        
        # Load the project
        project = Project.load(file_path)
        
        if project:
            # Set as current project
            self.current_project = project
            
            # Add to recent projects
            self.app.config.add_recent_project(file_path)
            
            # Save as last project
            self.app.config.set("general", "last_project", file_path)
            self.app.config.save()
            
            # Emit signal
            self.project_loaded.emit(project)
            
            # Save initial state for undo
            if self.app.undo_manager:
                self.app.undo_manager.save_state("load_project")
            
            return project
        else:
            self.logger.error(f"Failed to load project from: {file_path}")
            return None
    
    def save_project(self, file_path=None):
        """
        Save the current project to a file.
        
        Args:
            file_path (str, optional): Path to save the project to. If None, uses the current file_path.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.current_project:
            self.logger.warning("No project to save")
            return False
        
        # Use current file path if none provided
        if file_path is None and self.current_project.file_path:
            file_path = self.current_project.file_path
        
        # If still no file path, prompt user (handled by UI)
        if not file_path:
            self.logger.warning("No file path for save")
            return False
        
        self.logger.info(f"Saving project to: {file_path}")
        
        # Save the project
        success = self.current_project.save(file_path)
        
        if success:
            # Add to recent projects
            self.app.config.add_recent_project(file_path)
            
            # Save as last project
            self.app.config.set("general", "last_project", file_path)
            self.app.config.save()
            
            # Emit signal
            self.project_saved.emit(file_path)
        
        return success
    
    def start_autosave(self):
        """Start the autosave thread."""
        if self.autosave_thread and self.autosave_thread.is_alive():
            self.logger.warning("Autosave thread already running")
            return
        
        self.logger.info(f"Starting autosave thread (interval: {self.autosave_interval}s)")
        
        # Reset stop event
        self.autosave_stop_event.clear()
        
        # Start thread
        self.autosave_thread = threading.Thread(
            target=self._autosave_worker,
            daemon=True
        )
        self.autosave_thread.start()
    
    def stop_autosave(self):
        """Stop the autosave thread."""
        if not self.autosave_thread or not self.autosave_thread.is_alive():
            return
        
        self.logger.info("Stopping autosave thread")
        
        # Set stop event
        self.autosave_stop_event.set()
        
        # Wait for thread to finish
        self.autosave_thread.join(timeout=1.0)
        
        if self.autosave_thread.is_alive():
            self.logger.warning("Autosave thread did not stop cleanly")
    
    def _autosave_worker(self):
        """Autosave worker thread function."""
        while not self.autosave_stop_event.is_set():
            # Sleep for the autosave interval
            for _ in range(self.autosave_interval):
                time.sleep(1)
                if self.autosave_stop_event.is_set():
                    return
            
            # Perform autosave
            self._perform_autosave()
    
    def _perform_autosave(self):
        """Perform an autosave operation."""
        if not self.current_project:
            return
        
        # Generate autosave file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = self.current_project.name.replace(" ", "_")
        autosave_file = self.autosave_dir / f"autosave_{project_name}_{timestamp}{PROJECT_FILE_EXTENSION}"
        
        self.logger.info(f"Performing autosave to: {autosave_file}")
        
        # Save the project
        success = self.current_project.save(str(autosave_file))
        
        if success:
            # Emit signal
            self.autosave_completed.emit(str(autosave_file))
            
            # Clean up old autosave files
            self._cleanup_autosave_files()
    
    def _cleanup_autosave_files(self):
        """Clean up old autosave files, keeping only the most recent ones."""
        # Get all autosave files
        autosave_files = list(self.autosave_dir.glob(f"autosave_*{PROJECT_FILE_EXTENSION}"))
        
        # Sort by modification time (newest first)
        autosave_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        # Remove excess files
        for file in autosave_files[self.max_autosave_files:]:
            self.logger.info(f"Removing old autosave file: {file}")
            try:
                file.unlink()
            except Exception as e:
                self.logger.error(f"Error removing autosave file: {e}")
    
    def get_autosave_files(self):
        """
        Get a list of available autosave files.
        
        Returns:
            list: List of (file_path, timestamp) tuples.
        """
        # Get all autosave files
        autosave_files = list(self.autosave_dir.glob(f"autosave_*{PROJECT_FILE_EXTENSION}"))
        
        # Sort by modification time (newest first)
        autosave_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        # Create list of (file_path, timestamp) tuples
        result = []
        for file in autosave_files:
            timestamp = datetime.fromtimestamp(file.stat().st_mtime)
            result.append((str(file), timestamp))
        
        return result
    
    def recover_autosave(self, file_path):
        """
        Recover a project from an autosave file.
        
        Args:
            file_path (str): Path to the autosave file.
        
        Returns:
            Project: The recovered project, or None if recovery failed.
        """
        return self.load_project(file_path)