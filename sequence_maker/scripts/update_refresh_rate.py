#!/usr/bin/env python3
"""
Sequence Maker - Update Refresh Rate Script

This script updates the refresh rate of the current project to 100 Hz
and re-exports any JSON files with the new refresh rate.

Usage:
    python update_refresh_rate.py [project_file]

If no project file is specified, it will try to load the last opened project.
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path so we can import sequence_maker modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sequence_maker.app.application import Application
from sequence_maker.export.json_exporter import JSONExporter


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def update_refresh_rate(project_file=None):
    """
    Update the refresh rate of a project to 100 Hz.
    
    Args:
        project_file (str, optional): Path to the project file. If None, uses the last opened project.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    # Create application instance (without UI)
    app = Application(headless=True)
    
    # Load project
    if project_file:
        success = app.project_manager.load_project(project_file)
        if not success:
            logging.error(f"Failed to load project: {project_file}")
            return False
    else:
        # Try to load last project
        last_project = app.config.get("general", "last_project")
        if not last_project:
            logging.error("No last project found. Please specify a project file.")
            return False
        
        success = app.project_manager.load_project(last_project)
        if not success:
            logging.error(f"Failed to load last project: {last_project}")
            return False
    
    # Get current project
    project = app.project_manager.current_project
    if not project:
        logging.error("No project loaded.")
        return False
    
    # Update refresh rate
    old_refresh_rate = project.refresh_rate
    project.refresh_rate = 100  # 100 Hz for 1/100th second precision
    
    logging.info(f"Updated refresh rate from {old_refresh_rate} Hz to {project.refresh_rate} Hz")
    
    # Save project
    success = app.project_manager.save_project()
    if not success:
        logging.error("Failed to save project.")
        return False
    
    logging.info(f"Project saved: {project.file_path}")
    
    # Re-export JSON files
    export_dir = os.path.join(os.path.dirname(project.file_path), "json_exports")
    os.makedirs(export_dir, exist_ok=True)
    
    json_exporter = JSONExporter(app)
    success_count, total_count, exported_files = json_exporter.export_project(
        export_dir,
        base_filename=project.name.replace(" ", "_"),
        refresh_rate=100  # Explicitly set refresh rate to 100 Hz
    )
    
    if success_count > 0:
        logging.info(f"Exported {success_count}/{total_count} JSON files to {export_dir}")
        for file_path in exported_files:
            logging.info(f"  - {file_path}")
        return True
    else:
        logging.error("Failed to export JSON files.")
        return False


if __name__ == "__main__":
    setup_logging()
    
    if len(sys.argv) > 1:
        project_file = sys.argv[1]
        update_refresh_rate(project_file)
    else:
        update_refresh_rate()