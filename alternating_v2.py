#!/usr/bin/env python3
"""
This script writes a .prg file for a 4-pixel LTX juggling ball.
Based on our reverse–engineering of three hexdumps, our new guess is that:
  • A header (16 bytes) defines a loop count and pixel count.
  • Two 16–byte command blocks define two phases.
     In our file, phase 1 will be green and phase 2 red.
     We set each phase to last 40 ticks.
  • A 4–byte marker (b'CD0\x01') is written.
  • A color table then follows: for each phase (there will be 20 phases total,
    since the header loop count is half the total number of phases),
    we write (for each tick in the phase) one 32–bit color per pixel.
    (We assume that 32–bit colors are stored in the order: Blue, Green, Red, 0.)
    In the red–only files the table’s entries are all “00 00 ff 00” (i.e. red).
    Here we alternate:
      – Green = b'\x00\xff\x00\x00'
      – Red   = b'\x00\x00\xff\x00'
  • Finally, a 6–byte footer (b'BT' followed by four zero bytes) terminates the file.
  
This file is designed so that the built-in loop repeats a two–phase cycle (green then red)
a total of (loop_count×2) times. For 10 cycles (20 phases) we set loop_count = 10.
Each phase lasts 40 ticks (which in our examples is roughly one second).
"""

import struct

# --- PARAMETERS ---
num_pixels = 4

# We want 10 full cycles (i.e. 10 green/red pairs) = 20 phases total.
total_phases = 20
# Each phase lasts 40 ticks (40 ticks ≈ 1 second as suggested by the green phase in one example)
ticks_per_phase = 40
total_ticks = total_phases * ticks_per_phase  # (not used directly but for our color table size)

# Header loop count is (total phases) ÷ 2.
loop_count = total_phases // 2  # 20 phases → 10

# --- BUILD THE HEADER ---
# Format: b'PR' + version (0x03) + b'IN' +
#         4-byte loop count (little-endian) +
#         2-byte pixel count (big-endian) +
#         2-byte constant (00 08) +
#         2-byte flag (01 00) +
#         b'PI'
header = (
    b'PR' +
    b'\x03' +
    b'IN' +
    struct.pack('<I', loop_count) +      # e.g. 10 → 0A 00 00 00
    struct.pack('>H', num_pixels) +        # for 4 pixels: 00 04
    b'\x00\x08' +
    b'\x01\x00' +
    b'PI'
)
# (Header is 16 bytes.)

# --- COMMAND BLOCKS ---
# We'll use a two–block scheme (one for each phase of the cycle).

# Command Block 1: Green phase.
# Structure (16 bytes):
#   • 4 bytes: duration (40 ticks → 28 00 00 00, little–endian)
#   • 2 bytes: color index (02 for green → 02 00)
#   • 2 bytes: reserved (00 00)
#   • 2 bytes: brightness (100 → 64 00)
#   • 2 bytes: parameter (70 → 46 00)
#   • 4 bytes: reserved (00 00 01 00)
cmd1 = (
    struct.pack('<I', ticks_per_phase) +  # 28 00 00 00 for 40 ticks
    struct.pack('<H', 2) +                # color index 2 = green
    b'\x00\x00' +                         # reserved
    struct.pack('<H', 100) +              # brightness = 100
    struct.pack('<H', 70) +               # parameter = 70
    b'\x00\x00\x01\x00'                   # reserved
)

# Command Block 2: Red phase.
# We mimic the structure but choose red (color index 1) and use a parameter of 51 (0x33).
# (In the red–only examples the first block had a duration field;
# here we include a duration so that each phase lasts 40 ticks.)
cmd2 = (
    struct.pack('<I', ticks_per_phase) +  # 28 00 00 00 for 40 ticks
    struct.pack('<H', 1) +                # color index 1 = red
    b'\x00\x00' +                         # reserved
    struct.pack('<H', 100) +              # brightness = 100
    struct.pack('<H', 51) +               # parameter = 51 (0x33)
    b'\x00\x00\x00\x00'                   # reserved
)

# --- COLOR DATA MARKER ---
# In the red–only examples the marker appears as 43 44 30 01, i.e. b'CD0\x01'
color_marker = b'CD0\x01'

# --- COLOR TABLE ---
# We now build a table with one 32-bit word per tick per pixel.
# Our design: for each of the 20 phases, for each of 40 ticks in that phase,
# and for each pixel (4 pixels) we output a 4–byte color.
# We assume that the 32-bit color is stored with the order: Blue, Green, Red, 0.
# In the red–only examples the table uses 00 00 ff 00 to indicate red.
# Therefore, for red we use: b'\x00\x00\xff\x00'
# and for green we use: b'\x00\xff\x00\x00'
red_color   = b'\x00\x00\xff\x00'
green_color = b'\x00\xff\x00\x00'

color_table = bytearray()
for phase in range(total_phases):
    # Alternate: even phases = green, odd phases = red.
    if phase % 2 == 0:
        color = green_color
    else:
        color = red_color
    for tick in range(ticks_per_phase):
        for pix in range(num_pixels):
            color_table.extend(color)
# Expected size: total_phases * ticks_per_phase * num_pixels * 4 bytes
expected_table_size = total_phases * ticks_per_phase * num_pixels * 4
assert len(color_table) == expected_table_size, f"Color table is {len(color_table)} bytes; expected {expected_table_size}"

# --- FOOTER ---
# Footer: marker b'BT' (42 54) followed by 4 zero bytes.
footer = b'BT' + b'\x00\x00\x00\x00'

# --- ASSEMBLE THE FILE ---
prg_data = header + cmd1 + cmd2 + color_marker + color_table + footer

# Write out the file.
output_file = "alternating_v2.prg"
with open(output_file, "wb") as f:
    f.write(prg_data)

print(f"Created {output_file} ({len(prg_data)} bytes).")
