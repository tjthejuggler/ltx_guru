#!/usr/bin/env python3
"""
Song Data Manager for Roocode Sequence Designer Tools

Manages persistent per-song data storage. Once lyrics, audio analysis, beat data,
or any other song-related data is gathered, it is saved to a song_data.json file
in the project directory and never needs to be re-gathered unless explicitly requested.

Usage:
    python -m roocode_sequence_designer_tools.song_data_manager <project_dir> <action> [options]

Actions:
    show        - Display current song data summary
    get         - Get a specific data field
    set         - Set a specific data field
    has         - Check if a data field exists
    clear       - Clear a specific data field or all data
    init        - Initialize a new song_data.json with basic metadata
"""

import os
import sys
import json
import argparse
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


SONG_DATA_FILENAME = "song_data.json"


def _get_song_data_path(project_dir: str) -> str:
    """Get the path to the song_data.json file for a project directory."""
    return os.path.join(project_dir, SONG_DATA_FILENAME)


def load_song_data(project_dir: str) -> Dict[str, Any]:
    """
    Load song data from the project directory.

    Args:
        project_dir: Path to the song's project directory.

    Returns:
        Dictionary of song data, or empty dict with metadata if file doesn't exist.
    """
    path = _get_song_data_path(project_dir)
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load {path}: {e}", file=sys.stderr)
            return _create_empty_song_data()
    return _create_empty_song_data()


def save_song_data(project_dir: str, data: Dict[str, Any]) -> str:
    """
    Save song data to the project directory.

    Args:
        project_dir: Path to the song's project directory.
        data: The song data dictionary to save.

    Returns:
        Path to the saved file.
    """
    os.makedirs(project_dir, exist_ok=True)
    data["_last_updated"] = datetime.now(timezone.utc).isoformat()
    path = _get_song_data_path(project_dir)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    return path


def _create_empty_song_data() -> Dict[str, Any]:
    """Create an empty song data structure."""
    return {
        "_version": "1.0",
        "_created": datetime.now(timezone.utc).isoformat(),
        "_last_updated": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "song_title": None,
            "artist_name": None,
            "audio_file": None,
            "duration_seconds": None,
            "genre": None,
        },
        "lyrics": {
            "raw_text": None,
            "raw_text_file": None,
            "synced_lyrics_file": None,
            "synced_lyrics_data": None,
            "word_count": None,
        },
        "audio_analysis": {
            "analysis_report_file": None,
            "estimated_tempo": None,
            "time_signature": None,
            "key": None,
            "beats": None,
            "downbeats": None,
            "sections": None,
            "energy_profile": None,
            "onset_times": None,
            "spectral_features": None,
        },
        "sequences": {},
    }


def has_data(project_dir: str, field_path: str) -> bool:
    """
    Check if a specific data field exists and is not None.

    Args:
        project_dir: Path to the song's project directory.
        field_path: Dot-separated path to the field (e.g., "lyrics.raw_text").

    Returns:
        True if the field exists and is not None.
    """
    data = load_song_data(project_dir)
    return _get_nested(data, field_path) is not None


def get_data(project_dir: str, field_path: str) -> Any:
    """
    Get a specific data field.

    Args:
        project_dir: Path to the song's project directory.
        field_path: Dot-separated path to the field (e.g., "audio_analysis.beats").

    Returns:
        The field value, or None if not found.
    """
    data = load_song_data(project_dir)
    return _get_nested(data, field_path)


def set_data(project_dir: str, field_path: str, value: Any) -> None:
    """
    Set a specific data field and save.

    Args:
        project_dir: Path to the song's project directory.
        field_path: Dot-separated path to the field (e.g., "metadata.song_title").
        value: The value to set.
    """
    data = load_song_data(project_dir)
    _set_nested(data, field_path, value)
    save_song_data(project_dir, data)


