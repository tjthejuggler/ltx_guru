#!/usr/bin/env python3
"""
Diagnostic script for testing the audio-analyzer MCP server with STDIO transport.
This script launches the server as a subprocess and communicates with it directly.
"""

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_stdio_test")

# Path to the audio file
AUDIO_FILE_PATH = str(Path(__file__).parent / "sequence_maker" / "tests" / "resources" / "test_audio.mp3")

def main():
    # Check if the audio file exists
    if not os.path.exists(AUDIO_FILE_PATH):
        logger.error(f"Audio file not found: {AUDIO_FILE_PATH}")
        return
    
    logger.info(f"Audio file exists: {AUDIO_FILE_PATH}")
    
    # Path to the MCP server
    server_path = "/home/twain/.local/share/Roo-Code/MCP/audio_analyzer_mcp"
    
    # Command to start the server
    cmd = [
        "python", "-m", "audio_analyzer_mcp",
        "--transport", "stdio"
    ]
    
    logger.info(f"Starting MCP server with command: {' '.join(cmd)}")
    
    try:
        # Start the server as a subprocess
        process = subprocess.Popen(
            cmd,
            cwd=server_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )
        
        logger.info(f"Server process started with PID: {process.pid}")
        
        # Give the server a moment to initialize
        time.sleep(1)
        
        # Check if the process is still running
        if process.poll() is not None:
            logger.error(f"Server process exited with code: {process.returncode}")
            stderr = process.stderr.read()
            logger.error(f"Server stderr: {stderr}")
            return
        
        # Send a ListToolsRequest
        list_tools_request = {
            "type": "ListToolsRequest"
        }
        
        logger.info("Sending ListToolsRequest")
        send_request(process, list_tools_request)
        
        # Read the response
        response = read_response(process)
        logger.info(f"Received response: {response}")
        
        # Send a CallToolRequest for analyze_audio
        call_tool_request = {
            "type": "CallToolRequest",
            "name": "analyze_audio",
            "arguments": {
                "audio_file_path": AUDIO_FILE_PATH
            }
        }
        
        logger.info(f"Sending CallToolRequest for analyze_audio with file: {AUDIO_FILE_PATH}")
        send_request(process, call_tool_request)
        
        # Read the response (this might take a while for audio analysis)
        logger.info("Waiting for response (this might take a while)...")
        response = read_response(process, timeout=60)
        logger.info(f"Received response: {response}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Terminate the server process
        if 'process' in locals() and process.poll() is None:
            logger.info("Terminating server process")
            process.terminate()
            process.wait(timeout=5)

def send_request(process, request):
    """Send a request to the MCP server."""
    request_json = json.dumps(request)
    logger.debug(f"Sending: {request_json}")
    process.stdin.write(request_json + "\n")
    process.stdin.flush()

def read_response(process, timeout=10):
    """Read a response from the MCP server with timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if process.stdout.readable():
            line = process.stdout.readline().strip()
            if line:
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    logger.warning(f"Received non-JSON line: {line}")
        
        # Check if the process is still running
        if process.poll() is not None:
            logger.error(f"Server process exited with code: {process.returncode}")
            stderr = process.stderr.read()
            logger.error(f"Server stderr: {stderr}")
            return None
        
        # Sleep a bit to avoid busy waiting
        time.sleep(0.1)
    
    logger.error(f"Timeout after {timeout} seconds waiting for response")
    return None

if __name__ == "__main__":
    main()