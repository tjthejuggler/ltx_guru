# Sequence Designer Mode Instructions

## Lyrics Processing Workflow

When extracting lyrics timestamps from audio files, follow this optimized workflow:

1. **Check Prerequisites First**:
   - **CRITICAL**: Check if the Gentle Docker container is running before attempting lyrics alignment
   - If not running, start it immediately with: `python -m sequence_maker.scripts.start_gentle`
   - This step is essential and will save significant time and tokens

2. **Identify the song and artist**:
   - First attempt to automatically detect the song name and artist using the extract_lyrics.py tool
   - If automatic detection fails (which is likely if API keys are missing), immediately ask the user for:
     1. The song name and artist
     2. The complete lyrics text
   - Do not waste time with multiple attempts if API keys are missing

3. **Generate timestamps directly**:
   - Save user-provided lyrics to a text file
   - Use extract_lyrics.py with the `--conservative` flag (this is crucial for successful alignment)
   - Command: `python -m roocode_sequence_designer_tools.extract_lyrics path/to/audio.mp3 --lyrics-file lyrics.txt --output lyrics_timestamps.json --conservative`

4. **Present results**:
   - Show the user the timestamps that were generated
   - If the process fails, clearly explain what happened and what's needed next

## API Keys and Common Issues

The lyrics processing functionality requires API keys to work properly:

1. **API Keys Status Check**:
   - If you see "API keys file not found" or "Missing ACRCloud API keys" messages, assume automatic identification won't work
   - Skip directly to asking the user for lyrics rather than attempting multiple approaches
   - This saves significant time and tokens

2. **Gentle Server Requirements**:
   - The Gentle server must be running for lyrics alignment to work
   - If you see "Connection refused" errors when connecting to localhost:8765, the Gentle server is not running
   - Always start the Gentle server first before attempting lyrics alignment

3. **Conservative Alignment**:
   - Always use the `--conservative` flag with extract_lyrics.py when providing user lyrics
   - This significantly improves alignment success rates and prevents wasted attempts

## Optimized Command Sequence

For maximum efficiency, use this exact sequence of commands:

```bash
# Step 1: Start the Gentle server (ALWAYS do this first)
python -m sequence_maker.scripts.start_gentle

# Step 2: Save user-provided lyrics to a file
# (Ask for lyrics immediately if you see API key errors)

# Step 3: Run extraction with conservative alignment
python -m roocode_sequence_designer_tools.extract_lyrics path/to/audio.mp3 --lyrics-file lyrics.txt --output lyrics_timestamps.json --conservative
```

## Important Guidelines

- **Be direct and efficient**: Ask for all needed information upfront rather than in multiple steps
- **Recognize common errors**: If you see API key errors, immediately ask for lyrics
- **Use the conservative flag**: Always include `--conservative` when aligning user-provided lyrics
- **Start Gentle first**: Always ensure the Gentle server is running before attempting alignment
- **Check cached analysis**: Look for existing analysis files before running new analyses
- **Avoid unnecessary explanations**: Focus on getting the task done with minimal token usage

Remember that the sequence maker tools are designed to handle this workflow efficiently when used correctly. Following these optimized instructions will significantly reduce time and token usage.