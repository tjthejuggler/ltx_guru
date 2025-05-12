"""
Examples for LTX Sequence Maker

This package provides example scripts demonstrating how to use the LTX Sequence Maker
to create color sequences for LTX juggling balls.
"""

# List of example modules
__all__ = [
    'basic_analysis',
    'beat_patterns',
    'section_themes',
    'multiple_balls',
    'simple_sequence'
]

# Example descriptions
EXAMPLES = {
    'basic_analysis': 'Demonstrates how to analyze an audio file and extract musical features',
    'beat_patterns': 'Demonstrates how to create beat-synchronized color patterns',
    'section_themes': 'Demonstrates how to create section-based color themes',
    'multiple_balls': 'Demonstrates how to create sequences for multiple juggling balls',
    'simple_sequence': 'Demonstrates how to create simple color sequences without audio analysis'
}

def list_examples():
    """
    Print a list of available examples with descriptions.
    """
    print("Available Examples:")
    print("==================")
    
    for name, description in EXAMPLES.items():
        print(f"{name}: {description}")
    
    print("\nTo run an example, use:")
    print("python -m examples.<example_name> /path/to/audio.mp3")
    print("\nFor example:")
    print("python -m examples.basic_analysis /path/to/audio.mp3")

if __name__ == "__main__":
    list_examples()