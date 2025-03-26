"""
Sequence Maker - LLM Configuration

This module defines the LLMConfig class for managing LLM profiles and configuration.
"""

import logging
from app.constants import DEFAULT_LLM_TEMPERATURE, DEFAULT_LLM_MAX_TOKENS


class LLMConfig:
    """
    Manages LLM profiles and configuration.
    """
    
    def __init__(self, app):
        """
        Initialize the LLM configuration manager.
        
        Args:
            app: The main application instance.
        """
        self.logger = logging.getLogger("SequenceMaker.LLMConfig")
        self.app = app
        
        # Load configuration from app config
        self.enabled = app.config.get("llm", "enabled")
        self.active_profile = app.config.get("llm", "active_profile", "default")
        self.profiles = app.config.get("llm", "profiles", {})
        
        # Current profile settings
        self.provider = None
        self.api_key = None
        self.model = None
        self.temperature = None
        self.max_tokens = None
        self.top_p = None
        self.frequency_penalty = None
        self.presence_penalty = None
        
        # Load active profile settings
        self._load_active_profile()
        
        # Migrate legacy settings if needed
        self._migrate_legacy_settings_if_needed()
    
    def is_configured(self):
        """
        Check if the LLM is properly configured.
        
        Returns:
            bool: True if configured, False otherwise.
        """
        return (
            self.enabled and
            self.provider and
            self.api_key and
            self.model
        )
    
    def get_profiles(self):
        """
        Get all available LLM profiles.
        
        Returns:
            dict: Dictionary of profile configurations.
        """
        return self.profiles
    
    def get_profile_names(self):
        """
        Get names of all available profiles.
        
        Returns:
            list: List of profile names.
        """
        return list(self.profiles.keys())
    
    def get_active_profile(self):
        """
        Get the active profile name.
        
        Returns:
            str: Name of the active profile.
        """
        return self.active_profile
    
    def set_active_profile(self, profile_name):
        """
        Set the active profile.
        
        Args:
            profile_name (str): Name of the profile to activate.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if profile_name in self.profiles:
            self.active_profile = profile_name
            self.app.config.set("llm", "active_profile", profile_name)
            self.app.config.save()
            self._load_active_profile()
            return True
        return False
    
    def add_profile(self, name, provider="", api_key="", model="", temperature=0.7,
                   max_tokens=1024, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
        """
        Add a new LLM profile.
        
        Args:
            name (str): Profile name.
            provider (str): LLM provider.
            api_key (str): API key.
            model (str): Model name.
            temperature (float): Temperature parameter.
            max_tokens (int): Maximum tokens.
            top_p (float): Top-p parameter.
            frequency_penalty (float): Frequency penalty.
            presence_penalty (float): Presence penalty.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        profile_id = name.lower().replace(" ", "_")
        
        # Check if profile already exists
        if profile_id in self.profiles:
            return False
            
        # Create profile
        self.profiles[profile_id] = {
            "name": name,
            "provider": provider,
            "api_key": api_key,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty
        }
        
        # Save to config
        self.app.config.set("llm", "profiles", self.profiles)
        self.app.config.save()
        
        return True
    
    def update_profile(self, profile_id, **kwargs):
        """
        Update an existing LLM profile.
        
        Args:
            profile_id (str): ID of the profile to update.
            **kwargs: Profile settings to update.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if profile_id not in self.profiles:
            return False
        
        # Update profile settings
        for key, value in kwargs.items():
            if key in self.profiles[profile_id]:
                self.profiles[profile_id][key] = value
        
        # Save to config
        self.app.config.set("llm", "profiles", self.profiles)
        self.app.config.save()
        
        # Reload active profile if it was updated
        if profile_id == self.active_profile:
            self._load_active_profile()
        
        return True
    
    def delete_profile(self, profile_id):
        """
        Delete an LLM profile.
        
        Args:
            profile_id (str): ID of the profile to delete.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if profile_id not in self.profiles:
            return False
        
        # Cannot delete the active profile
        if profile_id == self.active_profile:
            return False
        
        # Delete profile
        del self.profiles[profile_id]
        
        # Save to config
        self.app.config.set("llm", "profiles", self.profiles)
        self.app.config.save()
        
        return True
    
    def _load_active_profile(self):
        """
        Load settings from the active profile.
        """
        if self.active_profile in self.profiles:
            profile = self.profiles[self.active_profile]
            self.provider = profile.get("provider", "")
            self.api_key = profile.get("api_key", "")
            self.model = profile.get("model", "")
            self.temperature = profile.get("temperature", DEFAULT_LLM_TEMPERATURE)
            self.max_tokens = profile.get("max_tokens", DEFAULT_LLM_MAX_TOKENS)
            self.top_p = profile.get("top_p", 1.0)
            self.frequency_penalty = profile.get("frequency_penalty", 0.0)
            self.presence_penalty = profile.get("presence_penalty", 0.0)
        else:
            # Create default profile if it doesn't exist
            if not self.profiles:
                self.add_profile(
                    "Default",
                    temperature=DEFAULT_LLM_TEMPERATURE,
                    max_tokens=DEFAULT_LLM_MAX_TOKENS
                )
                self.active_profile = "default"
                self._load_active_profile()
    
    def _migrate_legacy_settings_if_needed(self):
        """
        Migrate legacy settings to the new profile-based system.
        """
        # Check if we have legacy settings
        legacy_provider = self.app.config.get("llm", "provider", None)
        legacy_api_key = self.app.config.get("llm", "api_key", None)
        legacy_model = self.app.config.get("llm", "model", None)
        
        if legacy_provider and legacy_api_key and legacy_model:
            self.logger.info("Migrating legacy LLM settings to profile system")
            
            # Create a profile from legacy settings
            self.add_profile(
                "Migrated Settings",
                provider=legacy_provider,
                api_key=legacy_api_key,
                model=legacy_model,
                temperature=self.app.config.get("llm", "temperature", DEFAULT_LLM_TEMPERATURE),
                max_tokens=self.app.config.get("llm", "max_tokens", DEFAULT_LLM_MAX_TOKENS)
            )
            
            # Set as active profile
            self.set_active_profile("migrated_settings")
            
            # Remove legacy settings by setting them to empty values
            # Since there's no remove method, we'll just set them to empty values
            self.app.config.set("llm", "provider", "")
            self.app.config.set("llm", "api_key", "")
            self.app.config.set("llm", "model", "")
            self.app.config.set("llm", "temperature", DEFAULT_LLM_TEMPERATURE)
            self.app.config.set("llm", "max_tokens", DEFAULT_LLM_MAX_TOKENS)
            self.app.config.save()