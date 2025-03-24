"""
Sequence Maker - Task Templates Dialog

This module defines the TaskTemplatesDialog class, which allows users to manage LLM task templates.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QListWidget, QListWidgetItem, QSplitter,
    QWidget, QLineEdit, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

from models.llm_customization import LLMTaskTemplate, create_default_templates


class TaskTemplatesDialog(QDialog):
    """Dialog for managing LLM task templates."""
    
    def __init__(self, app, parent=None):
        """
        Initialize the task templates dialog.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.TaskTemplatesDialog")
        
        # Set dialog properties
        self.setWindowTitle("LLM Task Templates")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        
        # Templates
        self.templates = []
        self.current_template_index = -1
        
        # Create UI
        self._create_ui()
        
        # Load templates
        self._load_templates()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create header
        self.header_label = QLabel("LLM Task Templates")
        self.header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.main_layout.addWidget(self.header_label)
        
        # Create description
        self.description_label = QLabel(
            "Manage task templates for common LLM operations. Templates provide pre-defined prompts for specific tasks."
        )
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)
        
        # Create splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter, 1)
        
        # Create template list widget
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        
        self.template_list = QListWidget()
        self.template_list.setMinimumWidth(250)
        self.template_list.currentRowChanged.connect(self._on_template_selected)
        self.list_layout.addWidget(self.template_list)
        
        self.list_button_layout = QHBoxLayout()
        self.list_layout.addLayout(self.list_button_layout)
        
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self._on_add_template)
        self.list_button_layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self._on_remove_template)
        self.list_button_layout.addWidget(self.remove_button)
        
        self.reset_button = QPushButton("Reset to Default")
        self.reset_button.clicked.connect(self._on_reset_templates)
        self.list_button_layout.addWidget(self.reset_button)
        
        self.splitter.addWidget(self.list_widget)
        
        # Create template editor widget
        self.editor_widget = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_widget)
        
        self.editor_form = QFormLayout()
        self.editor_layout.addLayout(self.editor_form)
        
        self.name_edit = QLineEdit()
        self.editor_form.addRow("Name:", self.name_edit)
        
        self.description_edit = QLineEdit()
        self.editor_form.addRow("Description:", self.description_edit)
        
        self.prompt_label = QLabel("Prompt:")
        self.editor_layout.addWidget(self.prompt_label)
        
        self.prompt_edit = QTextEdit()
        self.editor_layout.addWidget(self.prompt_edit)
        
        self.editor_button_layout = QHBoxLayout()
        self.editor_layout.addLayout(self.editor_button_layout)
        
        self.save_template_button = QPushButton("Save Template")
        self.save_template_button.clicked.connect(self._on_save_template)
        self.editor_button_layout.addWidget(self.save_template_button)
        
        self.splitter.addWidget(self.editor_widget)
        
        # Create dialog buttons
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        
        self.button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.button_layout.addWidget(self.close_button)
        
        # Set splitter sizes
        self.splitter.setSizes([300, 500])
        
        # Disable editor initially
        self._set_editor_enabled(False)
    
    def _set_editor_enabled(self, enabled):
        """
        Enable or disable the template editor.
        
        Args:
            enabled (bool): Whether to enable the editor.
        """
        self.name_edit.setEnabled(enabled)
        self.description_edit.setEnabled(enabled)
        self.prompt_edit.setEnabled(enabled)
        self.save_template_button.setEnabled(enabled)
    
    def _load_templates(self):
        """Load templates from the current project."""
        # Clear list
        self.template_list.clear()
        self.templates = []
        
        if self.app.project_manager.current_project:
            # Get templates from project
            templates_data = getattr(self.app.project_manager.current_project, "llm_task_templates", None)
            
            if templates_data is None or not templates_data:
                # Create default templates if none exist
                self.templates = create_default_templates()
                self._save_templates()
            else:
                # Load templates from project data
                for template_data in templates_data:
                    template = LLMTaskTemplate.from_dict(template_data)
                    self.templates.append(template)
            
            # Populate list
            for template in self.templates:
                item = QListWidgetItem(template.name)
                item.setToolTip(template.description)
                self.template_list.addItem(item)
    
    def _save_templates(self):
        """Save templates to the current project."""
        if self.app.project_manager.current_project:
            # Convert templates to dictionaries
            templates_data = [template.to_dict() for template in self.templates]
            
            # Save to project
            self.app.project_manager.current_project.llm_task_templates = templates_data
            
            # Mark project as changed
            self.app.project_manager.project_changed.emit()
            
            # Log
            self.logger.info(f"Saved {len(templates_data)} LLM task templates")
    
    def _on_template_selected(self, row):
        """
        Handle template selection.
        
        Args:
            row (int): Selected row index.
        """
        if 0 <= row < len(self.templates):
            # Save current template if one is being edited
            if 0 <= self.current_template_index < len(self.templates):
                self._save_current_template()
            
            # Set current template index
            self.current_template_index = row
            
            # Get template
            template = self.templates[row]
            
            # Update editor
            self.name_edit.setText(template.name)
            self.description_edit.setText(template.description)
            self.prompt_edit.setText(template.prompt)
            
            # Enable editor
            self._set_editor_enabled(True)
        else:
            # Disable editor
            self._set_editor_enabled(False)
            self.current_template_index = -1
    
    def _save_current_template(self):
        """Save the currently edited template."""
        if 0 <= self.current_template_index < len(self.templates):
            # Get template
            template = self.templates[self.current_template_index]
            
            # Update template
            template.name = self.name_edit.text()
            template.description = self.description_edit.text()
            template.prompt = self.prompt_edit.toPlainText()
            
            # Update list item
            item = self.template_list.item(self.current_template_index)
            item.setText(template.name)
            item.setToolTip(template.description)
    
    def _on_save_template(self):
        """Handle Save Template button click."""
        # Save current template
        self._save_current_template()
        
        # Save templates to project
        self._save_templates()
        
        # Show confirmation
        QMessageBox.information(
            self,
            "Template Saved",
            "The template has been saved."
        )
    
    def _on_add_template(self):
        """Handle Add button click."""
        # Create new template
        template = LLMTaskTemplate(
            name="New Template",
            prompt="",
            description="New template description"
        )
        
        # Add to templates
        self.templates.append(template)
        
        # Add to list
        item = QListWidgetItem(template.name)
        item.setToolTip(template.description)
        self.template_list.addItem(item)
        
        # Select new template
        self.template_list.setCurrentRow(len(self.templates) - 1)
    
    def _on_remove_template(self):
        """Handle Remove button click."""
        if 0 <= self.current_template_index < len(self.templates):
            # Confirm removal
            result = QMessageBox.question(
                self,
                "Remove Template",
                f"Are you sure you want to remove the template '{self.templates[self.current_template_index].name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if result == QMessageBox.StandardButton.Yes:
                # Remove template
                self.templates.pop(self.current_template_index)
                
                # Remove from list
                self.template_list.takeItem(self.current_template_index)
                
                # Save templates
                self._save_templates()
                
                # Clear editor
                self.name_edit.clear()
                self.description_edit.clear()
                self.prompt_edit.clear()
                
                # Disable editor
                self._set_editor_enabled(False)
                self.current_template_index = -1
    
    def _on_reset_templates(self):
        """Handle Reset to Default button click."""
        # Confirm reset
        result = QMessageBox.question(
            self,
            "Reset Templates",
            "Are you sure you want to reset all templates to default? This will remove any custom templates.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Reset templates
            self.templates = create_default_templates()
            
            # Save templates
            self._save_templates()
            
            # Reload templates
            self._load_templates()
            
            # Clear editor
            self.name_edit.clear()
            self.description_edit.clear()
            self.prompt_edit.clear()
            
            # Disable editor
            self._set_editor_enabled(False)
            self.current_template_index = -1
    
    def accept(self):
        """Handle dialog acceptance."""
        # Save current template if one is being edited
        if 0 <= self.current_template_index < len(self.templates):
            self._save_current_template()
        
        # Save templates to project
        self._save_templates()
        
        # Accept dialog
        super().accept()