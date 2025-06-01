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
    
    def export_timeline(self, timeline, file_path): # refresh_rate parameter removed
        """
        Export a timeline to a PRG file.
        The internal JSON generated for prg_generator.py will always be 1000Hz based.
        
        Args:
            timeline: Timeline to export.
            file_path (str): Path to save the PRG file.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Create temporary JSON file
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
                temp_json_path = temp_file.name
            
            # Get JSON data
            self.logger.debug(f"Generating internal JSON (1000Hz scale) for PRG export.")
            json_data = timeline.to_json_sequence() # refresh_rate argument removed
            
            # Write JSON to temporary file
            with open(temp_json_path, 'w') as f:
                json.dump(json_data, f, indent=2)
            # --- BEGIN DEBUG LOGGING ---
            try:
                with open(temp_json_path, 'r') as f_read:
                    temp_json_content = f_read.read()
                self.logger.debug(f"Temporary JSON content for PRG export ({os.path.basename(file_path)}):\n{temp_json_content}")
            except Exception as log_e:
                self.logger.error(f"Error reading temporary JSON for logging: {log_e}")
            # --- END DEBUG LOGGING ---
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Call prg_generator.py with absolute path
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            prg_generator_path = os.path.join(root_dir, "prg_generator.py")
            
            self.logger.debug(f"Using prg_generator at: {prg_generator_path}")
            self.logger.debug(f"Calling prg_generator with: python3 {prg_generator_path} {temp_json_path} {file_path}")
            
            
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
    
    def export_project(self, directory): # refresh_rate parameter removed
        """
        Export all timelines in the current project to PRG files.
        The PRG files will be generated based on a 1000Hz intermediate JSON.
        
        Args:
            directory (str): Directory to save the PRG files.
        
        Returns:
            tuple: (success_count, total_count)
        """
        # Check if project is loaded
        if not self.app.project_manager.current_project:
            self.logger.warning("Cannot export project: No project loaded")
            return 0, 0
        
        # Get project
        project = self.app.project_manager.current_project
        
        # refresh_rate is no longer used here as to_json_sequence handles scaling
        # to a fixed 1000Hz for the intermediate JSON.
        
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
            if self.export_timeline(timeline, file_path):
                success_count += 1
        
        self.logger.info(f"Exported {success_count}/{total_count} timelines to {directory}")
        return success_count, total_count
    def export(self, file_path): # refresh_rate parameter removed
        """
        Export the current timeline to a PRG file.
        The PRG will be generated based on a 1000Hz intermediate JSON.
        
        This is a convenience method that exports the first timeline in the current project.
        
        Args:
            file_path (str): Path to save the PRG file.
        
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
        return self.export_timeline(timeline, file_path)
    
    
    def export_project_with_json(self, directory): # refresh_rate parameter removed
        """
        Export all timelines in the current project to both JSON and PRG files.
        PRG files are generated based on a 1000Hz intermediate JSON.
        Separate JSON exports (e.g. for .prg.json) use 100Hz.
        
        Args:
            directory (str): Directory to save the files.
        
        Returns:
            tuple: (json_success_count, prg_success_count, total_count)
        """
        # Check if project is loaded
        if not self.app.project_manager.current_project:
            self.logger.warning("Cannot export project: No project loaded")
            return 0, 0, 0
        
        # Get project
        project = self.app.project_manager.current_project
        
        # The original project's refresh_rate is no longer directly passed
        # to self.export_timeline for PRG generation, as the intermediate
        # JSON is now always 1000Hz based.
        # However, json_exporter might still use its own logic for refresh_rate.
        
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
            if self.export_timeline(timeline, prg_path):
                prg_success_count += 1
        
        self.logger.info(
            f"Exported {json_success_count}/{total_count} JSON files and "
            f"{prg_success_count}/{total_count} PRG files to {directory}"
        )
        
        return json_success_count, prg_success_count, total_count