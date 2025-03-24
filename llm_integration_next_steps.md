# LLM Integration: Detailed Implementation Plan for Remaining Components

This document provides a detailed implementation plan for the remaining components of the LLM integration for Sequence Maker.

## 1. Autosave & Version Control

### 1.1. AutosaveManager Class

Create a new class `AutosaveManager` in `sequence_maker/managers/autosave_manager.py`:

```python
import logging
import os
import json
import shutil
from datetime import datetime
from pathlib import Path

class AutosaveManager:
    """Manager for automatic project state saves and version control."""
    
    def __init__(self, app):
        """
        Initialize the autosave manager.
        
        Args:
            app: The main application instance.
        """
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.AutosaveManager")
        self.max_versions = app.config.get("general", "max_autosave_files", 10)
        self.autosave_dir = None
        
        # Create autosave directory if it doesn't exist
        self._ensure_autosave_directory()
    
    def _ensure_autosave_directory(self):
        """Ensure the autosave directory exists."""
        if not self.app.project_manager.current_project or not self.app.project_manager.current_project.file_path:
            return
            
        # Create autosave directory next to the project file
        project_path = Path(self.app.project_manager.current_project.file_path)
        self.autosave_dir = project_path.parent / f"{project_path.stem}_versions"
        self.autosave_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"Autosave directory: {self.autosave_dir}")
    
    def save_version(self, reason="LLM Operation"):
        """
        Save a version of the current project.
        
        Args:
            reason (str): Reason for saving the version.
        
        Returns:
            bool: True if the version was saved, False otherwise.
        """
        if not self.app.project_manager.current_project or not self.app.project_manager.current_project.file_path:
            return False
            
        # Ensure autosave directory exists
        self._ensure_autosave_directory()
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create version name
        version_name = f"{timestamp}_{reason.replace(' ', '_')}"
        
        # Create version file path
        version_path = self.autosave_dir / f"{version_name}.json"
        
        # Save project to version file
        try:
            # Get project data
            project_data = self.app.project_manager.current_project.to_dict()
            
            # Add version metadata
            project_data["version_metadata"] = {
                "timestamp": timestamp,
                "reason": reason,
                "original_file": self.app.project_manager.current_project.file_path
            }
            
            # Write to file
            with open(version_path, "w") as f:
                json.dump(project_data, f, indent=2)
            
            self.logger.info(f"Saved version: {version_path}")
            
            # Prune old versions if needed
            self._prune_old_versions()
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving version: {e}")
            return False
    
    def _prune_old_versions(self):
        """Remove old versions if max_versions is exceeded."""
        if not self.autosave_dir or not self.autosave_dir.exists():
            return
            
        # Get all version files
        version_files = sorted(self.autosave_dir.glob("*.json"))
        
        # Check if we need to prune
        if len(version_files) <= self.max_versions:
            return
            
        # Remove oldest versions
        versions_to_remove = version_files[:-self.max_versions]
        for version_file in versions_to_remove:
            try:
                version_file.unlink()
                self.logger.info(f"Removed old version: {version_file}")
            except Exception as e:
                self.logger.error(f"Error removing old version: {e}")
    
    def get_versions(self):
        """
        Get a list of available versions.
        
        Returns:
            list: List of version dictionaries with metadata.
        """
        if not self.autosave_dir or not self.autosave_dir.exists():
            return []
            
        # Get all version files
        version_files = sorted(self.autosave_dir.glob("*.json"), reverse=True)
        
        versions = []
        for version_file in version_files:
            try:
                # Read version metadata
                with open(version_file, "r") as f:
                    data = json.load(f)
                    
                metadata = data.get("version_metadata", {})
                versions.append({
                    "file_path": str(version_file),
                    "timestamp": metadata.get("timestamp", ""),
                    "reason": metadata.get("reason", ""),
                    "file_name": version_file.name
                })
            except Exception as e:
                self.logger.error(f"Error reading version metadata: {e}")
        
        return versions
    
    def restore_version(self, version_path):
        """
        Restore a project version.
        
        Args:
            version_path (str): Path to the version file.
        
        Returns:
            bool: True if the version was restored, False otherwise.
        """
        try:
            # Save current state before restoring
            self.save_version("Before Restore")
            
            # Load version
            with open(version_path, "r") as f:
                version_data = json.load(f)
            
            # Remove version metadata
            if "version_metadata" in version_data:
                del version_data["version_metadata"]
            
            # Load project from version data
            project = self.app.project_manager.load_from_dict(version_data)
            
            # Set current project
            self.app.project_manager.set_current_project(project)
            
            self.logger.info(f"Restored version: {version_path}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error restoring version: {e}")
            return False
```

