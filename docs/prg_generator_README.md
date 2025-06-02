# LTX Guru Tools - PRG Generator Documentation

**Last Updated:** 2025-06-02 10:35 UTC+7

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

### Standard PRG Generator (`prg_generator.py`)

A Python script (`prg_generator.py`) that converts JSON files describing color sequences into the binary `.prg` format used by LTX programmable juggling balls, where the PRG file's `refresh_rate` is taken directly from the JSON.

#### Usage (`prg_generator.py`)

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

*   `default_pixels` (Integer, 1-4): The number of LEDs (1 to 4) to light up for a segment if the `pixels` key is not specified within that segment's definition. Defaults to 1 if this field is omitted entirely. This value populates Header field `0x08`.
*   `color_format` (String, `"rgb"` or `"hsv"`): Specifies the format used for the `color` values in the `sequence`. If `"hsv"`, the generator converts colors to RGB before writing to the `.prg` file. Defaults to `"rgb"`.
    *   RGB: `[R, G, B]` where R, G, B are 0-255.
    *   HSV: `[H, S, V]` where H (Hue) is 0-360, S (Saturation) is 0-100, V (Value/Brightness) is 0-100.
*   `refresh_rate` (Integer, Hz): **Crucial for timing.** Defines the timing resolution, determining how many "time units" occur per second. Populates Header field `0x0C`.
    *   `1`: 1 time unit = 1 second.
    *   `100`: 1 time unit = 0.01 seconds (10ms).
    *   Formula: `Time Unit Duration (seconds) = 1 / refresh_rate`
*   `end_time` (Integer or Float, **time units**): The total duration of the *entire sequence* in **time units**. This value dictates the end time (and thus duration) of the very last segment in the `sequence`. Required if you want the sequence to end; otherwise, the last segment might have zero or default duration depending on implementation. **Note:** Fractional values will be rounded to the nearest integer to match refresh rate precision.
*   `sequence` (Object): A dictionary defining the color changes over time.
    *   **Keys:** Strings representing the **start time** of a color segment, measured in **time units**. Can be integers or floating-point numbers, but will be rounded to the nearest integer to match refresh rate precision.
        *   `Time Units = Time in Seconds * refresh_rate`
    *   **Values:** An object defining the segment starting at that time key:
        *   `color` (Array): The color for the segment, in the format specified by `color_format`.
        *   `pixels` (Integer, optional, 1-4): Number of pixels for this specific segment. Overrides `default_pixels`. Populates the `Pixel Count` field (`+0x00`) in the segment's Duration Block.

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
---

### High-Precision PRG Generator (`prg_generator.py`)

The `prg_generator.py` script is a **high-precision PRG generator that hardcodes the output PRG file's refresh rate to 1000Hz.** This allows for timing granularity down to 1 millisecond.

It incorporates the latest understanding of PRG header fields (see "Hypothesis 8" in the `.prg` File Format Specification section below) based on analysis of official app-generated files at both 1Hz and 1000Hz.

**Important Note on Previous 1Hz Experiment:** An earlier version of `prg_generator_new.py` experimented with a 1Hz PRG refresh rate, attempting to use the 100 internal color slots of a PRG segment for high-frequency changes. This experiment **failed**, as the LTX firmware appears to only use the *first* color slot in such a 1Hz configuration. For high-granularity timing, a high PRG file refresh rate (like 1000Hz) is necessary.

#### Usage (`prg_generator.py` - 1000Hz High-Precision Version)

```bash
python3 prg_generator.py input.json output_1000hz_no_gaps.prg # Default: no gaps
python3 prg_generator.py input.json output_1000hz_with_gaps.prg --use-gaps
```

*   `input.json`: Path to the JSON file. The `refresh_rate` and `end_time` in this JSON are used to define the sequence timing, which the script then converts to 1000Hz PRG time units.
*   `output_1000hz.prg`: Path for the generated 1000Hz `.prg` file.

#### JSON Input Format (for `prg_generator.py`)

The JSON input structure is the same as for `prg_generator.py`.
*   `refresh_rate` (in JSON): Interpreted as the input timing base (e.g., if 100, then a JSON time unit is 0.01s).
*   `end_time` (in JSON): Defines total duration in JSON time units.
*   The script calculates PRG segment durations by converting these JSON timings to the 1000Hz PRG scale.

