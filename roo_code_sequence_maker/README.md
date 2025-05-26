# Roo Code Sequence Maker

A toolkit for Roo agents to create color sequences for LTX juggling balls based on music analysis.

## Overview

This toolkit provides Python scripts and utilities that allow Roo agents to:

1. Analyze audio files to extract musical features (beats, sections, energy levels, etc.)
2. Process lyrics and align them with audio
3. Create color sequences synchronized to music
4. Generate JSON files compatible with LTX juggling balls

This toolkit provides standalone Python scripts that can be executed directly, making it easier for Roo agents to understand and modify the code as needed.

## Directory Structure

- `README.md`: This file
- `audio_analyzer.py`: Script for analyzing audio files and extracting musical features
- `sequence_generator.py`: Script for generating color sequences based on audio analysis
- `examples/`: Directory containing example scripts and data
- `utils/`: Directory containing utility functions

## Installation

### Prerequisites

- Python 3.8 or higher
- librosa (for audio analysis)
- numpy
- matplotlib (optional, for visualization)

### Install Dependencies

```bash
pip install librosa numpy matplotlib
```

## Usage Guide for Roo Agents

### 1. Analyzing an Audio File

The `audio_analyzer.py` script provides comprehensive audio analysis capabilities. It can extract beats, sections, energy levels, and other musical features from an audio file.

```python
from audio_analyzer import AudioAnalyzer

# Initialize the analyzer
analyzer = AudioAnalyzer()

# Analyze an audio file
analysis_data = analyzer.analyze_audio("/path/to/your/audio.mp3")

# Get basic metadata
print(f"Song duration: {analysis_data['duration_seconds']} seconds")
print(f"Estimated tempo: {analysis_data['estimated_tempo']} BPM")

# Get beats in a specific range
beats = analyzer.get_beats_in_range(0, 30)  # Get beats in the first 30 seconds
print(f"Found {len(beats)} beats in the first 30 seconds")

# Get section information
sections = analysis_data['sections']
print(f"The song has {len(sections)} sections:")
for section in sections:
    print(f"- {section['label']}: {section['start']:.2f}s to {section['end']:.2f}s")

# Get energy data
energy_data = analyzer.get_feature_timeseries("energy")
print(f"Energy data has {len(energy_data['times'])} data points")
```

### 2. Processing Lyrics

If the audio file has lyrics, you can use the lyrics processing capabilities to align the lyrics with the audio:

```python
from audio_analyzer import LyricsProcessor

# Initialize the processor
lyrics_processor = LyricsProcessor()

# Process lyrics for an audio file
lyrics_data = lyrics_processor.process_audio("/path/to/your/audio.mp3")

# Get word timestamps
word_timestamps = lyrics_data['word_timestamps']
print(f"Found {len(word_timestamps)} aligned words")

# Find words in a specific time range
words_in_range = lyrics_processor.get_words_in_range(10, 20)  # Words between 10s and 20s
print(f"Words between 10s and 20s: {' '.join([w['word'] for w in words_in_range])}")
```

### 3. Creating Color Sequences

The `sequence_generator.py` script provides tools for creating color sequences based on audio analysis:

```python
from sequence_generator import SequenceGenerator
from audio_analyzer import AudioAnalyzer

# Initialize the analyzer and generator
analyzer = AudioAnalyzer()
generator = SequenceGenerator()

# Analyze an audio file
analysis_data = analyzer.analyze_audio("/path/to/your/audio.mp3")

# Get beats in the entire song
beats = analysis_data['beats']

# Create a beat-synchronized color sequence
sequence = generator.apply_beat_pattern(
    beats=beats,
    pattern_type="pulse",  # Options: "pulse", "toggle", "fade_in", "fade_out"
    colors=["red", "green", "blue"],
    duration=0.25  # Duration of each color segment in seconds
)

# Print the first few segments
for i, segment in enumerate(sequence[:5]):
    print(f"Segment {i}: {segment['start_time']:.2f}s to {segment['end_time']:.2f}s, Color: {segment['color']}")

# Save the sequence to a JSON file
generator.save_sequence_to_json(sequence, "ball_1.json")
```

### 4. Creating Section-Based Color Themes

You can also create color sequences based on song sections:

