"""
Sequence Maker - Key Mapping Dialog

This module defines the KeyMappingDialog class, which allows users to configure keyboard mappings.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFormLayout, QComboBox,
    QDialogButtonBox, QGroupBox, QCheckBox, QMessageBox,
    QColorDialog, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QColor, QKeySequence

from models.key_mapping import KeyMapping


class KeyMappingDialog(QDialog):
    """Dialog for configuring keyboard mappings."""
    
    def __init__(self, app, parent=None):
        """
        Initialize the key mapping dialog.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.KeyMappingDialog")
        self.app = app
        
        # Set dialog properties
        self.setWindowTitle("Key Mapping")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        # Key mapping properties
        self.mappings = {}
        self.current_mapping = None
        self.recording_key = False
        
        # Create UI
        self._create_ui()
        
        # Load mappings
        self._load_mappings()
        
        # Install event filter for key recording
        self.installEventFilter(self)
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create mapping selection layout
        self.mapping_selection_layout = QHBoxLayout()
        self.main_layout.addLayout(self.mapping_selection_layout)
        
        # Create mapping list
        self.mapping_list = QListWidget()
        self.mapping_list.setMinimumWidth(150)
        self.mapping_list.currentItemChanged.connect(self._on_mapping_selected)
        self.mapping_selection_layout.addWidget(self.mapping_list)
        
        # Create mapping buttons
        self.mapping_buttons_layout = QVBoxLayout()
        self.mapping_selection_layout.addLayout(self.mapping_buttons_layout)
        
        self.new_mapping_button = QPushButton("New Mapping")
        self.new_mapping_button.clicked.connect(self._on_new_mapping)
        self.mapping_buttons_layout.addWidget(self.new_mapping_button)
        
        self.rename_mapping_button = QPushButton("Rename")
        self.rename_mapping_button.clicked.connect(self._on_rename_mapping)
        self.mapping_buttons_layout.addWidget(self.rename_mapping_button)
        
        self.duplicate_mapping_button = QPushButton("Duplicate")
        self.duplicate_mapping_button.clicked.connect(self._on_duplicate_mapping)
        self.mapping_buttons_layout.addWidget(self.duplicate_mapping_button)
        
        self.delete_mapping_button = QPushButton("Delete")
        self.delete_mapping_button.clicked.connect(self._on_delete_mapping)
        self.mapping_buttons_layout.addWidget(self.delete_mapping_button)
        
        self.mapping_buttons_layout.addStretch()
        
        # Create mapping editor
        self.mapping_editor = QGroupBox("Mapping Editor")
        self.main_layout.addWidget(self.mapping_editor)
        
        self.mapping_editor_layout = QVBoxLayout(self.mapping_editor)
        
        # Create key table
        self.key_table = QTableWidget()
        self.key_table.setColumnCount(4)
        self.key_table.setHorizontalHeaderLabels(["Key", "Color", "Timelines", "Actions"])
        self.key_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.key_table.verticalHeader().setVisible(False)
        self.mapping_editor_layout.addWidget(self.key_table)
        
        # Create key editor buttons
        self.key_editor_buttons_layout = QHBoxLayout()
        self.mapping_editor_layout.addLayout(self.key_editor_buttons_layout)
        
        self.add_key_button = QPushButton("Add Key")
        self.add_key_button.clicked.connect(self._on_add_key)
        self.key_editor_buttons_layout.addWidget(self.add_key_button)
        
        self.edit_key_button = QPushButton("Edit Key")
        self.edit_key_button.clicked.connect(self._on_edit_key)
        self.key_editor_buttons_layout.addWidget(self.edit_key_button)
        
        self.remove_key_button = QPushButton("Remove Key")
        self.remove_key_button.clicked.connect(self._on_remove_key)
        self.key_editor_buttons_layout.addWidget(self.remove_key_button)
        
        # Create effect modifiers group
        self.effect_modifiers_group = QGroupBox("Effect Modifiers")
        self.mapping_editor_layout.addWidget(self.effect_modifiers_group)
        
        self.effect_modifiers_layout = QFormLayout(self.effect_modifiers_group)
        
        self.shift_effect_combo = QComboBox()
        self.shift_effect_combo.addItems(["None", "Strobe", "Fade", "Pulse", "Rainbow"])
        self.effect_modifiers_layout.addRow("Shift:", self.shift_effect_combo)
        
        self.ctrl_effect_combo = QComboBox()
        self.ctrl_effect_combo.addItems(["None", "Strobe", "Fade", "Pulse", "Rainbow"])
        self.effect_modifiers_layout.addRow("Ctrl:", self.ctrl_effect_combo)
        
        self.alt_effect_combo = QComboBox()
        self.alt_effect_combo.addItems(["None", "Strobe", "Fade", "Pulse", "Rainbow"])
        self.effect_modifiers_layout.addRow("Alt:", self.alt_effect_combo)
        
        # Create button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)
    
    def _load_mappings(self):
        """Load key mappings from the application configuration."""
        # Get mappings from config
        config_mappings = self.app.config.get("key_mappings", "mappings")
        
        # Create key mappings
        for name, mapping_data in config_mappings.items():
            # Create mapping
            mapping = KeyMapping(name=name)
            
            # Add to mappings
            self.mappings[name] = mapping
            
            # Add to list
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.mapping_list.addItem(item)
        
        # If no mappings, create default
        if not self.mappings:
            # Create default mapping
            mapping = KeyMapping.create_default()
            
            # Add to mappings
            self.mappings[mapping.name] = mapping
            
            # Add to list
            item = QListWidgetItem(mapping.name)
            item.setData(Qt.ItemDataRole.UserRole, mapping.name)
            self.mapping_list.addItem(item)
        
        # Select first mapping
        self.mapping_list.setCurrentRow(0)
    
    def _save_mappings(self):
        """Save key mappings to the application configuration."""
        # Create mappings dict for config
        config_mappings = {}
        
        # Add each mapping
        for name, mapping in self.mappings.items():
            # Add to config mappings
            config_mappings[name] = mapping.to_dict()
        
        # Save to config
        self.app.config.set("key_mappings", "mappings", config_mappings)
        
        # Save default mapping
        default_mapping = self.app.config.get("key_mappings", "default_mapping")
        if default_mapping not in self.mappings:
            # Set first mapping as default
            if self.mappings:
                default_mapping = next(iter(self.mappings.keys()))
            else:
                default_mapping = ""
            
            # Save to config
            self.app.config.set("key_mappings", "default_mapping", default_mapping)
        
        # Save config
        self.app.config.save()
    
    def _update_key_table(self):
        """Update the key table with the current mapping."""
        # Clear table
        self.key_table.setRowCount(0)
        
        # Check if mapping is selected
        if not self.current_mapping:
            return
        
        # Add each key mapping
        for key, mapping in self.current_mapping.mappings.items():
            # Add row
            row = self.key_table.rowCount()
            self.key_table.insertRow(row)
            
            # Add key
            key_item = QTableWidgetItem(key)
            self.key_table.setItem(row, 0, key_item)
            
            # Add color
            color = mapping["color"]
            color_item = QTableWidgetItem()
            color_item.setBackground(QColor(*color))
            self.key_table.setItem(row, 1, color_item)
            
            # Add timelines
            timelines = mapping["timelines"]
            timelines_item = QTableWidgetItem(", ".join(str(t + 1) for t in timelines))
            self.key_table.setItem(row, 2, timelines_item)
            
            # Add actions
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_button = QPushButton("Edit")
            edit_button.setProperty("key", key)
            edit_button.clicked.connect(self._on_edit_key_row)
            actions_layout.addWidget(edit_button)
            
            remove_button = QPushButton("Remove")
            remove_button.setProperty("key", key)
            remove_button.clicked.connect(self._on_remove_key_row)
            actions_layout.addWidget(remove_button)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.key_table.setCellWidget(row, 3, actions_widget)
        
        # Update effect modifiers
        self._update_effect_modifiers()
    
    def _update_effect_modifiers(self):
        """Update the effect modifier combos with the current mapping."""
        # Check if mapping is selected
        if not self.current_mapping:
            return
        
        # Update shift effect
        shift_effect = self.current_mapping.effect_modifiers.get("shift", "")
        if shift_effect:
            self.shift_effect_combo.setCurrentText(shift_effect.capitalize())
        else:
            self.shift_effect_combo.setCurrentText("None")
        
        # Update ctrl effect
        ctrl_effect = self.current_mapping.effect_modifiers.get("ctrl", "")
        if ctrl_effect:
            self.ctrl_effect_combo.setCurrentText(ctrl_effect.capitalize())
        else:
            self.ctrl_effect_combo.setCurrentText("None")
        
        # Update alt effect
        alt_effect = self.current_mapping.effect_modifiers.get("alt", "")
        if alt_effect:
            self.alt_effect_combo.setCurrentText(alt_effect.capitalize())
        else:
            self.alt_effect_combo.setCurrentText("None")
    
    def _on_mapping_selected(self, current, previous):
        """
        Handle mapping selection changed.
        
        Args:
            current: Current item.
            previous: Previous item.
        """
        # Check if item is selected
        if not current:
            self.current_mapping = None
            return
        
        # Get mapping name
        name = current.data(Qt.ItemDataRole.UserRole)
        
        # Get mapping
        self.current_mapping = self.mappings.get(name)
        
        # Update key table
        self._update_key_table()
    
    def _on_new_mapping(self):
        """Handle New Mapping button click."""
        # Show input dialog
        from PyQt6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(
            self,
            "New Mapping",
            "Enter mapping name:"
        )
        
        if ok and name:
            # Check if name already exists
            if name in self.mappings:
                QMessageBox.warning(
                    self,
                    "Duplicate Name",
                    f"A mapping with the name '{name}' already exists."
                )
                return
            
            # Create new mapping
            mapping = KeyMapping(name=name)
            
            # Add to mappings
            self.mappings[name] = mapping
            
            # Add to list
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.mapping_list.addItem(item)
            
            # Select new mapping
            self.mapping_list.setCurrentItem(item)
    
    def _on_rename_mapping(self):
        """Handle Rename button click."""
        # Check if mapping is selected
        if not self.current_mapping:
            return
        
        # Show input dialog
        from PyQt6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(
            self,
            "Rename Mapping",
            "Enter new name:",
            text=self.current_mapping.name
        )
        
        if ok and name:
            # Check if name already exists
            if name in self.mappings and name != self.current_mapping.name:
                QMessageBox.warning(
                    self,
                    "Duplicate Name",
                    f"A mapping with the name '{name}' already exists."
                )
                return
            
            # Get current name
            current_name = self.current_mapping.name
            
            # Update mapping name
            self.current_mapping.name = name
            
            # Update mappings dict
            self.mappings.pop(current_name)
            self.mappings[name] = self.current_mapping
            
            # Update list item
            item = self.mapping_list.currentItem()
            item.setText(name)
            item.setData(Qt.ItemDataRole.UserRole, name)
    
    def _on_duplicate_mapping(self):
        """Handle Duplicate button click."""
        # Check if mapping is selected
        if not self.current_mapping:
            return
        
        # Create copy of mapping
        mapping = self.current_mapping.copy()
        
        # Add to mappings
        self.mappings[mapping.name] = mapping
        
        # Add to list
        item = QListWidgetItem(mapping.name)
        item.setData(Qt.ItemDataRole.UserRole, mapping.name)
        self.mapping_list.addItem(item)
        
        # Select new mapping
        self.mapping_list.setCurrentItem(item)
    
    def _on_delete_mapping(self):
        """Handle Delete button click."""
        # Check if mapping is selected
        if not self.current_mapping:
            return
        
        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the mapping '{self.current_mapping.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Get current name
            name = self.current_mapping.name
            
            # Remove from mappings
            self.mappings.pop(name)
            
            # Remove from list
            row = self.mapping_list.currentRow()
            self.mapping_list.takeItem(row)
            
            # Select another mapping
            if self.mapping_list.count() > 0:
                self.mapping_list.setCurrentRow(0)
            else:
                self.current_mapping = None
                self._update_key_table()
    
    def _on_add_key(self):
        """Handle Add Key button click."""
        # Check if mapping is selected
        if not self.current_mapping:
            return
        
        # Start key recording
        self.recording_key = True
        
        # Show message
        QMessageBox.information(
            self,
            "Record Key",
            "Press any key to add a mapping for it."
        )
    
    def _on_edit_key(self):
        """Handle Edit Key button click."""
        # Check if mapping is selected
        if not self.current_mapping:
            return
        
        # Check if row is selected
        row = self.key_table.currentRow()
        if row < 0:
            return
        
        # Get key
        key_item = self.key_table.item(row, 0)
        if not key_item:
            return
        
        key = key_item.text()
        
        # Show key mapping dialog
        self._show_key_mapping_dialog(key)
    
    def _on_remove_key(self):
        """Handle Remove Key button click."""
        # Check if mapping is selected
        if not self.current_mapping:
            return
        
        # Check if row is selected
        row = self.key_table.currentRow()
        if row < 0:
            return
        
        # Get key
        key_item = self.key_table.item(row, 0)
        if not key_item:
            return
        
        key = key_item.text()
        
        # Remove key mapping
        self.current_mapping.remove_mapping(key)
        
        # Update key table
        self._update_key_table()
    
    def _on_edit_key_row(self):
        """Handle Edit button click in key table."""
        # Get sender button
        button = self.sender()
        if not button:
            return
        
        # Get key
        key = button.property("key")
        if not key:
            return
        
        # Show key mapping dialog
        self._show_key_mapping_dialog(key)
    
    def _on_remove_key_row(self):
        """Handle Remove button click in key table."""
        # Get sender button
        button = self.sender()
        if not button:
            return
        
        # Get key
        key = button.property("key")
        if not key:
            return
        
        # Remove key mapping
        self.current_mapping.remove_mapping(key)
        
        # Update key table
        self._update_key_table()
    
    def _show_key_mapping_dialog(self, key=None):
        """
        Show the key mapping dialog.
        
        Args:
            key (str, optional): Key to edit. If None, adds a new key.
        """
        # Create dialog
        dialog = KeyMappingEditDialog(self.app, self.current_mapping, key, self)
        
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update key table
            self._update_key_table()
    
    def eventFilter(self, obj, event):
        """
        Filter events to capture key presses.
        
        Args:
            obj: Object that received the event.
            event: Event.
        
        Returns:
            bool: True if the event was handled, False otherwise.
        """
        # Check if recording key
        if self.recording_key and event.type() == QEvent.Type.KeyPress:
            # Get key text
            key_text = QKeySequence(event.key()).toString()
            
            # Stop recording
            self.recording_key = False
            
            # Show key mapping dialog
            self._show_key_mapping_dialog(key_text)
            
            return True
        
        return super().eventFilter(obj, event)
    
    def accept(self):
        """Handle dialog acceptance."""
        # Save effect modifiers
        if self.current_mapping:
            # Get effect modifiers
            shift_effect = self.shift_effect_combo.currentText().lower()
            ctrl_effect = self.ctrl_effect_combo.currentText().lower()
            alt_effect = self.alt_effect_combo.currentText().lower()
            
            # Update mapping
            self.current_mapping.effect_modifiers = {
                "shift": shift_effect if shift_effect != "none" else "",
                "ctrl": ctrl_effect if ctrl_effect != "none" else "",
                "alt": alt_effect if alt_effect != "none" else ""
            }
        
        # Save mappings
        self._save_mappings()
        
        # Accept dialog
        super().accept()


