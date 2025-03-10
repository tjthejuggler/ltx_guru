#!/usr/bin/env python3
"""
Direct Copy Test Generator

This script creates a .prg file by directly copying the structure of a known working example
(2px_red_5_green_10_blue_15.prg) but with different colors and pixel count.
"""

import sys
import os

def generate_direct_copy(pixel_count, colors, durations, output_file):
    """
    Generate a .prg file by directly copying the structure of a known working example.
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - colors: List of 3 (r, g, b) tuples for each color in the sequence
    - durations: List of 3 durations in deciseconds for each color
    - output_file: Path to save the generated .prg file
    """
    if len(colors) != 3 or len(durations) != 3:
        raise ValueError("This function requires exactly 3 colors and 3 durations")
    
    # Convert pixel count to bytes
    pixel_bytes = pixel_count.to_bytes(2, byteorder='little')
    
    # Convert durations to bytes
    dur1_bytes = durations[0].to_bytes(2, byteorder='little')
    dur2_bytes = durations[1].to_bytes(2, byteorder='little')
    dur3_bytes = durations[2].to_bytes(2, byteorder='little')
    
    # Calculate total duration
    total_duration = sum(durations)
    total_bytes = total_duration.to_bytes(2, byteorder='little')
    
    # Create the header and segment descriptors (exact copy from working example)
    # Just replace the pixel count and durations
    header = bytearray()
    
    # Fixed header
    header.extend(bytearray.fromhex("50 52 03 49 4e 05 00 00 00"))
    header.extend(bytes([pixel_count, 0]))  # Pixel count in little-endian
    header.extend(bytearray.fromhex("08 01 00 50 49"))
    
    # Variable header
    header.extend(bytearray.fromhex("3b 00 00 00 03 00 00 00"))
    header.extend(total_bytes)  # Total duration in little-endian
    header.extend(bytearray.fromhex("59 00 00 00"))
    header.extend(dur1_bytes)  # Duration 1 in little-endian
    
    # First segment
    header.extend(bytes([pixel_count, 0]))  # Pixel count in little-endian
    header.extend(bytearray.fromhex("01 00 00"))
    header.extend(dur1_bytes)  # Duration 1 in little-endian
    header.extend(bytearray.fromhex("00 00 00 00"))
    header.extend(total_bytes)  # Total duration in little-endian
    header.extend(bytearray.fromhex("85 01 00 00"))
    
    # Second segment
    header.extend(dur2_bytes)  # Duration 2 in little-endian
    header.extend(bytes([pixel_count, 0]))  # Pixel count in little-endian
    header.extend(bytearray.fromhex("01 00 00"))
    header.extend(dur2_bytes)  # Duration 2 in little-endian
    header.extend(bytearray.fromhex("00 00 00 00"))
    header.extend(total_bytes)  # Total duration in little-endian
    header.extend(bytearray.fromhex("b1 02 00 00"))
    
    # Third segment
    header.extend(dur3_bytes)  # Duration 3 in little-endian
    header.extend(bytes([pixel_count, 0]))  # Pixel count in little-endian
    header.extend(bytearray.fromhex("01 00 00"))
    header.extend(dur3_bytes)  # Duration 3 in little-endian
    header.extend(bytearray.fromhex("00 00 00 43"))
    
    # Create the color data blocks
    color_data = bytearray()
    
    # First color block (red in the original)
    color_block1 = bytearray([0, 0, 0])  # Start with 3 zeros
    r1, g1, b1 = colors[0]
    rgb_pattern1 = bytes([r1, g1, b1])
    for _ in range(99):
        color_block1.extend(rgb_pattern1)
    color_data.extend(color_block1)
    
    # Second color block (green in the original)
    color_block2 = bytearray([0, 0, 0])  # Start with 3 zeros
    r2, g2, b2 = colors[1]
    rgb_pattern2 = bytes([r2, g2, b2])
    for _ in range(99):
        color_block2.extend(rgb_pattern2)
    color_data.extend(color_block2)
    
    # Third color block (blue in the original)
    color_block3 = bytearray([0, 0, 0])  # Start with 3 zeros
    r3, g3, b3 = colors[2]
    rgb_pattern3 = bytes([r3, g3, b3])
    for _ in range(99):
        color_block3.extend(rgb_pattern3)
    
    # Replace the last byte with 0x42
    color_block3 = color_block3[:-1] + bytes([0x42])
    color_data.extend(color_block3)
    
    # Add the footer
    footer = bytes.fromhex("54 00 00 00 00")
    
    # Combine all parts
    prg_data = header + color_data + footer
    
    # Write the .prg file
    with open(output_file, 'wb') as f:
        f.write(prg_data)
    
    return len(prg_data)

def main():
    if len(sys.argv) < 13:
        print("Usage: script.py pixels r1 g1 b1 dur1 r2 g2 b2 dur2 r3 g3 b3 dur3 output.prg")
        sys.exit(1)
    
    try:
        pixel_count = int(sys.argv[1])
        
        r1 = int(sys.argv[2])
        g1 = int(sys.argv[3])
        b1 = int(sys.argv[4])
        dur1 = int(sys.argv[5])
        
        r2 = int(sys.argv[6])
        g2 = int(sys.argv[7])
        b2 = int(sys.argv[8])
        dur2 = int(sys.argv[9])
        
        r3 = int(sys.argv[10])
        g3 = int(sys.argv[11])
        b3 = int(sys.argv[12])
        dur3 = int(sys.argv[13])
        
        output_file = sys.argv[14]
        
        colors = [(r1, g1, b1), (r2, g2, b2), (r3, g3, b3)]
        durations = [dur1, dur2, dur3]
        
        file_size = generate_direct_copy(pixel_count, colors, durations, output_file)
        print(f"Successfully created {output_file} ({file_size} bytes)")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()