"""
Sequence Maker - Buddy Exporter

Exports a ZIP-based .smbuddy bundle for the SequenceMakerBuddy Android app.
The bundle contains a sequence.json file and the audio file, making it a
single self-contained file to transfer to the phone.

ZIP contents:
  sequence.json  - The sequence data (balls, metadata)
  audio.<ext>    - The audio file (mp3, wav, etc.) if one is loaded

JSON format inside sequence.json:
{
    "format": "sequence_maker_buddy",
    "version": 2,
    "project_name": "...",
    "audio_filename": "audio.mp3",
    "refresh_rate": 100,
    "balls": [
        {
            "name": "Ball 1",
            "default_pixels": 4,
            "sequence": { "0": [255, 0, 0], "1": [0, 255, 0], ... }
        },
        ...
    ]
}
"""

import os
import json
import logging
import zipfile
import shutil


class BuddyExporter:
    """Exports a combined sequence bundle for the SequenceMakerBuddy Android app."""

    def __init__(self, app):
        self.logger = logging.getLogger("SequenceMaker.BuddyExporter")
        self.app = app

    def export_project(self, file_path):
        """
        Export all timelines as a ZIP-based .smbuddy bundle containing
        sequence.json and the audio file.

        Args:
            file_path (str): Path to save the .smbuddy ZIP file.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            project = self.app.project_manager.current_project
            if not project:
                self.logger.warning("Cannot export: No project loaded")
                return False

            # Determine audio info
            audio_path = project.audio_file if project.audio_file else None
            audio_entry_name = None
            if audio_path and os.path.isfile(audio_path):
                ext = os.path.splitext(audio_path)[1]  # e.g. ".mp3"
                audio_entry_name = f"audio{ext}"

            # Build the JSON bundle
            bundle = {
                "format": "sequence_maker_buddy",
                "version": 2,
                "project_name": project.name,
                "audio_filename": audio_entry_name,
                "refresh_rate": 100,
                "balls": []
            }

            for timeline in project.timelines:
                # Get 1000Hz data from timeline
                json_data_1000hz = timeline.to_json_sequence()

                # Convert to 100Hz and simplify (just color arrays, no pixels wrapper)
                sequence_100hz = {}
                for time_key_1000hz, segment_data in json_data_1000hz.get("sequence", {}).items():
                    time_key_100hz = str(int(round(int(time_key_1000hz) / 10)))
                    # Solid segments have "color", fade segments have "start_color"/"end_color"
                    color = segment_data.get("color") or segment_data.get("start_color", [0, 0, 0])
                    sequence_100hz[time_key_100hz] = color

                ball_data = {
                    "name": timeline.name,
                    "default_pixels": json_data_1000hz.get("default_pixels", 4),
                    "sequence": sequence_100hz
                }
                bundle["balls"].append(ball_data)

            # Write ZIP file
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add sequence JSON
                json_bytes = json.dumps(bundle, indent=2).encode('utf-8')
                zf.writestr("sequence.json", json_bytes)

                # Add audio file if available
                if audio_path and audio_entry_name and os.path.isfile(audio_path):
                    zf.write(audio_path, audio_entry_name)

            self.logger.info(f"Exported buddy bundle to {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting buddy bundle: {e}")
            return False


def create_bundle_from_json_files(json_files, output_path, project_name="My Sequence",
                                   audio_file=None):
    """
    Standalone utility: Create a .smbuddy ZIP bundle from existing per-ball JSON files.

    Args:
        json_files (list): List of paths to Ball_N.json files (in order).
        output_path (str): Path to save the .smbuddy file.
        project_name (str): Name of the project.
        audio_file (str): Path to the audio file to include (full path).

    Returns:
        bool: True if successful.
    """
    # Determine audio entry name
    audio_entry_name = None
    if audio_file and os.path.isfile(audio_file):
        ext = os.path.splitext(audio_file)[1]
        audio_entry_name = f"audio{ext}"

    bundle = {
        "format": "sequence_maker_buddy",
        "version": 2,
        "project_name": project_name,
        "audio_filename": audio_entry_name,
        "refresh_rate": 100,
        "balls": []
    }

    for i, json_path in enumerate(json_files):
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Simplify: just store color arrays keyed by time
        sequence = {}
        for time_key, segment in data.get("sequence", {}).items():
            color = segment.get("color") or segment.get("start_color", [0, 0, 0])
            sequence[time_key] = color

        ball_data = {
            "name": f"Ball {i + 1}",
            "default_pixels": data.get("default_pixels", 4),
            "sequence": sequence
        }
        bundle["balls"].append(ball_data)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        json_bytes = json.dumps(bundle, indent=2).encode('utf-8')
        zf.writestr("sequence.json", json_bytes)

        if audio_file and audio_entry_name and os.path.isfile(audio_file):
            zf.write(audio_file, audio_entry_name)

    print(f"Created buddy bundle: {output_path}")
    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python buddy_exporter.py <output.smbuddy> <ball1.json> [ball2.json] [ball3.json] [--audio path/to/song.mp3]")
        sys.exit(1)

    output = sys.argv[1]
    audio = None
    files = []

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--audio" and i + 1 < len(sys.argv):
            audio = sys.argv[i + 1]
            i += 2
        else:
            files.append(sys.argv[i])
            i += 1

    create_bundle_from_json_files(files, output, audio_file=audio)
