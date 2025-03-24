# LLM Integration: Detailed Implementation Plan for Remaining Components

This document provides a detailed implementation plan for the remaining components of the LLM integration for Sequence Maker.

## 1. Completed Phases

### 1.1. Phase 1: Autosave & Version Control (COMPLETED)
1. ✅ Created `AutosaveManager` class
2. ✅ Created `VersionHistoryDialog` class
3. ✅ Integrated with `LLMManager` and `MainWindow`
4. ✅ Added tests for version creation and restoration

### 1.2. Phase 2: Enhanced Error Handling (COMPLETED)
1. ✅ Updated `LLMManager` with ambiguity handling
2. ✅ Created `AmbiguityResolutionDialog` class
3. ✅ Integrated with `LLMChatDialog`
4. ✅ Added tests for ambiguity detection and resolution

### 1.3. Phase 3: Audio Analysis Integration (COMPLETED)
1. ✅ Updated `AudioManager` with analysis methods
2. ✅ Updated `AppContextAPI` to include analysis data
3. ✅ Added tests for audio analysis and data extraction
4. ✅ Integrated with LLM system messages

### 1.4. Phase 4: Floating Chat Window (COMPLETED)
1. ✅ Created `LLMChatWindow` class
2. ✅ Updated `MainWindow` to use floating window
3. ✅ Added tests for window functionality
4. ✅ Updated documentation

### 1.5. Phase 5: Function Calling Integration (COMPLETED)
1. ✅ Implemented OpenAI function calling for more structured interactions
2. ✅ Created function schemas for timeline and audio operations
3. ✅ Added support for streaming responses
4. ✅ Enhanced the UI to display structured responses
5. ✅ Created LLM diagnostics dialog for performance monitoring

### 1.6. Phase 6: User Customization (COMPLETED)
1. ✅ Created `CustomInstructionsDialog` for editing custom LLM instructions
2. ✅ Implemented `LLMPreset` class for representing configuration presets
3. ✅ Created `LLMPresetsDialog` for managing presets
4. ✅ Implemented `LLMTaskTemplate` class for representing task templates
5. ✅ Created `TaskTemplatesDialog` for managing templates
6. ✅ Updated `Project` model to store custom instructions, presets, and templates
7. ✅ Enhanced `LLMChatWindow` to support customization features
8. ✅ Updated `SettingsDialog` with customization options
9. ✅ Added tests for customization features

## 2. Next Implementation: Advanced Integration Features

The next phase to focus on is Advanced Integration Features. This will involve:

1. Implementing a plugin system for extending LLM capabilities
2. Adding support for multi-modal inputs (images, audio clips)
3. Creating a feedback system for improving LLM responses
4. Implementing collaborative features for sharing presets and templates

This implementation will further enhance the LLM integration by making it more extensible and capable of handling more complex use cases.

### 2.1. Plugin System Implementation

Create a plugin system for extending LLM capabilities:

```python
class LLMPlugin:
    """Base class for LLM plugins."""
    
    def __init__(self, name, description=""):
        """
        Initialize the LLM plugin.
        
        Args:
            name (str): Plugin name.
            description (str, optional): Plugin description. Default is empty.
        """
        self.name = name
        self.description = description
    
    def get_system_message_extension(self):
        """
        Get the extension to add to the system message.
        
        Returns:
            str: Extension to add to the system message.
        """
        return ""
    
    def process_prompt(self, prompt):
        """
        Process the prompt before sending it to the LLM.
        
        Args:
            prompt (str): User prompt.
        
        Returns:
            str: Processed prompt.
        """
        return prompt
    
    def process_response(self, response):
        """
        Process the response from the LLM.
        
        Args:
            response (str): LLM response.
        
        Returns:
            str: Processed response.
        """
        return response
```

### 2.2. Multi-Modal Input Implementation

Add support for multi-modal inputs:

```python
class MultiModalInput:
    """Class for handling multi-modal inputs."""
    
    def __init__(self, app):
        """
        Initialize the multi-modal input handler.
        
        Args:
            app: The main application instance.
        """
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.MultiModalInput")
    
    def process_image(self, image_path):
        """
        Process an image for LLM input.
        
        Args:
            image_path (str): Path to the image file.
        
        Returns:
            str: Base64-encoded image data.
        """
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
                return base64.b64encode(image_data).decode("utf-8")
        except Exception as e:
            self.logger.error(f"Error processing image: {e}")
            return None
    
    def process_audio_clip(self, audio_path, max_duration=30):
        """
        Process an audio clip for LLM input.
        
        Args:
            audio_path (str): Path to the audio file.
            max_duration (int, optional): Maximum duration in seconds. Default is 30.
        
        Returns:
            str: Base64-encoded audio data.
        """
        try:
            # Load audio file
            audio_data, sample_rate = librosa.load(audio_path, sr=None, duration=max_duration)
            
            # Convert to WAV format
            wav_data = io.BytesIO()
            sf.write(wav_data, audio_data, sample_rate, format="WAV")
            wav_data.seek(0)
            
            # Encode as base64
            return base64.b64encode(wav_data.read()).decode("utf-8")
        except Exception as e:
            self.logger.error(f"Error processing audio clip: {e}")
            return None
```

