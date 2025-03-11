"""
Sequence Maker - About Dialog

This module defines the AboutDialog class, which displays information about the application.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QTextBrowser
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont

from app.constants import APP_NAME, APP_VERSION, APP_AUTHOR


class AboutDialog(QDialog):
    """Dialog for displaying information about the application."""
    
    def __init__(self, parent=None):
        """
        Initialize the about dialog.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.AboutDialog")
        
        # Set dialog properties
        self.setWindowTitle("About Sequence Maker")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create header layout
        self.header_layout = QHBoxLayout()
        self.main_layout.addLayout(self.header_layout)
        
        # Create logo label
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(64, 64)
        self.header_layout.addWidget(self.logo_label)
        
        # Create title layout
        self.title_layout = QVBoxLayout()
        self.header_layout.addLayout(self.title_layout)
        
        # Create title label
        self.title_label = QLabel(APP_NAME)
        self.title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.title_layout.addWidget(self.title_label)
        
        # Create version label
        self.version_label = QLabel(f"Version {APP_VERSION}")
        self.title_layout.addWidget(self.version_label)
        
        # Create author label
        self.author_label = QLabel(f"By {APP_AUTHOR}")
        self.title_layout.addWidget(self.author_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create about tab
        self.about_tab = QWidget()
        self.tab_widget.addTab(self.about_tab, "About")
        
        self.about_layout = QVBoxLayout(self.about_tab)
        
        self.about_text = QTextBrowser()
        self.about_text.setOpenExternalLinks(True)
        self.about_text.setHtml("""
            <h3>Sequence Maker</h3>
            <p>A tool for creating color sequences for LTX juggling balls.</p>
            <p>This application allows you to create, edit, and visualize color sequences for LTX juggling balls. 
            It provides an intuitive interface for designing complex color patterns, synchronizing them with music, 
            and exporting them to the LTX ball format.</p>
            <p>Features include:</p>
            <ul>
                <li>Interactive timeline editing</li>
                <li>Audio synchronization</li>
                <li>Real-time ball visualization</li>
                <li>Customizable keyboard mappings</li>
                <li>Export to JSON and PRG formats</li>
                <li>LLM integration for automatic sequence generation</li>
            </ul>
        """)
        self.about_layout.addWidget(self.about_text)
        
        # Create license tab
        self.license_tab = QWidget()
        self.tab_widget.addTab(self.license_tab, "License")
        
        self.license_layout = QVBoxLayout(self.license_tab)
        
        self.license_text = QTextBrowser()
        self.license_text.setHtml("""
            <h3>MIT License</h3>
            <p>Copyright (c) 2025 LTX Guru</p>
            <p>Permission is hereby granted, free of charge, to any person obtaining a copy
            of this software and associated documentation files (the "Software"), to deal
            in the Software without restriction, including without limitation the rights
            to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
            copies of the Software, and to permit persons to whom the Software is
            furnished to do so, subject to the following conditions:</p>
            <p>The above copyright notice and this permission notice shall be included in all
            copies or substantial portions of the Software.</p>
            <p>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
            IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
            FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
            AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
            LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
            OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
            SOFTWARE.</p>
        """)
        self.license_layout.addWidget(self.license_text)
        
        # Create credits tab
        self.credits_tab = QWidget()
        self.tab_widget.addTab(self.credits_tab, "Credits")
        
        self.credits_layout = QVBoxLayout(self.credits_tab)
        
        self.credits_text = QTextBrowser()
        self.credits_text.setHtml("""
            <h3>Credits</h3>
            <p>Sequence Maker uses the following open source libraries:</p>
            <ul>
                <li><b>PyQt6</b> - GUI framework</li>
                <li><b>librosa</b> - Audio analysis</li>
                <li><b>PyAudio</b> - Audio playback</li>
                <li><b>numpy</b> - Numerical computing</li>
                <li><b>matplotlib</b> - Data visualization</li>
            </ul>
            <p>Special thanks to:</p>
            <ul>
                <li>The LTX Guru team for their support and guidance</li>
                <li>All contributors to the open source libraries used in this project</li>
                <li>The juggling community for their feedback and suggestions</li>
            </ul>
        """)
        self.credits_layout.addWidget(self.credits_text)
        
        # Create close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.main_layout.addWidget(self.close_button)