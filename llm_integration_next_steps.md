# LLM Integration: Detailed Implementation Plan for Remaining Components

This document provides a detailed implementation plan for the remaining components of the LLM integration for Sequence Maker.

## 1. Autosave & Version Control

### 1.1. AutosaveManager Class

Create a new class `AutosaveManager` in `sequence_maker/managers/autosave_manager.py`:

```python
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
```

### 1.2. VersionHistoryDialog Class

Create a new dialog class `VersionHistoryDialog` in `sequence_maker/ui/dialogs/version_history_dialog.py`:

```python
import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

class VersionHistoryDialog(QDialog):
    """Dialog for browsing and restoring project versions."""
    
    version_selected = pyqtSignal(str)
    
    def __init__(self, app, parent=None):
        """
        Initialize the version history dialog.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.VersionHistoryDialog")
        self.app = app
        
        # Set dialog properties
        self.setWindowTitle("Version History")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        # Create UI
        self._create_ui()
        
        # Load versions
        self._load_versions()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create header
        self.header_label = QLabel("Project Version History")
        self.header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.main_layout.addWidget(self.header_label)
        
        # Create description
        self.description_label = QLabel(
            "Select a version to restore. A backup of the current state will be created before restoring."
        )
        self.main_layout.addWidget(self.description_label)
        
        # Create version list
        self.version_list = QListWidget()
        self.version_list.setAlternatingRowColors(True)
        self.version_list.itemDoubleClicked.connect(self._on_version_double_clicked)
        self.main_layout.addWidget(self.version_list)
        
        # Create button layout
        self.button_layout = QHBoxLayout()
        
        # Create restore button
        self.restore_button = QPushButton("Restore Selected Version")
        self.restore_button.clicked.connect(self._on_restore_clicked)
        self.button_layout.addWidget(self.restore_button)
        
        # Create refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._load_versions)
        self.button_layout.addWidget(self.refresh_button)
        
        # Create close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.close_button)
        
        self.main_layout.addLayout(self.button_layout)
    
    def _load_versions(self):
        """Load available versions."""
        # Clear list
        self.version_list.clear()
        
        # Get versions
        versions = self.app.autosave_manager.get_versions()
        
        # Add versions to list
        for version in versions:
            # Create item
            item = QListWidgetItem()
            
            # Format timestamp
            timestamp = version.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                    timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            # Set text
            item.setText(f"{timestamp} - {version.get('reason', 'Unknown')}")
            
            # Store file path
            item.setData(Qt.ItemDataRole.UserRole, version.get("file_path", ""))
            
            # Add to list
            self.version_list.addItem(item)
    
    def _on_version_double_clicked(self, item):
        """
        Handle version double click.
        
        Args:
            item: The clicked item.
        """
        # Get version path
        version_path = item.data(Qt.ItemDataRole.UserRole)
        
        # Confirm restore
        result = QMessageBox.question(
            self,
            "Restore Version",
            "Are you sure you want to restore this version? A backup of the current state will be created.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Restore version
            self._restore_version(version_path)
    
    def _on_restore_clicked(self):
        """Handle Restore button click."""
        # Get selected item
        selected_items = self.version_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self,
                "No Version Selected",
                "Please select a version to restore."
            )
            return
        
        # Get version path
        version_path = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # Confirm restore
        result = QMessageBox.question(
            self,
            "Restore Version",
            "Are you sure you want to restore this version? A backup of the current state will be created.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Restore version
            self._restore_version(version_path)
    
    def _restore_version(self, version_path):
        """
        Restore a version.
        
        Args:
            version_path (str): Path to the version file.
        """
        # Restore version
        success = self.app.autosave_manager.restore_version(version_path)
        
        if success:
            QMessageBox.information(
                self,
                "Version Restored",
                "The selected version has been restored successfully."
            )
            
            # Close dialog
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Restore Failed",
                "Failed to restore the selected version."
            )
```

## 2. Implementation Order and Timeline

### 2.1. Phase 1: Autosave & Version Control (COMPLETED)
1. ✅ Created `AutosaveManager` class
2. ✅ Created `VersionHistoryDialog` class
3. ✅ Integrated with `LLMManager` and `MainWindow`
4. ✅ Added tests for version creation and restoration

