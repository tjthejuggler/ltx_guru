#!/usr/bin/env python3
"""
Simple Lyrics Extraction Tool

This script provides a simplified workflow for extracting and aligning lyrics with audio.
It bypasses the song identification step and directly uses user-provided lyrics.

Usage:
    python -m roocode_sequence_designer_tools.extract_lyrics_simple audio_file lyrics_file.lyrics.txt output_file.synced_lyrics.json

Example:
    python -m roocode_sequence_designer_tools.extract_lyrics_simple song.mp3 song.lyrics.txt song.synced_lyrics.json
"""

import os
import sys
import json
import argparse
import logging
import requests
import subprocess
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LyricsExtractor")

def ensure_gentle_running():
    """
    Ensure the Gentle server is running.
    
    Returns:
        bool: True if Gentle is running, False otherwise
    """
    logger.info("Checking if Gentle server is running...")
    
    try:
        response = requests.get("http://localhost:8765", timeout=2)
        if response.status_code == 200:
            logger.info("Gentle server is already running.")
            return True
    except Exception:
        logger.info("Gentle server is not running. Starting it now...")
    
    # Try to start the Gentle server
    try:
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        start_gentle_script = os.path.join(script_dir, "sequence_maker", "scripts", "start_gentle.py")
        
        if not os.path.exists(start_gentle_script):
            logger.error(f"Could not find start_gentle.py at {start_gentle_script}")
            return False
        
        logger.info(f"Running start_gentle.py from {start_gentle_script}")
        subprocess.run([sys.executable, start_gentle_script], check=True)
        
        # Check if it's running now
        response = requests.get("http://localhost:8765", timeout=2)
        if response.status_code == 200:
            logger.info("Gentle server started successfully.")
            return True
        else:
            logger.error("Failed to start Gentle server.")
            return False
    except Exception as e:
        logger.error(f"Error starting Gentle server: {e}")
        return False

