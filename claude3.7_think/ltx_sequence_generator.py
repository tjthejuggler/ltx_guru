#!/usr/bin/env python3
"""
LTX Ball Sequence Generator

This script converts a JSON color sequence specification into a .prg file
that can be loaded onto LTX programmable juggling balls.

The JSON input format is:
{
  "pixels": 3,
  "color_format": "hsv",     // Optional: "hsv" (default) or "rgb"
  "sequence": {
    "0": [0, 100, 100],      // HSV: start Red (H=0, S=100, V=100)
    "1500": [120, 100, 100], // HSV: at 15 seconds change to Green (H=120)
    "3500": [240, 100, 100], // HSV: at 35 seconds change to Blue (H=240)
    "6000": [0, 100, 100]    // HSV: at 60 seconds change to Red (H=0)
  }
}

OR with RGB format:
{
  "pixels": 3,
  "color_format": "rgb",
  "sequence": {
    "0": [255, 0, 0],        // RGB: start Red
    "1500": [0, 255, 0],     // RGB: at 15 seconds change to Green
    "3500": [0, 0, 255],     // RGB: at 35 seconds change to Blue
    "6000": [255, 0, 0]      // RGB: at 60 seconds change to Red
  }
}

Where:
- "pixels" is the number of LED pixels (1-4)
- "color_format" is either "hsv" (default) or "rgb"
- "sequence" is a dictionary with timestamps (in deciseconds) as keys
  and color values as values:
  - For HSV: [H, S, V] where H=0-360, S=0-100, V=0-100
  - For RGB: [R, G, B] where R,G,B=0-255
"""

import json
import sys
import colorsys
import os

def hsv_to_rgb(h, s, v):
    """
    Convert HSV color to RGB.
    
    Parameters:
    - h: Hue (0-360)
    - s: Saturation (0-100)
    - v: Value (0-100)
    
    Returns:
    - (r, g, b): RGB values (0-255)
    """
    # Normalize values to range expected by colorsys (0-1)
    h_norm = h / 360
    s_norm = s / 100
    v_norm = v / 100
    
    # Convert to RGB (values between 0-1)
    r, g, b = colorsys.hsv_to_rgb(h_norm, s_norm, v_norm)
    
    # Scale to 0-255 range and return as integers
    return (int(r * 255), int(g * 255), int(b * 255))

