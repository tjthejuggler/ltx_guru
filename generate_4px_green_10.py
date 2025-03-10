#!/usr/bin/env python3
"""
This script creates a file named "4px_green_10.prg" that produces
a 4-pixel sequence that stays green for 10 seconds.

The pixel data block is built as a continuous 304-byte stream:
  - It starts with a 3-byte prefix of 0x00.
  - The remainder is filled with the 3-byte green pattern ("00 ff 00")
    repeated enough times (301 bytes total = 100 full cycles plus 1 extra byte).
  - The very last byte is then replaced with 0x42.
"""

def create_4px_green_10():
    # --- Header (48 bytes) ---
    header_hex = (
        "50 52 03 49 4e 05 00 00 "  # Offsets 0x00–0x07: Magic "PR.IN" and version info
        "00 04 00 08 01 00 50 49 "  # Offsets 0x08–0x0F: Pixel count = 4, etc.
        "15 00 00 00 01 00 01 00 "  # Offsets 0x10–0x17: Segment count = 1, etc.
        "64 00 33 00 00 00 00 00 "  # Offsets 0x18–0x1F: Timing/duration fields (0x64 = 100)
        "04 00 01 00 00 64 00 00 "  # Offsets 0x20–0x27: More header data (pixel count, duration, etc.)
        "00 43 44 30 01 00 00 64"   # Offsets 0x28–0x2F: Literal "CD0", then 0x64, etc.
    )
    header = bytes.fromhex(header_hex)
    assert len(header) == 48

    # --- Pixel Data Block (304 bytes) ---
    N = 304
    # Start with a prefix of 3 bytes (to force the proper offset).
    prefix = b"\x00\x00\x00"
    # Then fill the remaining bytes with repeated "00 ff 00" (green).
    remaining = N - len(prefix)  # 304 - 3 = 301 bytes
    green_pattern = b"\x00\xff\x00"  # 3 bytes for green
    repeat_count = remaining // len(green_pattern)  # 301 // 3 = 100
    remainder = remaining % len(green_pattern)      # 301 % 3 = 1
    body = green_pattern * repeat_count + green_pattern[:remainder]
    # Build the continuous 304-byte pixel block.
    pixel_block = prefix + body
    assert len(pixel_block) == 304
    # Force the very last byte to be 0x42.
    pixel_block = bytearray(pixel_block)
    pixel_block[-1] = 0x42
    pixel_block = bytes(pixel_block)

    # --- Footer (5 bytes) ---
    footer = bytes.fromhex("54 00 00 00 00")  # "T" (0x54) followed by four 0x00 bytes

    # --- Assemble the full file ---
    # Total file size = header (48) + pixel block (304) + footer (5) = 357 bytes.
    file_data = header + pixel_block + footer
    assert len(file_data) == 357, f"File size is {len(file_data)}, expected 357"

    with open("4px_green_10.prg", "wb") as f:
        f.write(file_data)
    print("Created 4px_green_10.prg with", len(file_data), "bytes")

if __name__ == "__main__":
    create_4px_green_10()
