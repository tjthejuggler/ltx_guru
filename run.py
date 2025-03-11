#!/usr/bin/env python3
"""
Sequence Maker - Run Script

This script provides a simple way to run the Sequence Maker application.
"""

import sys
import os
import logging
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create log directory if it doesn't exist
log_dir = Path.home() / '.sequence_maker'
log_dir.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_dir / 'sequence_maker.log')
    ]
)

logger = logging.getLogger("SequenceMaker")

def main():
    """Run the Sequence Maker application."""
    try:
        # Clear module cache to ensure fresh imports
        import sys
        import importlib
        for module in list(sys.modules.keys()):
            if module.startswith('sequence_maker'):
                del sys.modules[module]
        
        # Import the main module
        from sequence_maker.main import main as app_main
        
        # Run the application
        app_main()
    
    except ImportError as e:
        logger.error(f"Error importing Sequence Maker: {e}")
        print(f"Error: {e}")
        print("Make sure all dependencies are installed. Run 'pip install -r requirements.txt'.")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error running Sequence Maker: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Run the application
    main()