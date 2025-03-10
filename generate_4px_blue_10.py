#!/usr/bin/env python3
"""
This script creates a file named "4px_blue_10.prg" that produces
a 4-pixel sequence that stays blue for 10 seconds.

The pixel data block is built as a continuous stream:
  - It starts with a 3-byte prefix of 0x00
  - The remainder is filled with the 3-byte blue pattern ("00 00 ff")
  - The very last byte is then replaced with 0x42
"""

def create_4px_blue_10():
    # --- Header (48 bytes) ---
    header_hex = (
        "50 52 03 49 4e 05 00 00 "  # Magic "PR.IN" and version info
        "00 04 00 08 01 00 50 49 "  # Pixel count = 4 (changed from 01 to 04)
        "15 00 00 00 01 00 01 00 "  # Segment count = 1
        "64 00 33 00 00 00 00 00 "  # Timing/duration fields (0x64 = 100)
        "01 00 01 00 00 64 00 00 "  # More header data
        "00 43 44 30 01 00 00 64"   # Literal "CD0", then 0x64
    )
    header = bytes.fromhex(header_hex)
    assert len(header) == 48

    # --- Pixel Data Block (304 bytes) ---
    N = 304
    # Start with a prefix of 3 bytes (to force the proper offset)
    prefix = b"\x00\x00\x00"
    # Then fill the remaining bytes with repeated "00 00 ff" (blue)
    remaining = N - len(prefix)  # 304 - 3 = 301 bytes
    blue_pattern = b"\x00\x00\xff"  # 3 bytes for blue
    repeat_count = remaining // len(blue_pattern)  # 301 // 3 = 100
    remainder = remaining % len(blue_pattern)      # 301 % 3 = 1
    body = blue_pattern * repeat_count + blue_pattern[:remainder]
    # Build the continuous 304-byte pixel block
    pixel_block = prefix + body
    assert len(pixel_block) == 304
    # Force the very last byte to be 0x42
    pixel_block = bytearray(pixel_block)
    pixel_block[-1] = 0x42
    pixel_block = bytes(pixel_block)

    # --- Footer (5 bytes) ---
    footer = bytes.fromhex("54 00 00 00 00")  # "T" (0x54) followed by four 0x00 bytes

    # --- Assemble the full file ---
    # Total file size = header (48) + pixel block (304) + footer (5) = 357 bytes
    file_data = header + pixel_block + footer
    assert len(file_data) == 357, f"File size is {len(file_data)}, expected 357"

    with open("4px_blue_10.prg", "wb") as f:
        f.write(file_data)
    print("Created 4px_blue_10.prg with", len(file_data), "bytes")

if __name__ == "__main__":
    create_4px_blue_10()
