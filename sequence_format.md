# LTX Ball Sequence File Format (.prg) – Definitive Guide

This document is the definitive reference for constructing valid .prg sequence files for LTX Balls. Every byte matters; even a one‐byte error can result in unintended behavior. The guide explains the file’s structure, the proper method for generating its sections (with a special focus on the pixel data block), and how to verify the output using standard hex dump tools.

---

## 1. Overview

A typical .prg sequence file consists of three main parts:
- **Header Section:** Contains magic numbers, version info, pixel count, and timing/segment data.
- **Pixel Data (CD) Section:** Contains the color information as a continuous stream of RGB values.
- **Footer Section:** Contains an end marker.

**Important:**  
- The overall file size must exactly equal the sum of these sections.  
- For many examples (such as a 1px or 4px sequence with a single segment lasting 10 seconds), the standard layout is:  
  - Header: 48 bytes  
  - Pixel Data Block: 304 bytes  
  - Footer: 5 bytes  
  - **Total:** 48 + 304 + 5 = 357 bytes (0x165)

---

## 2. Header Section

### 2.1 Fixed Fields

- **Magic & Version:**  
  - Bytes 0–1: `"PR"` (0x50 0x52)  
  - Byte 2: Version number (e.g., 0x03)  
  - Bytes 3–4: `"IN"` (0x49 0x4E)

- **Configuration:**  
  Following the magic, fixed configuration bytes appear. For example, a sample header might include:
  ```
  05 00 00 00 04 00 08
  ```
  where the field representing the pixel count is critical.

### 2.2 Setting the Number of Pixels

- **Pixel Count Field(s):**  
  - At offset 0x08, the pixel count is stored.  
    - For a 1-pixel file, use `00 01`.  
    - For a 2-pixel file, use `00 02`.  
    - For a 4-pixel file, use `00 04`.
  - Later in the header (often around offset 0x20), the pixel count appears again in little‑endian order.  
    - For example, for 1 pixel: `01 00`; for 4 pixels: `04 00`.

- **Timing and Segment Info:**  
  The header also contains timing values (e.g., `64 00` might indicate a base timing unit of 0.1 seconds—so 0x64 [100] represents 10 seconds).  
  - Typically, the total header length is **48 bytes** for a basic single-segment file.

---

## 3. Pixel Data (CD) Section

### 3.1 The Need for a Continuous Stream

The color data is stored as RGB triplets (3 bytes per color). For instance:
- Red: `ff 00 00`
- Blue: `00 00 ff`

When the file is written to disk, it is a continuous stream of bytes that is viewed in 16-byte rows (using tools like `hexdump -C`). Because 16 is not a multiple of 3 (16 mod 3 = 1), if you simply generate a fixed 16-byte block and repeat it, every row will be identical. (Hexdump will compress such repetition using an asterisk, e.g., `*`.) More importantly, the ball’s firmware will misinterpret the data and produce unintended color cycles.

### 3.2 Correct Method: Build a Continuous Stream

To construct the pixel data block properly, follow these steps:

1. **Determine the Total Length:**  
   For our examples, the pixel block is **304 bytes**.

2. **Start with a Prefix:**  
   Begin the stream with a fixed prefix (typically 3 bytes of `00 00 00`).  
   - This “offset” forces the 16-byte row boundaries to fall in the middle of an RGB triplet, causing each subsequent row to be shifted relative to the previous one.

3. **Fill with the Color Pattern:**  
   Append the desired 3‑byte color pattern repeatedly. For example, for blue, use:
   ```python
   blue_pattern = b"\x00\x00\xff"
   ```
   - Compute the remaining length:  
     `remaining = 304 - len(prefix)`  
     (For a 3-byte prefix, remaining = 304 – 3 = 301 bytes.)
   - Determine how many full repeats fit:
     ```python
     repeat_count = remaining // 3  # For example, 301 // 3 = 100 full repeats.
     remainder = remaining % 3        # And 301 % 3 = 1 extra byte.
     ```
   - Build the body as:
     ```python
     body = blue_pattern * repeat_count + blue_pattern[:remainder]
     ```

4. **Final Adjustment:**  
   The very last byte of the continuous stream must be set to `0x42` to match the known–good files.

5. **Assemble the Pixel Block:**  
   ```python
   pixel_block = prefix + body
   pixel_block = bytearray(pixel_block)
   pixel_block[-1] = 0x42
   pixel_block = bytes(pixel_block)
   assert len(pixel_block) == 304
   ```

### 3.3 Consequences in the Hex Dump

- **Correct Construction:**  
  When you run `hexdump -C` on a correctly generated file, you will see that the 16‑byte rows in the pixel block are *not identical*. Instead, each row is a different 16‑byte slice (rotated by one byte relative to the previous row) because of the continuous stream.
  
