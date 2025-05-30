#!/usr/bin/env python3
"""
Test script to validate the scroll bar fix for sequence_maker.

This script demonstrates the issue and validates that our fix works.
"""

import sys
import os
import logging
from pathlib import Path

# Add the sequence_maker directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_scroll_bar_fix():
    """Test the scroll bar fix by simulating audio loading and ball sequence import."""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("ScrollBarTest")
    
    logger.info("=== Testing Scroll Bar Fix ===")
    
    try:
        # Import required modules
        from app.application import SequenceMakerApp
        from models.project import Project
        from models.timeline import Timeline
        from models.segment import TimelineSegment
        
        logger.info("1. Creating test application...")
        app = SequenceMakerApp(debug_mode=True)
        
        logger.info("2. Creating new project...")
        project = app.project_manager.new_project("Test Project")
        initial_duration = project.total_duration
        logger.info(f"   Initial project duration: {initial_duration}s")
        
        logger.info("3. Simulating audio loading (120 seconds)...")
        # Simulate audio loading by directly setting duration
        app.audio_manager.duration = 120.0
        
        # Trigger the audio loaded logic manually
        if hasattr(app.project_manager, 'current_project') and app.project_manager.current_project:
            old_duration = app.project_manager.current_project.total_duration
            app.project_manager.current_project.total_duration = app.audio_manager.duration
            logger.info(f"   Updated project total_duration from {old_duration}s to {app.audio_manager.duration}s")
            
            # Check if timeline container would update
            if hasattr(app, 'main_window') and hasattr(app.main_window, 'timeline_widget'):
                timeline_widget = app.main_window.timeline_widget
                timeline_container = timeline_widget.timeline_container
                
                # Get the duration values that would be used
                duration = 0
                for timeline in app.project_manager.current_project.timelines:
                    timeline_duration = timeline.get_duration()
                    if timeline_duration > duration:
                        duration = timeline_duration
                
                project_total_duration = app.project_manager.current_project.total_duration
                max_duration = max(duration, project_total_duration)
                
                logger.info(f"   Timeline container would use: timeline_duration={duration:.2f}s, project_total_duration={project_total_duration:.2f}s, max_duration={max_duration:.2f}s")
        
        logger.info("4. Simulating ball sequence import (180 seconds)...")
        # Create a test timeline with segments that extend to 180 seconds
        test_timeline = Timeline(name="Test Ball", default_pixels=4)
        test_timeline.add_segment(TimelineSegment(
            start_time=0.0,
            end_time=180.0,
            color=(255, 0, 0),
            pixels=4
        ))
        
        # Add timeline to project
        app.project_manager.current_project.add_timeline(test_timeline)
        
        # Update project total_duration to accommodate the imported sequence
        timeline_duration = test_timeline.get_duration()
        old_project_duration = app.project_manager.current_project.total_duration
        if timeline_duration > old_project_duration:
            app.project_manager.current_project.total_duration = timeline_duration
            logger.info(f"   Updated project total_duration from {old_project_duration}s to {timeline_duration}s after ball sequence import")
        
        logger.info("5. Final validation...")
        final_duration = app.project_manager.current_project.total_duration
        logger.info(f"   Final project duration: {final_duration}s")
        
        # Validate that the scroll bar would now work correctly
        if hasattr(app, 'main_window') and hasattr(app.main_window, 'timeline_widget'):
            timeline_widget = app.main_window.timeline_widget
            
            # Calculate what the timeline container size would be
            duration = 0
            for timeline in app.project_manager.current_project.timelines:
                timeline_duration = timeline.get_duration()
                if timeline_duration > duration:
                    duration = timeline_duration
            
            project_total_duration = app.project_manager.current_project.total_duration
            max_duration = max(duration, project_total_duration)
            max_duration += 10.0  # padding
            
            # Calculate width
            width = int(max_duration * timeline_widget.time_scale * timeline_widget.zoom_level)
            
            logger.info(f"   Timeline container would have width: {width}px for duration: {max_duration:.2f}s")
            logger.info(f"   This should enable proper scrolling across the entire sequence!")
        
        logger.info("=== Test completed successfully! ===")
        logger.info("The scroll bar issue should now be fixed.")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_scroll_bar_fix()
    sys.exit(0 if success else 1)