#!/usr/bin/env python3
"""
Cache Manager for Roocode Sequence Designer Tools

Provides persistent, cross-session caching for audio analysis results
and potentially other expensive computations.
"""

import os
import json
import hashlib
import shutil
from typing import Dict, Any, Optional, Union

DEFAULT_CACHE_DIR_NAME = "cache"
DEFAULT_APP_DIR_NAME = ".roocode_sequence_designer"

class CacheManager:
    """
    Manages caching of data to the filesystem.
    """
    def __init__(self, cache_dir: Optional[str] = None, app_name: str = DEFAULT_APP_DIR_NAME):
        """
        Initializes the CacheManager.

        Args:
            cache_dir: Specific cache directory path. If None, uses default.
            app_name: Name of the application directory in the user's home.
        """
        if cache_dir:
            self.cache_root_dir = cache_dir
        else:
            # Default cache directory: ~/.<app_name>/cache/
            home_dir = os.path.expanduser("~")
            self.cache_root_dir = os.path.join(home_dir, app_name, DEFAULT_CACHE_DIR_NAME)

        # Environment variable override for cache directory
        env_cache_dir = os.environ.get("ROOCODE_CACHE_DIR")
        if env_cache_dir:
            self.cache_root_dir = env_cache_dir
        
        os.makedirs(self.cache_root_dir, exist_ok=True)

    def _get_file_hash(self, file_path: str) -> str:
        """
        Generates an MD5 hash for the content of a file.

        Args:
            file_path: Path to the file.

        Returns:
            MD5 hash string of the file content.
        """
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192): # Read in 8KB chunks
                    hasher.update(chunk)
            return hasher.hexdigest()
        except FileNotFoundError:
            # If file not found during hashing, this will be part of cache key gen issue.
            # Or, we can decide to return a specific marker or raise error earlier.
            # For cache key generation, if file doesn't exist, perhaps no caching.
            raise
        except Exception as e:
            print(f"Warning: Could not hash file {file_path}: {e}")
            return "file_hash_error"


    def generate_cache_key(self, 
                           identifier: str,
                           params: Optional[Dict[str, Any]] = None, 
                           file_path_for_hash: Optional[str] = None) -> str:
        """
        Generates a unique cache key.

        Args:
            identifier: A primary string to identify the item being cached (e.g., tool name, file path).
            params: A dictionary of parameters that affect the cached output.
            file_path_for_hash: Optional path to a file whose content hash should be part of the key.

        Returns:
            A string representing the cache key.
        """
        key_parts = [identifier]

        if file_path_for_hash:
            try:
                file_hash = self._get_file_hash(file_path_for_hash)
                key_parts.append(f"filehash_{file_hash}")
            except FileNotFoundError:
                 key_parts.append("file_not_found_for_hash")


        if params:
            # Sort params by key to ensure consistent hash
            sorted_params = json.dumps(params, sort_keys=True)
            params_hash = hashlib.md5(sorted_params.encode('utf-8')).hexdigest()
            key_parts.append(f"params_{params_hash}")
        
        # Combine parts and hash for a fixed-length key filename
        combined_string = "_".join(key_parts)
        return hashlib.md5(combined_string.encode('utf-8')).hexdigest() + ".json"

    def get_cache_filepath(self, cache_key: str) -> str:
        """
        Constructs the full path for a cache file.
        """
        return os.path.join(self.cache_root_dir, cache_key)

    def load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Loads data from a cache file.

        Args:
            cache_key: The cache key for the data.

        Returns:
            The loaded data as a dictionary, or None if not found or invalid.
        """
        cache_file_path = self.get_cache_filepath(cache_key)
        if os.path.exists(cache_file_path):
            try:
                with open(cache_file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Corrupted cache file: {cache_file_path}. Removing.")
                os.remove(cache_file_path)
                return None
            except Exception as e:
                print(f"Warning: Error loading cache file {cache_file_path}: {e}")
                return None
        return None

    def save_to_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """
        Saves data to a cache file.

        Args:
            cache_key: The cache key for the data.
            data: The data to save (must be JSON serializable).
        """
        cache_file_path = self.get_cache_filepath(cache_key)
        try:
            with open(cache_file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error: Could not save to cache file {cache_file_path}: {e}")

    def clear_cache_by_key(self, cache_key: str) -> bool:
        """
        Clears a specific cache entry by its key.

        Args:
            cache_key: The cache key of the entry to remove.
        
        Returns:
            True if an entry was removed, False otherwise.
        """
        cache_file_path = self.get_cache_filepath(cache_key)
        if os.path.exists(cache_file_path):
            try:
                os.remove(cache_file_path)
                print(f"Cache entry removed: {cache_file_path}")
                return True
            except Exception as e:
                print(f"Error removing cache entry {cache_file_path}: {e}")
        return False

    def clear_cache_for_file(self, file_path_for_hash: str, identifier_prefix: str = ""):
        """
        Clears all cache entries associated with a specific file path hash.
        This is a best-effort clear as it relies on iterating through all cache files
        or constructing potential keys if `identifier_prefix` and parameter combinations are known.
        
        For simplicity, this example might require more specific key generation to make
        targeted clearing easier without iterating all cache files. A more robust solution
        might involve a manifest file or a naming convention that includes the original file_path hash
        more directly if this feature is critical.

        A simpler approach if params are not too varied for a file:
        Construct a partial key using identifier and file_hash and try to match.
        
        This implementation currently does not support this well without iterating all files.
        A more practical way is to use a known `cache_key` or clear all.
        """
        print(f"Warning: Clearing cache specifically for file '{file_path_for_hash}' is complex "
              f"without knowing all associated params. Use clear_cache_by_key or clear_all_cache.")
        # Placeholder - would require more advanced cache key management or iteration

    def clear_all_cache(self) -> None:
        """
        Clears all cache files in the cache directory.
        """
        try:
            for item_name in os.listdir(self.cache_root_dir):
                item_path = os.path.join(self.cache_root_dir, item_name)
                if os.path.isfile(item_path) and item_name.endswith(".json"):
                    os.remove(item_path)
            print(f"All cache cleared from: {self.cache_root_dir}")
        except Exception as e:
            print(f"Error clearing all cache: {e}")

if __name__ == "__main__":
    # Example Usage
    cache_manager = CacheManager()
    print(f"Cache directory: {cache_manager.cache_root_dir}")

    # Create a dummy file to hash
    dummy_file = "dummy_audio.mp3"
    with open(dummy_file, "wb") as f:
        f.write(os.urandom(1024)) # 1KB dummy data

    analysis_params_1 = {"feature": "beats", "rate": 44100}
    analysis_params_2 = {"feature": "chroma", "rate": 22050}

    # Generate cache keys
    key1 = cache_manager.generate_cache_key(
        identifier="extract_audio_features", 
        params=analysis_params_1,
        file_path_for_hash=dummy_file
    )
    key2 = cache_manager.generate_cache_key(
        identifier="extract_audio_features",
        params=analysis_params_2,
        file_path_for_hash=dummy_file
    )
    key_no_params = cache_manager.generate_cache_key(
        identifier="some_other_tool",
        file_path_for_hash=dummy_file
    )

    print(f"Cache key 1: {key1}")
    print(f"Cache key 2: {key2}")
    print(f"Cache key (no params): {key_no_params}")

    # Save some data
    data1 = {"beats": [0.5, 1.0, 1.5], "source_hash": cache_manager._get_file_hash(dummy_file)}
    cache_manager.save_to_cache(key1, data1)
    print(f"Saved data for key1.")

    # Load data
    loaded_data1 = cache_manager.load_from_cache(key1)
    if loaded_data1:
        print(f"Loaded data for key1: {loaded_data1}")
        assert loaded_data1["beats"] == data1["beats"]
    
    loaded_data2 = cache_manager.load_from_cache(key2)
    if not loaded_data2:
        print(f"Data for key2 not found (as expected).")

    # Clear specific cache
    cache_manager.clear_cache_by_key(key1)
    loaded_data1_after_clear = cache_manager.load_from_cache(key1)
    if not loaded_data1_after_clear:
        print(f"Data for key1 successfully cleared.")

    # Re-save for full clear test
    cache_manager.save_to_cache(key1, data1)
    cache_manager.save_to_cache(key2, {"chroma_data": "example"})
    
    # Clear all cache
    # cache_manager.clear_all_cache() # Uncomment to test
    # loaded_data1_after_all_clear = cache_manager.load_from_cache(key1)
    # if not loaded_data1_after_all_clear:
    #    print(f"All cache successfully cleared.")

    # Cleanup dummy file
    os.remove(dummy_file)
    print("CacheManager example finished.")