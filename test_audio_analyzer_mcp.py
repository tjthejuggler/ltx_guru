#!/usr/bin/env python3
"""
Test script for the audio-analyzer MCP server.
This script attempts to call the analyze_audio tool to test if it works or hangs.
"""

import json
import logging
import os
import requests
import sys
import time
import uuid

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_test")

# Sample audio file path - replace with an actual audio file on your system
AUDIO_FILE_PATH = "/home/twain/Projects/ltx_guru/sequence_maker/tests/resources/test_audio.mp3"

# Check if an alternative file path was provided as a command line argument
if len(sys.argv) > 1:
    AUDIO_FILE_PATH = sys.argv[1]

# Create a unique session ID
session_id = str(uuid.uuid4()).replace("-", "")

# Connect to the SSE endpoint
logger.info(f"Connecting to MCP server with session ID: {session_id}")
sse_url = f"http://localhost:8000/sse"

try:
    # Just check if the server is reachable
    logger.debug("Sending GET request to SSE endpoint")
    response = requests.get(sse_url, timeout=5)
    logger.info(f"Server connection test: {response.status_code}")
except Exception as e:
    logger.error(f"Error connecting to server: {e}")
    sys.exit(1)

# Function to call a tool
def call_tool(tool_name, arguments):
    logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")
    
    # Prepare the request
    url = f"http://localhost:8000/messages/?session_id={session_id}"
    headers = {"Content-Type": "application/json"}
    
    # Create a CallToolRequest
    payload = {
        "type": "CallToolRequest",
        "name": tool_name,
        "arguments": arguments
    }
    
    logger.debug(f"Request payload: {payload}")
    
    # Send the request with a shorter timeout (10 seconds instead of 30)
    try:
        start_time = time.time()
        logger.debug(f"Sending POST request at {start_time}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        end_time = time.time()
        logger.info(f"Received response in {end_time - start_time:.2f} seconds")
        
        if response.status_code == 202:
            logger.info("Request accepted")
            return True
        else:
            logger.error(f"Request failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        logger.error(f"Request timed out after 10 seconds")
        return False
    except Exception as e:
        logger.error(f"Error calling tool: {e}")
        return False

# First, list the available tools
logger.info("Listing available tools...")
url = f"http://localhost:8000/messages/?session_id={session_id}"
headers = {"Content-Type": "application/json"}
payload = {"type": "ListToolsRequest"}

try:
    logger.debug("Sending ListToolsRequest")
    response = requests.post(url, headers=headers, json=payload, timeout=5)
    logger.info(f"List tools response: {response.status_code}")
except Exception as e:
    logger.error(f"Error listing tools: {e}")

# Now call the analyze_audio tool
logger.info(f"\nTesting analyze_audio with file: {AUDIO_FILE_PATH}")

# Check if the file exists before trying to analyze it
if not os.path.exists(AUDIO_FILE_PATH):
    logger.error(f"Audio file does not exist: {AUDIO_FILE_PATH}")
    sys.exit(1)
else:
    logger.info(f"Audio file exists and is {os.path.getsize(AUDIO_FILE_PATH)} bytes")

result = call_tool("analyze_audio", {"audio_file_path": AUDIO_FILE_PATH})

if result:
    logger.info("Tool call completed successfully")
else:
    logger.error("Tool call failed or timed out")

logger.info("\nTest complete")