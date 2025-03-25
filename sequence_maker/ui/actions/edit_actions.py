"""
Sequence Maker - Edit Actions

This module defines the EditActions class, which contains edit-related actions
for the main window, such as undo, redo, cut, copy, paste, and delete actions.
"""

from PyQt6.QtGui import QAction, QKeySequence


class EditActions:
    """Edit-related actions for the main window."""
    
    def __init__(self, main_window):
        """
        Initialize edit actions.
        
        Args:
            main_window: The main window instance.
        """
        self.main_window = main_window
        self.app = main_window.app
        self._create_actions()
    
    def _create_actions(self):
        """Create edit-related actions."""
        # Undo action
        self.undo_action = QAction("&Undo", self.main_window)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.setStatusTip("Undo the last action")
        self.undo_action.triggered.connect(self.main_window._on_undo)
        self.undo_action.setEnabled(False)
        
        # Redo action
        self.redo_action = QAction("&Redo", self.main_window)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.setStatusTip("Redo the last undone action")
        self.redo_action.triggered.connect(self.main_window._on_redo)
        self.redo_action.setEnabled(False)
        
        # Cut action
        self.cut_action = QAction("Cu&t", self.main_window)
        self.cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        self.cut_action.setStatusTip("Cut the selected items")
        self.cut_action.triggered.connect(self.main_window._on_cut)
        
        # Copy action
        self.copy_action = QAction("&Copy", self.main_window)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.setStatusTip("Copy the selected items")
        self.copy_action.triggered.connect(self.main_window._on_copy)
        
        # Paste action
        self.paste_action = QAction("&Paste", self.main_window)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_action.setStatusTip("Paste the copied items")
        self.paste_action.triggered.connect(self.main_window._on_paste)
        
        # Delete action
        self.delete_action = QAction("&Delete", self.main_window)
        self.delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_action.setStatusTip("Delete the selected items")
        self.delete_action.triggered.connect(self.main_window._on_delete)
        
        # Select All action
        self.select_all_action = QAction("Select &All", self.main_window)
        self.select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        self.select_all_action.setStatusTip("Select all items")
        self.select_all_action.triggered.connect(self.main_window._on_select_all)
        
        # Preferences action
        self.preferences_action = QAction("&Preferences...", self.main_window)
        self.preferences_action.setStatusTip("Edit application preferences")
        self.preferences_action.triggered.connect(self.main_window._on_preferences)