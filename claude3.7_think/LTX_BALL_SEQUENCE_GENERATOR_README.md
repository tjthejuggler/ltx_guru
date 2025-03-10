# LTX Ball Sequence Generator

A tool for creating `.prg` files for LTX LED juggling balls based on the comprehensive understanding of the file format.

## Overview

This generator creates sequence files for LTX LED juggling balls by implementing the correct binary structure according to the final comprehensive specification. This approach allows for precise control over color sequences and timing.

## Installation

No installation is required. Simply download the `ltx_ball_sequence_generator.py` script and run it with Python 3.

```bash
# Make the script executable
chmod +x ltx_ball_sequence_generator.py
```

## Usage

The generator supports several modes of operation:

### Single Color

Generate a solid color sequence:

```bash
python3 ltx_ball_sequence_generator.py single 4 255 0 0 100 red.prg
```

Parameters:
- `single`: Mode of operation
- `4`: Number of pixels (1-4)
- `255 0 0`: RGB values for red
- `100`: Duration in deciseconds (10 seconds)
- `red.prg`: Output file path

### Two Colors

Generate a two-color sequence that alternates between two colors:

```bash
python3 ltx_ball_sequence_generator.py dual 4 255 0 0 100 0 255 0 100 red_to_green.prg
```

Parameters:
- `dual`: Mode of operation
- `4`: Number of pixels (1-4)
- `255 0 0`: RGB values for first color (red)
- `100`: Duration in deciseconds for first color (10 seconds)
- `0 255 0`: RGB values for second color (green)
- `100`: Duration in deciseconds for second color (10 seconds)
- `red_to_green.prg`: Output file path

### RGB Cycle

Generate an RGB cycle sequence (red → green → blue → red):

```bash
python3 ltx_ball_sequence_generator.py rgb_cycle 4 100 rgb_cycle.prg
```

Parameters:
- `rgb_cycle`: Mode of operation
- `4`: Number of pixels (1-4)
- `100`: Duration in deciseconds for each color (10 seconds)
- `rgb_cycle.prg`: Output file path

### Rainbow

Generate a rainbow cycle sequence:

```bash
python3 ltx_ball_sequence_generator.py rainbow 4 100 rainbow.prg
```

Parameters:
- `rainbow`: Mode of operation
- `4`: Number of pixels (1-4)
- `100`: Duration in deciseconds for each color (10 seconds)
- `rainbow.prg`: Output file path

### Police Lights

Generate a police lights effect (red → blue → red → blue):

```bash
python3 ltx_ball_sequence_generator.py police 4 100 police.prg
```

Parameters:
- `police`: Mode of operation
- `4`: Number of pixels (1-4)
- `100`: Duration in deciseconds for each color (10 seconds)
- `police.prg`: Output file path

### Traffic Lights

Generate a traffic lights effect (red → yellow → green → yellow → red):

```bash
python3 ltx_ball_sequence_generator.py traffic 4 100 traffic.prg
```

Parameters:
- `traffic`: Mode of operation
- `4`: Number of pixels (1-4)
- `100`: Duration in deciseconds for each color (10 seconds)
- `traffic.prg`: Output file path

### Custom Sequence

Generate a custom sequence with any number of colors and durations:

```bash
python3 ltx_ball_sequence_generator.py custom 4 custom.prg 255 0 0 100 0 255 0 150 0 0 255 200
```

Parameters:
- `custom`: Mode of operation
- `4`: Number of pixels (1-4)
- `custom.prg`: Output file path
- `255 0 0 100`: First color (red) with duration 100 deciseconds (10 seconds)
- `0 255 0 150`: Second color (green) with duration 150 deciseconds (15 seconds)
- `0 0 255 200`: Third color (blue) with duration 200 deciseconds (20 seconds)

## Technical Details

The generator creates `.prg` files according to the comprehensive specification of the file format.

### File Structure (Byte Offsets)

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

## Limitations

- The generator only supports up to 4 pixels (the maximum supported by the LTX balls).
- The refresh rate is typically set to 10Hz (0A 00), which means durations are specified in deciseconds.
- Very short durations may not display correctly on all LTX ball models.

## License

This project is open source and available under the MIT License.

## Acknowledgements

This generator was created by Claude 3.7 Opus as part of a project to understand and work with the LTX LED juggling ball protocol.