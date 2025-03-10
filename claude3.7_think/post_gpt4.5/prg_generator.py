#!/usr/bin/env python3
"""
Corrected LTX Ball PRG Generator

Generates accurate PRG files for LTX balls from a JSON color sequence.
Usage:
    python3 prg_generator.py input.json output.prg
"""

import json
import struct
import sys

FILE_SIGNATURE = b'PR\x03IN\x05\x00\x00\x00'
CONSTANT_MARKER = b'PI'
FOOTER = b'BT\x00\x00\x00\x00'
RGB_TRIPLE_COUNT = 100

def get_duration_intro(i):
    """
    Generate the sequence for a given number of segments.
    
    For each segment count i, the sequence contains i pairs of hexadecimal values.
    The first value in each pair increases by 0x2C from the previous pair.
    The second value in each pair is the index (0, 1, 2, etc.).
    
    Examples:
    i=1: 3300
    i=2: 4600, 7201
    i=3: 5900, 8501, B102
    i=4: 6C00, 9801, C402, F003
    i=5: 7F00, AB01, D702, 0303, 2F04
    i=6: 9200, BE01, EA02, 1603, 4204, 6E05
    i=7: A500, D101, FD02, 2903, 5504, 8105, AD06
    """
    sequence = []
    first_value_step = 0x13  # Step between first values of consecutive rows
    within_row_step = 0x2C   # Step between values within the same row
    
    # Calculate the first value for this segment count
    first_value = 0x33 + ((i - 1) * first_value_step) if i > 0 else 0x33
    
    # Generate the sequence for this segment count
    value = first_value
    for index in range(i):
        # Return as a tuple of (first_byte, second_byte)
        sequence.append((value, index))
        # Increment value for the next pair
        value = (value + within_row_step) & 0xFF  # Keep within byte range (0-255)
    
    return sequence

def get_color_data_intro(i):
    """
    Gets a 10 byte number that goes directly before the color data starts.
    """
    # Calculate numerical values
    part1 = 304 + (i - 1) * 300
    part2 = 100 * i

    # Pack integers into 4-byte little-endian format
    part1_bytes = struct.pack('<I', part1)
    part2_bytes = struct.pack('<I', part2)
    
    return part1_bytes + part2_bytes

def generate_prg_file(input_json, output_prg):
    with open(input_json, 'r') as f:
        data = json.load(f)

    default_pixels = data.get('default_pixels', 1)
    refresh_rate = data.get('refresh_rate', 1)
    end_time = data.get('end_time')

    sequence = sorted([(int(t), v) for t, v in data['sequence'].items()], key=lambda x: x[0])

    segments = []
    for idx, (time, entry) in enumerate(sequence):
        color = entry['color']
        pixels = entry.get('pixels', default_pixels)
        next_time = sequence[idx + 1][0] if idx + 1 < len(sequence) else (end_time if end_time else time + 10)
        duration = next_time - time
        segments.append((duration, color, pixels))

    segment_count = len(segments)
    
    # Calculate the header value: 21 + 19 × (segment_count - 1)
    header_value = 21 + 19 * (segment_count - 1)

    with open(output_prg, 'wb') as f:
        # Header
        f.write(FILE_SIGNATURE)
        f.write(struct.pack('<B', default_pixels))  # pixel count (1 byte)
        f.write(b'\x00\x08')
        f.write(struct.pack('<B', refresh_rate))  # refresh rate (1 byte)
        f.write(b'\x00')  # padding
        f.write(CONSTANT_MARKER)
        
        # Write header value
        f.write(struct.pack('<B', header_value))
        f.write(b'\x00\x00\x00')
        
        # Write segment count
        f.write(struct.pack('<B', segment_count))
        f.write(b'\x00\x00\x00')
        
        # Duration segments
        duration_intro_values = get_duration_intro(segment_count)
        
        for idx, (duration, _, pixels) in enumerate(segments):
            # Single segment duration (17 bytes)
            f.write(b'\x64\x00')  # Constant
            first_byte, second_byte = duration_intro_values[idx]
            f.write(struct.pack('<BB', first_byte, second_byte))  # Values from get_duration_intro
            f.write(b'\x00\x00')  # Padding
            f.write(struct.pack('<H', duration))  # Duration of this segment
            f.write(struct.pack('<H', pixels))  # Number of pixels
            f.write(b'\x01\x00')  # Constant
            f.write(b'\x00')  # Padding
            f.write(struct.pack('<H', duration))  # Duration of this segment (repeated)
            #f.write(b'\x00')  # Padding
            f.write(b'\x00\x00')  # Padding
        
        # Color data intro
        if segment_count > 0:
            f.write(b'CD0')  # Constant marker before color data
            f.write(b'\x01\x00\x00')  # Padding
            f.write(struct.pack('<I', 100))  # Number of RGB triples (100)
            #f.write(b'\x00\x00\x00')  # Padding
        
        # RGB data
        for _, color, _ in segments:
            # For each RGB color, we need to write each component as a byte
            r, g, b = color
            # Just repeat the RGB triple for 100 times
            for _ in range(RGB_TRIPLE_COUNT):
                f.write(struct.pack('<BBB', r, g, b))
        
        # Footer
        f.write(FOOTER)

    print(f"Generated {output_prg}, {segment_count} segments")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} input.json output.prg")
        sys.exit(1)

    generate_prg_file(sys.argv[1], sys.argv[2])