- **Incorrect Construction:**  
  In the other LLM’s code, the pixel block was built by repeating an identical 16‑byte row. The hex dump showed many identical rows (compressed with an asterisk), and the ball then cycled through unintended colors. See the following example comparisons:

  **Incorrect Example Hex Dump (4px Blue):**
  ```
  00000030  00 00 00 00 00 ff 00 00  ff 00 00 ff 00 00 ff 00  |................|
  00000040  00 00 ff 00 00 ff 00 00  ff 00 00 ff 00 00 ff 00  |................|
  *
  00000150  00 00 ff 00 00 ff 00 00  ff 00 00 ff 00 00 ff 42  |...............B|
  00000160  54 00 00 00 00                                    |T....|
  00000165
  ```
  
  **Correct Example Hex Dump (4px Blue, our method):**
  ```
  00000030  00 00 00 00 00 ff 00 00  ff 00 00 ff 00 00 ff 00  |................|
  00000040  00 00 ff 00 00 ff 00 00  ff 00 00 ff 00 00 ff 00  |................|
  00000050  ff 00 00 ff 00 00 ff 00  00 ff 00 00 ff 00 00 ff  |................|
  ...
  00000150  00 00 ff 00 00 ff 00 00  ff 00 00 ff 00 00 ff 42  |...............B|
  00000160  54 00 00 00 00                                    |T....|
  00000165
  ```
  Notice that in the correct file, while some rows may look similar, they are not *identical*—each is a shifted slice of a 304-byte continuous stream.

---

## 4. Footer Section

- **Structure:**  
  The footer is fixed and always 5 bytes:
  ```
  BT 00 00 00 00
  ```
  This consists of:
  - `BT`: 0x42 0x54  
  - Followed by 4 null bytes (0x00 0x00 0x00 0x00)

---

## 5. Overall Assembly

For a typical sequence (for example, a 4px blue-for-10-seconds file):
- **Header:** 48 bytes (with pixel count fields set to 4, e.g., `00 04` at offset 0x08 and `04 00` at offset 0x20)
- **Pixel Data Block:** 304 bytes constructed using the continuous stream method described above.
- **Footer:** 5 bytes (`42 54 00 00 00`)
- **Total File Size:** 48 + 304 + 5 = 357 bytes (0x165)

---

## 6. Verification Using Hexdump

Use the following commands to inspect your file:

### Basic Hex Dump
```bash
hexdump -C sequences/4px_blue_10.prg
```
- **What to Check:**
  - **Header:** The first 48 bytes must match the expected magic, version, pixel count, and timing data.
  - **Pixel Block:** The 304-byte region should show 16-byte rows that are not all identical. If many rows are identical (and compressed with an asterisk `*`), the pixel block was built incorrectly.
  - **Footer:** The last 5 bytes must be `42 54 00 00 00`.

### Using grep, head, and tail
```bash
hexdump -C sequences/4px_blue_10.prg | grep -A 50 "CD"
hexdump -C sequences/4px_blue_10.prg | head -n 10
hexdump -C sequences/4px_blue_10.prg | tail -n 10
```
These commands help isolate sections so you can verify that each section is correct.

---

## 7. Summary of Key Points

1. **Header Construction:**
   - The header must include the correct magic numbers, version, configuration, and pixel count.
   - **Pixel Count:**  
     - For 1px: Set offset 0x08 to `00 01` and the corresponding field (offset ~0x20) to `01 00`.
     - For 4px: Set offset 0x08 to `00 04` and the corresponding field to `04 00`.

2. **Pixel Data Block – Continuous Stream Method:**
   - **Total Length:** Must be exactly 304 bytes (in our examples).
   - **Prefix:** Start with 3 bytes of `00` to force a misalignment.
   - **Fill with Color Pattern:**  
     - Use the 3-byte color triplet (e.g., blue is `00 00 ff`).
     - Calculate the number of full repeats and any remainder for the remaining 301 bytes.
   - **Final Byte Adjustment:** Set the very last byte to `0x42`.
   - **Result:**  
     The resulting 304-byte stream, when divided into 16-byte rows, produces rows that are shifted relative to each other (i.e., they are not identical). This is critical for correct display.

3. **Footer:**
   - Always append `BT 00 00 00 00` (5 bytes).

4. **Overall File Size:**
   - Must be exactly the sum of the header, pixel block, and footer (e.g., 357 bytes for our examples).

5. **Verification:**
   - Use `hexdump -C` and related tools to ensure the file is correctly built.
   - Check that the pixel data block does not compress to a large `*` (which indicates identical 16-byte rows).

6. **Common Pitfall to Avoid:**
   - **Do not simply repeat a fixed 16-byte block.**  
     Instead, generate the pixel block as a continuous stream with the proper offset and final byte adjustment.

---

## 8. Final Notes and Future Considerations

- **Timing (PI) Section:**  
  This guide focuses primarily on the header and pixel data block. Proper timing data is also crucial and may require further documentation.
  
- **Multiple Pixel Support:**  
  The method for setting the pixel count (via header fields) is consistent regardless of the number of pixels. Adjust the pixel count fields accordingly.

- **Effects:**  
  Some files use special effect commands instead of direct RGB values. Future updates to this document will cover these in detail.

- **Iterative Testing:**  
  Always verify your generated files with tools like `hexdump -C` to catch even single-byte discrepancies.

---

*End of Updated Sequence File Format Notes*

---

This document, along with the provided sample Python generation scripts (generate_1px_red_10.py), should allow any future LLM or engineer to generate and verify proper .prg sequence files for LTX Balls.

