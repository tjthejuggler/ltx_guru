import json
import sys

def create_ball_json_for_repeating_sequence(original_lyrics_path, output_ball_json_path, second_round_first_word_start_time_seconds):
    """
    Generates a .ball.json file for a sequence that repeats, with color cycling
    and off-states between words.

    Args:
        original_lyrics_path (str): Path to the .lyrics.json file of the original (first) sequence.
        output_ball_json_path (str): Path to save the generated .ball.json file.
        second_round_first_word_start_time_seconds (float): The start time (in seconds)
                                                            of the first word in the second repetition.
    """
    try:
        with open(original_lyrics_path, 'r') as f:
            lyrics_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Original lyrics file not found at {original_lyrics_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {original_lyrics_path}")
        return

    word_timestamps = lyrics_data.get("word_timestamps", [])
    if not word_timestamps:
        print("Error: No word_timestamps found in the lyrics file.")
        return

    song_title = "One to One Hundred Twice"
    artist_name = lyrics_data.get("artist_name", "Unknown")

    colors = [
        [255, 0, 0],    # Red
        [255, 165, 0],  # Orange
        [255, 255, 0],  # Yellow
        [0, 255, 0],    # Green
        [0, 0, 255],    # Blue
        [255, 0, 255]   # Magenta (for Pink)
    ]
    black_color = [0, 0, 0]
    num_colors = len(colors)
    color_index = 0

    segments = []
    
    original_first_word_start = word_timestamps[0]["start"]
    time_offset_for_second_round = second_round_first_word_start_time_seconds - original_first_word_start

    last_word_end_time = 0

    # Process both rounds (original and repeated)
    for round_num in range(2):
        current_offset = 0 if round_num == 0 else time_offset_for_second_round
        
        # Ensure there's an initial off segment if the first word doesn't start at 0
        # and it's the first round, or if there's a gap before the second round starts
        # relative to the end of the first.
        if round_num == 0 and word_timestamps[0]["start"] > 0:
             # For the very first word, if it doesn't start at 0
            if last_word_end_time < word_timestamps[0]["start"] + current_offset:
                 segments.append({
                    "start_time": round(last_word_end_time, 3),
                    "end_time": round(word_timestamps[0]["start"] + current_offset, 3),
                    "color": black_color,
                    "pixels": [black_color]
                })
        elif round_num == 1: # Start of the second round
            # Add a black segment from the end of the first round to the start of the second
            if last_word_end_time < word_timestamps[0]["start"] + current_offset:
                segments.append({
                    "start_time": round(last_word_end_time, 3),
                    "end_time": round(word_timestamps[0]["start"] + current_offset, 3),
                    "color": black_color,
                    "pixels": [black_color]
                })


        for i, word_info in enumerate(word_timestamps):
            word_start_time = round(word_info["start"] + current_offset, 3)
            word_end_time = round(word_info["end"] + current_offset, 3)

            # Add black segment before the current word if there's a gap
            if word_start_time > last_word_end_time and last_word_end_time != 0 : #don't add if it's the very first segment
                 # Corrected condition: only add black if it's not the very first word of the entire sequence
                if not (round_num == 0 and i == 0): # or if it's the start of the second round and there's a designated gap
                    segments.append({
                        "start_time": round(last_word_end_time, 3),
                        "end_time": word_start_time,
                        "color": black_color,
                        "pixels": [black_color]
                    })


            # Add colored segment for the word
            current_color = colors[color_index % num_colors]
            segments.append({
                "start_time": word_start_time,
                "end_time": word_end_time,
                "color": current_color,
                "pixels": [current_color]
            })
            color_index += 1
            last_word_end_time = word_end_time

            # For the next iteration (gap after this word)
            # This logic for trailing black segment will be handled by the next word's pre-black segment
            # or by a final black segment if it's the absolute last word.

    # Calculate total duration
    total_duration_ms = 0
    if segments:
        total_duration_ms = int(segments[-1]["end_time"] * 1000)
        # Add a final black segment if the audio might be longer
        # For this specific case, we assume the sequence ends with the last word.
        # If there's a need for padding, it can be added here.

    ball_data = {
        "metadata": {
            "name": song_title,
            "artist": artist_name,
            "total_duration_ms": total_duration_ms
        },
        "segments": segments
    }

    try:
        with open(output_ball_json_path, 'w') as f:
            json.dump(ball_data, f, indent=2)
        print(f"Successfully generated {output_ball_json_path}")
    except IOError:
        print(f"Error: Could not write to file {output_ball_json_path}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_repeating_sequence_with_color_cycle.py <original_lyrics.json> <output.ball.json> <second_round_start_seconds>")
        sys.exit(1)
    
    original_lyrics_file = sys.argv[1]
    output_ball_file = sys.argv[2]
    try:
        second_round_start = float(sys.argv[3])
    except ValueError:
        print("Error: <second_round_start_seconds> must be a number.")
        sys.exit(1)

    create_ball_json_for_repeating_sequence(original_lyrics_file, output_ball_file, second_round_start)