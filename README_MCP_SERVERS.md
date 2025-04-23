# LTX Guru MCP Servers

This project provides two MCP (Model Context Protocol) servers that extend the capabilities of AI assistants like Roo to work with audio analysis and color sequence generation:

1. **Audio Analyzer MCP Server**: Analyzes audio files to extract musical features like beats, sections, and energy levels.
2. **LTX Sequence Maker MCP Server**: Creates color sequences synchronized to music based on the analysis data.

## Quick Start

### One-Command Demo

To try everything with a single command:

```bash
./try_mcp_servers.sh
```

This script will install dependencies, start the MCP servers, run the example script, and provide instructions for next steps.

### Step-by-Step Approach

Alternatively, follow these steps to get started:

1. **Install Dependencies**:
   ```bash
   ./install_mcp_servers.sh
   ```

   Alternatively, you can install the dependencies manually:
   ```bash
   pip install -r mcp_servers_requirements.txt
   ```

2. **Start the MCP Servers**:
   ```bash
   ./start_mcp_servers.sh
   ```

3. **Try the Example Script**:
   ```bash
   python example_usage.py lubalin_you_know_me.mp3
   ```

   You can also use any of these other audio files:
   - `sequence_maker/tests/resources/test_audio.mp3`
   - `empty_10s.mp3`

## Alternative: Simple Example Without MCP Servers

If you're having trouble with the MCP servers, you can try the simple example that doesn't rely on them:

```bash
python simple_example.py lubalin_you_know_me.mp3
```

This script:
1. Analyzes an audio file using librosa directly
2. Extracts beats and sections
3. Creates beat-synchronized color patterns
4. Saves the resulting color sequences to JSON files
5. Generates visualizations of the color patterns

It provides the same core functionality without the complexity of the MCP servers.

4. **Stop the MCP Servers** when you're done:
   ```bash
   ./stop_mcp_servers.sh
   ```

## Documentation

- [Getting Started Guide](GETTING_STARTED.md) - Step-by-step instructions for beginners
- [User Guide](MCP_SERVERS_USER_GUIDE.md) - Comprehensive user guide
- [Technical Documentation](mcp_servers_documentation.md) - Detailed technical documentation

## Scripts

- `install_mcp_servers.sh` - Installs all required dependencies
- `start_mcp_servers.sh` - Starts both MCP servers
- `stop_mcp_servers.sh` - Stops both MCP servers
- `example_usage.py` - Example script demonstrating how to use the MCP servers

## Using with Roo

Once the servers are running, you can use Roo to interact with them. For example:

```
Analyze the audio file at /home/twain/Projects/ltx_guru/lubalin_you_know_me.mp3 and tell me about its structure.
```

## Server Locations

- Audio Analyzer MCP: `/home/twain/.local/share/Roo-Code/MCP/audio_analyzer_mcp`
- LTX Sequence Maker MCP: `/home/twain/.local/share/Roo-Code/MCP/ltx_sequence_maker_mcp`

## Troubleshooting

If you encounter any issues, refer to the [Troubleshooting Guide](MCP_SERVERS_TROUBLESHOOTING.md) for solutions to common problems.

You can also check the [User Guide](MCP_SERVERS_USER_GUIDE.md) for more detailed information.