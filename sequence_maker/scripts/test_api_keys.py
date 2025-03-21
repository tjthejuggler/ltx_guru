#!/usr/bin/env python3
"""
Test API Keys for Sequence Maker

This script tests the API keys for the lyrics processing feature.
It verifies that the keys are valid and working.
"""

import os
import json
import sys
import requests

def load_api_keys():
    """Load API keys from config file."""
    # Define the path to the API keys file
    api_keys_path = os.path.expanduser("~/.sequence_maker/api_keys.json")
    
    # Check if file exists
    if not os.path.exists(api_keys_path):
        print(f"Error: API keys file not found at {api_keys_path}")
        print("Please run setup_api_keys.py first.")
        return None
    
    # Load API keys
    try:
        with open(api_keys_path, 'r') as f:
            api_keys = json.load(f)
        
        return api_keys
    except Exception as e:
        print(f"Error loading API keys: {e}")
        return None

def test_genius_api(api_key):
    """Test Genius API key."""
    print("Testing Genius API key...")
    
    url = "https://api.genius.com/search"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    params = {
        "q": "Bohemian Rhapsody"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            print("✅ Genius API key is valid!")
            return True
        else:
            print(f"❌ Genius API key is invalid. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error testing Genius API key: {e}")
        return False

def test_acr_cloud_api(access_key, secret_key, host):
    """Test ACRCloud API keys."""
    print("Testing ACRCloud API keys...")
    
    # Check if keys are present
    if not access_key or not secret_key or not host:
        print("❌ ACRCloud API keys are incomplete.")
        return False
    
    # Test the API by making a simple request
    try:
        import base64
        import hashlib
        import hmac
        import time
        
        # Prepare request
        http_method = "POST"
        http_uri = "/v1/identify"
        data_type = "fingerprint"
        signature_version = "1"
        timestamp = str(int(time.time()))
        
        # Generate signature
        string_to_sign = http_method + "\n" + http_uri + "\n" + access_key + "\n" + data_type + "\n" + signature_version + "\n" + timestamp
        sign = base64.b64encode(hmac.new(secret_key.encode('utf-8'), string_to_sign.encode('utf-8'), digestmod=hashlib.sha1).digest()).decode('utf-8')
        
        # Prepare request data
        data = {
            'access_key': access_key,
            'data_type': data_type,
            'signature': sign,
            'signature_version': signature_version,
            'timestamp': timestamp,
            'sample_bytes': 0,  # No audio data, just testing the API key
            'sample': ''
        }
        
        # Send request
        url = f"https://{host}{http_uri}"
        response = requests.post(url, data=data)
        
        # Check response
        if response.status_code == 200:
            # The API key is valid if we get a 200 response
            # Even though we'll get an error about missing audio data
            print("✅ ACRCloud API keys are valid!")
            print("Note: Full validation requires an audio file.")
            return True
        else:
            print(f"❌ ACRCloud API keys are invalid. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error testing ACRCloud API keys: {e}")
        return False

def main():
    """Main function."""
    print("Sequence Maker - API Keys Test")
    print("=============================")
    print()
    
    # Load API keys
    api_keys = load_api_keys()
    if not api_keys:
        sys.exit(1)
    
    # Test Genius API
    genius_api_key = api_keys.get("genius_api_key", "")
    genius_valid = test_genius_api(genius_api_key)
    
    # Test ACRCloud API
    acr_access_key = api_keys.get("acr_access_key", "")
    acr_secret_key = api_keys.get("acr_secret_key", "")
    acr_host = api_keys.get("acr_host", "")
    acr_valid = test_acr_cloud_api(acr_access_key, acr_secret_key, acr_host)
    
    # Summary
    print()
    print("Summary:")
    print(f"- Genius API: {'Valid' if genius_valid else 'Invalid'}")
    print(f"- ACRCloud API: {'Present' if acr_valid else 'Invalid'}")
    
    if genius_valid and acr_valid:
        print()
        print("All API keys are valid! You can now use the lyrics processing feature.")
    else:
        print()
        print("Some API keys are invalid. Please update them using setup_api_keys.py.")

if __name__ == "__main__":
    main()