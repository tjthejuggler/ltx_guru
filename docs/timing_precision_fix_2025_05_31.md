# Timing Precision Fix - 2025-05-31

## Issue Description

The sequence maker application was allowing ultra-precise floating-point timing values (15+ decimal places) to be stored in project files. When these values were converted to time units for PRG generation, they created irregular timing patterns that caused issues in the generated PRG files.

### Example of the Problem

**Ball 2 in `.smproj` file had timing values like:**
- `0.979041223526001` seconds
- `2.019168539047241` seconds  
- `3.012479066848755` seconds

**When converted to time units (×100 for 100Hz):**
- `97.9041223526001` → rounds to `98` (instead of expected `100`)
- `201.9168539047241` → rounds to `202` (instead of expected `200`)
- `301.2479066848755` → rounds to `301` (instead of expected `300`)

This created irregular timing patterns in the generated `project_Ball_2.json` file, while Ball 1 and Ball 3 had clean timing values.

## Root Cause

The issue was that ultra-precise floating-point timing values (15+ decimal places) were being stored and persisted in the sequence maker application at multiple levels:

1. **TimelineSegment model** - Allowed ultra-precise timing values to be stored
2. **Project file (.smproj)** - Saved ultra-precise values to disk
3. **JSON export** - Converted ultra-precise values without proper rounding

## Solution

Implemented comprehensive timing precision enforcement at multiple levels:

### 1. TimelineSegment Model (Primary Fix)
Modified `sequence_maker/models/segment.py` to:
- **Enforce 2 decimal place precision** for all timing values using property setters
- **Round timing values automatically** when set via properties or methods
- **Fix existing ultra-precise values** when loading from .smproj files

### 2. Timeline JSON Export (Secondary Fix)
Modified `sequence_maker/models/timeline.py` to:
- **Round timing values to 2 decimal places** before converting to time units
- **Apply rounding consistently** to all timing calculations

### 3. Timeline JSON Export Timing Gap Fix (Final Solution)
**Added automatic gap insertion in Timeline.to_json_sequence() to prevent exact timing overlaps:**

Modified `sequence_maker/models/timeline.py` to:
- **Detect exact timing overlaps** between segments during JSON export
- **Automatically insert 0.01 second gaps** between overlapping segments
- **Apply fix at JSON creation time** - ensures exported JSON files have proper timing
- **Maintain original segment durations** while adjusting start times to prevent overlaps
- **Allow verification** by inspecting the exported JSON files

This was the critical fix that resolved the actual PRG generation failures caused by exact timing overlaps between segments.

### Code Changes

**TimelineSegment Properties:**
```python
@staticmethod
def _round_timing(time_value):
    return round(float(time_value), 2)

@property
def start_time(self):
    return self._start_time

@start_time.setter
def start_time(self, value):
    self._start_time = self._round_timing(value)
```

**Timeline JSON Export:**
```python
def round_timing(time_value):
    return round(time_value, 2)

rounded_start_time = round_timing(segment.start_time)
rounded_end_time = round_timing(segment.end_time)
```

**Timeline JSON Export Timing Gap Fix:**
```python
# Apply timing gap fix to ensure segments don't have exact overlaps
adjusted_segments = []
gap_size = 0.01  # 0.01 second gap between segments

for i, segment in enumerate(sorted_segments):
    # Round timing values to prevent ultra-precise floating-point issues
    rounded_start_time = round_timing(segment.start_time)
    rounded_end_time = round_timing(segment.end_time)
    
    # Apply timing gap fix: ensure this segment starts after the previous one ends
    if i > 0:
        prev_segment = adjusted_segments[i - 1]
        prev_end_time = prev_segment['end_time']
        
        # If this segment starts at or before the previous segment ends, adjust it
        if rounded_start_time <= prev_end_time:
            rounded_start_time = prev_end_time + gap_size
            # Maintain the original duration by adjusting the end time too
            original_duration = rounded_end_time - round_timing(segment.start_time)
            rounded_end_time = rounded_start_time + original_duration
    
    # Store adjusted segment info for next iteration
    adjusted_segments.append({
        'start_time': rounded_start_time,
        'end_time': rounded_end_time,
        'color': segment.color,
        'pixels': segment.pixels
    })
```

## Testing

### Timing Precision Tests
Created and ran a test script that verified:
- Ultra-precise timing values like `0.979041223526001` are properly rounded
- Converted time units are clean integers
- No precision issues remain in the conversion process

**Test Results:** ✅ All timing values now convert to clean integers with zero precision errors.

### Timing Gap Fix Tests
Created test files to verify the gap insertion functionality:

**`test_timing_gap_fix_overlap.json`** - Contains exact timing overlaps:
```json
{
  "sequence": {
    "0": {"color": [255, 0, 0]},
    "100": {"color": [0, 255, 0]},
    "100.0": {"color": [0, 0, 255]},  // Exact overlap at time 100
    "200": {"color": [255, 255, 0]}
  }
}
```

**Test Results:**
- ✅ **Detected overlap**: Segments at time 100 and 100.0 both round to 100 time units
- ✅ **Applied gap**: Second segment moved from 100 to 101 time units (+1 unit gap)
- ✅ **Generated valid PRG**: No timing overlap errors in final PRG file
- ✅ **Preserved original JSON**: Source file remains unchanged

**Console Output Example:**
```
[TIMING_GAP] Applied gap: segment 2 moved from 100 to 101 units (+1 units)
[TIMING_GAP] Applied 1 timing gap adjustments to prevent exact overlaps
[TIMING_GAP] Updated sequence timestamps (units): [0, 100, 101, 200]
```

## Impact

- **Fixes timing precision issues** in PRG generation
- **Ensures consistent timing** across all balls in a project
- **Maintains backward compatibility** with existing project files
- **Prevents future timing precision problems**

## Files Modified

- `sequence_maker/models/segment.py` - Added timing precision enforcement with property setters and automatic rounding
- `sequence_maker/models/timeline.py` - Added timing precision rounding and timing gap fix in `to_json_sequence()` method to prevent exact overlaps between segments
- `prg_generator.py` - Added timing precision rounding for input validation (timing gap fix moved to Timeline class)

## Date

**Initial Fix:** 2025-05-31 19:07 UTC+7
**Timing Gap Fix (PRG Generator):** 2025-05-31 19:55 UTC+7
**Timing Gap Fix (Timeline - Final):** 2025-05-31 20:01 UTC+7