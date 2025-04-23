# LTX Guru MCP Servers Documentation

This document provides detailed information on how to use the Audio Analyzer and LTX Sequence Maker MCP servers together to create music-synchronized color sequences.

## Overview

The MCP (Model Context Protocol) servers provide a way to extend the capabilities of AI assistants like Roo. We've created two MCP servers:

1. **Audio Analyzer MCP Server**: Analyzes audio files to extract musical features like beats, sections, and energy levels.
2. **LTX Sequence Maker MCP Server**: Creates color sequences synchronized to music based on the analysis data.

These servers work together to enable the creation of sophisticated music-synchronized light shows.

## Installation

Both MCP servers have been installed in the following locations:

- Audio Analyzer MCP: `/home/twain/.local/share/Roo-Code/MCP/audio_analyzer_mcp`
- LTX Sequence Maker MCP: `/home/twain/.local/share/Roo-Code/MCP/ltx_sequence_maker_mcp`

They have been registered in the MCP settings file at:
`/home/twain/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json`

To install the dependencies for both servers, run:

```bash
cd /home/twain/.local/share/Roo-Code/MCP/audio_analyzer_mcp
pip install -e .

cd /home/twain/.local/share/Roo-Code/MCP/ltx_sequence_maker_mcp
pip install -e .
```

## Workflow

The typical workflow for creating music-synchronized color sequences is:

1. **Analyze an audio file** using the Audio Analyzer MCP
2. **Get song metadata** to understand the structure of the song
3. **Get beats or sections** from the analyzed data
4. **Create color patterns** using the LTX Sequence Maker MCP

## Example Usage

Here's a step-by-step example of how to use both MCP servers together:

### 1. Analyze an audio file

```python
# Use the Audio Analyzer MCP to analyze an audio file
analysis_result = use_mcp_tool(
    server_name="audio-analyzer",
    tool_name="analyze_audio",
    arguments={
        "audio_file_path": "/path/to/your/audio.mp3"
    }
)
```

### 2. Get song metadata

```python
# Get general metadata about the song
metadata = use_mcp_tool(
    server_name="audio-analyzer",
    tool_name="get_song_metadata",
    arguments={}
)

# This will return information like:
# - song_title
# - duration_seconds
# - estimated_tempo
# - time_signature_guess
# - total_beats
# - total_downbeats
# - sections (list of section labels)
```

### 3. Get beats in a specific range

```python
# Get beats in a specific time range
beats_result = use_mcp_tool(
    server_name="audio-analyzer",
    tool_name="get_beats_in_range",
    arguments={
        "start_time": 10.0,
        "end_time": 20.0,
        "beat_type": "all"  # or "downbeat"
    }
)

# Extract the beats from the result
beats = beats_result["beats"]
```

### 4. Create a beat-synchronized color pattern

```python
# Create a color pattern synchronized to the beats
pattern_result = use_mcp_tool(
    server_name="ltx-sequence-maker",
    tool_name="apply_beat_pattern",
    arguments={
        "beats": beats,
        "pattern_type": "pulse",  # or "toggle", "fade_in", "fade_out"
        "colors": ["red", "green", "blue"],
        "duration": 0.25
    }
)

# The result contains the created segments
segments = pattern_result["segments"]
```

### 5. Get section details

```python
# Get details about a specific section
section_result = use_mcp_tool(
    server_name="audio-analyzer",
    tool_name="get_section_details",
    arguments={
        "section_label": "Chorus 1"
    }
)

# This will return information like:
# - label
# - start_time
# - end_time
# - duration
# - beats (within the section)
# - beat_count
# - downbeats (within the section)
# - downbeat_count
# - average_energy
```

### 6. Apply section themes

```python
# Get all sections
sections = []
for section_label in metadata["sections"]:
    section_details = use_mcp_tool(
        server_name="audio-analyzer",
        tool_name="get_section_details",
        arguments={
            "section_label": section_label
        }
    )
    sections.append({
        "label": section_details["label"],
        "start_time": section_details["start_time"],
        "end_time": section_details["end_time"]
    })

# Get energy data for the entire song
energy_data = use_mcp_tool(
    server_name="audio-analyzer",
    tool_name="get_feature_value_at_time",
    arguments={
        "time": 0.0,  # This is just to access the energy_timeseries data
        "feature_name": "energy"
    }
)

# Apply section themes
theme_result = use_mcp_tool(
    server_name="ltx-sequence-maker",
    tool_name="apply_section_theme",
    arguments={
        "sections": sections,
        "section_themes": [
            {
                "section_label": "Intro",
                "base_color": "blue",
                "energy_mapping": "brightness"
            },
            {
                "section_label": "Verse 1",
                "base_color": "red",
                "energy_mapping": "saturation"
            },
            {
                "section_label": "Chorus 1",
                "base_color": "green",
                "energy_mapping": "none"
            }
        ],
        "default_color": "white",
        "energy_data": energy_data["energy_timeseries"]
    }
)

# The result contains the created segments
themed_segments = theme_result["segments"]
```

