"""
Tool Utilities for Roocode Sequence Designer

This package contains utility modules for the Roocode Sequence Designer tools.
"""

from .color_parser import parse_color, interpolate_color
from .cache_manager import CacheManager
from .audio_analyzer_core import AudioAnalyzer, LyricsProcessor
from .color_utils_core import (
    NAMED_COLORS,
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
    get_color_name
)
from .file_utils_core import (
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
    convert_sequence_format_segments_to_ltx # Renamed for clarity
)


__all__ = [
    # from color_parser
    'parse_color', 'interpolate_color',
    # from cache_manager
    'CacheManager',
    # from audio_analyzer_core
    'AudioAnalyzer', 'LyricsProcessor',
    # from color_utils_core
    'NAMED_COLORS', 'resolve_color', 'rgb_to_hsv', 'hsv_to_rgb',
    'adjust_brightness', 'adjust_saturation', 'adjust_hue',
    'create_gradient', 'create_rainbow', 'blend_colors',
    'get_complementary_color', 'get_analogous_colors', 'get_triadic_colors',
    'get_color_name',
    # from file_utils_core
    'ensure_directory_exists', 'save_json', 'load_json', 'list_files',
    'list_json_files', 'copy_file', 'move_file', 'delete_file',
    'get_file_size', 'get_file_modification_time', 'is_file_newer_than',
    'find_files_by_extension', 'find_sequence_files', 'get_sequence_metadata',
    'list_sequence_metadata', 'convert_sequence_format_segments_to_ltx'
]