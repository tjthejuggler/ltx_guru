# MCP Servers User Guide

This guide provides step-by-step instructions on how to set up and use the Audio Analyzer and LTX Sequence Maker MCP servers.

## Quick Start Guide

### Step 1: Install Dependencies

Run the installation script to install all required dependencies:

```bash
cd /home/twain/Projects/ltx_guru
./install_mcp_servers.sh
```

### Step 2: Start the MCP Servers

Run the start script to launch both MCP servers:

```bash
cd /home/twain/Projects/ltx_guru
./start_mcp_servers.sh
```

This will start:
- Audio Analyzer MCP Server on port 8000
- LTX Sequence Maker MCP Server on port 8001

### Step 3: Use the MCP Servers with Roo

Now you can use Roo to interact with the MCP servers. Here are some example prompts:

#### Analyze an audio file:
```
Analyze the audio file at /path/to/your/audio.mp3 and tell me about its structure.
```

#### Create a beat-synchronized color pattern:
```
Create a pulse pattern with red, green, and blue colors for the first 30 seconds of the audio file I just analyzed.
```

#### Create a section-themed color sequence:
```
Create a color sequence where the Intro is blue, Verses are red, and Choruses are green for the audio file I analyzed.
```

## Detailed Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- librosa and its dependencies (for audio analysis)

### Installation Steps

1. **Install Dependencies**

   The installation script will install all required dependencies for both MCP servers:

   ```bash
   cd /home/twain/Projects/ltx_guru
   ./install_mcp_servers.sh
   ```

   This script:
   - Installs the Audio Analyzer MCP server and its dependencies
   - Installs the LTX Sequence Maker MCP server and its dependencies

2. **Start the MCP Servers**

   The start script will launch both MCP servers:

   ```bash
   cd /home/twain/Projects/ltx_guru
   ./start_mcp_servers.sh
   ```

   This script:
   - Starts the Audio Analyzer MCP server on port 8000
   - Starts the LTX Sequence Maker MCP server on port 8001
   - Logs output to /tmp/audio_analyzer_mcp.log and /tmp/ltx_sequence_maker_mcp.log

3. **Verify the Servers are Running**

   You can check if the servers are running by:

   ```bash
   curl http://localhost:8000/sse
   curl http://localhost:8001/sse
   ```

   Or by checking the process IDs:

   ```bash
   ps aux | grep "audio_analyzer_mcp\|ltx_sequence_maker_mcp"
   ```

## Using the MCP Servers with Roo

Once the servers are running, you can use Roo to interact with them. Here's exactly what to say to Roo to perform common tasks:

### 1. Analyze an Audio File

Say to Roo:
```
Analyze the audio file at /path/to/your/audio.mp3 and tell me about its structure.
```

Roo will:
1. Use the Audio Analyzer MCP server to analyze the audio file
2. Extract beats, sections, and other musical features
3. Provide a summary of the song structure

### 2. Create a Beat-Synchronized Color Pattern

Say to Roo:
```
Create a pulse pattern with red, green, and blue colors for the first 30 seconds of the audio file I just analyzed.
```

Roo will:
1. Get the beats from the analyzed audio file
2. Use the LTX Sequence Maker MCP server to create a pulse pattern
3. Return the color segments that match the beats

### 3. Create a Section-Themed Color Sequence

Say to Roo:
```
Create a color sequence where the Intro is blue, Verses are red, and Choruses are green for the audio file I analyzed.
```

Roo will:
1. Get the sections from the analyzed audio file
2. Use the LTX Sequence Maker MCP server to apply section themes
3. Return the color segments that match the sections

### 4. Create a Custom Color Sequence

Say to Roo:
```
Create a 60-second color sequence that alternates between red, green, and blue every 2 seconds.
```

Roo will:
1. Use the LTX Sequence Maker MCP server to create a simple color sequence
2. Return the color segments with the specified duration and colors

## Troubleshooting

### MCP Servers Not Starting

If the MCP servers don't start:

1. Check the log files:
   ```bash
   tail -f /tmp/audio_analyzer_mcp.log /tmp/ltx_sequence_maker_mcp.log
   ```

2. Make sure the ports are available:
   ```bash
   lsof -i:8000
   lsof -i:8001
   ```

3. Ensure Python and dependencies are installed:
   ```bash
   python --version
   pip list | grep -E "librosa|mcp"
   ```

### Roo Can't Connect to MCP Servers

If Roo can't connect to the MCP servers:

1. Make sure the servers are running:
   ```bash
   ps aux | grep "audio_analyzer_mcp\|ltx_sequence_maker_mcp"
   ```

2. Check the MCP settings file:
   ```bash
   cat /home/twain/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json
   ```

3. Restart the MCP servers:
   ```bash
   ./start_mcp_servers.sh
   ```

### Audio Analysis Issues

If there are issues with audio analysis:

1. Make sure the audio file exists and is in a supported format (MP3, WAV, etc.)
2. Check that librosa is properly installed:
   ```bash
   pip show librosa
   ```
3. Try with a shorter audio file or a different format

## Advanced Usage

For more advanced usage and detailed documentation, refer to:
- `/home/twain/Projects/ltx_guru/mcp_servers_documentation.md`

This documentation includes:
- Detailed descriptions of all tools and their parameters
- Example workflows for creating music-synchronized color sequences
- Explanations of pattern types and energy mapping

## Stopping the MCP Servers

To stop the MCP servers:

```bash
# Find the process IDs
ps aux | grep "audio_analyzer_mcp\|ltx_sequence_maker_mcp"

# Kill the processes
kill [PID1] [PID2]
```

Or use the PID information provided when you started the servers:

```bash
kill [AUDIO_PID] [LTX_PID]