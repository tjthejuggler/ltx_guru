#!/usr/bin/env python3
"""
Long Duration LTX Ball Sequence Generator

This script creates .prg files with much longer durations to test if that resolves
the rapid flashing issues observed in previous test batches.
"""

import json
import sys
import os
import struct

def generate_single_color_prg(pixel_count, rgb_color, output_file, duration_ds=1000):
    """
    Generate a .prg file for a single solid color with longer duration.
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - rgb_color: Tuple of (r, g, b) values (0-255)
    - output_file: Path to save the generated .prg file
    - duration_ds: Duration in deciseconds (default: 1000 = 100 seconds)
    """
    # Convert duration to bytes (little-endian)
    duration_bytes = duration_ds.to_bytes(2, byteorder='little')
    
    # --- 1. Fixed header (16 bytes) ---
    fixed_header = bytes.fromhex(f"50 52 03 49 4e 05 00 00 00 {pixel_count:02x} 00 08 01 00 50 49")
    
    # --- 2. Variable header (16 bytes) ---
    var_header = bytearray()
    var_header.extend((0x15).to_bytes(4, byteorder='little'))  # Length value: 21
    var_header.extend((0x1).to_bytes(2, byteorder='little'))   # Segment count: 1
    var_header.extend((0x1).to_bytes(2, byteorder='little'))   # Mode/flags: 1
    var_header.extend(duration_bytes)                          # Duration (100 seconds)
    var_header.extend((0x33).to_bytes(2, byteorder='little'))  # Offset: 51
    var_header.extend(bytes(4))                                # Padding
    
    # --- 3. Segment descriptor (20 bytes) ---
    segment = bytearray()
    segment.extend((pixel_count).to_bytes(2, byteorder='little'))  # Pixel count
    segment.extend((0x1).to_bytes(2, byteorder='little'))          # Unknown constant: 1
    segment.extend((0x0).to_bytes(2, byteorder='little'))          # Unknown zeros
    segment.extend(duration_bytes)                                 # Duration (100 seconds)
    segment.extend((0x0).to_bytes(2, byteorder='little'))          # Unknown zeros
    segment.extend(b"CD")                                          # Constant: "CD"
    segment.extend((0x30).to_bytes(2, byteorder='little'))         # Offset/pointer: 0x30
    segment.extend((0x1).to_bytes(2, byteorder='little'))          # Unknown constant: 1
    segment.extend((0x0).to_bytes(2, byteorder='little'))          # Unknown zeros
    segment.extend(duration_bytes)                                 # Duration (100 seconds)
    segment.extend((0x0).to_bytes(2, byteorder='little'))          # Padding
    
    # --- 4. Color data (300 bytes) ---
    r, g, b = rgb_color
    pixel_data = bytearray()
    pixel_data.extend(bytes([0, 0, 0]))  # Start with 3 zeros
    
    # Create repeating RGB pattern for this color
    rgb_pattern = bytes([r, g, b])
    
    # Fill to 300 bytes (minus the 3 starting zeros and 1 end byte)
    repeats = (300 - 4) // 3
    remainder = (300 - 4) % 3
    
    pixel_data.extend(rgb_pattern * repeats)
    pixel_data.extend(rgb_pattern[:remainder])
    
    # Replace last byte with 0x42
    pixel_data = pixel_data[:-1] + bytes([0x42])
    
    # --- 5. Footer (5 bytes) ---
    footer = bytes.fromhex("54 00 00 00 00")  # 'T' followed by 4 zeros
    
    # Combine all parts
    prg_data = fixed_header + var_header + segment + pixel_data + footer
    
    # Write the .prg file
    with open(output_file, 'wb') as f:
        f.write(prg_data)
    
    return len(prg_data)

