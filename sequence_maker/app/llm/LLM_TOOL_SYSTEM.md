# Sequence Maker - LLM Tool System

This document explains the LLM tool system in Sequence Maker, including how tools are defined, registered, and executed, and how to add new tools.

## 1. Overview

The LLM integration in Sequence Maker allows the application to interact with Large Language Models (LLMs) like OpenAI's GPT models and Anthropic's Claude. A key part of this integration is the tool system, which enables the LLM to perform specific actions within the application, such as creating timeline segments, analyzing audio, or working with lyrics.

## 2. Architecture

The tool system is built around the following components:

### 2.1. LLMToolManager

The `LLMToolManager` class (`sequence_maker/app/llm/tool_manager.py`) is the central component of the tool system. It:
- Defines available tools (functions) for the LLM
- Registers handlers for each tool
- Executes tool actions when requested by the LLM
- Processes function calls from the LLM response

### 2.2. Function Definitions

Function definitions describe the tools available to the LLM, including:
- Name: The name of the function
- Description: What the function does
- Parameters: The inputs the function accepts, with types and descriptions

These definitions are organized into categories:
- `timeline_functions`: Tools for manipulating timelines and segments
- `audio_functions`: Tools for working with audio
- `lyrics_functions`: Tools for working with lyrics

### 2.3. Action Handlers

Action handlers are methods that implement the actual functionality of each tool. They:
- Take parameters from the LLM
- Perform the requested action
- Return a result to the LLM

### 2.4. LLMManager

The `LLMManager` class (`sequence_maker/app/llm/llm_manager.py`) coordinates the overall LLM interaction, including:
- Sending requests to the LLM with function definitions
- Processing responses from the LLM
- Delegating function calls to the `LLMToolManager`

## 3. Tool Definition and Registration

### 3.1. Defining Tools

Tools are defined as function definitions in the `LLMToolManager` class. Each function definition includes:

```python
{
    "name": "function_name",
    "description": "Description of what the function does",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Description of parameter 1"
            },
            "param2": {
                "type": "integer",
                "description": "Description of parameter 2"
            }
            # Additional parameters...
        },
        "required": ["param1"]  # List of required parameters
    }
}
```

These definitions follow the OpenAI function calling format, which is also compatible with other LLM providers through adaptation.

### 3.2. Registering Tool Handlers

Tool handlers are registered in the `LLMToolManager.__init__` method:

```python
self.register_action_handler("function_name", self._handle_function_name)
```

The handler method should have the following signature:

```python
def _handle_function_name(self, parameters):
    """
    Handle the function_name action.
    
    Args:
        parameters (dict): Action parameters.
        
    Returns:
        dict: Result of the action.
    """
    # Implementation...
    return result_dict
```

## 4. Adding New Tools

To add a new tool to the system, follow these steps:

### 4.1. Define the Function

Add a new function definition to the appropriate category property in `LLMToolManager`:

```python
@property
def timeline_functions(self):
    return [
        # Existing functions...
        {
            "name": "new_function_name",
            "description": "Description of the new function",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Description of parameter 1"
                    }
                    # Additional parameters...
                },
                "required": ["param1"]
            }
        }
    ]
```

### 4.2. Implement the Handler

Create a handler method in the `LLMToolManager` class:

```python
def _handle_new_function_name(self, parameters):
    """
    Handle the new_function_name action.
    
    Args:
        parameters (dict): Action parameters.
        
    Returns:
        dict: Result of the action.
    """
    # Extract parameters
    param1 = parameters.get("param1")
    
    # Validate parameters
    if not param1:
        return {"error": "param1 is required"}
    
    # Implement the action
    # ...
    
    # Return the result
    return {
        "success": True,
        "result": "Action completed successfully",
        "details": {
            # Additional details...
        }
    }
```

### 4.3. Register the Handler

Register the handler in the `LLMToolManager.__init__` method:

```python
self.register_action_handler("new_function_name", self._handle_new_function_name)
```

### 4.4. Test the Tool

Test the new tool by:
1. Running the application
2. Opening the LLM chat dialog
3. Asking the LLM to use the new tool
4. Verifying that the tool works as expected

## 5. Tool Execution Flow

When the LLM calls a tool, the following sequence occurs:

1. The LLM generates a response with a function call
2. `LLMManager._process_response` detects the function call
3. `LLMToolManager._handle_function_call` extracts the function name and arguments
4. `LLMToolManager.execute_action` finds the registered handler for the function
5. The handler is called with the arguments
6. The handler returns a result
7. The result is sent back to the LLM for further processing

## 6. Examples of Existing Tools

### 6.1. Timeline Tools

- `create_segment_for_word`: Creates color segments on specified juggling balls precisely during the occurrences of a specific word in the song lyrics
- `create_color_sequence`: Creates a sequence of color segments on specified balls
- `set_default_color`: Sets the default color for a ball
- `clear_timeline`: Clears all segments from a specific timeline (ball)
- `clear_all_timelines`: Clears all segments from all timelines (all balls) at once, optionally setting them to black

### 6.2. Audio Tools

- `get_audio_info`: Gets information about the current audio file
- `get_beat_info`: Gets information about beats in the audio
- `play_audio`: Plays the audio from a specified position
- `pause_audio`: Pauses audio playback

### 6.3. Lyrics Tools

- `get_lyrics_info`: Gets information about the current lyrics
- `get_word_timestamps`: Gets timestamps for specific words in the lyrics
- `find_first_word`: Finds the first occurrence of a word in the lyrics

## 7. Best Practices

When creating new tools, follow these best practices:

### 7.1. Clear Descriptions

Write clear, detailed descriptions for functions and parameters. The LLM relies on these descriptions to understand when and how to use the tools.

### 7.2. Parameter Validation

Always validate parameters in your handler methods. Check for required parameters and validate their types and values.

### 7.3. Error Handling

Implement robust error handling in your handler methods. Return clear error messages that the LLM can understand and act upon.

### 7.4. Return Structured Results

Return structured results that provide clear information about the outcome of the action. Include success/failure status and relevant details.

### 7.5. Keep Handlers Focused

Each handler should focus on a specific task. If a task is complex, consider breaking it down into multiple tools.

## 8. Debugging Tools

When debugging tools, you can:

1. Add logging statements to your handler methods:
   ```python
   self.logger.debug(f"Executing action: {action_type} with parameters: {parameters}")
   ```

2. Check the application log for errors and warnings

3. Use the LLM chat dialog to test tools interactively

4. Examine the function call arguments and results in the log

## 9. Future Enhancements

Potential enhancements to the tool system:

1. **Tool Categories**: Organize tools into categories for better management
2. **Tool Dependencies**: Define dependencies between tools
3. **Tool Permissions**: Implement permission levels for tools
4. **Tool Documentation**: Generate documentation for tools automatically
5. **Tool Testing**: Create automated tests for tools