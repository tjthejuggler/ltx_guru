"""
Sequence Maker - File Handlers

This module defines the FileHandlers class, which contains handlers for file-related
operations such as new, open, save, and export operations.
"""

from PyQt6.QtWidgets import QFileDialog, QMessageBox


class FileHandlers:
    """File operation handlers for the main window."""
    
    def __init__(self, main_window):
        """
        Initialize file handlers.
        
        Args:
            main_window: The main window instance.
        """
        self.main_window = main_window
        self.app = main_window.app
    
    def on_new(self):
        """Create a new project."""
        # Check for unsaved changes
        if not self._check_unsaved_changes():
            return
            
        # Create a new project
        self.app.project_manager.new_project()
        
        # Update UI
        self.main_window._update_ui()
    
    def on_open(self):
        """Open an existing project."""
        # Check for unsaved changes
        if not self._check_unsaved_changes():
            return
            
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Open Project",
            self.app.config.get("general", "default_project_dir"),
            "Sequence Maker Project (*.smproj)"
        )
        
        if file_path:
            # Load project
            self.app.project_manager.load_project(file_path)
            
            # Update UI
            self.main_window._update_ui()
    
    def on_save(self):
        """Save the current project."""
        # Check if project has a file path
        if not self.app.project_manager.current_project.file_path:
            # If not, use save as
            return self.on_save_as()
            
        # Save project
        success = self.app.project_manager.save_project()
        
        # Update UI
        if success:
            self.main_window.statusBar().showMessage("Project saved", 3000)
            
        return success
    
    def on_save_as(self):
        """Save the current project with a new name."""
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save Project As",
            self.app.config.get("general", "default_project_dir"),
            "Sequence Maker Project (*.smproj)"
        )
        
        if file_path:
            # Save project
            success = self.app.project_manager.save_project(file_path)
            
            # Update UI
            if success:
                self.main_window.statusBar().showMessage("Project saved", 3000)
                
            return success
            
        return False
    
    def on_load_audio(self):
        """Load an audio file."""
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Load Audio",
            self.app.config.get("general", "default_project_dir"),
            "Audio Files (*.mp3 *.wav)"
        )
        
        if file_path:
            # Load audio
            self.app.audio_manager.load_audio(file_path)
            
            # Update UI
            self.main_window._update_ui()
    
    def on_export_json(self):
        """Export timeline to JSON format."""
        # Check if project exists
        if not self.app.project_manager.current_project:
            QMessageBox.warning(
                self.main_window,
                "No Project",
                "No project is currently loaded."
            )
            return
        
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Export to JSON",
            self.app.config.get("general", "default_export_dir"),
            "JSON Files (*.json)"
        )
        
        if file_path:
            # Export to JSON
            from export.json_exporter import JSONExporter
            exporter = JSONExporter(self.app)
            success = exporter.export(file_path)
            
            # Update UI
            if success:
                self.main_window.statusBar().showMessage(f"Exported to {file_path}", 3000)
    
    def on_export_prg(self):
        """Export timeline to PRG format."""
        # Check if project exists
        if not self.app.project_manager.current_project:
            QMessageBox.warning(
                self.main_window,
                "No Project",
                "No project is currently loaded."
            )
            return
        
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Export to PRG",
            self.app.config.get("general", "default_export_dir"),
            "PRG Files (*.prg)"
        )
        
        if file_path:
            # Export to PRG
            from export.prg_exporter import PRGExporter
            exporter = PRGExporter(self.app)
            success = exporter.export(file_path)
            
            # Update UI
            if success:
                self.main_window.statusBar().showMessage(f"Exported to {file_path}", 3000)
    
    def on_version_history(self):
        """Show version history dialog."""
        from ui.dialogs.version_history_dialog import VersionHistoryDialog
        dialog = VersionHistoryDialog(self.app, self.main_window)
        dialog.exec()
    
    def _check_unsaved_changes(self):
        """
        Check if there are unsaved changes and prompt the user.
        
        Returns:
            bool: True if it's safe to proceed, False otherwise.
        """
        if not self.app.project_manager.has_unsaved_changes():
            return True
            
        # Show confirmation dialog
        reply = QMessageBox.question(
            self.main_window,
            "Unsaved Changes",
            "There are unsaved changes. Do you want to save them?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )
        
        if reply == QMessageBox.StandardButton.Save:
            # Save changes
            return self.on_save()
        elif reply == QMessageBox.StandardButton.Discard:
            # Discard changes
            return True
        else:
            # Cancel
            return False