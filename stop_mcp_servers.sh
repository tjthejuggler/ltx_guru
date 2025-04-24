#!/bin/bash

# Stop MCP Servers Script
# This script stops both the Audio Analyzer and LTX Sequence Maker MCP servers

echo "Stopping MCP servers..."

# Function to kill processes with increasing force
kill_processes() {
  local process_name=$1
  local grep_pattern=$2
  
  # First attempt with SIGTERM (graceful shutdown)
  local PIDS=$(ps aux | grep "$grep_pattern" | grep -v grep | awk '{print $2}')
  if [ -n "$PIDS" ]; then
    echo "Stopping $process_name (PIDs: $PIDS)..."
    kill $PIDS
    
    # Wait for processes to terminate
    echo "Waiting for processes to terminate..."
    sleep 2
    
    # Check if processes are still running
    PIDS=$(ps aux | grep "$grep_pattern" | grep -v grep | awk '{print $2}')
    if [ -n "$PIDS" ]; then
      echo "Some processes are still running. Using SIGKILL..."
      kill -9 $PIDS
      sleep 1
    fi
    
    # Final check
    PIDS=$(ps aux | grep "$grep_pattern" | grep -v grep | awk '{print $2}')
    if [ -n "$PIDS" ]; then
      echo "WARNING: Some $process_name processes (PIDs: $PIDS) could not be terminated!"
    else
      echo "$process_name stopped successfully."
    fi
  else
    echo "$process_name is not running."
  fi
}

# Kill all Audio Analyzer MCP Server processes
kill_processes "Audio Analyzer MCP Server" "audio_analyzer_mcp"

# Kill all LTX Sequence Maker MCP Server processes
kill_processes "LTX Sequence Maker MCP Server" "ltx_sequence_maker_mcp"

# Kill any processes using the MCP ports
echo "Checking for processes using MCP ports..."
PORT_8000_PID=$(lsof -t -i:8000 2>/dev/null)
if [ -n "$PORT_8000_PID" ]; then
  echo "Killing process using port 8000 (PID: $PORT_8000_PID)..."
  kill -9 $PORT_8000_PID
fi

PORT_8001_PID=$(lsof -t -i:8001 2>/dev/null)
if [ -n "$PORT_8001_PID" ]; then
  echo "Killing process using port 8001 (PID: $PORT_8001_PID)..."
  kill -9 $PORT_8001_PID
fi

echo "All MCP servers stopped."