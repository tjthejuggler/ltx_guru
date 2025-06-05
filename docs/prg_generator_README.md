# LTX Guru Tools - PRG Generator Documentation

**Last Updated:** 2025-06-05 19:30 UTC+7

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

## LTX Ball PRG Generators (Sequence Files)

### LTX Ball PRG Generator (`prg_generator.py`)

A Python script (`prg_generator.py`) that converts JSON files describing color sequences into the binary `.prg` format used by LTX programmable juggling balls. **This generator always produces `.prg` files with a 100Hz refresh rate.** The `refresh_rate` specified in the input JSON is used to interpret the time units for `sequence` keys and `end_time`; these JSON-based timings are then automatically scaled by the script to match the 100Hz timing of the output `.prg` file.

This script incorporates the latest understanding of PRG header fields and **now supports both solid color segments and fade effects**, including:
- **N=1 Full Program Fades**: Single fade sequences that use the entire program duration for smooth color transitions
- **Embedded Fades**: Fade segments within mixed sequences that are compressed to 100 PRG units (1 second at 100Hz)
- **Mixed Sequences**: Combinations of solid colors and embedded fades

The generator automatically detects the sequence type and applies the appropriate PRG format rules based on analysis of official app-generated files.

**Important Note on Previous 1Hz Experiment (relevant to older `prg_generator_new.py`):** An earlier script, potentially named `prg_generator_new.py`, experimented with a 1Hz PRG refresh rate, attempting to use the 100 internal color slots of a PRG segment for high-frequency changes. This experiment **failed**, as the LTX firmware appears to only use the *first* color slot in such a 1Hz configuration. For high-granularity timing, a PRG file refresh rate like 100Hz (as used by this generator) or potentially higher is necessary.

#### Usage (`prg_generator.py`)

```bash
python3 prg_generator.py input.json output_100hz.prg
# The --use-gaps option for inserting black gaps (if needed) is still available:
python3 prg_generator.py input.json output_100hz_with_gaps.prg --use-gaps
```

*   `input.json`: Path to the JSON file. The `refresh_rate` and `end_time` in this JSON are used to define the sequence timing, which the script then converts to the 100Hz PRG scale.
*   `output_100hz.prg`: Path for the generated 100Hz `.prg` file.

#### JSON Input Format

The generator accepts a JSON file defining the color sequence and timing.

##### Basic Structure

```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 100, // Defines timing base for this JSON's sequence and end_time
  "end_time": 207,     // In JSON time units
  "sequence": {
    "0": {"color": [255, 0, 0], "pixels": 4}, // Start time in JSON time units
    "63": {"color": [0, 0, 255], "pixels": 4}  // Start time in JSON time units
  }
}
```

##### Fields Explained

*   `default_pixels` (Integer, 1-4): The number of LEDs (1 to 4) to light up for a segment if the `pixels` key is not specified within that segment's definition. Defaults to 1 if this field is omitted entirely. This value populates Header field `0x08`.
*   `color_format` (String, `"rgb"` or `"hsv"`): Specifies the format used for the `color` values in the `sequence`. If `"hsv"`, the generator converts colors to RGB before writing to the `.prg` file. Defaults to `"rgb"`.
    *   RGB: `[R, G, B]` where R, G, B are 0-255.
    *   HSV: `[H, S, V]` where H (Hue) is 0-360, S (Saturation) is 0-100, V (Value/Brightness) is 0-100.
*   `refresh_rate` (Integer, Hz, in JSON): **Crucial for interpreting JSON timings.** Defines the timing resolution for the `sequence` keys and `end_time` *within this JSON file*. The script uses this value to correctly scale these timings to the **fixed 100Hz output PRG refresh rate.**
    *   Example: If JSON `refresh_rate` is 100, a JSON time unit is 0.01s. If JSON `refresh_rate` is 1000, a JSON time unit is 0.001s.
    *   The PRG file itself will always be 100Hz (meaning a PRG time unit is 0.01s).
