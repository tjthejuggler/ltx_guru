"""
Sequence Maker - LLM Response Processor

This module defines the LLMResponseProcessor class for parsing and processing LLM responses.
"""

import json
import logging
import re


class LLMResponseProcessor:
    """
    Processes and parses LLM responses.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the LLM response processor.
        
        Args:
            logger (logging.Logger, optional): Logger instance.
        """
        self.logger = logger or logging.getLogger("SequenceMaker.LLMResponseProcessor")
    
    def _extract_response_text(self, response):
        """
        Extract the text content from an LLM response.
        
        Args:
            response (dict): The LLM response.
            
        Returns:
            str: The extracted text.
        """
        try:
            if "choices" in response and len(response["choices"]) > 0:
                choice = response["choices"][0]
                
                # Handle different response formats
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"] or ""
                elif "text" in choice:
                    return choice["text"] or ""
                elif "delta" in choice and "content" in choice["delta"]:
                    return choice["delta"]["content"] or ""
            
            return ""
        except Exception as e:
            self.logger.error(f"Error extracting response text: {str(e)}")
            return ""
    
    def _handle_ambiguity(self, prompt, response_text):
        """
        Check if the response indicates ambiguity and extract suggestions.
        
        Args:
            prompt (str): The original prompt.
            response_text (str): The response text.
            
        Returns:
            tuple: (is_ambiguous, suggestions)
        """
        # Check for ambiguity markers
        ambiguity_markers = [
            "I'm not sure what you're asking",
            "Your request is ambiguous",
            "I could interpret this in several ways",
            "Did you mean",
            "I'm not clear on what you want",
            "This could mean different things",
            "Your request could be interpreted as",
            "I'm unsure about your intent",
            "Could you clarify",
            "I'm not sure if you want"
        ]
        
        is_ambiguous = any(marker.lower() in response_text.lower() for marker in ambiguity_markers)
        
        if is_ambiguous:
            suggestions = self._extract_suggestions(response_text)
            return True, suggestions
        
        return False, []
    
    def _extract_suggestions(self, response_text):
        """
        Extract suggestions from an ambiguous response.
        
        Args:
            response_text (str): The response text.
            
        Returns:
            list: Extracted suggestions.
        """
        suggestions = []
        
        # Look for numbered or bulleted lists
        list_patterns = [
            r'\d+\.\s*(.*?)(?=\n\d+\.|\n\n|$)',  # Numbered lists: 1. Item
            r'•\s*(.*?)(?=\n•|\n\n|$)',          # Bullet lists: • Item
            r'-\s*(.*?)(?=\n-|\n\n|$)',          # Dash lists: - Item
            r'\*\s*(.*?)(?=\n\*|\n\n|$)'         # Asterisk lists: * Item
        ]
        
        for pattern in list_patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            if matches:
                suggestions.extend([match.strip() for match in matches if match.strip()])
        
        # If no structured list is found, try to extract phrases after "Did you mean" or similar
        if not suggestions:
            clarification_patterns = [
                r'Did you mean\s*(.*?)(?=\?|\n|$)',
                r'Do you mean\s*(.*?)(?=\?|\n|$)',
                r'Are you asking\s*(.*?)(?=\?|\n|$)',
                r'Are you trying to\s*(.*?)(?=\?|\n|$)'
            ]
            
            for pattern in clarification_patterns:
                matches = re.findall(pattern, response_text, re.IGNORECASE | re.DOTALL)
                if matches:
                    # Split by "or" if present
                    for match in matches:
                        parts = re.split(r'\s+or\s+', match)
                        suggestions.extend([part.strip() for part in parts if part.strip()])
        
        # Limit to reasonable number of suggestions
        return suggestions[:5]
    
    def parse_actions(self, response_text):
        """
        Parse actions from the response text.
        
        Args:
            response_text (str): The response text.
            
        Returns:
            list: List of parsed actions.
        """
        actions = []
        
        # Look for action blocks in the format:
        # [ACTION:action_type]
        # parameter1=value1
        # parameter2=value2
        # [/ACTION]
        
        action_blocks = re.findall(
            r'\[ACTION:(.*?)\](.*?)\[/ACTION\]',
            response_text,
            re.DOTALL
        )
        
        for action_type, params_text in action_blocks:
            action_type = action_type.strip()
            params = {}
            
            # Parse parameters
            param_lines = params_text.strip().split('\n')
            for line in param_lines:
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    params[key.strip()] = value.strip()
            
            actions.append({
                "type": action_type,
                "parameters": params
            })
        
        return actions
    
    def parse_color_sequence(self, response_text):
        """
        Parse a color sequence from the response text.
        
        Args:
            response_text (str): The response text.
            
        Returns:
            list: List of color segments.
        """
        # First try to extract JSON blocks
        json_blocks = self._extract_json_blocks(response_text)
        
        for block in json_blocks:
            try:
                data = json.loads(block)
                
                # Check if this looks like a color sequence
                if isinstance(data, list) and len(data) > 0:
                    # Check if items have the expected structure
                    if all(isinstance(item, dict) and "start_time" in item and "end_time" in item and "color" in item for item in data):
                        return data
            except json.JSONDecodeError:
                continue
        
        # If no valid JSON blocks, try to parse from text
        return self._parse_sequence_from_text(response_text)
    
    def _extract_json_blocks(self, text):
        """
        Extract JSON blocks from text.
        
        Args:
            text (str): The text to extract JSON blocks from.
            
        Returns:
            list: List of extracted JSON blocks.
        """
        json_blocks = []
        
        # Look for JSON blocks enclosed in triple backticks
        code_blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)```', text)
        
        for block in code_blocks:
            # Clean up the block
            block = block.strip()
            if block:
                json_blocks.append(block)
        
        # Also look for JSON blocks enclosed in square brackets
        bracket_blocks = re.findall(r'\[\s*\n\s*{[\s\S]*?}\s*\n\s*\]', text)
        
        for block in bracket_blocks:
            block = block.strip()
            if block:
                json_blocks.append(block)
        
        return json_blocks
    
    def _parse_sequence_from_text(self, text):
        """
        Parse a color sequence from plain text.
        
        Args:
            text (str): The text to parse.
            
        Returns:
            list: List of color segments.
        """
        segments = []
        
        # Look for lines with time ranges and colors
        # Example: "0:00-0:30: Red" or "0:00 to 0:30: [255, 0, 0]"
        time_color_pattern = r'(\d+:\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+:\d+(?:\.\d+)?)\s*:?\s*(.+?)(?=\n|$)'
        
        matches = re.findall(time_color_pattern, text)
        
        for start_time_str, end_time_str, color_str in matches:
            try:
                # Parse time strings
                start_time = self._parse_time_string(start_time_str)
                end_time = self._parse_time_string(end_time_str)
                
                # Parse color
                color = self._parse_color_string(color_str)
                
                if start_time is not None and end_time is not None and color is not None:
                    segments.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "color": color
                    })
            except Exception as e:
                self.logger.warning(f"Error parsing segment: {str(e)}")
        
        return segments
    
    def _parse_time_string(self, time_str):
        """
        Parse a time string into seconds.
        
        Args:
            time_str (str): Time string in format "MM:SS" or "MM:SS.ms".
            
        Returns:
            float: Time in seconds.
        """
        parts = time_str.split(':')
        
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        
        return None
    
    def _parse_color_string(self, color_str):
        """
        Parse a color string into RGB values.
        
        Args:
            color_str (str): Color string (name or RGB values).
            
        Returns:
            list: RGB values.
        """
        # Check if it's an RGB array
        if '[' in color_str and ']' in color_str:
            try:
                # Extract the array part
                array_str = color_str[color_str.find('['):color_str.find(']')+1]
                color_array = json.loads(array_str)
                
                if isinstance(color_array, list) and len(color_array) == 3:
                    return color_array
            except json.JSONDecodeError:
                pass
        
        # Otherwise, assume it's a color name
        # This will be resolved later by the color utility
        return color_str.strip()