#!/bin/bash

# Start MCP Servers Script
# This script starts both the Audio Analyzer and LTX Sequence Maker MCP servers

# Function to check if a port is in use
port_in_use() {
  lsof -i:$1 >/dev/null 2>&1
  return $?
}

# Kill any existing processes on the ports we want to use
if port_in_use 8000; then
  echo "Port 8000 is in use. Killing the process..."
  kill $(lsof -t -i:8000) 2>/dev/null
fi

if port_in_use 8001; then
  echo "Port 8001 is in use. Killing the process..."
  kill $(lsof -t -i:8001) 2>/dev/null
fi

# Start the Audio Analyzer MCP Server
echo "Starting Audio Analyzer MCP Server on port 8000..."
cd /home/twain/.local/share/Roo-Code/MCP/audio_analyzer_mcp
python -m audio_analyzer_mcp --transport sse --port 8000 > /tmp/audio_analyzer_mcp.log 2>&1 &
AUDIO_PID=$!
echo "Audio Analyzer MCP Server started with PID: $AUDIO_PID"

# Wait a moment to ensure the first server starts properly
sleep 2

# Start the LTX Sequence Maker MCP Server
echo "Starting LTX Sequence Maker MCP Server on port 8001..."
cd /home/twain/.local/share/Roo-Code/MCP/ltx_sequence_maker_mcp
python -m ltx_sequence_maker_mcp --transport sse --port 8001 > /tmp/ltx_sequence_maker_mcp.log 2>&1 &
LTX_PID=$!
echo "LTX Sequence Maker MCP Server started with PID: $LTX_PID"

echo "Both MCP servers are now running!"
echo "Audio Analyzer MCP Server: http://localhost:8000/sse"
echo "LTX Sequence Maker MCP Server: http://localhost:8001/sse"
echo ""
echo "To stop the servers, run: kill $AUDIO_PID $LTX_PID"
echo "To view the logs, run: tail -f /tmp/audio_analyzer_mcp.log /tmp/ltx_sequence_maker_mcp.log"