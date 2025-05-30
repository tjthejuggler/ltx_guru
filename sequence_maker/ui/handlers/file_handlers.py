"""
Sequence Maker - File Handlers

This module defines the FileHandlers class, which contains handlers for file-related
operations such as new, open, save, and export operations.
"""

import os
import json
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QColorDialog
from models.timeline import Timeline
from models.segment import TimelineSegment
from utils.file_type_utils import is_valid_ball_sequence, is_valid_seqdesign, is_valid_lyrics_timestamps


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
        
        # Show directory selection dialog
        export_dir = QFileDialog.getExistingDirectory(
            self.main_window,
            "Select Directory for JSON Export",
            self.app.config.get("general", "default_export_dir"),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not export_dir:
            return  # User cancelled
        
        # Get a base filename (optional)
        base_filename, ok = QFileDialog.getSaveFileName(
            self.main_window,
            "Enter Base Filename (Optional)",
            os.path.join(export_dir, "export"),
            "JSON Files (*.json)",
            options=QFileDialog.Option.DontConfirmOverwrite
        )
        
        if not ok and not base_filename:
            # User cancelled or didn't provide a filename
            # We'll still proceed with export using default naming
            base_filename = None
        
        # Export to JSON
        from export.json_exporter import JSONExporter
        exporter = JSONExporter(self.app)
        success_count, total_count, exported_files = exporter.export_project(
            export_dir,
            os.path.basename(base_filename) if base_filename else None
        )
        
        # Update UI
        if success_count > 0:
            self.main_window.statusBar().showMessage(
                f"Exported {success_count}/{total_count} JSON files to {export_dir}",
                3000
            )
            
            # Ask if user wants to open the export directory
            reply = QMessageBox.question(
                self.main_window,
                "Export Complete",
                f"JSON files exported to {export_dir}. Would you like to open this directory?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Open the directory with the default file manager
                import subprocess
                import platform
                
                if platform.system() == 'Windows':
                    os.startfile(export_dir)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(('open', export_dir))
                else:  # Linux
                    subprocess.call(('xdg-open', export_dir))
    
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
            
    def on_import_ball_sequence(self):
        """Import a ball sequence file."""
        self.app.logger.info("Starting ball sequence import")
        
        # Check if there are any existing timelines
        existing_timelines = self.app.timeline_manager.get_timelines()
        self.app.logger.debug(f"Found {len(existing_timelines)} existing timelines")
        
        # If there are existing timelines, ask if the user wants to import into an existing timeline
        import_to_existing = False
        selected_timeline = None
        
        if existing_timelines:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout
            
            dialog = QDialog(self.main_window)
            dialog.setWindowTitle("Import Ball Sequence")
            layout = QVBoxLayout(dialog)
            
            # Add label
            layout.addWidget(QLabel("How would you like to import the ball sequence?"))
            
            # Add radio buttons
            import_option = QComboBox()
            import_option.addItem("Create a new timeline")
            import_option.addItem("Import into an existing timeline")
            layout.addWidget(import_option)
            
            # Add timeline selection combo box (initially hidden)
            timeline_selection_label = QLabel("Select timeline:")
            timeline_selection = QComboBox()
            for i, timeline in enumerate(existing_timelines):
                timeline_selection.addItem(f"{i+1}: {timeline.name}")
            
            timeline_selection_label.setVisible(False)
            timeline_selection.setVisible(False)
            layout.addWidget(timeline_selection_label)
            layout.addWidget(timeline_selection)
            
            # Add buttons
            button_layout = QHBoxLayout()
            ok_button = QPushButton("OK")
            cancel_button = QPushButton("Cancel")
            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)
            
            # Connect signals
            import_option.currentIndexChanged.connect(
                lambda index: (timeline_selection_label.setVisible(index == 1),
                              timeline_selection.setVisible(index == 1))
            )
            ok_button.clicked.connect(dialog.accept)
            cancel_button.clicked.connect(dialog.reject)
            
            # Show dialog
            if dialog.exec():
                import_to_existing = import_option.currentIndex() == 1
                if import_to_existing:
                    selected_timeline = existing_timelines[timeline_selection.currentIndex()]
        
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Import Ball Sequence",
            self.app.config.get("general", "default_project_dir"),
            "Ball Sequence Files (*.ball.json)"
        )
        
        if file_path:
            # Load ball sequence
            try:
                self.app.logger.info(f"Loading ball sequence from {file_path}")
                with open(file_path, 'r') as f:
                    ball_data = json.load(f)
                
                self.app.logger.debug(f"Ball data loaded: {len(ball_data.get('segments', []))} segments found")
                
                if import_to_existing and selected_timeline:
                    # Import into existing timeline
                    self.app.logger.info(f"Importing ball sequence into existing timeline: {selected_timeline.name}")
                    
                    # Clear existing segments from the timeline before importing
                    selected_timeline.clear()
                    self.app.logger.info(f"Cleared existing segments from timeline: {selected_timeline.name}")
                    
                    # Add segments to timeline
                    for segment in ball_data.get("segments", []):
                        timeline_segment = TimelineSegment(
                            start_time=segment["start_time"],
                            end_time=segment["end_time"],
                            color=tuple(segment["color"]),
                            pixels=segment["pixels"]
                        )
                        selected_timeline.add_segment(timeline_segment)
                    
                    # Update project total_duration to accommodate the imported sequence
                    timeline_duration = selected_timeline.get_duration()
                    old_project_duration = self.app.project_manager.current_project.total_duration
                    if timeline_duration > old_project_duration:
                        self.app.project_manager.current_project.total_duration = timeline_duration
                        self.app.logger.info(f"Updated project total_duration from {old_project_duration}s to {timeline_duration}s after ball sequence import into existing timeline")
                        
                        # Trigger timeline container size update
                        if hasattr(self.main_window, 'timeline_widget'):
                            self.main_window.timeline_widget.timeline_container.update_size()
                            self.app.logger.info("Triggered timeline container size update after ball sequence import into existing timeline")
                    
                    # Emit signal to update UI
                    self.app.logger.debug(f"Emitting timeline_modified signal for timeline: {selected_timeline.name}")
                    self.app.timeline_manager.timeline_modified.emit(selected_timeline)
                    
                    # Update UI
                    self.main_window._update_ui()
                    self.main_window.statusBar().showMessage(
                        f"Imported ball sequence from {file_path} into {selected_timeline.name}", 3000)
                else:
                    # Create a new timeline
                    self.app.logger.info("Creating new timeline for ball sequence import")
                    
                    timeline = Timeline(
                        name=ball_data.get("metadata", {}).get("name", "Imported Ball"),
                        default_pixels=ball_data.get("metadata", {}).get("default_pixels", 4)
                    )
                    
                    # Add segments to timeline
                    for segment in ball_data.get("segments", []):
                        timeline_segment = TimelineSegment(
                            start_time=segment["start_time"],
                            end_time=segment["end_time"],
                            color=tuple(segment["color"]),
                            pixels=segment["pixels"]
                        )
                        timeline.add_segment(timeline_segment)
                    
                    # Add timeline to project
                    self.app.project_manager.current_project.add_timeline(timeline)
                    
                    # Update project total_duration to accommodate the imported sequence
                    timeline_duration = timeline.get_duration()
                    old_project_duration = self.app.project_manager.current_project.total_duration
                    if timeline_duration > old_project_duration:
                        self.app.project_manager.current_project.total_duration = timeline_duration
                        self.app.logger.info(f"Updated project total_duration from {old_project_duration}s to {timeline_duration}s after ball sequence import")
                        
                        # Trigger timeline container size update
                        if hasattr(self.main_window, 'timeline_widget'):
                            self.main_window.timeline_widget.timeline_container.update_size()
                            self.app.logger.info("Triggered timeline container size update after ball sequence import")
                    
                    # Update UI
                    self.app.logger.info("Updating UI after ball sequence import")
                    self.main_window._update_ui()
                    self.main_window.statusBar().showMessage(f"Imported ball sequence from {file_path}", 3000)
            except Exception as e:
                self.app.logger.error(f"Error importing ball sequence: {str(e)}", exc_info=True)
                QMessageBox.warning(
                    self.main_window,
                    "Import Error",
                    f"Failed to import ball sequence: {str(e)}"
                )
    
    def on_export_ball_sequence(self):
        """Export timeline to ball sequence format."""
        # Check if project exists
        if not self.app.project_manager.current_project:
            QMessageBox.warning(
                self.main_window,
                "No Project",
                "No project is currently loaded."
            )
            return
        
        # Get selected timeline
        timeline = self.main_window.timeline_widget.get_selected_timeline()
        if not timeline:
            QMessageBox.warning(
                self.main_window,
                "No Timeline Selected",
                "Please select a timeline to export."
            )
            return
        
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Export to Ball Sequence",
            self.app.config.get("general", "default_export_dir"),
            "Ball Sequence Files (*.ball.json)"
        )
        
        if file_path:
            # Ensure file has .ball.json extension
            if not file_path.endswith(".ball.json"):
                file_path += ".ball.json"
            
            # Create ball sequence data
            ball_data = {
                "metadata": {
                    "name": timeline.name,
                    "default_pixels": timeline.default_pixels,
                    "refresh_rate": 50,
                    "total_duration": timeline.get_duration(),
                    "audio_file": self.app.audio_manager.get_audio_file_path() or ""
                },
                "segments": []
            }
            
            # Add segments
            for segment in timeline.segments:
                ball_data["segments"].append({
                    "start_time": segment.start_time,
                    "end_time": segment.end_time,
                    "color": list(segment.color),
                    "pixels": segment.pixels
                })
            
            # Write to file
            try:
                with open(file_path, 'w') as f:
                    json.dump(ball_data, f, indent=2)
                
                self.main_window.statusBar().showMessage(f"Exported to {file_path}", 3000)
            except Exception as e:
                QMessageBox.warning(
                    self.main_window,
                    "Export Error",
                    f"Failed to export ball sequence: {str(e)}"
                )
    
    def on_import_lyrics_timestamps(self):
        """Import lyrics timestamps and convert to a timeline."""
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Import Lyrics Timestamps",
            self.app.config.get("general", "default_project_dir"),
            "Lyrics Timestamps Files (*.lyrics.json *.json)"
        )
        
        if file_path:
            # Check if file is valid
            if not is_valid_lyrics_timestamps(file_path):
                QMessageBox.warning(
                    self.main_window,
                    "Import Error",
                    f"Invalid lyrics timestamps file: {file_path}"
                )
                return
            
            # Ask for color preferences
            color_dialog = QColorDialog(self.main_window)
            color_dialog.setWindowTitle("Select Color for Words")
            if color_dialog.exec():
                word_color = color_dialog.selectedColor().getRgb()[:3]  # Get RGB values
            else:
                word_color = [0, 0, 255]  # Default blue
            
            background_color = [0, 0, 0]  # Default black
            
            # Load lyrics timestamps
            try:
                with open(file_path, 'r') as f:
                    lyrics_data = json.load(f)
                
                # Extract metadata
                song_title = lyrics_data.get("song_title", "Unknown")
                artist_name = lyrics_data.get("artist_name", "Unknown")
                word_timestamps = lyrics_data.get("word_timestamps", [])
                
                # Create a new timeline
                timeline = Timeline(
                    name=f"{song_title} - {artist_name} - Word Flash",
                    default_pixels=4
                )
                
                # Find total duration
                total_duration = 0
                if word_timestamps:
                    total_duration = max(word["end"] for word in word_timestamps) + 5.0  # Add 5 seconds buffer
                
                # Add initial black segment if first word doesn't start at 0
                if word_timestamps and word_timestamps[0]["start"] > 0:
                    timeline.add_segment(TimelineSegment(
                        start_time=0.0,
                        end_time=word_timestamps[0]["start"],
                        color=tuple(background_color),
                        pixels=4
                    ))
                
                # Add segments for each word and gap
                for i, word in enumerate(word_timestamps):
                    # Add segment for the word
                    timeline.add_segment(TimelineSegment(
                        start_time=word["start"],
                        end_time=word["end"],
                        color=tuple(word_color),
                        pixels=4
                    ))
                    
                    # Add segment for the gap after this word (if not the last word)
                    if i < len(word_timestamps) - 1:
                        next_word = word_timestamps[i + 1]
                        if word["end"] < next_word["start"]:
                            timeline.add_segment(TimelineSegment(
                                start_time=word["end"],
                                end_time=next_word["start"],
                                color=tuple(background_color),
                                pixels=4
                            ))
                
                # Add final black segment after the last word
                if word_timestamps:
                    timeline.add_segment(TimelineSegment(
                        start_time=word_timestamps[-1]["end"],
                        end_time=total_duration,
                        color=tuple(background_color),
                        pixels=4
                    ))
                
                # Add timeline to project
                self.app.project_manager.current_project.add_timeline(timeline)
                
                # Update project total_duration to accommodate the imported lyrics timeline
                timeline_duration = timeline.get_duration()
                old_project_duration = self.app.project_manager.current_project.total_duration
                if timeline_duration > old_project_duration:
                    self.app.project_manager.current_project.total_duration = timeline_duration
                    self.app.logger.info(f"Updated project total_duration from {old_project_duration}s to {timeline_duration}s after lyrics import")
                    
                    # Trigger timeline container size update
                    if hasattr(self.main_window, 'timeline_widget'):
                        self.main_window.timeline_widget.timeline_container.update_size()
                        self.app.logger.info("Triggered timeline container size update after lyrics import")
                
                # Update UI
                self.main_window._update_ui()
                self.main_window.statusBar().showMessage(f"Imported lyrics timestamps from {file_path}", 3000)
            except Exception as e:
                QMessageBox.warning(
                    self.main_window,
                    "Import Error",
                    f"Failed to import lyrics timestamps: {str(e)}"
                )