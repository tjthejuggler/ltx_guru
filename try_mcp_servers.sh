#!/bin/bash

# Try MCP Servers Script
# This script installs dependencies, starts the MCP servers, and runs the example script

# Function to check if a server is running
check_server() {
    local url=$1
    local max_attempts=$2
    local attempt=1
    
    echo "Checking if server is running at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url/sse" > /dev/null 2>&1; then
            echo "Server is running at $url"
            return 0
        fi
        
        echo "Attempt $attempt/$max_attempts: Server not responding yet, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "Server at $url is not responding after $max_attempts attempts"
    return 1
}

# Function to handle errors
handle_error() {
    echo "ERROR: $1"
    echo "Please check the logs for more information:"
    echo "  Audio Analyzer MCP: /tmp/audio_analyzer_mcp.log"
    echo "  LTX Sequence Maker MCP: /tmp/ltx_sequence_maker_mcp.log"
    exit 1
}

echo "===== LTX Guru MCP Servers Demo ====="
echo ""

# Check which audio file to use
LUBALIN_AUDIO="lubalin_you_know_me.mp3"
TEST_AUDIO="sequence_maker/tests/resources/test_audio.mp3"
EMPTY_AUDIO="empty_10s.mp3"

if [ -f "$LUBALIN_AUDIO" ]; then
    AUDIO_FILE="$LUBALIN_AUDIO"
    echo "Using audio file: $AUDIO_FILE"
elif [ -f "$TEST_AUDIO" ]; then
    AUDIO_FILE="$TEST_AUDIO"
    echo "Using audio file: $AUDIO_FILE"
elif [ -f "$EMPTY_AUDIO" ]; then
    AUDIO_FILE="$EMPTY_AUDIO"
    echo "Using audio file: $AUDIO_FILE"
else
    handle_error "No suitable audio file found"
fi

# Step 1: Install dependencies
echo "Step 1: Installing dependencies..."
./install_mcp_servers.sh || handle_error "Failed to install dependencies"
echo ""

# Step 2: Start the MCP servers
echo "Step 2: Starting MCP servers..."
./start_mcp_servers.sh || handle_error "Failed to start MCP servers"
echo ""

# Wait for servers to fully start
echo "Waiting for servers to start..."
if ! check_server "http://localhost:8000" 10; then
    handle_error "Audio Analyzer MCP server failed to start"
fi

if ! check_server "http://localhost:8001" 10; then
    handle_error "LTX Sequence Maker MCP server failed to start"
fi
echo "Both servers are running!"
echo ""

# Step 3: Run the example script
echo "Step 3: Running example script..."
python example_usage.py "$AUDIO_FILE" || handle_error "Example script failed"
echo ""

# Check if the color sequence was generated
if [ ! -f "color_sequence.json" ]; then
    handle_error "Color sequence file was not generated"
fi

# Show the generated color sequence
echo "Generated color sequence:"
cat color_sequence.json | head -n 20
echo "..."
echo ""

# Provide instructions for next steps
echo "===== Next Steps ====="
echo "1. The MCP servers are now running in the background."
echo "2. You can use Roo to interact with them using prompts like:"
echo "   'Analyze the audio file at /home/twain/Projects/ltx_guru/$AUDIO_FILE and tell me about its structure.'"
echo "3. You can also try with your own audio files:"
echo "   'Analyze the audio file at /path/to/your/audio.mp3 and tell me about its structure.'"
echo "4. When you're done, stop the servers with:"
echo "   ./stop_mcp_servers.sh"
echo ""
echo "For more information, see README_MCP_SERVERS.md"