*   `end_time` (Integer or Float, **JSON time units**): The total duration of the *entire sequence* in **JSON time units**, relative to the JSON `refresh_rate`. This value dictates the end time (and thus duration) of the very last segment in the `sequence`. Required if you want the sequence to end. **Note:** Fractional values in the JSON for `end_time` will be rounded to the nearest integer JSON time unit before scaling.
*   `sequence` (Object): A dictionary defining the color changes over time.
    *   **Keys:** Strings representing the **start time** of a color segment, measured in **JSON time units** (relative to the JSON `refresh_rate`). Can be integers or floating-point numbers, but will be rounded to the nearest integer JSON time unit before scaling.
        *   `JSON Time Units = Time in Seconds * json_refresh_rate`
    *   **Values:** An object defining the segment starting at that time key:
        *   **For Solid Color Segments:**
            *   `color` (Array): The color for the segment, in the format specified by `color_format`.
            *   `pixels` (Integer, optional, 1-4): Number of pixels for this specific segment. Overrides `default_pixels`.
        *   **For Fade Segments:**
            *   `start_color` (Array): The starting color for the fade, in the format specified by `color_format`.
            *   `end_color` (Array): The ending color for the fade, in the format specified by `color_format`.
            *   `pixels` (Integer, optional, 1-4): Number of pixels for this specific segment. Overrides `default_pixels`.

#### Example 1: Precise Timing (Red 0.63s, Blue 1.44s) with matching JSON and PRG rates

Input JSON (`input_100rr.json`):
```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 100, // Input sequence timing base is 100Hz
  "end_time": 207,     // 207 units @ 100Hz JSON rate = 2.07s
  "sequence": {
    "0": {"color": [255, 0, 0]},
    "63": {"color": [0, 0, 255]}
  }
}
```
Command: `python3 prg_generator.py input_100rr.json example_output_100hz.prg`

*Resulting `example_output_100hz.prg` (100Hz PRG file):*
*   JSON `refresh_rate` (100Hz) matches the target PRG `refresh_rate` (100Hz), so the scaling factor is `100/100 = 1`.
*   Segment 1 (Red): JSON duration 63 units. PRG duration `round(63 * 1)` = 63 units (0.63s @ 100Hz).
*   Segment 2 (Blue): JSON duration `207 - 63` = 144 units. PRG duration `round(144 * 1)` = 144 units (1.44s @ 100Hz).
*   The PRG header will specify 100Hz.

#### Example 2: Red 0.05s, then Blue 0.1s (Scaling from 1000Hz JSON to 100Hz PRG)

Input JSON (`input_1000rr.json`):
```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 1000, // JSON times are in 0.001s units (1ms)
  "end_time": 150,       // Total 0.15s (50 units Red + 100 units Blue @ 1000Hz JSON rate)
  "sequence": {
    "0": {"color": [255, 0, 0], "pixels": 4},  // Red starts at 0s
    "50": {"color": [0, 0, 255], "pixels": 4}   // Blue starts at 0.05s (50 * 0.001s)
  }
}
```
Command: `python3 prg_generator.py input_1000rr.json example_output_100hz.prg`

Resulting `example_output_100hz.prg` will be a **100Hz** PRG file with:
*   JSON `refresh_rate` = 1000Hz. Target PRG `refresh_rate` = 100Hz.
*   Scaling factor = `TARGET_PRG_RATE / JSON_RATE` = `100 / 1000 = 0.1`.
*   Segment 1 (Red):
    *   JSON duration: 50 units (at 1000Hz) = 50ms.
    *   PRG duration: `round(50 * 0.1)` = 5 units (at 100Hz) = 50ms.
*   Segment 2 (Blue):
    *   JSON duration: `150 - 50` = 100 units (at 1000Hz) = 100ms.
    *   PRG duration: `round(100 * 0.1)` = 10 units (at 100Hz) = 100ms.
