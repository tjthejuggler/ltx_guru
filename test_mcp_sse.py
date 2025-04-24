#!/usr/bin/env python3
"""
Test script for the audio-analyzer MCP server using SSE transport.
This script follows the approach used in mcp_client.py but with more detailed logging.
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_sse_test")

# Import the MCP client library
try:
    from mcp.client.session import ClientSession
    from mcp.client.sse import sse_client
except ImportError:
    logger.error("MCP client library not found. Please install it with: pip install mcp-client")
    sys.exit(1)

# Path to the audio file
AUDIO_FILE_PATH = str(Path(__file__).parent / "sequence_maker" / "tests" / "resources" / "test_audio.mp3")

async def main():
    # Check if the audio file exists
    if not os.path.exists(AUDIO_FILE_PATH):
        logger.error(f"Audio file not found: {AUDIO_FILE_PATH}")
        return
    
    logger.info(f"Audio file exists: {AUDIO_FILE_PATH} ({os.path.getsize(AUDIO_FILE_PATH)} bytes)")
    
    # Create MCP client for the audio-analyzer server
    logger.info("Creating SSE client for audio-analyzer server")
    url = "http://localhost:8000/sse"
    
    try:
        # Use sse_client as an async context manager
        async with sse_client(url, timeout=10, sse_read_timeout=60) as (read_stream, write_stream):
            logger.info("Creating ClientSession with the SSE streams")
            audio_analyzer = ClientSession(read_stream, write_stream)
            
            # Connect to the MCP server
            logger.info("Connecting to audio-analyzer server...")
            await audio_analyzer.initialize()
            logger.info("Successfully connected to audio-analyzer server!")
        
        # List available tools
        logger.info("Listing available tools...")
        tools = await audio_analyzer.list_tools()
        logger.info(f"Available tools: {[tool.name for tool in tools]}")
        
        # Step 1: Analyze the audio file
        logger.info(f"Analyzing audio file: {AUDIO_FILE_PATH}")
        try:
            start_time = time.time()
            logger.debug(f"Starting analyze_audio at {start_time}")
            
            analysis_result = await audio_analyzer.call_tool(
                "analyze_audio",
                {"audio_file_path": AUDIO_FILE_PATH}
            )
            
            end_time = time.time()
            logger.debug(f"Completed analyze_audio in {end_time - start_time:.2f} seconds")
            
            logger.info("Audio analysis complete!")
            logger.info(f"Song title: {analysis_result.get('song_title', 'Unknown')}")
            logger.info(f"Duration: {analysis_result.get('duration_seconds', 0):.2f} seconds")
            logger.info(f"Tempo: {analysis_result.get('estimated_tempo', 0):.2f} BPM")
            
            # Step 2: Get song metadata
            logger.info("Getting song metadata...")
            metadata = await audio_analyzer.call_tool(
                "get_song_metadata",
                {}
            )
            
            logger.info("Song Metadata:")
            logger.info(f"Sections: {', '.join(metadata.get('sections', []))}")
            logger.info(f"Total beats: {metadata.get('total_beats', 0)}")
            
            # Step 3: Get beats in a range (first 5 seconds)
            start_time = 0
            end_time = min(5, analysis_result.get('duration_seconds', 0))
            
            logger.info(f"Getting beats in range {start_time}-{end_time} seconds...")
            beats_result = await audio_analyzer.call_tool(
                "get_beats_in_range",
                {
                    "start_time": start_time,
                    "end_time": end_time,
                    "beat_type": "all"
                }
            )
            
            beats = beats_result.get("beats", [])
            logger.info(f"Found {len(beats)} beats in the first {end_time:.2f} seconds")
            
            logger.info("Test completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during tool call: {e}")
            
            # List available tools
            logger.info("Listing available tools...")
            tools = await audio_analyzer.list_tools()
            logger.info(f"Available tools: {[tool.name for tool in tools]}")
            
            # Step 1: Analyze the audio file
            logger.info(f"Analyzing audio file: {AUDIO_FILE_PATH}")
            try:
                start_time = time.time()
                logger.debug(f"Starting analyze_audio at {start_time}")
                
                analysis_result = await audio_analyzer.call_tool(
                    "analyze_audio",
                    {"audio_file_path": AUDIO_FILE_PATH}
                )
                
                end_time = time.time()
                logger.debug(f"Completed analyze_audio in {end_time - start_time:.2f} seconds")
                
                logger.info("Audio analysis complete!")
                logger.info(f"Song title: {analysis_result.get('song_title', 'Unknown')}")
                logger.info(f"Duration: {analysis_result.get('duration_seconds', 0):.2f} seconds")
                logger.info(f"Tempo: {analysis_result.get('estimated_tempo', 0):.2f} BPM")
                
                # Step 2: Get song metadata
                logger.info("Getting song metadata...")
                metadata = await audio_analyzer.call_tool(
                    "get_song_metadata",
                    {}
                )
                
                logger.info("Song Metadata:")
                logger.info(f"Sections: {', '.join(metadata.get('sections', []))}")
                logger.info(f"Total beats: {metadata.get('total_beats', 0)}")
                
                # Step 3: Get beats in a range (first 5 seconds)
                start_time = 0
                end_time = min(5, analysis_result.get('duration_seconds', 0))
                
                logger.info(f"Getting beats in range {start_time}-{end_time} seconds...")
                beats_result = await audio_analyzer.call_tool(
                    "get_beats_in_range",
                    {
                        "start_time": start_time,
                        "end_time": end_time,
                        "beat_type": "all"
                    }
                )
                
                beats = beats_result.get("beats", [])
                logger.info(f"Found {len(beats)} beats in the first {end_time:.2f} seconds")
                
                logger.info("Test completed successfully!")
                
            except Exception as e:
                logger.error(f"Error during tool call: {e}")
                
            # Close the connection
            logger.info("Closing connection to audio-analyzer server")
            await audio_analyzer.close()
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())