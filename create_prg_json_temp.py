import json
import os

# Configuration for the generated JSON files
CONFIG = {
    "default_pixels": 1,
    "refresh_rate": 50, # Hz
}

SEGMENT_DURATION_UNITS = 10 # Each segment lasts for 10 time units.

# Colors to cycle through for segments
COLORS = [
    [255, 0, 0],  # Red
    [0, 255, 0],  # Green
    [0, 0, 255],  # Blue
]

SEGMENT_COUNTS = [1, 2, 3, 254, 255, 256, 257]
OUTPUT_DIR = "generated_test_prg_json"

def generate_prg_json_file(num_segments, filename_prefix="test_segments"):
    """
    Generates a .prg.json file with a specified number of simple segments.
    """
    prg_data = {
        "default_pixels": CONFIG["default_pixels"],
        "refresh_rate": CONFIG["refresh_rate"],
        "sequence": {}
    }

    current_time_units = 0
    for i in range(num_segments):
        segment_data = {
            "color": COLORS[i % len(COLORS)],
            "pixels": CONFIG["default_pixels"]
        }
        prg_data["sequence"][str(current_time_units)] = segment_data
        current_time_units += SEGMENT_DURATION_UNITS

    prg_data["end_time"] = current_time_units

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")
    
    full_output_path = os.path.join(OUTPUT_DIR, f"{filename_prefix}_{num_segments}.prg.json")

    with open(full_output_path, 'w') as f:
        json.dump(prg_data, f, indent=4)
    
    print(f"Successfully generated: {full_output_path}")

if __name__ == "__main__":
    print(f"Generating .prg.json files into directory: '{OUTPUT_DIR}'")
    for count in SEGMENT_COUNTS:
        generate_prg_json_file(count)
    
    print("\nAll .prg.json files generated.")
    print(f"You can now use prg_generator.py to convert these to .prg files, e.g.:")
    print(f"python prg_generator.py {os.path.join(OUTPUT_DIR, 'test_segments_254.prg.json')} output_prg_files/test_segments_254.prg")
    print("(Assuming prg_generator.py is in your PATH or current directory, and an 'output_prg_files' directory exists or is created by prg_generator.py)")