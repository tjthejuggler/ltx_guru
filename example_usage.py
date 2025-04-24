#!/usr/bin/env python3
"""
Example script demonstrating how to use the Audio Analyzer and LTX Sequence Maker MCP servers.

This script:
1. Checks if the MCP servers are running
2. Analyzes an audio file
3. Gets the beats in a specific range
4. Creates a beat-synchronized color pattern
5. Saves the resulting color sequence to a JSON file

Usage:
    python example_usage.py /path/to/your/audio.mp3
"""

import sys
import json
import os
import requests
import time
import subprocess
import uuid
import logging
import re
import threading
import queue
import sseclient  # You may need to install this: pip install sseclient-py

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("example_usage")

def check_server_running(url):
    """Check if a server is running at the given URL."""
    try:
        response = requests.get(url, timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def start_servers():
    """Start the MCP servers if they're not already running."""
    print("Starting MCP servers...")
    try:
        # Use subprocess to run the start_mcp_servers.sh script
        subprocess.run(["./stop_mcp_servers.sh"], check=True)
        subprocess.run(["./start_mcp_servers.sh"], check=True)
        # Wait for servers to start
        print("Waiting for servers to start...")
        time.sleep(5)
    except subprocess.CalledProcessError as e:
        print(f"Error starting MCP servers: {e}")
        return False
    return True

class MCPClient:
    """A client for interacting with MCP servers."""
    
    def __init__(self, server_url):
        self.server_url = server_url
        self.client_session_id = str(uuid.uuid4())
        self.server_session_id = None
        self.response_queue = queue.Queue()
        self.sse_thread = None
        self.sse_client = None
        self.sse_response = None
        self.request_id = 0
        logger.debug(f"Created session with ID: {self.client_session_id}")
        
    def _sse_listener(self):
        """Listen for SSE events in a separate thread."""
        try:
            for event in self.sse_client.events():
                logger.debug(f"Received SSE event: {event.data}")
                
                # Check if this is the initial endpoint event
                if event.data.startswith('/messages/'):
                    # Extract the server session ID from the event data
                    match = re.search(r'session_id=([a-zA-Z0-9]+)', event.data)
                    if match:
                        self.server_session_id = match.group(1)
                        logger.debug(f"Extracted server session ID: {self.server_session_id}")
                else:
                    # Try to parse the event data as JSON
                    try:
                        data = json.loads(event.data)
                        # Check if this is a response to a request
                        if "id" in data and "result" in data:
                            logger.debug(f"Received response: {data}")
                            self.response_queue.put(data)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse event data as JSON: {event.data}")
        except Exception as e:
            logger.error(f"Error in SSE listener thread: {e}")
        
    def initialize_session(self):
        """Initialize a session with the MCP server."""
        try:
            # Connect to the SSE endpoint with the session_id
            sse_url = f"{self.server_url}?session_id={self.client_session_id}"
            logger.debug(f"Connecting to SSE endpoint: {sse_url}")
            
            # Create an SSE client
            headers = {"Accept": "text/event-stream"}
            self.sse_response = requests.get(sse_url, stream=True, headers=headers)
            
            if self.sse_response.status_code != 200:
                logger.error(f"Failed to connect to SSE endpoint: {self.sse_response.status_code}")
                return False
                
            # Create an SSE client
            self.sse_client = sseclient.SSEClient(self.sse_response)
            
            # Start a thread to listen for SSE events
            self.sse_thread = threading.Thread(target=self._sse_listener)
            self.sse_thread.daemon = True
            self.sse_thread.start()
            
            # Wait for the server session ID to be extracted
            timeout = 10  # seconds
            start_time = time.time()
            while not self.server_session_id and time.time() - start_time < timeout:
                time.sleep(0.1)
                
            if not self.server_session_id:
                logger.error("Failed to extract server session ID from SSE event")
                return False
                
            # Send an initialize request
            self.request_id += 1
            payload = {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "method": "initialize",
                "params": {
                    "session_id": self.server_session_id,
                    "client_info": {
                        "name": "example_usage.py",
                        "version": "1.0.0"
                    }
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Extract the base URL without the /sse part
            base_url = self.server_url.replace("/sse", "")
            
            # Send the request to the /messages/ endpoint with the server session ID
            url = f"{base_url}/messages/?session_id={self.server_session_id}"
            logger.debug(f"Sending initialize request to: {url}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                url, 
                json=payload, 
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"Initialize response status: {response.status_code}")
            logger.debug(f"Initialize response: {response.text}")
            
            return True
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            return False
    
    def call_tool(self, tool_name, arguments):
        """Call an MCP tool and return the result."""
        if not self.server_session_id:
            logger.error("No server session ID available. Initialize session first.")
            return None
            
        self.request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",  # Correct method name according to the error logs
            "params": {
                "session_id": self.server_session_id,
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Extract the base URL without the /sse part
        base_url = self.server_url.replace("/sse", "")
        
        try:
            logger.debug(f"Calling tool: {tool_name}")
            logger.debug(f"Arguments: {json.dumps(arguments, indent=2)}")
            
            # Send the request to the /messages/ endpoint with the server session ID
            url = f"{base_url}/messages/?session_id={self.server_session_id}"
            logger.debug(f"Sending request to: {url}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                url, 
                json=payload, 
                headers=headers,
                timeout=30
            )
            
            # Print the raw response for debugging
            logger.debug(f"Raw response: {response.text}")
            logger.debug(f"Response status: {response.status_code}")
            
            # If the response is 202 Accepted, wait for the actual response from the SSE connection
            if response.status_code == 202:
                logger.debug("Request accepted, waiting for response from SSE connection...")
                
                # Wait for the response from the SSE connection
                try:
                    # Wait up to 60 seconds for a response
                    response_data = self.response_queue.get(timeout=60)
                    logger.debug(f"Received response from SSE connection: {response_data}")
                    
                    # Extract the text content from the result
                    content = response_data["result"]["content"][0]["text"]
                    return json.loads(content)
                except queue.Empty:
                    logger.error("Timed out waiting for response from SSE connection")
                    return None
            else:
                # Check if the response is valid JSON
                try:
                    response_data = response.json()
                    logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
                except json.JSONDecodeError:
                    logger.error(f"Error: Invalid JSON response from server: {response.text}")
                    return None
                
                if "error" in response_data:
                    logger.error(f"Error: {response_data['error']}")
                    return None
                
                # Extract the text content from the result
                content = response_data["result"]["content"][0]["text"]
                return json.loads(content)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with server: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    def close(self):
        """Close the SSE connection."""
        if self.sse_response:
            self.sse_response.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python example_usage.py /path/to/your/audio.mp3")
        return
    
    audio_file_path = sys.argv[1]
    
    # Check if the audio file exists
    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found: {audio_file_path}")
        return
    
    # URLs for the MCP servers
    audio_analyzer_url = "http://localhost:8000/sse"
    sequence_maker_url = "http://localhost:8001/sse"
    
    # Check if the servers are running
    audio_analyzer_running = check_server_running(audio_analyzer_url)
    sequence_maker_running = check_server_running(sequence_maker_url)
    
    if not (audio_analyzer_running and sequence_maker_running):
        print("MCP servers are not running.")
        if not start_servers():
            print("Failed to start MCP servers. Please run './start_mcp_servers.sh' manually.")
            return
    
    # Initialize clients
    audio_analyzer = MCPClient(audio_analyzer_url)
    sequence_maker = MCPClient(sequence_maker_url)
    
    try:
        # Initialize sessions
        print("Initializing sessions with MCP servers...")
        if not audio_analyzer.initialize_session():
            print("Failed to initialize session with Audio Analyzer MCP server.")
            return
            
        if not sequence_maker.initialize_session():
            print("Failed to initialize session with LTX Sequence Maker MCP server.")
            return
        
        print(f"Analyzing audio file: {audio_file_path}")
        
        # Step 1: Analyze the audio file
        print("Calling analyze_audio tool...")
        analysis_result = audio_analyzer.call_tool(
            "analyze_audio",
            {"audio_file_path": audio_file_path}
        )
        
        if not analysis_result:
            print("Failed to analyze audio file.")
            print("Please check that the MCP servers are running and the audio file is valid.")
            return
        
        print("Audio analysis complete!")
        print(f"Song title: {analysis_result.get('song_title', 'Unknown')}")
        print(f"Duration: {analysis_result.get('duration_seconds', 0):.2f} seconds")
        print(f"Tempo: {analysis_result.get('estimated_tempo', 0):.2f} BPM")
        
        # Step 2: Get song metadata
        print("Getting song metadata...")
        metadata = audio_analyzer.call_tool(
            "get_song_metadata",
            {}
        )
        
        if not metadata:
            print("Failed to get song metadata.")
            return
        
        print("\nSong Metadata:")
        print(f"Sections: {', '.join(metadata.get('sections', []))}")
        print(f"Total beats: {metadata.get('total_beats', 0)}")
        
        # Step 3: Get beats in a range (first 30 seconds)
        start_time = 0
        end_time = min(30, analysis_result.get('duration_seconds', 0))
        
        print(f"Getting beats in range {start_time}-{end_time} seconds...")
        beats_result = audio_analyzer.call_tool(
            "get_beats_in_range",
            {
                "start_time": start_time,
                "end_time": end_time,
                "beat_type": "all"
            }
        )
        
        if not beats_result:
            print("Failed to get beats.")
            return
        
        beats = beats_result.get("beats", [])
        print(f"\nFound {len(beats)} beats in the first {end_time:.2f} seconds")
        
        # Step 4: Create a beat-synchronized color pattern
        print("Creating beat-synchronized color pattern...")
        pattern_result = sequence_maker.call_tool(
            "apply_beat_pattern",
            {
                "beats": beats,
                "pattern_type": "pulse",
                "colors": ["red", "green", "blue"],
                "duration": 0.25
            }
        )
        
        if not pattern_result:
            print("Failed to create color pattern.")
            return
        
        segments = pattern_result.get("segments", [])
        print(f"\nCreated {len(segments)} color segments")
        
        # Step 5: Save the color sequence to a JSON file
        output_file = "color_sequence.json"
        with open(output_file, "w") as f:
            json.dump(segments, f, indent=2)
        
        print(f"\nColor sequence saved to {output_file}")
        print("Example usage complete!")
    finally:
        # Close the SSE connections
        audio_analyzer.close()
        sequence_maker.close()

if __name__ == "__main__":
    main()