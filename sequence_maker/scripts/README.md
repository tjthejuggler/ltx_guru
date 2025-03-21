# Sequence Maker Scripts

This directory contains utility scripts for Sequence Maker.

## API Keys Setup

### setup_api_keys.py

This script helps you set up your API keys for the lyrics processing feature. It creates the necessary directory structure and configuration file.

Usage:
```
python setup_api_keys.py
```

### test_api_keys.py

This script tests your API keys to ensure they are valid and working.

Usage:
```
python test_api_keys.py
```

## Gentle Docker Container

### start_gentle.py

This script starts the Gentle Docker container for lyrics alignment.

Usage:
```
python start_gentle.py
```

## Requirements

These scripts require the following Python packages:
- requests
- lyricsgenius (for lyrics processing)

You can install them using pip:
```
pip install requests lyricsgenius
```

## Docker

The Gentle alignment service requires Docker to be installed on your system. You can download Docker from [https://www.docker.com/get-started](https://www.docker.com/get-started).