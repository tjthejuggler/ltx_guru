#!/usr/bin/env python3
"""
Generate a sequence_maker JSON file that flashes blue during each word
and black/off between words.
"""

import json
import os

# Load the lyrics timestamps
with open('sequence_projects/you_know_me/lyrics_timestamps.json', 'r') as f:
    lyrics_data = json.load(f)

# Extract word timestamps
word_timestamps = lyrics_data['word_timestamps']

# Find the last word's end time for total duration
last_word_end = max(word['end'] for word in word_timestamps)
total_duration = last_word_end + 5.0  # Add 5 seconds buffer

# Create the sequence structure
sequence = {
    "name": "You Know Me - Word Flash",
    "default_pixels": 4,
    "refresh_rate": 50,
    "total_duration": total_duration,
    "timelines": [
        {
            "name": "Word Flash",
            "default_pixels": 4,
            "segments": []
        }
    ],
    "audio_file": "sequence_projects/you_know_me/lubalin_you_know_me.mp3",
    "key_mapping": "Default"
}

# Add initial black segment if first word doesn't start at 0
segments = sequence["timelines"][0]["segments"]
if word_timestamps[0]["start"] > 0:
    segments.append({
        "start_time": 0.0,
        "end_time": word_timestamps[0]["start"],
        "color": [0, 0, 0],
        "pixels": 4,
        "effects": []
    })

# Add segments for each word and the gaps between them
for i, word in enumerate(word_timestamps):
    # Add blue segment for the word
    segments.append({
        "start_time": word["start"],
        "end_time": word["end"],
        "color": [0, 0, 255],
        "pixels": 4,
        "effects": []
    })
    
    # Add black segment for the gap after this word (if not the last word)
    if i < len(word_timestamps) - 1:
        next_word = word_timestamps[i + 1]
        if word["end"] < next_word["start"]:
            segments.append({
                "start_time": word["end"],
                "end_time": next_word["start"],
                "color": [0, 0, 0],
                "pixels": 4,
                "effects": []
            })

# Add final black segment after the last word
segments.append({
    "start_time": last_word_end,
    "end_time": total_duration,
    "color": [0, 0, 0],
    "pixels": 4,
    "effects": []
})

# Save the sequence to a JSON file
output_path = 'sequence_projects/you_know_me/word_flash_sequence.json'
with open(output_path, 'w') as f:
    json.dump(sequence, f, indent=2)

print(f"Created sequence with {len(segments)} segments")
print(f"Saved to {output_path}")