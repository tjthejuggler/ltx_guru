"""
Sequence Maker - Tests for Sandbox Manager

This module contains tests for the SandboxManager class.
"""

import unittest
from unittest.mock import MagicMock, patch
import logging

from app.llm.sandbox_manager import SandboxManager


class TestSandboxManager(unittest.TestCase):
    """
    Tests for the SandboxManager class.
    """
    
    def setUp(self):
        """
        Set up the test environment.
        """
        # Configure logging
        logging.basicConfig(level=logging.DEBUG)
        
        # Create a mock app
        self.app = MagicMock()
        
        # Create a mock timeline manager
        self.app.timeline_manager = MagicMock()
        
        # Create a mock audio analysis manager
        self.app.audio_analysis_manager = MagicMock()
        
        # Create a SandboxManager instance
        self.sandbox_manager = SandboxManager(self.app)
    
    def test_initialization(self):
        """
        Test that the SandboxManager initializes correctly.
        """
        self.assertEqual(self.sandbox_manager.app, self.app)
        self.assertIsNotNone(self.sandbox_manager.logger)
        self.assertGreater(self.sandbox_manager.max_execution_time, 0)
    
    def test_execute_sandboxed_code_success(self):
        """
        Test executing valid code in the sandbox.
        """
        # Define test code
        code = """
        # Simple code to test the sandbox
        result = 2 + 2
        message = "Hello, world!"
        """
        
        # Define available context
        context = {
            "BEAT_TIMES": [1.0, 2.0, 3.0],
            "NUM_BALLS": 3,
            "SONG_DURATION": 10.0
        }
        
        # Execute the code
        result = self.sandbox_manager.execute_sandboxed_code(code, context)
        
        # Check the result
        self.assertTrue(result["success"])
        self.assertIn("variables", result)
        self.assertEqual(result["variables"].get("result"), 4)
        self.assertEqual(result["variables"].get("message"), "Hello, world!")
    
    def test_execute_sandboxed_code_syntax_error(self):
        """
        Test executing code with syntax errors in the sandbox.
        """
        # Define test code with syntax error
        code = """
        # Code with syntax error
        if True
            print("Missing colon")
        """
        
        # Define available context
        context = {}
        
        # Execute the code
        result = self.sandbox_manager.execute_sandboxed_code(code, context)
        
        # Check the result
        self.assertFalse(result["success"])
        self.assertEqual(result["error_type"], "CompilationError")
        self.assertIn("SyntaxError", result["error_message"])
    
    def test_execute_sandboxed_code_runtime_error(self):
        """
        Test executing code with runtime errors in the sandbox.
        """
        # Define test code with runtime error
        code = """
        # Code with runtime error
        1 / 0  # Division by zero
        """
        
        # Define available context
        context = {}
        
        # Execute the code
        result = self.sandbox_manager.execute_sandboxed_code(code, context)
        
        # Check the result
        self.assertFalse(result["success"])
        self.assertEqual(result["error_type"], "ZeroDivisionError")
        self.assertIn("division by zero", result["error_message"])
    
    def test_safe_create_segment(self):
        """
        Test the safe_create_segment wrapper.
        """
        # Set up mock timeline
        mock_timeline = MagicMock()
        self.app.timeline_manager.get_timeline.return_value = mock_timeline
        self.app.timeline_manager.get_timelines.return_value = [mock_timeline]
        
        # Set up mock segment
        mock_segment = MagicMock()
        self.app.timeline_manager.add_segment.return_value = mock_segment
        
        # Define test code
        code = """
        # Test create_segment
        result = create_segment(0, 1.0, 2.0, [255, 0, 0])
        """
        
        # Define available context
        context = {"NUM_BALLS": 1}
        
        # Execute the code
        result = self.sandbox_manager.execute_sandboxed_code(code, context)
        
        # Check the result
        self.assertTrue(result["success"])
        
        # Verify that add_segment was called with the correct arguments
        self.app.timeline_manager.add_segment.assert_called_once()
        call_args = self.app.timeline_manager.add_segment.call_args[0]
        self.assertEqual(call_args[0], mock_timeline)  # timeline
        self.assertEqual(call_args[1], 1.0)  # start_time
        self.assertEqual(call_args[2], 2.0)  # end_time
        self.assertEqual(call_args[3], (255, 0, 0))  # color
    
    def test_safe_clear_timeline(self):
        """
        Test the safe_clear_timeline wrapper.
        """
        # Set up mock timeline with segments
        mock_timeline = MagicMock()
        mock_segment1 = MagicMock()
        mock_segment2 = MagicMock()
        mock_timeline.segments = [mock_segment1, mock_segment2]
        
        self.app.timeline_manager.get_timeline.return_value = mock_timeline
        self.app.timeline_manager.get_timelines.return_value = [mock_timeline]
        
        # Define test code
        code = """
        # Test clear_timeline
        result = clear_timeline(0)
        """
        
        # Define available context
        context = {"NUM_BALLS": 1}
        
        # Execute the code
        result = self.sandbox_manager.execute_sandboxed_code(code, context)
        
        # Check the result
        self.assertTrue(result["success"])
        
        # Verify that remove_segment was called for each segment
        self.assertEqual(self.app.timeline_manager.remove_segment.call_count, 2)
    
    def test_safe_utilities(self):
        """
        Test the safe utility functions.
        """
        # Define test code
        code = """
        # Test utility functions
        random_col = random_color()
        random_val = random_float(0, 1)
        interp_col = interpolate_color([255, 0, 0], [0, 0, 255], 0.5)
        hsv_col = hsv_to_rgb(120, 1.0, 1.0)
        rgb_hsv = rgb_to_hsv(255, 0, 0)
        named_col = color_from_name("blue")
        """
        
        # Define available context
        context = {}
        
        # Execute the code
        result = self.sandbox_manager.execute_sandboxed_code(code, context)
        
        # Check the result
        self.assertTrue(result["success"])
        self.assertIn("variables", result)
        
        # Check random_color result
        self.assertIsInstance(result["variables"].get("random_col"), list)
        self.assertEqual(len(result["variables"].get("random_col")), 3)
        
        # Check random_float result
        self.assertIsInstance(result["variables"].get("random_val"), float)
        self.assertGreaterEqual(result["variables"].get("random_val"), 0)
        self.assertLessEqual(result["variables"].get("random_val"), 1)
        
        # Check interpolate_color result
        self.assertIsInstance(result["variables"].get("interp_col"), list)
        self.assertEqual(len(result["variables"].get("interp_col")), 3)
        
        # Check hsv_to_rgb result
        self.assertIsInstance(result["variables"].get("hsv_col"), list)
        self.assertEqual(len(result["variables"].get("hsv_col")), 3)
        
        # Check rgb_to_hsv result
        self.assertIsInstance(result["variables"].get("rgb_hsv"), list)
        self.assertEqual(len(result["variables"].get("rgb_hsv")), 3)
        
        # Check color_from_name result
        self.assertIsInstance(result["variables"].get("named_col"), list)
        self.assertEqual(len(result["variables"].get("named_col")), 3)
        self.assertEqual(result["variables"].get("named_col"), [0, 0, 255])  # blue
    
    def test_restricted_imports(self):
        """
        Test that restricted imports are blocked.
        """
        # Define test code with restricted import
        code = """
        # Try to import os module
        import os
        path = os.path.join('/', 'etc', 'passwd')
        """
        
        # Define available context
        context = {}
        
        # Execute the code
        result = self.sandbox_manager.execute_sandboxed_code(code, context)
        
        # Check the result
        self.assertFalse(result["success"])
        self.assertIn("ImportError", result["error_message"])
    
    def test_timeout(self):
        """
        Test that code execution times out after max_execution_time.
        """
        # Set a short timeout for the test
        self.sandbox_manager.max_execution_time = 0.1
        
        # Define test code with infinite loop
        code = """
        # Infinite loop
        while True:
            pass
        """
        
        # Define available context
        context = {}
        
        # Execute the code
        result = self.sandbox_manager.execute_sandboxed_code(code, context)
        
        # Check the result
        self.assertFalse(result["success"])
        self.assertEqual(result["error_type"], "TimeoutError")
    
    def test_context_data(self):
        """
        Test that context data is available in the sandbox.
        """
        # Define test code
        code = """
        # Access context data
        beat_count = len(BEAT_TIMES)
        first_beat = BEAT_TIMES[0]
        ball_count = NUM_BALLS
        duration = SONG_DURATION
        """
        
        # Define available context
        context = {
            "BEAT_TIMES": [1.0, 2.0, 3.0],
            "NUM_BALLS": 3,
            "SONG_DURATION": 10.0
        }
        
        # Execute the code
        result = self.sandbox_manager.execute_sandboxed_code(code, context)
        
        # Check the result
        self.assertTrue(result["success"])
        self.assertIn("variables", result)
        self.assertEqual(result["variables"].get("beat_count"), 3)
        self.assertEqual(result["variables"].get("first_beat"), 1.0)
        self.assertEqual(result["variables"].get("ball_count"), 3)
        self.assertEqual(result["variables"].get("duration"), 10.0)


if __name__ == "__main__":
    unittest.main()