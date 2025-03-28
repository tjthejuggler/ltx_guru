"""
Comprehensive tests for the improved LLM sandboxing functionality.

This test suite implements Phase 4 of the LLM improved sandboxing plan,
focusing on testing all aspects of the sandbox improvements.
"""

import unittest
import logging
from unittest.mock import MagicMock, patch

from app.llm.sandbox_manager import SandboxManager
from app.llm.llm_manager import LLMManager
from app.llm.tool_manager import LLMToolManager


class TestLLMImprovedSandboxing(unittest.TestCase):
    """Test suite for the improved LLM sandboxing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Configure logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
        # Create a mock app
        self.app = MagicMock()
        
        # Create mock managers
        self.app.timeline_manager = MagicMock()
        self.app.audio_analysis_manager = MagicMock()
        self.app.project_manager = MagicMock()
        self.app.lyrics_manager = MagicMock()
        
        # Create mock project with lyrics
        self.mock_project = MagicMock()
        self.app.project_manager.current_project = self.mock_project
        self.mock_lyrics = MagicMock()
        self.mock_project.lyrics = self.mock_lyrics
        
        # Create mock timelines
        self.mock_timelines = [MagicMock() for _ in range(3)]
        self.app.timeline_manager.get_timelines.return_value = self.mock_timelines
        self.app.timeline_manager.get_timeline.side_effect = lambda idx: self.mock_timelines[idx] if 0 <= idx < len(self.mock_timelines) else None
        
        # Create instances of the components
        self.sandbox_manager = SandboxManager(self.app)
        self.tool_manager = LLMToolManager(self.app)
        self.llm_manager = LLMManager(self.app)
        
        # Set up word timestamps for testing
        self.word_timestamps = [
            MagicMock(word="hello", start=1.0, end=1.5),
            MagicMock(word="world", start=2.0, end=2.5),
            MagicMock(word="test", start=3.0, end=3.5),
            MagicMock(word="hello", start=4.0, end=4.5),
        ]
        self.mock_lyrics.word_timestamps = self.word_timestamps
    
    def test_1_create_segment_for_word(self):
        """Test 1: Create segments for a specific word."""
        # Mock the _handle_get_word_timestamps method
        word_timestamps_result = {
            "success": True,
            "word_timestamps": [
                {"word": "hello", "start": 1.0, "end": 1.5, "duration": 0.5},
                {"word": "hello", "start": 4.0, "end": 4.5, "duration": 0.5}
            ],
            "count": 2
        }
        
        with patch.object(self.llm_manager, '_handle_get_word_timestamps', return_value=word_timestamps_result):
            with patch.object(self.app.timeline_action_api, 'create_segment', return_value={"success": True}):
                # Call the function
                parameters = {"word": "hello", "color": "red", "balls": [0, 1]}
                result = self.llm_manager._handle_create_segment_for_word(parameters)
                
                # Check the result
                self.assertTrue(result["success"])
                self.assertEqual(self.app.timeline_action_api.create_segment.call_count, 4)
    
    def test_2_alternating_pattern(self):
        """Test 2: Create an alternating pattern using the sandbox."""
        # Define test code
        code = """
        # Create an alternating pattern of red and blue segments
        colors = [[255, 0, 0], [0, 0, 255]]  # Red and blue
        duration = 0.5  # Each segment is 0.5 seconds
        
        # Clear timeline 0 first
        clear_timeline(0)
        
        # Create 10 segments with alternating colors
        for i in range(10):
            start_time = i * duration
            end_time = start_time + duration
            color = colors[i % 2]  # Alternate between red and blue
            create_segment(0, start_time, end_time, color)
        """
        
        # Execute the code
        result = self.sandbox_manager.execute_sandboxed_code(code, {"NUM_BALLS": 3})
        
        # Check the result
        self.assertTrue(result["success"])
        self.mock_timelines[0].clear.assert_called_once()
        self.assertEqual(self.app.timeline_manager.add_segment.call_count, 10)
    
    def test_3_clear_timeline_with_missing_argument(self):
        """Test 3: Test clear_timeline with missing argument."""
        # Mock the _handle_function_call method
        with patch.object(self.tool_manager, '_handle_function_call') as mock_handle_function_call:
            # Set up the mock to first return an error, then a success
            mock_handle_function_call.side_effect = [
                {"success": False, "error": "Missing required parameter: timeline_index"},
                {"success": True, "message": "Timeline 2 cleared."}
            ]
            
            # Mock the send_request method
            with patch.object(self.llm_manager, 'send_request') as mock_send_request:
                # Call the function with missing argument
                self.llm_manager._process_response("I'll clear the timeline", "clear_timeline", "{}")
                
                # Check that the error was detected and a retry was attempted
                self.assertEqual(mock_handle_function_call.call_count, 1)
                self.assertEqual(mock_send_request.call_count, 1)
                
                # Now simulate the LLM's corrected response
                self.llm_manager._process_response("I'll clear timeline 2", "clear_timeline", '{"timeline_index": 2}')
                
                # Check that the function was called again with the correct argument
                self.assertEqual(mock_handle_function_call.call_count, 2)
    
    def test_4_clear_timeline_with_correct_argument(self):
        """Test 4: Test clear_timeline with correct argument."""
        # Define test code
        code = "result = clear_timeline(1)"
        
        # Execute the code
        result = self.sandbox_manager.execute_sandboxed_code(code, {"NUM_BALLS": 3})
        
        # Check the result
        self.assertTrue(result["success"])
        self.mock_timelines[1].clear.assert_called_once()
    
    def test_5_complex_code_with_print(self):
        """Test 5: Test complex code with print statements."""
        # Define test code
        code = """
        # Get all word timestamps
        all_words = get_all_word_timestamps()
        
        # Create segments for each occurrence of "hello"
        hello_words = [w for w in all_words if w["word"] == "hello"]
        
        # Use random utilities to generate colors
        for i, word in enumerate(hello_words):
            hue = random_randint(0, 360)
            color = hsv_to_rgb(hue, 1.0, 1.0)
            
            for ball in range(NUM_BALLS):
                create_segment(ball, word["start_time"], word["end_time"], color)
        """
        
        # Mock the get_all_word_timestamps function
        with patch.object(self.sandbox_manager, '_create_safe_wrappers') as mock_create_safe_wrappers:
            # Create a mock for safe_get_all_word_timestamps
            mock_safe_get_all_word_timestamps = MagicMock(return_value=[
                {"word": "hello", "start_time": 1.0, "end_time": 1.5},
                {"word": "world", "start_time": 2.0, "end_time": 2.5},
                {"word": "hello", "start_time": 4.0, "end_time": 4.5}
            ])
            
            # Return a dictionary with our mock function
            mock_create_safe_wrappers.return_value = {
                "get_all_word_timestamps": mock_safe_get_all_word_timestamps,
                "create_segment": self.sandbox_manager._create_safe_wrappers()["create_segment"],
                "clear_timeline": self.sandbox_manager._create_safe_wrappers()["clear_timeline"],
                "modify_segment": self.sandbox_manager._create_safe_wrappers()["modify_segment"],
                "delete_segment": self.sandbox_manager._create_safe_wrappers()["delete_segment"],
                "get_word_timestamps": self.sandbox_manager._create_safe_wrappers()["get_word_timestamps"]
            }
            
            # Execute the code
            result = self.sandbox_manager.execute_sandboxed_code(code, {"NUM_BALLS": 3})
            
            # Check the result
            self.assertTrue(result["success"])
            mock_safe_get_all_word_timestamps.assert_called_once()
            self.assertEqual(self.app.timeline_manager.add_segment.call_count, 6)
    
    def test_6_restricted_imports(self):
        """Test 6: Test that restricted imports are blocked."""
        # Define test code with restricted import
        code = """
        import random
        number = random.randint(1, 10)
        """
        
        # Execute the code
        result = self.sandbox_manager.execute_sandboxed_code(code, {})
        
        # Check the result
        self.assertFalse(result["success"])
        self.assertIn("ImportError", result["error_message"])
    
    def test_7_random_utilities(self):
        """Test 7: Test the random utilities provided in the sandbox."""
        # Define test code
        code = """
        number = random_randint(1, 10)
        choice = random_choice(["red", "green", "blue"])
        value = random_uniform(0.0, 1.0)
        """
        
        # Execute the code
        result = self.sandbox_manager.execute_sandboxed_code(code, {})
        
        # Check the result
        self.assertTrue(result["success"])
        self.assertIn("variables", result)
        self.assertIsInstance(result["variables"].get("number"), int)
        self.assertIsInstance(result["variables"].get("choice"), str)
        self.assertIsInstance(result["variables"].get("value"), float)
    
    def test_8_edge_cases(self):
        """Test 8: Test edge cases (empty timelines, no lyrics)."""
        # Mock empty timelines
        self.app.timeline_manager.get_timelines.return_value = []
        self.app.timeline_manager.get_timeline.return_value = None
        
        # Define test code
        code = """
        try:
            result = create_segment(0, 1.0, 2.0, [255, 0, 0])
            success = True
        except Exception as e:
            error = str(e)
            success = False
        """
        
        # Execute the code
        result = self.sandbox_manager.execute_sandboxed_code(code, {"NUM_BALLS": 0})
        
        # Check the result
        self.assertTrue(result["success"])
        self.assertIn("variables", result)
        self.assertFalse(result["variables"].get("success"))
    
    def test_9_error_handling_loop(self):
        """Test 9: Test the error handling loop."""
        # Mock the _handle_function_call method
        with patch.object(self.tool_manager, '_handle_function_call') as mock_handle_function_call:
            # Set up the mock to first return an error, then a success
            mock_handle_function_call.side_effect = [
                {"success": False, "error": "Invalid color format"},
                {"success": True, "message": "Segment created successfully."}
            ]
            
            # Mock the send_request method
            with patch.object(self.llm_manager, 'send_request') as mock_send_request:
                # Call the function with invalid color
                self.llm_manager._process_response(
                    "I'll create a segment with an invalid color",
                    "create_segment",
                    '{"timeline_index": 0, "start_time": 1.0, "end_time": 2.0, "color": "invalid"}'
                )
                
                # Check that the error was detected and a retry was attempted
                self.assertEqual(mock_handle_function_call.call_count, 1)
                self.assertEqual(mock_send_request.call_count, 1)
                
                # Now simulate the LLM's corrected response
                self.llm_manager._process_response(
                    "I'll create a segment with a valid color",
                    "create_segment",
                    '{"timeline_index": 0, "start_time": 1.0, "end_time": 2.0, "color": [255, 0, 0]}'
                )
                
                # Check that the function was called again with the correct arguments
                self.assertEqual(mock_handle_function_call.call_count, 2)


if __name__ == "__main__":
    unittest.main()
