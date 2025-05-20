#!/usr/bin/env python3
"""
Unified converter script for sequence files
"""

import os
import sys
import argparse
from .convert_to_ball import convert_word_flash_to_ball
from .convert_ball_to_seqdesign import convert_ball_to_seqdesign
from .convert_lyrics_to_ball import convert_lyrics_to_ball

def main():
    parser = argparse.ArgumentParser(description="Convert between sequence file formats")
    parser.add_argument("input_file", help="Path to input file")
    parser.add_argument("output_file", help="Path to output file")
    parser.add_argument("--color", default="0,0,255", help="RGB color for words (comma-separated, e.g., '0,0,255')")
    parser.add_argument("--background", default="0,0,0", help="RGB color for gaps (comma-separated, e.g., '0,0,0')")
    parser.add_argument("--pixels", type=int, default=4, help="Number of pixels (1-4)")
    
    args = parser.parse_args()
    
    # Determine conversion type based on file extensions
    input_ext = os.path.splitext(args.input_file)[1].lower()
    output_ext = os.path.splitext(args.output_file)[1].lower()
    
    # Convert word_flash_sequence.json to .ball.json
    if input_ext == '.json' and 'word_flash_sequence' in args.input_file and output_ext == '.ball.json':
        convert_word_flash_to_ball(args.input_file, args.output_file)
    
    # Convert .ball.json to .seqdesign.json
    elif input_ext == '.ball.json' and output_ext == '.seqdesign.json':
        convert_ball_to_seqdesign(args.input_file, args.output_file)
    
    # Convert .lyrics.json to .ball.json
    elif input_ext == '.lyrics.json' and output_ext == '.ball.json':
        try:
            color = [int(x) for x in args.color.split(",")]
            if len(color) != 3:
                raise ValueError("Color must have 3 components")
        except:
            print(f"Warning: Invalid color format: {args.color}. Using default blue [0,0,255].")
            color = [0, 0, 255]
        
        try:
            background_color = [int(x) for x in args.background.split(",")]
            if len(background_color) != 3:
                raise ValueError("Background color must have 3 components")
        except:
            print(f"Warning: Invalid background color format: {args.background}. Using default black [0,0,0].")
            background_color = [0, 0, 0]
        
        convert_lyrics_to_ball(args.input_file, args.output_file, color, background_color, args.pixels)
    
    else:
        print(f"Error: Unsupported conversion from {input_ext} to {output_ext}")
        sys.exit(1)

if __name__ == "__main__":
    main()