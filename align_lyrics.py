#!/usr/bin/env python3
"""
Lyrics Alignment Tool

This script aligns lyrics with audio files using the Gentle forced alignment API.
It automatically ensures the Gentle server is running and provides timestamps for each word.

Usage:
    python align_lyrics.py <audio_file> <lyrics_file> <output_file> [--song-title "Song Title"] [--artist-name "Artist Name"] [--no-conservative]

Example:
    python align_lyrics.py song.mp3 lyrics.txt timestamps.json --song-title "My Song" --artist-name "My Artist"
"""

import os
import sys
import json
import requests
import time
import argparse
from pathlib import Path
import hashlib # For cache key

# Ensure roocode_sequence_designer_tools is in path for CacheManager import
_SCRIPT_DIR = Path(__file__).resolve().parent
_ROOCODE_TOOLS_DIR = _SCRIPT_DIR / "roocode_sequence_designer_tools"
if str(_ROOCODE_TOOLS_DIR.parent) not in sys.path: # Add parent of roocode_sequence_designer_tools
    sys.path.insert(0, str(_ROOCODE_TOOLS_DIR.parent))
if str(_ROOCODE_TOOLS_DIR) not in sys.path: # Add roocode_sequence_designer_tools itself
     sys.path.insert(0, str(_ROOCODE_TOOLS_DIR))


try:
    from roocode_sequence_designer_tools.tool_utils.cache_manager import CacheManager
except ImportError as e:
    print(f"Error importing CacheManager: {e}", file=sys.stderr)
    print("Please ensure 'roocode_sequence_designer_tools' is in your PYTHONPATH or accessible.", file=sys.stderr)
    sys.exit(1)


def check_gentle_server():
    """Check if the Gentle server is running."""
    try:
        response = requests.get("http://localhost:8765", timeout=2)
        if response.status_code == 200:
            print("Gentle server is running.")
            return True
        else:
            print(f"Gentle server returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error connecting to Gentle server: {e}")
        return False

