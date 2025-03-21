"""
Sequence Maker - Lyrics Manager

This module defines the LyricsManager class, which manages lyrics processing.
"""

import logging
import os
import json
import tempfile
import subprocess
import requests
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from models.lyrics import Lyrics, WordTimestamp
from ui.dialogs.lyrics_input_dialog import LyricsInputDialog

class LyricsManager(QObject):
    """
    Manager for lyrics processing.
    
    This class handles the processing of audio files to extract and align lyrics.
    It uses external services like ACRCloud for song identification, Genius for
    lyrics retrieval, and Gentle for word-level alignment.
    
    Attributes:
        app: The main application instance.
    """
    
    # Signals
    lyrics_processed = pyqtSignal(object)
    status_updated = pyqtSignal(str, int)
    
    def __init__(self, app):
        """
        Initialize the lyrics manager.
        
        Args:
            app: The main application instance.
        """
        super().__init__()
        
        self.logger = logging.getLogger("SequenceMaker.LyricsManager")
        self.app = app
        self.lyrics_widget = None
        
        # Load API keys from config
        self._load_api_keys()
    
    def set_lyrics_widget(self, lyrics_widget):
        """
        Set the lyrics widget reference.
        
        Args:
            lyrics_widget: The lyrics widget instance.
        """
        self.lyrics_widget = lyrics_widget
        
        # Connect status signal to widget
        self.status_updated.connect(self.lyrics_widget.update_status)
    
    def update_status(self, status_text, step=None):
        """
        Update the status indicator.
        
        Args:
            status_text (str): Status text to display.
            step (int, optional): Current step in the process (0-3).
        """
        print(f"[LyricsManager] Status update: {status_text}")
        self.logger.info(f"Status update: {status_text}")
        
        # Emit signal to update status in widget
        self.status_updated.emit(status_text, step)
    
    def _load_api_keys(self):
        """Load API keys from config file."""
        print("[LyricsManager] Loading API keys...")
        
        # Define the path to the API keys file
        api_keys_path = os.path.expanduser("~/.sequence_maker/api_keys.json")
        print(f"[LyricsManager] API keys path: {api_keys_path}")
        
        # Initialize default empty keys
        self.acr_access_key = ""
        self.acr_secret_key = ""
        self.acr_host = ""
        self.genius_api_key = ""
        
        # Try to load keys from file
        if os.path.exists(api_keys_path):
            print(f"[LyricsManager] API keys file exists")
            try:
                with open(api_keys_path, 'r') as f:
                    keys = json.load(f)
                
                self.acr_access_key = keys.get("acr_access_key", "")
                self.acr_secret_key = keys.get("acr_secret_key", "")
                self.acr_host = keys.get("acr_host", "")
                self.genius_api_key = keys.get("genius_api_key", "")
                
                self.logger.info("Loaded API keys from config file")
                print("[LyricsManager] Loaded API keys from config file")
            except Exception as e:
                self.logger.error(f"Error loading API keys: {e}")
                print(f"[LyricsManager] Error loading API keys: {e}")
        else:
            print(f"[LyricsManager] API keys file does not exist")
    
    def prompt_user_for_lyrics(self):
        """
        Show a dialog to prompt the user for manual lyrics input.
        
        Returns:
            str or None: The lyrics text entered by the user, or None if cancelled.
        """
        dialog = LyricsInputDialog(self.app.main_window)
        if dialog.exec():
            return dialog.get_lyrics()
        return None
    def process_audio(self, audio_path):
        """
        Process audio to extract and align lyrics.
        
        Args:
            audio_path (str): Path to the audio file.
            
        Returns:
            bool: True if processing was successful, False otherwise.
        """
        # Ensure we have an absolute path
        import os
        audio_path = os.path.abspath(audio_path)
        
        self.logger.info(f"Processing audio for lyrics: {audio_path}")
        print(f"[LyricsManager] Processing audio for lyrics: {audio_path}")
        print(f"[LyricsManager] Processing audio for lyrics: {audio_path}")
        
        # Update status
        self.update_status("Starting lyrics processing...", 0)
        
        # Check if we have API keys
        if not self._check_api_keys():
            self.logger.error("Missing API keys, cannot process lyrics")
            print("[LyricsManager] Missing API keys, cannot process lyrics")
            self.update_status("Error: Missing API keys", None)
            return False
        
        try:
            # Step 1: Identify song using ACRCloud
            self.update_status("Identifying song using ACRCloud...", 1)
            print("[LyricsManager] Step 1: Identifying song using ACRCloud...")
            song_name, artist_name = self._identify_song(audio_path)
            
            lyrics_text = None
            
            if not song_name or not artist_name:
                self.logger.warning("Could not identify song, prompting for manual lyrics input")
                print("[LyricsManager] Could not identify song, prompting for manual lyrics input")
                self.update_status("Song identification failed. Prompting for manual lyrics input...", None)
                
                # Prompt user for manual lyrics input
                lyrics_text = self.prompt_user_for_lyrics()
                
                if not lyrics_text:
                    self.logger.error("User cancelled manual lyrics input")
                    print("[LyricsManager] User cancelled manual lyrics input")
                    self.update_status("Lyrics processing cancelled", None)
                    return False
                
                # Use placeholder values for song and artist
                song_name = "Unknown Song"
                artist_name = "Unknown Artist"
                
                self.logger.info("Using manually entered lyrics")
                print("[LyricsManager] Using manually entered lyrics")
            else:
                self.logger.info(f"Identified song: {song_name} by {artist_name}")
                print(f"[LyricsManager] Identified song: {song_name} by {artist_name}")
                
                # Step 2: Fetch lyrics using Genius API
                self.update_status("Fetching lyrics using Genius API...", 2)
                print("[LyricsManager] Step 2: Fetching lyrics using Genius API...")
                lyrics_text = self._get_lyrics(song_name, artist_name)
                
                if not lyrics_text:
                    self.logger.error("Could not fetch lyrics")
                    print("[LyricsManager] Could not fetch lyrics")
                    self.update_status("Error: Could not fetch lyrics", None)
                    return False
                
                self.logger.info(f"Fetched lyrics for {song_name}")
                print(f"[LyricsManager] Fetched lyrics for {song_name}")
            
            # Step 3: Align lyrics using Gentle
            self.update_status("Aligning lyrics using Gentle...", 3)
            print("[LyricsManager] Step 3: Aligning lyrics using Gentle...")
            word_timestamps = self._align_lyrics(audio_path, lyrics_text)
            
            if not word_timestamps:
                self.logger.error("Could not align lyrics")
                print("[LyricsManager] Could not align lyrics")
                self.update_status("Error: Could not align lyrics", None)
                return False
            
            self.logger.info(f"Aligned {len(word_timestamps)} words")
            print(f"[LyricsManager] Aligned {len(word_timestamps)} words")
            
            # Step 4: Create lyrics object and update project
            self.update_status("Finalizing lyrics processing...", 3)
            print("[LyricsManager] Step 4: Creating lyrics object and updating project...")
            lyrics = Lyrics()
            lyrics.song_name = song_name
            lyrics.artist_name = artist_name
            lyrics.lyrics_text = lyrics_text
            lyrics.word_timestamps = word_timestamps
            
            # Update project
            if self.app.project_manager.current_project:
                self.app.project_manager.current_project.set_lyrics(
                    song_name=song_name,
                    artist_name=artist_name,
                    lyrics_text=lyrics_text,
                    word_timestamps=word_timestamps
                )
                
                # Mark project as changed
                self.app.project_manager.project_changed.emit()
                print("[LyricsManager] Project updated with lyrics data")
            
            # Update status
            self.update_status("Lyrics processing completed successfully", None)
            
            # Emit signal
            print("[LyricsManager] Emitting lyrics_processed signal")
            self.lyrics_processed.emit(lyrics)
            
            print("[LyricsManager] Lyrics processing completed successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Error processing lyrics: {e}")
            print(f"[LyricsManager] Error processing lyrics: {e}")
            self.update_status(f"Error: {str(e)}", None)
            import traceback
            traceback.print_exc()
            return False
    
    def _check_api_keys(self):
        """
        Check if we have all required API keys.
        
        Returns:
            bool: True if all keys are present, False otherwise.
        """
        print("[LyricsManager] Checking API keys...")
        print(f"[LyricsManager] ACR Access Key: {'Present' if self.acr_access_key else 'Missing'}")
        print(f"[LyricsManager] ACR Secret Key: {'Present' if self.acr_secret_key else 'Missing'}")
        print(f"[LyricsManager] ACR Host: {'Present' if self.acr_host else 'Missing'}")
        print(f"[LyricsManager] Genius API Key: {'Present' if self.genius_api_key else 'Missing'}")
        
        result = (
            self.acr_access_key and
            self.acr_secret_key and
            self.acr_host and
            self.genius_api_key
        )
        
        print(f"[LyricsManager] API keys check result: {'All present' if result else 'Some missing'}")
        return result
    def _identify_song(self, audio_path):
        """
        Identify song using ACRCloud.
        
        Args:
            audio_path (str): Path to the audio file.
            
        Returns:
            tuple: (song_name, artist_name) or (None, None) if identification failed.
        """
        try:
            import base64
            import hashlib
            import hmac
            import time
            import requests
            import os
            from pathlib import Path
            
            # Log the audio path for debugging
            self.logger.info(f"Attempting to identify song from file: {audio_path}")
            
            # Check if file exists
            if not os.path.exists(audio_path):
                self.logger.error(f"File does not exist: {audio_path}")
                
                # Try to resolve the path using Path
                path_obj = Path(audio_path)
                if not path_obj.exists():
                    self.logger.error(f"Path object also cannot find file: {path_obj}")
                    
                    # Try to get the absolute path
                    abs_path = os.path.abspath(audio_path)
                    self.logger.error(f"Absolute path: {abs_path}")
                    
                    if not os.path.exists(abs_path):
                        self.logger.error(f"File does not exist at absolute path either")
                        return None, None
                    else:
                        audio_path = abs_path
                        self.logger.info(f"Using absolute path: {audio_path}")
                else:
                    audio_path = str(path_obj.resolve())
                    self.logger.info(f"Using resolved path: {audio_path}")
            
            # Read audio file
            try:
                with open(audio_path, 'rb') as f:
                    sample_bytes = f.read(10 * 1024 * 1024)  # Read up to 10MB
                    self.logger.info(f"Successfully read {len(sample_bytes)} bytes from file")
            except Exception as e:
                self.logger.error(f"Error reading file: {e}")
                return None, None
                sample_bytes = f.read(10 * 1024 * 1024)  # Read up to 10MB
            
            # Prepare request
            http_method = "POST"
            http_uri = "/v1/identify"
            data_type = "audio"
            signature_version = "1"
            timestamp = str(int(time.time()))
            
            # Generate signature
            string_to_sign = http_method + "\n" + http_uri + "\n" + self.acr_access_key + "\n" + data_type + "\n" + signature_version + "\n" + timestamp
            sign = base64.b64encode(hmac.new(self.acr_secret_key.encode('utf-8'), string_to_sign.encode('utf-8'), digestmod=hashlib.sha1).digest()).decode('utf-8')
            
            # Prepare request data
            files = {
                'sample': sample_bytes,
            }
            
            data = {
                'access_key': self.acr_access_key,
                'data_type': data_type,
                'signature': sign,
                'signature_version': signature_version,
                'timestamp': timestamp,
            }
            
            # Send request
            url = f"https://{self.acr_host}{http_uri}"
            response = requests.post(url, files=files, data=data)
            
            # Parse result
            result_dict = response.json()
            
            # Check if we got a match
            if result_dict.get('status', {}).get('code') == 0:
                # Get the first music result
                music = result_dict.get('metadata', {}).get('music', [])
                
                if music:
                    song = music[0]
                    song_name = song.get('title', '')
                    
                    # Get artist name
                    artists = song.get('artists', [])
                    artist_name = artists[0].get('name', '') if artists else ''
                    
                    return song_name, artist_name
            
            return None, None
        
        except Exception as e:
            self.logger.error(f"Error identifying song: {e}")
            return None, None
    
    def _get_lyrics(self, song_name, artist_name):
        """
        Get lyrics using Genius API.
        
        Args:
            song_name (str): Name of the song.
            artist_name (str): Name of the artist.
            
        Returns:
            str: Lyrics text or None if retrieval failed.
        """
        try:
            # Import Genius API client
            import lyricsgenius
            
            # Create Genius client
            genius = lyricsgenius.Genius(self.genius_api_key)
            
            # Search for song
            song = genius.search_song(song_name, artist_name)
            
            # Return lyrics if found
            return song.lyrics if song else None
        
        except Exception as e:
            self.logger.error(f"Error getting lyrics: {e}")
            return None
    
    def _align_lyrics(self, audio_path, lyrics_text):
        """
        Align lyrics using Gentle.
        
        Args:
            audio_path (str): Path to the audio file.
            lyrics_text (str): Lyrics text.
            
        Returns:
            list: List of WordTimestamp objects or None if alignment failed.
        """
        try:
            # Ensure we have an absolute path
            import os
            audio_path = os.path.abspath(audio_path)
            
            self.logger.info(f"Aligning lyrics for audio file: {audio_path}")
            print(f"[LyricsManager] Aligning lyrics for audio file: {audio_path}")
            
            # Verify the file exists
            if not os.path.exists(audio_path):
                self.logger.error(f"Audio file does not exist: {audio_path}")
                print(f"[LyricsManager] Audio file does not exist: {audio_path}")
                return None
            
            # Check if Gentle Docker container is running
            if not self._check_gentle_container():
                # Start Gentle Docker container
                self.logger.info("Gentle container not running, attempting to start it")
                print("[LyricsManager] Gentle container not running, attempting to start it")
                
                if not self._start_gentle_container():
                    self.logger.error("Could not start Gentle Docker container")
                    print("[LyricsManager] Could not start Gentle Docker container")
                    return None
            
            # Send request to Gentle
            try:
                self.logger.info("Opening audio file for Gentle alignment")
                print("[LyricsManager] Opening audio file for Gentle alignment")
                
                with open(audio_path, 'rb') as audio_file:
                    files = {
                        'audio': audio_file,
                        'transcript': (None, lyrics_text)
                    }
                    
                    self.logger.info("Sending request to Gentle API")
                    print("[LyricsManager] Sending request to Gentle API")
                    
                    response = requests.post(
                        'http://localhost:8765/transcriptions?async=false',
                        files=files,
                        timeout=120  # Increase timeout to 2 minutes
                    )
            except FileNotFoundError as e:
                self.logger.error(f"Error opening audio file: {e}")
                print(f"[LyricsManager] Error opening audio file: {e}")
                return None
            except requests.RequestException as e:
                self.logger.error(f"Error communicating with Gentle API: {e}")
                print(f"[LyricsManager] Error communicating with Gentle API: {e}")
                return None
            
            # Check if request was successful
            if response.status_code != 200:
                self.logger.error(f"Gentle API error: {response.status_code}")
                return None
            
            # Parse response
            result = response.json()
            
            # Extract word timestamps
            word_timestamps = []
            
            for word in result.get('words', []):
                # Skip words without alignment
                if 'start' not in word or 'end' not in word:
                    continue
                
                # Create WordTimestamp object
                word_timestamp = WordTimestamp(
                    word=word.get('alignedWord', ''),
                    start=word.get('start', 0.0),
                    end=word.get('end', 0.0)
                )
                
                word_timestamps.append(word_timestamp)
            
            return word_timestamps
        
        except Exception as e:
            self.logger.error(f"Error aligning lyrics: {e}")
            return None
    
    def _check_gentle_container(self):
        """
        Check if Gentle Docker container is running.
        
        Returns:
            bool: True if container is running, False otherwise.
        """
        try:
            # Check if port 8765 is open
            response = requests.get('http://localhost:8765')
            return response.status_code == 200
        except:
            return False
    def _start_gentle_container(self):
        """
        Start Gentle Docker container.
        
        Returns:
            bool: True if container was started successfully, False otherwise.
        """
        try:
            # Update status
            self.update_status("Starting Gentle Docker container...", None)
            
            # Get the path to the start_gentle.py script
            import sys
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            start_gentle_script = os.path.join(script_dir, "scripts", "start_gentle.py")
            
            self.logger.info(f"Using start_gentle.py script at: {start_gentle_script}")
            print(f"[LyricsManager] Using start_gentle.py script at: {start_gentle_script}")
            
            # Check if the script exists
            if not os.path.exists(start_gentle_script):
                self.logger.error(f"start_gentle.py script not found at: {start_gentle_script}")
                print(f"[LyricsManager] start_gentle.py script not found at: {start_gentle_script}")
                return False
            
            # Create a log file path for the script output
            import tempfile
            log_file_path = os.path.join(tempfile.gettempdir(), "gentle_startup.log")
            self.logger.info(f"Script output will be logged to: {log_file_path}")
            print(f"[LyricsManager] Script output will be logged to: {log_file_path}")
            
            # Log the command we're about to run
            # Use shell=True and redirect output to a file
            cmd = f"{sys.executable} {start_gentle_script} > {log_file_path} 2>&1"
            self.logger.info(f"Running command: {cmd}")
            print(f"[LyricsManager] Running command: {cmd}")
            
            # Run the start_gentle.py script with a timeout
            try:
                # Run with shell=True to ensure proper environment and output redirection
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    text=True
                )
                
                # Wait for the process with timeout
                try:
                    process.wait(timeout=60)
                    
                    # Read the log file
                    try:
                        with open(log_file_path, 'r') as log_file:
                            log_content = log_file.read()
                        
                        # Log the output
                        self.logger.info(f"start_gentle.py output: {log_content}")
                        print(f"[LyricsManager] start_gentle.py output: {log_content}")
                    except Exception as e:
                        self.logger.error(f"Error reading log file: {e}")
                        print(f"[LyricsManager] Error reading log file: {e}")
                    
                    # Log the return code
                    self.logger.info(f"start_gentle.py return code: {process.returncode}")
                    print(f"[LyricsManager] start_gentle.py return code: {process.returncode}")
                    
                    if process.returncode != 0:
                        self.logger.error(f"start_gentle.py failed with return code: {process.returncode}")
                        print(f"[LyricsManager] start_gentle.py failed with return code: {process.returncode}")
                
                except subprocess.TimeoutExpired:
                    # Kill the process if it times out
                    process.kill()
                    
                    # Read the log file to see what happened before timeout
                    try:
                        with open(log_file_path, 'r') as log_file:
                            log_content = log_file.read()
                        
                        self.logger.error(f"start_gentle.py timed out after 60 seconds. Last output: {log_content}")
                        print(f"[LyricsManager] start_gentle.py timed out after 60 seconds. Last output: {log_content}")
                    except Exception as e:
                        self.logger.error(f"Error reading log file after timeout: {e}")
                        print(f"[LyricsManager] Error reading log file after timeout: {e}")
                    
                    return False
            except Exception as e:
                self.logger.error(f"Error running start_gentle.py: {e}")
                print(f"[LyricsManager] Error running start_gentle.py: {e}")
                return False
            
            # Check if container is running
            if self._check_gentle_container():
                self.logger.info("Gentle Docker container started successfully")
                print("[LyricsManager] Gentle Docker container started successfully")
                return True
            else:
                self.logger.error("Failed to start Gentle Docker container")
                print("[LyricsManager] Failed to start Gentle Docker container")
                
                # Show error message with more details
                error_msg = "Failed to start Gentle Docker container.\n\n"
                
                if "docker: command not found" in result.stderr or "No such file or directory: 'docker'" in result.stderr:
                    error_msg += "Docker is not installed or not in PATH.\n"
                    error_msg += "Please install Docker and try again."
                elif "docker-compose: command not found" in result.stderr:
                    error_msg += "docker-compose is not installed or not in PATH.\n"
                    error_msg += "Please install docker-compose and try again."
                else:
                    error_msg += f"Error: {result.stderr}"
                
                self.update_status(f"Error: Docker not available", None)
                
                # Show message box with error
                QMessageBox.critical(
                    None,
                    "Gentle Docker Error",
                    error_msg
                )
                
                return False
        
        except Exception as e:
            self.logger.error(f"Error starting Gentle container: {e}")
            print(f"[LyricsManager] Error starting Gentle container: {e}")
            self.update_status(f"Error starting Gentle container: {str(e)}", None)
            return False