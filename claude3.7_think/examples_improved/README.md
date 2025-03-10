# Improved LTX Ball Sequence Examples

This directory contains improved versions of the sequence examples that correctly implement multiple colors with variable durations according to the comprehensive specification.

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

## Issues Fixed

The previous examples in `examples_fixed` had two main issues:
1. They only showed the first two colors of the sequences
2. All colors had a fixed 10-second duration

These issues have been fixed by correctly implementing:
1. Proper segment descriptors for all colors in the sequence
2. Support for variable durations for each color
3. Correct pointer calculation using the formula: 21 + 19×(n - 1)
4. Proper refresh rate handling for accurate timing

## Examples

### rainbow.prg
- A rainbow sequence with 8 colors (red, orange, yellow, green, blue, indigo, violet, and back to red)
- Each color displays for 5 seconds (50 deciseconds)
- The file correctly defines 8 segments in the header
- The pointer at 0x0010 is set to 154 (21 + 19×7)

### rgb_cycle.prg
- A simple RGB cycle (red, green, blue, and back to red)
- Each color displays for 4 seconds (40 deciseconds)
- The file correctly defines 4 segments in the header
- The pointer at 0x0010 is set to 78 (21 + 19×3)

### custom_sequence.prg
- A custom RGB sequence with variable durations:
  - Red: 3 seconds (30 deciseconds)
  - Green: 5 seconds (50 deciseconds)
  - Blue: 7 seconds (70 deciseconds)
- The file correctly defines 3 segments with different durations
- The pointer at 0x0010 is set to 59 (21 + 19×2)

## Implementation Details

The improved sequences were created using the `improved_multi_color_generator.py` script, which:

1. Correctly sets the segment count in the header
2. Creates proper segment descriptors for all colors in the sequence
3. Sets the correct duration for each segment
4. Calculates the pointer value using the formula: 21 + 19×(n - 1)
5. Sets the RGB data start position correctly
6. Ensures the segment structure follows the specification:
   - Duration (2 bytes)
   - Pixel count (2 bytes)
   - Constant flag (01 00) (2 bytes)
   - Padding (00 00) (2 bytes)
   - Repeated duration (2 bytes)
   - Padding (00 00) (2 bytes)

## Usage

To create your own sequences with variable durations, use:

```bash
# For rainbow with 5-second durations
python improved_multi_color_generator.py rainbow 4 50 output.prg

# For custom sequence with variable durations
python improved_multi_color_generator.py custom 4 output.prg 255 0 0 30 0 255 0 50 0 0 255 70
```

Where:
- First parameter is the mode (rainbow, rgb_cycle, custom, single)
- Second parameter is the pixel count (1-4)
- For rainbow/rgb_cycle: Third parameter is the duration in deciseconds
- For custom: Parameters are groups of r,g,b,duration values