# Sequence Designer Mode Instructions

## File Organization and Types

Always organize project files in the sequence_projects directory using the following structure and file extensions:

```
sequence_projects/
└── song_name/                # Create a subdirectory for each song
    ├── artist_song_name.mp3  # Original audio file
    ├── lyrics.txt            # Raw lyrics text file
    ├── lyrics.json           # Timestamped lyrics
    ├── song_name.ball.json   # Ball sequence file
    ├── song_name.seqdesign.json # Sequence design file
    └── song_name.prg.json    # Compiled program file
```

### File Types and Extensions

| File Type | Extension | Description |
|-----------|-----------|-------------|
| Sequence Design Files | `.seqdesign.json` | High-level sequence design files |
| PRG JSON Files | `.prg.json` | Compiled program files for LTX balls |
| Ball Sequence Files | `.ball.json` | Single ball color sequences |
| Lyrics Timestamps | `.lyrics.json` | Timestamped/aligned lyrics |
| Audio Analysis Reports | `.analysis.json` | Audio analysis data |

This organization:
- Keeps all related files together in one place
- Makes it easier to find and manage project files
- Prevents clutter in the root directory
- Simplifies backup and sharing of complete projects

## Lyrics Processing Workflow

When extracting lyrics timestamps from audio files, follow this optimized workflow and maintain proper file organization:

### RECOMMENDED APPROACH: Using align_lyrics.py (Most Efficient)

The most efficient approach is to use the direct align_lyrics.py tool:

1. **Check Gentle server first**:
   - ALWAYS check if the Gentle server is running before attempting lyrics alignment
   - Run: `python -m sequence_maker.scripts.start_gentle`
   - This step is essential and will save significant time and tokens

2. **Ask for necessary information in a single step**:
   - Ask for the complete lyrics text in one prompt
   - Song title and artist can often be inferred from the filename

3. **Use the align_lyrics.py tool directly**:
   - Save user-provided lyrics to a text file in the same directory as the MP3 file
   - Run the align_lyrics.py tool which handles everything in one step:
   ```bash
   python align_lyrics.py sequence_projects/song_name/artist_song_name.mp3 sequence_projects/song_name/lyrics.txt sequence_projects/song_name/lyrics_timestamps.json --song-title "Song Title" --artist-name "Artist Name"
   ```
   - This tool automatically:
     - Ensures the Gentle server is running
     - Uses conservative alignment for better results
     - Handles all the alignment process in one command

4. **Present results efficiently**:
   - Show only the first 5-10 timestamps that were generated
   - NEVER display the entire JSON file (wastes tokens)
   - If the process fails, clearly explain what happened and what's needed next

### ALTERNATIVE APPROACH: Using extract_lyrics.py

Only use this approach if align_lyrics.py is not available:

1. **Check Prerequisites First**:
   - **CRITICAL**: Check if the Gentle Docker container is running before attempting lyrics alignment
   - If not running, start it immediately with: `python -m sequence_maker.scripts.start_gentle`

2. **Skip automatic identification**:
   - Do not waste time with automatic song identification - it requires API keys that are likely missing
   - Immediately ask the user for the complete lyrics text

3. **Generate timestamps directly**:
   - Save user-provided lyrics to a text file in the same directory as the MP3 file
   - Use extract_lyrics.py with the `--conservative` flag
   - Command: `python -m roocode_sequence_designer_tools.extract_lyrics sequence_projects/song_name/artist_song_name.mp3 --lyrics-file sequence_projects/song_name/lyrics.txt --output sequence_projects/song_name/lyrics_timestamps.json --conservative`

## Token Efficiency Guidelines

1. **Minimize token usage**:
   - NEVER read or display the entire JSON output - only show a small sample
   - Ask for all needed information in a single step
   - Use the most direct approach (align_lyrics.py) whenever possible

2. **Recognize common errors**:
   - If you see API key errors, immediately ask for lyrics
   - Don't waste tokens explaining technical details unless requested

3. **Optimize workflow**:
   - Start Gentle server first
   - Use align_lyrics.py directly
   - Infer song title and artist from filename when possible
   - Save lyrics to file and process in one step
   - Always store related files in the same subdirectory as the MP3 file

## Self-Improvement Mechanism

After completing any task:

1. **Analyze efficiency**:
   - Identify steps that could have been skipped or optimized
   - Note patterns that could be improved in future interactions

2. **Update knowledge base**:
   - Document more efficient approaches
   - Focus on reducing token usage and number of steps

3. **Apply learnings**:
   - Use the most efficient approach first in future interactions
   - Continuously refine your workflow based on experience

## Additional Resources

For more detailed information about lyrics extraction and alignment, refer to:
- [Lyrics Extraction Guide](lyrics_extraction_guide.md) - Comprehensive documentation on all lyrics extraction tools
- [Lyrics Extraction Efficiency](lyrics_extraction_efficiency.md) - Best practices for efficient lyrics extraction

Remember that the sequence maker tools are designed to handle this workflow efficiently when used correctly. Following these optimized instructions will significantly reduce time and token usage.

## File Organization Examples

### Correct Organization

```
sequence_projects/
└── you_know_me/
    ├── lubalin_you_know_me.mp3
    ├── lyrics.txt
    ├── lyrics.json
    ├── you_know_me.ball.json
    ├── you_know_me.seqdesign.json
    └── you_know_me.prg.json
```

### Incorrect Organization

```
sequence_projects/you_know_me/lubalin_you_know_me.mp3
lyrics.txt                    # In root directory
lyrics.json                   # In root directory
you_know_me.ball.json         # In root directory
```

Always maintain proper file organization to keep projects clean and manageable.