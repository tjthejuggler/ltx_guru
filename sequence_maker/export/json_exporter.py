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
    
    def export_timeline(self, timeline, file_path): # refresh_rate parameter removed
        """
        Export a timeline to a JSON file, ensuring the output JSON has a 100Hz refresh rate.
        It takes the 1000Hz-scaled data from timeline.to_json_sequence() and converts it.
        
        Args:
            timeline: Timeline to export.
            file_path (str): Path to save the JSON file.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Get JSON data (this will be 1000Hz scaled from Timeline.to_json_sequence)
            json_data_1000hz = timeline.to_json_sequence()
            
            # Convert to 100Hz for this specific JSON export type
            json_data_100hz = {
                "default_pixels": json_data_1000hz.get("default_pixels", 1),
                "color_format": json_data_1000hz.get("color_format", "rgb"),
                "refresh_rate": 100, # Target 100Hz for this JSON output
                "end_time": int(round(json_data_1000hz.get("end_time", 0) / 10)),
                "sequence": {}
            }
            for time_key_1000hz, segment_data in json_data_1000hz.get("sequence", {}).items():
                time_key_100hz = str(int(round(int(time_key_1000hz) / 10)))
                json_data_100hz["sequence"][time_key_100hz] = segment_data
            
            json_data = json_data_100hz # Use the rescaled data
            
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
    
    def export_project(self, directory, base_filename=None): # refresh_rate parameter removed
        """
        Export all timelines in the current project to JSON files (100Hz scaled).
        
        Args:
            directory (str): Directory to save the JSON files.
            base_filename (str, optional): Base filename to use for exports. If provided,
                                           files will be named {base_filename}_{timeline_name}.json.
                                           If None, project name will be used as base.
        
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
        
        # The export_timeline method now handles ensuring the output JSON is 100Hz scaled.
        
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
            if self.export_timeline(timeline, file_path):
                success_count += 1
                exported_files.append(file_path)
        
        self.logger.info(f"Exported {success_count}/{total_count} timelines to {directory}")
        return success_count, total_count, exported_files