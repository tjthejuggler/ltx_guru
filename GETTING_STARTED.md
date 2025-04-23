# Getting Started with MCP Servers

This guide provides the exact steps to set up and use the Audio Analyzer and LTX Sequence Maker MCP servers.

## Quickest Way to Get Started

If you want to try everything with a single command, run:

```bash
cd /home/twain/Projects/ltx_guru
./try_mcp_servers.sh
```

This script will:
1. Install all dependencies
2. Start both MCP servers
3. Run the example script with the test audio file
4. Show you the next steps

## Step-by-Step Instructions

If you prefer to go through each step individually, follow the instructions below.

## Step 1: Install Dependencies

Run this command in your terminal:

```bash
cd /home/twain/Projects/ltx_guru
./install_mcp_servers.sh
```

## Step 2: Start the MCP Servers

Run this command in your terminal:

```bash
cd /home/twain/Projects/ltx_guru
./start_mcp_servers.sh
```

You should see output indicating that both servers have started successfully.

## Step 3: Try the Example Script

To test that everything is working, run the example script with one of the included audio files:

```bash
cd /home/twain/Projects/ltx_guru
python example_usage.py /home/twain/Projects/ltx_guru/sequence_maker/tests/resources/test_audio.mp3
```

You can also use any of these other audio files that are included in the project:
- `/home/twain/Projects/ltx_guru/empty_10s.mp3` - A 10-second empty audio file
- `/home/twain/Projects/ltx_guru/lubalin_you_know_me.mp3` - The Lubalin "You Know Me" audio file

The script will:
1. Analyze the audio file
2. Get the beats in the first 30 seconds
3. Create a beat-synchronized color pattern
4. Save the resulting color sequence to `color_sequence.json`

## Step 4: Use with Roo

Now you can use Roo to interact with the MCP servers. Here are some exact phrases to use:

### To analyze an audio file:

```
Analyze the audio file at /home/twain/Projects/ltx_guru/lubalin_you_know_me.mp3 and tell me about its structure.
```

### To create a beat-synchronized color pattern:

```
Create a pulse pattern with red, green, and blue colors for the first 30 seconds of the audio file at /home/twain/Projects/ltx_guru/lubalin_you_know_me.mp3.
```

### To create a section-themed color sequence:

```
Create a color sequence where the Intro is blue, Verses are red, and Choruses are green for the audio file at /home/twain/Projects/ltx_guru/lubalin_you_know_me.mp3.
```

## Troubleshooting

If you encounter any issues, please refer to the [Troubleshooting Guide](MCP_SERVERS_TROUBLESHOOTING.md) for detailed solutions to common problems.

Here are some quick troubleshooting steps:

1. Make sure both servers are running:
   ```bash
   ps aux | grep "audio_analyzer_mcp\|ltx_sequence_maker_mcp"
   ```

2. Check the log files:
   ```bash
   tail -f /tmp/audio_analyzer_mcp.log /tmp/ltx_sequence_maker_mcp.log
   ```

3. Restart the servers:
   ```bash
   cd /home/twain/Projects/ltx_guru
   ./stop_mcp_servers.sh
   ./start_mcp_servers.sh
   ```

## Stopping the MCP Servers

When you're done using the MCP servers, you can stop them using the stop script:

```bash
cd /home/twain/Projects/ltx_guru
./stop_mcp_servers.sh
```

This will find and stop all running MCP server processes.

## Alternative: Simple Example Without MCP Servers

If you're having trouble with the MCP servers, you can try the simple example that doesn't rely on them:

```bash
cd /home/twain/Projects/ltx_guru
python simple_example.py lubalin_you_know_me.mp3
```

This script provides the same core functionality (audio analysis and color sequence generation) without the complexity of the MCP servers. It also creates visualizations of the color patterns as PNG files.

## Next Steps

For more detailed information, refer to:
- `MCP_SERVERS_USER_GUIDE.md` - Comprehensive user guide
- `mcp_servers_documentation.md` - Detailed technical documentation