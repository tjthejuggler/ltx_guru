#!/usr/bin/env python3
"""
This script creates a .prg file for an LED juggling ball.
Our reverse–engineering of the three provided hexdumps suggests that
a PRG file has roughly the following structure:

  [HEADER] (16 bytes)
    •  2 bytes: ASCII "PR"
    •  1 byte: version (0x03)
    •  2 bytes: ASCII "IN"
    •  4 bytes: loop–count (in the examples 05 00 00 00;
         we assume that this value equals half the total number of “phases”)
    •  2 bytes: pixel count (e.g. 00 04 for 4 pixels)
    •  2 bytes: a constant (00 08)
    •  2 bytes: a flag (01 00)
    •  2 bytes: ASCII "PI"

  [COMMAND BLOCKS] (2 blocks × 16 bytes)
    Block 1 (phase 1 – our “green” phase):
      •  4 bytes: phase duration (in ticks). In the 1g_9r file 0x28 = 40 ticks.
      •  2 bytes: color index (02 for green)
      •  2 bytes: reserved (00 00)
      •  2 bytes: brightness (0x64 = 100)
      •  2 bytes: a “parameter” (0x46 = 70 for green)
      •  4 bytes: reserved (00 00 01 00)
    Block 2 (phase 2 – our “red” phase):
      •  2 bytes: pixel count (04 00 for 4 pixels)
      •  2 bytes: color index (01 for red)
      •  2 bytes: reserved (00 01)
      •  2 bytes: reserved (00 00)
      •  2 bytes: reserved (00 01)
      •  2 bytes: brightness (we use 100; note that in the red–only examples
           this appears as “00 64”)
      •  2 bytes: a “parameter” (we use 0x72 = 114 for red)
      •  2 bytes: reserved (01 00)

  [COLOR DATA BLOCK]
    •  A marker (we’ll use b'CD0\x01')
    •  Then a long table of “ticks” (frames), one 32–bit word per LED per tick.
      In our design each phase lasts 40 ticks and there are 20 phases (10 cycles),
      and each tick gives a 4–byte color value for each of 4 pixels.
      We assume that the device expects 32–bit colors in little–endian order:
         full green = 0x00ff0000  →  b'\x00\x00\xff\x00'
         full red   = 0xff000000  →  b'\x00\x00\x00\xff'
      (That is, when printed as a hexdump the red value appears as "00 00 00 ff".)

  [FOOTER]
    •  A marker: b'BT'
    •  4 zero bytes

This file will be set up so that the device’s built–in looping will run the two
phases (green then red) a total of (loop_count×2) times. In our examples the header
had a 4–byte loop field of 05 00 00 00 (i.e. 5) which in a two–phase file gives 10 phases.
For our 10–cycle (20–phase) sequence we set that field to 0x0A (10).

Below is the Python code that writes out such a file.
"""

import struct

# === PARAMETERS ====================================================
# We target a 4-pixel device.
num_pixels = 4

# We want the LEDs to change color every 1 second.
# (Our examples suggest that a phase duration of 40 ticks is roughly 1 second.)
ticks_per_phase = 40

# We want 10 full cycles (i.e. 10 green phases followed by 10 red phases, so 20 phases total)
num_phases = 20  # device will play (loop_count * 2) phases; hence we need loop_count = num_phases/2
loop_count = num_phases // 2

# Total ticks = num_phases * ticks_per_phase
total_ticks = num_phases * ticks_per_phase

# For each tick we must supply a 32-bit color for each pixel.
# (4 bytes per pixel × num_pixels per tick)
bytes_per_tick = num_pixels * 4

# We'll use 32-bit colors (little-endian):
# full green = 0x00ff0000 (will appear in the dump as 00 00 ff 00)
# full red   = 0xff000000 (will appear in the dump as 00 00 00 ff)
color_green = struct.pack('<I', 0x00ff0000)
color_red   = struct.pack('<I', 0xff000000)

