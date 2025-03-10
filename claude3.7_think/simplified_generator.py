#!/usr/bin/env python3
"""
Simplified LTX Ball Sequence Generator

This script creates simple .prg files from JSON specifications for testing with LTX balls.
It focuses on clear, predictable patterns with minimal complexity.
"""

import json
import sys
import os

def generate_simple_prg(json_data, output_file):
    """
    Generate a simplified .prg file from the provided JSON color sequence data.
    
    Parameters:
    - json_data: Dictionary containing pixel count and sequence data
    - output_file: Path to save the generated .prg file
    """
    # Extract data from JSON
    pixel_count = json_data.get("pixels", 4)  # Default to 4 pixels
    sequence = json_data.get("sequence", {})
    
    # Validate pixel count
    if not 1 <= pixel_count <= 4:
        raise ValueError(f"Invalid pixel count: {pixel_count}. Must be between 1 and 4.")
    
    # Validate sequence data
    if not sequence:
        raise ValueError("Sequence data is empty.")
    
    # Convert times to integers and sort them
    time_points = [(int(time_str), color_values) for time_str, color_values in sequence.items()]
    time_points.sort(key=lambda x: x[0])
    
    # --- Generate the .prg file ---
    
    # --- 1. Fixed header (16 bytes) ---
    fixed_header = bytes.fromhex(f"50 52 03 49 4e 05 00 00 00 {pixel_count:02x} 00 08 01 00 50 49")
    
    # --- 2. Simple variable header (16 bytes) ---
    var_header = bytearray([0] * 16)
    var_header[0:4] = (300).to_bytes(4, byteorder='little')  # Fixed length for simplicity
    var_header[4:6] = (1).to_bytes(2, byteorder='little')    # Single segment
    var_header[6:8] = (1).to_bytes(2, byteorder='little')    # Mode 1
    var_header[8:10] = (100).to_bytes(2, byteorder='little') # Fixed duration
    var_header[10:12] = (300).to_bytes(2, byteorder='little') # Offset
    
    # --- 3. Segment table (simplified) ---
    segment_table = bytearray()
    segment_table.extend(pixel_count.to_bytes(2, byteorder='little'))
    
    # Add simplified segment record
    segment_record = bytearray([0] * 19)
    segment_record[0:2] = (1).to_bytes(2, byteorder='little')       # 01 00
    segment_record[4:6] = (100).to_bytes(2, byteorder='little')     # Duration
    segment_record[8:10] = (1).to_bytes(2, byteorder='little')      # 01 00
    segment_record[12:14] = (100).to_bytes(2, byteorder='little')   # Duration
    segment_record[14:16] = (0x0185).to_bytes(2, byteorder='little') # Offset
    segment_table.extend(segment_record)
    
    # --- 4. Pixel data block (simplified) ---
    pixel_data = bytearray()
    
    # Extract colors from time points
    color_blocks = []
    for i, (time, color) in enumerate(time_points):
        r, g, b = color
        color_block = bytearray([0, 0, 0])  # Start with zeros
        rgb_pattern = bytes([r, g, b])
        color_block.extend(rgb_pattern * 95)  # Repeat RGB pattern
        
        if i == len(time_points) - 1:
            color_block = color_block[:-1] + bytes([0x42])  # Last byte is 0x42
            
        color_blocks.append(color_block)
    
    # For simplicity, just use the first color block
    pixel_data.extend(color_blocks[0])
    
    # --- 5. Footer (5 bytes) ---
    footer = bytes.fromhex("54 00 00 00 00")
    
    # Combine all parts to create the final .prg file
    prg_data = fixed_header + var_header + segment_table + pixel_data + footer
    
    # Write the .prg file
    with open(output_file, 'wb') as f:
        f.write(prg_data)
    
    return len(prg_data)

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} input.json output.prg")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' not found.")
            sys.exit(1)
        
        # Load and parse JSON file
        with open(input_file, 'r') as f:
            try:
                json_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON format in '{input_file}': {e}")
                sys.exit(1)
        
        # Generate the .prg file
        file_size = generate_simple_prg(json_data, output_file)
        print(f"Successfully created {output_file} ({file_size} bytes)")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()