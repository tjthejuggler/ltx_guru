"""
Sequence Maker - Tools Actions

This module defines the ToolsActions class, which contains tools-related actions
for the main window, such as key mapping, connect balls, and LLM-related actions.
"""

from PyQt6.QtGui import QAction


class ToolsActions:
    """Tools-related actions for the main window."""
    
    def __init__(self, main_window):
        """
        Initialize tools actions.
        
        Args:
            main_window: The main window instance.
        """
        self.main_window = main_window
        self.app = main_window.app
        self._create_actions()
    
    def _create_actions(self):
        """Create tools-related actions."""
        # Key Mapping action
        self.key_mapping_action = QAction("&Key Mapping...", self.main_window)
        self.key_mapping_action.setStatusTip("Configure key mappings")
        self.key_mapping_action.triggered.connect(self.main_window._on_key_mapping)
        
        # Connect Balls action
        self.connect_balls_action = QAction("&Connect Balls", self.main_window)
        self.connect_balls_action.setStatusTip("Connect to juggling balls")
        self.connect_balls_action.triggered.connect(self.main_window._on_connect_balls)
        self.connect_balls_action.setCheckable(True)
        
        # LLM Chat action
        self.llm_chat_action = QAction("&LLM Chat...", self.main_window)
        self.llm_chat_action.setStatusTip("Open LLM chat interface")
        self.llm_chat_action.triggered.connect(self.main_window._on_llm_chat)
        
        # LLM Diagnostics action
        self.llm_diagnostics_action = QAction("LLM &Diagnostics...", self.main_window)
        self.llm_diagnostics_action.setStatusTip("View LLM performance metrics and diagnostics")
        self.llm_diagnostics_action.triggered.connect(self.main_window._on_llm_diagnostics)
        
        # Process Lyrics action
        self.process_lyrics_action = QAction("Process &Lyrics...", self.main_window)
        self.process_lyrics_action.setStatusTip("Process lyrics for timeline")
        self.process_lyrics_action.triggered.connect(self.main_window._on_process_lyrics)
        
        # Help actions
        self.about_action = QAction("&About", self.main_window)
        self.about_action.setStatusTip("About Sequence Maker")
        self.about_action.triggered.connect(self.main_window._on_about)
        
        self.help_action = QAction("&Help", self.main_window)
        self.help_action.setStatusTip("Show help")
        self.help_action.triggered.connect(self.main_window._on_help)