*   The PRG header will specify 100Hz. Header fields `0x16` and `0x1E` will be calculated based on the first segment's PRG duration (5 units).

#### Example 3: N=1 Full Program Fade (Red to Blue over 3 seconds)

Input JSON (`fade_red_blue_3s.json`):
```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 100,
  "end_time": 300,
  "sequence": {
    "0": {
      "start_color": [255, 0, 0],
      "end_color": [0, 0, 255]
    }
  }
}
```
Command: `python3 prg_generator.py fade_red_blue_3s.json fade_output.prg`

*Resulting `fade_output.prg` (100Hz PRG file):*
*   **N=1 True Fade Mode**: Single fade segment with 300 PRG units duration
*   **Header fields**: `0x16` = 300, `0x18` = 300 (actual duration, not 100)
*   **RGB Data**: 300 interpolated RGB steps from red to blue (900 bytes total)
*   **Duration Block**: Special Index2 calculation: Part1 = (3×300)+4 = 904, Part2 = 300

#### Example 4: Mixed Sequence with Embedded Fade

Input JSON (`mixed_solid_fade.json`):
```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 100,
  "end_time": 500,
  "sequence": {
    "0": {"color": [255, 0, 0]},
    "100": {
      "start_color": [255, 0, 0],
      "end_color": [0, 0, 255]
    },
    "300": {"color": [0, 255, 0]}
  }
}
```
Command: `python3 prg_generator.py mixed_solid_fade.json mixed_output.prg`

*Resulting `mixed_output.prg` (100Hz PRG file):*
*   **Standard Mode**: 3 segments (solid red, embedded fade, solid green)
*   **Segment 1**: 100 PRG units solid red (300 bytes RGB data)
*   **Segment 2**: 100 PRG units embedded fade (300 bytes interpolated RGB data, compressed from 200 JSON units)
*   **Segment 3**: 200 PRG units solid green (300 bytes RGB data)
*   **Header fields**: `0x16` = 1, `0x18` = 100 (standard values)

### `.prg` File Format Specification

The binary `.prg` files have the following structure. Multi-byte values are **Little Endian** unless specified otherwise.

#### Overall Structure

1.  **Header** (32 bytes)
2.  **Duration Blocks** (19 bytes * number of segments)
3.  **RGB Data** (300 bytes * number of segments)
4.  **Footer** (6 bytes)

#### 1. Header (32 Bytes)

| Offset (Hex) | Length | Field Name                                | Data Type | Endian | Details & Example (N=Number of Segments)        |
| :----------- | :----- | :---------------------------------------- | :-------- | :----- | :---------------------------------------------- |
| 0x00         | 8      | File Signature                            | `bytes`   | N/A    | `50 52 03 49 4E 05 00 00` ('PR\x03IN\x05\x00\x00') |
| 0x08         | 2      | Default Pixel Count                       | `H`       | Big    | Ex: `00 04` (4 pixels)                        |
| 0x0A         | 2      | Constant 0x0A                             | `bytes`   | N/A    | `00 08`                                       |
| 0x0C         | 2      | Refresh Rate (Hz)                         | `H`       | Little | Ex: `64 00` (100 Hz). This generator always writes 100Hz. |
| 0x0E         | 2      | Constant Marker "PI"                      | `bytes`   | N/A    | `50 49` ('PI')                                |
| 0x10         | 4      | Pointer1                                  | `I`       | Little | Ex: `28 00 00 00` (40 for N=2). Formula: `21 + 19*(N-1)` |
| 0x14         | 2      | Segment Count (N)                         | `H`       | Little | Ex: `02 00` (2 segments). Directly stores N; confirmed for N > 255 (e.g., `01 01` for 257 segments). |
| 0x16         | 2      | Header First Segment Info                 | `H`       | Little | Conditional, see logic below. Ex: `00 00` (if N=2, Dur0Units=1); `01 00` (if Dur0Units=100) |
| 0x18         | 2      | RGB Data Repetition Count                 | `H`       | Little | `64 00` (100 LE)                              |
| 0x1A         | 2      | RGB Data Start Offset                     | `H`       | Little | Ex: `46 00` (70 for N=2). Formula: `32 + N * 19` |
| 0x1C         | 2      | Constant 0x1C                             | `bytes`   | N/A    | `00 00`                                       |
| 0x1E         | 2      | Header First Segment Duration (Conditional) | `H`      | Little | Conditional, see logic below. Ex: `01 00` (if N=2, Dur0Units=1); `00 00` (if Dur0Units=100) |

