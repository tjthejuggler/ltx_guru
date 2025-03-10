# Fixed LTX Ball Sequence Examples

This directory contains example `.prg` files created with the fixed LTX Ball Sequence Generator. These examples demonstrate different types of color sequences that can be loaded onto LTX LED juggling balls.

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

## Examples

### rgb_cycle.prg

An RGB cycle that transitions through red, green, blue, and back to red with 10-second durations for each color.

```bash
python3 ../fixed_generator.py rgb_cycle 4 100 rgb_cycle.prg
```

### police_lights.prg

A police lights effect that alternates between red and blue with 10-second durations for each color.

```bash
python3 ../fixed_generator.py police 4 100 police_lights.prg
```

### rainbow.prg

A rainbow cycle that transitions through all colors of the rainbow with 10-second durations for each color.

```bash
python3 ../fixed_generator.py rainbow 4 100 rainbow.prg
```

### custom_sequence.prg

A custom sequence with multiple colors:
- Red (10 seconds)
- Green (10 seconds)
- Blue (10 seconds)
- Yellow (10 seconds)

```bash
python3 ../fixed_generator.py custom 4 custom_sequence.prg 255 0 0 100 0 255 0 100 0 0 255 100 255 255 0 100
```

## Implementation Details

These sequences are created following the comprehensive specification of the file format:

### Segment Duration Data Structure

Each segment's timing definition follows this structure:
- Duration (2 bytes)
- Pixel count (2 bytes)
- Constant flag (01 00) (2 bytes)
- Padding (00 00) (2 bytes)
- Repeated duration (2 bytes)
- Padding (00 00) (2 bytes)

### Timing Calculation

The actual duration of each segment is calculated as:
```
Real Duration (sec) = Duration Value / Refresh Rate (Hz)
```

For example:
- 1 second red @ 1Hz refresh rate: Duration value 01 00 = 1 second
- 0.1 second red @ 10Hz refresh rate: Duration value 01 00 = 0.1 seconds
- 0.02 second red @ 50Hz refresh rate: Duration value 01 00 = 0.02 seconds
- 0.001 second red @ 1000Hz refresh rate: Duration value 01 00 = 0.001 seconds

## Usage

To use these examples, upload the `.prg` files to your LTX LED juggling balls using the appropriate method for your device.

## Creating Your Own Sequences

You can create your own sequences using the fixed generator. See the main README file for more information.

```bash
python3 ../fixed_generator.py --help