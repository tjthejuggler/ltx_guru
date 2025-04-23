#!/bin/bash

# Stop MCP Servers Script
# This script stops both the Audio Analyzer and LTX Sequence Maker MCP servers

echo "Stopping MCP servers..."

# Find and kill Audio Analyzer MCP Server
AUDIO_PIDS=$(ps aux | grep "audio_analyzer_mcp" | grep -v grep | awk '{print $2}')
if [ -n "$AUDIO_PIDS" ]; then
  echo "Stopping Audio Analyzer MCP Server (PIDs: $AUDIO_PIDS)..."
  kill $AUDIO_PIDS
  echo "Audio Analyzer MCP Server stopped."
else
  echo "Audio Analyzer MCP Server is not running."
fi

# Find and kill LTX Sequence Maker MCP Server
LTX_PIDS=$(ps aux | grep "ltx_sequence_maker_mcp" | grep -v grep | awk '{print $2}')
if [ -n "$LTX_PIDS" ]; then
  echo "Stopping LTX Sequence Maker MCP Server (PIDs: $LTX_PIDS)..."
  kill $LTX_PIDS
  echo "LTX Sequence Maker MCP Server stopped."
else
  echo "LTX Sequence Maker MCP Server is not running."
fi

echo "All MCP servers stopped."