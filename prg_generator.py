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
import pprint
import binascii

def bytes_to_hex(data):
    """Convert bytes to a formatted hex string with spaces between bytes"""
    if isinstance(data, int):
        return f"0x{data:02X}"
    elif isinstance(data, bytes):
        return ' '.join([f"{b:02X}" for b in data])
    return str(data)

FILE_SIGNATURE = b'PR\x03IN\x05\x00\x00\x00'
CONSTANT_MARKER = b'PI'
FOOTER = b'BT\x00\x00\x00\x00'
RGB_TRIPLE_COUNT = 100

def get_duration_intro(i):
    """
    Generate the sequence for a given number of segments.
    
    For each segment count i, the sequence contains i pairs of hexadecimal values.
    The first value in each pair increases by 0x2C from the previous pair.
    The second value follows a specific pattern for indices.
    
    Examples:
    i=1: 3300
    i=2: 4600, 7201
    i=3: 5900, 8501, B102
    i=4: 6C00, 9801, C402, F003
    i=5: 7F00, AB01, D702, 0304, 2F05
    i=6: 9200, BE01, EA02, 1604, 4205, 6E06
    i=7: A500, D101, FD02, 2904, 5505, 8106, AD07
    """
    print("\n[DURATION_INTRO] Generating sequence for", i, "segments")
    sequence = []
    first_value_step = 0x13  # Step between first values of consecutive rows
    within_row_step = 0x2C   # Step between values within the same row
    
    # Calculate the first value for this segment count
    first_value = 0x33 + ((i - 1) * first_value_step) if i > 0 else 0x33
    print(f"[DURATION_INTRO] First value calculation: 0x33 + (({i} - 1) * 0x13) = 0x{first_value:02X}")
    
    # Generate the sequence for this segment count
    value = first_value
    for index in range(i):
        # Determine the second byte (index value) based on the pattern
        if index < 3:
            second_byte = index
        else:
            second_byte = index + 1
            
        # Return as a tuple of (first_byte, second_byte)
        sequence.append((value, second_byte))
        print(f"[DURATION_INTRO] Added pair: (0x{value:02X}, {second_byte}) -> {value:02X}{second_byte:02X}")
        # Increment value for the next pair
        value = (value + within_row_step) & 0xFF  # Keep within byte range (0-255)
        if index < i - 1:  # Only print next value if not the last iteration
            print(f"[DURATION_INTRO] Next value: 0x{value:02X}")
    
    print(f"[DURATION_INTRO] Final sequence: {[(hex(v), idx) for v, idx in sequence]}")
    return sequence

def get_color_data_intro(i):
    """
    Gets a 10 byte number that goes directly before the color data starts.
    """
    print(f"\n[COLOR_DATA_INTRO] Calculating color data intro for {i} segments")
    
    # Calculate numerical values
    part1 = 304 + (i - 1) * 300
    print(f"[COLOR_DATA_INTRO] part1 = 304 + ({i} - 1) * 300 = {part1}")
    
    part2 = 100 * i
    print(f"[COLOR_DATA_INTRO] part2 = 100 * {i} = {part2}")

    # Pack integers into 4-byte little-endian format
    part1_bytes = struct.pack('<I', part1)
    part2_bytes = struct.pack('<I', part2)
    
    # Format hex values for logging
    part1_hex = part1_bytes.hex().upper()
    part2_hex = part2_bytes.hex().upper()
    part1_formatted = ' '.join(part1_hex[j:j+2] for j in range(0, 8, 2))
    part2_formatted = ' '.join(part2_hex[j:j+2] for j in range(0, 8, 2))
    
    print(f"[COLOR_DATA_INTRO] {i} = {part1_formatted} {part2_formatted}")
    
    result = part1_bytes + part2_bytes
    print(f"[COLOR_DATA_INTRO] Packed bytes: {result.hex()}")
    
    return result

