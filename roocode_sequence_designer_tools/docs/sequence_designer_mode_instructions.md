# Sequence Designer Mode Instructions

## Lyrics Processing Workflow

When extracting lyrics timestamps from audio files, follow this exact workflow:

1. **Identify the song and artist**:
   - First attempt to automatically detect the song name and artist using the extract_lyrics.py tool
   - If automatic detection fails, immediately ask the user for the song name and artist
   - Do not create placeholder content or make assumptions

2. **Obtain the lyrics**:
   - With song name and artist, attempt to automatically retrieve lyrics
   - If automatic retrieval fails, immediately ask the user to provide the lyrics
   - Do not create placeholder lyrics or sample text

3. **Generate timestamps**:
   - Use the existing extract_lyrics.py tool with the provided lyrics to generate timestamps
   - Do not write custom Python scripts or create new tools unless absolutely necessary

4. **Present results**:
   - Show the user the timestamps that were generated
   - If the process fails at any point, clearly explain what happened and what's needed next

## API Keys Requirements

The lyrics processing functionality requires API keys to work properly:

1. **API Keys Location**:
   - The system looks for API keys at: `~/.ltx_sequence_maker/api_keys.json`
   - Alternative location: `~/.config/ltx_sequence_maker/api_keys.json`

2. **Required API Keys**:
   - `acr_access_key`: For ACRCloud song identification
   - `acr_secret_key`: For ACRCloud song identification
   - `acr_host`: For ACRCloud host URL
   - `genius_api_key`: For Genius lyrics retrieval

3. **Error Handling**:
   - If API keys are missing, the system will report this in the logs
   - When this happens, immediately ask the user for the required information (song name, artist, lyrics)
   - Do not attempt to create workarounds or alternative solutions

## Important Guidelines

- **Use existing tools**: Always use the tools that are already available in the roocode_sequence_designer_tools directory
- **Don't create unnecessary files**: Avoid creating Python scripts or other files in the song directories
- **Follow established patterns**: Look at examples in the codebase to understand the correct workflow
- **Be efficient**: Don't waste tokens on unnecessary steps or explanations
- **Ask directly**: When user input is needed, ask clearly and directly
- **No placeholders**: Never use placeholder content when real content is needed

## Tool Usage Examples

### Correct Lyrics Extraction Workflow

```bash
# Step 1: Try to identify song and get lyrics
python -m roocode_sequence_designer_tools.extract_lyrics path/to/audio.mp3 --output lyrics_data.json

# Step 2: If identification fails, ask user for lyrics and then run:
python -m roocode_sequence_designer_tools.extract_lyrics path/to/audio.mp3 --lyrics-file user_provided_lyrics.txt --output lyrics_data.json
```

### Checking API Keys Status

If you suspect API keys might be missing, you can check the error messages in the output. Look for messages like:
- "API keys file not found at /home/twain/.ltx_sequence_maker/api_keys.json"
- "Missing ACRCloud API keys, cannot identify song"
- "Missing Genius API key, cannot fetch lyrics"

When you see these messages, immediately ask the user for the required information rather than attempting complex workarounds.

Remember that the sequence maker tools are designed to handle this workflow efficiently. Trust the existing tools and processes rather than creating new ones.