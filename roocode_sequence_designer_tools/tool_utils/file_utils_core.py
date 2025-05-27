#!/usr/bin/env python3
"""
Core File Utilities for Roocode Sequence Designer Tools

This module provides utility functions for working with files.
Originally from roo_code_sequence_maker/utils/file_utils.py, migrated here.
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger("RoocodeFileUtilsCore") # Updated logger name

def ensure_directory_exists(directory_path: Union[str, Path]) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Path: Path object for the directory
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def save_json(data: Any, file_path: Union[str, Path], indent: int = 2) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to the JSON file
        indent: Indentation level for the JSON file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure the directory exists
        ensure_directory_exists(Path(file_path).parent)
        
        # Save the data
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
        
        logger.debug(f"Data saved to {file_path}") # Changed to debug for less verbosity
        return True
    
    except Exception as e:
        logger.error(f"Error saving data to {file_path}: {e}")
        return False

def load_json(file_path: Union[str, Path]) -> Optional[Any]:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Any: Loaded data, or None if the file could not be loaded
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        logger.debug(f"Data loaded from {file_path}") # Changed to debug
        return data
    
    except FileNotFoundError:
        logger.warning(f"JSON file not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return None

def list_files(directory_path: Union[str, Path], pattern: str = "*") -> List[Path]:
    """
    List files in a directory that match a pattern. Non-recursive.
    
    Args:
        directory_path: Path to the directory
        pattern: Glob pattern to match files
        
    Returns:
        list: List of Path objects for matching files
    """
    path = Path(directory_path)
    if not path.is_dir():
        logger.warning(f"Directory not found for listing files: {directory_path}")
        return []
    return [p for p in path.glob(pattern) if p.is_file()]

def list_json_files(directory_path: Union[str, Path]) -> List[Path]:
    """
    List JSON files in a directory. Non-recursive.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        list: List of Path objects for JSON files
    """
    return list_files(directory_path, "*.json")

def copy_file(source_path: Union[str, Path], destination_path: Union[str, Path]) -> bool:
    """
    Copy a file from source to destination.
    
    Args:
        source_path: Path to the source file
        destination_path: Path to the destination file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure the destination directory exists
        ensure_directory_exists(Path(destination_path).parent)
        
        # Copy the file
        shutil.copy2(source_path, destination_path)
        
        logger.info(f"File copied from {source_path} to {destination_path}")
        return True
    
    except FileNotFoundError:
        logger.error(f"Source file not found for copy: {source_path}")
        return False
    except Exception as e:
        logger.error(f"Error copying file from {source_path} to {destination_path}: {e}")
        return False

def move_file(source_path: Union[str, Path], destination_path: Union[str, Path]) -> bool:
    """
    Move a file from source to destination.
    
    Args:
        source_path: Path to the source file
        destination_path: Path to the destination file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure the destination directory exists
        ensure_directory_exists(Path(destination_path).parent)
        
        # Move the file
        shutil.move(str(source_path), str(destination_path)) # shutil.move prefers strings
        
        logger.info(f"File moved from {source_path} to {destination_path}")
        return True
    
    except FileNotFoundError:
        logger.error(f"Source file not found for move: {source_path}")
        return False
    except Exception as e:
        logger.error(f"Error moving file from {source_path} to {destination_path}: {e}")
        return False

def delete_file(file_path: Union[str, Path]) -> bool:
    """
    Delete a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        Path(file_path).unlink(missing_ok=True) # missing_ok=True (Python 3.8+) makes it not raise error if not found
        logger.info(f"File deleted (or did not exist): {file_path}")
        return True
    except Exception as e: # Catch other errors like permission issues
        logger.error(f"Error deleting file {file_path}: {e}")
        return False


