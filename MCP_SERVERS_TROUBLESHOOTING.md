# MCP Servers Troubleshooting Guide

This guide provides solutions for common issues you might encounter when using the Audio Analyzer and LTX Sequence Maker MCP servers.

## Common Issues and Solutions

### 1. MCP Servers Won't Start

**Symptoms:**
- Error messages when running `./start_mcp_servers.sh`
- The servers start but immediately stop
- You see "Server not responding" messages

**Solutions:**
- Check if the ports are already in use:
  ```bash
  lsof -i:8000
  lsof -i:8001
  ```
  If they are, kill those processes or use different ports.

- Check the log files for errors:
  ```bash
  tail -f /tmp/audio_analyzer_mcp.log
  tail -f /tmp/ltx_sequence_maker_mcp.log
  ```

- Make sure all dependencies are installed:
  ```bash
  ./install_mcp_servers.sh
  ```

- Try stopping any running servers first:
  ```bash
  ./stop_mcp_servers.sh
  ```

### 2. JSON Decode Errors or "session_id is required" Errors

**Symptoms:**
- Error messages like `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`
- Error messages like `Error: Invalid JSON response from server: session_id is required`
- The example script fails with HTTP errors

**Solutions:**
- Make sure the servers are actually running:
  ```bash
  ps aux | grep "audio_analyzer_mcp\|ltx_sequence_maker_mcp"
  ```

- Check if the servers are responding:
  ```bash
  curl http://localhost:8000/sse
  curl http://localhost:8001/sse
  ```

- Restart the servers and wait longer for them to start:
  ```bash
  ./stop_mcp_servers.sh
  ./start_mcp_servers.sh
  sleep 10  # Wait 10 seconds
  ```

- Try using the improved example script which has better error handling and properly initializes sessions:
  ```bash
  python example_usage.py lubalin_you_know_me.mp3
  ```

- The "session_id is required" error occurs when the MCP protocol isn't being followed correctly. The latest version of the example script fixes this by properly initializing a session with the MCP server before making tool calls.

### 3. Audio Analysis Fails

**Symptoms:**
- Error messages about audio file not found
- Error messages from librosa or other audio processing libraries
- Empty or incomplete analysis results

**Solutions:**
- Make sure the audio file exists and is in a supported format:
  ```bash
  file /path/to/your/audio.mp3
  ```

- Try using one of the known working audio files:
  ```bash
  python example_usage.py lubalin_you_know_me.mp3
  ```
  or
  ```bash
  python example_usage.py sequence_maker/tests/resources/test_audio.mp3
  ```

- Check if librosa is properly installed:
  ```bash
  pip show librosa
  ```

- For large audio files, try using a shorter clip:
  ```bash
  ffmpeg -i input.mp3 -t 60 output.mp3  # Create a 60-second clip
  ```

### 4. Roo Can't Connect to MCP Servers

**Symptoms:**
- Roo says it can't connect to the MCP servers
- Roo doesn't recognize the MCP tools

**Solutions:**
- Make sure the MCP settings file is correctly configured:
  ```bash
  cat /home/twain/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/mcp_settings.json
  ```

- Check if the servers are running:
  ```bash
  ps aux | grep "audio_analyzer_mcp\|ltx_sequence_maker_mcp"
  ```

- Restart VS Code to reload the MCP settings

- Try using the example script first to verify the servers are working:
  ```bash
  python example_usage.py lubalin_you_know_me.mp3
  ```

## Advanced Troubleshooting

### Checking Server Logs

The MCP servers write logs to these files:
- Audio Analyzer MCP: `/tmp/audio_analyzer_mcp.log`
- LTX Sequence Maker MCP: `/tmp/ltx_sequence_maker_mcp.log`

You can view these logs with:
```bash
tail -f /tmp/audio_analyzer_mcp.log
```

### Manually Starting Servers

If the start script isn't working, you can try starting the servers manually:

```bash
cd /home/twain/.local/share/Roo-Code/MCP/audio_analyzer_mcp
python -m audio_analyzer_mcp --transport sse --port 8000 > /tmp/audio_analyzer_mcp.log 2>&1 &

cd /home/twain/.local/share/Roo-Code/MCP/ltx_sequence_maker_mcp
python -m ltx_sequence_maker_mcp --transport sse --port 8001 > /tmp/ltx_sequence_maker_mcp.log 2>&1 &
```

### Reinstalling from Scratch

If all else fails, you can try reinstalling everything from scratch:

1. Stop any running servers:
   ```bash
   ./stop_mcp_servers.sh
   ```

2. Reinstall the dependencies:
   ```bash
   pip uninstall -y audio_analyzer_mcp ltx_sequence_maker_mcp
   ./install_mcp_servers.sh
   ```

3. Start the servers:
   ```bash
   ./start_mcp_servers.sh
   ```

## Alternative: Simple Example Without MCP Servers

If you're continuing to have issues with the MCP servers, we've provided a simple example that doesn't rely on them:

```bash
python simple_example.py lubalin_you_know_me.mp3
```

This script:
1. Analyzes an audio file using librosa directly
2. Extracts beats and sections
3. Creates beat-synchronized color patterns
4. Saves the resulting color sequences to JSON files
5. Generates visualizations of the color patterns

It provides the same core functionality without the complexity of the MCP servers and is a good fallback option if you can't get the MCP servers working.

## Getting Help

If you're still having issues, check the following resources:
- `README_MCP_SERVERS.md` - Main README with an overview
- `GETTING_STARTED.md` - Step-by-step instructions for beginners
- `MCP_SERVERS_USER_GUIDE.md` - Comprehensive user guide
- `mcp_servers_documentation.md` - Detailed technical documentation