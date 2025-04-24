#!/usr/bin/env python3
"""
A simple client for interacting with MCP servers using the official mcp library.

This script:
1. Connects to the MCP servers
2. Analyzes an audio file
3. Gets the beats in a specific range
4. Creates a beat-synchronized color pattern
5. Saves the resulting color sequence to a JSON file

Usage:
    python mcp_client.py /path/to/your/audio.mp3
"""

import sys
import json
import os
import time
import subprocess
import logging
import asyncio
from mcp.client.session import ClientSession

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mcp_client")

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

async def main():
    if len(sys.argv) < 2:
        print("Usage: python mcp_client.py /path/to/your/audio.mp3")
        return
    
    audio_file_path = sys.argv[1]
    
    # Check if the audio file exists
    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found: {audio_file_path}")
        return
    
    # Start the MCP servers
    if not start_servers():
        print("Failed to start MCP servers.")
        return
    
    # Create MCP clients
    audio_analyzer = ClientSession(url="http://localhost:8000/sse")
    sequence_maker = ClientSession(url="http://localhost:8001/sse")
    
    try:
        # Connect to the MCP servers
        print("Connecting to MCP servers...")
        await audio_analyzer.initialize()
        await sequence_maker.initialize()
        
        print("Successfully connected to MCP servers!")
        
        # Step 1: Analyze the audio file
        print(f"Analyzing audio file: {audio_file_path}")
        analysis_result = await audio_analyzer.call_tool(
            "analyze_audio",
            {"audio_file_path": audio_file_path}
        )
        
        print("Audio analysis complete!")
        print(f"Song title: {analysis_result.get('song_title', 'Unknown')}")
        print(f"Duration: {analysis_result.get('duration_seconds', 0):.2f} seconds")
        print(f"Tempo: {analysis_result.get('estimated_tempo', 0):.2f} BPM")
        
        # Step 2: Get song metadata
        print("Getting song metadata...")
        metadata = await audio_analyzer.call_tool(
            "get_song_metadata",
            {}
        )
        
        print("\nSong Metadata:")
        print(f"Sections: {', '.join(metadata.get('sections', []))}")
        print(f"Total beats: {metadata.get('total_beats', 0)}")
        
        # Step 3: Get beats in a range (first 30 seconds)
        start_time = 0
        end_time = min(30, analysis_result.get('duration_seconds', 0))
        
        print(f"Getting beats in range {start_time}-{end_time} seconds...")
        beats_result = await audio_analyzer.call_tool(
            "get_beats_in_range",
            {
                "start_time": start_time,
                "end_time": end_time,
                "beat_type": "all"
            }
        )
        
        beats = beats_result.get("beats", [])
        print(f"\nFound {len(beats)} beats in the first {end_time:.2f} seconds")
        
        # Step 4: Create a beat-synchronized color pattern
        print("Creating beat-synchronized color pattern...")
        pattern_result = await sequence_maker.call_tool(
            "apply_beat_pattern",
            {
                "beats": beats,
                "pattern_type": "pulse",
                "colors": ["red", "green", "blue"],
                "duration": 0.25
            }
        )
        
        segments = pattern_result.get("segments", [])
        print(f"\nCreated {len(segments)} color segments")
        
        # Step 5: Save the color sequence to a JSON file
        output_file = "color_sequence.json"
        with open(output_file, "w") as f:
            json.dump(segments, f, indent=2)
        
        print(f"\nColor sequence saved to {output_file}")
        print("MCP client complete!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the connections
        await audio_analyzer.close()
        await sequence_maker.close()

if __name__ == "__main__":
    asyncio.run(main())