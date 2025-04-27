"""
Utilities for LTX Sequence Maker

This package provides utility functions for working with colors, files, and other
common operations in the LTX Sequence Maker.
"""

from .color_utils import (
    resolve_color,
    rgb_to_hsv,
    hsv_to_rgb,
    adjust_brightness,
    adjust_saturation,
    adjust_hue,
    create_gradient,
    create_rainbow,
    blend_colors,
    get_complementary_color,
    get_analogous_colors,
    get_triadic_colors,
    get_color_name,
    NAMED_COLORS
)

from .file_utils import (
    ensure_directory_exists,
    save_json,
    load_json,
    list_files,
    list_json_files,
    copy_file,
    move_file,
    delete_file,
    get_file_size,
    get_file_modification_time,
    is_file_newer_than,
    find_files_by_extension,
    find_sequence_files,
    get_sequence_metadata,
    list_sequence_metadata,
    convert_sequence_format
)

__all__ = [
    # Color utilities
    'resolve_color',
    'rgb_to_hsv',
    'hsv_to_rgb',
    'adjust_brightness',
    'adjust_saturation',
    'adjust_hue',
    'create_gradient',
    'create_rainbow',
    'blend_colors',
    'get_complementary_color',
    'get_analogous_colors',
    'get_triadic_colors',
    'get_color_name',
    'NAMED_COLORS',
    
    # File utilities
    'ensure_directory_exists',
    'save_json',
    'load_json',
    'list_files',
    'list_json_files',
    'copy_file',
    'move_file',
    'delete_file',
    'get_file_size',
    'get_file_modification_time',
    'is_file_newer_than',
    'find_files_by_extension',
    'find_sequence_files',
    'get_sequence_metadata',
    'list_sequence_metadata',
    'convert_sequence_format'
]