*Data Types:* `H`=Unsigned Short (2 bytes), `I`=Unsigned Int (4 bytes).
*Pointer1 Calculation:* `32 + (N-1)*19 - 11 = 21 + 19*(N-1)`. This points to 11 bytes *before* the start of the last duration block.
*RGB Start Offset Calculation:* `HEADER_SIZE + N * DURATION_BLOCK_SIZE = 32 + N * 19`.
*RGB Data Repetition Count:* Always 100. Defines how many times each 3-byte RGB color is repeated for its segment's color data.

**Field `0x16` (Header First Segment Info) Logic (Revised 2025-06-02, after K & L series):**
Let `Dur0Units_actual` be the duration of the first PRG segment (Segment 0) in PRG time units.
Let `NominalBase = 100`.
Let `val_0x16_dec` be the decimal value calculated for this field.

  `val_0x16_dec = floor(Dur0Units_actual / NominalBase)`

*This logic holds universally across all tests (A-L, N=1 and N>1, various refresh rates).*
The byte value written to the file is `struct.pack('<H', val_0x16_dec)`.

**Field `0x1E` (Header First Segment Duration (Conditional)) Logic (Revised 2025-06-02, after S-V and additional tests):**
Let `Dur0Units_actual` and `NominalBase (=100)` be defined as above.
Let `N_prg` be the total number of PRG segments in the file.
Let `val_0x1E_dec` be the decimal value calculated for this field.

1.  **If `N_prg == 1` (Single Segment):**
    *   If `Dur0Units_actual == NominalBase` (i.e., 100): `val_0x1E_dec = 0`.
    *   Else if `Dur0Units_actual % NominalBase == 0` (i.e., `Dur0Units_actual` is a multiple of 100 but not 100 itself):
        *   If `Dur0Units_actual <= 400`: `val_0x1E_dec = 0`. (Updated from 300 based on S2 test where 400ms gave 0).
        *   Else (`Dur0Units_actual >= 500`): `val_0x1E_dec = Dur0Units_actual`. (Threshold is between 400 and 500).
    *   Else (`Dur0Units_actual % NominalBase != 0`):
        `val_0x1E_dec = Dur0Units_actual % NominalBase`.

2.  **If `N_prg > 1` (Multiple Segments):**
    *   If `Dur0Units_actual == 1000` (specific value, as seen in `red_1s_blue_.5s_1000r.prg`):
        `val_0x1E_dec = 1000`.
    *   Else if `Dur0Units_actual % NominalBase == 0` (i.e., `Dur0Units_actual` is a multiple of 100, e.g., 100, 200):
        `val_0x1E_dec = 0`. (Covers `red_100s_blue_50s_1r.prg` and Test Q3).
    *   Else (`Dur0Units_actual % NominalBase != 0`):
        `val_0x1E_dec = Dur0Units_actual % NominalBase`. (Confirmed by Q4, where Dur0=170 -> 0x1E=70)

*This refined logic for Header Field 0x1E is based on analysis of all tests up to and including the S-V series and additional header `0x1E` specific tests.*
The byte value written to the file for Field `0x1E` is `struct.pack('<H', val_0x1E_dec & 0xFFFF)`.

#### 2. Duration Blocks (19 Bytes per Segment)

One block exists for each segment, immediately following the header. Let N be the total segment count. Segments are 0-indexed (Segment 0 to Segment N-1).

