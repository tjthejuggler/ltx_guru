"""
Sequence Maker - Crop Audio Dialog

This module defines the CropAudioDialog class, which provides an interface for cropping audio files.
"""

import os
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QMessageBox, QFormLayout
)
from PyQt6.QtCore import Qt
from pydub import AudioSegment

class CropAudioDialog(QDialog):
    """Dialog for cropping audio files."""
    
    def __init__(self, app, parent=None):
        """
        Initialize the crop audio dialog.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.CropAudioDialog")
        self.app = app
        
        # Set dialog properties
        self.setWindowTitle("Crop Audio")
        self.setMinimumWidth(400)
        
        # Create UI
        self._create_ui()
        
        # Load previous values
        self._load_previous_values()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create form layout for inputs
        self.form_layout = QFormLayout()
        
        # Create milliseconds input
        self.ms_input = QLineEdit()
        self.ms_input.setPlaceholderText("Enter milliseconds to crop from start")
        self.form_layout.addRow("Milliseconds to crop:", self.ms_input)
        
        # Add form layout to main layout
        self.main_layout.addLayout(self.form_layout)
        
        # Create output file section
        self.output_layout = QHBoxLayout()
        
        # Create output file label
        self.output_label = QLabel("Output file:")
        self.output_layout.addWidget(self.output_label)
        
        # Create output file path input
        self.output_path_input = QLineEdit()
        self.output_path_input.setReadOnly(True)
        self.output_layout.addWidget(self.output_path_input)
        
        # Create browse button
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._on_browse_clicked)
        self.output_layout.addWidget(self.browse_button)
        
        # Add output layout to main layout
        self.main_layout.addLayout(self.output_layout)
        
        # Create button layout
        self.button_layout = QHBoxLayout()
        
        # Create crop button
        self.crop_button = QPushButton("Crop")
        self.crop_button.clicked.connect(self._on_crop_clicked)
        self.button_layout.addWidget(self.crop_button)
        
        # Create cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)
        
        # Add button layout to main layout
        self.main_layout.addLayout(self.button_layout)
    
    def _load_previous_values(self):
        """Load previous values from config."""
        # Get previous milliseconds value
        ms_value = self.app.config.get("audio", "crop_ms")
        if ms_value is not None:
            self.ms_input.setText(str(ms_value))
        else:
            # Default to 1000 ms (1 second)
            self.ms_input.setText("1000")
        
        # Update output path based on current audio file
        self._update_output_path()
    
    def _update_output_path(self):
        """Update the output path based on the current audio file and ms value."""
        # Get current audio file
        audio_file = self.app.audio_manager.audio_file
        
        if not audio_file:
            self.output_path_input.setText("")
            return
        
        # Get ms value
        try:
            ms_value = int(self.ms_input.text())
        except ValueError:
            ms_value = 1000  # Default to 1000 ms
        
        # Get directory and filename
        directory = os.path.dirname(audio_file)
        filename = os.path.basename(audio_file)
        
        # Get last save directory from config
        last_save_dir = self.app.config.get("audio", "last_save_dir")
        if last_save_dir and os.path.isdir(last_save_dir):
            directory = last_save_dir
        
        # Create new filename
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}_cropped_{ms_value}ms{ext}"
        
        # Set output path
        output_path = os.path.join(directory, new_filename)
        self.output_path_input.setText(output_path)
    
    def _on_browse_clicked(self):
        """Handle Browse button click."""
        # Get current output path
        current_path = self.output_path_input.text()
        
        # Get directory and filename
        directory = os.path.dirname(current_path) if current_path else ""
        filename = os.path.basename(current_path) if current_path else ""
        
        # Show file dialog
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Cropped Audio",
            os.path.join(directory, filename),
            "Audio Files (*.mp3 *.wav);;All Files (*)"
        )
        
        if output_path:
            # Save directory to config
            self.app.config.set("audio", "last_save_dir", os.path.dirname(output_path))
            
            # Set output path
            self.output_path_input.setText(output_path)
    
    def _on_crop_clicked(self):
        """Handle Crop button click."""
        # Get input values
        try:
            ms_value = int(self.ms_input.text())
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter a valid number of milliseconds."
            )
            return
        
        # Save ms value to config
        self.app.config.set("audio", "crop_ms", ms_value)
        
        # Get output path
        output_path = self.output_path_input.text()
        
        if not output_path:
            QMessageBox.warning(
                self,
                "No Output Path",
                "Please specify an output path for the cropped audio."
            )
            return
        
        # Get current audio file
        audio_file = self.app.audio_manager.audio_file
        
        if not audio_file:
            QMessageBox.warning(
                self,
                "No Audio Loaded",
                "Please load an audio file before cropping."
            )
            return
        
        # Crop audio
        try:
            # Load the audio file
            audio = AudioSegment.from_file(audio_file)
            
            # Crop the audio
            cropped_audio = audio[ms_value:]
            
            # Get format from file extension
            file_ext = os.path.splitext(output_path)[1][1:].lower()
            # Default to mp3 if no extension or unrecognized extension
            if not file_ext or file_ext not in ['mp3', 'wav', 'ogg', 'flac']:
                file_ext = 'mp3'
                
            # Export the cropped audio
            cropped_audio.export(output_path, format=file_ext)
            
            QMessageBox.information(
                self,
                "Crop Successful",
                f"Successfully cropped {ms_value} milliseconds from the audio.\nSaved as: {output_path}"
            )
            
            # Close dialog
            self.accept()
        except Exception as e:
            self.logger.error(f"Error cropping audio: {e}")
            QMessageBox.critical(
                self,
                "Crop Failed",
                f"Failed to crop audio: {str(e)}"
            )
    
    def showEvent(self, event):
        """Handle dialog show event."""
        super().showEvent(event)
        
        # Update output path when dialog is shown
        self._update_output_path()
        
        # Connect ms_input text changed signal
        self.ms_input.textChanged.connect(self._update_output_path)