def align_lyrics(
    audio_path,
    lyrics_path,
    output_path,
    conservative=True,
    song_title_arg=None, # Added for output consistency
    artist_name_arg=None, # Added for output consistency
    cache_manager: CacheManager = None, # Added
    no_cache: bool = False # Added
    ):
    """
    Align lyrics with audio using the Gentle API.
    
    Args:
        audio_path: Path to the audio file
        lyrics_path: Path to the lyrics file
        output_path: Path to save the output JSON
        conservative: Whether to use conservative alignment
        song_title_arg: Song title provided as argument
        artist_name_arg: Artist name provided as argument
        cache_manager (CacheManager): Instance of CacheManager.
        no_cache (bool): If True, bypasses cache read/write.
            
    Returns:
        Optional[dict]: Lyrics data if successful, None otherwise. (Changed from bool for caching)
    """
    if cache_manager is None:
        cache_manager = CacheManager()

    print(f"Aligning audio: {audio_path}")
    print(f"Using lyrics from: {lyrics_path}")

    # --- Caching Logic ---
    tool_params_for_cache = {
        "conservative": conservative,
    }
    # The content of the lyrics file is crucial for the cache key
    lyrics_file_hash = "lyrics_file_not_found_for_hash"
    try:
        lyrics_file_hash = cache_manager._get_file_hash(lyrics_path)
    except FileNotFoundError:
        pass # Handled by lyrics_file_hash default
    tool_params_for_cache["lyrics_file_hash"] = lyrics_file_hash

    cache_key = cache_manager.generate_cache_key(
        identifier="align_lyrics_gentle", # Specific ID
        params=tool_params_for_cache,
        file_path_for_hash=audio_path # Hash of the audio file
    )

    if not no_cache:
        cached_data = cache_manager.load_from_cache(cache_key)
        if cached_data:
            print(f"Loading aligned lyrics from cache (key: {cache_key}).")
            # Save to output_path is handled by the caller (main)
            return cached_data # Return the data directly
            
    print("Cache not used or cache miss for Gentle alignment. Performing new alignment.")
    # --- End Caching Logic ---
    
    # Check if the Gentle server is running
    if not check_gentle_server():
        print("Gentle server is not running. Please start it first.")
        return None # Changed from False
    
    # Load the lyrics
    try:
        with open(lyrics_path, 'r') as f:
            lyrics_text = f.read()
        print(f"Loaded lyrics ({len(lyrics_text)} characters)")
    except Exception as e:
        print(f"Error loading lyrics: {e}")
        return None # Changed from False
    
    # Ensure audio path is absolute
    audio_path = os.path.abspath(audio_path)
    
    # Verify the file exists
    if not os.path.exists(audio_path):
        print(f"Audio file does not exist: {audio_path}")
        return None # Changed from False
    
    # Send request to Gentle
    try:
        print("Opening audio file for Gentle alignment")
        
        with open(audio_path, 'rb') as audio_file_obj: # Renamed to avoid conflict
            files = {
                'audio': audio_file_obj,
                'transcript': (None, lyrics_text)
            }
            
            print("Sending request to Gentle API")
            
            # Build the URL with parameters
            url = 'http://localhost:8765/transcriptions?async=false'
            if conservative:
                url += '&conservative=true'
                print("Using conservative alignment mode")
            
            response = requests.post(
                url,
                files=files,
                timeout=120  # Increase timeout to 2 minutes
            )
    except FileNotFoundError as e:
        print(f"Error opening audio file: {e}")
        return None # Changed from False
    except requests.RequestException as e:
        print(f"Error communicating with Gentle API: {e}")
        return None # Changed from False
    
    # Check if request was successful
    if response.status_code != 200:
        print(f"Gentle API error: {response.status_code}")
        print(response.text)
        return None # Changed from False
    
    # Parse response
    try:
        result = response.json()
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print("Response might not be JSON. Saving raw response to file.")
        with open("gentle_raw_response.txt", "w") as f:
            f.write(response.text)
        print("Raw response saved to gentle_raw_response.txt")
        return None # Changed from False
    
    # Extract word timestamps
    processed_word_timestamps = [] # Renamed
    
    for word_entry in result.get('words', []): # Renamed
        # Skip words without alignment
        if 'start' not in word_entry or 'end' not in word_entry:
            continue
        
        # Create word timestamp object
        word_ts_obj = { # Renamed
            'word': word_entry.get('alignedWord', ''),
            'start': word_entry.get('start', 0.0),
            'end': word_entry.get('end', 0.0)
        }
        
        processed_word_timestamps.append(word_ts_obj)
    
    # Create the output data object
    # Use song_title_arg and artist_name_arg passed to this function
    output_lyrics_data = { # Renamed
        "song_title": song_title_arg, # Use args passed to this func
        "artist_name": artist_name_arg, # Use args passed to this func
        "raw_lyrics": lyrics_text,
        "word_timestamps": processed_word_timestamps,
        "processing_status": {
            "song_identified": True, # Assuming if align_lyrics is called, these are known
            "lyrics_retrieved": True,
            "lyrics_aligned": len(processed_word_timestamps) > 0,
            "user_assistance_needed": False, # If alignment worked.
            "message": "Lyrics aligned successfully via Gentle."
        }
    }
    if not output_lyrics_data["processing_status"]["lyrics_aligned"]:
        output_lyrics_data["processing_status"]["message"] = "Lyrics alignment via Gentle did not produce timestamps."
        output_lyrics_data["processing_status"]["user_assistance_needed"] = True


    # Saving to output_path is handled by the caller (main)
    # Save to cache if enabled
    if not no_cache:
        print(f"Saving new Gentle alignment to cache (key: {cache_key}).")
        cache_manager.save_to_cache(cache_key, output_lyrics_data)

    return output_lyrics_data # Return the data object

