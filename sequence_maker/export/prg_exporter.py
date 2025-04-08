"""
Sequence Maker - PRG Exporter

This module defines the PRGExporter class, which exports sequences to PRG format.
"""

import os
import json
import logging
import subprocess
import tempfile


class PRGExporter:
    """Exports sequences to PRG format."""
    
    def __init__(self, app):
        """
        Initialize the PRG exporter.
        
        Args:
            app: The main application instance.
        """
        self.logger = logging.getLogger("SequenceMaker.PRGExporter")
        self.app = app
    
    def export_timeline(self, timeline, file_path, refresh_rate=None):
        """
        Export a timeline to a PRG file.
        
        Args:
            timeline: Timeline to export.
            file_path (str): Path to save the PRG file.
            refresh_rate (int, optional): Refresh rate in Hz. If None, uses the project refresh rate.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Create temporary JSON file
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
                temp_json_path = temp_file.name
            
            # Get JSON data
            json_data = timeline.to_json_sequence(refresh_rate)
            
            # Write JSON to temporary file
            with open(temp_json_path, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Call prg_generator.py with absolute path
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            prg_generator_path = os.path.join(root_dir, "prg_generator.py")
            
            self.logger.debug(f"Using prg_generator at: {prg_generator_path}")
            
            result = subprocess.run(
                ["python3", prg_generator_path, temp_json_path, file_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Log output
            self.logger.debug(f"prg_generator output: {result.stdout}")
            
            # Clean up temporary file
            os.unlink(temp_json_path)
            
            self.logger.info(f"Exported timeline to {file_path}")
            return True
        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error calling prg_generator: {e}")
            self.logger.error(f"prg_generator stderr: {e.stderr}")
            return False
        
        except Exception as e:
            self.logger.error(f"Error exporting timeline to PRG: {e}")
            return False
    
    def export_project(self, directory, refresh_rate=None):
        """
        Export all timelines in the current project to PRG files.
        
        Args:
            directory (str): Directory to save the PRG files.
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
            file_name = f"{timeline.name.replace(' ', '_')}.prg"
            file_path = os.path.join(directory, file_name)
            
            # Export timeline
            if self.export_timeline(timeline, file_path, refresh_rate):
                success_count += 1
        
        self.logger.info(f"Exported {success_count}/{total_count} timelines to {directory}")
        return success_count, total_count
    def export(self, file_path, refresh_rate=None):
        """
        Export the current timeline to a PRG file.
        
        This is a convenience method that exports the first timeline in the current project.
        
        Args:
            file_path (str): Path to save the PRG file.
            refresh_rate (int, optional): Refresh rate in Hz. If None, uses the project refresh rate.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        # Check if project is loaded
        if not self.app.project_manager.current_project:
            self.logger.warning("Cannot export: No project loaded")
            return False
        
        # Get project
        project = self.app.project_manager.current_project
        
        # Check if there are any timelines
        if not project.timelines:
            self.logger.warning("Cannot export: No timelines in project")
            return False
        
        # Get the first timeline
        timeline = project.timelines[0]
        
        # Export timeline
        return self.export_timeline(timeline, file_path, refresh_rate)
    
    
    def export_project_with_json(self, directory, refresh_rate=None):
        """
        Export all timelines in the current project to both JSON and PRG files.
        
        Args:
            directory (str): Directory to save the files.
            refresh_rate (int, optional): Refresh rate in Hz. If None, uses the project refresh rate.
        
        Returns:
            tuple: (json_success_count, prg_success_count, total_count)
        """
        # Check if project is loaded
        if not self.app.project_manager.current_project:
            self.logger.warning("Cannot export project: No project loaded")
            return 0, 0, 0
        
        # Get project
        project = self.app.project_manager.current_project
        
        # Use project refresh rate if not specified
        if refresh_rate is None:
            refresh_rate = project.refresh_rate
        
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Create subdirectories
        json_dir = os.path.join(directory, "json")
        prg_dir = os.path.join(directory, "prg")
        
        os.makedirs(json_dir, exist_ok=True)
        os.makedirs(prg_dir, exist_ok=True)
        
        # Export each timeline
        json_success_count = 0
        prg_success_count = 0
        total_count = len(project.timelines)
        
        for i, timeline in enumerate(project.timelines):
            # Create file paths
            base_name = timeline.name.replace(' ', '_')
            json_path = os.path.join(json_dir, f"{base_name}.json")
            prg_path = os.path.join(prg_dir, f"{base_name}.prg")
            
            # Export to JSON
            from export.json_exporter import JSONExporter
            json_exporter = JSONExporter(self.app)
            # Always use 100 Hz refresh rate for JSON exports for 1/100th second precision
            if json_exporter.export_timeline(timeline, json_path, 100):
                json_success_count += 1
            
            
            # Export to PRG
            if self.export_timeline(timeline, prg_path, refresh_rate):
                prg_success_count += 1
        
        self.logger.info(
            f"Exported {json_success_count}/{total_count} JSON files and "
            f"{prg_success_count}/{total_count} PRG files to {directory}"
        )
        
        return json_success_count, prg_success_count, total_count