def register_sequence_version(
    project_dir: str,
    version_name: str,
    description: str,
    files: Dict[str, str],
    diff_from: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Register a new sequence version for this song.

    Args:
        project_dir: Path to the song's project directory.
        version_name: Short name/identifier for this version (e.g., "v1_beat_pulse").
        description: Human-readable description of what this version does and how
                     it differs from other versions.
        files: Dict mapping file type to relative path, e.g.:
               {"seqdesign": "song_v1.seqdesign.json", "prg": "song_v1.prg.json"}
        diff_from: Optional name of the version this was derived from.
        tags: Optional list of tags for categorization.

    Returns:
        The version entry that was created.
    """
    data = load_song_data(project_dir)
    if "sequences" not in data:
        data["sequences"] = {}

    version_entry = {
        "description": description,
        "created": datetime.now(timezone.utc).isoformat(),
        "files": files,
        "diff_from": diff_from,
        "tags": tags or [],
    }

    data["sequences"][version_name] = version_entry
    save_song_data(project_dir, data)
    return version_entry


def list_sequence_versions(project_dir: str) -> Dict[str, Any]:
    """
    List all registered sequence versions for this song.

    Args:
        project_dir: Path to the song's project directory.

    Returns:
        Dictionary of version_name -> version_entry.
    """
    data = load_song_data(project_dir)
    return data.get("sequences", {})


def get_song_data_summary(project_dir: str) -> str:
    """
    Get a human-readable summary of what data is available for this song.

    Args:
        project_dir: Path to the song's project directory.

    Returns:
        A formatted string summary.
    """
    data = load_song_data(project_dir)
    lines = []
    lines.append(f"=== Song Data Summary for: {project_dir} ===")
    lines.append(f"  Version: {data.get('_version', 'unknown')}")
    lines.append(f"  Last Updated: {data.get('_last_updated', 'never')}")

    # Metadata
    meta = data.get("metadata", {})
    lines.append(f"\n  Metadata:")
    lines.append(f"    Title: {meta.get('song_title', 'N/A')}")
    lines.append(f"    Artist: {meta.get('artist_name', 'N/A')}")
    lines.append(f"    Audio File: {meta.get('audio_file', 'N/A')}")
    lines.append(f"    Duration: {meta.get('duration_seconds', 'N/A')}s")

    # Lyrics
    lyrics = data.get("lyrics", {})
    has_raw = lyrics.get("raw_text") is not None or lyrics.get("raw_text_file") is not None
    has_synced = lyrics.get("synced_lyrics_data") is not None or lyrics.get("synced_lyrics_file") is not None
    lines.append(f"\n  Lyrics:")
    lines.append(f"    Raw Text: {'✓' if has_raw else '✗'}")
    lines.append(f"    Synced/Aligned: {'✓' if has_synced else '✗'}")
    if lyrics.get("word_count"):
        lines.append(f"    Word Count: {lyrics['word_count']}")

    # Audio Analysis
    analysis = data.get("audio_analysis", {})
    lines.append(f"\n  Audio Analysis:")
    lines.append(f"    Report File: {'✓' if analysis.get('analysis_report_file') else '✗'}")
    lines.append(f"    Tempo: {analysis.get('estimated_tempo', 'N/A')}")
    lines.append(f"    Time Signature: {analysis.get('time_signature', 'N/A')}")
    lines.append(f"    Key: {analysis.get('key', 'N/A')}")
    lines.append(f"    Beats: {'✓ (' + str(len(analysis['beats'])) + ')' if analysis.get('beats') else '✗'}")
    lines.append(f"    Downbeats: {'✓ (' + str(len(analysis['downbeats'])) + ')' if analysis.get('downbeats') else '✗'}")
    lines.append(f"    Sections: {'✓ (' + str(len(analysis['sections'])) + ')' if analysis.get('sections') else '✗'}")
    lines.append(f"    Energy Profile: {'✓' if analysis.get('energy_profile') else '✗'}")
    lines.append(f"    Onsets: {'✓' if analysis.get('onset_times') else '✗'}")

    # Sequences
    sequences = data.get("sequences", {})
    lines.append(f"\n  Sequence Versions: {len(sequences)}")
    for name, entry in sequences.items():
        desc = entry.get("description", "No description")
        created = entry.get("created", "unknown")
        diff = entry.get("diff_from")
        tags = entry.get("tags", [])
        lines.append(f"    [{name}] {desc}")
        lines.append(f"      Created: {created}")
        if diff:
            lines.append(f"      Based on: {diff}")
        if tags:
            lines.append(f"      Tags: {', '.join(tags)}")
        files = entry.get("files", {})
        for ftype, fpath in files.items():
            lines.append(f"      {ftype}: {fpath}")

    return "\n".join(lines)


def _get_nested(data: dict, field_path: str) -> Any:
    """Get a value from a nested dict using dot-separated path."""
    keys = field_path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current


def _set_nested(data: dict, field_path: str, value: Any) -> None:
    """Set a value in a nested dict using dot-separated path."""
    keys = field_path.split(".")
    current = data
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Manage persistent per-song data for sequence design projects."
    )
    parser.add_argument("project_dir", help="Path to the song's project directory")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")

    # show
    subparsers.add_parser("show", help="Display current song data summary")

    # get
    get_parser = subparsers.add_parser("get", help="Get a specific data field")
    get_parser.add_argument("field", help="Dot-separated field path (e.g., 'lyrics.raw_text')")

    # set
    set_parser = subparsers.add_parser("set", help="Set a specific data field")
    set_parser.add_argument("field", help="Dot-separated field path")
    set_parser.add_argument("value", help="Value to set (JSON-parsed if possible)")

    # has
    has_parser = subparsers.add_parser("has", help="Check if a data field exists")
    has_parser.add_argument("field", help="Dot-separated field path")

    # clear
    clear_parser = subparsers.add_parser("clear", help="Clear a data field or all data")
    clear_parser.add_argument("--field", help="Dot-separated field path to clear (omit for all)")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize song_data.json")
    init_parser.add_argument("--title", help="Song title")
    init_parser.add_argument("--artist", help="Artist name")
    init_parser.add_argument("--audio-file", help="Audio file path (relative to project dir)")

    # register-version
    rv_parser = subparsers.add_parser("register-version", help="Register a sequence version")
    rv_parser.add_argument("version_name", help="Short version identifier")
    rv_parser.add_argument("--description", required=True, help="Description of this version")
    rv_parser.add_argument("--files", required=True, help="JSON dict of file_type:path pairs")
    rv_parser.add_argument("--diff-from", help="Version this was derived from")
    rv_parser.add_argument("--tags", help="Comma-separated tags")

    # list-versions
    subparsers.add_parser("list-versions", help="List all sequence versions")

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        sys.exit(1)

    project_dir = args.project_dir

    if args.action == "show":
        print(get_song_data_summary(project_dir))

    elif args.action == "get":
        value = get_data(project_dir, args.field)
        if value is None:
            print(f"Field '{args.field}' not found or is None.")
            sys.exit(1)
        print(json.dumps(value, indent=2) if isinstance(value, (dict, list)) else str(value))

    elif args.action == "set":
        # Try to parse value as JSON, fall back to string
        try:
            value = json.loads(args.value)
        except (json.JSONDecodeError, TypeError):
            value = args.value
        set_data(project_dir, args.field, value)
        print(f"Set '{args.field}' successfully.")

    elif args.action == "has":
        exists = has_data(project_dir, args.field)
        print(f"{'yes' if exists else 'no'}")
        sys.exit(0 if exists else 1)

    elif args.action == "clear":
        if args.field:
            set_data(project_dir, args.field, None)
            print(f"Cleared '{args.field}'.")
        else:
            data = _create_empty_song_data()
            save_song_data(project_dir, data)
            print("Cleared all song data.")

    elif args.action == "init":
        data = load_song_data(project_dir)
        if args.title:
            _set_nested(data, "metadata.song_title", args.title)
        if args.artist:
            _set_nested(data, "metadata.artist_name", args.artist)
        if args.audio_file:
            _set_nested(data, "metadata.audio_file", args.audio_file)
        save_song_data(project_dir, data)
        print(f"Initialized {_get_song_data_path(project_dir)}")

    elif args.action == "register-version":
        try:
            files = json.loads(args.files)
        except json.JSONDecodeError:
            print("Error: --files must be valid JSON", file=sys.stderr)
            sys.exit(1)
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        entry = register_sequence_version(
            project_dir, args.version_name, args.description, files, args.diff_from, tags
        )
        print(f"Registered version '{args.version_name}':")
        print(json.dumps(entry, indent=2))

    elif args.action == "list-versions":
        versions = list_sequence_versions(project_dir)
        if not versions:
            print("No sequence versions registered.")
        else:
            for name, entry in versions.items():
                print(f"  [{name}] {entry.get('description', 'No description')}")
                if entry.get("diff_from"):
                    print(f"    Based on: {entry['diff_from']}")
                if entry.get("tags"):
                    print(f"    Tags: {', '.join(entry['tags'])}")


if __name__ == "__main__":
    main()
