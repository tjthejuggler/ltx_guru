#!/usr/bin/env python3
"""
This script builds a .prg file for an LTX juggling ball with 4 pixels and
three color segments (red, green, blue), each lasting 10 seconds.

Our reverse–engineered file format is as follows:

  1. Fixed header (16 bytes):
       50 52 03 49 4E 05 00 00 00 04 00 08 01 00 50 49

  2. Variable header (16 bytes):
     •  A 4–byte field whose value is computed as:
           2 + (19 × <number of segments>)
        For 3 segments: 2 + (19×3) = 59 → 3B 00 00 00.
     •  A 2–byte segment–count: 03 00.
     •  A 2–byte flag (or mode): for 3–segment files this is 01 00.
     •  A 2–byte “duration” field. In the 100‑second file this was 64 00,
        but here we set it to 0A 00 for 10 seconds.
     •  A 2–byte “pixel–data offset”. In the 100‑second file this was 59 00.
        (It must be recalculated if the segment–table size changes; here we use 59 00.)
     •  4 bytes reserved (all zeros): 00 00 00 00.
        
     Thus the variable header is:
         3B 00 00 00  03 00  01 00  0A 00  59 00  00 00 00 00

  3. Segment table:
     •  First 2 bytes: global pixel count (always 04 00).
     •  Then one “segment record” per segment.
       (Our examples show that each record is 19 bytes long.)
     In the official 100‑second 3–segment file the records contained two occurrences
     of “64 00” (the 100‑sec duration). Here we mimic that layout but replace those
     with “0A 00”. (The values in the rest of the record are taken from our 100–second
     example.)
     
     We define three records as follows:
     
       – Record 1 (red):
         Original (100 sec) hex (as extracted from the dump):
             01 00 00 64 00 00 00 01 00 64 00 85 01 00 00 00 00 00 00
         We replace the two "64 00" with "0A 00":
             01 00 00 0A 00 00 00 01 00 0A 00 85 01 00 00 00 00 00 00

       – Record 2 (green):
         Original (100 sec):
             00 04 00 01 00 00 64 00 00 00 01 00 64 00 B1 02 00 00 00
         Replacing "64 00" gives:
             00 04 00 01 00 00 0A 00 00 00 01 00 0A 00 B1 02 00 00 00

       – Record 3 (blue):
         Original (100 sec):
             00 04 00 01 00 00 64 00 00 00 43 44 88 03 00 00 2C 01 00
         After replacing "64 00":
             00 04 00 01 00 00 0A 00 00 00 43 44 88 03 00 00 2C 01 00
     
     (These records are concatenated after the initial 2–byte pixel count so that the total
      segment–table length is 2 + (3×19) = 59 bytes.)

  4. Pixel data table:
     We generate an “animation” of 4–pixel frames (each frame is 16 bytes, holding 4 pixels × 4 bytes).
     For our file we create 10 frames per segment (total 30 frames). In each frame only one pixel
     is “active” (its color is set) and the active pixel rotates among the 4 positions.
     In segment 1 the active pixel shows red, in segment 2 green, and in segment 3 blue.

  5. Footer (6 bytes):
       The ASCII characters “BT” (42 54) followed by four null bytes.

Because the format is not documented, these values are our best–guess.
"""

def create_prg():
    # 1. Fixed header (16 bytes)
    fixed_header = bytes.fromhex("50 52 03 49 4E 05 00 00 00 04 00 08 01 00 50 49")
    
    # 2. Variable header (16 bytes) for 3 segments
    seg_table_len_field = (2 + 19*3).to_bytes(4, byteorder='little')  # 2 + 57 = 59 → 3B 00 00 00
    seg_count = (3).to_bytes(2, byteorder='little')                    # 03 00
    flag = (1).to_bytes(2, byteorder='little')                           # 01 00
    duration = (10).to_bytes(2, byteorder='little')                      # 0A 00 (10 seconds)
    pix_offset = (0x59).to_bytes(2, byteorder='little')                  # 59 00 (from our 100-sec example)
    reserved = bytes(4)                                                  # 00 00 00 00
    variable_header = seg_table_len_field + seg_count + flag + duration + pix_offset + reserved
    # variable_header = 3B 00 00 00  03 00  01 00  0A 00  59 00  00 00 00 00

    header = fixed_header + variable_header

    # 3. Segment table (59 bytes total)
    # First 2 bytes: global pixel count (always 04 00)
    seg_table = (4).to_bytes(2, byteorder='little')  # 04 00

    # Define three segment records (each 19 bytes) by taking the 100-sec record and replacing 64 00 with 0A 00.
    # Record 1 (red)
    seg1_orig = bytes.fromhex(
        "01 00 00 64 00 00 00 01 00 64 00 85 01 00 00 00 00 00 00"
    )
    seg1 = seg1_orig[:2] + (10).to_bytes(2, byteorder='little') + seg1_orig[4:8] \
           + (10).to_bytes(2, byteorder='little') + seg1_orig[10:]
    
    # Record 2 (green)
    seg2_orig = bytes.fromhex(
        "00 04 00 01 00 00 64 00 00 00 01 00 64 00 B1 02 00 00 00"
    )
    seg2 = seg2_orig[:6] + (10).to_bytes(2, byteorder='little') + seg2_orig[8:12] \
           + (10).to_bytes(2, byteorder='little') + seg2_orig[12:]
    
    # Record 3 (blue)
    seg3_orig = bytes.fromhex(
        "00 04 00 01 00 00 64 00 00 00 43 44 88 03 00 00 2C 01 00"
    )
    seg3 = seg3_orig[:6] + (10).to_bytes(2, byteorder='little') + seg3_orig[8:]
    
    # Ensure each segment record is exactly 19 bytes:
    seg1 = seg1.ljust(19, b'\x00')
    seg2 = seg2.ljust(19, b'\x00')
    seg3 = seg3.ljust(19, b'\x00')
    
    seg_table += seg1 + seg2 + seg3
    # Now seg_table is 2 + 3*19 = 59 bytes, matching the computed value in the variable header.

    # 4. Pixel data table: 10 frames per segment; each frame is 16 bytes.
    # Total frames: 3 segments × 10 frames = 30 frames.
    frames_per_segment = 10
    frames = []
    for seg in range(3):
        if seg == 0:
            color = bytes([0xFF, 0x00, 0x00, 0xFF])  # red
        elif seg == 1:
            color = bytes([0x00, 0xFF, 0x00, 0xFF])  # green
        else:
            color = bytes([0x00, 0x00, 0xFF, 0xFF])  # blue
        for i in range(frames_per_segment):
            frame = bytearray(16)  # 4 pixels × 4 bytes each
            # Rotate the “active” LED (so the lit pixel moves)
            active_pixel = (3 - (i % 4))
            for p in range(4):
                if p == active_pixel:
                    frame[p*4:(p+1)*4] = color
                else:
                    frame[p*4:(p+1)*4] = b'\x00\x00\x00\x00'
            frames.append(frame)
    pixel_data = b''.join(frames)
    
    # 5. Footer (6 bytes): "BT" followed by four nulls.
    footer = b'BT' + bytes(4)
    
    # Assemble full file:
    prg_data = header + seg_table + pixel_data + footer
    return prg_data

def main():
    data = create_prg()
    outfile = "4px_red_10_green_10_blue_10.prg"
    with open(outfile, "wb") as f:
        f.write(data)
    print(f"Wrote {len(data)} bytes to {outfile}")

if __name__ == '__main__':
    main()
