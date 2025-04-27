#!/usr/bin/env python3
"""
File Utilities for LTX Sequence Maker

This module provides utility functions for working with files in the LTX Sequence Maker.
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger("FileUtils")

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
        
        logger.info(f"Data saved to {file_path}")
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
        
        logger.info(f"Data loaded from {file_path}")
        return data
    
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return None

def list_files(directory_path: Union[str, Path], pattern: str = "*") -> List[Path]:
    """
    List files in a directory that match a pattern.
    
    Args:
        directory_path: Path to the directory
        pattern: Glob pattern to match files
        
    Returns:
        list: List of Path objects for matching files
    """
    path = Path(directory_path)
    return list(path.glob(pattern))

def list_json_files(directory_path: Union[str, Path]) -> List[Path]:
    """
    List JSON files in a directory.
    
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
        shutil.move(source_path, destination_path)
        
        logger.info(f"File moved from {source_path} to {destination_path}")
        return True
    
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
        os.remove(file_path)
        
        logger.info(f"File deleted: {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return False

def get_file_size(file_path: Union[str, Path]) -> Optional[int]:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        int: Size of the file in bytes, or None if the file does not exist
    """
    try:
        return os.path.getsize(file_path)
    
    except Exception as e:
        logger.error(f"Error getting size of file {file_path}: {e}")
        return None

def get_file_modification_time(file_path: Union[str, Path]) -> Optional[float]:
    """
    Get the modification time of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        float: Modification time of the file (seconds since epoch), or None if the file does not exist
    """
    try:
        return os.path.getmtime(file_path)
    
    except Exception as e:
        logger.error(f"Error getting modification time of file {file_path}: {e}")
        return None

def is_file_newer_than(file_path: Union[str, Path], reference_path: Union[str, Path]) -> bool:
    """
    Check if a file is newer than a reference file.
    
    Args:
        file_path: Path to the file
        reference_path: Path to the reference file
        
    Returns:
        bool: True if the file is newer than the reference file, False otherwise
    """
    try:
        file_mtime = get_file_modification_time(file_path)
        reference_mtime = get_file_modification_time(reference_path)
        
        if file_mtime is None or reference_mtime is None:
            return False
        
        return file_mtime > reference_mtime
    
    except Exception as e:
        logger.error(f"Error comparing modification times: {e}")
        return False

def find_files_by_extension(directory_path: Union[str, Path], extension: str) -> List[Path]:
    """
    Find files with a specific extension in a directory (recursively).
    
    Args:
        directory_path: Path to the directory
        extension: File extension to search for (e.g., ".json")
        
    Returns:
        list: List of Path objects for matching files
    """
    if not extension.startswith("."):
        extension = f".{extension}"
    
    path = Path(directory_path)
    return list(path.glob(f"**/*{extension}"))

def find_sequence_files(directory_path: Union[str, Path]) -> List[Path]:
    """
    Find LTX sequence files in a directory (recursively).
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        list: List of Path objects for sequence files
    """
    return find_files_by_extension(directory_path, ".json")

def get_sequence_metadata(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    Get metadata for an LTX sequence file.
    
    Args:
        file_path: Path to the sequence file
        
    Returns:
        dict: Metadata for the sequence, or None if the file could not be loaded
    """
    data = load_json(file_path)
    
    if data is None:
        return None
    
    # Extract metadata
    metadata = {
        "file_path": str(file_path),
        "file_name": Path(file_path).name,
        "pixels": data.get("pixels", 0),
        "refresh_rate": data.get("refresh_rate", 0),
        "sequence_length": len(data.get("sequence", {})),
        "duration": max([float(t) for t in data.get("sequence", {}).keys()], default=0)
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

def convert_sequence_format(input_path: Union[str, Path], output_path: Union[str, Path]) -> bool:
    """
    Convert a sequence file from segments format to LTX format.
    
    Args:
        input_path: Path to the input file (segments format)
        output_path: Path to the output file (LTX format)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load the input file
        segments = load_json(input_path)
        
        if segments is None:
            return False
        
        # Convert to LTX format
        sequence = {}
        
        for segment in segments:
            start_time = segment.get("start_time", 0)
            color = segment.get("color", [0, 0, 0])
            
            # Add the color change at the start time
            sequence[str(start_time)] = {"color": color}
        
        # Create the final JSON structure
        data = {
            "pixels": 4,  # Default value
            "refresh_rate": 50,  # Default value
            "sequence": sequence
        }
        
        # Save to output file
        return save_json(data, output_path)
    
    except Exception as e:
        logger.error(f"Error converting sequence format: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create a test directory
    test_dir = Path("test_files")
    ensure_directory_exists(test_dir)
    
    # Create a test sequence
    test_sequence = {
        "pixels": 4,
        "refresh_rate": 50,
        "sequence": {
            "0": {"color": [255, 0, 0]},
            "1": {"color": [0, 255, 0]},
            "2": {"color": [0, 0, 255]}
        }
    }
    
    # Save the test sequence
    test_file = test_dir / "test_sequence.json"
    save_json(test_sequence, test_file)
    
    # Load the test sequence
    loaded_sequence = load_json(test_file)
    print(f"Loaded sequence: {loaded_sequence}")
    
    # Get metadata for the test sequence
    metadata = get_sequence_metadata(test_file)
    print(f"Sequence metadata: {metadata}")
    
    # List all JSON files in the test directory
    json_files = list_json_files(test_dir)
    print(f"JSON files in {test_dir}: {json_files}")
    
    # Clean up
    delete_file(test_file)
    print(f"Test file deleted: {test_file}")