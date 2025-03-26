# Sequence Maker - LLM Integration

This directory contains the refactored LLM (Large Language Model) integration components for Sequence Maker.

## Directory Structure

```
app/llm/
├── __init__.py                # Package exports
├── llm_manager.py             # Main orchestrator class
├── llm_config.py              # Configuration and profiles management
├── tool_manager.py            # Function definitions and execution
├── response_processor.py      # Response parsing and processing
├── tracker.py                 # Token usage and cost tracking
├── utils.py                   # Utility functions
├── exceptions.py              # Custom exceptions
└── api_clients/               # API client implementations
    ├── __init__.py            # Package exports
    ├── base_client.py         # Abstract base class
    ├── openai_client.py       # OpenAI API client
    ├── anthropic_client.py    # Anthropic API client
    └── local_client.py        # Local model client
```

## Components

### LLMManager

The main orchestrator class that coordinates all other components. It handles:
- Initialization of all components
- Request dispatching
- Signal emission
- Thread management
- Version history integration

### LLMConfig

Manages LLM configuration and profiles, including:
- Loading and saving profiles
- Profile switching
- Legacy settings migration

### LLMToolManager

Manages function definitions and execution, including:
- Function definitions for timeline, audio, and lyrics
- Function call handling
- Action registration and execution

### LLMResponseProcessor

Processes and parses LLM responses, including:
- Text extraction
- Ambiguity detection
- Suggestion extraction
- Action parsing
- Color sequence parsing

### LLMTracker

Tracks token usage, costs, and performance metrics, including:
- Token counting
- Cost calculation
- Performance metrics logging
- Project metadata updates

### API Clients

Provider-specific API clients that implement the BaseLLMClient interface:
- OpenAIClient: For OpenAI API (GPT-3.5, GPT-4)
- AnthropicClient: For Anthropic API (Claude)
- LocalClient: For local LLM models

## Usage

```python
from app.llm import LLMManager

# Create an instance
llm_manager = LLMManager(app)

# Send a request
llm_manager.send_request(
    prompt="Generate a color sequence for a juggling ball",
    system_message="You are a helpful assistant for creating juggling light sequences.",
    temperature=0.7,
    max_tokens=1024,
    use_functions=True,
    stream=False
)

# Connect to signals
llm_manager.llm_response_received.connect(handle_response)
llm_manager.llm_error.connect(handle_error)
```

## Migration from Legacy Structure

The LLM integration has been refactored from a monolithic class into smaller, focused components. If you were previously using `LLMManager` from `managers.llm_manager`, you should update your imports to use `app.llm.LLMManager` instead.

For backward compatibility, the old import path still works but will show a deprecation warning.