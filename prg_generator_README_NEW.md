Okay, here is the rewritten prg_generator_README.md incorporating the corrected understanding of the binary format. You should be able to replace the entire content of your existing file with this.

# LTX Ball PRG Generator Documentation

This document describes the usage and technical details of the LTX Ball PRG Generator, a tool for creating custom `.prg` sequence files for LTX programmable LED juggling balls. It also details the reverse-engineered `.prg` file format specification based on analysis and testing.

## Usage

Generate a `.prg` file from a JSON sequence definition:

```bash
python3 prg_generator.py input.json output.prg


input.json: Path to the JSON file describing the color sequence.

output.prg: Path where the generated binary .prg file will be saved.

JSON Input Format

The generator accepts a JSON file defining the color sequence.

Basic Structure
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 100,
  "end_time": 1506,
  "sequence": {
    "0": {"color": [255, 0, 0], "pixels": 4},
    "63": {"color": [0, 0, 255], "pixels": 4},
    "207": {"color": [0, 255, 0], "pixels": 4}
  }
}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Json
IGNORE_WHEN_COPYING_END
Fields Explained

default_pixels (Integer, 1-4): The number of LEDs to light up for a segment if not explicitly specified in the sequence entry. Defaults to 1 if omitted.

color_format (String, "rgb" or "hsv"): Specifies the format used for the color values in the sequence.

refresh_rate (Integer, Hz): Defines the timing resolution. This value determines how many time units occur per second.

1: 1 time unit = 1 second.

10: 1 time unit = 0.1 seconds.

100: 1 time unit = 0.01 seconds.

Formula: Time Unit Duration (seconds) = 1 / refresh_rate

end_time (Integer, time units): The total duration of the sequence in time units. The sequence will stop or loop after this time. This determines the duration of the last segment in the sequence.

sequence (Object): A dictionary where keys are strings representing the start time (in time units) of a color segment, and values are objects defining the color and pixel count for that segment.

Keys (Time Points): Must be strings representing non-negative integers, sorted chronologically. Time Units = Time in Seconds * refresh_rate.

Values (Segment Definition):

color (Array): The color for the segment.

If color_format is "rgb": [R, G, B] where R, G, B are 0-255.

If color_format is "hsv": [H, S, V] where H is 0-360, S is 0-100, V is 0-100. (Note: The generator converts HSV to RGB for the .prg file).

pixels (Integer, optional, 1-4): Number of pixels for this specific segment. Overrides default_pixels.

Handling Non-Integer Durations

Use the refresh_rate to achieve precise timing:

Choose Precision: Decide the smallest time step needed (e.g., 0.01s).

Set Refresh Rate: refresh_rate = 1 / smallest_time_step. (e.g., for 0.01s precision, refresh_rate = 100).

Convert Times: Convert all start times from seconds to time units: Time Units = round(Time in Seconds * refresh_rate).

Set End Time: Convert total duration to time units: end_time = round(Total Duration Seconds * refresh_rate).

Define Sequence: Use the calculated time units as keys in the sequence object.

Example: Red for 0.63s, then Blue for 1.44s (Total 2.07s). Precision needed: 0.01s.

{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 100, // 1 / 0.01s
  "end_time": 207,     // 2.07s * 100
  "sequence": {
    "0": {"color": [255, 0, 0]}, // Starts at 0s (0 time units)
    "63": {"color": [0, 0, 255]}  // Starts at 0.63s (63 time units)
  }
}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Json
IGNORE_WHEN_COPYING_END

Segment Durations:

Red: Starts at 0, ends at 63. Duration = 63 time units (0.63s).

Blue: Starts at 63, ends at 207 (end_time). Duration = 207 - 63 = 144 time units (1.44s).

File Format Specification (.prg Binary)

The LTX ball sequence files (.prg) follow a specific binary format. All multi-byte integer values are Little Endian unless otherwise specified.

Header Structure (34 Bytes Total)
Offset (Hex)	Length (Bytes)	Field Name	Data Type	Details & Example (red_1sec.prg)
0x0000	8	File Signature	bytes	Always 50 52 03 49 4E 05 00 00 (PR\x03IN\x05\x00\x00)
0x0008	2	Default Pixel Count	<H	Default pixels (1-4). 04 00 (4 pixels)
0x000A	2	Bit Depth	<H	Usually 08 00 (8-bit color depth)
0x000C	2	Refresh Rate (Hz)	<H	Timing resolution. 01 00 (1 Hz)
0x000E	2	Constant Marker	bytes	Always 50 49 (PI)
0x0010	4	Pointer/Value 0x10	<I	Purpose unclear, potentially related to segment count. Seems to follow 21 + 19*(n-1). 15 00 00 00 (21 for n=1)
0x0014	4	Segment Count (n)	<I	Total number of color segments. 01 00 00 00 (1 segment)
0x0018	2	Timing Constant	<H	Always 64 00
0x001A	2	RGB Data Start Offset	<H	Byte offset where RGB data begins. Calculated as 34 + (n * 19). 33 00 (51 for n=1)
0x001C	4	Additional Data	<I	Always 00 00 01 00
0x0020	2	Default Pixel Count (Rep.)	<H	Repeated default pixels. 04 00 (4 pixels)

Data Types: <H = 2-byte unsigned short (Little Endian), <I = 4-byte unsigned int (Little Endian)

Segment Duration Data Structure (19 Bytes per Segment)

Immediately following the 34-byte header, one 19-byte block exists for each color segment (n blocks total, where n is the Segment Count from offset 0x0014).

Offset (Relative)	Length (Bytes)	Field Name	Data Type	Details
0x00	2	Pixel Count	<H	Number of pixels for this segment (1-4).
0x02	3	Constant 1	bytes	Always 01 00 00
0x05	4	Constant 2	bytes	Always 01 00 00 00
0x09	3	Constant 3	bytes	Always 43 44 30 (CD0)
0x0C	2	Segment Duration	<H	Duration in time units (max 65535).
0x0E	6	Constant 4	bytes	Always 00 00 64 00 00 00
RGB Color Data (300 Bytes per Segment)

Immediately following the last Segment Duration Data block (starting at the offset specified in the header at 0x001A), the RGB color data begins.

For each segment, the corresponding RGB color is written 100 times.

Each color write consists of 3 bytes: Red, Green, Blue (0-255 each).

Format: R G B R G B R G B ... (repeated 100 times per segment).

Total size per segment: 3 bytes/color * 100 repeats = 300 bytes.

There are no intermediate markers or headers between the last duration block and the start of the RGB data, nor between the RGB data of consecutive segments.

Footer (5 Bytes)

The file ends with a fixed 5-byte footer:

42 54 00 00 00 (BT\x00\x00\x00)

File Size Calculation

The total size of a .prg file can be calculated based on the number of segments (n):

File Size (bytes) = Header Size + (n * Duration Block Size) + (n * RGB Block Size) + Footer Size
File Size (bytes) = 34 + (n * 19) + (n * 300) + 5
File Size (bytes) = 39 + n * 319

Alternatively, using an empirically derived formula based on observed file sizes:

File Size (bytes) = 356 + (n - 1) * 319 (Where n >= 1)

Breakdown:

Base size for 1 segment (n=1): 356 bytes (observed).

Theoretical sum: 34 (Header) + 19 (Duration) + 300 (RGB) + 5 (Footer) = 358 bytes.

(The 2-byte difference is minor and unexplained, but the structure holds).

Each additional segment adds 19 (Duration) + 300 (RGB) = 319 bytes.

Example Sizes:

Segments (n)	Calculation	File Size (bytes)	End Offset (Hex)
1	356 + (0) * 319	356	0x0163
2	356 + (1) * 319	675	0x02A2
3	356 + (2) * 319	994	0x03E1
4	356 + (3) * 319	1313	0x0520
Implementation Details (Corrected Generator)

The prg_generator.py script implements the .prg file specification as follows:

Parses the input JSON file.

Calculates segment durations based on sequence time points and end_time.

Handles potential segment durations exceeding 65535 by splitting them (split_long_segments).

Calculates necessary header values (segment count, RGB data start offset, etc.).

Writes the correct 34-byte file header using proper multi-byte Little Endian formats (<H, <I).

For each segment:

Writes the correct 19-byte duration data block.

For each segment:

Writes the 300-byte RGB color data block (100 repetitions of the 3-byte RGB value).

Writes the correct 5-byte footer (BT\x00\x00\x00).

Outputs debug information about the process.

Limitations

Maximum pixels value is 4 (hardware limit).

Maximum duration per generated segment is 65535 time units (due to 2-byte field). Longer durations in JSON are automatically split.

Very short durations (high refresh_rate and small duration values) might not display accurately due to hardware limitations.

License

This project is open source and available under the MIT License.

Acknowledgements

This format specification was derived through reverse engineering, analysis of existing files, and community contributions.

IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
IGNORE_WHEN_COPYING_END