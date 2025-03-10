# LTX Ball PRG Generator (Post-GPT4.5)

This is an updated PRG file generator for LTX LED juggling balls that implements the comprehensive specification of the file format. This generator creates .prg files that can be loaded onto LTX programmable juggling balls.

## File Format Specification

The LTX ball sequence files (.prg) follow a specific binary format:

### Header Structure (Byte Offsets)
| Offset (Hex) | Length (Bytes) | Purpose | Details |
|--------------|----------------|---------|---------|
| 0x0000 | 8 | File Signature | Always 50 52 03 49 4E 05 00 00 |
| 0x0008 | 2 | Pixel count | Number of pixels (e.g., 00 04 for 4 pixels) - Big endian |
| 0x000A | 2 | Bit Depth | Usually 00 08 |
| 0x000C | 2 | Refresh Rate (Hz) | Defines timing resolution (e.g., 01 00=1Hz) - Little endian |
| 0x000E | 2 | Constant Marker | Always 50 49 ("PI") |
| 0x0010 | 4 | Pointer to Duration Data | Always follows formula: 21 + 19×(n - 1) (decimal), with n as number of segments |
| 0x0014 | 4 | Segment Count | Integer value indicating how many segments follow |
| 0x0018 | 2 | Timing Constant | Always 64 00 (marks end of metadata/start of durations) |
| 0x001A | 2 | RGB Data Start Position | Points exactly to the byte where RGB data begins (e.g., 33 00 for a single segment) |
| 0x001C | 4 | Additional Data | Appears to be 00 00 01 00 |
| 0x0020 | 2 | Pixel Count (repeated) | Number of pixels again (e.g., 04 00 for 4 pixels) |

### Segment Duration Data Structure

Each segment's timing definition follows this structure:
- Pixel count (04 00) (2 bytes)
- Constant (01 00 00) (3 bytes)
- Constant (01 00 00 00) (4 bytes)
- Constant "CD0" (43 44 30) (3 bytes)
- Duration (2 bytes)
- Constant (00 00 64 00 00 00) (6 bytes)

### RGB Color Data

- RGB data begins at the location marked by offset 0x001A (typically 0x33 for a single segment)
- RGB values appear in 3-byte format (FF 00 00 for red, 00 FF 00 green, etc.)
- Each color is repeated 100 times for each pixel
- For example, a 4-pixel red segment would have FF 00 00 repeated 400 times (4 pixels × 100 repetitions)

### Footer

- The file ends with a footer: 42 54 00 00 00 ("BT" followed by 3 null bytes)

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

```bash
python3 prg_generator.py input.json output.prg
```

## JSON Input Format

The generator accepts a JSON file with the following structure:

### RGB Color Format

```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 1,
  "end_time": 10,
  "sequence": {
    "0": {"color": [255, 0, 0], "pixels": 4}
  }
}
```

- `default_pixels`: Default number of pixels (1-4) used when not specified for a color
- `color_format`: Color format, "rgb" or "hsv"
- `refresh_rate`: Timing resolution in Hz (default: 1, meaning seconds)
- `end_time`: Total duration of the sequence in deciseconds (optional)
- `sequence`: Dictionary of time points and colors
  - Keys: Time in deciseconds (e.g., "10" = 10 seconds with refresh_rate=1)
  - Values: Object with:
    - `color`: RGB color [R, G, B] with values 0-255
    - `pixels`: Number of pixels for this segment (1-4)

### HSV Color Format

```json
{
  "default_pixels": 4,
  "color_format": "hsv",
  "refresh_rate": 1,
  "end_time": 10,
  "sequence": {
    "0": {"color": [0, 100, 100], "pixels": 4}
  }
}
```

- HSV color values:
  - H: Hue (0-360)
  - S: Saturation (0-100)
  - V: Value/Brightness (0-100)

## Examples

### Simple Red (1 second)

```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 1,
  "end_time": 1,
  "sequence": {
    "0": {"color": [255, 0, 0], "pixels": 4}
  }
}
```

### Red to Green (1 second each)

```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 1,
  "end_time": 2,
  "sequence": {
    "0": {"color": [255, 0, 0], "pixels": 4},
    "1": {"color": [0, 255, 0], "pixels": 4}
  }
}
```

### RGB Cycle (1 second each)

```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 1,
  "end_time": 3,
  "sequence": {
    "0": {"color": [255, 0, 0], "pixels": 4},
    "1": {"color": [0, 255, 0], "pixels": 4},
    "2": {"color": [0, 0, 255], "pixels": 4}
  }
}
```

### Blinking Red (0.5 seconds on, 0.5 seconds off)

```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 2,
  "end_time": 2,
  "sequence": {
    "0": {"color": [255, 0, 0], "pixels": 4},
    "1": {"color": [0, 0, 0], "pixels": 4}
  }
}
```

## Implementation Details

The generator creates .prg files according to the comprehensive specification of the file format:

1. It correctly sets the header structure with all required fields in the proper byte order
2. It calculates the pointer at 0x0010 using the formula: 21 + 19×(n - 1)
3. It sets the segment count at 0x0014 based on the number of colors in the sequence
4. It creates proper segment descriptors for all colors in the sequence
5. It sets the RGB data start position at 0x001A to point to the beginning of the RGB data
6. It writes the RGB color data in the correct format, repeating each color 100 times per pixel
7. It supports variable pixel counts for each segment
8. It uses the end_time parameter to determine the total duration of the sequence
9. It adds the proper footer at the end of the file

## File Size Calculation

The size of a .prg file follows a precise formula based on the number of segments:

```
File Size (bytes) = 356 + (n - 1) × 319
```

Where:
- n = number of color segments
- 356 = size (bytes) for 1 color segment file
- 319 = additional bytes per extra color segment

This formula has been verified with multiple examples:

| Segments | Calculation | File Size (bytes) | End Offset (Hex) |
|----------|-------------|-------------------|------------------|
| 1 | 356 + (0) × 319 | 356 | 0x0164 |
| 2 | 356 + (1) × 319 | 675 | 0x02A3 |
| 3 | 356 + (2) × 319 | 994 | 0x03E2 |
| 4 | 356 + (3) × 319 | 1313 | 0x0521 |

The number of hex dump lines can be calculated as:
```
Total lines = Ceiling(File Size ÷ 16)
```

For example, a single segment file would have:
- 356 bytes total
- Ceiling(356 ÷ 16) = 23 lines in a hex dump

## Limitations

- The generator only supports up to 4 pixels (the maximum supported by the LTX balls)
- Very short durations may not display correctly on all LTX ball models
- If end_time is not specified, the generator will loop back to the first color after the last color

## License

This project is open source and available under the MIT License.

## Acknowledgements

This generator was created based on the comprehensive specification of the LTX LED juggling ball protocol.# ltx_guru
