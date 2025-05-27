#!/usr/bin/env python3
"""
Pattern Templates Example

This example demonstrates how to use Pattern Templates to create sophisticated
sequence designs with minimal manual effect creation.
"""

import json
import os
import sys

def create_example_seqdesign_with_patterns():
    """Create an example .seqdesign.json file with pattern templates."""
    
    seqdesign_data = {
        "metadata": {
            "title": "Pattern Templates Demo Sequence",
            "audio_file_path": "demo_song.mp3",
            "total_duration_seconds": 180.0,
            "target_prg_refresh_rate": 100,
            "default_pixels": 4,
            "default_base_color": {"rgb": [10, 10, 30]}
        },
        "effects_timeline": [
            {
                "id": "base_atmosphere",
                "type": "solid_color",
                "description": "Base atmospheric color throughout the song",
                "timing": {
                    "start_seconds": 0.0,
                    "end_seconds": 180.0
                },
                "params": {
                    "color": {"rgb": [10, 10, 30]}
                }
            },
            {
                "id": "intro_fade",
                "type": "fade",
                "description": "Gentle fade in at the beginning",
                "timing": {
                    "start_seconds": 0.0,
                    "end_seconds": 5.0
                },
                "params": {
                    "color_start": {"name": "black"},
                    "color_end": {"rgb": [10, 10, 30]},
                    "steps_per_second": 20
                }
            }
        ],
        "pattern_templates": [
            {
                "id": "love_word_warnings",
                "pattern_type": "WarningThenEvent",
                "description": "Yellow warning flash 0.5 seconds before every 'love' word, followed by red main event",
                "params": {
                    "trigger_type": "lyric",
                    "trigger_lyric": "love",
                    "warning_offset_seconds": -0.5,
                    "target_ball_selection_strategy": "round_robin",
                    "case_sensitive": False,
                    "event_definition": {
                        "type": "solid_color",
                        "params": {
                            "color": {"name": "red"},
                            "duration_seconds": 0.4
                        }
                    },
                    "warning_definition": {
                        "type": "solid_color",
                        "params": {
                            "color": {"name": "yellow"},
                            "duration_seconds": 0.2
                        }
                    }
                }
            },
            {
                "id": "emotional_highlights",
                "pattern_type": "LyricHighlight",
                "description": "Highlight emotional words with white flash and fade",
                "params": {
                    "target_words": ["heart", "soul", "dream", "hope", "forever"],
                    "target_ball_selection_strategy": "round_robin",
                    "case_sensitive": False,
                    "effect_definition": {
                        "type": "snap_on_flash_off",
                        "params": {
                            "pre_base_color": {"rgb": [10, 10, 30]},
                            "target_color": {"name": "white"},
                            "post_base_color": {"rgb": [10, 10, 30]},
                            "fade_out_duration": 0.8,
                            "duration_seconds": 1.0
                        }
                    }
                }
            },
            {
                "id": "chorus_beat_sync",
                "pattern_type": "BeatSync",
                "description": "Cyan pulses on every beat during the chorus sections",
                "params": {
                    "beat_type": "all_beats",
                    "target_ball_selection_strategy": "round_robin",
                    "time_window": {
                        "start_seconds": 45.0,
                        "end_seconds": 75.0
                    },
                    "effect_definition": {
                        "type": "pulse_on_beat",
                        "params": {
                            "color": {"name": "cyan"},
                            "pulse_duration_seconds": 0.1,
                            "duration_seconds": 0.1
                        }
                    }
                }
            },
            {
                "id": "bridge_beat_sync",
                "pattern_type": "BeatSync",
                "description": "Purple pulses on downbeats during the bridge",
                "params": {
                    "beat_type": "downbeats",
                    "target_ball_selection_strategy": "ball_1",
                    "time_window": {
                        "start_seconds": 120.0,
                        "end_seconds": 150.0
                    },
                    "effect_definition": {
                        "type": "solid_color",
                        "params": {
                            "color": {"rgb": [128, 0, 128]},
                            "duration_seconds": 0.2
                        }
                    }
                }
            },
            {
                "id": "custom_timing_pattern",
                "pattern_type": "WarningThenEvent",
                "description": "Custom timed events with warnings at specific moments",
                "params": {
                    "trigger_type": "custom_times",
                    "custom_times": [30.5, 60.2, 90.8, 150.3],
                    "warning_offset_seconds": -1.0,
                    "target_ball_selection_strategy": "random",
                    "event_definition": {
                        "type": "fade",
                        "params": {
                            "color_start": {"rgb": [10, 10, 30]},
                            "color_end": {"name": "gold"},
                            "duration_seconds": 2.0,
                            "steps_per_second": 25
                        }
                    },
                    "warning_definition": {
                        "type": "strobe",
                        "params": {
                            "color_on": {"name": "orange"},
                            "color_off": {"rgb": [10, 10, 30]},
                            "frequency_hz": 5.0,
                            "duration_seconds": 0.8
                        }
                    }
                }
            }
        ]
    }
    
    return seqdesign_data

