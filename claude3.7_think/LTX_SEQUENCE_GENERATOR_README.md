# LTX Ball Sequence Generator

This tool converts JSON color sequence specifications into .prg files that can be loaded onto LTX programmable juggling balls, following the comprehensive specification of the file format.

## Features

- Generate custom color sequences for LTX balls
- Support for 1-4 pixel configurations
- Support for both HSV and RGB color formats
- Define exact timing for color transitions
- Simple JSON input format
- Precise control over refresh rate and timing resolution

## Usage

```bash
python3 ltx_sequence_generator.py input.json output.prg
```

## JSON Input Format

The tool accepts a JSON file with the following structure:

### HSV Color Format (Default)

```json
{
  "pixels": 4,
  "color_format": "hsv",
  "refresh_rate": 10,
  "sequence": {
    "0": [0, 100, 100],        // Red at start
    "1500": [120, 100, 100],   // Green at 15 seconds
    "3500": [240, 100, 100],   // Blue at 35 seconds
    "6000": [0, 100, 100]      // Red at 60 seconds
  }
}
```

- `pixels`: Number of pixels to program (1-4)
- `color_format`: Color format, "hsv" (default) or "rgb"
- `refresh_rate`: Timing resolution in Hz (default: 10)
- `sequence`: Dictionary of time points and colors
  - Keys: Time in deciseconds (e.g., "1500" = 15 seconds)
  - Values: HSV color [H, S, V]
    - H: Hue (0-360)
    - S: Saturation (0-100)
    - V: Value/Brightness (0-100)

### RGB Color Format

```json
{
  "pixels": 3,
  "color_format": "rgb",
  "refresh_rate": 10,
  "sequence": {
    "0": [255, 0, 0],          // Red at start
    "1500": [0, 255, 0],       // Green at 15 seconds
    "3500": [0, 0, 255],       // Blue at 35 seconds
    "6000": [255, 0, 0]        // Red at 60 seconds
  }
}
```

- RGB color values are integers from 0-255

## Examples

1. **Simple RGB sequence** (4 pixels, RGB format)
   ```json
   {
     "pixels": 4,
     "color_format": "rgb",
     "refresh_rate": 10,
     "sequence": {
       "0": [255, 0, 0],
       "1000": [0, 255, 0],
       "2000": [0, 0, 255],
       "3000": [255, 0, 0]
     }
   }
   ```

2. **Rainbow sequence** (3 pixels, HSV format)
   ```json
   {
     "pixels": 3,
     "refresh_rate": 10,
     "sequence": {
       "0": [0, 100, 100],
       "500": [30, 100, 100],
       "1000": [60, 100, 100],
       "1500": [120, 100, 100],
       "2000": [180, 100, 100],
       "2500": [240, 100, 100],
       "3000": [300, 100, 100],
       "3500": [330, 100, 100],
       "4000": [0, 100, 100]
     }
   }
   ```

## Technical Details

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

## Notes

- Times are specified in deciseconds (1/10th of a second) by default
- The final color point will repeat until the total duration is reached
- The generated .prg files are compatible with LTX ball programmers
- The refresh rate can be adjusted to achieve different timing resolutions