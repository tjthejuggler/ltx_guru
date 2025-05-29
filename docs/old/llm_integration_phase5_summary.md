# LLM Integration Phase 5: User Customization

This document outlines the implementation plan for Phase 5 of the LLM integration for Sequence Maker, focusing on user customization.

## 1. Overview

Phase 5 will enhance the LLM integration by allowing users to customize the LLM's behavior and responses. This will make the LLM more adaptable to different user preferences and workflows.

## 2. Components to Implement

### 2.1. Custom Instructions

- Allow users to define custom system instructions for the LLM
- Create a UI for editing and managing custom instructions
- Store custom instructions in project settings
- Apply custom instructions to LLM requests

### 2.2. LLM Presets

- Create a preset system for LLM configurations
- Allow users to save and load presets
- Include model, temperature, max tokens, and other parameters in presets
- Provide default presets for common use cases

### 2.3. Task Templates

- Implement templates for common LLM tasks
- Create a UI for managing templates
- Allow users to create, edit, and delete templates
- Apply templates to LLM requests

## 3. Implementation Details

### 3.1. Custom Instructions UI

```python
class CustomInstructionsDialog(QDialog):
    """Dialog for editing custom LLM instructions."""
    
    def __init__(self, app, parent=None):
        super().__init__(parent)
        
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.CustomInstructionsDialog")
        
        # Set dialog properties
        self.setWindowTitle("Custom LLM Instructions")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        # Create UI
        self._create_ui()
        
        # Load current instructions
        self._load_instructions()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create header
        self.header_label = QLabel("Custom LLM Instructions")
        self.header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.main_layout.addWidget(self.header_label)
        
        # Create description
        self.description_label = QLabel(
            "Define custom instructions for the LLM. These instructions will be included in the system message."
        )
        self.main_layout.addWidget(self.description_label)
        
        # Create instructions editor
        self.instructions_editor = QTextEdit()
        self.instructions_editor.setPlaceholderText("Enter custom instructions here...")
        self.main_layout.addWidget(self.instructions_editor)
        
        # Create button layout
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        
        # Create save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._on_save)
        self.button_layout.addWidget(self.save_button)
        
        # Create reset button
        self.reset_button = QPushButton("Reset to Default")
        self.reset_button.clicked.connect(self._on_reset)
        self.button_layout.addWidget(self.reset_button)
        
        # Create cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)
    
    def _load_instructions(self):
        """Load current custom instructions."""
        if self.app.project_manager.current_project:
            instructions = getattr(self.app.project_manager.current_project, "llm_custom_instructions", "")
            self.instructions_editor.setPlainText(instructions)
    
    def _on_save(self):
        """Handle Save button click."""
        if self.app.project_manager.current_project:
            # Get instructions
            instructions = self.instructions_editor.toPlainText()
            
            # Save to project
            self.app.project_manager.current_project.llm_custom_instructions = instructions
            
            # Mark project as changed
            self.app.project_manager.project_changed.emit()
            
            # Accept dialog
            self.accept()
    
    def _on_reset(self):
        """Handle Reset button click."""
        # Set default instructions
        default_instructions = (
            "You are an assistant that helps create color sequences for juggling balls. "
            "You can analyze music and suggest color patterns that match the rhythm, mood, and style of the music. "
            "Your responses should be clear and specific, describing exact colors and timings."
        )
        
        # Set in editor
        self.instructions_editor.setPlainText(default_instructions)
```

### 3.2. LLM Presets Implementation

```python
class LLMPreset:
    """Class representing an LLM configuration preset."""
    
    def __init__(self, name, provider, model, temperature, max_tokens, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
        """
        Initialize the LLM preset.
        
        Args:
            name (str): Preset name.
            provider (str): LLM provider (openai, anthropic, local).
            model (str): Model name.
            temperature (float): Temperature parameter.
            max_tokens (int): Maximum tokens in the response.
            top_p (float, optional): Top-p parameter. Default is 1.0.
            frequency_penalty (float, optional): Frequency penalty parameter. Default is 0.0.
            presence_penalty (float, optional): Presence penalty parameter. Default is 0.0.
        """
        self.name = name
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
    
    def to_dict(self):
        """Convert preset to dictionary."""
        return {
            "name": self.name,
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create preset from dictionary."""
        return cls(
            name=data.get("name", "Unnamed"),
            provider=data.get("provider", "openai"),
            model=data.get("model", "gpt-3.5-turbo"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 1024),
            top_p=data.get("top_p", 1.0),
            frequency_penalty=data.get("frequency_penalty", 0.0),
            presence_penalty=data.get("presence_penalty", 0.0)
        )
```

### 3.3. Task Templates Implementation

```python
class LLMTaskTemplate:
    """Class representing an LLM task template."""
    
    def __init__(self, name, prompt, description=""):
        """
        Initialize the LLM task template.
        
        Args:
            name (str): Template name.
            prompt (str): Template prompt.
            description (str, optional): Template description. Default is empty.
        """
        self.name = name
        self.prompt = prompt
        self.description = description
    
    def to_dict(self):
        """Convert template to dictionary."""
        return {
            "name": self.name,
            "prompt": self.prompt,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create template from dictionary."""
        return cls(
            name=data.get("name", "Unnamed"),
            prompt=data.get("prompt", ""),
            description=data.get("description", "")
        )
```

## 4. Integration with Existing Components

### 4.1. LLM Chat Window Updates

- Add preset selection dropdown to the LLM chat window
- Add template selection dropdown to the LLM chat window
- Add button to open custom instructions dialog
- Update system message creation to include custom instructions

### 4.2. Settings Dialog Updates

- Add tab for managing LLM presets
- Add tab for managing task templates
- Add UI for importing and exporting presets and templates

### 4.3. Project Model Updates

- Add fields for storing custom instructions, presets, and templates
- Update serialization and deserialization methods

## 5. Testing

- Add tests for custom instructions functionality
- Add tests for preset management
- Add tests for template management
- Add integration tests for the updated LLM chat window

## 6. Documentation

- Update user documentation with information about customization features
- Add examples of common custom instructions, presets, and templates
- Provide guidelines for creating effective custom instructions