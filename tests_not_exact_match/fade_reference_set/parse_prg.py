#!/usr/bin/env python3
"""Quick PRG parser for byte-level diff."""
import struct, sys

def parse_prg(path):
    with open(path, 'rb') as f:
        data = f.read()
    print(f'=== {path} ({len(data)} bytes) ===')
    default_px = struct.unpack('>H', data[8:10])[0]
    refresh = struct.unpack('<H', data[12:14])[0]
    pointer1 = struct.unpack('<I', data[16:20])[0]
    seg_count = struct.unpack('<H', data[20:22])[0]
    f16 = struct.unpack('<H', data[22:24])[0]
    f18 = struct.unpack('<H', data[24:26])[0]
    rgb_start = struct.unpack('<H', data[26:28])[0]
    f1e = struct.unpack('<H', data[30:32])[0]
    print(f'  default_pixels={default_px}, refresh={refresh}, pointer1={pointer1}, seg_count={seg_count}')
    print(f'  f16={f16}, f18={f18}, rgb_start={rgb_start}, f1e={f1e}')
    print('  Duration blocks:')
    for i in range(seg_count):
        off = 32 + i * 19
        b = data[off:off + 19]
        pixels = struct.unpack('<H', b[0:2])[0]
        duration = struct.unpack('<H', b[5:7])[0]
        if i == seg_count - 1:
            cd = b[9:11]
            i2_p1_lo = struct.unpack('<H', b[11:13])[0]
            i2_p1_hi = struct.unpack('<H', b[13:15])[0]
            i2_p2_lo = struct.unpack('<H', b[15:17])[0]
            i2_p2_hi = struct.unpack('<H', b[17:19])[0]
            print(f'  [LAST] block{i}: pixels={pixels}, dur={duration}, CD={cd.hex()}, '
                  f'idx2_p1={i2_p1_lo | (i2_p1_hi << 16)}, idx2_p2={i2_p2_lo | (i2_p2_hi << 16)}')
        else:
            f9a = struct.unpack('<H', b[9:11])[0]
            f9b = struct.unpack('<H', b[11:13])[0]
            f0d = struct.unpack('<H', b[13:15])[0]
            f0f = struct.unpack('<H', b[15:17])[0]
            f11 = struct.unpack('<H', b[17:19])[0]
            print(f'  block{i}: pixels={pixels}, dur={duration}, f9=({f9a},{f9b}), '
                  f'idx1={f0d | (f0f << 16)}, f11={f11}')
    rgb_end = len(data) - 6
    rgb_size = rgb_end - rgb_start
    print(f'  RGB size: {rgb_size} bytes ({rgb_size // 3} triples)')
    # Show first and last few RGB triples
    rgb = data[rgb_start:rgb_end]
    print(f'  First 5 RGB: ', end='')
    for k in range(min(5, len(rgb)//3)):
        r, g, bb = rgb[k*3], rgb[k*3+1], rgb[k*3+2]
        print(f'({r},{g},{bb}) ', end='')
    print()
    print(f'  Last 5 RGB:  ', end='')
    n = len(rgb) // 3
    for k in range(max(0, n-5), n):
        r, g, bb = rgb[k*3], rgb[k*3+1], rgb[k*3+2]
        print(f'({r},{g},{bb}) ', end='')
    print()

for p in sys.argv[1:]:
    parse_prg(p)
    print()
