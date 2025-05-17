# Lyrics Extraction Efficiency Guide

This document outlines efficiency improvements and best practices for extracting lyrics timestamps from audio files. It was created based on real-world usage patterns and is designed to minimize token usage and processing time.

## Efficiency Analysis

### Common Inefficiencies

1. **Unnecessary API Attempts**:
   - Attempting automatic song identification when API keys are missing
   - Making multiple API calls that are likely to fail
   - Not recognizing API error patterns quickly

2. **Workflow Inefficiencies**:
   - Using extract_lyrics.py first instead of align_lyrics.py
   - Not checking if the Gentle server is running before starting
   - Asking for information in multiple steps instead of all at once

3. **Token Usage Issues**:
   - Reading and displaying entire JSON files with hundreds of timestamps
   - Providing lengthy explanations of technical processes
   - Redundant code inclusion in responses

## Optimized Workflow

### 1. File Organization

Always organize related files in the same subdirectory within the sequence_projects folder:

```
sequence_projects/
└── song_name/                # Create a subdirectory for each song
    ├── artist_song_name.mp3  # Original audio file
    ├── lyrics.txt            # Raw lyrics text file
    ├── lyrics_timestamps.json # Generated timestamps
    ├── analysis_report.json  # Audio analysis data
    └── song_name.seqdesign.json # Sequence design file
```

This organization:
- Keeps all related files together
- Makes it easier to find and manage project files
- Prevents clutter in the root directory
- Simplifies backup and sharing of complete projects

### 2. Direct Alignment Approach (Recommended)

```
# Step 1: Check if Gentle server is running
python -m sequence_maker.scripts.start_gentle

# Step 2: Save lyrics to file (ask for lyrics in a single step)
write_to_file sequence_projects/song_name/lyrics.txt [lyrics content]

# Step 3: Run alignment directly
python align_lyrics.py sequence_projects/song_name/artist_song_name.mp3 sequence_projects/song_name/lyrics.txt sequence_projects/song_name/lyrics_timestamps.json --song-title "[Title]" --artist-name "[Artist]"

# Step 4: Display only a sample of the results (first 5-10 timestamps)
```

### 3. Token Optimization Techniques

- **Infer metadata when possible**: Extract song title and artist from filename
- **Sample data display**: Show only 5-10 timestamps instead of the entire file
- **Direct approach**: Use align_lyrics.py directly instead of extract_lyrics.py
- **Single-step information gathering**: Ask for all needed information at once
- **Error pattern recognition**: Immediately adapt when API errors are detected

## Self-Improvement Mechanism

The system should continuously improve its efficiency by:

1. **Learning from each interaction**:
   - Identifying patterns that lead to inefficiencies
   - Documenting more efficient approaches
   - Updating workflows based on success rates

2. **Applying optimizations automatically**:
   - Using the most efficient approach first
   - Skipping steps known to fail
   - Adapting to user patterns

3. **Measuring improvement**:
   - Tracking token usage across similar tasks
   - Comparing completion time for similar requests
   - Noting reduction in error rates

## Implementation Examples

### Before Optimization

```
# Step 1: Start Gentle server
python -m sequence_maker.scripts.start_gentle

# Step 2: Ask user for song name, artist, and lyrics (multiple steps)

# Step 3: Try extract_lyrics.py first (likely to fail)
python -m roocode_sequence_designer_tools.extract_lyrics [audio_path] --lyrics-file lyrics.txt --output lyrics_timestamps.json --conservative

# Step 4: Fall back to align_lyrics.py
python align_lyrics.py [audio_path] lyrics.txt lyrics_timestamps.json --song-title "[Title]" --artist-name "[Artist]"

# Step 5: Display entire JSON file (wastes tokens)
```

### After Optimization

```
# Step 1: Check Gentle server and start if needed
python -m sequence_maker.scripts.start_gentle

# Step 2: Ask for lyrics in a single step
write_to_file sequence_projects/song_name/lyrics.txt [lyrics content]

# Step 3: Use align_lyrics.py directly
python align_lyrics.py sequence_projects/song_name/artist_song_name.mp3 sequence_projects/song_name/lyrics.txt sequence_projects/song_name/lyrics_timestamps.json --song-title "[Title]" --artist-name "[Artist]"

# Step 4: Display only first few timestamps
```

### File Organization Example

Before:
```
lyrics.txt                    # In root directory
lyrics_timestamps.json        # In root directory
sequence_projects/song_name/artist_song_name.mp3
```

After:
```
sequence_projects/song_name/artist_song_name.mp3
sequence_projects/song_name/lyrics.txt
sequence_projects/song_name/lyrics_timestamps.json
```

## Continuous Improvement

This document should be updated regularly as new efficiency patterns are discovered. The goal is to create a system that automatically applies the most efficient approach based on context and continuously improves its performance.

By following these guidelines, we can significantly reduce token usage, processing time, and error rates when extracting lyrics timestamps from audio files.