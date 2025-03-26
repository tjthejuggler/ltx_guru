"""
Sequence Maker - LLM Tracker

This module defines the LLMTracker class for tracking token usage and costs.
"""

import logging
import time
from datetime import datetime


class LLMTracker:
    """
    Tracks token usage, costs, and performance metrics for LLM requests.
    """
    
    def __init__(self, app, config, token_usage_updated_signal=None):
        """
        Initialize the LLM tracker.
        
        Args:
            app: The main application instance.
            config: The LLM configuration instance.
            token_usage_updated_signal: Signal to emit when token usage is updated.
        """
        self.logger = logging.getLogger("SequenceMaker.LLMTracker")
        self.app = app
        self.config = config
        self.token_usage_updated_signal = token_usage_updated_signal
        
        # Token tracking
        self.token_usage = 0
        self.estimated_cost = 0.0
        self.token_prices = {
            "openai": {
                "gpt-3.5-turbo": 0.0015,  # per 1K tokens
                "gpt-4": 0.03,  # per 1K tokens
            },
            "anthropic": {
                "claude-2": 0.01,  # per 1K tokens
                "claude-instant": 0.0025,  # per 1K tokens
            },
            "local": {
                "default": 0.0  # Local models are free
            }
        }
    
    def _get_token_count_from_response(self, response):
        """
        Extract token count from an API response.
        
        Args:
            response (dict): The API response.
            
        Returns:
            int: Token count.
        """
        try:
            if "usage" in response:
                return response["usage"].get("total_tokens", 0)
            
            # For streaming responses, we don't get token counts
            return 0
        except Exception as e:
            self.logger.error(f"Error getting token count: {str(e)}")
            return 0
    
    def track_token_usage(self, response):
        """
        Track token usage from an API response.
        
        Args:
            response (dict): The API response.
            
        Returns:
            tuple: (token_count, cost)
        """
        token_count = self._get_token_count_from_response(response)
        
        if token_count > 0:
            self.token_usage += token_count
            
            # Calculate cost
            provider = self.config.provider.lower()
            model = self.config.model.lower()
            
            # Get price per 1K tokens
            price_per_1k = 0.0
            
            if provider in self.token_prices:
                provider_prices = self.token_prices[provider]
                
                if model in provider_prices:
                    price_per_1k = provider_prices[model]
                elif "default" in provider_prices:
                    price_per_1k = provider_prices["default"]
            
            # Calculate cost for this request
            cost = (token_count / 1000) * price_per_1k
            self.estimated_cost += cost
            
            # Update project metadata
            if hasattr(self.app, 'project_manager') and self.app.project_manager.current_project:
                project = self.app.project_manager.current_project
                
                if not hasattr(project, 'llm_metadata'):
                    project.llm_metadata = {}
                
                project.llm_metadata['token_usage'] = self.token_usage
                project.llm_metadata['estimated_cost'] = self.estimated_cost
                
                # Signal that the project has changed
                self.app.project_manager.project_changed.emit()
            
            # Emit signal if provided
            if self.token_usage_updated_signal:
                self.token_usage_updated_signal.emit(self.token_usage, self.estimated_cost)
            
            return token_count, cost
        
        return 0, 0.0
    
    def _track_performance_metrics(self, start_time, end_time, prompt_length, response_length, tokens):
        """
        Track performance metrics for an LLM request.
        
        Args:
            start_time (float): Request start time.
            end_time (float): Request end time.
            prompt_length (int): Length of the prompt in characters.
            response_length (int): Length of the response in characters.
            tokens (int): Number of tokens used.
        """
        try:
            duration = end_time - start_time
            
            # Calculate metrics
            tokens_per_second = tokens / duration if duration > 0 else 0
            chars_per_token = (prompt_length + response_length) / tokens if tokens > 0 else 0
            
            # Log metrics
            self.logger.info(f"LLM Request Performance:")
            self.logger.info(f"  Duration: {duration:.2f} seconds")
            self.logger.info(f"  Tokens: {tokens}")
            self.logger.info(f"  Tokens per second: {tokens_per_second:.2f}")
            self.logger.info(f"  Characters per token: {chars_per_token:.2f}")
            
            # Store metrics in project metadata
            if hasattr(self.app, 'project_manager') and self.app.project_manager.current_project:
                project = self.app.project_manager.current_project
                
                if not hasattr(project, 'llm_metadata'):
                    project.llm_metadata = {}
                
                if 'performance_metrics' not in project.llm_metadata:
                    project.llm_metadata['performance_metrics'] = []
                
                # Add this request's metrics
                project.llm_metadata['performance_metrics'].append({
                    'timestamp': datetime.now().isoformat(),
                    'duration': duration,
                    'tokens': tokens,
                    'tokens_per_second': tokens_per_second,
                    'chars_per_token': chars_per_token,
                    'prompt_length': prompt_length,
                    'response_length': response_length
                })
                
                # Keep only the last 10 metrics
                if len(project.llm_metadata['performance_metrics']) > 10:
                    project.llm_metadata['performance_metrics'] = project.llm_metadata['performance_metrics'][-10:]
                
                # Signal that the project has changed
                self.app.project_manager.project_changed.emit()
                
        except Exception as e:
            self.logger.error(f"Error tracking performance metrics: {str(e)}")