#!/usr/bin/env python3
"""
Generate a 4px sequence file that displays 10 seconds of blue.

File Structure:
- Header: 48 bytes with pixel count set to 4 and timing fields set so that
          0x64 (100 in hex) represents 10 seconds (using a base of 0.1s).
- Pixel Block: 304 bytes of continuous color data.
    • Constructed as a continuous stream for blue (RGB = 00 00 ff) that starts
      with a 3-byte prefix (0x00 0x00 0x00) to force an offset.
    • The remaining 301 bytes are filled by repeating the 3-byte blue pattern,
      yielding 100 full cycles plus 1 extra byte.
    • The final byte of the block is forced to 0x42.
- Footer: 5 bytes "54 00 00 00 00" (the letter T followed by four null bytes).
- Total file size: 48 + 304 + 5 = 357 bytes.
"""

def create_4px_blue_10():
    # --- Header (48 bytes) ---
    # Note: The header for a 4px file is similar to that for a 1px file,
    # except the pixel count fields are changed from 1 to 4.
    header_hex = (
        "50 52 03 49 4e 05 00 00 "  # Offsets 0x00–0x07: "PR", version, "IN", etc.
        "00 04 00 08 01 00 50 49 "  # Offsets 0x08–0x0F: Pixel count = 4 (0x0004)
        "15 00 00 00 01 00 01 00 "  # Offsets 0x10–0x17: Segment info (unchanged)
        "64 00 33 00 00 00 00 00 "  # Offsets 0x18–0x1F: Timing fields; 0x64 is the base unit (0x64 = 100 decimal → 10 sec if base = 0.1s)
        "04 00 01 00 00 64 00 00 "  # Offsets 0x20–0x27: Pixel count field updated to 4 (0x04 00) plus more timing info
        "00 43 44 30 01 00 00 64"   # Offsets 0x28–0x2F: Literal "CD0", then 0x64, etc.
    )
    header = bytes.fromhex(header_hex)
    assert len(header) == 48, f"Header length is {len(header)} bytes, expected 48"

    # --- Pixel Data Block (304 bytes) ---
    # For 4px, the pixel block is built as a continuous 304-byte stream.
    # We want to fill it with blue (00 00 ff). However, because colors are stored
    # as 3-byte groups and 16 is not a multiple of 3, the 16-byte rows will be offset.
    N = 304
    prefix = b"\x00\x00\x00"  # 3-byte prefix to force the offset
    remaining = N - len(prefix)  # 304 - 3 = 301 bytes remain
    blue_pattern = b"\x00\x00\xff"  # 3-byte pattern for blue
    repeat_count = remaining // len(blue_pattern)  # 301 // 3 = 100 full cycles
    remainder = remaining % len(blue_pattern)        # 301 % 3 = 1 byte extra
    body = blue_pattern * repeat_count + blue_pattern[:remainder]
    pixel_block = prefix + body
    assert len(pixel_block) == 304, f"Pixel block length is {len(pixel_block)} bytes, expected 304"
    # Force the very last byte to be 0x42
    pixel_block = bytearray(pixel_block)
    pixel_block[-1] = 0x42
    pixel_block = bytes(pixel_block)

    # --- Footer (5 bytes) ---
    footer = bytes.fromhex("54 00 00 00 00")  # 0x54 = 'T' followed by four null bytes

    # --- Assemble the file ---
    file_data = header + pixel_block + footer
    total_size = len(file_data)
    assert total_size == 357, f"Total file size is {total_size} bytes, expected 357"

    with open("gen_4px_blue_10.prg", "wb") as f:
        f.write(file_data)
    print("Created gen_4px_blue_10.prg with", total_size, "bytes")

if __name__ == "__main__":
    create_4px_blue_10()
