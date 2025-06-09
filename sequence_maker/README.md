# Sequence Maker

A tool for creating color sequences for LTX juggling balls.

## Overview

Sequence Maker is a desktop application that allows you to create, edit, and visualize color sequences for LTX juggling balls. It provides an intuitive interface for designing complex color patterns, synchronizing them with music, and exporting them to the LTX ball format.

## Features

- **Interactive Timeline Editing**: Create and edit color sequences on a timeline interface.
- **Multiple Ball Support**: Design sequences for multiple juggling balls simultaneously.
- **Audio Synchronization**: Import audio files and synchronize color changes with the music.
- **Real-time Visualization**: See how your sequences will look on the juggling balls in real-time.
- **Keyboard Mapping**: Customize keyboard shortcuts for quick color changes.
- **Export to JSON and PRG**: Export your sequences to JSON format for use with prg_generator.
- **Color Fades**: Create smooth transitions between colors.
  - Visually represented as gradients on the timeline.
  - Shift + (color key) creates a fade from the previous segment's color to the new color.
  - Right-click a segment > "Add Effect" > "Fade" to configure start and end colors via a dialog.
- **LLM Integration**: Use AI to automatically generate sequences based on music analysis, lyrics synchronization, and natural language instructions.

## Installation

### Prerequisites

- Python 3.8 or higher
- PyQt6
- librosa (for audio analysis)
- PyAudio (for audio playback)
- numpy
- matplotlib

### Install Dependencies

```bash
pip install PyQt6 librosa PyAudio numpy matplotlib
```

### Run the Application

```bash
python sequence_maker/main.py
```

## Usage

### Creating a New Project

1. Launch the application. An untitled project will be created automatically.
2. Alternatively, click on **File > New** to create a new project.
3. Set the project name and default settings.
4. New projects will have 3 timelines by default.

### Adding Color Sequences

1. Select a timeline for a ball.
2. Double-click on the timeline to add a solid color segment.
3. Choose a color for the segment.
4. Adjust the start and end times by dragging the segment edges.
5. **To create a fade**:
   - Hold **Shift** while pressing a mapped color key. This creates a fade from the end color of the previous segment (or black if no preceding segment) to the color of the pressed key.
   - Alternatively, right-click an existing segment, navigate to **Add Effect > Fade**. A dialog will appear allowing you to set a specific start and end color for that segment, turning it into a fade.

### Keyboard Mapping

1. Go to **Tools > Key Mapping** to configure keyboard shortcuts.
2. Assign keys to specific colors and timelines.
3. Use the keyboard to quickly add colors to the timeline.

### Audio Synchronization

1. Click on **File > Load Audio** to import an audio file.
2. The audio waveform will be displayed in the audio visualization panel.
3. Use the playback controls to play, pause, and stop the audio.
4. Add color changes at specific points in the audio.

### Exporting Sequences

1. Click on **File > Export to JSON** to export the sequences to JSON format.
2. Click on **File > Export to PRG** to export the sequences to PRG format for use with LTX balls.

## Project Structure

- **app/**: Core application components.
  - **llm/**: LLM integration components.
- **models/**: Data models for the application.
- **managers/**: Manager classes for different aspects of the application.
- **ui/**: User interface components.
- **export/**: Export functionality for different formats.
- **utils/**: Utility functions.
- **api/**: API classes for different application features.

## Timeline Format

The timeline format is a JSON structure that defines color changes over time. Each timeline represents a juggling ball, and each segment represents a color change.

Example:

```json
{
  "pixels": 4,
  "refresh_rate": 50,
  "sequence": {
    "0": {"color": [255, 0, 0]},                           // Solid red segment
    "5200": {"start_color": [255,0,0], "end_color": [0,255,0]}, // Fade from red to green (times in ms for 1000Hz JSON)
    "10800": {"color": [0, 0, 255]}                          // Solid blue segment
  },
  "end_time": 15000 // Example end time in ms
}
```

**Note on Fades in JSON**: Fade segments are represented with `start_color` and `end_color` keys. Solid segments use a single `color` key. The `prg_generator.py` script interprets these to produce the correct PRG file output.

## LLM Integration

Sequence Maker includes integration with Large Language Models (LLMs) like OpenAI's GPT models and Anthropic's Claude. This integration allows you to:

- Generate color sequences based on natural language instructions
- Synchronize colors with specific words in lyrics
- Get creative suggestions based on audio analysis
- Automate complex sequence creation tasks

### Using the LLM Integration

1. Click on **Tools > LLM Chat** to open the LLM chat dialog
2. Enter a natural language prompt describing what you want to do
3. The LLM will analyze your request and perform the appropriate actions

### LLM Documentation

Detailed documentation about the LLM integration can be found in:

- `sequence_maker/app/llm/README.md`: Overview of the LLM integration components
- `sequence_maker/app/llm/LLM_TOOL_SYSTEM.md`: Documentation of the tool system
- `sequence_maker/app/llm/REFACTORING_SUMMARY.md`: Summary of the refactoring process

## Integration with prg_generator

Sequence Maker is designed to work with prg_generator to create .prg files for LTX juggling balls. The application can export sequences in the JSON format expected by prg_generator, and can also directly call prg_generator to create .prg files.

## Recent Projects

The application keeps track of recently opened projects:

1. Access recent projects from **File > Recent Files**. (Fixed in vX.Y.Z - menu now correctly populates and updates).
2. Click on a project in the list to open it.
3. Use the "Clear Recent Files" option to clear the list.
4. The application will remember the last opened project and can reopen it automatically.

## Keyboard Shortcuts

- **Ctrl+N**: New project
- **Ctrl+O**: Open project
- **Ctrl+S**: Save project
- **Ctrl+Shift+S**: Save project as
- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo
- **Ctrl+X**: Cut segment
- **Ctrl+C**: Copy segment
- **Ctrl+V**: Paste segment
- **Delete**: Delete segment
- **Space**: Play/Pause audio
- **Escape**: Stop audio
- **Ctrl+Plus**: Zoom in
- **Ctrl+Minus**: Zoom out
- **Ctrl+0**: Zoom fit

## Configuration

The application settings are stored in the user's home directory:

- **Windows**: `%APPDATA%\SequenceMaker\config.json`
- **macOS**: `~/Library/Application Support/SequenceMaker/config.json`
- **Linux**: `~/.config/SequenceMaker/config.json`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---
*Last updated: 2025-06-09*