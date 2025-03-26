"""
Sequence Maker - LLM Customization Models

This module defines classes for LLM customization, including presets and task templates.
"""

import logging
import json
from datetime import datetime


class LLMPreset:
    """Class representing an LLM configuration preset."""
    
    def __init__(self, name, provider, model, temperature, max_tokens, top_p=1.0,
                 frequency_penalty=0.0, presence_penalty=0.0, enable_thinking=False,
                 thinking_budget=1024):
        """
        Initialize the LLM preset.
        
        Args:
            name (str): Preset name.
            provider (str): LLM provider (openai, anthropic, local).
            model (str): Model name.
            temperature (float): Temperature parameter.
            max_tokens (int): Maximum tokens in the response.
            top_p (float, optional): Top-p parameter. Default is 1.0.
            frequency_penalty (float, optional): Frequency penalty parameter. Default is 0.0.
            presence_penalty (float, optional): Presence penalty parameter. Default is 0.0.
            enable_thinking (bool, optional): Whether to enable Anthropic's extended thinking. Default is False.
            thinking_budget (int, optional): Token budget for Anthropic's extended thinking. Default is 1024.
        """
        self.name = name
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.enable_thinking = enable_thinking
        self.thinking_budget = thinking_budget
    
    def to_dict(self):
        """Convert preset to dictionary."""
        return {
            "name": self.name,
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "enable_thinking": self.enable_thinking,
            "thinking_budget": self.thinking_budget
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create preset from dictionary."""
        return cls(
            name=data.get("name", "Unnamed"),
            provider=data.get("provider", "openai"),
            model=data.get("model", "gpt-3.5-turbo"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 1024),
            top_p=data.get("top_p", 1.0),
            frequency_penalty=data.get("frequency_penalty", 0.0),
            presence_penalty=data.get("presence_penalty", 0.0),
            enable_thinking=data.get("enable_thinking", False),
            thinking_budget=data.get("thinking_budget", 1024)
        )


class LLMTaskTemplate:
    """Class representing an LLM task template."""
    
    def __init__(self, name, prompt, description=""):
        """
        Initialize the LLM task template.
        
        Args:
            name (str): Template name.
            prompt (str): Template prompt.
            description (str, optional): Template description. Default is empty.
        """
        self.name = name
        self.prompt = prompt
        self.description = description
    
    def to_dict(self):
        """Convert template to dictionary."""
        return {
            "name": self.name,
            "prompt": self.prompt,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create template from dictionary."""
        return cls(
            name=data.get("name", "Unnamed"),
            prompt=data.get("prompt", ""),
            description=data.get("description", "")
        )


def create_default_presets():
    """Create default LLM presets."""
    return [
        LLMPreset(
            name="Default",
            provider="openai",
            model="gpt-4-turbo",
            temperature=0.7,
            max_tokens=1024
        ),
        LLMPreset(
            name="Creative",
            provider="openai",
            model="gpt-4-turbo",
            temperature=1.0,
            max_tokens=1024
        ),
        LLMPreset(
            name="Precise",
            provider="openai",
            model="gpt-4-turbo",
            temperature=0.3,
            max_tokens=1024
        ),
        LLMPreset(
            name="Claude Default",
            provider="anthropic",
            model="claude-3-opus-20240229",
            temperature=0.7,
            max_tokens=1024
        )
    ]


def create_default_templates():
    """Create default LLM task templates."""
    return [
        LLMTaskTemplate(
            name="Create Beat-Synchronized Pattern",
            prompt="Create a color pattern that changes on every beat of the music. Use bright colors for strong beats and darker colors for weak beats.",
            description="Synchronizes color changes with the beat of the music"
        ),
        LLMTaskTemplate(
            name="Create Mood-Based Sequence",
            prompt="Analyze the mood of the music and create a color sequence that matches it. Use warm colors for happy/energetic sections and cool colors for calm/sad sections.",
            description="Creates a sequence based on the mood of the music"
        ),
        LLMTaskTemplate(
            name="Create Rainbow Cycle",
            prompt="Create a sequence that cycles through the colors of the rainbow (red, orange, yellow, green, blue, indigo, violet) at regular intervals.",
            description="Creates a rainbow color cycle"
        ),
        LLMTaskTemplate(
            name="Create Complementary Colors Pattern",
            prompt="Create a sequence that alternates between complementary colors (colors opposite each other on the color wheel).",
            description="Creates a pattern using complementary colors"
        )
    ]