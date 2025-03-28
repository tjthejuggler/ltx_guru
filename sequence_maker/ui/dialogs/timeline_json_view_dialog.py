"""
Sequence Maker - Timeline JSON View Dialog

This module defines the TimelineJsonViewDialog class, which displays the JSON representation
of timelines.
"""

import json
from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QVBoxLayout, QTextEdit, QPushButton,
    QHBoxLayout, QLabel, QSplitter, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class TimelineJsonViewDialog(QDialog):
    """Dialog for viewing JSON representations of timelines."""
    
    def __init__(self, parent, app):
        """
        Initialize the dialog.
        
        Args:
            parent: Parent widget.
            app: The main application instance.
        """
        super().__init__(parent)
        
        self.app = app
        self.setWindowTitle("Timeline JSON View")
        self.resize(800, 600)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        # Create tabs for each timeline
        self.create_timeline_tabs()
        
        # Create button layout
        button_layout = QHBoxLayout()
        self.layout.addLayout(button_layout)
        
        # Add close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
    
    def create_timeline_tabs(self):
        """Create tabs for each timeline."""
        # Get timelines from the timeline manager
        timelines = self.app.timeline_manager.get_timelines()
        
        if not timelines:
            # Create a single tab with a message
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            label = QLabel("No timelines available.")
            tab_layout.addWidget(label)
            self.tab_widget.addTab(tab, "No Timelines")
            return
        
        # Create a tab for each timeline
        for timeline in timelines:
            # Create tab widget
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            # Create a splitter for the two JSON views
            splitter = QSplitter(Qt.Orientation.Vertical)
            tab_layout.addWidget(splitter)
            
            # Create text edit for timeline.to_dict() JSON
            dict_container = QWidget()
            dict_layout = QVBoxLayout(dict_container)
            dict_label = QLabel("Timeline Dictionary (to_dict):")
            dict_layout.addWidget(dict_label)
            
            dict_text = QTextEdit()
            dict_text.setReadOnly(True)
            dict_text.setFont(QFont("Courier New", 10))
            dict_layout.addWidget(dict_text)
            
            # Format the JSON with indentation
            timeline_dict = timeline.to_dict()
            formatted_dict = json.dumps(timeline_dict, indent=2)
            dict_text.setText(formatted_dict)
            
            # Create text edit for timeline.to_json_sequence() JSON
            seq_container = QWidget()
            seq_layout = QVBoxLayout(seq_container)
            seq_label = QLabel("JSON Sequence (to_json_sequence):")
            seq_layout.addWidget(seq_label)
            
            seq_text = QTextEdit()
            seq_text.setReadOnly(True)
            seq_text.setFont(QFont("Courier New", 10))
            seq_layout.addWidget(seq_text)
            
            # Format the JSON with indentation
            json_sequence = timeline.to_json_sequence()
            formatted_seq = json.dumps(json_sequence, indent=2)
            seq_text.setText(formatted_seq)
            
            # Add containers to splitter
            splitter.addWidget(dict_container)
            splitter.addWidget(seq_container)
            
            # Add tab to tab widget
            self.tab_widget.addTab(tab, timeline.name)