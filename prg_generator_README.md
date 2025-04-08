Okay, this combines the information from both tools, updates the PRG format specification based on our findings, and clarifies the relationship between time units and refresh rate.

Here is the complete, updated documentation file:

```markdown
# LTX Guru Tools

This repository contains tools for discovering, controlling, and generating sequence files for LTX programmable LED juggling balls.

**Sections:**
1.  [LTX Ball Control (Real-time WiFi Control)](#ltx-ball-control-real-time-wifi-control)
2.  [LTX Ball PRG Generator (Sequence Files)](#ltx-ball-prg-generator-sequence-files)
3.  [License](#license)
4.  [Acknowledgements](#acknowledgements)

---

## LTX Ball Control (Real-time WiFi Control)

A Python script (`ball_control.py`) for discovering and controlling LTX juggling balls over WiFi in real-time.

### Requirements

*   Python 3.x
*   Root/sudo privileges (required for raw socket network discovery)
*   LTX balls must be connected to the same WiFi network as the computer running the script.

### Usage

#### Basic Commands

```bash
# Scan for balls on the network (requires sudo)
sudo python3 ball_control.py scan

# Set discovered ball(s) to solid red
sudo python3 ball_control.py red

# Set discovered ball(s) to solid green
sudo python3 ball_control.py green

# Set discovered ball(s) to solid blue
sudo python3 ball_control.py blue

# Turn discovered ball(s) off (black)
sudo python3 ball_control.py off

# Set a custom RGB color (e.g., Orange)
sudo python3 ball_control.py --rgb=255,128,0 color

# Set brightness (0-255, applied to subsequent color commands)
sudo python3 ball_control.py --brightness=128 red
```

#### Options and All Commands

```
Options:
    --network=SUBNET   Specify network prefix to scan (default: 192.168.1)
    --timeout=SECS     Duration in seconds to scan for balls (default: 5)
    --no-continuous    Stop scanning after timeout even if no balls found
    --rgb=R,G,B        Specify custom RGB color (values 0-255) for the 'color' command
    --brightness=N     Set brightness level (0-255) for subsequent color commands

Commands:
    scan               Scan for balls and list their IP addresses
    red                Set found ball(s) to red (full brightness unless --brightness specified)
    green              Set found ball(s) to green (full brightness unless --brightness specified)
    blue               Set found ball(s) to blue (full brightness unless --brightness specified)
    off                Turn found ball(s) off (set color to black)
    color              Set found ball(s) to the custom RGB color specified with --rgb