**Structure for Segments 0 to N-2 (Intermediate Blocks):**

| Offset (Relative to block start) | Length | Field Name                            | Data Type | Endian | Details (Example values may vary based on context)        |
| :------------------------------- | :----- | :------------------------------------ | :-------- | :----- | :--------------------------------------------------------- |
| +0x00                            | 2      | Pixel Count                           | `H`       | Little | Pixels for *this* segment (1-4). Ex: `02 00` (2 pixels)   |
| +0x02                            | 3      | Block Constant 0x02                   | `bytes`   | N/A    | `01 00 00`                                                 |
| +0x05                            | 2      | Current Segment Duration Units        | `H`       | Little | Duration (units) of *this* segment. Ex: `64 00` (100 units) |
| +0x07                            | 2      | Block Constant 0x07                   | `bytes`   | N/A    | `00 00`                                                    |
| +0x09                            | 4      | Field[+0x09] (NextSegDur/100 & Const) | `bytes`   | N/A    | Two 2-byte LE values. See logic below. Ex: `01 00 64 00` |
| +0x0D                            | 2      | Index1 Value (Lower 16 bits)          | `H`       | Little | Lower 16 bits of a calculated index value. Example: `4C 14` for value `0x144C`. |
| +0x0F                            | 2      | Index1 Value (Higher 16 bits / Carry) | `H`       | Little | Higher 16 bits (carry) of the Index1 value. Example: `01 00` for value `0x1144C`. Formerly thought to be `00 00`. |
| +0x11                            | 2      | Next Segment Info (Conditional)       | `H`       | Little | Duration of next segment, with conditions. See logic below. Ex: `00 00` if next segment is 100 units. |

**Field `+0x09` (Next Segment Duration Info & Constant) Logic for Intermediate Blocks (Revised 2025-06-03):**
This 4-byte field (at offset `+0x09` from the start of an intermediate duration block) consists of two 2-byte Little Endian values: `field_09_part1` followed by `field_09_part2`.

*   **`field_09_part1`:**
    *   **Hypothesis (Official App Tests A-V, 1000Hz):** For an intermediate duration block `k` (describing segment `k`), if the *next* segment (segment `k+1`) has a duration `Dur_k+1` (in PRG time units):
        **`field_09_part1 (for block k) = floor(Dur_k+1 / 100)`**
    *   **Status:** Confirmed robustly across all 1000Hz tests (A-V, M-R, S-V, DB_11).

*   **`field_09_part2`:**
    *   **Observation (Official App Tests A-V, 1000Hz):** For all intermediate duration blocks (segments 0 to N-2), `field_09_part2` is consistently `64 00` (decimal 100).
    *   **Status:** Confirmed.

**Field `+0x11` (Next Segment Info (Conditional)) Logic for Intermediate Blocks (Current Segment `k`) (Revised 2025-06-03):**
Let `Dur_k+1` be the duration of the next segment (segment `k+1`) in PRG time units.
Let `Dur_k` be the duration of the current segment (segment `k`).
The value for `Field[+0x11]` in Block `k` is determined by the first matching rule in the following priority:

1.  **Special Overrides:**
    *   If `Dur_k+1 == 1930`: `Field[+0x11]` is `1E 00` (decimal 30). (Confirmed by Test L series, R2).
    *   Else if `Dur_k+1 == 103`: `Field[+0x11]` is `03 00` (decimal 3). (Confirmed by Test M series).

2.  **`Dur_k+1` is Exactly 100:**
    *   Else if `Dur_k+1 == 100`: `Field[+0x11]` is `00 00` (decimal 0). (Confirmed by Test E, N25x_all_100ms series, DB_11_B1, DB_11_C1).