def align_lyrics(audio_path, lyrics_path, output_path, song_title="Unknown Song", artist_name="Unknown Artist", conservative=False):
    """
    Align lyrics with audio using the Gentle API.

    Args:
        audio_path: Path to the audio file
        lyrics_path: Path to the lyrics file
        output_path: Path to save the output JSON
        song_title: Title of the song
        artist_name: Name of the artist
        conservative: If True, use Gentle's conservative alignment (stricter,
            drops more words). Defaults to False because conservative mode
            silently rejects 20-30%+ of words on sung music, leaving large
            gaps in the timeline. Use True only if you specifically need
            high-confidence-only timestamps for spoken-word audio.

    Returns:
        bool: Success status
    """
    logger.info(f"Aligning audio: {audio_path}")
    logger.info(f"Using lyrics from: {lyrics_path}")
    
    # Ensure audio path is absolute
    audio_path = os.path.abspath(audio_path)
    
    # Verify the file exists
    if not os.path.exists(audio_path):
        logger.error(f"Audio file does not exist: {audio_path}")
        return False
    
    # Ensure lyrics path has the correct extension
    if not lyrics_path.endswith('.lyrics.txt'):
        base_path = lyrics_path.rsplit('.', 1)[0] if '.' in lyrics_path else lyrics_path
        standardized_lyrics_path = f"{base_path}.lyrics.txt"
        
        # If the file doesn't exist but a standardized version does, use that
        if not os.path.exists(lyrics_path) and os.path.exists(standardized_lyrics_path):
            lyrics_path = standardized_lyrics_path
            logger.info(f"Using standardized lyrics file path: {lyrics_path}")
    
    # Load the lyrics
    try:
        with open(lyrics_path, 'r') as f:
            lyrics_text = f.read()
        logger.info(f"Loaded lyrics ({len(lyrics_text)} characters)")
    except Exception as e:
        logger.error(f"Error loading lyrics: {e}")
        return False
    
    # Send request to Gentle
    try:
        logger.info("Opening audio file for Gentle alignment")
        
        with open(audio_path, 'rb') as audio_file:
            files = {
                'audio': audio_file,
                'transcript': (None, lyrics_text)
            }
            
            mode_label = "conservative" if conservative else "standard"
            logger.info(f"Sending request to Gentle API with {mode_label} alignment")

            # Build URL based on conservative flag.
            # Conservative mode is OFF by default — it drops too many words
            # for sung music. See lyrics_extraction_guide.md for details.
            url = 'http://localhost:8765/transcriptions?async=false'
            if conservative:
                url += '&conservative=true'

            response = requests.post(
                url,
                files=files,
                timeout=300  # 5 minutes timeout for longer audio files
            )
    except Exception as e:
        logger.error(f"Error during alignment: {e}")
        return False
    
    # Check if request was successful
    if response.status_code != 200:
        logger.error(f"Gentle API error: {response.status_code}")
        logger.error(response.text)
        return False
    
    # Parse response
    try:
        result = response.json()
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON response: {e}")
        logger.error("Response might not be JSON. Saving raw response to file.")
        with open("gentle_raw_response.txt", "w") as f:
            f.write(response.text)
        logger.error("Raw response saved to gentle_raw_response.txt")
        return False
    
    # Extract word timestamps.
    #
    # IMPORTANT: We keep one entry per word in the original lyrics, even when
    # Gentle could not align it. Unaligned words are stored with start=None,
    # end=None, case='not-found-in-audio'. This way:
    #   - downstream tools see the full lyric text (no missing words)
    #   - they can interpolate timestamps for the gaps if they need to
    #   - the output honestly reflects alignment quality instead of pretending
    #     the words don't exist.
    word_timestamps = []
    aligned_count = 0
    not_found_count = 0
    other_count = 0

    for word in result.get('words', []):
        case = word.get('case', 'unknown')
        original_word = word.get('word', '')
        aligned_word = word.get('alignedWord', original_word)

        if 'start' in word and 'end' in word:
            word_timestamps.append({
                'word': aligned_word or original_word,
                'start': word['start'],
                'end': word['end'],
                'case': case
            })
            aligned_count += 1
        else:
            # Preserve the word in the timeline so downstream tools see the
            # full lyric, but mark it as un-aligned.
            word_timestamps.append({
                'word': original_word,
                'start': None,
                'end': None,
                'case': case
            })
            if case == 'not-found-in-audio':
                not_found_count += 1
            else:
                other_count += 1

    total = len(word_timestamps)
    pct = (100.0 * aligned_count / total) if total else 0.0
    quality = (
        "EXCELLENT" if pct >= 90 else
        "GOOD"      if pct >= 75 else
        "FAIR"      if pct >= 60 else
        "POOR"
    )
    logger.info(
        f"Alignment quality: {quality} "
        f"({aligned_count}/{total} aligned, {pct:.1f}%; "
        f"not-found={not_found_count}, other-unaligned={other_count})"
    )
    if pct < 75:
        logger.warning(
            "Low alignment rate. Consider: (1) verifying the lyrics text "
            "matches the actual sung lyrics; (2) checking audio quality; "
            "(3) re-running with --conservative disabled (it already is by "
            "default) — or, if you ran with --conservative, removing it."
        )

    # Create the output data
    lyrics_data = {
        "song_title": song_title,
        "artist_name": artist_name,
        "raw_lyrics": lyrics_text,
        "word_timestamps": word_timestamps,
        "alignment_stats": {
            "total_words": total,
            "aligned_words": aligned_count,
            "not_found_in_audio": not_found_count,
            "other_unaligned": other_count,
            "aligned_percentage": round(pct, 2),
            "quality": quality,
            "conservative_mode": conservative,
        },
        "processing_status": {
            "song_identified": True,
            "lyrics_retrieved": True,
            "lyrics_aligned": aligned_count > 0,
            "user_assistance_needed": False,
            "message": f"Lyrics aligned: {aligned_count}/{total} words ({quality})."
        }
    }
    
    # Save to file
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Ensure output path has the correct extension
        if not output_path.endswith('.synced_lyrics.json'):
            base_path = output_path.rsplit('.', 1)[0] if '.' in output_path else output_path
            output_path = f"{base_path}.synced_lyrics.json"
            logger.info(f"Adjusting output path to use standardized extension: {output_path}")
        
        with open(output_path, 'w') as f:
            json.dump(lyrics_data, f, indent=2)
        logger.info(f"Lyrics data saved to {output_path}")
    except Exception as e:
        logger.error(f"Error saving lyrics data: {e}")
        return False
    
    # Print summary
    word_count = len(word_timestamps)
    logger.info(f"Processed {word_count} words with timestamps.")
    
    if word_count > 0:
        logger.info("First few words with timestamps:")
        for i, word in enumerate(word_timestamps[:5]):
            logger.info(f"  {word['word']}: {word['start']:.2f}s - {word['end']:.2f}s")
    
    return True

def main():
    """Main function to parse arguments and align lyrics."""
    parser = argparse.ArgumentParser(description="Simple lyrics extraction and alignment tool.")
    parser.add_argument("audio_file", help="Path to the audio file")
    parser.add_argument("lyrics_file", help="Path to the lyrics file")
    parser.add_argument("output_file", help="Path to save the output JSON file")
    parser.add_argument("--song-title", default="Unknown Song", help="Title of the song")
    parser.add_argument("--artist-name", default="Unknown Artist", help="Name of the artist")
    parser.add_argument(
        "--conservative",
        action="store_true",
        help="Use Gentle's conservative alignment mode (stricter, drops more "
             "words). OFF by default — conservative mode rejects too many "
             "words on sung music, leaving large gaps. Only enable for "
             "spoken-word audio where you need high-confidence-only timestamps."
    )

    args = parser.parse_args()

    # Ensure Gentle is running
    if not ensure_gentle_running():
        logger.error("Failed to ensure Gentle server is running. Exiting.")
        sys.exit(1)

    # Align lyrics
    success = align_lyrics(
        args.audio_file,
        args.lyrics_file,
        args.output_file,
        args.song_title,
        args.artist_name,
        conservative=args.conservative,
    )
    
    if success:
        logger.info("Lyrics alignment completed successfully!")
        sys.exit(0)
    else:
        logger.error("Lyrics alignment failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()