def generate_prg_file(input_json, output_prg):
    print(f"\n[GENERATE_PRG] Starting PRG generation from {input_json} to {output_prg}")
    
    with open(input_json, 'r') as f:
        data = json.load(f)
    
    print("[GENERATE_PRG] Loaded JSON data:")
    print(f"[GENERATE_PRG] {pprint.pformat(data, indent=2)}")

    default_pixels = data.get('default_pixels', 1)
    refresh_rate = data.get('refresh_rate', 1)
    end_time = data.get('end_time')
    
    print(f"[GENERATE_PRG] Configuration parameters:")
    print(f"[GENERATE_PRG] - Default pixels: {default_pixels}")
    print(f"[GENERATE_PRG] - Refresh rate: {refresh_rate}")
    print(f"[GENERATE_PRG] - End time: {end_time}")

    sequence = sorted([(int(t), v) for t, v in data['sequence'].items()], key=lambda x: x[0])
    print(f"[GENERATE_PRG] Sorted sequence timestamps: {[t for t, _ in sequence]}")

    print("\n[GENERATE_PRG] Processing sequence segments:")
    segments = []
    for idx, (time, entry) in enumerate(sequence):
        color = entry['color']
        pixels = entry.get('pixels', default_pixels)
        next_time = sequence[idx + 1][0] if idx + 1 < len(sequence) else (end_time if end_time else time + 10)
        duration = next_time - time
        
        r, g, b = color
        rgb_bytes = struct.pack('<BBB', r, g, b)
        
        print(f"[GENERATE_PRG] Segment {idx}:")
        print(f"[GENERATE_PRG] - Time: {time} (hex: 0x{time:04X})")
        print(f"[GENERATE_PRG] - Color: RGB{color} (hex: {bytes_to_hex(rgb_bytes)})")
        print(f"[GENERATE_PRG] - Pixels: {pixels} (hex: 0x{pixels:02X})")
        print(f"[GENERATE_PRG] - Next time: {next_time} (hex: 0x{next_time:04X})")
        print(f"[GENERATE_PRG] - Duration: {duration} (hex: 0x{duration:04X})")
        
        segments.append((duration, color, pixels))

    segment_count = len(segments)
    print(f"\n[GENERATE_PRG] Total segments: {segment_count}")
    print(f"[GENERATE_PRG] Segments summary:")
    for i, (duration, color, pixels) in enumerate(segments):
        r, g, b = color
        rgb_bytes = struct.pack('<BBB', r, g, b)
        print(f"[GENERATE_PRG] - Segment {i}: Duration={duration} (0x{duration:04X}), Color=RGB{color} (hex: {bytes_to_hex(rgb_bytes)}), Pixels={pixels} (0x{pixels:04X})")
    
    # Calculate the header value: 21 + 19 × (segment_count - 1)
    header_value = 21 + 19 * (segment_count - 1)
    print(f"\n[GENERATE_PRG] Header value calculation: 21 + 19 × ({segment_count} - 1) = {header_value}")

    print("\n[GENERATE_PRG] Starting to write PRG file")
    with open(output_prg, 'wb') as f:
        # Collect all header bytes in a bytearray
        header_bytes = bytearray()
        
        # Header
        print(f"[GENERATE_PRG] Writing file signature: {bytes_to_hex(FILE_SIGNATURE)} ('{FILE_SIGNATURE.decode('latin-1')}')")
        f.write(FILE_SIGNATURE)
        header_bytes.extend(FILE_SIGNATURE)
        
        default_pixels_bytes = struct.pack('<B', default_pixels)
        print(f"[GENERATE_PRG] Writing default pixels: {default_pixels} (hex: {bytes_to_hex(default_pixels_bytes)})")
        f.write(default_pixels_bytes)  # pixel count (1 byte)
        header_bytes.extend(default_pixels_bytes)
        
        constant_bytes = b'\x00\x08'
        print(f"[GENERATE_PRG] Writing constant: {bytes_to_hex(constant_bytes)}")
        f.write(constant_bytes)
        header_bytes.extend(constant_bytes)
        
        refresh_rate_bytes = struct.pack('<B', refresh_rate)
        print(f"[GENERATE_PRG] Writing refresh rate: {refresh_rate} (hex: {bytes_to_hex(refresh_rate_bytes)})")
        f.write(refresh_rate_bytes)  # refresh rate (1 byte)
        header_bytes.extend(refresh_rate_bytes)
        
        padding_bytes = b'\x00'
        print(f"[GENERATE_PRG] Writing padding: {bytes_to_hex(padding_bytes)}")
        f.write(padding_bytes)  # padding
        header_bytes.extend(padding_bytes)
        
        print(f"[GENERATE_PRG] Writing constant marker: {bytes_to_hex(CONSTANT_MARKER)} ('{CONSTANT_MARKER.decode('latin-1')}')")
        f.write(CONSTANT_MARKER)
        header_bytes.extend(CONSTANT_MARKER)
        
        # Write header value
        header_value_bytes = struct.pack('<B', header_value)
        print(f"[GENERATE_PRG] Writing header value: {header_value} (hex: {bytes_to_hex(header_value_bytes)})")
        f.write(header_value_bytes)
        header_bytes.extend(header_value_bytes)
        
        header_padding = b'\x00\x00\x00'
        print(f"[GENERATE_PRG] Writing header padding: {bytes_to_hex(header_padding)}")
        f.write(header_padding)
        header_bytes.extend(header_padding)
        
        # Write segment count
        segment_count_bytes = struct.pack('<B', segment_count)
        print(f"[GENERATE_PRG] Writing segment count: {segment_count} (hex: {bytes_to_hex(segment_count_bytes)})")
        f.write(segment_count_bytes)
        header_bytes.extend(segment_count_bytes)
        
        segment_padding = b'\x00'
        print(f"[GENERATE_PRG] Writing segment padding: {bytes_to_hex(segment_padding)}")
        f.write(segment_padding)
        header_bytes.extend(segment_padding)
        
        # Print the complete header as a single hex string
        print(f"[GENERATE_PRG] - COMPLETE HEADER HEX: {bytes_to_hex(header_bytes)}")
        
        # Duration segments
        print("\n[GENERATE_PRG] Getting duration intro values")
        duration_intro_values = get_duration_intro(segment_count)
        
        print("\n[GENERATE_PRG] Writing duration segments")
        for idx, (duration, _, pixels) in enumerate(segments):
            print(f"\n[GENERATE_PRG] Writing segment {idx} duration data:")
            
            # Collect all bytes for this segment in a bytearray
            segment_bytes = bytearray()
            
            # Add 00 00 bytes before the first segment only
            #if idx == 0:
            initial_padding = b'\x00\x00'
            print(f"[GENERATE_PRG] - Writing initial padding before first segment: {bytes_to_hex(initial_padding)}")
            f.write(initial_padding)
            segment_bytes.extend(initial_padding)
            
            # Single segment duration (17 bytes)
            constant_bytes = b'\x64\x00'
            print(f"[GENERATE_PRG] - Writing constant: {bytes_to_hex(constant_bytes)}")
            f.write(constant_bytes)
            segment_bytes.extend(constant_bytes)
            
            first_byte, second_byte = duration_intro_values[idx]
            intro_bytes = struct.pack('<BB', first_byte, second_byte)
            print(f"[GENERATE_PRG] - Writing duration intro values: 0x{first_byte:02X}, 0x{second_byte:02X} (hex: {bytes_to_hex(intro_bytes)})")
            f.write(intro_bytes)
            segment_bytes.extend(intro_bytes)
            
            padding_bytes = b'\x00\x00'
            print(f"[GENERATE_PRG] - Writing padding: {bytes_to_hex(padding_bytes)}")
            f.write(padding_bytes)
            segment_bytes.extend(padding_bytes)
            
            duration_bytes = struct.pack('<H', duration)
            print(f"[GENERATE_PRG] - Writing duration: {duration} (hex: {bytes_to_hex(duration_bytes)})")
            f.write(duration_bytes)
            segment_bytes.extend(duration_bytes)
            
            pixels_bytes = struct.pack('<H', pixels)
            print(f"[GENERATE_PRG] - Writing pixels: {pixels} (hex: {bytes_to_hex(pixels_bytes)})")
            f.write(pixels_bytes)
            segment_bytes.extend(pixels_bytes)
            
            constant2_bytes = b'\x01\x00'
            print(f"[GENERATE_PRG] - Writing constant: {bytes_to_hex(constant2_bytes)}")
            f.write(constant2_bytes)
            segment_bytes.extend(constant2_bytes)
            
            padding2_bytes = b'\x00'
            print(f"[GENERATE_PRG] - Writing padding: {bytes_to_hex(padding2_bytes)}")
            f.write(padding2_bytes)
            segment_bytes.extend(padding2_bytes)
            
            duration2_bytes = struct.pack('<H', duration)
            print(f"[GENERATE_PRG] - Writing duration again: {duration} (hex: {bytes_to_hex(duration2_bytes)})")
            f.write(duration2_bytes)
            segment_bytes.extend(duration2_bytes)
            
            final_padding_bytes = b'\x00\x00'
            print(f"[GENERATE_PRG] - Writing final padding: {bytes_to_hex(final_padding_bytes)}")
            f.write(final_padding_bytes)
            segment_bytes.extend(final_padding_bytes)
            
            # Print the complete segment duration data as a single hex string
            print(f"[GENERATE_PRG] - COMPLETE SEGMENT {idx} HEX: {bytes_to_hex(segment_bytes)}")
        
        # Color data intro
        if segment_count > 0:
            print("\n[GENERATE_PRG] Writing color data intro")
            
            # Write the CD marker first
            cd_marker = b'CD'
            print(f"[GENERATE_PRG] - Writing CD marker: {bytes_to_hex(cd_marker)} ('{cd_marker.decode('latin-1')}')")
            f.write(cd_marker)
            
            # Get the color data intro
            color_data_intro = get_color_data_intro(segment_count)
            print(f"[GENERATE_PRG] - Writing color data intro: {bytes_to_hex(color_data_intro)}")
            
            # Write the color data intro bytes
            f.write(color_data_intro)
            
            # Print the complete color data intro as a single hex string
            complete_intro = cd_marker + color_data_intro
            print(f"[GENERATE_PRG] - COMPLETE COLOR DATA INTRO HEX: {bytes_to_hex(complete_intro)}")
        
        # RGB data
        print("\n[GENERATE_PRG] Writing RGB color data")
        for idx, (_, color, _) in enumerate(segments):
            # For each RGB color, we need to write each component as a byte
            r, g, b = color
            rgb_bytes = struct.pack('<BBB', r, g, b)
            print(f"[GENERATE_PRG] - Writing segment {idx} color: RGB({r}, {g}, {b}) (hex: {bytes_to_hex(rgb_bytes)}) x {RGB_TRIPLE_COUNT} times")
            
            # Collect all RGB bytes for this segment in a bytearray
            all_rgb_bytes = bytearray()
            
            # Just repeat the RGB triple for 100 times
            for i in range(RGB_TRIPLE_COUNT):
                if i == 0:
                    print(f"[GENERATE_PRG]   - Writing first RGB triple: {bytes_to_hex(rgb_bytes)}")
                elif i == RGB_TRIPLE_COUNT - 1:
                    print(f"[GENERATE_PRG]   - Writing last RGB triple: {bytes_to_hex(rgb_bytes)}")
                f.write(rgb_bytes)
                all_rgb_bytes.extend(rgb_bytes)
            
            # Print the first few and last few RGB triples to avoid excessive output
            print(f"[GENERATE_PRG] - COMPLETE RGB DATA FOR SEGMENT {idx} (showing first 3 and last 3 triples):")
            first_bytes = bytes(all_rgb_bytes[:9])  # First 3 RGB triples
            last_bytes = bytes(all_rgb_bytes[-9:])  # Last 3 RGB triples
            print(f"[GENERATE_PRG]   First: {bytes_to_hex(first_bytes)} ... Last: {bytes_to_hex(last_bytes)}")
            print(f"[GENERATE_PRG]   Total size: {len(all_rgb_bytes)} bytes (hex: 0x{len(all_rgb_bytes):04X})")
        
        # Footer
        print(f"\n[GENERATE_PRG] Writing footer: {bytes_to_hex(FOOTER)} ('{FOOTER.decode('latin-1')}')")
        f.write(FOOTER)

    print(f"\n[GENERATE_PRG] Successfully generated {output_prg}")
    print(f"[GENERATE_PRG] Summary:")
    print(f"[GENERATE_PRG] - Total segments: {segment_count} (hex: 0x{segment_count:02X})")
    print(f"[GENERATE_PRG] - Default pixels: {default_pixels} (hex: 0x{default_pixels:02X})")
    print(f"[GENERATE_PRG] - Refresh rate: {refresh_rate} (hex: 0x{refresh_rate:02X})")
    print(f"[GENERATE_PRG] - Header value: {header_value} (hex: 0x{header_value:02X})")
    print(f"[GENERATE_PRG] - RGB triple count: {RGB_TRIPLE_COUNT} (hex: 0x{RGB_TRIPLE_COUNT:02X})")
    
    # Print file size information
    import os
    file_size = os.path.getsize(output_prg)
    print(f"[GENERATE_PRG] - File size: {file_size} bytes (hex: 0x{file_size:04X})")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} input.json output.prg")
        sys.exit(1)

    generate_prg_file(sys.argv[1], sys.argv[2])