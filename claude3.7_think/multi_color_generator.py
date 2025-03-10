#!/usr/bin/env python3
"""
Multi-Color LTX Ball Sequence Generator

This script creates .prg files for complex color sequences by extending the direct copy approach
that was proven to work correctly in our tests.
"""

import sys
import os

def generate_multi_color_prg(pixel_count, colors, durations, output_file):
    """
    Generate a .prg file for a multi-color sequence.
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - colors: List of (r, g, b) tuples for each color in the sequence
    - durations: List of durations in deciseconds for each color (100 = 10 seconds)
    - output_file: Path to save the generated .prg file
    """
    if len(colors) != len(durations):
        raise ValueError("Number of colors must match number of durations")
    
    if len(colors) < 1:
        raise ValueError("At least one color must be provided")
    
    # For single color, use the simple format
    if len(colors) == 1:
        return generate_single_color_prg(pixel_count, colors[0], output_file)
    
    # For multi-color sequences, we'll build on the two-color format
    # and extend it for more colors
    
    # --- 1. Fixed header (16 bytes) ---
    fixed_header = bytearray.fromhex(f"50 52 03 49 4e 05 00 00 00 {pixel_count:02x} 00 08 01 00 50 49")
    
    # --- 2. Variable header (16 bytes) ---
    segment_count = len(colors)
    var_header = bytearray()
    var_header.extend((0x28).to_bytes(4, byteorder='little'))  # Length value (will adjust later)
    var_header.extend(segment_count.to_bytes(2, byteorder='little'))  # Segment count
    var_header.extend((0x0).to_bytes(2, byteorder='little'))   # Mode/flags: 0
    
    # Total duration (sum of all durations)
    total_duration = sum(durations)
    var_header.extend(total_duration.to_bytes(2, byteorder='little'))  # Total duration
    
    var_header.extend((0x46).to_bytes(2, byteorder='little'))  # Offset: 70 (will adjust later)
    var_header.extend(bytes([0, 0, 0x0a, 0]))                  # Special pattern
    
    # --- 3. Segment descriptors ---
    segments = bytearray()
    
    # First segment
    segments.extend((pixel_count).to_bytes(2, byteorder='little'))  # Pixel count
    segments.extend((0x1).to_bytes(2, byteorder='little'))          # Constant: 1
    segments.extend((0x0).to_bytes(2, byteorder='little'))          # Zeros
    segments.extend(durations[0].to_bytes(2, byteorder='little'))   # Duration for first segment
    segments.extend((0x0).to_bytes(2, byteorder='little'))          # Zeros
    segments.extend((0x0).to_bytes(2, byteorder='little'))          # Zeros
    segments.extend(total_duration.to_bytes(2, byteorder='little')) # Total duration
    segments.extend((0x72).to_bytes(2, byteorder='little'))         # Offset: 0x172 (will adjust)
    segments.extend((0x01).to_bytes(2, byteorder='little'))         # Constant: 1
    segments.extend((0x0).to_bytes(1, byteorder='little'))          # Padding
    
    # Middle segments (if any)
    offset_base = 0x172  # Starting offset for color data
    for i in range(1, len(colors) - 1):
        segments.extend((0x0).to_bytes(1, byteorder='little'))         # First byte is 0
        segments.extend((pixel_count).to_bytes(2, byteorder='little')) # Pixel count
        segments.extend((0x1).to_bytes(2, byteorder='little'))         # Constant: 1
        segments.extend((0x0).to_bytes(2, byteorder='little'))         # Zeros
        segments.extend(durations[i].to_bytes(2, byteorder='little'))  # Duration for this segment
        segments.extend((0x0).to_bytes(2, byteorder='little'))         # Zeros
        segments.extend((0x0).to_bytes(2, byteorder='little'))         # Zeros
        segments.extend(durations[i].to_bytes(2, byteorder='little'))  # Duration again
        
        # Calculate offset for this segment's color data
        next_offset = offset_base + ((i - 1) * 0x022C)
        segments.extend(next_offset.to_bytes(2, byteorder='little'))   # Offset
        segments.extend((0x0).to_bytes(4, byteorder='little'))         # Padding
    
    # Last segment
    if len(colors) > 1:
        last_idx = len(colors) - 1
        segments.extend((0x0).to_bytes(1, byteorder='little'))             # First byte is 0
        segments.extend((pixel_count).to_bytes(2, byteorder='little'))     # Pixel count
        segments.extend((0x1).to_bytes(2, byteorder='little'))             # Constant: 1
        segments.extend((0x0).to_bytes(2, byteorder='little'))             # Zeros
        segments.extend(durations[last_idx].to_bytes(2, byteorder='little')) # Duration for last segment
        segments.extend((0x0).to_bytes(2, byteorder='little'))             # Zeros
        segments.extend(b"CD")                                              # Constant: "CD"
        
        # Calculate offset for last segment's color data
        last_offset = offset_base + ((last_idx - 1) * 0x022C)
        segments.extend(last_offset.to_bytes(2, byteorder='little'))       # Offset
        
        # Size of color data
        color_data_size = 300  # Approximate color data size per segment
        segments.extend(color_data_size.to_bytes(2, byteorder='little'))   # Size
        segments.extend((0x0).to_bytes(2, byteorder='little'))             # Padding
    
    # --- 4. Color data blocks ---
    color_data = bytearray()
    
    # For each color, create a color block
    for i, (r, g, b) in enumerate(colors):
        # Start with 3 zeros
        color_block = bytearray([0, 0, 0])
        
        # Create repeating RGB pattern
        rgb_pattern = bytes([r, g, b])
        
        # Fill to 300 bytes (minus the 3 starting zeros)
        repeats = (300 - 3) // 3
        remainder = (300 - 3) % 3
        
        color_block.extend(rgb_pattern * repeats)
        color_block.extend(rgb_pattern[:remainder])
        
        # For the last color block, replace the last byte with 0x42
        if i == len(colors) - 1:
            color_block = color_block[:-1] + bytes([0x42])
            
        color_data.extend(color_block)
    
    # --- 5. Footer ---
    if len(colors) == 2:
        footer = bytes.fromhex("54 10 27 00 00")
    else:
        # For more colors, adjust footer
        footer = bytes.fromhex("54 00 00 00 00")
    
    # Combine all parts
    prg_data = fixed_header + var_header + segments + color_data + footer
    
    # Write the .prg file
    with open(output_file, 'wb') as f:
        f.write(prg_data)
    
    return len(prg_data)

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

