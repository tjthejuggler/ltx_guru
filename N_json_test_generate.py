import json
import argparse
import os # Added for path operations if needed, but string formatting is enough here

# --- Configuration ---
DEFAULT_PIXELS = 4
COLOR_FORMAT = "rgb"
REFRESH_RATE = 1000
TIMESTAMP_INCREMENT = 100
COLORS_CYCLE = [
    [255, 0, 0],  # Red
    [0, 255, 0],  # Green
    [0, 0, 255]   # Blue
]
OUTPUT_FILENAME_TEMPLATE = "N{}_json_test_generate.json" # Template for the output filename
# --- End Configuration ---

def generate_sequence_json(num_items):
    """
    Generates a JSON string with a sequence of color changes.

    Args:
        num_items (int): The number of items to generate in the sequence.

    Returns:
        str: A JSON formatted string.
    """
    if not isinstance(num_items, int) or num_items < 0:
        raise ValueError("Number of items must be a non-negative integer.")

    output_data = {
        "default_pixels": DEFAULT_PIXELS,
        "color_format": COLOR_FORMAT,
        "refresh_rate": REFRESH_RATE,
        "end_time": num_items * TIMESTAMP_INCREMENT,
        "sequence": {}
    }

    for i in range(num_items):
        timestamp = i * TIMESTAMP_INCREMENT
        current_color = COLORS_CYCLE[i % len(COLORS_CYCLE)] # Cycle through colors

        output_data["sequence"][str(timestamp)] = {
            "color": current_color,
            "pixels": DEFAULT_PIXELS
        }

    return json.dumps(output_data, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a JSON file with a timed color sequence and save it."
    )
    parser.add_argument(
        "num_items",
        type=int,
        help="The number of items (color steps) to generate in the sequence."
    )

    args = parser.parse_args()

    try:
        json_output = generate_sequence_json(args.num_items)
        
        # Generate filename
        output_filename = OUTPUT_FILENAME_TEMPLATE.format(args.num_items)

        # Write to file
        with open(output_filename, 'w') as f:
            f.write(json_output)
        
        print(f"Successfully generated JSON and saved to: {output_filename}")

    except ValueError as e:
        print(f"Error: {e}")
    except IOError as e:
        print(f"Error writing to file {output_filename}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")