# === BUILD THE FILE =================================================
# Construct the header (16 bytes):
#   b'PR' + version (0x03) + b'IN' + loop_count (4 bytes, little-endian)
#   + pixel count (2 bytes; we mimic the examples: e.g. b'\x00\x04')
#   + constant (b'\x00\x08') + flag (b'\x01\x00') + b'PI'
header = (
    b'PR' +
    b'\x03' +
    b'IN' +
    struct.pack('<I', loop_count) +  # 4-byte loop count (we use 0x0A for 10 cycles)
    struct.pack('>H', num_pixels) +    # 2-byte pixel count (big-endian as in the examples)
    b'\x00\x08' +
    b'\x01\x00' +
    b'PI'
)
# (This should produce, for our case, the hex sequence:
#  50 52 03 49 4e 0a 00 00 00 04 00 08 01 00 50 49)

# Command Block 1: For the first phase (green)
# 16 bytes: [4 bytes duration, 2 bytes color index, 2 bytes reserved,
#           2 bytes brightness, 2 bytes parameter, 4 bytes reserved]
# In the example for green (in file 3) the duration was 0x28 (40 ticks),
# color index = 0x0002, brightness = 0x0064 (100), parameter = 0x0046 (70),
# and the reserved 4 bytes were b'\x00\x00\x01\x00'.
cmd_block1 = (
    struct.pack('<I', ticks_per_phase) +  # duration = 40 ticks
    struct.pack('<H', 2) +                # color index 2 (green)
    struct.pack('<H', 0) +                # reserved
    struct.pack('<H', 100) +              # brightness = 100
    struct.pack('<H', 70) +               # parameter (70 for green)
    b'\x00\x00\x01\x00'                   # reserved (as in file3)
)
# Command Block 2: For the second phase (red)
# In the file3 example the second block (for red) was 16 bytes:
#   2 bytes: pixel count, 2 bytes: color index, 2 bytes: reserved,
#   2 bytes: reserved, 2 bytes: reserved, 2 bytes: brightness, 2 bytes: parameter,
#   2 bytes: reserved.
cmd_block2 = (
    b'\x04\x00' +         # pixel count = 4 (same as num_pixels)
    struct.pack('<H', 1) +  # color index 1 (red)
    b'\x00\x01' +         # reserved
    b'\x00\x00' +         # reserved
    b'\x00\x01' +         # reserved
    struct.pack('>H', 100) +# brightness = 100 (big–endian 0x0064 as in examples)
    struct.pack('>H', 114) +# parameter = 114 (0x0072)
    b'\x01\x00'           # reserved
)

# (In the examples the second command block also contained a "CD0" marker
#  inside it. For our file we’ll write our own color data marker immediately below.)

# Now build the color data table.
# Our plan: for each phase (total num_phases phases), use a constant color for ticks_per_phase ticks.
# In phase 0, 2, 4, … (even–numbered phases) we use green; in phases 1, 3, 5, … we use red.
color_table = bytearray()
for phase in range(num_phases):
    # decide on the color for this phase:
    if phase % 2 == 0:
        color = color_green
    else:
        color = color_red
    # for this phase, write ticks_per_phase ticks
    for _ in range(ticks_per_phase):
        # for each tick, write the same color for each pixel
        for _ in range(num_pixels):
            color_table += color

# Make sure we have the expected size:
expected_size = total_ticks * bytes_per_tick  # 20 * 40 * (4*4) = 12800 bytes
assert len(color_table) == expected_size, f"Color table size is {len(color_table)}, expected {expected_size}"

# Build the footer: marker "BT" then four 0 bytes.
footer = b'BT' + b'\x00\x00\x00\x00'

# Optionally, you can add a marker right before the color table.
# (In the red–only examples, the color table was preceded by a 4–byte marker such as b'CD0\x01'.)
color_marker = b'CD0\x01'

# Now concatenate all parts to form the file:
prg_data = header + cmd_block1 + cmd_block2 + color_marker + color_table + footer

# Write the binary file.
output_filename = "alternating.prg"
with open(output_filename, "wb") as f:
    f.write(prg_data)

print(f"Created {output_filename} ({len(prg_data)} bytes).")
