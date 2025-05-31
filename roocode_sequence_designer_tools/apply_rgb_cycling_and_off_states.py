import json
import argparse

def apply_rgb_cycling_and_off_states(input_file_path, output_file_path):
    """
    Applies RGB color cycling to word segments and inserts "off" states
    between words in a .ball.json file.

    Args:
        input_file_path (str): Path to the input .ball.json file.
        output_file_path (str): Path to save the modified .ball.json file.
    """
    try:
        with open(input_file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_file_path}")
        return

    if "segments" not in data:
        print(f"Error: 'segments' key not found in {input_file_path}")
        return

    # The input .ball.json (e.g., from convert_lyrics_to_ball.py) is expected to have
    # segments for spoken words (e.g., initially colored blue or some other non-black color)
    # and segments for silence (colored black [0,0,0]).
    # This script will iterate through these segments and only change the color of
    # the spoken word segments according to the R-G-B cycle.

    colors = [[255, 0, 0], [0, 0, 255]]  # Red, Blue
    word_color_index = 0  # This index tracks the color for actual word segments

    # Ensure segments are processed in order. The input from convert_lyrics_to_ball.py
    # should already be sorted and have the correct on/off structure.
    # We will modify the segment colors in data["segments"] directly.
    
    # Sorting defensively, although convert_lyrics_to_ball.py should provide sorted segments.
    if "segments" in data and isinstance(data["segments"], list):
        data["segments"].sort(key=lambda s: s.get("start_time", 0))

    for segment in data.get("segments", []):
        current_color = segment.get("color", [0,0,0])
        # A segment is considered "off" if all its color components are zero.
        is_off_segment = all(c == 0 for c in current_color)
        
        if not is_off_segment:
            # This is a "word" segment (not off), so apply the R-G-B cycle color
            segment["color"] = colors[word_color_index % len(colors)]
            word_color_index += 1
        # If it is an "off" segment, its color (e.g., [0,0,0]) remains unchanged.
    
    # data["segments"] has now been modified in place with the correct colors.

    # Ensure metadata like total_duration is present and sensible
    if "metadata" not in data:
        data["metadata"] = {}
    if not data.get("segments"): # Check against data["segments"] which is modified in-place
        data["metadata"]["total_duration"] = 0
    else:
        # total_duration should be the end time of the last segment
        data["metadata"]["total_duration"] = max(s.get("end_time", 0) for s in data["segments"]) if data["segments"] else 0
        if "default_pixels" not in data["metadata"]:
             data["metadata"]["default_pixels"] = "all"


    try:
        with open(output_file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Successfully modified sequence and saved to {output_file_path}")
    except IOError:
        print(f"Error: Could not write to output file {output_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Apply RGB cycling and off states to a .ball.json file.')
    parser.add_argument('input_file', help='Path to the input .ball.json file')
    parser.add_argument('output_file', help='Path to save the modified .ball.json file')
    
    args = parser.parse_args()
    
    apply_rgb_cycling_and_off_states(args.input_file, args.output_file)