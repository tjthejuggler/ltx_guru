"""
Test file for the refactored LLM components.

This file demonstrates how to use the refactored LLM components.
"""

import unittest
from unittest.mock import MagicMock, patch

from app.llm import (
    LLMManager, LLMConfig, LLMToolManager, 
    LLMResponseProcessor, LLMTracker,
    LLMError, LLMConfigError
)
from app.llm.api_clients import (
    BaseLLMClient, OpenAIClient, AnthropicClient, LocalClient
)


class TestLLMRefactored(unittest.TestCase):
    """Test the refactored LLM components."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock app
        self.app = MagicMock()
        self.app.config.get.return_value = {}
        
        # Create instances of the components
        self.llm_config = LLMConfig(self.app)
        self.llm_manager = LLMManager(self.app)
    
    def test_llm_config(self):
        """Test the LLMConfig class."""
        # Test profile management
        self.llm_config.add_profile(
            "Test Profile",
            provider="openai",
            api_key="test_key",
            model="gpt-3.5-turbo"
        )
        
        profiles = self.llm_config.get_profiles()
        self.assertIn("test_profile", profiles)
        
        # Test active profile
        self.llm_config.set_active_profile("test_profile")
        self.assertEqual(self.llm_config.get_active_profile(), "test_profile")
    
    @patch('app.llm.api_clients.openai_client.OpenAIClient.send_request')
    def test_llm_manager_send_request(self, mock_send_request):
        """Test the LLMManager.send_request method."""
        # Mock the API client
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Test response"
                    }
                }
            ],
            "usage": {
                "total_tokens": 10
            }
        }
        mock_send_request.return_value = mock_response
        
        # Configure the LLM manager
        self.llm_manager.config.provider = "openai"
        self.llm_manager.config.api_key = "test_key"
        self.llm_manager.config.model = "gpt-3.5-turbo"
        self.llm_manager.config.enabled = True
        
        # Connect to signals
        response_received = MagicMock()
        self.llm_manager.llm_response_received.connect(response_received)
        
        # Send a request
        self.llm_manager.send_request("Test prompt")
        
        # Wait for the request to complete
        import time
        time.sleep(0.1)
        
        # Check that the API client was called
        mock_send_request.assert_called_once()
        
        # Check that the signal was emitted
        response_received.assert_called_once()
    
    def test_response_processor(self):
        """Test the LLMResponseProcessor class."""
        processor = LLMResponseProcessor()
        
        # Test extracting response text
        response = {
            "choices": [
                {
                    "message": {
                        "content": "Test response"
                    }
                }
            ]
        }
        text = processor._extract_response_text(response)
        self.assertEqual(text, "Test response")
        
        # Test parsing actions
        action_text = """
        Here's what I'll do:
        
        [ACTION:create_segment]
        timeline_index=0
        start_time=1.0
        end_time=2.0
        color=[255, 0, 0]
        [/ACTION]
        """
        actions = processor.parse_actions(action_text)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["type"], "create_segment")
        self.assertEqual(actions[0]["parameters"]["timeline_index"], "0")
    
    def test_tool_manager(self):
        """Test the LLMToolManager class."""
        tool_manager = LLMToolManager(self.app)
        
        # Test registering and executing actions
        mock_handler = MagicMock(return_value={"result": "success"})
        tool_manager.register_action_handler("test_action", mock_handler)
        
        result = tool_manager.execute_action("test_action", {"param": "value"})
        self.assertEqual(result, {"result": "success"})
        mock_handler.assert_called_once_with({"param": "value"})
    
    def test_tracker(self):
        """Test the LLMTracker class."""
        tracker = LLMTracker(self.app, self.llm_config)
        
        # Test tracking token usage
        response = {
            "usage": {
                "total_tokens": 100
            }
        }
        tokens, cost = tracker.track_token_usage(response)
        self.assertEqual(tokens, 100)
        self.assertEqual(tracker.token_usage, 100)


if __name__ == "__main__":
    unittest.main()