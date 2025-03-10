# Simple Test Sequences for LTX Juggling Balls

I've created several simple test files to better understand how the LTX balls interpret color sequences. Each file is designed to demonstrate a specific pattern with clear, predictable behavior.

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

### Segment Duration Data Structure
Each segment's timing definition follows this structure:
- Duration (2 bytes)
- Pixel count (2 bytes)
- Constant flag (01 00) (2 bytes)
- Padding (00 00) (2 bytes)
- Repeated duration (2 bytes)
- Padding (00 00) (2 bytes)

### RGB Color Data
- RGB data always begins at the location explicitly marked by offset 0x001A
- RGB values appear in 3-byte format (FF 00 00 for red, 00 FF 00 green, etc.)

## Basic Solid Colors

These files should display a single, constant color:

1. `test_solid_red.prg` - Should display solid red
2. `test_solid_green.prg` - Should display solid green
3. `test_solid_blue.prg` - Should display solid blue

## Simple Patterns

These files should display various simple patterns:

1. `test_simple_alternating.prg` - Should alternate between red and green every 5 seconds
2. `test_rgb_slow.prg` - Should cycle through red → green → blue → red, with 10 seconds per color
3. `test_longer_duration.prg` - Should cycle through red → green → blue → red, with 30 seconds per color
4. `test_blink_red.prg` - Should blink red on (10 seconds) and off (10 seconds)

## Testing Process

1. Load each `.prg` file onto the ball one at a time
2. Note which patterns work as expected and which don't
3. For patterns that don't work as expected, note what actually happens

## Expected Results

The simplified sequences should be much easier to interpret, with clear color changes that happen slowly enough to observe and describe. This will help us build an accurate model of how the LTX balls process sequence files.

## Important Notes on Timing

The actual duration of each segment is calculated as:
```
Real Duration (sec) = Duration Value / Refresh Rate (Hz)
```

For example:
- 1 second red @ 1Hz refresh rate: Duration value 01 00 = 1 second
- 0.1 second red @ 10Hz refresh rate: Duration value 01 00 = 0.1 seconds
- 0.02 second red @ 50Hz refresh rate: Duration value 01 00 = 0.02 seconds
- 0.001 second red @ 1000Hz refresh rate: Duration value 01 00 = 0.001 seconds