def get_file_size(file_path: Union[str, Path]) -> Optional[int]:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        int: Size of the file in bytes, or None if the file does not exist or error.
    """
    try:
        return Path(file_path).stat().st_size
    except FileNotFoundError:
        logger.warning(f"File not found for getting size: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error getting size of file {file_path}: {e}")
        return None

def get_file_modification_time(file_path: Union[str, Path]) -> Optional[float]:
    """
    Get the modification time of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        float: Modification time of the file (seconds since epoch), or None if error.
    """
    try:
        return Path(file_path).stat().st_mtime
    except FileNotFoundError:
        logger.warning(f"File not found for getting modification time: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error getting modification time of file {file_path}: {e}")
        return None

def is_file_newer_than(file_path: Union[str, Path], reference_path: Union[str, Path]) -> Optional[bool]:
    """
    Check if a file is newer than a reference file.
    
    Args:
        file_path: Path to the file
        reference_path: Path to the reference file
        
    Returns:
        bool: True if the file is newer than the reference file.
              False if older or same.
              None if either file doesn't exist or error.
    """
    try:
        file_mtime = get_file_modification_time(file_path)
        reference_mtime = get_file_modification_time(reference_path)
        
        if file_mtime is None or reference_mtime is None:
            return None # One of the files (or both) might not exist
        
        return file_mtime > reference_mtime
    
    except Exception as e: # Should be caught by get_file_modification_time already
        logger.error(f"Error comparing modification times: {e}")
        return None

def find_files_by_extension(directory_path: Union[str, Path], extension: str, recursive: bool = False) -> List[Path]:
    """
    Find files with a specific extension in a directory.
    
    Args:
        directory_path: Path to the directory
        extension: File extension to search for (e.g., ".json" or "json")
        recursive: If True, search recursively. Defaults to False.
        
    Returns:
        list: List of Path objects for matching files
    """
    if not extension.startswith("."):
        extension = f".{extension}"
    
    path = Path(directory_path)
    if not path.is_dir():
        logger.warning(f"Directory not found for finding files: {directory_path}")
        return []

    pattern = f"**/*{extension}" if recursive else f"*{extension}"
    return [p for p in path.glob(pattern) if p.is_file()]

# LTX Sequence Maker specific functions - migrated for now, can be reviewed/pruned later
# These might depend on specific file formats not used by the new toolkit.

LTX_STD_EXTENSIONS = [
    '.seqdesign.json', '.prg.json', '.ballseq.json',
    '.synced_lyrics.json', '.analysis_report.json',
    '.beatpattern.json', '.sectiontheme.json'
]

def find_sequence_files(directory_path: Union[str, Path]) -> List[Path]:
    """
    Find LTX sequence files in a directory (recursively).
    This interpretation of "sequence files" is from the original LTX Sequence Maker.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        list: List of Path objects for sequence files
    """
    path = Path(directory_path)
    if not path.is_dir():
        return []

    # Find files with standardized extensions relevant to LTX sequence concepts
    seqdesign_files = find_files_by_extension(directory_path, ".seqdesign.json", recursive=True)
    prg_files = find_files_by_extension(directory_path, ".prg.json", recursive=True)
    ballseq_files = find_files_by_extension(directory_path, ".ballseq.json", recursive=True)
    
    # For backward compatibility, also find generic .json files that might be sequences
    all_json_files = find_files_by_extension(directory_path, ".json", recursive=True)
    
    # Filter out files that already have more specific standardized extensions
    # to avoid double-counting if a generic .json is also a .prg.json (unlikely by name, but good check)
    current_known_files = set(seqdesign_files + prg_files + ballseq_files)
    
    generic_json_files = [
        f for f in all_json_files
        if f not in current_known_files and not any(f.name.endswith(std_ext) for std_ext in LTX_STD_EXTENSIONS)
    ]
    
    return list(current_known_files) + generic_json_files

def get_sequence_metadata(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    Get metadata for an LTX sequence file (original LTX format).
    
    Args:
        file_path: Path to the sequence file (typically .ballseq.json or .prg.json)
        
    Returns:
        dict: Metadata for the sequence, or None if the file could not be loaded or is not recognized format.
    """
    data = load_json(file_path)
    
    if data is None or not isinstance(data, dict):
        return None
    
    # Extract metadata (assuming LTX .ballseq.json or .prg.json like structure)
    # This is highly specific to the old format.
    sequence_data = data.get("sequence")
    if not isinstance(sequence_data, dict): # LTX format expects sequence to be a dict of time-keyed frames
        # Could be a .seqdesign.json or other format.
        # For now, return basic info if not the expected LTX structure.
        return {
            "file_path": str(file_path),
            "file_name": Path(file_path).name,
            "type": "unknown_sequence_format_for_ltx_metadata"
        }

    metadata = {
        "file_path": str(file_path),
        "file_name": Path(file_path).name,
        "pixels": data.get("pixels", 0), # From .ballseq.json
        "num_pixels": data.get("num_pixels", data.get("pixels", 0)), # From .prg.json
        "refresh_rate": data.get("refresh_rate", 0),
        "sequence_length_frames": len(sequence_data),
        "duration_seconds": max([float(t) for t in sequence_data.keys() if t.replace('.', '', 1).isdigit()], default=0.0)
    }
    
    return metadata

