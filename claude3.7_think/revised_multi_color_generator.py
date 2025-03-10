#!/usr/bin/env python3
"""
Revised Multi-Color LTX Ball Sequence Generator

This script creates .prg files for complex color sequences with multiple colors and
variable durations. It's based on a more careful analysis of working examples and
addresses issues identified in previous versions.
"""

import sys
import os

def generate_multi_color_prg(pixel_count, colors, durations, output_file):
    """
    Generate a .prg file for a multi-color sequence with variable durations.
    
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
        return generate_single_color_prg(pixel_count, colors[0], durations[0], output_file)
    
    # --- 1. Fixed header (16 bytes) ---
    fixed_header = bytearray.fromhex(f"50 52 03 49 4e 05 00 00 00 {pixel_count:02x} 00 08 01 00 50 49")
    
    # --- 2. Variable header ---
    segment_count = len(colors)
    var_header = bytearray()
    
    # Calculate total header size based on working examples
    # For 2px_red_5_green_10_blue_15.prg, the header size is 0x3b (59) bytes for 3 segments
    # We'll use a formula that matches this example
    header_size = 16 + 16 + (segment_count * 9)  # Adjusted based on working example
    
    # Total duration (sum of all durations)
    total_duration = sum(durations)
    
    # Variable header
    var_header.extend(header_size.to_bytes(4, byteorder='little'))  # Header size
    var_header.extend(segment_count.to_bytes(2, byteorder='little'))  # Number of segments
    var_header.extend((0x0).to_bytes(2, byteorder='little'))   # Mode/flags: 0
    var_header.extend(total_duration.to_bytes(2, byteorder='little'))  # Total duration
    
    # Offset to first segment's color data (based on working example)
    first_segment_offset = 0x59  # From working example
    var_header.extend(first_segment_offset.to_bytes(2, byteorder='little'))
    
    # Special pattern (based on working examples)
    var_header.extend(bytes([0, 0, durations[0] & 0xFF, 0]))
    
    # --- 3. Segment descriptors ---
    segments = bytearray()
    
    # Calculate base offset for color data
    color_data_offset = header_size + 4  # Starting offset for color data
    color_block_size = 300  # Approximate size of each color block
    
    # Create segment descriptors for each color
    for i, duration in enumerate(durations):
        # First segment
        if i == 0:
            segments.extend((pixel_count).to_bytes(2, byteorder='little'))  # Pixel count
            segments.extend((0x1).to_bytes(2, byteorder='little'))          # Constant: 1
            segments.extend((0x0).to_bytes(2, byteorder='little'))          # Zeros
            segments.extend(duration.to_bytes(2, byteorder='little'))       # Duration for this segment
            segments.extend((0x0).to_bytes(2, byteorder='little'))          # Zeros
            segments.extend((0x0).to_bytes(2, byteorder='little'))          # Zeros
            
            # For first segment, we include total duration
            segments.extend(total_duration.to_bytes(2, byteorder='little'))
            
            # Offset to next segment's color data (based on working example)
            next_offset = 0x85  # From working example for first segment
            segments.extend(next_offset.to_bytes(2, byteorder='little'))
            
            # Additional constants
            segments.extend((0x01).to_bytes(2, byteorder='little'))
        
        # Middle segments
        elif i < segment_count - 1:
            segments.extend((pixel_count).to_bytes(2, byteorder='little'))  # Pixel count
            segments.extend((0x1).to_bytes(2, byteorder='little'))          # Constant: 1
            segments.extend((0x0).to_bytes(2, byteorder='little'))          # Zeros
            segments.extend(duration.to_bytes(2, byteorder='little'))       # Duration for this segment
            segments.extend((0x0).to_bytes(2, byteorder='little'))          # Zeros
            segments.extend((0x0).to_bytes(2, byteorder='little'))          # Zeros
            segments.extend(duration.to_bytes(2, byteorder='little'))       # Duration again
            
            # Offset to next segment's color data (calculated based on pattern in working example)
            next_offset = 0x85 + (i * 0x2c)  # Pattern from working example
            segments.extend(next_offset.to_bytes(2, byteorder='little'))
            
            # Additional constants and padding
            segments.extend((0x0).to_bytes(4, byteorder='little'))
        
        # Last segment
        else:
            segments.extend((pixel_count).to_bytes(2, byteorder='little'))  # Pixel count
            segments.extend((0x1).to_bytes(2, byteorder='little'))          # Constant: 1
            segments.extend((0x0).to_bytes(2, byteorder='little'))          # Zeros
            segments.extend(duration.to_bytes(2, byteorder='little'))       # Duration for this segment
            segments.extend((0x0).to_bytes(2, byteorder='little'))          # Zeros
            segments.extend(b"CD")                                          # Constant: "CD"
            
            # Offset to this segment's color data (calculated based on pattern in working example)
            last_offset = 0x85 + ((i - 1) * 0x2c)  # Pattern from working example
            segments.extend(last_offset.to_bytes(2, byteorder='little'))
            
            # Size of color data
            segments.extend(color_block_size.to_bytes(2, byteorder='little'))
            segments.extend((0x0).to_bytes(2, byteorder='little'))          # Padding
    
    # --- 4. Color data blocks ---
    color_data = bytearray()
    
    # For each color, create a color block
    for i, (r, g, b) in enumerate(colors):
        # Start with 3 zeros
        color_block = bytearray([0, 0, 0])
        
        # Create repeating RGB pattern - using the same order as in working examples
        # In working examples, red is FF 00 00, green is 00 FF 00, blue is 00 00 FF
        rgb_pattern = bytes([r, g, b])
        
        # Fill to color_block_size bytes (minus the 3 starting zeros)
        repeats = (color_block_size - 3) // 3
        remainder = (color_block_size - 3) % 3
        
        color_block.extend(rgb_pattern * repeats)
        color_block.extend(rgb_pattern[:remainder])
        
        # For the last color block, replace the last byte with 0x42
        if i == len(colors) - 1:
            color_block = color_block[:-1] + bytes([0x42])
            
        color_data.extend(color_block)
    
    # --- 5. Footer ---
    # Use the same footer as in working examples
    footer = bytes.fromhex("54 00 00 00 00")
    
    # Combine all parts
    prg_data = fixed_header + var_header + segments + color_data + footer
    
    # Write the .prg file
    with open(output_file, 'wb') as f:
        f.write(prg_data)
    
    return len(prg_data)

def generate_single_color_prg(pixel_count, rgb_color, duration_ds, output_file):
    """
    Generate a .prg file for a single solid color with specified duration.
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - rgb_color: Tuple of (r, g, b) values (0-255)
    - duration_ds: Duration in deciseconds (100 = 10 seconds)
    - output_file: Path to save the generated .prg file
    """
    # For single color, we'll directly copy from a known working example
    # and just modify the pixel count, color, and duration
    
    r, g, b = rgb_color
    
    # Convert duration to little-endian hex
    duration_hex = f"{duration_ds:02x} 00"
    
    # Fixed header and structure with variable duration
    data = bytearray.fromhex(
        f"50 52 03 49 4e 05 00 00 00 {pixel_count:02x} 00 08 01 00 50 49" +  # Fixed header
        f"15 00 00 00 01 00 01 00 {duration_hex} 33 00 00 00 00 00" +        # Variable header with duration
        f"{pixel_count:02x} 00 01 00 00 {duration_hex} 00 00 43 44 30 01 00 00 {duration_hex}" +  # Segment descriptor
        "00 00"                                                              # Start of color data
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

def generate_custom_sequence(pixel_count, colors, durations, output_file):
    """
    Generate a .prg file for a custom color sequence with variable durations.
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - colors: List of (r, g, b) tuples for each color in the sequence
    - durations: List of durations in deciseconds for each color
    - output_file: Path to save the generated .prg file
    """
    return generate_multi_color_prg(pixel_count, colors, durations, output_file)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  For single color: script.py single pixels r g b duration_ds output.prg")
        print("  For RGB cycle: script.py rgb_cycle pixels duration_ds output.prg")
        print("  For rainbow: script.py rainbow pixels duration_ds output.prg")
        print("  For custom sequence: script.py custom pixels output.prg r1 g1 b1 duration1 [r2 g2 b2 duration2 ...]")
        sys.exit(1)
    
    try:
        mode = sys.argv[1].lower()
        
        if mode == "single":
            if len(sys.argv) < 8:
                print("Usage for single color: script.py single pixels r g b duration_ds output.prg")
                sys.exit(1)
                
            pixels = int(sys.argv[2])
            r = int(sys.argv[3])
            g = int(sys.argv[4])
            b = int(sys.argv[5])
            duration_ds = int(sys.argv[6])
            output_file = sys.argv[7]
            
            file_size = generate_single_color_prg(pixels, (r, g, b), duration_ds, output_file)
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
            
            file_size = generate_custom_sequence(pixels, colors, durations, output_file)
            print(f"Successfully created custom sequence {output_file} ({file_size} bytes)")
            
        else:
            print("Invalid mode. Use 'single', 'rgb_cycle', 'rainbow', or 'custom'.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()