def generate_two_color_prg(pixel_count, rgb_color1, rgb_color2, output_file, duration_ds=1000):
    """
    Generate a .prg file for a two-color sequence with longer durations.
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - rgb_color1: First color as (r, g, b) tuple
    - rgb_color2: Second color as (r, g, b) tuple
    - output_file: Path to save the generated .prg file
    - duration_ds: Duration in deciseconds (default: 1000 = 100 seconds)
    """
    # Convert duration to bytes (little-endian)
    duration_bytes = duration_ds.to_bytes(2, byteorder='little')
    segment_duration_bytes = duration_ds.to_bytes(2, byteorder='little')
    
    # --- 1. Fixed header (16 bytes) ---
    fixed_header = bytes.fromhex(f"50 52 03 49 4e 05 00 00 00 {pixel_count:02x} 00 08 01 00 50 49")
    
    # --- 2. Variable header (16 bytes) ---
    var_header = bytearray()
    var_header.extend((0x28).to_bytes(4, byteorder='little'))  # Length value: 40
    var_header.extend((0x2).to_bytes(2, byteorder='little'))   # Segment count: 2
    var_header.extend((0x0).to_bytes(2, byteorder='little'))   # Mode/flags: 0
    var_header.extend(duration_bytes)                          # Duration (100 seconds)
    var_header.extend((0x46).to_bytes(2, byteorder='little'))  # Offset: 70
    var_header.extend(bytes([0, 0, 0x0a, 0]))                  # Special pattern for two colors
    
    # --- 3. First segment descriptor (19 bytes) ---
    segment1 = bytearray()
    segment1.extend((0x04).to_bytes(2, byteorder='little'))        # Pixel count
    segment1.extend((0x1).to_bytes(2, byteorder='little'))         # Constant: 1
    segment1.extend((0x0).to_bytes(2, byteorder='little'))         # Zeros
    segment1.extend(segment_duration_bytes)                        # Duration for this segment
    segment1.extend((0x0).to_bytes(2, byteorder='little'))         # Zeros
    segment1.extend((0x0).to_bytes(2, byteorder='little'))         # Zeros
    segment1.extend(duration_bytes)                                # Overall duration
    segment1.extend((0x72).to_bytes(2, byteorder='little'))        # Offset: 0x172
    segment1.extend((0x01).to_bytes(2, byteorder='little'))        # Constant: 1
    segment1.extend((0x0).to_bytes(1, byteorder='little'))         # Padding
    
    # --- 4. Second segment descriptor (19 bytes) ---
    segment2 = bytearray()
    segment2.extend((0x0).to_bytes(1, byteorder='little'))         # First byte is 0
    segment2.extend((0x04).to_bytes(2, byteorder='little'))        # Pixel count
    segment2.extend((0x1).to_bytes(2, byteorder='little'))         # Constant: 1
    segment2.extend((0x0).to_bytes(2, byteorder='little'))         # Zeros
    segment2.extend(segment_duration_bytes)                        # Duration for this segment
    segment2.extend((0x0).to_bytes(2, byteorder='little'))         # Zeros
    segment2.extend(b"CD")                                          # Constant: "CD"
    segment2.extend((0x5c).to_bytes(2, byteorder='little'))        # Offset: 0x25c
    segment2.extend((0x02).to_bytes(2, byteorder='little'))        # Constant: 2
    segment2.extend((0x0).to_bytes(2, byteorder='little'))         # Padding
    segment2.extend((0xc8).to_bytes(2, byteorder='little'))        # Special value: 0xc8
    segment2.extend((0x0).to_bytes(2, byteorder='little'))         # Padding
    
    # --- 5. First color data (300 bytes) ---
    r1, g1, b1 = rgb_color1
    color_data1 = bytearray()
    color_data1.extend(bytes([0, 0, 0]))  # Start with 3 zeros
    
    # Create repeating RGB pattern for first color
    rgb_pattern1 = bytes([r1, g1, b1])
    
    # Fill to 300 bytes (minus the 3 starting zeros)
    repeats = (300 - 3) // 3
    remainder = (300 - 3) % 3
    
    color_data1.extend(rgb_pattern1 * repeats)
    color_data1.extend(rgb_pattern1[:remainder])
    
    # --- 6. Second color data (300 bytes) ---
    r2, g2, b2 = rgb_color2
    color_data2 = bytearray()
    color_data2.extend(bytes([0, 0, 0]))  # Start with 3 zeros
    
    # Create repeating RGB pattern for second color
    rgb_pattern2 = bytes([r2, g2, b2])
    
    # Fill to 300 bytes (minus the 3 starting zeros and 1 end byte)
    repeats = (300 - 4) // 3
    remainder = (300 - 4) % 3
    
    color_data2.extend(rgb_pattern2 * repeats)
    color_data2.extend(rgb_pattern2[:remainder])
    
    # Replace last byte with 0x42
    color_data2 = color_data2[:-1] + bytes([0x42])
    
    # --- 7. Footer (4 bytes) ---
    footer = bytes.fromhex("54 10 27 00 00")
    
    # Combine all parts
    prg_data = fixed_header + var_header + segment1 + segment2 + color_data1 + color_data2 + footer
    
    # Write the .prg file
    with open(output_file, 'wb') as f:
        f.write(prg_data)
    
    return len(prg_data)

def main():
    if len(sys.argv) < 3:
        print("Usage for single color: script.py single pixels r g b output.prg [duration_ds]")
        print("Usage for two colors: script.py dual pixels r1 g1 b1 r2 g2 b2 output.prg [duration_ds]")
        sys.exit(1)
    
    try:
        mode = sys.argv[1].lower()
        
        if mode == "single":
            if len(sys.argv) < 7:
                print("Usage for single color: script.py single pixels r g b output.prg [duration_ds]")
                sys.exit(1)
                
            pixels = int(sys.argv[2])
            r = int(sys.argv[3])
            g = int(sys.argv[4])
            b = int(sys.argv[5])
            output_file = sys.argv[6]
            
            # Optional duration parameter (in deciseconds)
            duration_ds = 1000  # Default: 100 seconds
            if len(sys.argv) >= 8:
                duration_ds = int(sys.argv[7])
            
            file_size = generate_single_color_prg(pixels, (r, g, b), output_file, duration_ds)
            print(f"Successfully created {output_file} ({file_size} bytes) with duration {duration_ds/10} seconds")
            
        elif mode == "dual":
            if len(sys.argv) < 10:
                print("Usage for two colors: script.py dual pixels r1 g1 b1 r2 g2 b2 output.prg [duration_ds]")
                sys.exit(1)
                
            pixels = int(sys.argv[2])
            r1 = int(sys.argv[3])
            g1 = int(sys.argv[4])
            b1 = int(sys.argv[5])
            r2 = int(sys.argv[6])
            g2 = int(sys.argv[7])
            b2 = int(sys.argv[8])
            output_file = sys.argv[9]
            
            # Optional duration parameter (in deciseconds)
            duration_ds = 1000  # Default: 100 seconds
            if len(sys.argv) >= 11:
                duration_ds = int(sys.argv[10])
            
            file_size = generate_two_color_prg(pixels, (r1, g1, b1), (r2, g2, b2), output_file, duration_ds)
            print(f"Successfully created {output_file} ({file_size} bytes) with duration {duration_ds/10} seconds")
            
        else:
            print("Invalid mode. Use 'single' or 'dual'.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()