```python
from sequence_generator import SequenceGenerator
from audio_analyzer import AudioAnalyzer

# Initialize the analyzer and generator
analyzer = AudioAnalyzer()
generator = SequenceGenerator()

# Analyze an audio file
analysis_data = analyzer.analyze_audio("/path/to/your/audio.mp3")

# Get sections and energy data
sections = analysis_data['sections']
energy_data = analyzer.get_feature_timeseries("energy")

# Create section themes
section_themes = [
    {
        "section_label": "Intro",
        "base_color": "blue",
        "energy_mapping": "brightness"  # Options: "brightness", "saturation", "none"
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
]

# Apply section themes
sequence = generator.apply_section_theme(
    sections=sections,
    section_themes=section_themes,
    default_color="white",
    energy_data=energy_data
)

# Save the sequence to a JSON file
generator.save_sequence_to_json(sequence, "ball_2.json")
```

### 5. Creating Multiple Ball Sequences

You can create sequences for multiple balls:

```python
from sequence_generator import SequenceGenerator
from audio_analyzer import AudioAnalyzer

# Initialize the analyzer and generator
analyzer = AudioAnalyzer()
generator = SequenceGenerator()

# Analyze an audio file
analysis_data = analyzer.analyze_audio("/path/to/your/audio.mp3")

# Get beats and sections
beats = analysis_data['beats']
sections = analysis_data['sections']

# Create sequences for three balls
sequences = []

# Ball 1: Beat-synchronized pulse pattern
sequences.append(generator.apply_beat_pattern(
    beats=beats,
    pattern_type="pulse",
    colors=["red", "orange", "yellow"],
    duration=0.25
))

# Ball 2: Beat-synchronized toggle pattern
sequences.append(generator.apply_beat_pattern(
    beats=beats,
    pattern_type="toggle",
    colors=["green", "cyan", "blue"],
    duration=0.5
))

# Ball 3: Section-based themes
sequences.append(generator.apply_section_theme(
    sections=sections,
    section_themes=[
        {"section_label": "Intro", "base_color": "purple", "energy_mapping": "brightness"},
        {"section_label": "Verse 1", "base_color": "magenta", "energy_mapping": "saturation"},
        {"section_label": "Chorus 1", "base_color": "white", "energy_mapping": "none"}
    ],
    default_color="black",
    energy_data=analyzer.get_feature_timeseries("energy")
))

# Save sequences to JSON files
for i, sequence in enumerate(sequences):
    generator.save_sequence_to_json(sequence, f"ball_{i+1}.json")
```

### 6. Synchronizing Colors with Lyrics

You can create color sequences synchronized with specific words in the lyrics:

```python
from sequence_generator import SequenceGenerator
from audio_analyzer import AudioAnalyzer, LyricsProcessor

# Initialize the components
analyzer = AudioAnalyzer()
lyrics_processor = LyricsProcessor()
generator = SequenceGenerator()

# Analyze an audio file
analysis_data = analyzer.analyze_audio("/path/to/your/audio.mp3")

# Process lyrics
lyrics_data = lyrics_processor.process_audio("/path/to/your/audio.mp3")
word_timestamps = lyrics_data['word_timestamps']

# Create a sequence that changes color on specific words
target_words = ["love", "heart", "dream", "dance", "night"]
sequence = generator.create_word_synchronized_sequence(
    word_timestamps=word_timestamps,
    target_words=target_words,
    target_color="red",
    default_color="blue",
    duration=0.5  # Duration of color change in seconds
)

# Save the sequence to a JSON file
generator.save_sequence_to_json(sequence, "lyrics_sync.json")
```

## Advanced Usage

### Audio Analysis Caching

The `AudioAnalyzer` class includes a robust caching mechanism to avoid re-analyzing the same audio file unnecessarily. This is particularly useful when working with large audio files or when multiple tools need to analyze the same file.

```python
from audio_analyzer import AudioAnalyzer

# Initialize the analyzer with default cache directory
analyzer = AudioAnalyzer()  # Uses ~/.ltx_sequence_maker/analysis_cache by default

# Or specify a custom cache directory
analyzer = AudioAnalyzer(cache_dir="/path/to/custom/cache")

# Analyze an audio file (will use cache if available)
analysis_data = analyzer.analyze_audio("/path/to/your/audio.mp3")

# Force reanalysis (ignore cache)
analysis_data = analyzer.analyze_audio("/path/to/your/audio.mp3", force_reanalysis=True)

# Analyze with specific parameters (will be included in cache key)
analysis_data = analyzer.analyze_audio(
    "/path/to/your/audio.mp3",
    analysis_params={"sample_rate": 22050, "n_fft": 2048}
)

# Clear cache for a specific file
analyzer.clear_cache("/path/to/your/audio.mp3")

# Clear entire cache
analyzer.clear_cache()

# Get information about the cache
cache_info = analyzer.get_cache_info()
print(f"Cache directory: {cache_info['cache_directory']}")
print(f"Number of cache files: {len(cache_info['cache_files'])}")

# Get cache info for a specific file
file_cache_info = analyzer.get_cache_info("/path/to/your/audio.mp3")
```