### 1.2. VersionHistoryDialog Class

Create a new dialog class `VersionHistoryDialog` in `sequence_maker/ui/dialogs/version_history_dialog.py`:

```python
import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

class VersionHistoryDialog(QDialog):
    """Dialog for browsing and restoring project versions."""
    
    version_selected = pyqtSignal(str)
    
    def __init__(self, app, parent=None):
        """
        Initialize the version history dialog.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.VersionHistoryDialog")
        self.app = app
        
        # Set dialog properties
        self.setWindowTitle("Version History")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        # Create UI
        self._create_ui()
        
        # Load versions
        self._load_versions()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create header
        self.header_label = QLabel("Project Version History")
        self.header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.main_layout.addWidget(self.header_label)
        
        # Create description
        self.description_label = QLabel(
            "Select a version to restore. A backup of the current state will be created before restoring."
        )
        self.main_layout.addWidget(self.description_label)
        
        # Create version list
        self.version_list = QListWidget()
        self.version_list.setAlternatingRowColors(True)
        self.version_list.itemDoubleClicked.connect(self._on_version_double_clicked)
        self.main_layout.addWidget(self.version_list)
        
        # Create button layout
        self.button_layout = QHBoxLayout()
        
        # Create restore button
        self.restore_button = QPushButton("Restore Selected Version")
        self.restore_button.clicked.connect(self._on_restore_clicked)
        self.button_layout.addWidget(self.restore_button)
        
        # Create refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._load_versions)
        self.button_layout.addWidget(self.refresh_button)
        
        # Create close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.close_button)
        
        self.main_layout.addLayout(self.button_layout)
    
    def _load_versions(self):
        """Load available versions."""
        # Clear list
        self.version_list.clear()
        
        # Get versions
        versions = self.app.autosave_manager.get_versions()
        
        # Add versions to list
        for version in versions:
            # Create item
            item = QListWidgetItem()
            
            # Format timestamp
            timestamp = version.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                    timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            # Set text
            item.setText(f"{timestamp} - {version.get('reason', 'Unknown')}")
            
            # Store file path
            item.setData(Qt.ItemDataRole.UserRole, version.get("file_path", ""))
            
            # Add to list
            self.version_list.addItem(item)
    
    def _on_version_double_clicked(self, item):
        """
        Handle version double click.
        
        Args:
            item: The clicked item.
        """
        # Get version path
        version_path = item.data(Qt.ItemDataRole.UserRole)
        
        # Confirm restore
        result = QMessageBox.question(
            self,
            "Restore Version",
            "Are you sure you want to restore this version? A backup of the current state will be created.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Restore version
            self._restore_version(version_path)
    
    def _on_restore_clicked(self):
        """Handle Restore button click."""
        # Get selected item
        selected_items = self.version_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self,
                "No Version Selected",
                "Please select a version to restore."
            )
            return
        
        # Get version path
        version_path = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # Confirm restore
        result = QMessageBox.question(
            self,
            "Restore Version",
            "Are you sure you want to restore this version? A backup of the current state will be created.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Restore version
            self._restore_version(version_path)
    
    def _restore_version(self, version_path):
        """
        Restore a version.
        
        Args:
            version_path (str): Path to the version file.
        """
        # Restore version
        success = self.app.autosave_manager.restore_version(version_path)
        
        if success:
            QMessageBox.information(
                self,
                "Version Restored",
                "The selected version has been restored successfully."
            )
            
            # Close dialog
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Restore Failed",
                "Failed to restore the selected version."
            )
```