### 2.3. Feedback System Implementation

Create a feedback system for improving LLM responses:

```python
class LLMFeedbackSystem:
    """Class for collecting and managing LLM feedback."""
    
    def __init__(self, app):
        """
        Initialize the LLM feedback system.
        
        Args:
            app: The main application instance.
        """
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.LLMFeedbackSystem")
        
        # Create feedback database
        self.feedback_db = {}
    
    def add_feedback(self, prompt, response, rating, comment=""):
        """
        Add feedback for an LLM interaction.
        
        Args:
            prompt (str): User prompt.
            response (str): LLM response.
            rating (int): Rating (1-5).
            comment (str, optional): User comment. Default is empty.
        
        Returns:
            bool: True if feedback was added successfully, False otherwise.
        """
        try:
            # Generate unique ID for the interaction
            interaction_id = str(uuid.uuid4())
            
            # Add feedback to database
            self.feedback_db[interaction_id] = {
                "prompt": prompt,
                "response": response,
                "rating": rating,
                "comment": comment,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save feedback to file
            self._save_feedback()
            
            return True
        except Exception as e:
            self.logger.error(f"Error adding feedback: {e}")
            return False
    
    def _save_feedback(self):
        """Save feedback to file."""
        try:
            feedback_file = os.path.join(self.app.config.get("general", "data_dir"), "llm_feedback.json")
            
            with open(feedback_file, "w") as f:
                json.dump(self.feedback_db, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving feedback: {e}")
```

### 2.4. Collaborative Features Implementation

Implement collaborative features for sharing presets and templates:

```python
class LLMCollaborationManager:
    """Class for managing LLM collaboration features."""
    
    def __init__(self, app):
        """
        Initialize the LLM collaboration manager.
        
        Args:
            app: The main application instance.
        """
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.LLMCollaborationManager")
        
        # Create collaboration directory
        self.collab_dir = os.path.join(self.app.config.get("general", "data_dir"), "llm_collaboration")
        os.makedirs(self.collab_dir, exist_ok=True)
    
    def export_preset(self, preset, file_path=None):
        """
        Export an LLM preset to a file.
        
        Args:
            preset (LLMPreset): Preset to export.
            file_path (str, optional): Path to save the preset. Default is None.
        
        Returns:
            str: Path to the exported preset file, or None if export failed.
        """
        try:
            # Generate file path if not provided
            if file_path is None:
                file_path = os.path.join(self.collab_dir, f"preset_{preset.name.lower().replace(' ', '_')}.json")
            
            # Export preset to file
            with open(file_path, "w") as f:
                json.dump(preset.to_dict(), f, indent=2)
            
            return file_path
        except Exception as e:
            self.logger.error(f"Error exporting preset: {e}")
            return None
    
    def import_preset(self, file_path):
        """
        Import an LLM preset from a file.
        
        Args:
            file_path (str): Path to the preset file.
        
        Returns:
            LLMPreset: Imported preset, or None if import failed.
        """
        try:
            # Import preset from file
            with open(file_path, "r") as f:
                preset_data = json.load(f)
            
            # Create preset from data
            from models.llm_customization import LLMPreset
            preset = LLMPreset.from_dict(preset_data)
            
            return preset
        except Exception as e:
            self.logger.error(f"Error importing preset: {e}")
            return None
```

## 3. Implementation Timeline

### 3.1. Week 1: Plugin System
1. Create `LLMPlugin` base class
2. Implement plugin loading and registration
3. Update `LLMManager` to use plugins
4. Add sample plugins for common use cases

### 3.2. Week 2: Multi-Modal Inputs
1. Create `MultiModalInput` class
2. Implement image processing for LLM input
3. Implement audio clip processing for LLM input
4. Update `LLMChatWindow` to support multi-modal inputs

### 3.3. Week 3: Feedback System
1. Create `LLMFeedbackSystem` class
2. Implement feedback collection and storage
3. Create UI for providing feedback
4. Add feedback analysis tools

### 3.4. Week 4: Collaborative Features
1. Create `LLMCollaborationManager` class
2. Implement preset and template export/import
3. Create UI for sharing and importing
4. Add documentation and examples