### 2.2. Phase 2: Enhanced Error Handling (COMPLETED)
1. ✅ Updated `LLMManager` with ambiguity handling
2. ✅ Created `AmbiguityResolutionDialog` class
3. ✅ Integrated with `LLMChatDialog`
4. ✅ Added tests for ambiguity detection and resolution

### 2.3. Phase 3: Audio Analysis Integration (NEXT PRIORITY)
1. Update `AudioManager` with analysis methods
2. Update `AppContextAPI` to include analysis data
3. Test audio analysis and data extraction
4. Integrate with LLM system messages

### 2.4. Phase 4: Floating Chat Window (1-2 days)
1. Create `LLMChatWindow` class
2. Update `MainWindow` to use floating window
3. Test window functionality

## 3. Next Implementation: Audio Analysis Integration

The next phase to implement is Audio Analysis Integration. This will involve:

1. Updating the `AudioManager` class with methods to analyze audio files
2. Extracting musical features such as beats, tempo, rhythm, and intensity
3. Making this data available to the LLM via the `AppContextAPI`
4. Enhancing the system messages to include audio analysis data

This implementation will improve the LLM's ability to generate color sequences that match the music by providing detailed information about the audio's musical characteristics.

### 3.1. AudioManager Enhancement

The `AudioManager` class will be enhanced with methods to analyze audio files using the librosa library:

```python
def analyze_audio(self):
    """Analyze audio file to extract musical features."""
    if not self.audio_file:
        return
        
    try:
        import librosa
        
        # Load audio file
        y, sr = librosa.load(self.audio_file)
        
        # Extract tempo
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        self.tempo = tempo
        
        # Extract beat times
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        self.beat_times = beat_times
        
        # Extract onset strength
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        self.onset_strength = onset_env
        
        # Extract spectral contrast
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        self.spectral_contrast = contrast
        
        # Emit signal
        self.audio_analyzed.emit()
        
    except Exception as e:
        self.logger.error(f"Error analyzing audio: {e}")
```

### 3.2. AppContextAPI Enhancement

The `AppContextAPI` class will be updated to include the audio analysis data:

```python
def get_audio_context(self):
    """
    Get audio context data.
    
    Returns:
        dict: Audio context data.
    """
    context = {}
    
    if self.app.audio_manager.audio_file:
        context["file"] = os.path.basename(self.app.audio_manager.audio_file)
        context["duration"] = self.app.audio_manager.duration
        context["tempo"] = self.app.audio_manager.tempo
        
        # Add beat times
        if self.app.audio_manager.beat_times is not None:
            context["beat_times"] = self.app.audio_manager.beat_times.tolist()
        
        # Add onset strength
        if hasattr(self.app.audio_manager, "onset_strength"):
            context["onset_strength"] = self.app.audio_manager.onset_strength.tolist()
        
        # Add spectral contrast
        if hasattr(self.app.audio_manager, "spectral_contrast"):
            context["spectral_contrast"] = self.app.audio_manager.spectral_contrast.tolist()
    
    return context
```

### 3.3. System Message Enhancement

The system message in `LLMChatDialog` will be enhanced to include the audio analysis data:

```python
# Add detailed audio analysis information
if self.app.audio_manager.audio_file:
    system_message += f"\n\nAudio file: {os.path.basename(self.app.audio_manager.audio_file)}"
    system_message += f"\nAudio duration: {self.app.audio_manager.duration} seconds"
    system_message += f"\nTempo: {self.app.audio_manager.tempo} BPM"
    
    # Add information about beats if available
    if self.app.audio_manager.beat_times is not None:
        beat_count = len(self.app.audio_manager.beat_times)
        system_message += f"\nDetected beats: {beat_count}"
        
        # Add some beat times as examples
        if beat_count > 0:
            system_message += "\nBeat times (seconds): "
            beat_times = self.app.audio_manager.beat_times[:10]  # First 10 beats
            system_message += ", ".join(f"{time:.2f}" for time in beat_times)
            if beat_count > 10:
                system_message += f", ... (and {beat_count - 10} more)"
    
    # Add information about onset strength if available
    if hasattr(self.app.audio_manager, "onset_strength"):
        system_message += "\nOnset strength analysis is available"
    
    # Add information about spectral contrast if available
    if hasattr(self.app.audio_manager, "spectral_contrast"):
        system_message += "\nSpectral contrast analysis is available"
```