def create_example_lyrics():
    """Create example synced lyrics data."""
    
    lyrics_data = {
        "song_title": "Demo Song",
        "artist_name": "Pattern Templates Demo",
        "raw_lyrics": "In my heart there's love forever, dreams of hope and soul together...",
        "word_timestamps": [
            {"word": "in", "start": 10.0, "end": 10.2},
            {"word": "my", "start": 10.3, "end": 10.5},
            {"word": "heart", "start": 10.6, "end": 11.0},
            {"word": "there's", "start": 11.1, "end": 11.4},
            {"word": "love", "start": 11.5, "end": 11.9},
            {"word": "forever", "start": 12.0, "end": 12.6},
            {"word": "dreams", "start": 15.0, "end": 15.4},
            {"word": "of", "start": 15.5, "end": 15.6},
            {"word": "hope", "start": 15.7, "end": 16.0},
            {"word": "and", "start": 16.1, "end": 16.2},
            {"word": "soul", "start": 16.3, "end": 16.7},
            {"word": "together", "start": 16.8, "end": 17.4},
            {"word": "love", "start": 25.2, "end": 25.6},
            {"word": "is", "start": 25.7, "end": 25.8},
            {"word": "the", "start": 25.9, "end": 26.0},
            {"word": "answer", "start": 26.1, "end": 26.6},
            {"word": "heart", "start": 35.1, "end": 35.5},
            {"word": "and", "start": 35.6, "end": 35.7},
            {"word": "soul", "start": 35.8, "end": 36.2},
            {"word": "unite", "start": 36.3, "end": 36.8},
            {"word": "love", "start": 50.3, "end": 50.7},
            {"word": "conquers", "start": 50.8, "end": 51.3},
            {"word": "all", "start": 51.4, "end": 51.7},
            {"word": "hope", "start": 65.2, "end": 65.6},
            {"word": "never", "start": 65.7, "end": 66.1},
            {"word": "dies", "start": 66.2, "end": 66.6},
            {"word": "dream", "start": 80.1, "end": 80.5},
            {"word": "big", "start": 80.6, "end": 80.8},
            {"word": "and", "start": 80.9, "end": 81.0},
            {"word": "love", "start": 81.1, "end": 81.5},
            {"word": "deeper", "start": 81.6, "end": 82.1}
        ]
    }
    
    return lyrics_data

