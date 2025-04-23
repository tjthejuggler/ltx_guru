#!/bin/bash

# Install MCP Servers Dependencies Script
# This script installs all the required dependencies for the Audio Analyzer and LTX Sequence Maker MCP servers

echo "Installing dependencies for Audio Analyzer MCP Server..."
cd /home/twain/.local/share/Roo-Code/MCP/audio_analyzer_mcp
pip install -e .

echo "Installing dependencies for LTX Sequence Maker MCP Server..."
cd /home/twain/.local/share/Roo-Code/MCP/ltx_sequence_maker_mcp
pip install -e .

echo "All dependencies installed successfully!"