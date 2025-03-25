# Refactoring Plan for main_window.py

After analyzing the codebase, I've gained a comprehensive understanding of the Sequence Maker application structure and how `main_window.py` interacts with other components. The file has grown to over 1600 lines, making it difficult to maintain and debug. Here's my detailed plan to refactor it into smaller, more manageable components.

## Current Structure Analysis

The `main_window.py` file currently contains:

1. **ApplyTextEdit** class - A custom QTextEdit that applies changes on Enter key press
2. **MainWindow** class - The main application window with numerous responsibilities:
   - UI creation and layout
   - Menu and toolbar creation
   - Action definitions and handlers (over 30 actions)
   - File operations (new, open, save)
   - Timeline operations
   - Segment editing
   - Playback controls
   - Dialog management
   - Settings management
   - Event handling
   - Time and color parsing/formatting

The application follows an MVC-like pattern with:
- **Models**: `models/` directory (Project, Timeline, Segment, etc.)
- **Views**: `ui/` directory (MainWindow, TimelineWidget, AudioWidget, etc.)
- **Controllers**: `managers/` directory (ProjectManager, TimelineManager, etc.)

## Refactoring Strategy

I propose breaking down the `main_window.py` file into multiple smaller files based on functionality, following these principles:

1. **Single Responsibility Principle**: Each class should have only one reason to change
2. **Separation of Concerns**: UI, actions, and handlers should be separated
3. **Maintainability**: Smaller files are easier to understand and modify
4. **Testability**: Isolated components are easier to test

## Proposed File Structure

```
sequence_maker/ui/
├── main_window.py                  # Main window class (core functionality only)
├── widgets/
│   ├── __init__.py
│   └── apply_text_edit.py          # Custom text edit widget
├── actions/
│   ├── __init__.py
│   ├── file_actions.py             # File-related actions (new, open, save)
│   ├── edit_actions.py             # Edit-related actions (undo, redo, cut, copy)
│   ├── view_actions.py             # View-related actions (zoom)
│   ├── timeline_actions.py         # Timeline-related actions
│   ├── playback_actions.py         # Playback-related actions
│   └── tools_actions.py            # Tools-related actions
├── handlers/
│   ├── __init__.py
│   ├── file_handlers.py            # File operation handlers
│   ├── segment_handlers.py         # Segment editing handlers
│   ├── boundary_handlers.py        # Boundary editing handlers
│   └── utility_handlers.py         # Utility functions (time/color parsing)
└── dialogs/
    └── ... (existing dialog files)
```

## Detailed Refactoring Steps

### 1. Extract ApplyTextEdit Class

Move the `ApplyTextEdit` class to its own file:

```python
# sequence_maker/ui/widgets/apply_text_edit.py
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QKeyEvent

class ApplyTextEdit(QTextEdit):
    """
    Custom QTextEdit that applies changes when Enter is pressed instead of creating a new line.
    """
    apply_pressed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Override keyPressEvent to handle Enter key."""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Log the event for debugging
            print(f"Enter key pressed in {self.__class__.__name__}")
            
            # Emit apply_pressed signal instead of inserting a new line
            self.apply_pressed.emit()
            
            # Mark the event as handled
            event.accept()
            
            # Return early to prevent default behavior
            return
        
        # For all other keys, use the default behavior
        super().keyPressEvent(event)
```

### 2. Create Action Classes

Group related actions into separate files:

```python
# sequence_maker/ui/actions/file_actions.py
from PyQt6.QtWidgets import QAction
from PyQt6.QtGui import QKeySequence

class FileActions:
    """File-related actions for the main window."""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.app = main_window.app
        self._create_actions()
    
    def _create_actions(self):
        """Create file-related actions."""
        # New action
        self.new_action = QAction("&New", self.main_window)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.setStatusTip("Create a new project")
        self.new_action.triggered.connect(self.main_window._on_new)
        
        # Open action
        self.open_action = QAction("&Open...", self.main_window)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.setStatusTip("Open an existing project")
        self.open_action.triggered.connect(self.main_window._on_open)
        
        # Save action
        self.save_action = QAction("&Save", self.main_window)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setStatusTip("Save the current project")
        self.save_action.triggered.connect(self.main_window._on_save)
        
        # Save As action
        self.save_as_action = QAction("Save &As...", self.main_window)
        self.save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_as_action.setStatusTip("Save the current project with a new name")
        self.save_as_action.triggered.connect(self.main_window._on_save_as)
        
        # Load Audio action
        self.load_audio_action = QAction("Load &Audio...", self.main_window)
        self.load_audio_action.setStatusTip("Load an audio file")
        self.load_audio_action.triggered.connect(self.main_window._on_load_audio)
        
        # Export actions
        self.export_json_action = QAction("Export to &JSON...", self.main_window)
        self.export_json_action.setStatusTip("Export timeline to JSON format")
        self.export_json_action.triggered.connect(self.main_window._on_export_json)
        
        self.export_prg_action = QAction("Export to &PRG...", self.main_window)
        self.export_prg_action.setStatusTip("Export timeline to PRG format")
        self.export_prg_action.triggered.connect(self.main_window._on_export_prg)
        
        # Version history action
        self.version_history_action = QAction("&Version History...", self.main_window)
        self.version_history_action.setStatusTip("View and restore previous versions")
        self.version_history_action.triggered.connect(self.main_window._on_version_history)
        
        # Exit action
        self.exit_action = QAction("E&xit", self.main_window)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.setStatusTip("Exit the application")
        self.exit_action.triggered.connect(self.main_window.close)
```

Similar files would be created for other action groups.

### 3. Create Handler Classes

Move handler methods to separate files:

```python
# sequence_maker/ui/handlers/file_handlers.py
from PyQt6.QtWidgets import QFileDialog, QMessageBox

class FileHandlers:
    """File operation handlers for the main window."""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.app = main_window.app
    
    def on_new(self):
        """Create a new project."""
        # Check for unsaved changes
        if not self._check_unsaved_changes():
            return
            
        # Create a new project
        self.app.project_manager.new_project()
        
        # Update UI
        self.main_window._update_ui()
    
    def on_open(self):
        """Open an existing project."""
        # Check for unsaved changes
        if not self._check_unsaved_changes():
            return
            
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Open Project",
            self.app.config.get("general", "default_project_dir"),
            "Sequence Maker Project (*.smproj)"
        )
        
        if file_path:
            # Load project
            self.app.project_manager.load_project(file_path)
            
            # Update UI
            self.main_window._update_ui()
    
    # ... other file operation handlers ...
    
    def _check_unsaved_changes(self):
        """
        Check if there are unsaved changes and prompt the user.
        
        Returns:
            bool: True if it's safe to proceed, False otherwise.
        """
        if not self.app.project_manager.has_unsaved_changes():
            return True
            
        # Show confirmation dialog
        reply = QMessageBox.question(
            self.main_window,
            "Unsaved Changes",
            "There are unsaved changes. Do you want to save them?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )
        
        if reply == QMessageBox.StandardButton.Save:
            # Save changes
            return self.on_save()
        elif reply == QMessageBox.StandardButton.Discard:
            # Discard changes
            return True
        else:
            # Cancel
            return False
```

### 4. Refactor MainWindow Class

Simplify the MainWindow class to use the new components:

```python
# sequence_maker/ui/main_window.py
import logging
from PyQt6.QtWidgets import QMainWindow, QSplitter, QMenuBar, QStatusBar
from PyQt6.QtCore import Qt, QTimer

from ui.widgets.apply_text_edit import ApplyTextEdit
from ui.timeline_widget import TimelineWidget
from ui.ball_widget import BallWidget
from ui.audio_widget import AudioWidget
from ui.lyrics_widget import LyricsWidget

from ui.actions.file_actions import FileActions
from ui.actions.edit_actions import EditActions
from ui.actions.view_actions import ViewActions
from ui.actions.timeline_actions import TimelineActions
from ui.actions.playback_actions import PlaybackActions
from ui.actions.tools_actions import ToolsActions

from ui.handlers.file_handlers import FileHandlers
from ui.handlers.segment_handlers import SegmentHandlers
from ui.handlers.boundary_handlers import BoundaryHandlers
from ui.handlers.utility_handlers import UtilityHandlers

from api.app_context_api import AppContextAPI
from api.timeline_action_api import TimelineActionAPI
from api.audio_action_api import AudioActionAPI

class MainWindow(QMainWindow):
    """Main application window for Sequence Maker."""
    
    def __init__(self, app):
        """Initialize the main window."""
        super().__init__()
        
        self.logger = logging.getLogger("SequenceMaker.MainWindow")
        self.app = app
        
        # Set window properties
        self.setWindowTitle("Sequence Maker")
        self.setMinimumSize(1200, 800)
        
        # Create APIs
        self.context_api = AppContextAPI(app)
        self.timeline_action_api = TimelineActionAPI(app)
        self.audio_action_api = AudioActionAPI(app)
        
        # Create action groups
        self._create_action_groups()
        
        # Create handlers
        self._create_handlers()
        
        # Create UI
        self._create_ui()
        
        # Create menus
        self._create_menus()
        
        # Create toolbars
        self._create_toolbars()
        
        # Create status bar
        self._create_status_bar()
        
        # Connect signals
        self._connect_signals()
        
        # Load settings
        self._load_settings()
        
        # Set up timers
        self._setup_timers()
        
        # Create LLM chat window
        self._create_llm_chat_window()
        
        # Initialize UI state
        self._update_ui()
        
        self.logger.info("Main window initialized")
    
    def _create_action_groups(self):
        """Create action groups."""
        self.file_actions = FileActions(self)
        self.edit_actions = EditActions(self)
        self.view_actions = ViewActions(self)
        self.timeline_actions = TimelineActions(self)
        self.playback_actions = PlaybackActions(self)
        self.tools_actions = ToolsActions(self)
    
    def _create_handlers(self):
        """Create handlers."""
        self.file_handlers = FileHandlers(self)
        self.segment_handlers = SegmentHandlers(self)
        self.boundary_handlers = BoundaryHandlers(self)
        self.utility_handlers = UtilityHandlers(self)
    
    def _create_ui(self):
        """Create the user interface."""
        # ... (simplified UI creation code) ...
    
    # ... (other methods) ...
    
    # Delegate to handlers
    def _on_new(self):
        self.file_handlers.on_new()
    
    def _on_open(self):
        self.file_handlers.on_open()
    
    # ... (other delegated methods) ...
```

### 5. Update Import Statements

Update import statements in all affected files to use the new structure.

## Implementation Plan

1. **Phase 1: Preparation**
   - Create the new directory structure
   - Add `__init__.py` files to make the modules importable

2. **Phase 2: Extract ApplyTextEdit**
   - Move the ApplyTextEdit class to its own file
   - Update imports in main_window.py

3. **Phase 3: Extract Actions**
   - Create action class files
   - Move action creation and related methods
   - Update main_window.py to use the new action classes

4. **Phase 4: Extract Handlers**
   - Create handler class files
   - Move handler methods
   - Update main_window.py to use the new handler classes

5. **Phase 5: Refactor MainWindow**
   - Simplify the MainWindow class
   - Update imports and method calls

6. **Phase 6: Testing**
   - Test each component individually
   - Test the integrated application
   - Fix any issues that arise

## Benefits of This Refactoring

1. **Improved Maintainability**: Smaller files are easier to understand and modify
2. **Better Organization**: Related functionality is grouped together
3. **Enhanced Testability**: Isolated components can be tested independently
4. **Easier Collaboration**: Multiple developers can work on different components
5. **Clearer Responsibilities**: Each class has a single, well-defined purpose
6. **Reduced Cognitive Load**: Developers can focus on one aspect at a time

## Potential Challenges

1. **Circular Dependencies**: May need to carefully manage imports to avoid circular dependencies
2. **Maintaining State**: Ensure state is properly shared between components
3. **Refactoring Effort**: Significant initial effort required
4. **Testing Overhead**: Need to ensure all functionality works after refactoring

## Conclusion

This refactoring plan provides a clear path to breaking down the large main_window.py file into smaller, more manageable components. By following the principles of single responsibility and separation of concerns, we can create a more maintainable and testable codebase.