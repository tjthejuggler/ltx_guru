# Handling Large Audio Analysis Reports

## Overview

Audio analysis reports can become very large, especially for longer audio files or when including comprehensive analysis data like lyrics with word-level timestamps. These large reports can cause context overflow issues when working with LLMs (Large Language Models) like Roocode.

This document provides guidelines and best practices for working with audio analysis reports to prevent context overflow issues.

## Tools for Handling Large Reports

The Roocode Sequence Designer Tools include several utilities specifically designed to help manage large audio analysis reports:

### 1. Check Report Size Tool

The `check_report_size.py` tool allows you to check the size of an audio analysis report before attempting to view it directly:

```bash
python -m roocode_sequence_designer_tools.check_report_size <report_path>
```

This tool provides:
- File size information
- A warning if the report is too large for direct viewing
- A summary of the report's content (number of sections, beats, etc.)
- Recommendations for handling large reports

### 2. Time Range Filtering

The enhanced `audio_analysis_report.py` tool now supports time range filtering, allowing you to generate reports for specific sections of an audio file:

```bash
python -m roocode_sequence_designer_tools.audio_analysis_report <audio_file> --start-time 0 --end-time 60
```

This command generates a report for just the first 60 seconds of the audio file, resulting in a much smaller report.

### 3. Feature Selection

You can also generate reports that include only specific audio features:

```bash
python -m roocode_sequence_designer_tools.audio_analysis_report <audio_file> --features beats,sections
```

This command generates a report that only includes beat and section information, omitting other features like energy analysis or lyrics.

### 4. Dedicated Lyrics Tool

For lyrics processing, use the dedicated `extract_lyrics.py` tool:

```bash
python -m roocode_sequence_designer_tools.extract_lyrics <audio_file>
```

This tool can also filter lyrics by time range:

```bash
python -m roocode_sequence_designer_tools.extract_lyrics <audio_file> --start-time 60 --end-time 120
```

## Best Practices

1. **Always Check Report Size First**: Before attempting to view or process a complete audio analysis report, check its size using the `check_report_size.py` tool.

2. **Use Time Range Filtering**: When working with longer audio files (over 3 minutes), use time range filtering to focus on specific sections of interest.

3. **Use Feature Selection**: If you only need specific audio features (e.g., beats for a beat-driven effect), use feature selection to generate smaller, more focused reports.

4. **Process Lyrics Separately**: Use the dedicated lyrics extraction tool for lyrics processing, especially when working with word-level timestamps.

5. **Combine Approaches**: For the most efficient workflow, combine these approaches. For example:
   ```bash
   python -m roocode_sequence_designer_tools.audio_analysis_report <audio_file> --start-time 0 --end-time 60 --features beats,sections
   python -m roocode_sequence_designer_tools.extract_lyrics <audio_file> --start-time 0 --end-time 60
   ```

## Troubleshooting

If you encounter context overflow issues when working with audio analysis reports:

1. **Check Report Size**: Use the `check_report_size.py` tool to verify if the report is too large.

2. **Generate a Smaller Report**: Use time range filtering and/or feature selection to generate a smaller report.

3. **Use Multiple Reports**: For comprehensive analysis of longer audio files, generate multiple smaller reports for different time ranges or features.

4. **Avoid Direct Viewing**: Avoid attempting to view the complete contents of large reports directly. Instead, use the tools provided to extract specific information or generate summaries.

## Example Workflow

Here's a recommended workflow for analyzing a 5-minute song:

1. Generate a complete report but don't view it directly:
   ```bash
   python -m roocode_sequence_designer_tools.audio_analysis_report song.mp3
   ```

2. Check the report size:
   ```bash
   python -m roocode_sequence_designer_tools.check_report_size song_analysis_report.json
   ```

3. If the report is too large, generate smaller reports for specific time ranges:
   ```bash
   python -m roocode_sequence_designer_tools.audio_analysis_report song.mp3 --start-time 0 --end-time 60 --output-dir song_analysis/part1
   python -m roocode_sequence_designer_tools.audio_analysis_report song.mp3 --start-time 60 --end-time 120 --output-dir song_analysis/part2
   # ... and so on
   ```

4. Process lyrics separately:
   ```bash
   python -m roocode_sequence_designer_tools.extract_lyrics song.mp3 --output song_lyrics.json
   ```

5. Use these smaller, more focused reports for your sequence design work.