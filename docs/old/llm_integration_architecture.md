# LLM Integration Architecture for Sequence Maker

This document outlines the architecture and implementation details of the LLM integration for the Sequence Maker application.

## 1. Overview

The LLM integration allows users to interact with the application using natural language. The LLM can understand the application's state, manipulate timelines, and provide suggestions based on audio analysis.

## 2. Architecture Components

### 2.1. LLM Service Layer (`LLMManager`)

The `LLMManager` class provides an abstraction layer for interacting with different LLM providers:

- **Supported Providers**: OpenAI, Anthropic, Local models
- **Configuration**: API keys, model selection, temperature, max tokens
- **Token Usage Tracking**: Monitors token usage and estimated costs
- **Request Handling**: Manages requests to the LLM, including interruption support

### 2.2. Application Context API (`AppContextAPI`)

The `AppContextAPI` class provides a unified API for accessing application state data:

- **Project Context**: Project metadata, settings, and configuration
- **Timeline Context**: Timeline data, segments, colors, and effects
- **Audio Context**: Audio file information, beat detection, and playback state
- **Lyrics Context**: Lyrics text and word timestamps

### 2.3. Timeline Action API (`TimelineActionAPI`)

The `TimelineActionAPI` class provides an API for manipulating timelines:

- **Segment Creation**: Create new segments with specified colors and durations
- **Segment Modification**: Modify existing segments (color, duration, effects)
- **Segment Deletion**: Remove segments from timelines
- **Default Color Setting**: Set default colors for timelines
- **Batch Operations**: Create multiple segments in a single operation

### 2.4. Audio Action API (`AudioActionAPI`)

The `AudioActionAPI` class provides an API for controlling audio playback:

- **Playback Control**: Play, pause, stop, and seek audio
- **Volume Control**: Adjust audio volume

### 2.5. User Interface (`LLMChatDialog`)

The `LLMChatDialog` class provides a user interface for interacting with the LLM:

- **Chat Interface**: Text input and response display
- **Timeline Selection**: Select which timelines to manipulate
- **Confirmation Modes**: Full confirmation, selective confirmation, or full automation
- **Token Usage Display**: Show token usage and estimated cost
- **Chat History Persistence**: Save chat history with the project

## 3. Data Flow

1. **User Input**: User enters a natural language prompt in the LLM chat dialog
2. **Context Collection**: Application context is collected and formatted for the LLM
3. **LLM Request**: Request is sent to the LLM provider with the context and prompt
4. **Response Processing**: LLM response is processed to extract actions and explanations
5. **Action Execution**: Actions are executed based on the confirmation mode
6. **Feedback**: Results are displayed to the user in the chat dialog

## 4. Confirmation Modes

The LLM integration supports three confirmation modes:

1. **Full Confirmation**: All actions require explicit user confirmation
2. **Selective Confirmation**: Major changes require confirmation, minor changes are applied automatically
3. **Full Automation**: All actions are applied automatically without confirmation

## 5. Token Usage and Cost Tracking

The LLM integration tracks token usage and estimated costs:

- **Token Counting**: Count tokens used in requests and responses
- **Cost Calculation**: Calculate estimated costs based on token usage and provider rates
- **Usage Display**: Show token usage and estimated cost in the chat dialog
- **Usage Persistence**: Save token usage statistics with the project

## 6. Chat History Persistence

The LLM integration saves chat history with the project:

- **Message Storage**: Store user messages and LLM responses
- **Timestamp Recording**: Record timestamps for each message
- **Project Integration**: Save chat history as part of the project file

## 7. Error Handling

The LLM integration includes robust error handling:

- **Request Errors**: Handle network errors, API errors, and authentication errors
- **Action Errors**: Handle errors in action execution
- **User Feedback**: Provide clear error messages to the user

## 8. Implementation Details

### 8.1. LLM Manager

The `LLMManager` class has been extended to support:

- Multiple LLM providers (OpenAI, Anthropic, Local)
- Token usage tracking
- Action parsing
- Interruption support

### 8.2. API Classes

New API classes have been created:

- `AppContextAPI`: Provides access to application state data
- `TimelineActionAPI`: Provides methods for manipulating timelines
- `AudioActionAPI`: Provides methods for controlling audio playback

### 8.3. UI Components

The `LLMChatDialog` class has been enhanced with:

- Confirmation mode selection
- Token usage display
- Stop button for interrupting requests
- Chat history persistence

### 8.4. Settings Integration

The `SettingsDialog` class has been updated to include LLM settings:

- Provider selection
- API key configuration
- Model selection
- Temperature and max tokens settings
- Local model endpoint configuration
- Default confirmation mode selection

## 9. Future Enhancements

Potential future enhancements to the LLM integration:

- **Function Calling**: Implement OpenAI function calling for more structured interactions
- **Streaming Responses**: Support streaming responses for faster feedback
- **Multi-turn Context**: Improve context management for multi-turn conversations
- **Audio Analysis Integration**: Enhance audio analysis capabilities for better music-driven suggestions
- **Custom Instructions**: Allow users to define custom instructions for the LLM