3.  **`Dur_k+1` is a Multiple of 100 (and `Dur_k+1 > 100`):**
    *   Else if `Dur_k+1 > 100` AND `Dur_k+1 % 100 == 0`:
        *   If `Dur_k == Dur_k+1` (e.g., current segment is 600ms, next is 600ms): `Field[+0x11] = Dur_k+1`. (e.g., Test DB_11_B4: 600/600 -> 600; L6: 1000/1000 -> 1000).
        *   Else if `Dur_k >= 1000` AND `Dur_k+1 >= 600` (e.g., current segment is 1000ms, next is 600ms): `Field[+0x11] = Dur_k+1`. (e.g., Test L5: Block 0 for (1000ms, 600ms) sequence has +0x11 = 600).
        *   Else (e.g., current 50ms, next 200ms; or current 200ms, next 600ms where `Dur_k` < 1000): `Field[+0x11] = 0`. (e.g., Tests Q3, U1-U3, DB_11_B1/B2/B3, DB_11_C1/C2/C3).

4.  **`Dur_k+1` is Exactly 150:**
    *   Else if `Dur_k+1 == 150`:
        *   If `Dur_k >= 100`: `Field[+0x11] = 150`. (Pattern B behavior, e.g., Test H3, DB_11_A3/A4/A5).
        *   Else (`Dur_k < 100`): `Field[+0x11] = 50` (Pattern A: `150 % 100`, e.g., Test T5, DB_11_A1/A2).

5.  **`Dur_k+1` is Less Than 100 (and not 103 from Rule 1):**
    *   Else if `Dur_k+1 < 100`: `Field[+0x11] = Dur_k+1`. (e.g., Test H1, K1, K3).

6.  **Fallback for `Dur_k+1 > 100` (and not covered by Rules 1, 3, or 4):**
    *   Else (covers cases like `Dur_k+1` = 101, 102, 104, 120, 140, 149, 151, 199, 201, 470, etc.):
        *   If `Dur_k >= 100`: `Field[+0x11] = Dur_k+1` (Pattern B: direct passthrough, e.g., Test A Block 0, K4-K8, DB_11_A3).
        *   Else (`Dur_k < 100`): `Field[+0x11] = Dur_k+1 % 100` (Pattern A: modulo, e.g., Test P2, T1-T4, T6, V-series).

*   **Note on Patterns:** "Pattern A" generally refers to `Dur_k+1 % 100` when `Dur_k+1 > 100`. "Pattern B" refers to direct passthrough (`Dur_k+1`). The interaction with `Dur_k` determines which pattern applies for some `Dur_k+1` values. The rules above are ordered by priority.

**Structure for Segment N-1 (LAST Block):**

This is the final duration block in the sequence.

| Offset (Relative to block start) | Length | Field Name                                 | Data Type | Endian | Details (Example values may vary)                      |
| :------------------------------- | :----- | :----------------------------------------- | :-------- | :----- | :---------------------------------------------------- |
| +0x00                            | 2      | Pixel Count                                | `H`       | Little | Pixels for *this* segment (1-4). Ex: `02 00` (2 pixels) |
| +0x02                            | 3      | Block Constant 0x02                        | `bytes`   | N/A    | `01 00 00`                                            |
| +0x05                            | 2      | Current Segment Duration Units             | `H`       | Little | Duration (units) of *this* segment. Ex: `63 00` (99 units) |
| +0x07                            | 2      | Block Constant 0x07                        | `bytes`   | N/A    | `00 00`                                               |
| +0x09                            | 2      | Last Block Constant 0x09                   | `bytes`   | N/A    | `43 44` ('CD')                                        |
| +0x0B                            | 2      | Index2 Part 1 (Lower 16 bits)              | `H`       | Little | Lower 16 bits of a calculated index value. Example: `30 2D` for value `0x12D30`. |
| +0x0D                            | 2      | Index2 Part 1 (Higher 16 bits / Carry)     | `H`       | Little | Higher 16 bits (carry) of Index2 Part 1. Example: `01 00` for value `0x12D30`. Formerly `00 00`. |
| +0x0F                            | 2      | Index2 Part 2 (Lower 16 bits)              | `H`       | Little | Lower 16 bits of a second calculated index value. Example: `64 64` for value `0x6464`. |
| +0x11                            | 2      | Index2 Part 2 (Higher 16 bits / Carry)     | `H`       | Little | Higher 16 bits (carry) of Index2 Part 2. Example: `00 00` for value `0x6464`. Formerly `00 00`. |

