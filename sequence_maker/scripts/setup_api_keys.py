#!/usr/bin/env python3
"""
Setup API Keys for Sequence Maker

This script helps users set up their API keys for the lyrics processing feature.
It creates the necessary directory structure and configuration file.
"""

import os
import json
import sys

def main():
    """Main function."""
    print("Sequence Maker - API Keys Setup")
    print("===============================")
    print()
    print("This script will help you set up your API keys for the lyrics processing feature.")
    print("You will need API keys from ACRCloud and Genius.")
    print()
    
    # Get API keys from user
    acr_access_key = input("Enter your ACRCloud Access Key: ").strip()
    acr_secret_key = input("Enter your ACRCloud Secret Key: ").strip()
    acr_host = input("Enter your ACRCloud Host URL: ").strip()
    genius_api_key = input("Enter your Genius API Key: ").strip()
    
    # Create config directory
    config_dir = os.path.expanduser("~/.sequence_maker")
    os.makedirs(config_dir, exist_ok=True)
    
    # Create API keys file
    api_keys_path = os.path.join(config_dir, "api_keys.json")
    
    # Check if file already exists
    if os.path.exists(api_keys_path):
        overwrite = input(f"API keys file already exists at {api_keys_path}. Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Aborted.")
            return
    
    # Create API keys data
    api_keys = {
        "acr_access_key": acr_access_key,
        "acr_secret_key": acr_secret_key,
        "acr_host": acr_host,
        "genius_api_key": genius_api_key
    }
    
    # Write API keys to file
    with open(api_keys_path, 'w') as f:
        json.dump(api_keys, f, indent=4)
    
    print()
    print(f"API keys saved to {api_keys_path}")
    print("You can now use the lyrics processing feature in Sequence Maker.")

if __name__ == "__main__":
    main()