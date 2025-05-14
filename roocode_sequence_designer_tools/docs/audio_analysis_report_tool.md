# Audio Analysis Report Tool

## Overview

The Audio Analysis Report Tool is a comprehensive utility for analyzing audio files and generating detailed reports about their musical features. This tool provides a complete assessment of audio analysis capabilities, generates visualizations, and creates a structured JSON report.

## Features

- **Comprehensive Capability Testing**: Tests and reports on all audio analysis capabilities including beat detection, section detection, energy analysis, onset strength analysis, tempo estimation, time signature detection, and lyrics processing.

- **Visualization Generation**: Creates visual plots of audio features including:
  - Energy over time with section and beat markers
  - Onset strength over time with beat markers

- **Structured Reporting**: Generates a detailed JSON report containing:
  - Analysis results for all features
  - Capability status (working/not working)
  - Issues encountered during analysis
  - Paths to generated visualizations

- **Summary Output**: Provides a concise console summary of the analysis results.

## Usage

```bash
python -m roocode_sequence_designer_tools.audio_analysis_report <audio_file_path> [--output-dir <dir>]
```

### Arguments

- `audio_file_path`: Path to the audio file to analyze
- `--output-dir` (optional): Directory to save the report and visualizations. If not provided, uses the directory containing the audio file.

### Example

```bash
python -m roocode_sequence_designer_tools.audio_analysis_report my_song.mp3 --output-dir ./analysis_results
```

## Output

The tool generates the following outputs:

1. **JSON Report** (`analysis_report.json`): Contains detailed analysis results, capability status, and any issues encountered.

2. **Visualization Plots**:
   - `plots/energy_plot.png`: Energy levels over time with section and beat markers
   - `plots/onset_strength_plot.png`: Onset strength over time with beat markers

3. **Console Summary**: A concise summary of the analysis results printed to the console.

## Report Structure

The generated JSON report has the following structure:

```json
{
  "audio_file": "/path/to/audio.mp3",
  "analysis_timestamp": 1621234567.89,
  "analysis_results": {
    "basic_analysis": {
      // All extracted audio features
    },
    "lyrics_analysis": {
      // Lyrics information if available
    }
  },
  "issues": [
    // List of any issues encountered during analysis
  ],
  "capabilities": {
    "beat_detection": {"supported": true, "working": true},
    "section_detection": {"supported": true, "working": true},
    "energy_analysis": {"supported": true, "working": true},
    "onset_strength_analysis": {"supported": true, "working": true},
    "tempo_estimation": {"supported": true, "working": true},
    "time_signature_detection": {"supported": true, "working": true},
    "lyrics_processing": {"supported": true, "working": true}
  },
  "visualization_path": "/path/to/plots"
}
```

## Programmatic Usage

The tool can also be used programmatically in Python scripts:

```python
from roocode_sequence_designer_tools.audio_analysis_report import analyze_audio_and_generate_report, print_report_summary

# Generate the report
report = analyze_audio_and_generate_report("my_song.mp3", "./analysis_results")

# Print a summary
print_report_summary(report)

# Access specific analysis results
bpm = report["analysis_results"]["basic_analysis"]["estimated_tempo"]
print(f"The song's tempo is {bpm} BPM")
```

## Dependencies

- Python 3.6+
- matplotlib
- numpy
- roo_code_sequence_maker.audio_analyzer

## Related Tools

- **extract_audio_features.py**: For extracting specific audio features without generating a comprehensive report or visualizations.
- **compile_seqdesign.py**: For compiling sequence design files that may use the audio analysis data.