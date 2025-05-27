#!/usr/bin/env python3
"""
Test suite for Pattern Templates functionality

This test suite verifies that pattern templates are correctly expanded
into concrete effects with proper timing, ball selection, and parameters.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to allow importing the pattern_templates module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pattern_templates import (
    expand_warning_then_event_pattern,
    expand_lyric_highlight_pattern,
    expand_beat_sync_pattern,
    expand_pattern_templates,
    find_word_timestamps
)

class TestPatternTemplates(unittest.TestCase):
    """Test cases for pattern templates functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_lyrics_data = {
            "song_title": "Test Song",
            "artist_name": "Test Artist",
            "raw_lyrics": "love is all you need, love conquers all",
            "word_timestamps": [
                {"word": "love", "start": 10.0, "end": 10.4},
                {"word": "is", "start": 10.5, "end": 10.6},
                {"word": "all", "start": 10.7, "end": 10.9},
                {"word": "you", "start": 11.0, "end": 11.2},
                {"word": "need", "start": 11.3, "end": 11.6},
                {"word": "love", "start": 20.0, "end": 20.4},
                {"word": "conquers", "start": 20.5, "end": 21.0},
                {"word": "all", "start": 21.1, "end": 21.3},
                {"word": "heart", "start": 30.0, "end": 30.4},
                {"word": "soul", "start": 35.0, "end": 35.3}
            ]
        }
        
        self.sample_audio_analysis = {
            "beats": [5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0]
        }
    
    def test_find_word_timestamps(self):
        """Test finding word timestamps in lyrics data."""
        # Test case-insensitive matching (default)
        love_timestamps = find_word_timestamps(self.sample_lyrics_data, "love", case_sensitive=False)
        self.assertEqual(love_timestamps, [10.0, 20.0])
        
        # Test case-sensitive matching
        love_timestamps_sensitive = find_word_timestamps(self.sample_lyrics_data, "Love", case_sensitive=True)
        self.assertEqual(love_timestamps_sensitive, [])
        
        # Test word that doesn't exist
        missing_timestamps = find_word_timestamps(self.sample_lyrics_data, "missing", case_sensitive=False)
        self.assertEqual(missing_timestamps, [])
        
        # Test single occurrence
        heart_timestamps = find_word_timestamps(self.sample_lyrics_data, "heart", case_sensitive=False)
        self.assertEqual(heart_timestamps, [30.0])
    
    def test_warning_then_event_pattern_lyric_trigger(self):
        """Test WarningThenEvent pattern with lyric trigger."""
        pattern_config = {
            "id": "test_pattern",
            "pattern_type": "WarningThenEvent",
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
        }
        
        effects = expand_warning_then_event_pattern(pattern_config, self.sample_lyrics_data)
        
        # Should generate 4 effects: 2 warnings + 2 main events
        self.assertEqual(len(effects), 4)
        
        # Check first warning effect
        warning1 = effects[0]
        self.assertEqual(warning1["id"], "warning_test_pattern_0")
        self.assertEqual(warning1["type"], "solid_color")
        self.assertEqual(warning1["timing"]["start_seconds"], 9.5)  # 10.0 - 0.5
        self.assertEqual(warning1["timing"]["duration_seconds"], 0.2)
        self.assertEqual(warning1["target_ball"], 1)
        
        # Check first main event
        event1 = effects[1]
        self.assertEqual(event1["id"], "event_test_pattern_0")
        self.assertEqual(event1["type"], "solid_color")
        self.assertEqual(event1["timing"]["start_seconds"], 10.0)
        self.assertEqual(event1["timing"]["duration_seconds"], 0.4)
        self.assertEqual(event1["target_ball"], 1)
        
        # Check second warning effect (should use ball 2 due to round_robin)
        warning2 = effects[2]
        self.assertEqual(warning2["target_ball"], 2)
        self.assertEqual(warning2["timing"]["start_seconds"], 19.5)  # 20.0 - 0.5
        
        # Check second main event
        event2 = effects[3]
        self.assertEqual(event2["target_ball"], 2)
        self.assertEqual(event2["timing"]["start_seconds"], 20.0)
    
    def test_warning_then_event_pattern_custom_times(self):
        """Test WarningThenEvent pattern with custom times trigger."""
        pattern_config = {
            "id": "custom_pattern",
            "pattern_type": "WarningThenEvent",
            "params": {
                "trigger_type": "custom_times",
                "custom_times": [15.0, 25.0, 35.0],
                "warning_offset_seconds": -1.0,
                "target_ball_selection_strategy": "ball_1",
                "event_definition": {
                    "type": "fade",
                    "params": {
                        "duration_seconds": 2.0
                    }
                },
                "warning_definition": {
                    "type": "strobe",
                    "params": {
                        "duration_seconds": 0.8
                    }
                }
            }
        }
        
        effects = expand_warning_then_event_pattern(pattern_config, self.sample_lyrics_data)
        
        # Should generate 6 effects: 3 warnings + 3 main events
        self.assertEqual(len(effects), 6)
        
        # All effects should target ball 1
        for effect in effects:
            self.assertEqual(effect["target_ball"], 1)
        
        # Check timing
        self.assertEqual(effects[0]["timing"]["start_seconds"], 14.0)  # 15.0 - 1.0
        self.assertEqual(effects[1]["timing"]["start_seconds"], 15.0)
        self.assertEqual(effects[2]["timing"]["start_seconds"], 24.0)  # 25.0 - 1.0
        self.assertEqual(effects[3]["timing"]["start_seconds"], 25.0)
    
    def test_lyric_highlight_pattern(self):
        """Test LyricHighlight pattern."""
        pattern_config = {
            "id": "highlight_pattern",
            "pattern_type": "LyricHighlight",
            "params": {
                "target_words": ["love", "heart", "soul"],
                "target_ball_selection_strategy": "round_robin",
                "case_sensitive": False,
                "effect_definition": {
                    "type": "snap_on_flash_off",
                    "params": {
                        "duration_seconds": 0.6
                    }
                }
            }
        }
        
        effects = expand_lyric_highlight_pattern(pattern_config, self.sample_lyrics_data)
        
        # Should find: love (10.0, 20.0), heart (30.0), soul (35.0) = 4 effects
        self.assertEqual(len(effects), 4)
        
        # Check ball cycling (round_robin)
        expected_balls = [1, 2, 3, 4]  # love, love, heart, soul
        for i, effect in enumerate(effects):
            self.assertEqual(effect["target_ball"], expected_balls[i])
        
        # Check timestamps
        expected_times = [10.0, 20.0, 30.0, 35.0]
        for i, effect in enumerate(effects):
            self.assertEqual(effect["timing"]["start_seconds"], expected_times[i])
    
    def test_beat_sync_pattern(self):
        """Test BeatSync pattern."""
        pattern_config = {
            "id": "beat_pattern",
            "pattern_type": "BeatSync",
            "params": {
                "beat_type": "all_beats",
                "target_ball_selection_strategy": "round_robin",
                "time_window": {
                    "start_seconds": 6.0,
                    "end_seconds": 9.0
                },
                "effect_definition": {
                    "type": "pulse_on_beat",
                    "params": {
                        "duration_seconds": 0.1
                    }
                }
            }
        }
        
        effects = expand_beat_sync_pattern(pattern_config, self.sample_audio_analysis)
        
        # Should find beats at: 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0 (7 beats in window 6.0-9.0)
        self.assertEqual(len(effects), 7)
        
        # Check ball cycling
        expected_balls = [1, 2, 3, 4, 1, 2, 3]
        for i, effect in enumerate(effects):
            self.assertEqual(effect["target_ball"], expected_balls[i])
        
        # Check timestamps
        expected_times = [6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0]
        for i, effect in enumerate(effects):
            self.assertEqual(effect["timing"]["start_seconds"], expected_times[i])
    
    def test_expand_pattern_templates_integration(self):
        """Test the full pattern templates expansion process."""
        seqdesign_data = {
            "metadata": {
                "title": "Test Sequence",
                "total_duration_seconds": 60.0
            },
            "effects_timeline": [
                {
                    "id": "base_effect",
                    "type": "solid_color",
                    "timing": {"start_seconds": 0.0, "end_seconds": 60.0},
                    "params": {"color": {"name": "blue"}}
                }
            ],
            "pattern_templates": [
                {
                    "id": "love_warnings",
                    "pattern_type": "WarningThenEvent",
                    "params": {
                        "trigger_type": "lyric",
                        "trigger_lyric": "love",
                        "warning_offset_seconds": -0.3,
                        "target_ball_selection_strategy": "round_robin",
                        "event_definition": {
                            "type": "solid_color",
                            "params": {"color": {"name": "red"}, "duration_seconds": 0.4}
                        },
                        "warning_definition": {
                            "type": "solid_color",
                            "params": {"color": {"name": "yellow"}, "duration_seconds": 0.2}
                        }
                    }
                },
                {
                    "id": "emotional_highlights",
                    "pattern_type": "LyricHighlight",
                    "params": {
                        "target_words": ["heart"],
                        "target_ball_selection_strategy": "ball_3",
                        "effect_definition": {
                            "type": "snap_on_flash_off",
                            "params": {"duration_seconds": 0.5}
                        }
                    }
                }
            ]
        }
        
        # Create temporary lyrics file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_lyrics_data, f)
            lyrics_file = f.name
        
        try:
            # Expand patterns
            expanded_data = expand_pattern_templates(seqdesign_data, lyrics_file)
            
            # Check that pattern_templates section was removed
            self.assertNotIn("pattern_templates", expanded_data)
            
            # Check that effects were added to effects_timeline
            effects_timeline = expanded_data["effects_timeline"]
            
            # Should have: 1 original + 4 from love_warnings + 1 from emotional_highlights = 6 total
            self.assertEqual(len(effects_timeline), 6)
            
            # Check that original effect is still there
            original_effect = next(e for e in effects_timeline if e["id"] == "base_effect")
            self.assertIsNotNone(original_effect)
            
            # Check that warning effects were created
            warning_effects = [e for e in effects_timeline if e["id"].startswith("warning_")]
            self.assertEqual(len(warning_effects), 2)
            
            # Check that main event effects were created
            event_effects = [e for e in effects_timeline if e["id"].startswith("event_")]
            self.assertEqual(len(event_effects), 2)
            
            # Check that highlight effect was created
            highlight_effects = [e for e in effects_timeline if e["id"].startswith("highlight_")]
            self.assertEqual(len(highlight_effects), 1)
            self.assertEqual(highlight_effects[0]["target_ball"], 3)  # ball_3 strategy
            
        finally:
            # Clean up temporary file
            os.unlink(lyrics_file)
    
    def test_ball_selection_strategies(self):
        """Test different ball selection strategies."""
        pattern_config = {
            "id": "test_pattern",
            "pattern_type": "WarningThenEvent",
            "params": {
                "trigger_type": "custom_times",
                "custom_times": [10.0, 20.0, 30.0, 40.0, 50.0],
                "warning_offset_seconds": -0.5,
                "event_definition": {"type": "solid_color", "params": {"duration_seconds": 0.4}},
                "warning_definition": {"type": "solid_color", "params": {"duration_seconds": 0.2}}
            }
        }
        
        # Test round_robin strategy
        pattern_config["params"]["target_ball_selection_strategy"] = "round_robin"
        effects = expand_warning_then_event_pattern(pattern_config, self.sample_lyrics_data)
        expected_balls = [1, 1, 2, 2, 3, 3, 4, 4, 1, 1]  # warning, event pairs
        for i, effect in enumerate(effects):
            self.assertEqual(effect["target_ball"], expected_balls[i])
        
        # Test specific ball strategy
        pattern_config["params"]["target_ball_selection_strategy"] = "ball_2"
        effects = expand_warning_then_event_pattern(pattern_config, self.sample_lyrics_data)
        for effect in effects:
            self.assertEqual(effect["target_ball"], 2)
        
        # Test random strategy (should be deterministic based on index)
        pattern_config["params"]["target_ball_selection_strategy"] = "random"
        effects = expand_warning_then_event_pattern(pattern_config, self.sample_lyrics_data)
        expected_random_balls = [1, 1, 2, 2, 3, 3, 4, 4, 1, 1]  # (i % 4) + 1 pattern
        for i, effect in enumerate(effects):
            self.assertEqual(effect["target_ball"], expected_random_balls[i])

if __name__ == "__main__":
    unittest.main()