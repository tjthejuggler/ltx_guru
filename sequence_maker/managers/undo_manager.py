"""
Sequence Maker - Undo Manager

This module defines the UndoManager class, which handles undo and redo operations
using a snapshot-based approach.
"""

import logging
import copy
import json
from PyQt6.QtCore import QObject, pyqtSignal


class TimelineState:
    """
    Represents a snapshot of the entire timeline state.
    
    Attributes:
        action_type (str): Type of action that created this state.
        timelines (list): Deep copy of all timelines.
    """
    
    def __init__(self, action_type, timelines):
        """
        Initialize a timeline state.
        
        Args:
            action_type (str): Type of action that created this state.
            timelines (list): List of timelines to copy.
        """
        self.action_type = action_type
        
        # Create a deep copy of all timelines
        self.timelines = []
        for timeline in timelines:
            # Convert to dict and back to create a deep copy
            timeline_dict = timeline.to_dict()
            self.timelines.append(timeline_dict)
        
        # Create a unique ID for this state to help with debugging
        import uuid
        self.state_id = str(uuid.uuid4())[:8]
        
        # Get logger
        self.logger = logging.getLogger("SequenceMaker.TimelineState")
        self.logger.debug(f"Created state {self.state_id} of type {action_type} with {len(timelines)} timelines")
    
    def __str__(self):
        """Return a string representation of the state."""
        return f"TimelineState({self.action_type}, id={self.state_id}, timelines={len(self.timelines)})"


class UndoManager(QObject):
    """
    Manages undo and redo operations using a snapshot-based approach.
    
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
        
        # For backward compatibility
        self.group_active = False
        self.current_group = []
    
    def save_state(self, action_type):
        """
        Save the current state of all timelines.
        
        Args:
            action_type (str): Type of action that will be performed.
        
        Returns:
            TimelineState: The saved state.
        """
        if not self.app.project_manager.current_project:
            self.logger.warning("Cannot save state: No project loaded")
            return None
        
        # Get all timelines
        timelines = self.app.project_manager.current_project.timelines
        
        # Create a new state
        state = TimelineState(action_type, timelines)
        
        # Add to undo stack
        self.undo_stack.append(state)
        
        # Limit stack size
        if len(self.undo_stack) > self.max_stack_size:
            self.undo_stack.pop(0)
        
        # Clear redo stack - this is critical for proper undo/redo behavior
        if self.redo_stack:
            self.logger.debug(f"Clearing redo stack with {len(self.redo_stack)} items")
            self.redo_stack.clear()
        
        # Emit signals
        self.undo_stack_changed.emit()
        self.redo_stack_changed.emit()
        
        return state
    
    def restore_state(self, state):
        """
        Restore a saved state.
        
        Args:
            state (TimelineState): State to restore.
        
        Returns:
            bool: True if the state was restored, False otherwise.
        """
        if not self.app.project_manager.current_project:
            self.logger.warning("Cannot restore state: No project loaded")
            return False
        
        # Get the project
        project = self.app.project_manager.current_project
        
        # Clear current timelines
        old_timelines = project.timelines.copy()
        project.timelines.clear()
        
        # Restore timelines from state
        from models.timeline import Timeline
        for timeline_dict in state.timelines:
            timeline = Timeline.from_dict(timeline_dict)
            project.add_timeline(timeline)
        
        # Notify timeline manager of changes
        for timeline in old_timelines:
            self.app.timeline_manager.timeline_removed.emit(timeline)
        
        for timeline in project.timelines:
            self.app.timeline_manager.timeline_added.emit(timeline)
        
        return True
    
    def undo(self):
        """
        Undo the last action by restoring the previous state.
        
        Returns:
            bool: True if an action was undone, False if the undo stack is empty.
        """
        if len(self.undo_stack) <= 1:
            self.logger.info("Cannot undo: Not enough states in undo stack")
            return False
        
        # Get the current state (top of undo stack)
        current_state = self.undo_stack.pop()
        
        # Get the previous state (new top of undo stack)
        previous_state = self.undo_stack[-1]
        
        # Log undo stack state
        self.logger.debug(f"Undo stack before undo: {[str(s) for s in self.undo_stack]}")
        self.logger.debug(f"Redo stack before undo: {[str(s) for s in self.redo_stack]}")
        
        # Restore the previous state
        self.logger.info(f"Undoing to state: {previous_state}")
        result = self.restore_state(previous_state)
        
        # Add current state to redo stack
        self.redo_stack.append(current_state)
        
        # Log stack state after undo
        self.logger.debug(f"Undo stack after undo: {[str(s) for s in self.undo_stack]}")
        self.logger.debug(f"Redo stack after undo: {[str(s) for s in self.redo_stack]}")
        
        # Emit signals
        self.undo_performed.emit(current_state.action_type)
        self.undo_stack_changed.emit()
        self.redo_stack_changed.emit()
        
        return result
    
    def redo(self):
        """
        Redo the last undone action by restoring the next state.
        
        Returns:
            bool: True if an action was redone, False if the redo stack is empty.
        """
        if not self.redo_stack:
            self.logger.info("Cannot redo: Redo stack is empty")
            return False
        
        # Get the next state (top of redo stack)
        next_state = self.redo_stack.pop()
        
        # Log stack state before redo
        self.logger.debug(f"Undo stack before redo: {[str(s) for s in self.undo_stack]}")
        self.logger.debug(f"Redo stack before redo: {[str(s) for s in self.redo_stack]}")
        
        # Restore the next state
        self.logger.info(f"Redoing to state: {next_state}")
        result = self.restore_state(next_state)
        
        # Add next state to undo stack
        self.undo_stack.append(next_state)
        
        # Log stack state after redo
        self.logger.debug(f"Undo stack after redo: {[str(s) for s in self.undo_stack]}")
        self.logger.debug(f"Redo stack after redo: {[str(s) for s in self.redo_stack]}")
        
        # Emit signals
        self.redo_performed.emit(next_state.action_type)
        self.undo_stack_changed.emit()
        self.redo_stack_changed.emit()
        
        return result
    
    def can_undo(self):
        """
        Check if undo is available.
        
        Returns:
            bool: True if undo is available, False otherwise.
        """
        return len(self.undo_stack) > 1
    
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
        if len(self.undo_stack) <= 1:
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
    
    # For backward compatibility
    def add_action(self, action_type, **params):
        """
        Add an action to the undo stack by saving the current state.
        
        Args:
            action_type (str): Type of action.
            **params: Ignored for backward compatibility.
        """
        self.save_state(action_type)
    
    def begin_group(self):
        """For backward compatibility."""
        self.logger.debug("begin_group called - using save_state instead")
        return True
    
    def end_group(self, action_type="group"):
        """For backward compatibility."""
        self.logger.debug("end_group called - using save_state instead")
        return True
    
    def cancel_group(self):
        """For backward compatibility."""
        self.logger.debug("cancel_group called - no action needed")
        return True