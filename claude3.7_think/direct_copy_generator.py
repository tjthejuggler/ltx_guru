#!/usr/bin/env python3
"""
Direct Copy LTX Ball Sequence Generator

This script creates .prg files by directly copying the binary structure of known working examples,
with minimal modifications to the color values.
"""

import sys
import os

def generate_single_color_prg(pixel_count, rgb_color, output_file):
    """
    Generate a .prg file for a single solid color by directly copying a known working example.
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - rgb_color: Tuple of (r, g, b) values (0-255)
    - output_file: Path to save the generated .prg file
    """
    # Known working example for red (4px_10_red.prg)
    # This is a direct copy of the hex values with only the color data modified
    r, g, b = rgb_color
    
    # Fixed header and structure (exact copy from working example)
    data = bytearray.fromhex(
        "50 52 03 49 4e 05 00 00 00 04 00 08 01 00 50 49" +  # Fixed header
        "15 00 00 00 01 00 01 00 64 00 33 00 00 00 00 00" +  # Variable header
        "04 00 01 00 00 64 00 00 00 43 44 30 01 00 00 64" +  # Segment descriptor
        "00 00 00"                                           # Start of color data
    )
    
    # Add color data (replace FF 00 00 with the specified RGB values)
    rgb_pattern = bytes([r, g, b])
    
    # Fill with repeating RGB pattern (99 times)
    for _ in range(99):
        data.extend(rgb_pattern)
    
    # Add final byte 0x42 and footer
    data.extend(bytes([0x42, 0x54, 0x00, 0x00, 0x00, 0x00]))
    
    # Write the .prg file
    with open(output_file, 'wb') as f:
        f.write(data)
    
    return len(data)

def generate_two_color_prg(pixel_count, rgb_color1, rgb_color2, output_file):
    """
    Generate a .prg file for a two-color sequence by directly copying a known working example.
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - rgb_color1: First color as (r, g, b) tuple
    - rgb_color2: Second color as (r, g, b) tuple
    - output_file: Path to save the generated .prg file
    """
    # Known working example for red-to-green (4px_red_10_green_10.prg)
    # This is a direct copy of the hex values with only the color data modified
    r1, g1, b1 = rgb_color1
    r2, g2, b2 = rgb_color2
    
    # Fixed header and structure (exact copy from working example)
    data = bytearray.fromhex(
        "50 52 03 49 4e 05 00 00 00 04 00 08 01 00 50 49" +  # Fixed header
        "28 00 00 00 02 00 00 00 64 00 46 00 00 00 0a 00" +  # Variable header
        "04 00 01 00 00 0a 00 00 00 00 00 64 00 72 01 00" +  # First segment descriptor
        "00 0a 00 04 00 01 00 00 0a 00 00 00 43 44 5c 02" +  # Second segment descriptor
        "00 00 c8 00 00 00"                                  # Start of first color data
    )
    
    # Add first color data
    rgb_pattern1 = bytes([r1, g1, b1])
    
    # Fill with repeating RGB pattern (99 times)
    for _ in range(99):
        data.extend(rgb_pattern1)
    
    # Add second color data
    rgb_pattern2 = bytes([r2, g2, b2])
    
    # Fill with repeating RGB pattern (98 times)
    for _ in range(98):
        data.extend(rgb_pattern2)
    
    # Add final byte 0x42 and footer
    data.extend(bytes([0x42, 0x54, 0x10, 0x27, 0x00, 0x00]))
    
    # Write the .prg file
    with open(output_file, 'wb') as f:
        f.write(data)
    
    return len(data)

def main():
    if len(sys.argv) < 3:
        print("Usage for single color: script.py single pixels r g b output.prg")
        print("Usage for two colors: script.py dual pixels r1 g1 b1 r2 g2 b2 output.prg")
        sys.exit(1)
    
    try:
        mode = sys.argv[1].lower()
        
        if mode == "single":
            if len(sys.argv) < 7:
                print("Usage for single color: script.py single pixels r g b output.prg")
                sys.exit(1)
                
            pixels = int(sys.argv[2])
            r = int(sys.argv[3])
            g = int(sys.argv[4])
            b = int(sys.argv[5])
            output_file = sys.argv[6]
            
            file_size = generate_single_color_prg(pixels, (r, g, b), output_file)
            print(f"Successfully created {output_file} ({file_size} bytes)")
            
        elif mode == "dual":
            if len(sys.argv) < 10:
                print("Usage for two colors: script.py dual pixels r1 g1 b1 r2 g2 b2 output.prg")
                sys.exit(1)
                
            pixels = int(sys.argv[2])
            r1 = int(sys.argv[3])
            g1 = int(sys.argv[4])
            b1 = int(sys.argv[5])
            r2 = int(sys.argv[6])
            g2 = int(sys.argv[7])
            b2 = int(sys.argv[8])
            output_file = sys.argv[9]
            
            file_size = generate_two_color_prg(pixels, (r1, g1, b1), (r2, g2, b2), output_file)
            print(f"Successfully created {output_file} ({file_size} bytes)")
            
        else:
            print("Invalid mode. Use 'single' or 'dual'.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()