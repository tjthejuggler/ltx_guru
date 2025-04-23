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

def check_server_running(url):
    """Check if a server is running at the given URL."""
    try:
        response = requests.get(url + "/sse", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def start_servers():
    """Start the MCP servers if they're not already running."""
    print("Starting MCP servers...")
    try:
        # Use subprocess to run the start_mcp_servers.sh script
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
        self.session_id = str(uuid.uuid4())
        
    def initialize_session(self):
        """Initialize a session with the MCP server."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "session_id": self.session_id,
                "client_info": {
                    "name": "example_usage.py",
                    "version": "1.0.0"
                }
            }
        }
        
        try:
            response = requests.post(f"{self.server_url}/messages/", json=payload, timeout=30)
            response_data = response.json()
            
            if "error" in response_data:
                print(f"Error initializing session: {response_data['error']}")
                return False
                
            return True
        except Exception as e:
            print(f"Error initializing session: {e}")
            return False
    
    def call_tool(self, tool_name, arguments):
        """Call an MCP tool and return the result."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "callTool",
            "params": {
                "session_id": self.session_id,
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            response = requests.post(f"{self.server_url}/messages/", json=payload, timeout=30)
            
            # Check if the response is valid JSON
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON response from server: {response.text}")
                return None
            
            if "error" in response_data:
                print(f"Error: {response_data['error']}")
                return None
            
            # Extract the text content from the result
            content = response_data["result"]["content"][0]["text"]
            return json.loads(content)
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with server: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

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
    audio_analyzer_url = "http://localhost:8000"
    sequence_maker_url = "http://localhost:8001"
    
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

if __name__ == "__main__":
    main()