def list_sequence_metadata(directory_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    List metadata for all LTX sequence files in a directory.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        list: List of metadata dictionaries for sequence files
    """
    sequence_files = find_sequence_files(directory_path)
    metadata_list = []
    
    for file_path in sequence_files:
        metadata = get_sequence_metadata(file_path)
        if metadata is not None:
            metadata_list.append(metadata)
    
    return metadata_list

def convert_sequence_format_segments_to_ltx(input_path: Union[str, Path], output_path: Union[str, Path]) -> bool:
    """
    Convert a sequence file from a simple "segments" list format to LTX .ballseq.json format.
    The "segments" format is assumed to be a list of dicts: [{"start_time": t, "color": [r,g,b]}, ...].
    
    Args:
        input_path: Path to the input file (segments format)
        output_path: Path to the output file (LTX .ballseq.json format)
        
    Returns:
        bool: True if successful, False otherwise
    """
    output_path_obj = Path(output_path)
    # Ensure output path has the correct extension
    if not output_path_obj.name.endswith('.ballseq.json'):
        output_path_obj = output_path_obj.with_suffix('.ballseq.json')
        logger.info(f"Adjusting output path to use standardized extension: {output_path_obj}")
    try:
        # Load the input file (list of segments)
        segments = load_json(input_path)
        
        if not isinstance(segments, list):
            logger.error(f"Input file {input_path} is not a valid list of segments.")
            return False
        
        # Convert to LTX format
        ltx_sequence_frames = {} # LTX sequence is a dict of time-keyed frames
        
        for segment in segments:
            if not isinstance(segment, dict):
                logger.warning(f"Skipping invalid segment (not a dict): {segment}")
                continue
            start_time = segment.get("start_time")
            color = segment.get("color")
            
            if start_time is None or color is None:
                logger.warning(f"Skipping segment with missing start_time or color: {segment}")
                continue
            
            try:
                # Ensure time is string, color is list of 3 ints
                time_key = str(float(start_time))
                resolved_color = [int(c) for c in color[:3]] if isinstance(color, list) and len(color) >=3 else [0,0,0]
                ltx_sequence_frames[time_key] = {"color": resolved_color}
            except ValueError:
                logger.warning(f"Skipping segment with invalid time/color format: {segment}")
                continue

        # Create the final JSON structure for .ballseq.json
        data_to_save = {
            "pixels": 4,  # Default value, should ideally come from somewhere
            "refresh_rate": 50,  # Default value
            "sequence": ltx_sequence_frames
        }
        
        # Save to output file
        return save_json(data_to_save, output_path_obj)
    
    except Exception as e:
        logger.error(f"Error converting sequence format from segments to LTX: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create a test directory
    test_dir_main = Path("temp_file_utils_test_dir") # Renamed to avoid conflict with other tests
    ensure_directory_exists(test_dir_main)
    
    # Create a test sequence for LTX format
    test_ltx_sequence = {
        "pixels": 4,
        "refresh_rate": 50,
        "sequence": {
            "0.0": {"color": [255, 0, 0]},
            "1.0": {"color": [0, 255, 0]},
            "2.0": {"color": [0, 0, 255]}
        }
    }
    test_ltx_file = test_dir_main / "test_sequence.ballseq.json"
    save_json(test_ltx_sequence, test_ltx_file)
    
    loaded_ltx_seq = load_json(test_ltx_file)
    print(f"Loaded LTX sequence: {loaded_ltx_seq}")
    
    metadata_ltx = get_sequence_metadata(test_ltx_file)
    print(f"LTX Sequence metadata: {metadata_ltx}")
    
    # Create a test segments file for conversion
    test_segments_data = [
        {"start_time": 0.0, "color": [255,0,0]},
        {"start_time": 0.5, "color": [0,255,0], "some_other_key": "value"}, # Extra key should be ignored
        {"start_time": 1.0, "color": [0,0,255]}
    ]
    test_segments_file = test_dir_main / "test_segments.json"
    save_json(test_segments_data, test_segments_file)
    
    converted_ltx_path = test_dir_main / "converted_from_segments.ballseq.json"
    success_conversion = convert_sequence_format_segments_to_ltx(test_segments_file, converted_ltx_path)
    if success_conversion:
        print(f"Successfully converted segments to LTX: {converted_ltx_path}")
        loaded_converted = load_json(converted_ltx_path)
        print(f"Converted LTX data: {loaded_converted}")
    else:
        print(f"Failed to convert segments to LTX.")

    # List all JSON files in the test directory
    json_files_list = list_json_files(test_dir_main)
    print(f"JSON files in {test_dir_main}: {json_files_list}")
    
    # Clean up
    # Use shutil.rmtree to remove the directory and its contents
    try:
        shutil.rmtree(test_dir_main)
        print(f"Test directory {test_dir_main} and its contents deleted.")
    except Exception as e:
        print(f"Error deleting test directory {test_dir_main}: {e}")