"""
Sequence Maker - Key Mapping Model

This module defines the KeyMapping class, which represents a keyboard mapping configuration.
"""

import logging
import copy


class KeyMapping:
    """
    Represents a keyboard mapping configuration.
    
    A key mapping defines which keys correspond to which colors and timelines.
    """
    
    def __init__(self, name="Default Mapping"):
        """
        Initialize a new key mapping.
        
        Args:
            name (str, optional): Mapping name. Defaults to "Default Mapping".
        """
        self.logger = logging.getLogger("SequenceMaker.KeyMapping")
        
        self.name = name
        self.mappings = {}
        self.effect_modifiers = {
            "shift": "strobe",
            "ctrl": "fade",
            "alt": "custom"
        }
    
    def to_dict(self):
        """
        Convert the key mapping to a dictionary for serialization.
        
        Returns:
            dict: Key mapping data as a dictionary.
        """
        # Convert mappings to a serializable format
        mapping_dict = {}
        for key, mapping in self.mappings.items():
            mapping_dict[key] = {
                "color": list(mapping["color"]),
                "timelines": mapping["timelines"],
                "modifiers": mapping.get("modifiers", [])
            }
        
        return {
            "name": self.name,
            "mappings": mapping_dict,
            "effectModifiers": self.effect_modifiers
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a key mapping from a dictionary.
        
        Args:
            data (dict): Key mapping data as a dictionary.
        
        Returns:
            KeyMapping: A new KeyMapping instance.
        """
        key_mapping = cls(name=data["name"])
        
        # Load mappings
        for key, mapping in data["mappings"].items():
            key_mapping.mappings[key] = {
                "color": tuple(mapping["color"]),
                "timelines": mapping["timelines"],
                "modifiers": mapping.get("modifiers", [])
            }
        
        # Load effect modifiers
        if "effectModifiers" in data:
            key_mapping.effect_modifiers = data["effectModifiers"]
        
        return key_mapping
    
    def add_mapping(self, key, color, timelines, modifiers=None):
        """
        Add a key mapping.
        
        Args:
            key (str): Key name.
            color (tuple): RGB color tuple.
            timelines (list): List of timeline indices.
            modifiers (list, optional): List of modifier keys. Defaults to None.
        """
        self.mappings[key] = {
            "color": color,
            "timelines": timelines,
            "modifiers": modifiers or []
        }
    
    def remove_mapping(self, key):
        """
        Remove a key mapping.
        
        Args:
            key (str): Key name.
        
        Returns:
            bool: True if the mapping was removed, False if it wasn't found.
        """
        if key in self.mappings:
            del self.mappings[key]
            return True
        return False
    
    def get_mapping(self, key):
        """
        Get a key mapping.
        
        Args:
            key (str): Key name.
        
        Returns:
            dict: Mapping data, or None if the key isn't mapped.
        """
        return self.mappings.get(key)
    
    def get_keys_for_timeline(self, timeline_index):
        """
        Get all keys mapped to a specific timeline.
        
        Args:
            timeline_index (int): Timeline index.
        
        Returns:
            list: List of key names.
        """
        return [
            key for key, mapping in self.mappings.items()
            if timeline_index in mapping["timelines"]
        ]
    
    def get_keys_for_color(self, color):
        """
        Get all keys mapped to a specific color.
        
        Args:
            color (tuple): RGB color tuple.
        
        Returns:
            list: List of key names.
        """
        return [
            key for key, mapping in self.mappings.items()
            if mapping["color"] == color
        ]
    
    def set_effect_modifier(self, modifier, effect_type):
        """
        Set an effect modifier.
        
        Args:
            modifier (str): Modifier key name (e.g., "shift", "ctrl", "alt").
            effect_type (str): Effect type.
        """
        self.effect_modifiers[modifier] = effect_type
    
    def get_effect_for_modifier(self, modifier):
        """
        Get the effect type for a modifier key.
        
        Args:
            modifier (str): Modifier key name.
        
        Returns:
            str: Effect type, or None if the modifier isn't mapped.
        """
        return self.effect_modifiers.get(modifier)
    
    def copy(self):
        """
        Create a copy of the key mapping.
        
        Returns:
            KeyMapping: A new KeyMapping instance with the same properties.
        """
        new_mapping = KeyMapping(name=f"{self.name} (Copy)")
        new_mapping.mappings = copy.deepcopy(self.mappings)
        new_mapping.effect_modifiers = copy.deepcopy(self.effect_modifiers)
        return new_mapping
    
    def clear(self):
        """Clear all mappings."""
        self.mappings = {}
    
    @classmethod
    def create_default(cls):
        """
        Create a default key mapping.
        
        Returns:
            KeyMapping: A new KeyMapping instance with default mappings.
        """
        from app.constants import DEFAULT_KEY_MAPPING, EFFECT_MODIFIERS
        
        key_mapping = cls(name="Default")
        
        # Add default mappings
        for key, mapping in DEFAULT_KEY_MAPPING.items():
            key_mapping.add_mapping(
                key=key,
                color=mapping["color"],
                timelines=mapping["timelines"]
            )
        
        # Set default effect modifiers
        key_mapping.effect_modifiers = EFFECT_MODIFIERS.copy()
        
        return key_mapping