def start_gentle_server():
    """
    Attempt to start the Gentle server if it's not already running.
    
    Returns:
        bool: True if server is running or was started successfully, False otherwise
    """
    if check_gentle_server():
        return True
        
    print("Attempting to start Gentle server...")
    try:
        # Try to find and run the start_gentle.py script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        
        # Check common locations for the start_gentle.py script
        possible_paths = [
            os.path.join(project_dir, "sequence_maker", "scripts", "start_gentle.py"),
            os.path.join(project_dir, "scripts", "start_gentle.py"),
            os.path.join(script_dir, "start_gentle.py")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found start_gentle.py at {path}")
                result = os.system(f"{sys.executable} {path}")
                if result == 0 and check_gentle_server():
                    print("Successfully started Gentle server")
                    return True
        
        print("Could not find or start the Gentle server")
        return False
    except Exception as e:
        print(f"Error starting Gentle server: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Align lyrics with audio using Gentle forced alignment")
    parser.add_argument("audio_file", help="Path to the audio file")
    parser.add_argument("lyrics_file", help="Path to the lyrics text file")
    parser.add_argument("output_file", help="Path to save the output JSON file with timestamps")
    parser.add_argument("--song-title", default=None, help="Title of the song")
    parser.add_argument("--artist-name", default=None, help="Name of the artist")
    parser.add_argument("--no-conservative", action="store_true", help="Disable conservative alignment mode")
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Force re-alignment and do not use or save to cache."
    )
    parser.add_argument(
        "--clear-all-cache",
        action="store_true",
        help="Clear all cache entries for this tool and exit."
    )
    
    args = parser.parse_args()

    cache_manager_instance = CacheManager()

    if args.clear_all_cache:
        print("Clearing all cache entries...")
        cache_manager_instance.clear_all_cache()
        sys.exit(0)
        
    # Determine song title and artist name from filename if not provided
    # This logic is for the final output JSON, pass these to align_lyrics
    current_song_title = args.song_title
    current_artist_name = args.artist_name
    
    if current_song_title is None or current_artist_name is None:
        filename = os.path.basename(args.audio_file)
        name_parts = os.path.splitext(filename)[0].split('_')
        if len(name_parts) >= 2 and current_song_title is None:
            current_song_title = ' '.join(name_parts[:-1]).title()
        elif current_song_title is None:
            current_song_title = name_parts[0].title()
            
        if current_artist_name is None and len(name_parts) >= 2:
            current_artist_name = name_parts[-1].title()
        elif current_artist_name is None:
            current_artist_name = "Unknown Artist"
    
    # Ensure the Gentle server is running
    if not start_gentle_server():
        print("Error: Gentle server is required for lyrics alignment")
        sys.exit(1)
    
    # Check if files exist
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file not found: {args.audio_file}")
        sys.exit(1)
    
    if not os.path.exists(args.lyrics_file):
        print(f"Error: Lyrics file not found: {args.lyrics_file}")
        sys.exit(1)
    
    # Run alignment
    conservative_setting = not args.no_conservative
    
    aligned_data = align_lyrics(
        audio_path=args.audio_file,
        lyrics_path=args.lyrics_file,
        output_path=args.output_file, # align_lyrics no longer saves, main does
        conservative=conservative_setting,
        song_title_arg=current_song_title, # Pass determined title/artist
        artist_name_arg=current_artist_name,
        cache_manager=cache_manager_instance,
        no_cache=args.no_cache
    )
    
    if aligned_data:
        # Save the returned data to output_file
        try:
            with open(args.output_file, 'w') as f:
                json.dump(aligned_data, f, indent=2)
            print(f"Aligned lyrics data saved to {args.output_file}")
        except Exception as e:
            print(f"Error saving aligned lyrics data: {e}")
            print("\nLyrics alignment process had issues but data might be in cache.")
            sys.exit(1) # Exit if save fails after successful alignment

        # Print summary from the returned data
        word_count = len(aligned_data.get("word_timestamps", []))
        print(f"\nProcessed {word_count} words with timestamps.")
        if word_count > 0:
            print("\nFirst few words with timestamps:")
            for i, word_obj in enumerate(aligned_data["word_timestamps"][:5]):
                print(f"  {word_obj['word']}: {word_obj['start']:.2f}s - {word_obj['end']:.2f}s")
        
        print("\nLyrics alignment completed successfully!")
    else:
        print("\nLyrics alignment failed.")