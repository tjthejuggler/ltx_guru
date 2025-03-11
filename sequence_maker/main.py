#!/usr/bin/env python3
"""
Sequence Maker - Main Entry Point

A tool for creating color sequences for LTX juggling balls.
"""

import sys
import os
import argparse
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.application import SequenceMakerApp


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Sequence Maker - A tool for creating color sequences for LTX juggling balls')
    parser.add_argument('--project', type=str, help='Load a project file on startup')
    parser.add_argument('--audio', type=str, help='Load an audio file on startup')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Create and run the application
    app = SequenceMakerApp(
        project_file=args.project,
        audio_file=args.audio,
        debug_mode=args.debug
    )
    
    exit_code = app.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()