## 2. Implementation Order and Timeline

### 2.1. Phase 1: Autosave & Version Control (COMPLETED)
1. ✅ Created `AutosaveManager` class
2. ✅ Created `VersionHistoryDialog` class
3. ✅ Integrated with `LLMManager` and `MainWindow`
4. ✅ Added tests for version creation and restoration

### 2.2. Phase 2: Enhanced Error Handling (COMPLETED)
1. ✅ Updated `LLMManager` with ambiguity handling
2. ✅ Created `AmbiguityResolutionDialog` class
3. ✅ Integrated with `LLMChatDialog`
4. ✅ Added tests for ambiguity detection and resolution

### 2.3. Phase 3: Audio Analysis Integration (COMPLETED)
1. ✅ Updated `AudioManager` with analysis methods
2. ✅ Updated `AppContextAPI` to include analysis data
3. ✅ Added tests for audio analysis and data extraction
4. ✅ Integrated with LLM system messages

### 2.4. Phase 4: Floating Chat Window (COMPLETED)
1. ✅ Created `LLMChatWindow` class
2. ✅ Updated `MainWindow` to use floating window
3. ✅ Added tests for window functionality
4. ✅ Updated documentation

## 3. Next Implementation: Function Calling Integration

With the Enhanced Logging and Diagnostics now implemented, the next phase to focus on is Function Calling Integration. This will involve:

1. Implementing OpenAI function calling for more structured interactions
2. Creating function schemas for common operations
3. Adding support for streaming responses
4. Enhancing the UI to display structured responses

This implementation will improve the reliability and effectiveness of the LLM integration by providing more structured interactions and better response handling.

### 3.1. Function Calling Implementation

Update the `LLMManager` class to support OpenAI function calling:

```python
def _send_openai_request_with_functions(self, prompt, system_message, temperature, max_tokens, functions):
    """
    Send a request to the OpenAI API with function calling.
    
    Args:
        prompt (str): User prompt.
        system_message (str): System message.
        temperature (float): Temperature parameter.
        max_tokens (int): Maximum tokens in the response.
        functions (list): List of function definitions.
    
    Returns:
        dict: API response, or None if the request failed.
    """
    self.logger.info("Sending request to OpenAI API with function calling")
    
    try:
        # Prepare request
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "functions": functions,
            "function_call": "auto",
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Send request
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        # Check for errors
        response.raise_for_status()
        
        # Parse response
        return response.json()
    
    except Exception as e:
        self.logger.error(f"Error in OpenAI function calling request: {e}")
        raise
```

### 3.2. Function Schemas

Create function schemas for common operations:

```python
# Timeline function schemas
TIMELINE_FUNCTIONS = [
    {
        "name": "create_segment",
        "description": "Create a new segment in a timeline",
        "parameters": {
            "type": "object",
            "properties": {
                "timeline_index": {
                    "type": "integer",
                    "description": "Index of the timeline to add the segment to"
                },
                "start_time": {
                    "type": "number",
                    "description": "Start time of the segment in seconds"
                },
                "end_time": {
                    "type": "number",
                    "description": "End time of the segment in seconds"
                },
                "color": {
                    "type": "array",
                    "description": "RGB color values (0-255)",
                    "items": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 255
                    },
                    "minItems": 3,
                    "maxItems": 3
                }
            },
            "required": ["timeline_index", "start_time", "end_time", "color"]
        }
    },
    {
        "name": "delete_segment",
        "description": "Delete a segment from a timeline",
        "parameters": {
            "type": "object",
            "properties": {
                "timeline_index": {
                    "type": "integer",
                    "description": "Index of the timeline containing the segment"
                },
                "segment_index": {
                    "type": "integer",
                    "description": "Index of the segment to delete"
                }
            },
            "required": ["timeline_index", "segment_index"]
        }
    },
    {
        "name": "modify_segment",
        "description": "Modify an existing segment in a timeline",
        "parameters": {
            "type": "object",
            "properties": {
                "timeline_index": {
                    "type": "integer",
                    "description": "Index of the timeline containing the segment"
                },
                "segment_index": {
                    "type": "integer",
                    "description": "Index of the segment to modify"
                },
                "start_time": {
                    "type": "number",
                    "description": "New start time of the segment in seconds"
                },
                "end_time": {
                    "type": "number",
                    "description": "New end time of the segment in seconds"
                },
                "color": {
                    "type": "array",
                    "description": "New RGB color values (0-255)",
                    "items": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 255
                    },
                    "minItems": 3,
                    "maxItems": 3
                }
            },
            "required": ["timeline_index", "segment_index"]
        }
    }
]

# Audio function schemas
AUDIO_FUNCTIONS = [
    {
        "name": "play_audio",
        "description": "Play the loaded audio file",
        "parameters": {
            "type": "object",
            "properties": {
                "start_time": {
                    "type": "number",
                    "description": "Start time in seconds (optional)"
                }
            }
        }
    },
    {
        "name": "pause_audio",
        "description": "Pause audio playback",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "stop_audio",
        "description": "Stop audio playback",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]
```

### 3.3. Function Call Handling

Add methods to handle function calls:

```python
def _handle_function_call(self, response):
    """
    Handle a function call from the LLM.
    
    Args:
        response (dict): API response containing a function call.
    
    Returns:
        dict: Result of the function call.
    """
    try:
        # Extract function call
        message = response["choices"][0]["message"]
        function_call = message.get("function_call")
        
        if not function_call:
            return {"success": False, "error": "No function call in response"}
        
        # Extract function name and arguments
        function_name = function_call.get("name")
        arguments_str = function_call.get("arguments", "{}")
        
        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid function arguments: {arguments_str}"}
        
        # Log function call
        self.logger.info(f"Function call: {function_name}({arguments})")
        
        # Execute function
        result = self.execute_action(function_name, arguments)
        
        return result
    
    except Exception as e:
        self.logger.error(f"Error handling function call: {e}")
        return {"success": False, "error": str(e)}
```

### 3.4. Streaming Response Support

Add support for streaming responses:

```python
def _send_openai_streaming_request(self, prompt, system_message, temperature, max_tokens):
    """
    Send a streaming request to the OpenAI API.
    
    Args:
        prompt (str): User prompt.
        system_message (str): System message.
        temperature (float): Temperature parameter.
        max_tokens (int): Maximum tokens in the response.
    
    Yields:
        str: Chunks of the response text.
    """
    self.logger.info("Sending streaming request to OpenAI API")
    
    try:
        # Prepare request
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        # Send request
        response = requests.post(url, headers=headers, json=data, stream=True, timeout=60)
        
        # Check for errors
        response.raise_for_status()
        
        # Process streaming response
        for line in response.iter_lines():
            if line:
                # Remove "data: " prefix
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    line = line[6:]
                
                # Skip "[DONE]" message
                if line == "[DONE]":
                    break
                
                try:
                    # Parse JSON
                    chunk = json.loads(line)
                    
                    # Extract content
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue
    
    except Exception as e:
        self.logger.error(f"Error in OpenAI streaming request: {e}")
        yield f"Error: {str(e)}"
```

### 3.5. UI Updates for Structured Responses

Update the `LLMChatWindow` class to display structured responses:

