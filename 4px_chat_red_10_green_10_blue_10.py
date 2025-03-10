#!/usr/bin/env python3
"""
This script builds a .prg file for an LTX juggling ball with 4 pixels and
three color segments (red, green, blue), each lasting 10 seconds.

Our reverse‐engineered format (based on our 100‑second examples) is as follows:

  1. Fixed header (16 bytes):
       50 52 03 49 4e 05 00 00 00 04 00 08 01 00 50 49

  2. Variable header (16 bytes) for 3 segments:
       •  4‑byte segment table length field: 2 + 19×3 = 59 → 3B 00 00 00
       •  2‑byte segment count: 03 00
       •  2‑byte flag: 01 00
       •  2‑byte “duration” field (normally 64 00 for 100 sec, here 0a 00 for 10 sec)
       •  2‑byte pixel‐data offset (taken from our 100‑second example): 59 00
       •  4 bytes reserved: 00 00 00 00

  3. Segment table (59 bytes total):
       •  2 bytes: global pixel count (04 00)
       •  Then one 19‑byte record per segment.
         (We take the 100‑second records and replace every “64 00” with “0a 00”.)
         For seg2, note that the original record is:
         
             00 04 00 01 00 00 64 00 00 00 01 00 64 00 B1 02 00 00 00
         
         We must replace both occurrences of “64 00” (at bytes 6–7 and 12–13). In our
         earlier code we mistakenly did:
         
             seg2 = seg2_orig[:6] + (10).to_bytes(2, 'little') + seg2_orig[8:12] +
                    (10).to_bytes(2, 'little') + seg2_orig[12:]
         
         but seg2_orig[12:] re‑inserts the unmodified “64 00”. The fix is to use seg2_orig[14:].
         
  4. Pixel data table:
       We generate 10 frames per segment (each frame is 16 bytes, representing 4 pixels of 4 bytes each).
       In each frame the “active” LED (which rotates among the four) is lit with the segment’s color.
       Segment 1 uses red, segment 2 green, segment 3 blue.

  5. Footer (6 bytes): ASCII “BT” followed by four nulls.
  
Because the format is undocumented, these values are our best–guess.
"""

def create_prg():
    # 1. Fixed header (16 bytes)
    fixed_header = bytes.fromhex("50 52 03 49 4e 05 00 00 00 04 00 08 01 00 50 49")
    
    # 2. Variable header (16 bytes) for 3 segments:
    #  - segment table length field: 2 + (19×3) = 59 → 3B 00 00 00
    seg_table_len_field = (2 + 19*3).to_bytes(4, byteorder='little')
    seg_count   = (3).to_bytes(2, byteorder='little')       # 03 00
    flag        = (1).to_bytes(2, byteorder='little')       # 01 00
    duration    = (10).to_bytes(2, byteorder='little')      # 0A 00 (for 10 seconds)
    pix_offset  = (0x59).to_bytes(2, byteorder='little')      # 59 00 (taken from the 100-sec example)
    reserved    = bytes(4)                                  # 00 00 00 00
    variable_header = seg_table_len_field + seg_count + flag + duration + pix_offset + reserved
    # variable_header will be: 3B 00 00 00  03 00  01 00  0A 00  59 00  00 00 00 00

    header = fixed_header + variable_header

    # 3. Segment table (59 bytes total)
    # First 2 bytes: global pixel count (always 04 00)
    seg_table = (4).to_bytes(2, byteorder='little')  # 04 00

    # Each segment record is 19 bytes. We start from our 100‑second records and replace each "64 00" with "0A 00".
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
    # FIX: Replace the second "64 00" by taking seg2_orig[14:] (not seg2_orig[12:])
    seg2 = seg2_orig[:6] + (10).to_bytes(2, byteorder='little') + seg2_orig[8:12] \
           + (10).to_bytes(2, byteorder='little') + seg2_orig[14:]
    # Record 3 (blue)
    seg3_orig = bytes.fromhex(
        "00 04 00 01 00 00 64 00 00 00 43 44 88 03 00 00 2C 01 00"
    )
    seg3 = seg3_orig[:6] + (10).to_bytes(2, byteorder='little') + seg3_orig[8:]
    
    # Ensure each record is exactly 19 bytes (pad with zeros if necessary)
    seg1 = seg1.ljust(19, b'\x00')
    seg2 = seg2.ljust(19, b'\x00')
    seg3 = seg3.ljust(19, b'\x00')
    
    seg_table += seg1 + seg2 + seg3
    # Total segment table length = 2 + (3×19) = 59 bytes (which matches the variable header)

    # 4. Pixel data table: 10 frames per segment; each frame is 16 bytes.
    # Total frames = 3 segments × 10 frames = 30 frames.
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
            # Cycle the “active” pixel among the four (e.g. 3, 2, 1, 0)
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
    outfile = "4px_chat_red_10_green_10_blue_10.prg"
    with open(outfile, "wb") as f:
        f.write(data)
    print(f"Wrote {len(data)} bytes to {outfile}")

if __name__ == '__main__':
    main()