**Index Value Calculation (Known Complexities):**
The `Index1 Value` (split across `+0x0D` and `+0x0F` in intermediate blocks), and `Index2 Part 1` / `Part 2` (split across `+0x0B`/`+0x0D` and `+0x0F`/`+0x11` respectively in the last block) are crucial for the firmware to correctly step through the sequence. Their calculation is based on arithmetic progressions (see `_calculate_intermediate_block_index1_base` and `_calculate_last_block_index2_bases` in the code). These progressions can result in values exceeding 16 bits. The lower 16 bits are stored in the primary field (`+0x0D` or `+0x0B`/`+0x0F`), and the higher 16 bits (effectively a carry or page counter) are stored in the adjacent field that was previously believed to be a constant zero (`+0x0F` for intermediate blocks, or `+0x0D`/`+0x11` for the last block). This behavior becomes apparent in sequences with a large number of segments. Refer to the code comments within these functions for the specific arithmetic logic discovered.

#### 3. RGB Color Data (Variable Size per Segment)

Starts immediately after the last Duration Block (at the offset specified in Header `0x1A`). The size and content depend on the segment type:

**Solid Color Segments (300 bytes each):**
*   For *each* solid segment, the corresponding 3-byte RGB value (R, G, B; 0-255) is written **100 times** consecutively.
*   Total size per segment = 3 bytes/color * 100 repeats = 300 bytes.
*   Example: Segment 0 (Red `FF 00 00`), Segment 1 (Green `00 FF 00`)
    *   Data: `FF 00 00 FF 00 00 ... (100 times) ... 00 FF 00 00 FF 00 ... (100 times)`

**N=1 Full Program Fade Segments (duration × 3 bytes):**
*   For a single fade segment spanning the entire program, RGB values are interpolated across the fade duration.
*   Each PRG time unit gets one interpolated RGB triple.
*   Total size = fade_duration_prg_units × 3 bytes.
*   Example: 300 PRG unit fade from Red to Blue
    *   Data: `FF 00 00 FE 00 01 FD 00 02 ... (300 interpolated steps) ... 00 00 FF`

**Embedded Fade Segments (300 bytes each):**
*   For fade segments within mixed sequences, RGB values are interpolated across exactly 100 steps.
*   Total size = 100 steps × 3 bytes = 300 bytes (same as solid segments).
*   The fade speed is determined by the JSON duration, but the PRG block always uses 100 interpolated steps.
*   Example: Red to Blue embedded fade
    *   Data: `FF 00 00 FC 00 03 F9 00 06 ... (100 interpolated steps) ... 00 00 FF`

**Interpolation Formula:**
For fade segments, each RGB component is calculated as:
```
r = start_r + step * (end_r - start_r) / (total_steps - 1)
g = start_g + step * (end_g - start_g) / (total_steps - 1)
b = start_b + step * (end_b - start_b) / (total_steps - 1)
```
Where `step` ranges from 0 to `total_steps - 1`, and values are rounded and clamped to 0-255.

*   **Note on Color Order:** Observations of filenames vs. hex data (e.g., "blue" in filename corresponding to `00 FF 00` which is Green in standard RGB) suggest the possibility that the device or generating software might use a different color component order (e.g., GBR or BGR) internally than standard RGB for some colors, or filenames might not perfectly reflect the stored RGB. For generating specific colors, verify the component order expected by the device.

#### 4. Footer (6 Bytes)

The file ends with a fixed 6-byte footer: `42 54 00 00 00 00` ('BT\x00\x00\x00\x00').

### File Size Calculation

