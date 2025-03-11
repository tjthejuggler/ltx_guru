"""
Sequence Maker - JSON Utilities

This module provides utility functions for JSON operations.
"""

import json
import logging


logger = logging.getLogger("SequenceMaker.JSONUtils")


def load_json(file_path):
    """
    Load JSON from a file.
    
    Args:
        file_path (str): File path.
    
    Returns:
        dict: JSON data, or None if loading failed.
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {e}")
        return None


def save_json(file_path, data, indent=2):
    """
    Save JSON data to a file.
    
    Args:
        file_path (str): File path.
        data: JSON-serializable data.
        indent (int, optional): Indentation level. Defaults to 2.
    
    Returns:
        bool: True if the file was saved successfully, False otherwise.
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {e}")
        return False


def parse_json(json_string):
    """
    Parse a JSON string.
    
    Args:
        json_string (str): JSON string.
    
    Returns:
        dict: JSON data, or None if parsing failed.
    """
    try:
        return json.loads(json_string)
    except Exception as e:
        logger.error(f"Error parsing JSON string: {e}")
        return None


def to_json_string(data, indent=None):
    """
    Convert data to a JSON string.
    
    Args:
        data: JSON-serializable data.
        indent (int, optional): Indentation level. Defaults to None.
    
    Returns:
        str: JSON string, or None if conversion failed.
    """
    try:
        return json.dumps(data, indent=indent)
    except Exception as e:
        logger.error(f"Error converting data to JSON string: {e}")
        return None


def merge_json(base, overlay):
    """
    Merge two JSON objects.
    
    Args:
        base (dict): Base JSON object.
        overlay (dict): Overlay JSON object.
    
    Returns:
        dict: Merged JSON object.
    """
    if not isinstance(base, dict) or not isinstance(overlay, dict):
        return overlay
    
    result = base.copy()
    
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_json(result[key], value)
        else:
            result[key] = value
    
    return result


def extract_json_blocks(text):
    """
    Extract JSON blocks from text.
    
    Args:
        text (str): Text to extract JSON blocks from.
    
    Returns:
        list: List of JSON block strings.
    """
    import re
    
    json_blocks = []
    
    # Look for blocks between ```json and ```
    json_pattern = r"```json\s*([\s\S]*?)\s*```"
    matches = re.findall(json_pattern, text)
    
    if matches:
        json_blocks.extend(matches)
    
    # Also look for blocks between { and }
    brace_pattern = r"(\{[\s\S]*?\})"
    matches = re.findall(brace_pattern, text)
    
    if matches:
        for match in matches:
            # Try to parse as JSON to validate
            try:
                json.loads(match)
                json_blocks.append(match)
            except:
                pass
    
    return json_blocks


def validate_json_schema(data, schema):
    """
    Validate JSON data against a schema.
    
    Args:
        data: JSON data to validate.
        schema (dict): JSON schema.
    
    Returns:
        bool: True if the data is valid, False otherwise.
    """
    try:
        import jsonschema
        jsonschema.validate(data, schema)
        return True
    except ImportError:
        logger.warning("jsonschema module not available, skipping validation")
        return True
    except Exception as e:
        logger.error(f"JSON validation error: {e}")
        return False


def get_json_path(data, path):
    """
    Get a value from a JSON object using a path.
    
    Args:
        data: JSON data.
        path (str): Path to the value (e.g., "a.b.c").
    
    Returns:
        The value at the specified path, or None if the path doesn't exist.
    """
    try:
        parts = path.split('.')
        result = data
        
        for part in parts:
            if isinstance(result, dict) and part in result:
                result = result[part]
            else:
                return None
        
        return result
    except Exception as e:
        logger.error(f"Error getting JSON path {path}: {e}")
        return None


def set_json_path(data, path, value):
    """
    Set a value in a JSON object using a path.
    
    Args:
        data: JSON data.
        path (str): Path to the value (e.g., "a.b.c").
        value: Value to set.
    
    Returns:
        bool: True if the value was set successfully, False otherwise.
    """
    try:
        parts = path.split('.')
        result = data
        
        for i, part in enumerate(parts[:-1]):
            if part not in result:
                result[part] = {}
            result = result[part]
        
        result[parts[-1]] = value
        return True
    except Exception as e:
        logger.error(f"Error setting JSON path {path}: {e}")
        return False


def flatten_json(data, separator='.'):
    """
    Flatten a nested JSON object.
    
    Args:
        data: JSON data.
        separator (str, optional): Separator for nested keys. Defaults to '.'.
    
    Returns:
        dict: Flattened JSON object.
    """
    result = {}
    
    def _flatten(x, name=''):
        if isinstance(x, dict):
            for a in x:
                _flatten(x[a], name + a + separator)
        elif isinstance(x, list):
            for i, a in enumerate(x):
                _flatten(a, name + str(i) + separator)
        else:
            result[name[:-1]] = x
    
    _flatten(data)
    return result


def unflatten_json(data, separator='.'):
    """
    Unflatten a flattened JSON object.
    
    Args:
        data: Flattened JSON data.
        separator (str, optional): Separator for nested keys. Defaults to '.'.
    
    Returns:
        dict: Nested JSON object.
    """
    result = {}
    
    for key, value in data.items():
        parts = key.split(separator)
        d = result
        
        for part in parts[:-1]:
            if part not in d:
                d[part] = {}
            d = d[part]
        
        d[parts[-1]] = value
    
    return result