```python
def _display_function_call(self, function_name, arguments, result):
    """
    Display a function call in the chat window.
    
    Args:
        function_name (str): Name of the function.
        arguments (dict): Function arguments.
        result (dict): Result of the function call.
    """
    # Create function call HTML
    html = f"""
    <div class="function-call">
        <div class="function-header">Function Call: <span class="function-name">{function_name}</span></div>
        <div class="function-arguments">
            <pre>{json.dumps(arguments, indent=2)}</pre>
        </div>
        <div class="function-result">
            <div class="result-header">Result:</div>
            <pre>{json.dumps(result, indent=2)}</pre>
        </div>
    </div>
    """
    
    # Add to chat history
    self._add_html_to_chat(html)
```

### 3.1. Enhanced Logging Implementation

The logging system should be enhanced to provide more detailed information about LLM operations:

```python
# Add to LLMManager class
def _log_request_details(self, prompt, system_message, temperature, max_tokens):
    """
    Log detailed information about an LLM request.
    
    Args:
        prompt (str): User prompt.
        system_message (str): System message.
        temperature (float): Temperature parameter.
        max_tokens (int): Maximum tokens in the response.
    """
    self.logger.info(f"LLM Request Details:")
    self.logger.info(f"Provider: {self.provider}")
    self.logger.info(f"Model: {self.model}")
    self.logger.info(f"Temperature: {temperature}")
    self.logger.info(f"Max Tokens: {max_tokens}")
    self.logger.info(f"Prompt Length: {len(prompt)} characters")
    self.logger.info(f"System Message Length: {len(system_message)} characters")
    
    # Log truncated versions of prompt and system message
    max_log_length = 100
    prompt_truncated = prompt[:max_log_length] + "..." if len(prompt) > max_log_length else prompt
    system_truncated = system_message[:max_log_length] + "..." if len(system_message) > max_log_length else system_message
    
    self.logger.info(f"Prompt (truncated): {prompt_truncated}")
    self.logger.info(f"System Message (truncated): {system_truncated}")
```

### 3.2. Performance Metrics Tracking

Add performance metrics tracking to measure response times and other performance indicators:

```python
# Add to LLMManager class
def _track_performance_metrics(self, start_time, end_time, prompt_length, response_length, tokens):
    """
    Track performance metrics for an LLM request.
    
    Args:
        start_time (float): Request start time.
        end_time (float): Request end time.
        prompt_length (int): Length of the prompt in characters.
        response_length (int): Length of the response in characters.
        tokens (int): Number of tokens used.
    """
    duration = end_time - start_time
    
    # Log metrics
    self.logger.info(f"LLM Request Performance Metrics:")
    self.logger.info(f"Duration: {duration:.2f} seconds")
    self.logger.info(f"Tokens: {tokens}")
    self.logger.info(f"Tokens per second: {tokens / duration:.2f}")
    self.logger.info(f"Characters per second: {response_length / duration:.2f}")
    
    # Store metrics in project metadata
    if self.app.project_manager.current_project:
        if not hasattr(self.app.project_manager.current_project, "llm_performance_metrics"):
            self.app.project_manager.current_project.llm_performance_metrics = []
        
        self.app.project_manager.current_project.llm_performance_metrics.append({
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "tokens": tokens,
            "prompt_length": prompt_length,
            "response_length": response_length,
            "tokens_per_second": tokens / duration,
            "characters_per_second": response_length / duration,
            "model": self.model,
            "provider": self.provider
        })
        
        # Mark project as changed
        self.app.project_manager.project_changed.emit()
```

### 3.3. Diagnostic Tools

Create a diagnostic dialog to display LLM performance metrics and other diagnostic information:

```python
class LLMDiagnosticsDialog(QDialog):
    """Dialog for displaying LLM diagnostics."""
    
    def __init__(self, app, parent=None):
        """
        Initialize the LLM diagnostics dialog.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.app = app
        
        # Set dialog properties
        self.setWindowTitle("LLM Diagnostics")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Create UI
        self._create_ui()
        
        # Load metrics
        self._load_metrics()
    
    def _create_ui(self):
        """Create the user interface."""
        # Implementation details...
```
