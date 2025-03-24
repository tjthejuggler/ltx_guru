"""
Sequence Maker - Autosave Manager

This module defines the AutosaveManager class, which handles automatic project state saves and version control.
"""

import logging
import os
import json
import shutil
from datetime import datetime
from pathlib import Path

class AutosaveManager:
    """Manager for automatic project state saves and version control."""
    
    def __init__(self, app):
        """
        Initialize the autosave manager.
        
        Args:
            app: The main application instance.
        """
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.AutosaveManager")
        self.max_versions = app.config.get("general", "max_autosave_files", 10)
        self.autosave_dir = None
        
        # Create autosave directory if it doesn't exist
        self._ensure_autosave_directory()
    
    def _ensure_autosave_directory(self):
        """Ensure the autosave directory exists."""
        if not self.app.project_manager.current_project or not self.app.project_manager.current_project.file_path:
            return
            
        # Create autosave directory next to the project file
        project_path = Path(self.app.project_manager.current_project.file_path)
        self.autosave_dir = project_path.parent / f"{project_path.stem}_versions"
        self.autosave_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"Autosave directory: {self.autosave_dir}")
    
    def save_version(self, reason="LLM Operation"):
        """
        Save a version of the current project.
        
        Args:
            reason (str): Reason for saving the version.
        
        Returns:
            bool: True if the version was saved, False otherwise.
        """
        if not self.app.project_manager.current_project or not self.app.project_manager.current_project.file_path:
            return False
            
        # Ensure autosave directory exists
        self._ensure_autosave_directory()
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create version name
        version_name = f"{timestamp}_{reason.replace(' ', '_')}"
        
        # Create version file path
        version_path = self.autosave_dir / f"{version_name}.json"
        
        # Save project to version file
        try:
            # Get project data
            project_data = self.app.project_manager.current_project.to_dict()
            
            # Add version metadata
            project_data["version_metadata"] = {
                "timestamp": timestamp,
                "reason": reason,
                "original_file": self.app.project_manager.current_project.file_path
            }
            
            # Write to file
            with open(version_path, "w") as f:
                json.dump(project_data, f, indent=2)
            
            self.logger.info(f"Saved version: {version_path}")
            
            # Prune old versions if needed
            self._prune_old_versions()
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving version: {e}")
            return False
    
    def _prune_old_versions(self):
        """Remove old versions if max_versions is exceeded."""
        if not self.autosave_dir or not self.autosave_dir.exists():
            return
            
        # Get all version files
        version_files = sorted(self.autosave_dir.glob("*.json"))
        
        # Check if we need to prune
        if len(version_files) <= self.max_versions:
            return
            
        # Remove oldest versions
        versions_to_remove = version_files[:-self.max_versions]
        for version_file in versions_to_remove:
            try:
                version_file.unlink()
                self.logger.info(f"Removed old version: {version_file}")
            except Exception as e:
                self.logger.error(f"Error removing old version: {e}")
    
    def get_versions(self):
        """
        Get a list of available versions.
        
        Returns:
            list: List of version dictionaries with metadata.
        """
        if not self.autosave_dir or not self.autosave_dir.exists():
            return []
            
        # Get all version files
        version_files = sorted(self.autosave_dir.glob("*.json"), reverse=True)
        
        versions = []
        for version_file in version_files:
            try:
                # Read version metadata
                with open(version_file, "r") as f:
                    data = json.load(f)
                    
                metadata = data.get("version_metadata", {})
                versions.append({
                    "file_path": str(version_file),
                    "timestamp": metadata.get("timestamp", ""),
                    "reason": metadata.get("reason", ""),
                    "file_name": version_file.name
                })
            except Exception as e:
                self.logger.error(f"Error reading version metadata: {e}")
        
        return versions
    
    def restore_version(self, version_path):
        """
        Restore a project version.
        
        Args:
            version_path (str): Path to the version file.
        
        Returns:
            bool: True if the version was restored, False otherwise.
        """
        try:
            # Save current state before restoring
            self.save_version("Before Restore")
            
            # Load version
            with open(version_path, "r") as f:
                version_data = json.load(f)
            
            # Remove version metadata
            if "version_metadata" in version_data:
                del version_data["version_metadata"]
            
            # Load project from version data
            project = self.app.project_manager.load_from_dict(version_data)
            
            # Set current project
            self.app.project_manager.set_current_project(project)
            
            self.logger.info(f"Restored version: {version_path}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error restoring version: {e}")
            return False