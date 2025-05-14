#!/usr/bin/env python3
"""
Test script for the snap_on_flash_off effect.

This script tests the snap_on_flash_off effect implementation
to ensure it works correctly with various parameters.
"""

import unittest
from roocode_sequence_designer_tools.effect_implementations import apply_snap_on_flash_off_effect

class TestSnapOnFlashOffEffect(unittest.TestCase):
    """Test cases for the snap_on_flash_off effect."""

    def setUp(self):
        """Set up test fixtures."""
        self.metadata = {"default_pixels": 4}
        self.basic_params = {
            "pre_base_color": {"name": "blue"},
            "target_color": {"name": "white"},
            "post_base_color": {"name": "blue"},
            "fade_out_duration": 1.5,
            "steps_per_second": 10
        }

    def test_basic_functionality(self):
        """Test basic functionality of the effect."""
        # Apply the effect from 0.0 to 2.0 seconds
        segments = apply_snap_on_flash_off_effect(
            0.0, 2.0, self.basic_params, self.metadata
        )
        
        # Check that segments were generated
        self.assertGreater(len(segments), 0, "No segments were generated")
        
        # Check that the first segment is the flash (target color)
        first_segment = segments[0]
        self.assertEqual(first_segment[0], 0.0, "First segment should start at 0.0")
        self.assertEqual(first_segment[2], (255, 255, 255), "First segment should be white")
        
        # Check that the last segment ends at the effect end time
        last_segment = segments[-1]
        self.assertEqual(last_segment[1], 2.0, "Last segment should end at 2.0")
        
        # Check that the last segment color is close to the post_base_color
        self.assertEqual(last_segment[2], (0, 0, 255), "Last segment should be blue")

    def test_zero_flash_duration(self):
        """Test when fade_out_duration equals total effect duration."""
        params = self.basic_params.copy()
        params["fade_out_duration"] = 2.0  # Same as total effect duration
        
        segments = apply_snap_on_flash_off_effect(
            0.0, 2.0, params, self.metadata
        )
        
        # Check that segments were generated
        self.assertGreater(len(segments), 0, "No segments were generated")
        
        # Check that the first segment starts with the target color
        first_segment = segments[0]
        self.assertEqual(first_segment[0], 0.0, "First segment should start at 0.0")
        self.assertEqual(first_segment[2], (255, 255, 255), "First segment should be white")

    def test_zero_fade_duration(self):
        """Test when fade_out_duration is zero."""
        params = self.basic_params.copy()
        params["fade_out_duration"] = 0.0
        
        segments = apply_snap_on_flash_off_effect(
            0.0, 2.0, params, self.metadata
        )
        
        # Should just be one segment with the target color
        self.assertEqual(len(segments), 1, "Should be exactly one segment")
        self.assertEqual(segments[0][0], 0.0, "Segment should start at 0.0")
        self.assertEqual(segments[0][1], 2.0, "Segment should end at 2.0")
        self.assertEqual(segments[0][2], (255, 255, 255), "Segment should be white")

    def test_different_colors(self):
        """Test with different colors."""
        params = {
            "pre_base_color": {"rgb": [50, 0, 50]},  # Dark purple
            "target_color": {"rgb": [255, 255, 0]},  # Yellow
            "post_base_color": {"rgb": [50, 0, 50]},  # Dark purple
            "fade_out_duration": 1.0,
            "steps_per_second": 20
        }
        
        segments = apply_snap_on_flash_off_effect(
            0.0, 2.0, params, self.metadata
        )
        
        # Check that segments were generated
        self.assertGreater(len(segments), 0, "No segments were generated")
        
        # Check that the first segment is the flash (target color)
        first_segment = segments[0]
        self.assertEqual(first_segment[2], (255, 255, 0), "First segment should be yellow")
        
        # Check that the last segment color is close to the post_base_color
        last_segment = segments[-1]
        self.assertEqual(last_segment[2], (50, 0, 50), "Last segment should be dark purple")

if __name__ == "__main__":
    unittest.main()