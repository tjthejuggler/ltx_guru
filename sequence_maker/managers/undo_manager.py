"""
Sequence Maker - Undo Manager

This module defines the UndoManager class, which handles undo and redo operations.
"""

import logging
from PyQt6.QtCore import QObject, pyqtSignal


class UndoAction:
    """
    Represents an undoable action.
    
    Attributes:
        action_type (str): Type of action.
        undo_func (callable): Function to call for undo.
        redo_func (callable): Function to call for redo.
        params (dict): Parameters for the undo and redo functions.
    """
    
    def __init__(self, action_type, undo_func, redo_func, **params):
        """
        Initialize an undo action.
        
        Args:
            action_type (str): Type of action.
            undo_func (callable): Function to call for undo.
            redo_func (callable): Function to call for redo.
            **params: Parameters for the undo and redo functions.
        """
        self.action_type = action_type
        self.undo_func = undo_func
        self.redo_func = redo_func
        self.params = params
    
    def undo(self):
        """
        Perform the undo operation.
        
        Returns:
            The result of the undo function.
        """
        return self.undo_func(**self.params)
    
    def redo(self):
        """
        Perform the redo operation.
        
        Returns:
            The result of the redo function.
        """
        return self.redo_func(**self.params)
    
    def __str__(self):
        """Return a string representation of the action."""
        return f"UndoAction({self.action_type})"


class UndoManager(QObject):
    """
    Manages undo and redo operations.
    
    Signals:
        undo_performed: Emitted when an undo operation is performed.
        redo_performed: Emitted when a redo operation is performed.
        undo_stack_changed: Emitted when the undo stack changes.
        redo_stack_changed: Emitted when the redo stack changes.
    """
    
    # Signals
    undo_performed = pyqtSignal(str)  # action_type
    redo_performed = pyqtSignal(str)  # action_type
    undo_stack_changed = pyqtSignal()
    redo_stack_changed = pyqtSignal()
    
    def __init__(self, app, max_stack_size=100):
        """
        Initialize the undo manager.
        
        Args:
            app: The main application instance.
            max_stack_size (int, optional): Maximum size of the undo and redo stacks. Defaults to 100.
        """
        super().__init__()
        
        self.logger = logging.getLogger("SequenceMaker.UndoManager")
        self.app = app
        
        self.max_stack_size = max_stack_size
        self.undo_stack = []
        self.redo_stack = []
        
        # Group related actions
        self.group_active = False
        self.current_group = []
    
    def add_action(self, action_type, undo_func, redo_func, **params):
        """
        Add an action to the undo stack.
        
        Args:
            action_type (str): Type of action.
            undo_func (callable): Function to call for undo.
            redo_func (callable): Function to call for redo.
            **params: Parameters for the undo and redo functions.
        """
        action = UndoAction(action_type, undo_func, redo_func, **params)
        
        # If grouping is active, add to current group
        if self.group_active:
            self.current_group.append(action)
            return
        
        # Add to undo stack
        self.undo_stack.append(action)
        
        # Limit stack size
        if len(self.undo_stack) > self.max_stack_size:
            self.undo_stack.pop(0)
        
        # Clear redo stack
        self.redo_stack.clear()
        
        # Emit signals
        self.undo_stack_changed.emit()
        self.redo_stack_changed.emit()
    
    def begin_group(self):
        """
        Begin a group of actions that will be undone/redone together.
        
        Returns:
            bool: True if a new group was started, False if a group was already active.
        """
        if self.group_active:
            self.logger.warning("Cannot begin group: Group already active")
            return False
        
        self.group_active = True
        self.current_group = []
        
        return True
    
    def end_group(self, action_type="group"):
        """
        End the current group of actions.
        
        Args:
            action_type (str, optional): Type of action for the group. Defaults to "group".
        
        Returns:
            bool: True if the group was ended, False if no group was active.
        """
        if not self.group_active:
            self.logger.warning("Cannot end group: No group active")
            return False
        
        # If group is empty, just deactivate
        if not self.current_group:
            self.group_active = False
            return True
        
        # Create a group action
        group = self.current_group.copy()
        
        def undo_group(**_):
            """Undo all actions in the group in reverse order."""
            for action in reversed(group):
                action.undo()
            return True
        
        def redo_group(**_):
            """Redo all actions in the group in order."""
            for action in group:
                action.redo()
            return True
        
        # Add group action to undo stack
        self.undo_stack.append(UndoAction(action_type, undo_group, redo_group))
        
        # Limit stack size
        if len(self.undo_stack) > self.max_stack_size:
            self.undo_stack.pop(0)
        
        # Clear redo stack
        self.redo_stack.clear()
        
        # Reset group state
        self.group_active = False
        self.current_group = []
        
        # Emit signals
        self.undo_stack_changed.emit()
        self.redo_stack_changed.emit()
        
        return True
    
    def cancel_group(self):
        """
        Cancel the current group of actions.
        
        Returns:
            bool: True if the group was canceled, False if no group was active.
        """
        if not self.group_active:
            self.logger.warning("Cannot cancel group: No group active")
            return False
        
        # Reset group state
        self.group_active = False
        self.current_group = []
        
        return True
    
    def undo(self):
        """
        Undo the last action.
        
        Returns:
            bool: True if an action was undone, False if the undo stack is empty.
        """
        if not self.undo_stack:
            self.logger.info("Cannot undo: Undo stack is empty")
            return False
        
        # Get the last action
        action = self.undo_stack.pop()
        
        # Perform undo
        self.logger.info(f"Undoing action: {action}")
        result = action.undo()
        
        # Add to redo stack
        self.redo_stack.append(action)
        
        # Emit signals
        self.undo_performed.emit(action.action_type)
        self.undo_stack_changed.emit()
        self.redo_stack_changed.emit()
        
        return result
    
    def redo(self):
        """
        Redo the last undone action.
        
        Returns:
            bool: True if an action was redone, False if the redo stack is empty.
        """
        if not self.redo_stack:
            self.logger.info("Cannot redo: Redo stack is empty")
            return False
        
        # Get the last undone action
        action = self.redo_stack.pop()
        
        # Perform redo
        self.logger.info(f"Redoing action: {action}")
        result = action.redo()
        
        # Add to undo stack
        self.undo_stack.append(action)
        
        # Emit signals
        self.redo_performed.emit(action.action_type)
        self.undo_stack_changed.emit()
        self.redo_stack_changed.emit()
        
        return result
    
    def can_undo(self):
        """
        Check if undo is available.
        
        Returns:
            bool: True if undo is available, False otherwise.
        """
        return len(self.undo_stack) > 0
    
    def can_redo(self):
        """
        Check if redo is available.
        
        Returns:
            bool: True if redo is available, False otherwise.
        """
        return len(self.redo_stack) > 0
    
    def get_undo_action_type(self):
        """
        Get the type of the next action to undo.
        
        Returns:
            str: Action type, or None if the undo stack is empty.
        """
        if not self.undo_stack:
            return None
        
        return self.undo_stack[-1].action_type
    
    def get_redo_action_type(self):
        """
        Get the type of the next action to redo.
        
        Returns:
            str: Action type, or None if the redo stack is empty.
        """
        if not self.redo_stack:
            return None
        
        return self.redo_stack[-1].action_type
    
    def clear(self):
        """Clear both undo and redo stacks."""
        self.undo_stack.clear()
        self.redo_stack.clear()
        
        # Emit signals
        self.undo_stack_changed.emit()
        self.redo_stack_changed.emit()