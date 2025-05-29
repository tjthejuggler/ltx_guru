# Phase 2 Implementation: Enhanced Error Handling

## Overview

This document provides guidance for implementing Phase 2 of the LLM integration for Sequence Maker: Enhanced Error Handling. Phase 1 (Autosave & Version Control) has been successfully completed.

## Implementation Tasks

1. **Update `LLMManager` with ambiguity handling**
   - Add methods to detect ambiguity in LLM responses
   - Implement signal for ambiguity detection
   - Add methods to handle ambiguity resolution

2. **Create `AmbiguityResolutionDialog` class**
   - Create a new dialog in `sequence_maker/ui/dialogs/ambiguity_resolution_dialog.py`
   - Implement UI for displaying ambiguous instructions
   - Add options for user to clarify or choose from suggestions
   - Include feedback mechanism for improving future interactions

3. **Integrate with `LLMChatDialog`**
   - Update `LLMChatDialog` to handle ambiguity signals
   - Show the ambiguity resolution dialog when needed
   - Process user clarifications and send back to LLM

4. **Add comprehensive tests**
   - Create tests for ambiguity detection in `LLMManager`
   - Create tests for the `AmbiguityResolutionDialog`
   - Test integration with `LLMChatDialog`

## Implementation Details

### 1. Ambiguity Detection in `LLMManager`

The `LLMManager` should be updated to detect potential ambiguity in LLM responses. This can be done by:

```python
def _handle_ambiguity(self, prompt, response):
    """Handle ambiguous instructions."""
    # Check for ambiguity markers in response
    if "ambiguous" in response.lower() or "unclear" in response.lower():
        # Log ambiguity
        self.logger.warning(f"Ambiguous instruction: {prompt}")
        
        # Extract suggestions from response
        suggestions = self._extract_suggestions(response)
        
        # Emit ambiguity signal
        self.llm_ambiguity.emit(prompt, suggestions)
        
        return True
    
    return False

def _extract_suggestions(self, response):
    """Extract suggestions from an ambiguous response."""
    suggestions = []
    
    # Look for numbered or bulleted lists
    import re
    
    # Match numbered lists (1. Option one)
    numbered_pattern = r"\d+\.\s+(.*?)(?=\n\d+\.|\n\n|$)"
    numbered_matches = re.findall(numbered_pattern, response, re.DOTALL)
    
    # Match bulleted lists (- Option one or * Option one)
    bulleted_pattern = r"[-*]\s+(.*?)(?=\n[-*]|\n\n|$)"
    bulleted_matches = re.findall(bulleted_pattern, response, re.DOTALL)
    
    # Combine matches
    matches = numbered_matches + bulleted_matches
    
    # Add unique suggestions
    for match in matches:
        suggestion = match.strip()
        if suggestion and suggestion not in suggestions:
            suggestions.append(suggestion)
    
    return suggestions
```

### 2. `AmbiguityResolutionDialog` Class

Create a new dialog class in `sequence_maker/ui/dialogs/ambiguity_resolution_dialog.py`:

```python
class AmbiguityResolutionDialog(QDialog):
    """Dialog for resolving ambiguous instructions."""
    
    resolution_selected = pyqtSignal(str)
    
    def __init__(self, prompt, suggestions, parent=None):
        """
        Initialize the ambiguity resolution dialog.
        
        Args:
            prompt (str): The original prompt.
            suggestions (list): List of suggested clarifications.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.AmbiguityResolutionDialog")
        self.prompt = prompt
        self.suggestions = suggestions
        
        # Set dialog properties
        self.setWindowTitle("Clarify Instructions")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create header
        self.header_label = QLabel("Please clarify your instructions")
        self.header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.main_layout.addWidget(self.header_label)
        
        # Create description
        self.description_label = QLabel(
            "Your instructions were a bit ambiguous. Please select one of the following options or provide a clarification."
        )
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)
        
        # Create prompt display
        self.prompt_label = QLabel("Your original instruction:")
        self.main_layout.addWidget(self.prompt_label)
        
        self.prompt_text = QTextEdit()
        self.prompt_text.setReadOnly(True)
        self.prompt_text.setText(self.prompt)
        self.prompt_text.setMaximumHeight(80)
        self.main_layout.addWidget(self.prompt_text)
        
        # Create suggestions list
        self.suggestions_label = QLabel("Suggested clarifications:")
        self.main_layout.addWidget(self.suggestions_label)
        
        self.suggestions_list = QListWidget()
        for suggestion in self.suggestions:
            item = QListWidgetItem(suggestion)
            self.suggestions_list.addItem(item)
        self.main_layout.addWidget(self.suggestions_list)
        
        # Create custom clarification input
        self.custom_label = QLabel("Or provide your own clarification:")
        self.main_layout.addWidget(self.custom_label)
        
        self.custom_text = QTextEdit()
        self.custom_text.setMaximumHeight(80)
        self.main_layout.addWidget(self.custom_text)
        
        # Create button layout
        self.button_layout = QHBoxLayout()
        
        # Create select button
        self.select_button = QPushButton("Use Selected")
        self.select_button.clicked.connect(self._on_select_clicked)
        self.button_layout.addWidget(self.select_button)
        
        # Create custom button
        self.custom_button = QPushButton("Use Custom")
        self.custom_button.clicked.connect(self._on_custom_clicked)
        self.button_layout.addWidget(self.custom_button)
        
        # Create cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)
        
        self.main_layout.addLayout(self.button_layout)
    
    def _on_select_clicked(self):
        """Handle Select button click."""
        # Get selected item
        selected_items = self.suggestions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self,
                "No Suggestion Selected",
                "Please select a suggestion or provide a custom clarification."
            )
            return
        
        # Get selected suggestion
        suggestion = selected_items[0].text()
        
        # Emit signal
        self.resolution_selected.emit(suggestion)
        
        # Accept dialog
        self.accept()
    
    def _on_custom_clicked(self):
        """Handle Custom button click."""
        # Get custom text
        custom_text = self.custom_text.toPlainText().strip()
        if not custom_text:
            QMessageBox.warning(
                self,
                "No Custom Clarification",
                "Please enter a custom clarification or select a suggestion."
            )
            return
        
        # Emit signal
        self.resolution_selected.emit(custom_text)
        
        # Accept dialog
        self.accept()
```

### 3. Integration with `LLMChatDialog`

Update the `LLMChatDialog` class to handle ambiguity signals:

```python
# Add to __init__
self.app.llm_manager.llm_ambiguity.connect(self._on_llm_ambiguity)

# Add new method
def _on_llm_ambiguity(self, prompt, suggestions):
    """
    Handle LLM ambiguity.
    
    Args:
        prompt (str): The original prompt.
        suggestions (list): List of suggested clarifications.
    """
    # Create and show ambiguity resolution dialog
    dialog = AmbiguityResolutionDialog(prompt, suggestions, self)
    
    # Connect resolution signal
    dialog.resolution_selected.connect(self._on_ambiguity_resolved)
    
    # Show dialog
    dialog.exec()

def _on_ambiguity_resolved(self, resolution):
    """
    Handle ambiguity resolution.
    
    Args:
        resolution (str): The selected or custom resolution.
    """
    # Add resolution to chat history
    self._add_message("You (clarification)", resolution)
    
    # Send resolution to LLM
    self._on_send_clicked(resolution)
```

## Testing Strategy

1. **Unit Tests**
   - Test ambiguity detection in `LLMManager`
   - Test suggestion extraction from ambiguous responses
   - Test `AmbiguityResolutionDialog` UI and signals

2. **Integration Tests**
   - Test the full ambiguity resolution workflow
   - Test integration with `LLMChatDialog`

3. **User Acceptance Testing**
   - Test with real LLM providers
   - Verify ambiguity detection and resolution

## Next Steps After Completion

After completing Phase 2, update the `llm_integration_status.md` and `llm_integration_next_steps.md` files to reflect the progress and prepare for Phase 3: Audio Analysis Integration.