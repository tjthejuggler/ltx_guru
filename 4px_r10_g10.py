#!/usr/bin/env python3
"""
This script builds a .prg file for an LTX juggling ball that uses four pixels.
It creates a two‐segment file: segment 1 shows “red” for 10 seconds and segment 2 shows “green” for 10 seconds.
The file structure (as deduced from several hex–dump examples) is as follows:

  [Fixed header] (16 bytes):
    50 52 03 49 4E 05 00 00 00 04 00 08 01 00 50 49

  [Variable header] (16 bytes):
    •  4–byte field = (2 + 19×segment_count). For 2 segments: 0x28 00 00 00.
    •  2–byte segment count: 0x02 00.
    •  2–byte constant: 0x01 00.
    •  2–byte segment duration (seconds). For 10 sec: 0x0A 00.
    •  2–byte pixel–data offset, which (in our examples) comes out as 0x46 00.
    •  4 zero bytes.

  [Segment table] (in our two–segment case, 38 bytes total):
    •  2 bytes: pixel count (always 0x04 00).
    •  Then 2 records (each about 18 bytes). Here we mimic the values from the red/green example,
       except that we change the “duration” bytes from 0x64 (100) to 0x0A (10).
       
  [Pixel–data table]:
    A sequence of 16–byte blocks (one per “frame”; each block holds 4 pixels×4 bytes).
    (In our file we generate 10 frames per segment – for a total of 20 frames – and for a “solid color”
     we light only one LED per frame (cycling through the four).)

  [Footer] (6 bytes): ASCII “BT” plus four zero bytes.

Because the true format is undocumented the following values are our “best guess”.
"""

import sys

def create_prg():
    # -------------------------
    # 1. Fixed header (16 bytes)
    header_fixed = bytes.fromhex("50 52 03 49 4E 05 00 00 00 04 00 08 01 00 50 49")
    
    # -------------------------
    # 2. Variable header (16 bytes)
    # For 2 segments, our field = 2 + 19*2 = 40 (0x28 00 00 00)
    seg_table_len_field = (40).to_bytes(4, byteorder='little')
    seg_count = (2).to_bytes(2, byteorder='little')
    constant = (1).to_bytes(2, byteorder='little')
    # Segment duration (seconds): use 10 seconds (0x0A 00)
    seg_duration = (10).to_bytes(2, byteorder='little')
    # Pixel–data offset: fixed header (16) + variable header (16) + seg table (40-2 bytes) = 32 + 38 = 70 (0x46 00)
    pixel_data_offset = (70).to_bytes(2, byteorder='little')
    reserved = bytes(4)
    header_variable = seg_table_len_field + seg_count + constant + seg_duration + pixel_data_offset + reserved

    header = header_fixed + header_variable

    # -------------------------
    # 3. Segment table (38 bytes total)
    # First 2 bytes: pixel count = 4 (0x04 00)
    seg_table = (4).to_bytes(2, byteorder='little')
    
    # Each segment record we assume is 18 bytes.
    # For segment 1 (red): based on the red-green example record, but change duration (byte positions 3–4 and 9–10) from 0x64 to 0x0A.
    seg1 = bytes([
        0x01, 0x00,        # (example field)
        0x00, 0x0A,        # duration = 10 sec (was 0x00 0x64)
        0x00, 0x00,        # (reserved)
        0x00, 0x01,        # (example field)
        0x00, 0x0A,        # duration = 10 sec (was 0x00 0x64)
        0x00, 0x72, 0x01, 0x00,  # (some pointer or value – unchanged)
        0x00, 0x00, 0x00, 0x04   # (example ending)
    ])
    # For segment 2 (green): based on the second record from the red-green example, with duration changed.
    seg2 = bytes([
        0x00, 0x00,
        0x00, 0x04,
        0x00, 0x01,
        0x00, 0x00,
        0x0A, 0x00,        # duration = 10 sec (was 0x64)
        0x00, 0x00,
        0x43, 0x44, 0x5C, 0x02,
        0x00, 0x00         # pad to 18 bytes
    ])
    # Make sure each record is exactly 18 bytes:
    if len(seg1) != 18:
        seg1 = seg1.ljust(18, b'\x00')
    if len(seg2) != 18:
        seg2 = seg2.ljust(18, b'\x00')
    
    seg_table += seg1 + seg2
    assert len(seg_table) == 38, f"Segment table length is {len(seg_table)}; expected 38"
    
    # -------------------------
    # 4. Pixel data table
    # We generate a “frame‐animation” for each segment.
    # Each frame is 16 bytes (4 pixels × 4 bytes each).
    # For our purposes, we generate 10 frames per segment.
    frames_per_segment = 10
    total_frames = frames_per_segment * 2
    frames = []
    for seg in range(2):
        # Choose a “solid” color:
        # For segment 0, we want red; for segment 1, green.
        if seg == 0:
            color = bytes([0xFF, 0x00, 0x00, 0xFF])  # red (e.g. R, G, B, brightness)
        else:
            color = bytes([0x00, 0xFF, 0x00, 0xFF])  # green

        # In the examples the lit LED rotates among the four pixels.
        # We will make each frame light one LED (the “active” LED) and leave the others off.
        for i in range(frames_per_segment):
            frame = bytearray(16)  # 4 pixels × 4 bytes
            # Cycle through pixel indices (for example, descending from 3 to 0)
            active_pixel = (3 - (i % 4))
            for p in range(4):
                if p == active_pixel:
                    frame[p*4:(p+1)*4] = color
                else:
                    frame[p*4:(p+1)*4] = b'\x00\x00\x00\x00'
            frames.append(frame)
    pixel_data = b''.join(frames)

    # -------------------------
    # 5. Footer (6 bytes): ASCII "BT" + 4 nulls.
    footer = b'BT' + bytes(4)

    # Assemble full file:
    prg_data = header + seg_table + pixel_data + footer
    return prg_data

def main():
    data = create_prg()
    outfile = "4px_red10_green10.prg"
    with open(outfile, "wb") as f:
        f.write(data)
    print(f"Wrote {len(data)} bytes to {outfile}")

if __name__ == '__main__':
    main()
