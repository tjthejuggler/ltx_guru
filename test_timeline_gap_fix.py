#!/usr/bin/env python3
"""
Test script to verify the timing gap fix in Timeline.to_json_sequence()
"""

import sys
import os
import json

# Add the sequence_maker directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sequence_maker'))

from models.timeline import Timeline
from models.segment import TimelineSegment

def test_timeline_gap_fix():
    """Test that Timeline.to_json_sequence() applies timing gaps correctly"""
    
    print("Testing Timeline timing gap fix...")
    
    # Create a timeline
    timeline = Timeline(name="Test Timeline", default_pixels=1)
    
    # Add segments with exact overlaps (same start/end times)
    segments = [
        TimelineSegment(start_time=0.0, end_time=1.0, color=(255, 0, 0), pixels=1),    # Red: 0-1s
        TimelineSegment(start_time=1.0, end_time=2.0, color=(0, 255, 0), pixels=1),    # Green: 1-2s (exact overlap)
        TimelineSegment(start_time=1.0, end_time=3.0, color=(0, 0, 255), pixels=1),    # Blue: 1-3s (exact overlap)
        TimelineSegment(start_time=2.0, end_time=4.0, color=(255, 255, 0), pixels=1),  # Yellow: 2-4s
    ]
    
    for segment in segments:
        timeline.add_segment(segment)
    
    print(f"Original segments:")
    for i, seg in enumerate(timeline.segments):
        print(f"  Segment {i}: {seg.start_time}s - {seg.end_time}s, Color: {seg.color}")
    
    # Convert to JSON sequence
    json_data = timeline.to_json_sequence(refresh_rate=100)
    
    print(f"\nGenerated JSON sequence:")
    print(f"  Refresh rate: {json_data['refresh_rate']} Hz")
    print(f"  End time: {json_data['end_time']} time units")
    print(f"  Sequence timestamps: {sorted([int(k) for k in json_data['sequence'].keys()])}")
    
    # Check for timing gaps
    timestamps = sorted([int(k) for k in json_data['sequence'].keys()])
    print(f"\nTiming analysis:")
    for i in range(len(timestamps) - 1):
        current = timestamps[i]
        next_ts = timestamps[i + 1]
        gap = next_ts - current
        print(f"  Time {current} -> {next_ts}: gap = {gap} time units")
        if gap == 0:
            print(f"    ❌ EXACT OVERLAP DETECTED!")
        elif gap == 1:
            print(f"    ✅ Proper 0.01s gap applied")
        else:
            print(f"    ℹ️  Gap of {gap/100:.2f}s")
    
    # Save the JSON for inspection
    output_file = "test_timeline_gap_fix_output.json"
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"\nJSON output saved to: {output_file}")
    
    # Verify no exact overlaps exist
    has_overlaps = any(timestamps[i] == timestamps[i+1] for i in range(len(timestamps)-1))
    
    if has_overlaps:
        print("❌ TEST FAILED: Exact timing overlaps still exist!")
        return False
    else:
        print("✅ TEST PASSED: No exact timing overlaps detected!")
        return True

if __name__ == "__main__":
    success = test_timeline_gap_fix()
    sys.exit(0 if success else 1)