def demonstrate_pattern_expansion():
    """Demonstrate the pattern expansion process."""
    
    print("=== Pattern Templates Example ===\n")
    
    # Create example data
    seqdesign_data = create_example_seqdesign_with_patterns()
    lyrics_data = create_example_lyrics()
    
    # Save example files
    example_dir = "pattern_templates_demo"
    os.makedirs(example_dir, exist_ok=True)
    
    seqdesign_path = os.path.join(example_dir, "demo_with_patterns.seqdesign.json")
    lyrics_path = os.path.join(example_dir, "demo_lyrics.synced_lyrics.json")
    
    with open(seqdesign_path, 'w') as f:
        json.dump(seqdesign_data, f, indent=4)
    
    with open(lyrics_path, 'w') as f:
        json.dump(lyrics_data, f, indent=4)
    
    print(f"Created example files:")
    print(f"  - {seqdesign_path}")
    print(f"  - {lyrics_path}")
    
    # Show pattern templates summary
    print(f"\nPattern Templates in this example:")
    for i, pattern in enumerate(seqdesign_data["pattern_templates"], 1):
        print(f"  {i}. {pattern['id']} ({pattern['pattern_type']})")
        print(f"     Description: {pattern.get('description', 'No description')}")
    
    # Show what would be generated
    print(f"\nExpected expansions:")
    
    # Count love words
    love_count = sum(1 for word in lyrics_data["word_timestamps"] if word["word"].lower() == "love")
    print(f"  - 'love_word_warnings': {love_count} love words → {love_count * 2} effects (warning + main)")
    
    # Count emotional words
    emotional_words = ["heart", "soul", "dream", "hope", "forever"]
    emotional_count = sum(1 for word in lyrics_data["word_timestamps"] 
                         if word["word"].lower() in [w.lower() for w in emotional_words])
    print(f"  - 'emotional_highlights': {emotional_count} emotional words → {emotional_count} effects")
    
    # Custom timing
    custom_times = seqdesign_data["pattern_templates"][4]["params"]["custom_times"]
    print(f"  - 'custom_timing_pattern': {len(custom_times)} custom times → {len(custom_times) * 2} effects")
    
    print(f"\nTo expand these patterns, run:")
    print(f"python -m roocode_sequence_designer_tools.pattern_templates \\")
    print(f"    {seqdesign_path} \\")
    print(f"    {example_dir}/demo_expanded.seqdesign.json \\")
    print(f"    --lyrics-file {lyrics_path}")
    
    print(f"\nThen compile with:")
    print(f"python -m roocode_sequence_designer_tools.compile_seqdesign \\")
    print(f"    {example_dir}/demo_expanded.seqdesign.json \\")
    print(f"    {example_dir}/demo_output.prg.json")

def show_pattern_template_structure():
    """Show the structure of different pattern template types."""
    
    print("\n=== Pattern Template Structures ===\n")
    
    # WarningThenEvent example
    warning_then_event = {
        "id": "example_warning_pattern",
        "pattern_type": "WarningThenEvent",
        "description": "Example warning then event pattern",
        "params": {
            "trigger_type": "lyric",  # or "custom_times", "beat_number"
            "trigger_lyric": "chorus",  # required if trigger_type is "lyric"
            "warning_offset_seconds": -0.8,  # negative means before
            "target_ball_selection_strategy": "round_robin",  # or "ball_1", "ball_2", etc.
            "case_sensitive": False,
            "event_definition": {
                "type": "solid_color",
                "params": {
                    "color": {"name": "red"},
                    "duration_seconds": 0.5
                }
            },
            "warning_definition": {
                "type": "solid_color",
                "params": {
                    "color": {"name": "yellow"},
                    "duration_seconds": 0.3
                }
            }
        }
    }
    
    # LyricHighlight example
    lyric_highlight = {
        "id": "example_highlight_pattern",
        "pattern_type": "LyricHighlight",
        "description": "Example lyric highlight pattern",
        "params": {
            "target_words": ["love", "heart", "soul"],
            "target_ball_selection_strategy": "round_robin",
            "case_sensitive": False,
            "effect_definition": {
                "type": "snap_on_flash_off",
                "params": {
                    "pre_base_color": {"name": "blue"},
                    "target_color": {"name": "white"},
                    "post_base_color": {"name": "blue"},
                    "fade_out_duration": 0.6,
                    "duration_seconds": 0.8
                }
            }
        }
    }
    
    # BeatSync example
    beat_sync = {
        "id": "example_beat_pattern",
        "pattern_type": "BeatSync",
        "description": "Example beat synchronization pattern",
        "params": {
            "beat_type": "all_beats",  # or "downbeats"
            "target_ball_selection_strategy": "round_robin",
            "time_window": {
                "start_seconds": 30.0,
                "end_seconds": 90.0
            },
            "effect_definition": {
                "type": "pulse_on_beat",
                "params": {
                    "color": {"name": "cyan"},
                    "pulse_duration_seconds": 0.1,
                    "duration_seconds": 0.1
                }
            }
        }
    }
    
    print("1. WarningThenEvent Pattern:")
    print(json.dumps(warning_then_event, indent=2))
    
    print("\n2. LyricHighlight Pattern:")
    print(json.dumps(lyric_highlight, indent=2))
    
    print("\n3. BeatSync Pattern:")
    print(json.dumps(beat_sync, indent=2))

if __name__ == "__main__":
    demonstrate_pattern_expansion()
    show_pattern_template_structure()