#### Example: Red 0.05s, then Blue 0.1s (using `prg_generator.py`)

Input JSON (`input_example.json`):
```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 100, // JSON times are in 0.01s units
  "end_time": 15,       // Total 0.15s (5 units Red + 10 units Blue)
  "sequence": {
    "0": {"color": [255, 0, 0], "pixels": 4},  // Red starts at 0s
    "5": {"color": [0, 0, 255], "pixels": 4}   // Blue starts at 0.05s (5 * 0.01s)
  }
}
```
Command: `python3 prg_generator.py input_example.json example_output.prg`

Resulting `example_output.prg` will be a 1000Hz PRG file with:
*   Segment 1 (Red): Duration 50ms (50 units @ 1000Hz).
*   Segment 2 (Blue): Duration 100ms (100 units @ 1000Hz).
*   Header fields `0x16` and `0x1E` calculated according to "Hypothesis 8" using `Dur0Units_actual = 50`.

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
| 0x0C         | 2      | Refresh Rate (Hz)                         | `H`       | Little | Ex: `64 00` (100 Hz)                          |
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

**Field `0x16` (Header First Segment Info) Logic (Revised 2025-06-01, "Hypothesis 8"):**
Let `Dur0Units_actual` be the duration of the first PRG segment (Segment 0) in PRG time units (e.g., if PRG Refresh Rate is 1000Hz, then 1s duration means `Dur0Units_actual = 1000`).
Let `NominalBase = 100`. This value appears to be consistently used for these calculations.
Let `val_0x16_dec` be the decimal value calculated for this field.

  `val_0x16_dec = floor(Dur0Units_actual / NominalBase)`

*This logic applies universally, regardless of the number of PRG segments (`N_prg`) or the PRG file's refresh rate.*
*Examples:*
  * 1s duration @ 1Hz PRG Rate (N=1, Dur0Units_actual=1): `floor(1/100) = 0`. Field: `00 00`.
  * 100s duration @ 1Hz PRG Rate (N=1, Dur0Units_actual=100): `floor(100/100) = 1`. Field: `01 00`.
  * 0.01s duration @ 1000Hz PRG Rate (N=1, Dur0Units_actual=10): `floor(10/100) = 0`. Field: `00 00`.
  * 0.1s duration @ 1000Hz PRG Rate (N=1, Dur0Units_actual=100): `floor(100/100) = 1`. Field: `01 00`.
  * 1s duration @ 1000Hz PRG Rate (N=1, Dur0Units_actual=1000): `floor(1000/100) = 10`. Field: `0A 00`.
  * First segment 1s @ 1000Hz PRG Rate (N=2, Dur0Units_actual=1000): `floor(1000/100) = 10`. Field: `0A 00`.
The byte value written to the file is `struct.pack('<H', val_0x16_dec)`.

**Field `0x1E` (Header First Segment Duration (Conditional)) Logic (Revised 2025-06-01, "Hypothesis 8"):**
Let `Dur0Units_actual` and `NominalBase (=100)` be defined as above.
Let `val_0x16_dec` be the decimal value for field `0x16` calculated as `floor(Dur0Units_actual / NominalBase)`.
Let `val_0x1E_dec` be the decimal value calculated for this field.

  `calculated_remainder = Dur0Units_actual - (val_0x16_dec * NominalBase)`
  If `calculated_remainder == 0`:
    If `Dur0Units_actual == NominalBase` (i.e., `Dur0Units_actual` is exactly 100):
      `val_0x1E_dec = 0`
    Else (`Dur0Units_actual` is a multiple of 100, but not 100 itself e.g., 200, 500, 1000):
      `val_0x1E_dec = Dur0Units_actual`
  Else (`calculated_remainder != 0`):
    `val_0x1E_dec = calculated_remainder`