```

### How It Works

#### Ball Discovery

1.  **Broadcasting:** Each LTX ball periodically sends a UDP broadcast packet to the network's broadcast address (e.g., 192.168.1.255 or 255.255.255.255) on port `41412`.
2.  **Identifier:** These packets contain the ASCII string `"NPLAYLTXBALL"` as an identifier.
3.  **Listening:** The `scan` command uses raw sockets to listen for these specific UDP broadcast packets. Raw sockets are necessary to reliably capture broadcast traffic across different operating systems and network configurations, hence the need for root/sudo privileges.
4.  **Identification:** When a packet matching the criteria is received, the script extracts the source IP address of the ball.

#### Ball Control

1.  **Targeting:** Once a ball's IP address is known (from discovery), commands are sent directly to that IP address via UDP on port `41412`.
2.  **Packet Format:** Control commands are sent as 12-byte UDP packets with the following structure:

    | Byte Offset | Value        | Purpose                                      |
    | :---------- | :----------- | :------------------------------------------- |
    | 0           | `0x42` ('B') | Packet identifier                            |
    | 1-7         | `0x00`       | Unused padding                               |
    | 8           | Opcode       | Command Type (`0x0A`: Set Color, `0x10`: Set Brightness) |
    | 9-11        | Parameters   | Command-specific data                        |

3.  **Parameters:**
    *   **Set Color (Opcode `0x0A`):** Bytes 9, 10, 11 are the Red, Green, and Blue values (0-255), respectively. Example: `... 0A FF 00 00` for Red.
    *   **Set Brightness (Opcode `0x10`):** Byte 9 is the brightness level (0-255). Bytes 10 and 11 are unused (`0x00`). Example: `... 10 80 00 00` for 50% brightness (128).

4.  **UDP Reliability:** Since UDP is a connectionless protocol and packets can be lost, professional LTX control software often sends commands multiple times in quick succession, sometimes with slightly varying parameters (like decreasing power levels), to increase the likelihood that the command is received and executed correctly. This script sends each command once.

### Network and Packet Analysis Notes

*   Ensure your network firewall allows UDP traffic on port `41412`, both incoming broadcasts and outgoing direct packets.
*   **Wireshark Filter:** Use `udp.port == 41412` in Wireshark to capture both discovery (destination: broadcast IP) and command (destination: ball IP) packets.
*   Look for the `"NPLAYLTXBALL"` string (hex: `4E 50 4C 41 59 4C 54 58 42 41 4C 4C`) in the UDP payload of discovery packets.
*   Look for 12-byte UDP payloads starting with `42` (hex) for command packets sent *to* the ball's IP address.

---

## LTX Ball PRG Generator (Sequence Files)

A Python script (`prg_generator.py`) that converts JSON files describing color sequences into the binary `.prg` format used by LTX programmable juggling balls.

### Usage

```bash
python3 prg_generator.py input.json output.prg
```

*   `input.json`: Path to the JSON file describing the color sequence.
*   `output.prg`: Path where the generated binary `.prg` file will be saved.

### JSON Input Format

The generator accepts a JSON file defining the color sequence and timing.

#### Basic Structure

```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 100,
  "end_time": 207,
  "sequence": {
    "0": {"color": [255, 0, 0], "pixels": 4},
    "63": {"color": [0, 0, 255], "pixels": 4}
  }
}
```

#### Fields Explained

*   `default_pixels` (Integer, 1-4): The number of LEDs (1 to 4) to light up for a segment if the `pixels` key is not specified within that segment's definition. Defaults to 1 if this field is omitted entirely.
*   `color_format` (String, `"rgb"` or `"hsv"`): Specifies the format used for the `color` values in the `sequence`. If `"hsv"`, the generator converts colors to RGB before writing to the `.prg` file. Defaults to `"rgb"`.
    *   RGB: `[R, G, B]` where R, G, B are 0-255.
    *   HSV: `[H, S, V]` where H (Hue) is 0-360, S (Saturation) is 0-100, V (Value/Brightness) is 0-100.
*   `refresh_rate` (Integer, Hz): **Crucial for timing.** Defines the timing resolution, determining how many "time units" occur per second.
    *   `1`: 1 time unit = 1 second.
    *   `100`: 1 time unit = 0.01 seconds (10ms).
    *   Formula: `Time Unit Duration (seconds) = 1 / refresh_rate`
*   `end_time` (Integer, **time units**): The total duration of the *entire sequence* in **time units**. This value dictates the end time (and thus duration) of the very last segment in the `sequence`. Required if you want the sequence to end; otherwise, the last segment might have zero or default duration depending on implementation.
*   `sequence` (Object): A dictionary defining the color changes over time.
    *   **Keys:** Strings representing the **start time** of a color segment, measured in **time units**. Must be non-negative integers, sorted chronologically in the file (though the script sorts them).
        *   `Time Units = Time in Seconds * refresh_rate`
    *   **Values:** An object defining the segment starting at that time key:
        *   `color` (Array): The color for the segment, in the format specified by `color_format`.
        *   `pixels` (Integer, optional, 1-4): Number of pixels for this specific segment. Overrides `default_pixels`.

#### Example: Precise Timing (Red 0.63s, Blue 1.44s)

To achieve 0.01s precision:
1.  Set `refresh_rate` to `100` (1 / 0.01).
2.  Convert times to time units:
    *   Start Red: 0s * 100 = 0 time units.
    *   Start Blue: 0.63s * 100 = 63 time units.
    *   End Sequence: (0.63s + 1.44s) * 100 = 2.07s * 100 = 207 time units.
3.  Create the JSON:

```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 100,
  "end_time": 207,
  "sequence": {
    "0": {"color": [255, 0, 0]},
    "63": {"color": [0, 0, 255]}
  }
}
```
*Resulting Durations (in time units):*
*   Segment 0 (Red): Starts at 0, ends at 63 (start of next). Duration = 63 - 0 = 63 units.
*   Segment 1 (Blue): Starts at 63, ends at 207 (`end_time`). Duration = 207 - 63 = 144 units.

### `.prg` File Format Specification

The binary `.prg` files have the following structure. Multi-byte values are **Little Endian** unless specified otherwise.

#### Overall Structure

1.  **Header** (32 bytes)
2.  **Duration Blocks** (19 bytes * number of segments)
3.  **RGB Data** (300 bytes * number of segments)
4.  **Footer** (6 bytes)

#### 1. Header (32 Bytes)

| Offset (Hex) | Length | Field Name            | Data Type | Endian | Details & Example (N=3, 4px, 1Hz) |
| :----------- | :----- | :-------------------- | :-------- | :----- | :-------------------------------- |
| 0x00         | 8      | File Signature        | `bytes`   | N/A    | `50 52 03 49 4E 05 00 00` ('PR\x03IN\x05\x00\x00') |
| 0x08         | 2      | Default Pixel Count   | `H`       | Big    | `00 04` (4 pixels)                |
| 0x0A         | 2      | Constant 0x0A         | `bytes`   | N/A    | `00 08` (Purpose unclear)         |
| 0x0C         | 2      | Refresh Rate (Hz)     | `H`       | Little | `01 00` (1 Hz)                    |
| 0x0E         | 2      | Constant Marker "PI"  | `bytes`   | N/A    | `50 49` ('PI')                    |
| 0x10         | 4      | Pointer1              | `I`       | Little | `3B 00 00 00` (59 for N=3)        |
| 0x14         | 2      | Segment Count (N)     | `H`       | Little | `03 00` (3 segments)              |
| 0x16         | 2      | Constant 0x16         | `bytes`   | N/A    | `00 00`                           |
| 0x18         | 2      | Constant 0x18         | `bytes`   | N/A    | `64 00` (100 LE)                  |
| 0x1A         | 2      | RGB Data Start Offset | `H`       | Little | `59 00` (89 for N=3)              |
| 0x1C         | 2      | Constant 0x1C         | `bytes`   | N/A    | `00 00`                           |
| 0x1E         | 2      | First Duration Units  | `H`       | Little | Duration (units) of the first segment |

*Data Types:* `H`=Unsigned Short (2 bytes), `I`=Unsigned Int (4 bytes).
*Pointer1 Calculation:* Seems related to the start of the last duration block: `32 + (N-1)*19 - 11 = 21 + 19*(N-1)`.
*RGB Start Offset Calculation:* `HEADER_SIZE + N * DURATION_BLOCK_SIZE = 32 + N * 19`.

#### 2. Duration Blocks (19 Bytes per Segment)

One block exists for each segment, immediately following the header. Let N be the total segment count.

**Structure for Segments 0 to N-2 (Intermediate Blocks):**

| Offset (Relative) | Length | Field Name            | Data Type | Endian | Details                                      |
| :---------------- | :----- | :-------------------- | :-------- | :----- | :------------------------------------------- |
| +0x00             | 2      | Pixel Count           | `H`       | Little | Pixels for *this* segment (1-4)              |
| +0x02             | 3      | Block Constant 0x02   | `bytes`   | N/A    | `01 00 00`                                   |
| +0x05             | 2      | Current Duration Units| `H`       | Little | Duration (units) of *this* segment           |
| +0x07             | 2      | Block Constant 0x07   | `bytes`   | N/A    | `00 00`                                      |
| +0x09             | 4      | Block Constant 0x09   | `bytes`   | N/A    | `00 00 64 00` (100 LE)                     |
| +0x0D             | 2      | Index1 Value          | `H`       | Little | Calculated by `calculate_legacy_intro_pair`  |
| +0x0F             | 2      | Block Constant 0x0F   | `bytes`   | N/A    | `00 00`                                      |
| +0x11             | 2      | Next Duration Units   | `H`       | Little | Duration (units) of the *next* segment       |

**Structure for Segment N-1 (LAST Block):**

| Offset (Relative) | Length | Field Name            | Data Type | Endian | Details                                          |
| :---------------- | :----- | :-------------------- | :-------- | :----- | :----------------------------------------------- |
| +0x00             | 2      | Pixel Count           | `H`       | Little | Pixels for *this* segment (1-4)                  |
| +0x02             | 3      | Block Constant 0x02   | `bytes`   | N/A    | `01 00 00`                                       |
| +0x05             | 2      | Current Duration Units| `H`       | Little | Duration (units) of *this* segment               |
| +0x07             | 2      | Block Constant 0x07   | `bytes`   | N/A    | `00 00`                                          |
| +0x09             | 2      | Last Block Const 0x09 | `bytes`   | N/A    | `43 44` ('CD')                                   |
| +0x0B             | 2      | Index2 Part 1         | `H`       | Little | Calculated by `calculate_legacy_color_intro_parts` |
| +0x0D             | 2      | Last Block Const 0x0D | `bytes`   | N/A    | `00 00`                                          |
| +0x0F             | 2      | Index2 Part 2         | `H`       | Little | Calculated by `calculate_legacy_color_intro_parts` |
| +0x11             | 2      | Last Block Const 0x11 | `bytes`   | N/A    | `00 00`                                          |

**Index Value Calculation (Known Complexities):**
The `Index1 Value`, `Index2 Part 1`, and `Index2 Part 2` fields are crucial for the firmware to correctly step through the sequence. Their calculation is non-trivial and depends on the total number of segments (N) and the current segment's index. The generator uses the functions `calculate_legacy_intro_pair` and `calculate_legacy_color_intro_parts` which contain formulas derived from reverse-engineering known-good files. Refer to the code comments within these functions for the specific logic discovered.

#### 3. RGB Color Data (300 Bytes per Segment)

Starts immediately after the last Duration Block (at the offset specified in Header 0x1A).
*   For *each* segment, the corresponding 3-byte RGB value (R, G, B; 0-255) is written **100 times** consecutively.
*   Total size per segment = 3 bytes/color * 100 repeats = 300 bytes.
*   Example: Segment 0 (Red `FF 00 00`), Segment 1 (Green `00 FF 00`)
    *   Data: `FF 00 00 FF 00 00 ... (100 times) ... 00 FF 00 00 FF 00 ... (100 times)`

#### 4. Footer (6 Bytes)

The file ends with a fixed 6-byte footer: `42 54 00 00 00 00` ('BT\x00\x00\x00\x00').

### File Size Calculation

The total size of a `.prg` file can be calculated structurally based on the number of segments (N):

`File Size (bytes) = HEADER_SIZE + (N * DURATION_BLOCK_SIZE) + (N * RGB_DATA_SIZE) + FOOTER_SIZE`
`File Size (bytes) = 32 + (N * 19) + (N * 300) + 6`
`File Size (bytes) = 38 + N * 319`

### Implementation Notes

*   **Segment Splitting:** The `.prg` format uses a 2-byte field (`<H`) for segment durations, limiting each block to 65535 time units. If a segment's calculated duration in the JSON exceeds this, the `split_long_segments` function automatically breaks it into multiple consecutive `.prg` segments of the same color, ensuring the total duration is preserved within the format's limits.
*   **HSV Conversion:** If `color_format` is "hsv", colors are converted to RGB before being written.
*   **Debugging Output:** The script provides verbose output during generation, showing calculated values and file offsets.

---

## License

This project is open source and available under the MIT License. (You may want to include the actual license text in a separate LICENSE file).

## Acknowledgements

The LTX ball control protocol and `.prg` file format details were determined through reverse engineering, analysis of network traffic and existing files, and community collaboration. Special thanks to contributions that helped refine the understanding of the complex index value calculations in the `.prg` format.
```