### 7. Create a simple color sequence

```python
# Create a simple color sequence
sequence_result = use_mcp_tool(
    server_name="ltx-sequence-maker",
    tool_name="create_color_sequence",
    arguments={
        "duration": metadata["duration_seconds"],
        "colors": ["red", "green", "blue"],
        "segment_duration": 1.0
    }
)

# The result contains the created segments
sequence_segments = sequence_result["segments"]
```

## Audio Analyzer MCP Tools

### analyze_audio

Analyzes an audio file to extract musical features.

**Parameters:**
- `audio_file_path` (string, required): Path to the audio file to analyze

### get_song_metadata

Gets general metadata about the analyzed song.

**Parameters:**
- `audio_file_path` (string, optional): Path to the audio file to analyze if no analysis is available

### get_beats_in_range

Gets beat timestamps within a specified time range.

**Parameters:**
- `start_time` (number, required): Start time in seconds
- `end_time` (number, required): End time in seconds
- `beat_type` (string, optional): Type of beats to retrieve ("all" or "downbeat")

### get_section_details

Gets details about a specific section of the song.

**Parameters:**
- `section_label` (string, required): Label of the section (e.g., "Intro", "Verse 1", "Chorus 1")

### get_feature_value_at_time

Gets the value of a specific audio feature at a given time.

**Parameters:**
- `time` (number, required): Time in seconds
- `feature_name` (string, required): Name of the feature to retrieve (one of: "energy", "onset_strength", "chroma", "spectral_contrast", "spectral_centroid", "spectral_rolloff", "zero_crossing_rate")

## LTX Sequence Maker MCP Tools

### apply_beat_pattern

Applies a color pattern synchronized to beats.

**Parameters:**
- `beats` (array of numbers, required): List of beat timestamps in seconds
- `pattern_type` (string, required): Type of pattern to apply (one of: "pulse", "toggle", "fade_in", "fade_out")
- `colors` (array, required): List of colors to use in the pattern (RGB arrays or color names)
- `duration` (number, optional): Duration of each color segment in seconds (default: 0.25)

### apply_section_theme

Applies color themes to different sections of the song.

**Parameters:**
- `sections` (array, required): List of sections with start and end times
- `section_themes` (array, required): List of section themes
- `default_color` (RGB array or string, optional): Default color for sections without a theme
- `energy_data` (object, optional): Energy timeseries data for energy mapping

### create_color_sequence

Creates a simple color sequence with alternating colors.

**Parameters:**
- `duration` (number, required): Total duration of the sequence in seconds
- `colors` (array, required): List of colors to use in the sequence (RGB arrays or color names)
- `segment_duration` (number, optional): Duration of each color segment in seconds (default: 1.0)

## Pattern Types

### Pulse

Creates a short color segment at each beat. The color changes with each beat, cycling through the provided colors.

### Toggle

Alternates between colors, with each color lasting until the next beat. The color changes with each beat, cycling through the provided colors.

### Fade In

Creates segments that fade in from black to the target color at each beat. The target color changes with each beat, cycling through the provided colors.

### Fade Out

Creates segments that fade out from the target color to black at each beat. The target color changes with each beat, cycling through the provided colors.

## Energy Mapping

### Brightness

Maps energy values to the brightness of the base color. Higher energy results in brighter colors.

### Saturation

Maps energy values to the saturation of the base color. Higher energy results in more saturated colors.

## Output Format

All tools return segments in the following format:

```json
{
  "start_time": 0.0,  // Start time in seconds
  "end_time": 1.0,    // End time in seconds
  "color": [255, 0, 0]  // RGB color values
}
```

These segments can be used to create color sequences in the LTX Guru application.

## Troubleshooting

### Audio Analysis Issues

- Make sure the audio file exists and is in a supported format (MP3, WAV, etc.)
- Check that librosa is properly installed (`pip install librosa`)
- If analysis is slow, consider using a shorter audio file or a lower sample rate

### Color Sequence Issues

- Make sure the beats or sections are properly defined
- Check that the colors are valid (either RGB arrays or color names)
- If segments are not created, check the pattern type and parameters

## Conclusion

The Audio Analyzer and LTX Sequence Maker MCP servers provide a powerful way to create music-synchronized color sequences. By analyzing audio files and applying various pattern types, you can create sophisticated light shows that match the rhythm and structure of music.