The caching system works as follows:

1. **Cache Keys**: Generated based on the audio file path, file content hash, and analysis parameters.
2. **Cache Validation**: Cache is considered valid if:
   - The audio file hasn't been modified since the cache was created
   - The file content hash matches
   - The analysis parameters match
3. **Cache Storage**: Cache files are stored in JSON format for compatibility and readability.
4. **Cache Location**: By default, cache files are stored in `~/.ltx_sequence_maker/analysis_cache/`.

### Creating Custom Pattern Types

You can create custom pattern types by extending the `SequenceGenerator` class:

```python
from sequence_generator import SequenceGenerator
import numpy as np

class CustomSequenceGenerator(SequenceGenerator):
    def apply_custom_pattern(self, beats, colors, duration=0.25):
        """
        Apply a custom pattern that creates a rainbow effect at each beat.
        """
        segments = []
        
        for i, beat in enumerate(beats):
            # Create a rainbow effect with multiple segments
            base_color = colors[i % len(colors)]
            
            # Create 5 segments with different hues
            for j in range(5):
                # Calculate segment times
                segment_duration = duration / 5
                start_time = beat + (j * segment_duration)
                end_time = start_time + segment_duration
                
                # Create a color with shifted hue
                hue_shift = j * 0.1
                color = self._shift_hue(base_color, hue_shift)
                
                # Add segment
                segments.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "color": color
                })
        
        return segments
    
    def _shift_hue(self, color, shift):
        """Shift the hue of a color."""
        # Implementation depends on how colors are represented
        # This is a simplified example
        if isinstance(color, str):
            # Convert named color to RGB
            color = self._named_color_to_rgb(color)
        
        # Convert RGB to HSV, shift hue, convert back to RGB
        # (Simplified implementation)
        r, g, b = color
        # ... (hue shifting logic)
        return [r, g, b]
```

### Working with Multiple Audio Files

You can analyze multiple audio files and create sequences that span across them:

```python
from audio_analyzer import AudioAnalyzer
from sequence_generator import SequenceGenerator

# Initialize components
analyzer = AudioAnalyzer()
generator = SequenceGenerator()

# Analyze multiple audio files
analysis_1 = analyzer.analyze_audio("/path/to/first.mp3")
analysis_2 = analyzer.analyze_audio("/path/to/second.mp3")

# Get beats from both files
beats_1 = analysis_1['beats']
beats_2 = analysis_2['beats']

# Adjust beats from the second file to account for the duration of the first file
first_duration = analysis_1['duration_seconds']
adjusted_beats_2 = [beat + first_duration for beat in beats_2]

# Combine beats
all_beats = beats_1 + adjusted_beats_2

# Create a sequence using all beats
sequence = generator.apply_beat_pattern(
    beats=all_beats,
    pattern_type="pulse",
    colors=["red", "green", "blue"],
    duration=0.25
)

# Save the sequence
generator.save_sequence_to_json(sequence, "combined_sequence.json")
```

## Example Scripts

The `examples/` directory contains example scripts that demonstrate various use cases:

- `basic_analysis.py`: Basic audio analysis example
- `beat_patterns.py`: Creating beat-synchronized patterns
- `section_themes.py`: Creating section-based color themes
- `lyrics_sync.py`: Synchronizing colors with lyrics
- `multiple_balls.py`: Creating sequences for multiple balls

## Troubleshooting

### Audio Analysis Issues

- Make sure the audio file exists and is in a supported format (MP3, WAV, etc.)
- Check that librosa is properly installed (`pip install librosa`)
- If analysis is slow, consider using a shorter audio file or a lower sample rate

### Color Sequence Issues

- Make sure the beats or sections are properly defined
- Check that the colors are valid (either RGB arrays or color names)
- If segments are not created, check the pattern type and parameters

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.