class KeyMappingEditDialog(QDialog):
    """Dialog for editing a key mapping."""
    
    def __init__(self, app, mapping, key=None, parent=None):
        """
        Initialize the key mapping edit dialog.
        
        Args:
            app: The main application instance.
            mapping: Key mapping to edit.
            key (str, optional): Key to edit. If None, adds a new key.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.app = app
        self.mapping = mapping
        self.key = key
        self.is_new_key = key is None or key not in mapping.mappings
        
        # Set dialog properties
        self.setWindowTitle("Edit Key Mapping" if not self.is_new_key else "Add Key Mapping")
        self.setMinimumWidth(400)
        
        # Create UI
        self._create_ui()
        
        # Load mapping
        self._load_mapping()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create form layout
        self.form_layout = QFormLayout()
        self.main_layout.addLayout(self.form_layout)
        
        # Create key field
        self.key_label = QLabel(self.key if self.key else "Press a key")
        self.form_layout.addRow("Key:", self.key_label)
        
        if not self.key:
            # Create record button
            self.record_button = QPushButton("Record Key")
            self.record_button.clicked.connect(self._on_record_key)
            self.form_layout.addRow("", self.record_button)
        
        # Create color button
        self.color_button = QPushButton("Choose Color...")
        self.color_button.clicked.connect(self._on_choose_color)
        self.form_layout.addRow("Color:", self.color_button)
        
        # Create timelines group
        self.timelines_group = QGroupBox("Timelines")
        self.form_layout.addRow(self.timelines_group)
        
        self.timelines_layout = QVBoxLayout(self.timelines_group)
        
        # Create timeline checkboxes
        self.timeline_checkboxes = []
        
        # Get number of timelines
        timeline_count = 3  # Default
        if self.app.project_manager.current_project:
            timeline_count = len(self.app.project_manager.current_project.timelines)
        
        # Create checkbox for each timeline
        for i in range(timeline_count):
            checkbox = QCheckBox(f"Ball {i + 1}")
            self.timeline_checkboxes.append(checkbox)
            self.timelines_layout.addWidget(checkbox)
        
        # Create all timelines checkbox
        self.all_timelines_checkbox = QCheckBox("All Timelines")
        self.all_timelines_checkbox.stateChanged.connect(self._on_all_timelines_changed)
        self.timelines_layout.addWidget(self.all_timelines_checkbox)
        
        # Create button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)
        
        # Install event filter for key recording
        self.installEventFilter(self)
    
    def _load_mapping(self):
        """Load the key mapping."""
        # Set default color
        self.color = (255, 0, 0)  # Red
        
        # Set default timelines
        self.timelines = []
        
        # If editing existing key, load its values
        if not self.is_new_key and self.key in self.mapping.mappings:
            # Get mapping
            key_mapping = self.mapping.mappings[self.key]
            
            # Set color
            self.color = key_mapping["color"]
            
            # Set timelines
            self.timelines = key_mapping["timelines"]
            
            # Update color button
            self._update_color_button()
            
            # Update timeline checkboxes
            self._update_timeline_checkboxes()
    
    def _update_color_button(self):
        """Update the color button style."""
        # Set button style
        self.color_button.setStyleSheet(
            f"background-color: rgb({self.color[0]}, {self.color[1]}, {self.color[2]})"
        )
    
    def _update_timeline_checkboxes(self):
        """Update the timeline checkboxes."""
        # Check if all timelines are selected
        all_selected = len(self.timelines) == len(self.timeline_checkboxes)
        
        # Update all timelines checkbox
        self.all_timelines_checkbox.setChecked(all_selected)
        
        # Update individual checkboxes
        for i, checkbox in enumerate(self.timeline_checkboxes):
            checkbox.setChecked(i in self.timelines)
    
    def _on_record_key(self):
        """Handle Record Key button click."""
        # Show message
        QMessageBox.information(
            self,
            "Record Key",
            "Press any key to record it."
        )
    
    def _on_choose_color(self):
        """Handle Choose Color button click."""
        # Show color dialog
        color = QColor(*self.color)
        
        dialog = QColorDialog(color, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get selected color
            color = dialog.selectedColor()
            
            # Update color
            self.color = (color.red(), color.green(), color.blue())
            
            # Update button style
            self._update_color_button()
    
    def _on_all_timelines_changed(self, state):
        """
        Handle All Timelines checkbox state changed.
        
        Args:
            state: Checkbox state.
        """
        # Update individual checkboxes
        for checkbox in self.timeline_checkboxes:
            checkbox.setChecked(state == Qt.CheckState.Checked)
    
    def eventFilter(self, obj, event):
        """
        Filter events to capture key presses.
        
        Args:
            obj: Object that received the event.
            event: Event.
        
        Returns:
            bool: True if the event was handled, False otherwise.
        """
        # Check if key press event
        if event.type() == QEvent.Type.KeyPress:
            # Get key text
            key_text = QKeySequence(event.key()).toString()
            
            # Update key
            self.key = key_text
            self.key_label.setText(key_text)
            
            return True
        
        return super().eventFilter(obj, event)
    
    def accept(self):
        """Handle dialog acceptance."""
        # Check if key is set
        if not self.key:
            QMessageBox.warning(
                self,
                "No Key",
                "Please record a key."
            )
            return
        
        # Get selected timelines
        self.timelines = []
        for i, checkbox in enumerate(self.timeline_checkboxes):
            if checkbox.isChecked():
                self.timelines.append(i)
        
        # Check if timelines are selected
        if not self.timelines:
            QMessageBox.warning(
                self,
                "No Timelines",
                "Please select at least one timeline."
            )
            return
        
        # Add or update mapping
        self.mapping.add_mapping(
            key=self.key,
            color=self.color,
            timelines=self.timelines
        )
        
        # Accept dialog
        super().accept()