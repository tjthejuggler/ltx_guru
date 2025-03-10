# Revised LTX Ball Sequence Examples

This directory contains revised versions of the sequence examples that address the issues identified in previous versions, following the comprehensive specification of the file format.

## File Format Specification

The LTX ball sequence files (.prg) follow a specific binary format:

### Header Structure (Byte Offsets)
| Offset (Hex) | Length (Bytes) | Purpose | Details |
|--------------|----------------|---------|---------|
| 0x0000 | 8 | File Signature | Always 50 52 03 49 4E 05 00 00 |
| 0x0008 | 2 | Pixel count | Number of pixels (e.g., 04 00 for 4 pixels) |
| 0x000A | 1 | Bit Depth | Usually 08 |
| 0x000C | 2 | Refresh Rate (Hz) | Defines timing resolution (e.g., 01 00=1Hz, 0A 00=10Hz, E8 03=1000Hz) |
| 0x000E | 2 | Constant Marker | Always 50 49 ("PI") |
| 0x0010 | 4 | Pointer to Duration Data | Always follows formula: 21 + 19×(n - 1) (decimal), with n as number of segments |
| 0x0014 | 4 | Segment Count | Integer value indicating how many segments follow |
| 0x0018 | 2 | Timing Constant | Always 64 00 (marks end of metadata/start of durations) |
| 0x001A | 2 | RGB Data Start Position | Points exactly to the byte where RGB data begins |

## Issues Addressed

The previous examples in `examples_improved` had several issues:

1. **RGB Cycle Issues**:
   - Nothing (no light) for 40 seconds
   - White for 40 seconds
   - Dull green after another 40 seconds
   - No light for 40 seconds
   - Blue for 2 minutes or longer

2. **Rainbow Issues**:
   - Cycling through colors very fast
   - Only showing green, blue, and cyan (not the full rainbow)

3. **Custom Sequence Issues**:
   - Super rapid flashing between red and green

## Improvements Made

The revised generator (`revised_multi_color_generator.py`) includes the following improvements:

1. **Correct Implementation of File Format**:
   - Proper implementation of the header structure according to the specification
   - Correct calculation of the pointer at 0x0010 using the formula: 21 + 19×(n - 1)
   - Accurate segment count at 0x0014
   - Proper RGB data start position at 0x001A

2. **Accurate Segment Structure**:
   - Each segment's timing definition follows the correct structure:
     - Duration (2 bytes)
     - Pixel count (2 bytes)
     - Constant flag (01 00) (2 bytes)
     - Padding (00 00) (2 bytes)
     - Repeated duration (2 bytes)
     - Padding (00 00) (2 bytes)

3. **Proper Timing Calculation**:
   - Using the formula: Real Duration (sec) = Duration Value / Refresh Rate (Hz)
   - Setting appropriate refresh rate (typically 10Hz) for desired timing resolution

4. **Longer Durations**:
   - Increased durations to ensure colors are visible for longer periods
   - RGB cycle: 20 seconds per color (200 deciseconds)
   - Rainbow: 15 seconds per color (150 deciseconds)
   - Custom sequence: Variable durations (10s, 20s, 30s)

## Examples

### rgb_cycle_long.prg
- A simple RGB cycle (red, green, blue, and back to red)
- Each color displays for 20 seconds (200 deciseconds)
- The file correctly defines 4 segments in the header
- The pointer at 0x0010 is set to 78 (21 + 19×3)

### rainbow_long.prg
- A rainbow sequence with 8 colors (red, orange, yellow, green, blue, indigo, violet, and back to red)
- Each color displays for 15 seconds (150 deciseconds)
- The file correctly defines 8 segments in the header
- The pointer at 0x0010 is set to 154 (21 + 19×7)

### custom_sequence_variable.prg
- A custom RGB sequence with variable durations:
  - Red: 10 seconds (100 deciseconds)
  - Green: 20 seconds (200 deciseconds)
  - Blue: 30 seconds (300 deciseconds)
- The file correctly defines 3 segments with different durations
- The pointer at 0x0010 is set to 59 (21 + 19×2)

### direct_copy_test.prg
- A direct copy of the structure from a known working example
- Implements the file format according to the comprehensive specification
- RGB sequence with variable durations:
  - Red: 10 seconds (100 deciseconds)
  - Green: 20 seconds (200 deciseconds)
  - Blue: 30 seconds (300 deciseconds)

## Usage

To create your own sequences with the revised generator, use:

```bash
# For RGB cycle with 20-second durations
python revised_multi_color_generator.py rgb_cycle 4 200 output.prg

# For rainbow with 15-second durations
python revised_multi_color_generator.py rainbow 4 150 output.prg

# For custom sequence with variable durations
python revised_multi_color_generator.py custom 4 output.prg 255 0 0 100 0 255 0 200 0 0 255 300

# For direct copy test (exactly 3 colors with variable durations)
python direct_copy_test.py 4 255 0 0 100 0 255 0 200 0 0 255 300 output.prg
```

Where:
- First parameter is the mode (rainbow, rgb_cycle, custom, single)
- Second parameter is the pixel count (1-4)
- For rainbow/rgb_cycle: Third parameter is the duration in deciseconds
- For custom: Parameters are groups of r,g,b,duration values
- For direct_copy_test: Parameters are pixel count, followed by three sets of r,g,b,duration values