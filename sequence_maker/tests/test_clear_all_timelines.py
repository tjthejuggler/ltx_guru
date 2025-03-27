"""
Sequence Maker - Test Clear All Timelines

This module tests the clear_all_timelines functionality.
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.timeline_action_api import TimelineActionAPI
from models.timeline import Timeline
from models.project import Project
from models.segment import TimelineSegment


class TestClearAllTimelines(unittest.TestCase):
    """Test the clear_all_timelines functionality."""

    def setUp(self):
        """Set up the test environment."""
        # Create mock app
        self.app = MagicMock()
        
        # Create mock project manager
        self.app.project_manager = MagicMock()
        
        # Create mock project
        self.project = Project()
        self.project.name = "Test Project"
        self.project.total_duration = 100.0
        
        # Create mock timelines
        self.timeline1 = Timeline()
        self.timeline1.name = "Ball 1"
        self.timeline2 = Timeline()
        self.timeline2.name = "Ball 2"
        self.timeline3 = Timeline()
        self.timeline3.name = "Ball 3"
        
        # Create segments
        segment1 = TimelineSegment(start_time=0, end_time=10, color=(255, 0, 0))
        segment2 = TimelineSegment(start_time=5, end_time=15, color=(0, 255, 0))
        segment3 = TimelineSegment(start_time=10, end_time=20, color=(0, 0, 255))
        
        # Add segments to timelines
        self.timeline1.add_segment(segment1)
        self.timeline2.add_segment(segment2)
        self.timeline3.add_segment(segment3)
        
        # Add timelines to project
        self.project.timelines = [self.timeline1, self.timeline2, self.timeline3]
        
        # Set current project
        self.app.project_manager.current_project = self.project
        
        # Create mock timeline manager
        self.app.timeline_manager = MagicMock()
        
        # Mock the add_segment method to actually add a segment to the timeline
        def mock_add_segment(timeline, start_time, end_time, color, pixels=None):
            segment = TimelineSegment(
                start_time=start_time,
                end_time=end_time,
                color=color,
                pixels=pixels or 4
            )
            timeline.add_segment(segment)
            return segment
            
        self.app.timeline_manager.add_segment = mock_add_segment
        
        # Create mock undo manager
        self.app.undo_manager = MagicMock()
        
        # Create mock audio manager
        self.app.audio_manager = MagicMock()
        self.app.audio_manager.duration = 100.0
        
        # Create timeline action API
        self.timeline_api = TimelineActionAPI(self.app)

    def test_clear_all_timelines(self):
        """Test clearing all timelines."""
        # Verify initial state
        self.assertEqual(len(self.timeline1.segments), 1)
        self.assertEqual(len(self.timeline2.segments), 1)
        self.assertEqual(len(self.timeline3.segments), 1)
        
        # Call clear_all_timelines
        result = self.timeline_api.clear_all_timelines({})
        
        # Verify result
        self.assertTrue(result["success"])
        self.assertEqual(result["timelines_cleared"], 3)
        self.assertTrue(result["set_black"])
        
        # Verify timelines were cleared and black segments were added
        self.assertEqual(len(self.timeline1.segments), 1)  # One black segment
        self.assertEqual(len(self.timeline2.segments), 1)  # One black segment
        self.assertEqual(len(self.timeline3.segments), 1)  # One black segment
        
        # Verify the segments are black and span the entire duration
        for timeline in self.project.timelines:
            self.assertEqual(len(timeline.segments), 1)
            segment = timeline.segments[0]
            self.assertEqual(segment.start_time, 0)
            self.assertEqual(segment.end_time, 100.0)
            self.assertEqual(segment.color, (0, 0, 0))
        
        # Verify undo manager was called
        self.app.undo_manager.save_state.assert_called_once_with("llm_clear_all_timelines")
        
        # Verify timeline_modified signal was emitted for each timeline
        self.assertEqual(self.app.timeline_manager.timeline_modified.emit.call_count, 3)

    def test_clear_all_timelines_without_black(self):
        """Test clearing all timelines without setting black."""
        # Call clear_all_timelines with set_black=False
        result = self.timeline_api.clear_all_timelines({"set_black": False})
        
        # Verify result
        self.assertTrue(result["success"])
        self.assertEqual(result["timelines_cleared"], 3)
        self.assertFalse(result["set_black"])
        
        # Verify timelines were cleared and no black segments were added
        self.assertEqual(len(self.timeline1.segments), 0)
        self.assertEqual(len(self.timeline2.segments), 0)
        self.assertEqual(len(self.timeline3.segments), 0)


if __name__ == '__main__':
    unittest.main()