"""
Sequence Maker - Edit Handlers

This module defines the EditHandlers class, which contains handlers for edit-related
operations such as undo, redo, cut, copy, paste, and delete operations.
"""

from PyQt6.QtWidgets import QMessageBox


class EditHandlers:
    """Edit operation handlers for the main window."""
    
    def __init__(self, main_window):
        """
        Initialize edit handlers.
        
        Args:
            main_window: The main window instance.
        """
        self.main_window = main_window
        self.app = main_window.app
    
    def on_undo(self):
        """Undo the last action."""
        if self.app.undo_manager:
            self.app.undo_manager.undo()
    
    def on_redo(self):
        """Redo the last undone action."""
        if self.app.undo_manager:
            self.app.undo_manager.redo()
    
    def on_cut(self):
        """Cut the selected segment."""
        if self.main_window.timeline_widget:
            self.main_window.timeline_widget.cut_selected_segment()
    
    def on_copy(self):
        """Copy the selected segment."""
        if self.main_window.timeline_widget:
            self.main_window.timeline_widget.copy_selected_segment()
    
    def on_paste(self):
        """Paste the copied segment."""
        if self.main_window.timeline_widget:
            self.main_window.timeline_widget.paste_segment()
    
    def on_delete(self):
        """Delete the selected segment."""
        if self.main_window.timeline_widget:
            self.main_window.timeline_widget.delete_selected_segment()
    
    def on_select_all(self):
        """Select all segments in the current timeline."""
        if self.main_window.timeline_widget:
            self.main_window.timeline_widget.select_all_segments()
    
    def on_preferences(self):
        """Show preferences dialog."""
        from ui.dialogs.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.app, self.main_window)
        dialog.exec()