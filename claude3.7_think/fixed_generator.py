#!/usr/bin/env python3
"""
LTX Juggling Ball Sequence Generator (Fixed Version)

A tool for creating .prg files for LTX LED juggling balls based on the direct copy approach
that was proven to work correctly in our tests.

Usage:
  python3 fixed_generator.py single 4 255 0 0 red.prg
  python3 fixed_generator.py dual 4 255 0 0 0 255 0 red_to_green.prg
  python3 fixed_generator.py rgb_cycle 4 rgb_cycle.prg
  python3 fixed_generator.py rainbow 4 rainbow.prg
  python3 fixed_generator.py police 4 police.prg
  python3 fixed_generator.py traffic 4 traffic.prg
  python3 fixed_generator.py custom 4 custom.prg 255 0 0 0 255 0 0 0 255

Note: All colors will have a fixed duration of 10 seconds to ensure correct timing.
"""

import sys
import os
import argparse

def generate_single_color_prg(pixel_count, rgb_color, output_file):
    """
    Generate a .prg file for a single solid color by directly copying a known working example.
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - rgb_color: Tuple of (r, g, b) values (0-255)
    - output_file: Path to save the generated .prg file
    
    Returns:
    - Size of the generated file in bytes
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
    
    # Update pixel count if different from 4
    if pixel_count != 4:
        data[9] = pixel_count
        data[32] = pixel_count
    
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
    
    Returns:
    - Size of the generated file in bytes
    """
    # Known working example for red-to-green (4px_red_10_green_10.prg)
    # This is a direct copy of the hex values with only the color data modified
    r1, g1, b1 = rgb_color1
    r2, g2, b2 = rgb_color2
    
    # IMPORTANT: For correct timing, we must use the exact hex values from the working example
    # The duration is hardcoded to 10 seconds (0x0A) per color
    # Attempting to modify these values causes timing issues
    
    # Fixed header and structure (exact copy from working example)
    data = bytearray.fromhex(
        "50 52 03 49 4e 05 00 00 00 04 00 08 01 00 50 49" +  # Fixed header
        "28 00 00 00 02 00 00 00 64 00 46 00 00 00 0a 00" +  # Variable header
        "04 00 01 00 00 0a 00 00 00 00 00 64 00 72 01 00" +  # First segment descriptor
        "00 0a 00 04 00 01 00 00 0a 00 00 00 43 44 5c 02" +  # Second segment descriptor
        "00 00 c8 00 00 00"                                  # Start of first color data
    )
    
    # Update pixel count if different from 4
    if pixel_count != 4:
        data[9] = pixel_count
        data[32] = pixel_count
        data[45] = pixel_count
    
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

def generate_rgb_cycle(pixel_count, output_file):
    """
    Generate a .prg file for an RGB cycle (red → green → blue → red).
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - output_file: Path to save the generated .prg file
    
    Returns:
    - Size of the generated file in bytes
    
    Note: Each color will display for 10 seconds before transitioning.
    """
    # Create red to green
    temp_file1 = output_file + ".temp1"
    generate_two_color_prg(pixel_count, (255, 0, 0), (0, 255, 0), temp_file1)
    
    # Create green to blue
    temp_file2 = output_file + ".temp2"
    generate_two_color_prg(pixel_count, (0, 255, 0), (0, 0, 255), temp_file2)
    
    # Create blue to red
    temp_file3 = output_file + ".temp3"
    generate_two_color_prg(pixel_count, (0, 0, 255), (255, 0, 0), temp_file3)
    
    # Combine the files (just concatenate them)
    with open(output_file, 'wb') as outfile:
        for temp_file in [temp_file1, temp_file2, temp_file3]:
            with open(temp_file, 'rb') as infile:
                outfile.write(infile.read())
            os.remove(temp_file)
    
    # Get the file size
    file_size = os.path.getsize(output_file)
    
    return file_size

