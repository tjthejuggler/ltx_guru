"""
Sequence Maker - JSON Exporter

This module defines the JSONExporter class, which exports sequences to JSON format.
"""

import os
import json
import logging


class JSONExporter:
    """Exports sequences to JSON format."""
    
    def __init__(self, app):
        """
        Initialize the JSON exporter.
        
        Args:
            app: The main application instance.
        """
        self.logger = logging.getLogger("SequenceMaker.JSONExporter")
        self.app = app
    
    def export_timeline(self, timeline, file_path, refresh_rate=None):
        """
        Export a timeline to a JSON file.
        
        Args:
            timeline: Timeline to export.
            file_path (str): Path to save the JSON file.
            refresh_rate (int, optional): Refresh rate in Hz. If None, uses the project refresh rate.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Get JSON data
            json_data = timeline.to_json_sequence(refresh_rate)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            self.logger.info(f"Exported timeline to {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting timeline to JSON: {e}")
            return False
    
    def export_project(self, directory, refresh_rate=None):
        """
        Export all timelines in the current project to JSON files.
        
        Args:
            directory (str): Directory to save the JSON files.
            refresh_rate (int, optional): Refresh rate in Hz. If None, uses the project refresh rate.
        
        Returns:
            tuple: (success_count, total_count)
        """
        # Check if project is loaded
        if not self.app.project_manager.current_project:
            self.logger.warning("Cannot export project: No project loaded")
            return 0, 0
        
        # Get project
        project = self.app.project_manager.current_project
        
        # Use project refresh rate if not specified
        if refresh_rate is None:
            refresh_rate = project.refresh_rate
        
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Export each timeline
        success_count = 0
        total_count = len(project.timelines)
        
        for i, timeline in enumerate(project.timelines):
            # Create file path
            file_name = f"{timeline.name.replace(' ', '_')}.json"
            file_path = os.path.join(directory, file_name)
            
            # Export timeline
            if self.export_timeline(timeline, file_path, refresh_rate):
                success_count += 1
        
        self.logger.info(f"Exported {success_count}/{total_count} timelines to {directory}")
        return success_count, total_count