def generate_prg_file(json_data, output_file):
    """
    Generate a .prg file from the provided JSON color sequence data.
    
    Parameters:
    - json_data: Dictionary containing pixel count and sequence data
    - output_file: Path to save the generated .prg file
    """
    # Extract data from JSON
    pixel_count = json_data.get("pixels", 4)  # Default to 4 pixels if not specified
    sequence = json_data.get("sequence", {})
    color_format = json_data.get("color_format", "hsv").lower()  # Default to HSV
    
    # Validate pixel count
    if not 1 <= pixel_count <= 4:
        raise ValueError(f"Invalid pixel count: {pixel_count}. Must be between 1 and 4.")
    
    # Validate color format
    if color_format not in ["hsv", "rgb"]:
        raise ValueError(f"Invalid color format: {color_format}. Must be 'hsv' or 'rgb'.")
    
    # Validate and sort sequence data
    if not sequence:
        raise ValueError("Sequence data is empty.")
    
    # Convert times to integers and sort them
    time_points = [(int(time_str), color_values) for time_str, color_values in sequence.items()]
    time_points.sort(key=lambda x: x[0])
    
    # Calculate segments (transitions between color points)
    segments = []
    for i in range(len(time_points) - 1):
        start_time, start_color = time_points[i]
        end_time, end_color = time_points[i+1]
        duration = end_time - start_time
        
        # Convert color to RGB if needed
        if color_format == "hsv":
            rgb = hsv_to_rgb(*start_color)
        else:  # RGB format
            rgb = tuple(start_color)
        
        segments.append({
            "start_time": start_time,
            "duration": duration,
            "rgb": rgb
        })
    
    # Add final segment (using the last color)
    final_time, final_color = time_points[-1]
    
    # Convert final color to RGB if needed
    if color_format == "hsv":
        final_rgb = hsv_to_rgb(*final_color)
    else:  # RGB format
        final_rgb = tuple(final_color)
    
    # Set a default duration of 10 seconds for the final segment if not specified
    segments.append({
        "start_time": final_time,
        "duration": 100,  # 10 seconds in deciseconds
        "rgb": final_rgb
    })
    
    # --- Generate the .prg file ---
    segment_count = len(segments)
    
    # --- 1. Fixed header (16 bytes) ---
    fixed_header = bytes.fromhex(f"50 52 03 49 4e 05 00 00 00 {pixel_count:02x} 00 08 01 00 50 49")
    
    # --- 2. Variable header (16 bytes) ---
    # Calculate segment table length: 2 bytes for pixel count + 19 bytes per segment
    segment_table_length = 2 + (19 * segment_count)
    
    # Build variable header
    var_header = bytearray()
    var_header.extend(segment_table_length.to_bytes(4, byteorder='little'))  # Segment table length (4 bytes)
    var_header.extend(segment_count.to_bytes(2, byteorder='little'))         # Segment count (2 bytes)
    var_header.extend((1).to_bytes(2, byteorder='little'))                   # Flag/mode (2 bytes)
    
    # Total duration (sum of all segment durations)
    total_duration = sum(segment["duration"] for segment in segments)
    var_header.extend(total_duration.to_bytes(2, byteorder='little'))       # Duration (2 bytes)
    
    # Pixel data offset (equals segment table length)
    var_header.extend(segment_table_length.to_bytes(2, byteorder='little'))  # Offset (2 bytes)
    
    # Reserved (4 bytes)
    var_header.extend(bytes(4))
    
    # --- 3. Segment table ---
    segment_table = bytearray()
    
    # First 2 bytes: pixel count
    segment_table.extend(pixel_count.to_bytes(2, byteorder='little'))
    
    # Calculate base offset for color data
    base_offset = 0x0185  # Initial offset observed in example files
    
    # Add segment records (19 bytes each)
    for i, segment in enumerate(segments):
        record = bytearray()
        
        if i == 0:
            # First segment has a special format
            record.extend((1).to_bytes(2, byteorder='little'))                     # 01 00
            record.extend((0).to_bytes(2, byteorder='little'))                     # 00 00
            record.extend(segment["duration"].to_bytes(2, byteorder='little'))     # Duration
            record.extend((0).to_bytes(2, byteorder='little'))                     # 00 00
            record.extend((1).to_bytes(2, byteorder='little'))                     # 01 00
            record.extend((0).to_bytes(2, byteorder='little'))                     # 00 00
            record.extend(segment["duration"].to_bytes(2, byteorder='little'))     # Duration
            
            # Offset for first segment
            next_offset = base_offset
            record.extend(next_offset.to_bytes(2, byteorder='little'))
            
            record.extend((0).to_bytes(3, byteorder='little'))                     # 00 00 00
        else:
            # Middle and last segments
            record.extend((0).to_bytes(1, byteorder='little'))                     # 00
            record.extend(pixel_count.to_bytes(2, byteorder='little'))             # Pixel count
            record.extend((1).to_bytes(2, byteorder='little'))                     # 01 00
            record.extend((0).to_bytes(2, byteorder='little'))                     # 00 00
            record.extend(segment["duration"].to_bytes(2, byteorder='little'))     # Duration
            
            if i == segment_count - 1:
                # Last segment has 'CD' marker
                record.extend((0).to_bytes(2, byteorder='little'))                 # 00 00
                record.extend(b'CD')                                               # CD marker
                
                # Calculate offset for color data
                next_offset = base_offset + (i * 0x022C)
                record.extend(next_offset.to_bytes(2, byteorder='little'))
                
                # Size of color data
                color_data_size = 300  # Approximate color data size per segment
                record.extend(color_data_size.to_bytes(2, byteorder='little'))
                record.extend((0).to_bytes(2, byteorder='little'))                 # 00 00
            else:
                # Middle segments
                record.extend((0).to_bytes(2, byteorder='little'))                 # 00 00
                record.extend((1).to_bytes(2, byteorder='little'))                 # 01 00
                record.extend((0).to_bytes(2, byteorder='little'))                 # 00 00
                record.extend(segment["duration"].to_bytes(2, byteorder='little')) # Duration
                
                # Calculate offset for next segment
                next_offset = base_offset + (i * 0x022C)
                record.extend(next_offset.to_bytes(2, byteorder='little'))
                
                record.extend((0).to_bytes(4, byteorder='little'))                 # 00 00 00 00
        
        # Ensure record is exactly 19 bytes
        record = record[:19]
        record = record.ljust(19, b'\x00')
        
        segment_table.extend(record)
    
    # --- 4. Pixel data block ---
    pixel_data = bytearray()
    
    # For each segment, we create a color block
    for segment in segments:
        # RGB color
        r, g, b = segment["rgb"]
        
        # Prepare the color block
        color_block = bytearray()
        
        # Start with a 3-byte prefix of zeros
        color_block.extend(bytes([0, 0, 0]))
        
        # Fill the block with RGB pattern
        rgb_pattern = bytes([r, g, b])
        
        # Each segment gets about 300 bytes of color data
        color_data_size = 300 - len(color_block)  # Subtract the prefix
        repeats = color_data_size // 3
        remainder = color_data_size % 3
        
        color_block.extend(rgb_pattern * repeats)
        color_block.extend(rgb_pattern[:remainder])
        
        # Ensure the very last byte is 0x42 (for the last segment)
        if segment == segments[-1]:
            color_block = color_block[:-1] + bytes([0x42])
        
        pixel_data.extend(color_block)
    
    # --- 5. Footer (5 bytes) ---
    footer = bytes.fromhex("54 00 00 00 00")  # 'T' followed by four 0x00 bytes
    
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
        file_size = generate_prg_file(json_data, output_file)
        print(f"Successfully created {output_file} ({file_size} bytes)")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()