def generate_rainbow(pixel_count, output_file):
    """
    Generate a .prg file for a rainbow cycle.
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - output_file: Path to save the generated .prg file
    
    Returns:
    - Size of the generated file in bytes
    
    Note: Each color will display for 10 seconds before transitioning.
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
    
    # Create a series of two-color transitions
    temp_files = []
    for i in range(len(colors) - 1):
        temp_file = f"{output_file}.temp{i}"
        temp_files.append(temp_file)
        generate_two_color_prg(pixel_count, colors[i], colors[i+1], temp_file)
    
    # Combine the files (just concatenate them)
    with open(output_file, 'wb') as outfile:
        for temp_file in temp_files:
            with open(temp_file, 'rb') as infile:
                outfile.write(infile.read())
            os.remove(temp_file)
    
    # Get the file size
    file_size = os.path.getsize(output_file)
    
    return file_size

def generate_police_lights(pixel_count, output_file):
    """
    Generate a .prg file for police lights effect (red → blue → red).
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - output_file: Path to save the generated .prg file
    
    Returns:
    - Size of the generated file in bytes
    
    Note: Each color will display for 10 seconds before transitioning.
    """
    # Create red to blue
    temp_file1 = output_file + ".temp1"
    generate_two_color_prg(pixel_count, (255, 0, 0), (0, 0, 255), temp_file1)
    
    # Create blue to red
    temp_file2 = output_file + ".temp2"
    generate_two_color_prg(pixel_count, (0, 0, 255), (255, 0, 0), temp_file2)
    
    # Combine the files (just concatenate them)
    with open(output_file, 'wb') as outfile:
        for temp_file in [temp_file1, temp_file2]:
            with open(temp_file, 'rb') as infile:
                outfile.write(infile.read())
            os.remove(temp_file)
    
    # Get the file size
    file_size = os.path.getsize(output_file)
    
    return file_size

def generate_traffic_lights(pixel_count, output_file):
    """
    Generate a .prg file for traffic lights effect (red → yellow → green → yellow → red).
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - output_file: Path to save the generated .prg file
    
    Returns:
    - Size of the generated file in bytes
    
    Note: Each color will display for 10 seconds before transitioning.
    This is a limitation of the current implementation, which uses fixed 10-second durations
    for all colors to ensure correct timing.
    """
    colors = [
        (255, 0, 0),      # Red
        (255, 255, 0),    # Yellow
        (0, 255, 0),      # Green
        (255, 255, 0),    # Yellow
        (255, 0, 0),      # Red
    ]
    
    # Create a series of two-color transitions
    temp_files = []
    for i in range(len(colors) - 1):
        temp_file = f"{output_file}.temp{i}"
        temp_files.append(temp_file)
        generate_two_color_prg(pixel_count, colors[i], colors[i+1], temp_file)
    
    # Combine the files (just concatenate them)
    with open(output_file, 'wb') as outfile:
        for temp_file in temp_files:
            with open(temp_file, 'rb') as infile:
                outfile.write(infile.read())
            os.remove(temp_file)
    
    # Get the file size
    file_size = os.path.getsize(output_file)
    
    return file_size

def generate_custom_sequence(pixel_count, colors, output_file):
    """
    Generate a .prg file for a custom sequence of colors.
    
    Parameters:
    - pixel_count: Number of pixels (1-4)
    - colors: List of (r, g, b) tuples for each color in the sequence
    - output_file: Path to save the generated .prg file
    
    Returns:
    - Size of the generated file in bytes
    
    Note: Each color will display for 10 seconds before transitioning.
    """
    if len(colors) < 1:
        raise ValueError("At least one color must be provided")
    
    if len(colors) == 1:
        return generate_single_color_prg(pixel_count, colors[0], output_file)
    
    # Create a series of two-color transitions
    temp_files = []
    for i in range(len(colors) - 1):
        temp_file = f"{output_file}.temp{i}"
        temp_files.append(temp_file)
        generate_two_color_prg(pixel_count, colors[i], colors[i+1], temp_file)
    
    # Combine the files (just concatenate them)
    with open(output_file, 'wb') as outfile:
        for temp_file in temp_files:
            with open(temp_file, 'rb') as infile:
                outfile.write(infile.read())
            os.remove(temp_file)
    
    # Get the file size
    file_size = os.path.getsize(output_file)
    
    return file_size

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate .prg files for LTX LED juggling balls.')
    
    subparsers = parser.add_subparsers(dest='mode', help='Mode of operation')
    
    # Single color mode
    single_parser = subparsers.add_parser('single', help='Generate a single color sequence')
    single_parser.add_argument('pixels', type=int, choices=range(1, 5), help='Number of pixels (1-4)')
    single_parser.add_argument('r', type=int, choices=range(256), help='Red value (0-255)')
    single_parser.add_argument('g', type=int, choices=range(256), help='Green value (0-255)')
    single_parser.add_argument('b', type=int, choices=range(256), help='Blue value (0-255)')
    single_parser.add_argument('output', help='Output file path')
    
    # Dual color mode
    dual_parser = subparsers.add_parser('dual', help='Generate a two-color sequence')
    dual_parser.add_argument('pixels', type=int, choices=range(1, 5), help='Number of pixels (1-4)')
    dual_parser.add_argument('r1', type=int, choices=range(256), help='First color red value (0-255)')
    dual_parser.add_argument('g1', type=int, choices=range(256), help='First color green value (0-255)')
    dual_parser.add_argument('b1', type=int, choices=range(256), help='First color blue value (0-255)')
    dual_parser.add_argument('r2', type=int, choices=range(256), help='Second color red value (0-255)')
    dual_parser.add_argument('g2', type=int, choices=range(256), help='Second color green value (0-255)')
    dual_parser.add_argument('b2', type=int, choices=range(256), help='Second color blue value (0-255)')
    dual_parser.add_argument('output', help='Output file path')
    
    # RGB cycle mode
    rgb_parser = subparsers.add_parser('rgb_cycle', help='Generate an RGB cycle sequence')
    rgb_parser.add_argument('pixels', type=int, choices=range(1, 5), help='Number of pixels (1-4)')
    rgb_parser.add_argument('output', help='Output file path')
    
    # Rainbow mode
    rainbow_parser = subparsers.add_parser('rainbow', help='Generate a rainbow cycle sequence')
    rainbow_parser.add_argument('pixels', type=int, choices=range(1, 5), help='Number of pixels (1-4)')
    rainbow_parser.add_argument('output', help='Output file path')
    
    # Police lights mode
    police_parser = subparsers.add_parser('police', help='Generate a police lights sequence')
    police_parser.add_argument('pixels', type=int, choices=range(1, 5), help='Number of pixels (1-4)')
    police_parser.add_argument('output', help='Output file path')
    
    # Traffic lights mode
    traffic_parser = subparsers.add_parser('traffic', help='Generate a traffic lights sequence')
    traffic_parser.add_argument('pixels', type=int, choices=range(1, 5), help='Number of pixels (1-4)')
    traffic_parser.add_argument('output', help='Output file path')
    
    # Custom mode
    custom_parser = subparsers.add_parser('custom', help='Generate a custom sequence')
    custom_parser.add_argument('pixels', type=int, choices=range(1, 5), help='Number of pixels (1-4)')
    custom_parser.add_argument('output', help='Output file path')
    custom_parser.add_argument('values', nargs='+', type=int, help='List of RGB values (r1 g1 b1 r2 g2 b2 ...)')
    custom_parser.epilog = "Note: All colors will have a fixed duration of 10 seconds."
    
    return parser.parse_args()

def main():
    """Main function."""
    # If no arguments provided, use sys.argv
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 fixed_generator.py single 4 255 0 0 red.prg")
        print("  python3 fixed_generator.py dual 4 255 0 0 0 255 0 red_to_green.prg")
        print("  python3 fixed_generator.py rgb_cycle 4 rgb_cycle.prg")
        print("  python3 fixed_generator.py rainbow 4 rainbow.prg")
        print("  python3 fixed_generator.py police 4 police.prg")
        print("  python3 fixed_generator.py traffic 4 traffic.prg")
        print("  python3 fixed_generator.py custom 4 custom.prg 255 0 0 0 255 0 0 0 255")
        print("\nIMPORTANT: All colors will have a fixed duration of 10 seconds.")
        print("          The duration parameters are ignored to ensure correct timing.")
        sys.exit(1)
    
    try:
        # Use argparse if available, otherwise fallback to manual parsing
        try:
            args = parse_arguments()
            mode = args.mode
        except:
            # Fallback to manual parsing
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
            print("Color will display for 10 seconds before repeating.")
            
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
            print("Each color will display for 10 seconds before transitioning.")
            
        elif mode == "rgb_cycle":
            if len(sys.argv) < 4:
                print("Usage for RGB cycle: script.py rgb_cycle pixels output.prg")
                sys.exit(1)
                
            pixels = int(sys.argv[2])
            output_file = sys.argv[3]
            
            file_size = generate_rgb_cycle(pixels, output_file)
            print(f"Successfully created RGB cycle {output_file} ({file_size} bytes)")
            print("Each color will display for 10 seconds before transitioning.")
            
        elif mode == "rainbow":
            if len(sys.argv) < 4:
                print("Usage for rainbow: script.py rainbow pixels output.prg")
                sys.exit(1)
                
            pixels = int(sys.argv[2])
            output_file = sys.argv[3]
            
            file_size = generate_rainbow(pixels, output_file)
            print(f"Successfully created rainbow {output_file} ({file_size} bytes)")
            print("Each color will display for 10 seconds before transitioning.")
            
        elif mode == "police":
            if len(sys.argv) < 4:
                print("Usage for police lights: script.py police pixels output.prg")
                sys.exit(1)
                
            pixels = int(sys.argv[2])
            output_file = sys.argv[3]
            
            file_size = generate_police_lights(pixels, output_file)
            print(f"Successfully created police lights {output_file} ({file_size} bytes)")
            print("Each color will display for 10 seconds before transitioning.")
            
        elif mode == "traffic":
            if len(sys.argv) < 4:
                print("Usage for traffic lights: script.py traffic pixels output.prg")
                sys.exit(1)
                
            pixels = int(sys.argv[2])
            output_file = sys.argv[3]
            
            file_size = generate_traffic_lights(pixels, output_file)
            print(f"Successfully created traffic lights {output_file} ({file_size} bytes)")
            print("Each color will display for 10 seconds before transitioning.")
            
        elif mode == "custom":
            if len(sys.argv) < 7 or (len(sys.argv) - 4) % 3 != 0:
                print("Usage for custom sequence: script.py custom pixels output.prg r1 g1 b1 [r2 g2 b2 ...]")
                print("IMPORTANT: All colors will have a fixed duration of 10 seconds.")
                sys.exit(1)
                
            pixels = int(sys.argv[2])
            output_file = sys.argv[3]
            
            # Parse color arguments (ignoring durations)
            colors = []
            
            for i in range(4, len(sys.argv), 3):
                if i+2 >= len(sys.argv):
                    break
                    
                r = int(sys.argv[i])
                g = int(sys.argv[i+1])
                b = int(sys.argv[i+2])
                
                colors.append((r, g, b))
            
            file_size = generate_custom_sequence(pixels, colors, output_file)
            print(f"Successfully created custom sequence {output_file} ({file_size} bytes)")
            print("Each color will display for 10 seconds before transitioning.")
            
        else:
            print("Invalid mode. Use 'single', 'dual', 'rgb_cycle', 'rainbow', 'police', 'traffic', or 'custom'.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()