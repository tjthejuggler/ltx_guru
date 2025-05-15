#!/usr/bin/env python3
"""
Lyrics Extraction Tool

This script extracts and processes lyrics from an audio file using the AudioAnalyzer class.
It can identify songs, fetch lyrics, and align them with the audio.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

# Import the AudioAnalyzer
try:
    from roo_code_sequence_maker.audio_analyzer import AudioAnalyzer
except ImportError as e:
    print(f"Error importing AudioAnalyzer: {e}")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LyricsExtractor")

def extract_lyrics(audio_file_path, output_path=None, time_range=None, conservative=False, user_lyrics=None):
    """
    Extract lyrics from an audio file.
    
    Args:
        audio_file_path (str): Path to the audio file
        output_path (str, optional): Path to save the lyrics JSON file
        time_range (tuple, optional): Tuple of (start_time, end_time) in seconds
        conservative (bool): Whether to use conservative alignment
        user_lyrics (str, optional): User-provided lyrics text
        
    Returns:
        dict: Lyrics data
    """
    # Initialize the analyzer
    analyzer = AudioAnalyzer()
    
    # Prepare analysis parameters
    analysis_params = {
        'request_lyrics': True,
        'conservative_lyrics_alignment': conservative
    }
    
    # Add user-provided lyrics if available
    if user_lyrics:
        analysis_params['user_provided_lyrics'] = user_lyrics
    
    # Analyze the audio
    logger.info(f"Analyzing audio file for lyrics: {audio_file_path}")
    analysis_data = analyzer.analyze_audio(audio_file_path, analysis_params=analysis_params)
    
    # Extract lyrics data
    if 'lyrics_info' not in analysis_data:
        logger.warning("No lyrics information found in analysis data")
        lyrics_data = {
            "song_title": None,
            "artist_name": None,
            "raw_lyrics": None,
            "word_timestamps": [],
            "processing_status": {
                "song_identified": False,
                "lyrics_retrieved": False,
                "lyrics_aligned": False,
                "user_assistance_needed": True,
                "assistance_type": "complete_lyrics_processing",
                "message": "Could not process lyrics. Please provide song title, artist, and lyrics text."
            }
        }
    else:
        lyrics_data = analysis_data['lyrics_info']
        
        # Add processing status information
        processing_status = {
            "song_identified": lyrics_data.get("song_title") is not None and lyrics_data.get("artist_name") is not None,
            "lyrics_retrieved": lyrics_data.get("raw_lyrics") is not None,
            "lyrics_aligned": len(lyrics_data.get("word_timestamps", [])) > 0,
            "user_assistance_needed": False,
            "assistance_type": None,
            "message": "Lyrics processing completed successfully."
        }
        
        # Determine if user assistance is needed
        if not processing_status["song_identified"]:
            processing_status["user_assistance_needed"] = True
            processing_status["assistance_type"] = "song_identification"
            processing_status["message"] = "Could not identify song. Please provide song title and artist name."
        elif not processing_status["lyrics_retrieved"]:
            processing_status["user_assistance_needed"] = True
            processing_status["assistance_type"] = "lyrics_text"
            processing_status["message"] = "Song identified but lyrics could not be retrieved. Please provide lyrics text."
        elif not processing_status["lyrics_aligned"]:
            processing_status["user_assistance_needed"] = True
            processing_status["assistance_type"] = "alignment_issue"
            processing_status["message"] = "Lyrics retrieved but could not be aligned with audio. Please check audio quality or provide timestamps manually."
        
        lyrics_data["processing_status"] = processing_status
        
        # Filter by time range if specified
        if time_range:
            start_time, end_time = time_range
            if 'word_timestamps' in lyrics_data:
                filtered_words = [
                    word for word in lyrics_data['word_timestamps']
                    if start_time <= word['start'] < end_time
                ]
                lyrics_data['word_timestamps'] = filtered_words
                logger.info(f"Filtered lyrics to {len(filtered_words)} words in time range {start_time}-{end_time}s")
    
    # Save to file if output path is provided
    if output_path:
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Ensure the output path has the correct extension
            if not output_path.endswith('.synced_lyrics.json'):
                base_path = output_path.rsplit('.', 1)[0] if '.' in output_path else output_path
                output_path = f"{base_path}.synced_lyrics.json"
                logger.info(f"Adjusting output path to use standardized extension: {output_path}")
            
            with open(output_path, 'w') as f:
                json.dump(lyrics_data, f, indent=2)
            logger.info(f"Lyrics data saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving lyrics data: {e}")
    
    return lyrics_data

def format_lyrics_text(lyrics_data, include_timestamps=False):
    """
    Format lyrics data as readable text.
    
    Args:
        lyrics_data (dict): Lyrics data
        include_timestamps (bool): Whether to include timestamps
        
    Returns:
        str: Formatted lyrics text
    """
    lines = []
    
    # Add song info if available
    if lyrics_data.get('song_title') and lyrics_data.get('artist_name'):
        lines.append(f"Song: {lyrics_data['song_title']}")
        lines.append(f"Artist: {lyrics_data['artist_name']}")
        lines.append("")
    
    # Add raw lyrics if available
    if lyrics_data.get('raw_lyrics'):
        lines.append("Raw Lyrics:")
        lines.append(lyrics_data['raw_lyrics'])
        lines.append("")
    
    # Add word timestamps if available and requested
    if include_timestamps and lyrics_data.get('word_timestamps'):
        lines.append("Word Timestamps:")
        
        # Group words into lines based on timing
        current_line = []
        last_end_time = 0
        
        for word in lyrics_data['word_timestamps']:
            # Start a new line if there's a significant gap
            if word['start'] - last_end_time > 1.0 and current_line:
                lines.append(" ".join(current_line))
                current_line = []
            
            # Add the word with its timestamp
            if include_timestamps:
                current_line.append(f"{word['word']}[{word['start']:.2f}s]")
            else:
                current_line.append(word['word'])
            
            last_end_time = word['end']
        
        # Add the last line
        if current_line:
            lines.append(" ".join(current_line))
    
    return "\n".join(lines)

def print_lyrics_summary(lyrics_data):
    """Print a summary of the extracted lyrics."""
    print("\n=== Lyrics Extraction Summary ===")
    
    # Print processing status
    if "processing_status" in lyrics_data:
        status = lyrics_data["processing_status"]
        print("\nProcessing Status:")
        print(f"- Song identified: {'Yes' if status['song_identified'] else 'No'}")
        print(f"- Lyrics retrieved: {'Yes' if status['lyrics_retrieved'] else 'No'}")
        print(f"- Lyrics aligned: {'Yes' if status['lyrics_aligned'] else 'No'}")
        
        if status["user_assistance_needed"]:
            print("\n⚠️ User Assistance Needed:")
            print(f"  {status['message']}")
            
            if status["assistance_type"] == "lyrics_text":
                print("\n  To provide lyrics and process them:")
                print("  1. Save lyrics to a text file with .lyrics.txt extension (e.g., song.lyrics.txt)")
                print("  2. Run: python -m roocode_sequence_designer_tools.extract_lyrics <audio_file> --lyrics-file song.lyrics.txt --output song.synced_lyrics.json")
            elif status["assistance_type"] == "song_identification":
                print("\n  To manually process with known song info:")
                print("  1. Find lyrics for the song")
                print("  2. Save lyrics to a text file with .lyrics.txt extension (e.g., song.lyrics.txt)")
                print("  3. Run: python -m roocode_sequence_designer_tools.extract_lyrics <audio_file> --lyrics-file song.lyrics.txt --output song.synced_lyrics.json")
    
    # Print song info
    if lyrics_data.get('song_title') and lyrics_data.get('artist_name'):
        print(f"\nSong: {lyrics_data['song_title']}")
        print(f"Artist: {lyrics_data['artist_name']}")
    else:
        print("\nSong identification: Not available")
    
    # Print word count
    word_count = len(lyrics_data.get('word_timestamps', []))
    print(f"Words with timestamps: {word_count}")
    
    # Print lyrics preview
    if lyrics_data.get('raw_lyrics'):
        raw_lyrics_preview = lyrics_data['raw_lyrics'][:100] + "..." if len(lyrics_data['raw_lyrics']) > 100 else lyrics_data['raw_lyrics']
        print(f"\nLyrics preview: {raw_lyrics_preview}")
    
    # Print word timestamps
    if word_count > 0:
        print("\nFirst few words with timestamps:")
        for i, word in enumerate(lyrics_data['word_timestamps'][:10]):
            print(f"  {word['word']} ({word['start']:.2f}s - {word['end']:.2f}s)")
            if i >= 4:
                break
        
        if word_count > 5:
            print(f"  ... and {word_count - 5} more words")
    
    print("\nExtraction complete!")

def main():
    """Main function to parse arguments and extract lyrics."""
    parser = argparse.ArgumentParser(description="Extract lyrics from an audio file.")
    parser.add_argument("audio_file_path", help="Path to the audio file")
    parser.add_argument(
        "--output",
        help="Path to save the lyrics JSON file. If not provided, only prints summary."
    )
    parser.add_argument(
        "--start-time",
        type=float,
        help="Start time in seconds for time-range extraction"
    )
    parser.add_argument(
        "--end-time",
        type=float,
        help="End time in seconds for time-range extraction"
    )
    parser.add_argument(
        "--conservative",
        action="store_true",
        help="Use conservative alignment for lyrics processing"
    )
    parser.add_argument(
        "--lyrics-file",
        help="Path to a text file containing user-provided lyrics"
    )
    parser.add_argument(
        "--format-text",
        action="store_true",
        help="Format lyrics as readable text instead of JSON"
    )
    parser.add_argument(
        "--include-timestamps",
        action="store_true",
        help="Include timestamps in formatted text output"
    )
    
    args = parser.parse_args()
    
    # Check if the audio file exists
    if not os.path.exists(args.audio_file_path):
        logger.error(f"Audio file not found: {args.audio_file_path}")
        sys.exit(1)
    
    # Load user-provided lyrics if specified
    user_lyrics = None
    if args.lyrics_file:
        # Check if the lyrics file exists
        lyrics_file_path = args.lyrics_file
        if not os.path.exists(lyrics_file_path):
            # Try adding the .lyrics.txt extension if it's missing
            if not lyrics_file_path.endswith('.lyrics.txt'):
                potential_path = f"{lyrics_file_path}.lyrics.txt"
                if os.path.exists(potential_path):
                    lyrics_file_path = potential_path
                    logger.info(f"Using standardized lyrics file path: {lyrics_file_path}")
                else:
                    # Also try replacing any existing extension with .lyrics.txt
                    base_path = lyrics_file_path.rsplit('.', 1)[0] if '.' in lyrics_file_path else lyrics_file_path
                    potential_path = f"{base_path}.lyrics.txt"
                    if os.path.exists(potential_path):
                        lyrics_file_path = potential_path
                        logger.info(f"Using standardized lyrics file path: {lyrics_file_path}")
                    else:
                        logger.error(f"Lyrics file not found: {args.lyrics_file}")
                        sys.exit(1)
            else:
                logger.error(f"Lyrics file not found: {args.lyrics_file}")
                sys.exit(1)
        
        try:
            with open(lyrics_file_path, 'r') as f:
                user_lyrics = f.read()
            logger.info(f"Loaded user-provided lyrics from {lyrics_file_path}")
        except Exception as e:
            logger.error(f"Error loading lyrics file: {e}")
            sys.exit(1)
    
    # Determine time range
    time_range = None
    if args.start_time is not None and args.end_time is not None:
        time_range = (args.start_time, args.end_time)
        logger.info(f"Using time range: {args.start_time}-{args.end_time}s")
    
    # Extract lyrics
    lyrics_data = extract_lyrics(
        args.audio_file_path,
        args.output,
        time_range,
        args.conservative,
        user_lyrics
    )
    
    # Print summary or formatted text
    if args.format_text:
        formatted_text = format_lyrics_text(lyrics_data, args.include_timestamps)
        print(formatted_text)
    else:
        print_lyrics_summary(lyrics_data)

if __name__ == "__main__":
    main()