*This logic applies universally, regardless of `N_prg` or PRG file refresh rate.*
*Examples:*
  * 1s @ 1Hz (Dur0=1, val_0x16=0): `calc_rem=1`. `!=0`. val_0x1E=1. Field: `01 00`.
  * 100s @ 1Hz (Dur0=100, val_0x16=1): `calc_rem=0`. `Dur0 == 100`. val_0x1E=0. Field: `00 00`.
  * 0.01s @ 1000Hz (Dur0=10, val_0x16=0): `calc_rem=10`. `!=0`. val_0x1E=10. Field: `0A 00`.
  * 0.1s @ 1000Hz (Dur0=100, val_0x16=1): `calc_rem=0`. `Dur0 == 100`. val_0x1E=0. Field: `00 00`.
  * 0.5s @ 1000Hz (Dur0=500, val_0x16=5): `calc_rem=0`. `Dur0 != 100`. val_0x1E=500. Field: `F4 01`.
  * 1s @ 1000Hz (Dur0=1000, val_0x16=10): `calc_rem=0`. `Dur0 != 100`. val_0x1E=1000. Field: `E8 03`.
  * First seg 0.1s @ 1000Hz (N=2, Dur0=100, val_0x16=1): `calc_rem=0`. `Dur0 == 100`. val_0x1E=0. Field: `00 00`.
  * First seg 1s @ 1000Hz (N=2, Dur0=1000, val_0x16=10): `calc_rem=0`. `Dur0 != 100`. val_0x1E=1000. Field: `E8 03`.
The byte value written to the file is `struct.pack('<H', val_0x1E_dec & 0xFFFF)`.

#### 2. Duration Blocks (19 Bytes per Segment)

One block exists for each segment, immediately following the header. Let N be the total segment count. Segments are 0-indexed (Segment 0 to Segment N-1).

**Structure for Segments 0 to N-2 (Intermediate Blocks):**

| Offset (Relative to block start) | Length | Field Name                   | Data Type | Endian | Details (Example for Seg0 of N=2 file: `2px_r1_g99_1r`) |
| :------------------------------- | :----- | :--------------------------- | :-------- | :----- | :--------------------------------------------------------- |
| +0x00                            | 2      | Pixel Count                  | `H`       | Little | Pixels for *this* segment (1-4). Ex: `02 00` (2 pixels)   |
| +0x02                            | 3      | Block Constant 0x02          | `bytes`   | N/A    | `01 00 00`                                                 |
| +0x05                            | 2      | Current Segment Duration Units| `H`      | Little | Duration (units) of *this* segment. Ex: `01 00` (1 unit)   |
| +0x07                            | 2      | Block Constant 0x07          | `bytes`   | N/A    | `00 00`                                                    |
| +0x09                            | 4      | Segment Index & Duration     | `bytes`   | N/A    | Two 2-byte LE values. Part1: Conditional index. Part2: CurrentSegDurUnits. See logic below. |
| +0x0D                            | 2      | Index1 Value                 | `H`       | Little | Calculated by `calculate_legacy_intro_pair` (see code)     |
| +0x0F                            | 2      | Block Constant 0x0F          | `bytes`   | N/A    | `00 00`                                                    |
| +0x11                            | 2      | Next Segment Info (Conditional)| `H`     | Little | Duration of next segment, with conditions. See logic below. Ex: `63 00` (99 units for next seg) |

**Field `+0x09` (Segment Index & Duration) Logic for Intermediate Blocks (Current Generator Implementation as of 2025-06-02):**
Currently, for intermediate duration blocks (not the last one), the `prg_generator.py` script writes a static value of `00 00 64 00` for this 4-byte field.
    *   This decision was made after observing that implementing a more dynamic "Hypothesis I" for this field reintroduced unintentional strobing (see "Important Note on Duration Block Field `+0x09`" under "Implementation Notes" below).
    *   The static value `00 00 64 00` (effectively Part1 = `0`, Part2 = `100`) was the behavior of the generator prior to attempting Hypothesis I and was found to not cause strobing with the test sequences that exhibited issues.
    *   The exact reason why "Hypothesis I" caused strobing, and the full correct dynamic logic for this field (especially as seen in official app PRGs with complex sequences), requires further investigation.

