"""
Sequence Maker - Resources

This module provides access to application resources.
"""

import os
import logging
from pathlib import Path


logger = logging.getLogger("SequenceMaker.Resources")


def get_resource_path(relative_path):
    """
    Get the absolute path to a resource file.
    
    Args:
        relative_path (str): Relative path to the resource file.
    
    Returns:
        str: Absolute path to the resource file.
    """
    try:
        # Get the directory of this file
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the absolute path
        absolute_path = os.path.join(base_path, relative_path)
        
        # Check if the file exists
        if not os.path.exists(absolute_path):
            logger.warning(f"Resource file not found: {absolute_path}")
        
        return absolute_path
    
    except Exception as e:
        logger.error(f"Error getting resource path: {e}")
        return None


def get_icon_path(icon_name):
    """
    Get the absolute path to an icon file.
    
    Args:
        icon_name (str): Name of the icon file.
    
    Returns:
        str: Absolute path to the icon file.
    """
    return get_resource_path(f"icons/{icon_name}")


def get_style_path(style_name):
    """
    Get the absolute path to a style file.
    
    Args:
        style_name (str): Name of the style file.
    
    Returns:
        str: Absolute path to the style file.
    """
    return get_resource_path(f"styles/{style_name}")


def get_template_path(template_name):
    """
    Get the absolute path to a template file.
    
    Args:
        template_name (str): Name of the template file.
    
    Returns:
        str: Absolute path to the template file.
    """
    return get_resource_path(f"templates/{template_name}")


def get_resource_dirs():
    """
    Get a list of resource directories.
    
    Returns:
        list: List of resource directory paths.
    """
    try:
        # Get the directory of this file
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Get all subdirectories
        subdirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        
        # Filter out __pycache__ and other non-resource directories
        resource_dirs = [d for d in subdirs if not d.startswith("__")]
        
        return resource_dirs
    
    except Exception as e:
        logger.error(f"Error getting resource directories: {e}")
        return []


def list_resources(resource_type):
    """
    List all resources of a specific type.
    
    Args:
        resource_type (str): Type of resource (e.g., "icons", "styles", "templates").
    
    Returns:
        list: List of resource file names.
    """
    try:
        # Get the directory of this file
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the resource directory path
        resource_dir = os.path.join(base_path, resource_type)
        
        # Check if the directory exists
        if not os.path.exists(resource_dir) or not os.path.isdir(resource_dir):
            logger.warning(f"Resource directory not found: {resource_dir}")
            return []
        
        # List all files in the directory
        files = [f for f in os.listdir(resource_dir) if os.path.isfile(os.path.join(resource_dir, f))]
        
        return files
    
    except Exception as e:
        logger.error(f"Error listing resources: {e}")
        return []