#!/usr/bin/env python3
import sys
import os
from pydub import AudioSegment

def trim_mp3(input_file, centiseconds):
    try:
        # Load the audio file
        audio = AudioSegment.from_mp3(input_file)
        
        # Convert centiseconds to milliseconds
        ms_to_trim = centiseconds * 10
        
        # Trim the audio
        trimmed_audio = audio[ms_to_trim:]
        
        # Generate output filename using just the base filename
        base_filename = os.path.basename(input_file)
        output_file = f"trimmed_{base_filename}"
        
        # Export the trimmed audio
        trimmed_audio.export(output_file, format="mp3")
        print(f"Successfully trimmed {centiseconds/100} seconds from {input_file}")
        print(f"Saved as: {output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 mp3trim.py <input_file.mp3> <centiseconds>")
        print("Example: python3 mp3trim.py song.mp3 130")
        sys.exit(1)
    
    try:
        input_file = sys.argv[1]
        centiseconds = int(sys.argv[2])
        
        if centiseconds < 0:
            print("Error: Centiseconds must be a positive number")
            sys.exit(1)
            
        trim_mp3(input_file, centiseconds)
        
    except ValueError:
        print("Error: Centiseconds must be a valid number")
        sys.exit(1)

if __name__ == "__main__":
    main()