**Field `+0x11` (Next Segment Info (Conditional)) Logic for Intermediate Blocks (Current Segment `k`) (Updated 2025-06-02 based on Hypothesis F):**
This 2-byte Little Endian field depends on the duration of the current segment (`Dur_k`, in PRG time units) and the next segment (`Dur_k+1`, in PRG time units).

1.  If `Dur_k+1 < 100`:
    *   `field_11_val = Dur_k+1`.
    *   *Example: CurrentSegDur=10, NextSegDur=99. `field_11_val = 99` (Hex: `63 00`).*
2.  Else if `Dur_k+1 == 100`:
    *   `field_11_val = 0`.
    *   *Example: CurrentSegDur=50, NextSegDur=100. `field_11_val = 0` (Hex: `00 00`).*
    *   *Example: CurrentSegDur=100, NextSegDur=100. `field_11_val = 0` (Hex: `00 00`).*
3.  Else (`Dur_k+1 > 100`):
    *   If `Dur_k == 100` (Current segment's duration is exactly 100 units):
        *   `field_11_val = 0`.
        *   *Example: CurrentSegDur=100, NextSegDur=101. `field_11_val = 0` (Hex: `00 00`).*
    *   Else (`Dur_k != 100`):
        *   `field_11_val = Dur_k+1`.
        *   *Example: CurrentSegDur=50, NextSegDur=101. `field_11_val = 101` (Hex: `65 00`).*
    *   *Note:* The official LTX app output for specific high segment counts (like N=258) shows deviations from this general hypothesis for certain blocks (e.g., idx=58 where `Field+0x11` is 95 due to Seg 59 duration being 95; idx=62 where `Field+0x11` is 85 even if Seg 63 is 100). These specific exceptions are not covered by the generator's current general logic.

**Structure for Segment N-1 (LAST Block):**

This is the final duration block in the sequence.

| Offset (Relative to block start) | Length | Field Name            | Data Type | Endian | Details (Example for Seg1 of N=2 file: `2px_r1_g99_1r`) |
| :------------------------------- | :----- | :-------------------- | :-------- | :----- | :---------------------------------------------------- |
| +0x00                            | 2      | Pixel Count           | `H`       | Little | Pixels for *this* segment (1-4). Ex: `02 00` (2 pixels) |
| +0x02                            | 3      | Block Constant 0x02   | `bytes`   | N/A    | `01 00 00`                                            |
| +0x05                            | 2      | Current Duration Units| `H`       | Little | Duration (units) of *this* segment. Ex: `63 00` (99 units) |
| +0x07                            | 2      | Block Constant 0x07   | `bytes`   | N/A    | `00 00`                                               |
| +0x09                            | 2      | Last Block Const 0x09 | `bytes`   | N/A    | `43 44` ('CD')                                        |
| +0x0B                            | 2      | Index2 Part 1         | `H`       | Little | Calculated by `calculate_legacy_color_intro_parts`      |
| +0x0D                            | 2      | Last Block Const 0x0D | `bytes`   | N/A    | `00 00`                                               |
| +0x0F                            | 2      | Index2 Part 2         | `H`       | Little | Calculated by `calculate_legacy_color_intro_parts`      |
| +0x11                            | 2      | Last Block Const 0x11 | `bytes`   | N/A    | `00 00`                                               |

**Index Value Calculation (Known Complexities):**
The `Index1 Value` (in intermediate blocks), `Index2 Part 1`, and `Index2 Part 2` (in the last block) fields are crucial for the firmware to correctly step through the sequence. Their calculation is non-trivial and depends on the total number of segments (N) and the current segment's index. The generator uses the functions `calculate_legacy_intro_pair` and `calculate_legacy_color_intro_parts` which contain formulas derived from reverse-engineering known-good files. Refer to the code comments within these functions for the specific logic discovered.

#### 3. RGB Color Data (300 Bytes per Segment)

Starts immediately after the last Duration Block (at the offset specified in Header `0x1A`).
*   For *each* segment, the corresponding 3-byte RGB value (R, G, B; 0-255) is written **100 times** consecutively.
*   Total size per segment = 3 bytes/color * 100 repeats = 300 bytes.
*   Example: Segment 0 (Red `FF 00 00`), Segment 1 (Green `00 FF 00`)
    *   Data: `FF 00 00 FF 00 00 ... (100 times) ... 00 FF 00 00 FF 00 ... (100 times)`
*   **Note on Color Order:** Observations of filenames vs. hex data (e.g., "blue" in filename corresponding to `00 FF 00` which is Green in standard RGB) suggest the possibility that the device or generating software might use a different color component order (e.g., GBR or BGR) internally than standard RGB for some colors, or filenames might not perfectly reflect the stored RGB. For generating specific colors, verify the component order expected by the device.

#### 4. Footer (6 Bytes)

The file ends with a fixed 6-byte footer: `42 54 00 00 00 00` ('BT\x00\x00\x00\x00').

### File Size Calculation

The total size of a `.prg` file can be calculated structurally based on the number of segments (N):

`File Size (bytes) = HEADER_SIZE + (N * DURATION_BLOCK_SIZE) + (N * RGB_DATA_SIZE) + FOOTER_SIZE`
`File Size (bytes) = 32 + (N * 19) + (N * 300) + 6`
`File Size (bytes) = 38 + N * 319`

### Implementation Notes

*   **Timing Precision Rounding:** The generator automatically rounds all timing values (sequence keys and `end_time`) to the nearest integer to ensure compatibility with the refresh rate precision. For example, with a 100Hz refresh rate, fractional timing values like `101.5` will be rounded to `102`. This prevents timing precision issues that could cause problems in the PRG generation process. Any rounding adjustments are logged during generation.
*   **Segment Splitting:** The `.prg` format uses a 2-byte field (`<H`) for segment durations in duration blocks, limiting each block to 65535 time units. If a segment's calculated duration in the JSON exceeds this, the `split_long_segments` function automatically breaks it into multiple consecutive `.prg` segments of the same color, ensuring the total duration is preserved within the format's limits.
*   **HSV Conversion:** If `color_format` is "hsv", colors are converted to RGB before being written.
*   **Debugging Output:** The script provides verbose output during generation, showing calculated values and file offsets.
*   **Automatic Black Gaps:** To prevent strobing effects on hardware with non-instantaneous color changes, the script can insert a 1ms black segment before each change to a new, different color if the segment is long enough. This behavior is **disabled by default** and can be enabled with the `--use-gaps` flag. Note that this is not an acceptable fix, this information is only here to help understand the nature of the issue.
*   **Official App Segment Duration Alterations:** For certain sequence lengths (e.g., N=258), the official LTX app may alter the duration of specific segments (e.g., segment at index 59 becomes 95ms instead of an input 100ms). This behavior is not yet fully understood or generalized in the generator.
*   **Important Note on Duration Block Field `+0x09` (as of 2025-06-02):**
    *   **Official App Behavior:** The official LTX app uses a dynamic system for Field `+0x09` in intermediate duration blocks, where its value changes based on sequence characteristics. This is evident from analyzing official PRG files.
    *   **Strobing Issue with "Hypothesis I":** An attempt on 2025-06-02 to implement a dynamic model ("Hypothesis I") for Field `+0x09` in `prg_generator.py` caused an unintentional strobing effect with certain test sequences.
    *   **Resolution & Current State:** To resolve the strobing, the logic for Field `+0x09` in intermediate duration blocks within `prg_generator.py` was reverted to its previous, simpler behavior of writing a static value (`00 00 64 00`). This successfully eliminated the strobing.
    *   **Conclusion:** While the official app uses a dynamic Field `+0x09`, our current understanding ("Hypothesis I") of that dynamic behavior is either incomplete or incorrect, leading to instability. The static value is a stable workaround. The "Hypothesis F" logic for Field `+0x11` (Next Segment Info) remains implemented. Further research is needed to fully understand the official app's dynamic logic for Field `+0x09` and replicate it safely.

---

## License

This project is open source and available under the MIT License. (You may want to include the actual license text in a separate LICENSE file).

## Acknowledgements

The LTX ball control protocol and `.prg` file format details were determined through reverse engineering, analysis of network traffic and existing files, and community collaboration. Special thanks to contributions that helped refine the understanding of the complex index value calculations and conditional fields in the `.prg` format.
```