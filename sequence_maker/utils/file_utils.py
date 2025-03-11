"""
Sequence Maker - File Utilities

This module provides utility functions for file operations.
"""

import os
import shutil
import logging
import tempfile
import base64
from pathlib import Path


logger = logging.getLogger("SequenceMaker.FileUtils")


def ensure_directory_exists(directory):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory (str): Directory path.
    
    Returns:
        bool: True if the directory exists or was created, False otherwise.
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False


def get_file_extension(file_path):
    """
    Get the extension of a file.
    
    Args:
        file_path (str): File path.
    
    Returns:
        str: File extension (including the dot), or empty string if no extension.
    """
    return os.path.splitext(file_path)[1]


def get_file_name(file_path):
    """
    Get the name of a file without extension.
    
    Args:
        file_path (str): File path.
    
    Returns:
        str: File name without extension.
    """
    return os.path.splitext(os.path.basename(file_path))[0]


def get_file_size(file_path):
    """
    Get the size of a file in bytes.
    
    Args:
        file_path (str): File path.
    
    Returns:
        int: File size in bytes, or 0 if the file doesn't exist.
    """
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        logger.error(f"Error getting file size for {file_path}: {e}")
        return 0


def copy_file(source, destination):
    """
    Copy a file from source to destination.
    
    Args:
        source (str): Source file path.
        destination (str): Destination file path.
    
    Returns:
        bool: True if the file was copied successfully, False otherwise.
    """
    try:
        # Ensure destination directory exists
        dest_dir = os.path.dirname(destination)
        ensure_directory_exists(dest_dir)
        
        # Copy file
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        logger.error(f"Error copying file from {source} to {destination}: {e}")
        return False


def move_file(source, destination):
    """
    Move a file from source to destination.
    
    Args:
        source (str): Source file path.
        destination (str): Destination file path.
    
    Returns:
        bool: True if the file was moved successfully, False otherwise.
    """
    try:
        # Ensure destination directory exists
        dest_dir = os.path.dirname(destination)
        ensure_directory_exists(dest_dir)
        
        # Move file
        shutil.move(source, destination)
        return True
    except Exception as e:
        logger.error(f"Error moving file from {source} to {destination}: {e}")
        return False


def delete_file(file_path):
    """
    Delete a file.
    
    Args:
        file_path (str): File path.
    
    Returns:
        bool: True if the file was deleted successfully, False otherwise.
    """
    try:
        os.remove(file_path)
        return True
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return False


def create_temp_file(suffix=None):
    """
    Create a temporary file.
    
    Args:
        suffix (str, optional): File suffix (extension). Defaults to None.
    
    Returns:
        str: Path to the temporary file, or None if creation failed.
    """
    try:
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        return path
    except Exception as e:
        logger.error(f"Error creating temporary file: {e}")
        return None


def create_temp_directory():
    """
    Create a temporary directory.
    
    Returns:
        str: Path to the temporary directory, or None if creation failed.
    """
    try:
        return tempfile.mkdtemp()
    except Exception as e:
        logger.error(f"Error creating temporary directory: {e}")
        return None


def list_files(directory, pattern=None, recursive=False):
    """
    List files in a directory.
    
    Args:
        directory (str): Directory path.
        pattern (str, optional): File pattern (glob). Defaults to None.
        recursive (bool, optional): Whether to search recursively. Defaults to False.
    
    Returns:
        list: List of file paths, or empty list if the directory doesn't exist.
    """
    try:
        path = Path(directory)
        
        if not path.exists() or not path.is_dir():
            return []
        
        if recursive:
            if pattern:
                return [str(f) for f in path.glob(f"**/{pattern}") if f.is_file()]
            else:
                return [str(f) for f in path.glob("**/*") if f.is_file()]
        else:
            if pattern:
                return [str(f) for f in path.glob(pattern) if f.is_file()]
            else:
                return [str(f) for f in path.glob("*") if f.is_file()]
    
    except Exception as e:
        logger.error(f"Error listing files in {directory}: {e}")
        return []


def list_directories(directory, recursive=False):
    """
    List subdirectories in a directory.
    
    Args:
        directory (str): Directory path.
        recursive (bool, optional): Whether to search recursively. Defaults to False.
    
    Returns:
        list: List of directory paths, or empty list if the directory doesn't exist.
    """
    try:
        path = Path(directory)
        
        if not path.exists() or not path.is_dir():
            return []
        
        if recursive:
            return [str(d) for d in path.glob("**/*/") if d.is_dir()]
        else:
            return [str(d) for d in path.glob("*/") if d.is_dir()]
    
    except Exception as e:
        logger.error(f"Error listing directories in {directory}: {e}")
        return []


def read_file(file_path, binary=False):
    """
    Read a file.
    
    Args:
        file_path (str): File path.
        binary (bool, optional): Whether to read in binary mode. Defaults to False.
    
    Returns:
        str or bytes: File contents, or None if reading failed.
    """
    try:
        mode = 'rb' if binary else 'r'
        with open(file_path, mode) as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None


def write_file(file_path, content, binary=False):
    """
    Write content to a file.
    
    Args:
        file_path (str): File path.
        content (str or bytes): Content to write.
        binary (bool, optional): Whether to write in binary mode. Defaults to False.
    
    Returns:
        bool: True if the file was written successfully, False otherwise.
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        ensure_directory_exists(directory)
        
        # Write file
        mode = 'wb' if binary else 'w'
        with open(file_path, mode) as f:
            f.write(content)
        
        return True
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {e}")
        return False


def encode_file_to_base64(file_path):
    """
    Encode a file to base64.
    
    Args:
        file_path (str): File path.
    
    Returns:
        str: Base64-encoded file contents, or None if encoding failed.
    """
    try:
        with open(file_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding file {file_path} to base64: {e}")
        return None


def decode_base64_to_file(base64_data, file_path):
    """
    Decode base64 data to a file.
    
    Args:
        base64_data (str): Base64-encoded data.
        file_path (str): File path.
    
    Returns:
        bool: True if the file was written successfully, False otherwise.
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        ensure_directory_exists(directory)
        
        # Decode and write file
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(base64_data))
        
        return True
    except Exception as e:
        logger.error(f"Error decoding base64 data to file {file_path}: {e}")
        return False