def generate_rgb_cycle(pixel_count, duration_ds, output_file):
    """
    Generate a .prg file for an RGB cycle (red → green → blue → red).
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - duration_ds: Duration in deciseconds for each color (100 = 10 seconds)
    - output_file: Path to save the generated .prg file
    """
    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 0, 0)     # Back to Red
    ]
    durations = [duration_ds] * len(colors)
    
    return generate_multi_color_prg(pixel_count, colors, durations, output_file)

def generate_rainbow(pixel_count, duration_ds, output_file):
    """
    Generate a .prg file for a rainbow cycle.
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - duration_ds: Duration in deciseconds for each color (100 = 10 seconds)
    - output_file: Path to save the generated .prg file
    """
    colors = [
        (255, 0, 0),      # Red
        (255, 127, 0),    # Orange
        (255, 255, 0),    # Yellow
        (0, 255, 0),      # Green
        (0, 0, 255),      # Blue
        (75, 0, 130),     # Indigo
        (148, 0, 211),    # Violet
        (255, 0, 0)       # Back to Red
    ]
    durations = [duration_ds] * len(colors)
    
    return generate_multi_color_prg(pixel_count, colors, durations, output_file)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  For single color: script.py single pixels r g b output.prg")
        print("  For RGB cycle: script.py rgb_cycle pixels duration_ds output.prg")
        print("  For rainbow: script.py rainbow pixels duration_ds output.prg")
        print("  For custom sequence: script.py custom pixels output.prg r1 g1 b1 duration1 [r2 g2 b2 duration2 ...]")
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
            
        elif mode == "rgb_cycle":
            if len(sys.argv) < 5:
                print("Usage for RGB cycle: script.py rgb_cycle pixels duration_ds output.prg")
                sys.exit(1)
                
            pixels = int(sys.argv[2])
            duration_ds = int(sys.argv[3])
            output_file = sys.argv[4]
            
            file_size = generate_rgb_cycle(pixels, duration_ds, output_file)
            print(f"Successfully created RGB cycle {output_file} ({file_size} bytes)")
            
        elif mode == "rainbow":
            if len(sys.argv) < 5:
                print("Usage for rainbow: script.py rainbow pixels duration_ds output.prg")
                sys.exit(1)
                
            pixels = int(sys.argv[2])
            duration_ds = int(sys.argv[3])
            output_file = sys.argv[4]
            
            file_size = generate_rainbow(pixels, duration_ds, output_file)
            print(f"Successfully created rainbow {output_file} ({file_size} bytes)")
            
        elif mode == "custom":
            if len(sys.argv) < 7 or (len(sys.argv) - 4) % 4 != 0:
                print("Usage for custom sequence: script.py custom pixels output.prg r1 g1 b1 duration1 [r2 g2 b2 duration2 ...]")
                sys.exit(1)
                
            pixels = int(sys.argv[2])
            output_file = sys.argv[3]
            
            # Parse color and duration arguments
            colors = []
            durations = []
            
            for i in range(4, len(sys.argv), 4):
                r = int(sys.argv[i])
                g = int(sys.argv[i+1])
                b = int(sys.argv[i+2])
                duration = int(sys.argv[i+3])
                
                colors.append((r, g, b))
                durations.append(duration)
            
            file_size = generate_multi_color_prg(pixels, colors, durations, output_file)
            print(f"Successfully created custom sequence {output_file} ({file_size} bytes)")
            
        else:
            print("Invalid mode. Use 'single', 'rgb_cycle', 'rainbow', or 'custom'.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()