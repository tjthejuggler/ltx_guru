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
    
    def export_timeline(self, timeline, file_path, refresh_rate=100):
        """
        Export a timeline to a JSON file.
        
        Args:
            timeline: Timeline to export.
            file_path (str): Path to save the JSON file.
            refresh_rate (int, optional): Refresh rate in Hz. Default is 100 Hz for 1/100th second precision.
        
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
    
    def export_project(self, directory, base_filename=None, refresh_rate=100):
        """
        Export all timelines in the current project to JSON files.
        
        Args:
            directory (str): Directory to save the JSON files.
            base_filename (str, optional): Base filename to use for exports. If provided,
                                          files will be named {base_filename}_{timeline_name}.json.
                                          If None, project name will be used as base.
            refresh_rate (int, optional): Refresh rate in Hz. Default is 100 Hz for 1/100th second precision.
        
        Returns:
            tuple: (success_count, total_count, exported_files)
        """
        # Check if project is loaded
        if not self.app.project_manager.current_project:
            self.logger.warning("Cannot export project: No project loaded")
            return 0, 0, []
        
        # Get project
        project = self.app.project_manager.current_project
        
        # Use project name as base filename if not specified
        if base_filename is None:
            base_filename = project.name.replace(' ', '_')
        else:
            # Remove extension if present
            base_filename = os.path.splitext(os.path.basename(base_filename))[0]
        
        # Always use 100 Hz refresh rate for 1/100th second precision
        # (refresh_rate parameter is already defaulted to 100)
        
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Export each timeline
        success_count = 0
        total_count = len(project.timelines)
        exported_files = []
        
        for i, timeline in enumerate(project.timelines):
            # Create file path with project name prefix
            file_name = f"{base_filename}_{timeline.name.replace(' ', '_')}.json"
            file_path = os.path.join(directory, file_name)
            
            # Export timeline
            if self.export_timeline(timeline, file_path, refresh_rate):
                success_count += 1
                exported_files.append(file_path)
        
        self.logger.info(f"Exported {success_count}/{total_count} timelines to {directory}")
        return success_count, total_count, exported_files