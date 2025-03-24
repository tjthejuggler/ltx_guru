"""
Sequence Maker - Version History Dialog

This module defines the VersionHistoryDialog class, which provides an interface for browsing and restoring project versions.
"""

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