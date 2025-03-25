"""
Sequence Maker - Tools Handlers

This module defines the ToolsHandlers class, which contains handlers for tools-related
operations such as key mapping, connect balls, and LLM-related operations.
"""


class ToolsHandlers:
    """Tools operation handlers for the main window."""
    
    def __init__(self, main_window):
        """
        Initialize tools handlers.
        
        Args:
            main_window: The main window instance.
        """
        self.main_window = main_window
        self.app = main_window.app
    
    def on_key_mapping(self):
        """Show key mapping dialog."""
        from ui.dialogs.key_mapping_dialog import KeyMappingDialog
        dialog = KeyMappingDialog(self.app, self.main_window)
        dialog.exec()
    
    def on_connect_balls(self):
        """Connect to juggling balls."""
        # Toggle connection state
        if self.main_window.tools_actions.connect_balls_action.isChecked():
            # Connect to balls
            self.app.ball_manager.connect_balls()
        else:
            # Disconnect from balls
            self.app.ball_manager.disconnect_balls()
    
    def on_llm_chat(self):
        """Show LLM chat window."""
        if self.main_window.llm_chat_window:
            self.main_window.llm_chat_window.show()
            self.main_window.llm_chat_window.raise_()
            self.main_window.llm_chat_window.activateWindow()
    
    def on_llm_diagnostics(self):
        """Show LLM diagnostics dialog."""
        from ui.dialogs.llm_diagnostics_dialog import LLMDiagnosticsDialog
        dialog = LLMDiagnosticsDialog(self.app, self.main_window)
        dialog.exec()
    
    def on_process_lyrics(self):
        """Process lyrics for timeline."""
        # Check if lyrics manager exists
        if not hasattr(self.app, 'lyrics_manager'):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self.main_window,
                "Lyrics Manager Not Found",
                "The lyrics manager is not available."
            )
            return
        
        # Show lyrics input dialog
        from ui.dialogs.lyrics_input_dialog import LyricsInputDialog
        dialog = LyricsInputDialog(self.app, self.main_window)
        dialog.exec()
    
    def on_about(self):
        """Show about dialog."""
        from ui.dialogs.about_dialog import AboutDialog
        dialog = AboutDialog(self.main_window)
        dialog.exec()
    
    def on_help(self):
        """Show help."""
        # Open help documentation
        import webbrowser
        webbrowser.open("https://sequence-maker.readthedocs.io/")