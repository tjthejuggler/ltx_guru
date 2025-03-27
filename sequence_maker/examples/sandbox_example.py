"""
Sequence Maker - Sandbox Example

This example demonstrates how to use the Python sandbox for creating complex light sequences.
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication

# Add parent directory to path to import sequence_maker modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sequence_maker.app.application import Application
from sequence_maker.app.llm.sandbox_manager import SandboxManager


def main():
    """
    Main function to demonstrate the sandbox functionality.
    """
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("SandboxExample")
    
    # Create application
    app = QApplication(sys.argv)
    sequence_maker_app = Application()
    
    # Create sandbox manager
    sandbox_manager = SandboxManager(sequence_maker_app)
    
    # Example 1: Simple color sequence
    logger.info("Example 1: Simple color sequence")
    
    # Define code for a simple color sequence
    code1 = """
    # Create a simple alternating color sequence
    colors = [
        [255, 0, 0],    # Red
        [0, 255, 0],    # Green
        [0, 0, 255]     # Blue
    ]
    
    # Create segments for each beat
    for i, beat_time in enumerate(BEAT_TIMES):
        # Get color (cycle through colors)
        color_index = i % len(colors)
        color = colors[color_index]
        
        # Create segment
        create_segment(0, beat_time, beat_time + 0.25, color)
    
    # Return summary
    segments_created = len(BEAT_TIMES)
    """
    
    # Define context with beat times
    context1 = {
        "BEAT_TIMES": [1.0, 2.0, 3.0, 4.0, 5.0],
        "NUM_BALLS": 3,
        "SONG_DURATION": 10.0
    }
    
    # Execute the code
    result1 = sandbox_manager.execute_sandboxed_code(code1, context1)
    
    # Print the result
    logger.info(f"Result 1: {result1}")
    
    # Example 2: Rainbow pattern
    logger.info("Example 2: Rainbow pattern")
    
    # Define code for a rainbow pattern
    code2 = """
    # Create a rainbow pattern across all beats
    for i, beat_time in enumerate(BEAT_TIMES):
        # Calculate hue based on position in beat sequence
        hue = (i / len(BEAT_TIMES)) * 360
        
        # Create segments for each ball with different hue offsets
        for ball in range(NUM_BALLS):
            offset_hue = (hue + (ball * 30)) % 360
            ball_color = hsv_to_rgb(offset_hue, 1.0, 1.0)
            create_segment(ball, beat_time, beat_time + 0.25, ball_color)
    
    # Return summary
    segments_created = len(BEAT_TIMES) * NUM_BALLS
    """
    
    # Execute the code
    result2 = sandbox_manager.execute_sandboxed_code(code2, context1)
    
    # Print the result
    logger.info(f"Result 2: {result2}")
    
    # Example 3: Fade pattern
    logger.info("Example 3: Fade pattern")
    
    # Define code for a fade pattern
    code3 = """
    # Create a fade pattern
    base_color = [255, 0, 0]  # Red
    
    for i, beat_time in enumerate(BEAT_TIMES):
        # Skip the last beat
        if i == len(BEAT_TIMES) - 1:
            continue
        
        # Get current and next beat time
        current_beat = beat_time
        next_beat = BEAT_TIMES[i + 1]
        duration = next_beat - current_beat
        
        # Create fade segments
        steps = 5
        step_duration = duration / steps
        
        for step in range(steps):
            # Calculate fade factor (0 to 1)
            fade_factor = step / (steps - 1)
            
            # Interpolate between colors
            faded_color = interpolate_color(base_color, [0, 0, 0], fade_factor)
            
            # Calculate segment times
            start_time = current_beat + (step * step_duration)
            end_time = current_beat + ((step + 1) * step_duration)
            
            # Create segment
            create_segment(0, start_time, end_time, faded_color)
    
    # Return summary
    segments_created = (len(BEAT_TIMES) - 1) * 5
    """
    
    # Execute the code
    result3 = sandbox_manager.execute_sandboxed_code(code3, context1)
    
    # Print the result
    logger.info(f"Result 3: {result3}")
    
    # Example 4: Error handling
    logger.info("Example 4: Error handling")
    
    # Define code with an error
    code4 = """
    # Code with an error
    for i in range(10):
        # This will cause an error because timeline_index is out of range
        create_segment(99, i, i + 1, [255, 0, 0])
    """
    
    # Execute the code
    result4 = sandbox_manager.execute_sandboxed_code(code4, context1)
    
    # Print the result
    logger.info(f"Result 4: {result4}")
    
    logger.info("Examples completed")


if __name__ == "__main__":
    main()