The total size of a `.prg` file depends on the segment types and must be calculated dynamically:

**Base Formula:**
`File Size (bytes) = HEADER_SIZE + (N × DURATION_BLOCK_SIZE) + (Total RGB Data Size) + FOOTER_SIZE`
`File Size (bytes) = 32 + (N × 19) + (Total RGB Data Size) + 6`

**RGB Data Size by Segment Type:**
*   **Solid Color Segments**: 300 bytes each (`100 × 3`)
*   **N=1 Full-Program Fade**: `duration × 3` bytes (where duration is PRG time units)
*   **Embedded Fade Segments**: 300 bytes each (`100 × 3`)

**Calculation Examples:**

1. **Traditional Solid Color Sequence (N segments):**
   `File Size = 38 + N × 319`

2. **N=1 Full-Program Fade (300 PRG units):**
   `File Size = 32 + (1 × 19) + (300 × 3) + 6 = 957 bytes`

3. **Mixed Sequence (2 solid + 1 embedded fade):**
   `File Size = 32 + (3 × 19) + (2 × 300) + (1 × 300) + 6 = 995 bytes`

4. **N=1 Full-Program Fade (Maximum 65535 PRG units):**
   `File Size = 32 + (1 × 19) + (65535 × 3) + 6 = 196,662 bytes`

**Dynamic Calculation Logic:**
```
Total RGB Data Size = 0
For each segment:
    If segment_type == 'fade' and N == 1:
        Total RGB Data Size += fade_duration × 3
    Else:  // solid or embedded fade
        Total RGB Data Size += 300
```

This dynamic approach ensures accurate file size prediction regardless of the mix of segment types in the sequence.

### Implementation Notes

*   **Timing Precision Rounding:** JSON timing values (`sequence` keys and `end_time`) can be fractional. They are first rounded to the nearest integer JSON time unit. These integer JSON time units are then scaled to target PRG time units (for the 100Hz output). The result of this scaling is rounded again to obtain integer PRG time units. This two-step rounding ensures compatibility with the PRG format's integer-based timing. Any rounding adjustments are logged during generation.
*   **Segment Splitting:** The `.prg` format uses a 2-byte field (`<H`) for segment durations in duration blocks, limiting each block to 65535 PRG time units (at 100Hz, this is 655.35 seconds). If a segment's calculated duration *in PRG time units* (after scaling from JSON) exceeds this, the `split_long_segments` function automatically breaks it into multiple consecutive `.prg` segments of the same color, ensuring the total duration is preserved within the format's limits.
*   **HSV Conversion:** If `color_format` is "hsv", colors are converted to RGB before being written.
*   **Debugging Output:** The script provides verbose output during generation, showing calculated values and file offsets.
*   **Automatic Black Gaps:** To prevent strobing effects on hardware with non-instantaneous color changes, the script can insert a 1ms black segment before each change to a new, different color if the segment is long enough. This behavior is **disabled by default** and can be enabled with the `--use-gaps` flag. Note that this is not an acceptable fix, this information is only here to help understand the nature of the issue.
*   **Important Note on Duration Block Field `+0x09` (Updated 2025-06-03):**
    The logic for `Field[+0x09]` (composed of `field_09_part1` and `field_09_part2`) has been refined. `field_09_part1` is now understood to be `floor(Dur_k+1 / 100)` (where `Dur_k+1` is the duration of the next segment *in PRG time units*), and `field_09_part2` is consistently `100` (`64 00`) for intermediate blocks. This logic is robustly confirmed by all 1000Hz official app tests and ensures correct PRG generation.

---

## License

This project is open source and available under the MIT License. (You may want to include the actual license text in a separate LICENSE file).

## Acknowledgements

The LTX ball control protocol and `.prg` file format details were determined through reverse engineering, analysis of network traffic and existing files, and community collaboration. Special thanks to contributions that helped refine the understanding of the complex index value calculations and conditional fields in the `.prg` format.
```