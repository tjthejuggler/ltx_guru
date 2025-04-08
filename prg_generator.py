#!/usr/bin/env python3
"""
LTX Ball PRG Generator - v5 - CORRECTED Header 0x1C-0x1F

Generates PRG files for LTX balls from a JSON color sequence, matching the
format observed in known-good examples by:
- Writing durations *in time units* within the duration blocks.
- Correctly handling header fields 0x1C-0x1F as 0x0000 + FirstDurationUnits(<H).

Usage:
    python3 prg_generator.py input.json output.prg
"""

import json
import struct
import sys
import pprint
import binascii
import os

# --- Constants based on observed format (Simple Examples) ---
FILE_SIGNATURE = b'PR\x03IN\x05\x00\x00' # 8 bytes
HEADER_CONST_0A = b'\x00\x08'
HEADER_CONST_PI = b'PI'
HEADER_CONST_16 = b'\x00\x00'
HEADER_CONST_18 = b'\x64\x00' # Value 100 LE
HEADER_CONST_1C = b'\x00\x00' # Constant part of the 0x1C field

# Duration Block Constants (Simple Format)
BLOCK_CONST_02 = b'\x01\x00\x00'
BLOCK_CONST_07 = b'\x00\x00'
BLOCK_CONST_09 = b'\x00\x00\x64\x00'
BLOCK_CONST_15 = b'\x00\x00'

# Last Duration Block Constants
LAST_BLOCK_CONST_09 = b'\x43\x44' # "CD"
LAST_BLOCK_CONST_13 = b'\x00\x00'
LAST_BLOCK_CONST_17 = b'\x00\x00'

FOOTER = b'BT\x00\x00\x00\x00'
RGB_TRIPLE_COUNT = 100
DURATION_BLOCK_SIZE = 19
HEADER_SIZE = 32
# --- End Constants ---

def bytes_to_hex(data):
    """Convert bytes or int to a formatted hex string"""
    if isinstance(data, int):
        if data >= 0:
            # Ensure minimum width for better alignment if needed, e.g., 04X for 2 bytes
            if data <= 0xFFFF:
                 return f"0x{data:04X}"
            else:
                 return f"0x{data:X}" # Longer values
        else:
            return f"-0x{abs(data):X}"
    elif isinstance(data, bytes):
        return ' '.join([f"{b:02X}" for b in data])
    return str(data)

# def calculate_legacy_intro_pair(target_index, total_segments):
#     """
#     Calculates the specific value pair (Index Value 1 equivalent) based on
#     the logic derived from the old 'get_duration_intro'. This pair is used
#     at offset +13 in the duration block logic.

#     Args:
#         target_index (int): The 0-based index of the value pair needed (e.g., for block 0, we need pair 1).
#         total_segments (int): The total number of segments in the sequence.

#     Returns:
#         int: The calculated 16-bit value pair (packed Little Endian later).
#              Returns 0 if target_index is out of bounds.
#     """
#     if not (0 <= target_index < total_segments):
#          print(f"[WARN] calculate_legacy_intro_pair called with invalid target_index {target_index} for {total_segments} segments.")
#          return 0

#     first_value_base_step = 0x13
#     within_row_step = 0x2C

#     base_first_value = (0x33 + (total_segments - 1) * first_value_base_step) & 0xFF
#     current_first_value = (base_first_value + target_index * within_row_step) & 0xFF
#     current_second_value = target_index & 0xFF

#     value_pair = (current_second_value * 256) + current_first_value
#     # print(f"[DEBUG][IntroPair] TargetIdx={target_index}, TotalSegs={total_segments} -> ValuePair=0x{value_pair:04X}")
#     return value_pair

# def calculate_legacy_intro_pair(target_index, total_segments):
#     """
#     Calculates the specific value pair (Index Value 1 equivalent) based on
#     the logic derived from the old 'get_duration_intro'. This pair is used
#     at offset +13 in the duration block logic.

#     Args:
#         target_index (int): The 0-based index of the value pair needed (e.g., for block 0, we need pair 1).
#                              This corresponds to (block_index + 1).
#         total_segments (int): The total number of segments in the sequence.

#     Returns:
#         int: The calculated 16-bit value pair (packed Little Endian later).
#              Returns 0 if target_index is out of bounds.
#     """
#     # Target index should range from 1 to total_segments - 1
#     if not (1 <= target_index < total_segments):
#          print(f"[WARN] calculate_legacy_intro_pair called with invalid target_index {target_index} for {total_segments} segments.")
#          # Optional: You might want to raise an error here instead of returning 0 if this indicates a deeper logic error.
#          # raise ValueError(f"Invalid target_index {target_index} for {total_segments} segments.")
#          return 0 # Keep original behavior for now

#     first_value_base_step = 0x13
#     within_row_step = 0x2C

#     base_first_value = (0x33 + (total_segments - 1) * first_value_base_step) & 0xFF
#     current_first_value = (base_first_value + target_index * within_row_step) & 0xFF

#     # --- CORRECTED LOGIC for the high byte ---
#     if target_index <= 2:
#         current_second_value = target_index & 0xFF
#     else:
#         current_second_value = (target_index + 1) & 0xFF
#     # --- END CORRECTION ---

#     value_pair = (current_second_value * 256) + current_first_value
#     # print(f"[DEBUG][IntroPair] TargetIdx={target_index}, TotalSegs={total_segments} -> ValuePair=0x{value_pair:04X}")
#     return value_pair

# def calculate_legacy_intro_pair(target_index, total_segments):
#     """
#     Calculates the specific value pair (Index Value 1 equivalent) based on
#     the logic derived from known good examples up to N=9. This pair is used
#     at offset +13 in the duration block logic.

#     Args:
#         target_index (int): The 1-based index for this value pair,
#                              corresponding to (block_index + 1). Ranges from 1 to N-1.
#         total_segments (int): The total number of segments (N) in the sequence.

#     Returns:
#         int: The calculated 16-bit value pair (packed Little Endian later).
#              Returns 0 or raises error if target_index is out of bounds.
#     """
#     if not (1 <= target_index < total_segments):
#          print(f"[WARN] calculate_legacy_intro_pair called with invalid target_index {target_index} for {total_segments} segments.")
#          # Consider raising an error for clearer debugging:
#          # raise ValueError(f"Invalid target_index {target_index} for {total_segments} segments.")
#          return 0 # Maintain original behavior

#     # --- Low Byte Calculation (Seems Stable) ---
#     first_value_base_step = 0x13 # 19
#     within_row_step = 0x2C       # 44
#     base_first_value = (0x33 + (total_segments - 1) * first_value_base_step) & 0xFF
#     current_first_value = (base_first_value + target_index * within_row_step) & 0xFF

#     # --- High Byte Calculation (Derived from N=1 to N=9) ---
#     diff = 0
#     if target_index == 1:
#         # Rule for T=1
#         diff = 0
#     elif target_index == 2:
#         # Rule for T=2 depends on N
#         if total_segments >= 8:
#             diff = 1
#         else:
#             diff = 0 # For N=2 to 7
#     elif target_index >= 3:
#         # Rules for T>=3
#         # Check for the specific N=9, T=8 exception first
#         if total_segments == 9 and target_index == 8:
#             diff = 2
#         else:
#             # General rule for T>=3 (covers N=4-8, and N=9 T=3-7)
#             diff = 1

#     # Calculate high byte: target_index + difference
#     current_second_value = (target_index + diff) & 0xFF # Ensure it fits in a byte

#     # Combine bytes (High byte first for multiplication)
#     value_pair = (current_second_value * 256) + current_first_value
#     # Optional debug print
#     # print(f"[DEBUG][IntroPair] TargetIdx={target_index}, TotalSegs={total_segments} -> Diff={diff}, HighByte=0x{current_second_value:02X}, LowByte=0x{current_first_value:02X} => ValuePair=0x{value_pair:04X}")
#     return value_pair

def calculate_legacy_intro_pair(target_index, total_segments):
    """
    Calculates the 16-bit value pair for intermediate duration blocks (offset +13)
    based on arithmetic progressions observed in known-good files (N=2 to N=9).

    Args:
        target_index (int): The 1-based index for this value pair,
                             corresponding to (block_index + 1). Ranges from 1 to N-1.
        total_segments (int): The total number of segments (N) in the sequence.

    Returns:
        int: The calculated 16-bit value pair (packed Little Endian later).
             Returns 0 or raises error if target_index is out of bounds.
    """
    # Validate target_index relative to total_segments
    if not (1 <= target_index < total_segments):
         print(f"[WARN] calculate_legacy_intro_pair called with invalid target_index {target_index} for {total_segments} segments.")
         # Optional: raise ValueError(f"Invalid target_index {target_index} for {total_segments} segments.")
         return 0 # Maintain original behavior

    # Constants derived from pattern analysis
    base_value_n2_t1 = 370  # Value(N=2, T=1)
    vertical_step = 19      # Difference when N increases by 1 (for fixed T)
    horizontal_step = 300   # Difference when T increases by 1 (for fixed N)

    # Calculate Value(N, 1)
    value_n_t1 = base_value_n2_t1 + (total_segments - 2) * vertical_step

    # Calculate Value(N, T) based on Value(N, 1)
    value_pair = value_n_t1 + (target_index - 1) * horizontal_step

    # Ensure the value fits within 16 bits if necessary (though calculations seem okay)
    # value_pair &= 0xFFFF

    # Optional debug print
    # print(f"[DEBUG][IntroPair] TargetIdx={target_index}, TotalSegs={total_segments} -> ValuePair=0x{value_pair:04X} ({value_pair})")

    return value_pair

def calculate_legacy_color_intro_parts(total_segments):
    """
    Calculates the Index Value 2 Parts 1 & 2 (16-bit each) for the *last*
    duration block based on the logic derived from the old 'get_color_data_intro'.

    Args:
        total_segments (int): The total number of segments.

    Returns:
        tuple(int, int): (part1, part2) as 16-bit values.
    """
    part1_full = 304 + (total_segments - 1) * 300
    part2_full = 100 * total_segments

    part1_16bit = part1_full & 0xFFFF
    part2_16bit = part2_full & 0xFFFF
    # print(f"[DEBUG][ColorIntroParts] Segs={total_segments}: Part1_16b=0x{part1_16bit:04X}, Part2_16b=0x{part2_16bit:04X}")
    return part1_16bit, part2_16bit

def split_long_segments(segments, max_duration=65535):
    """
    Split segments with durations *in time units* exceeding max_duration (65535 for <H).
    """
    print("[SPLIT] Checking for segments exceeding maximum duration (65535 time units)...")
    new_segments = []
    split_occurred = False
    original_segment_count = len(segments) # Store original count for logging

    if original_segment_count == 0:
        return [] # Handle empty input

    for idx, (duration_units, color, pixels) in enumerate(segments):
        if duration_units <= max_duration:
            new_segments.append((duration_units, color, pixels))
            continue

        split_occurred = True
        print(f"[SPLIT] WARNING: Segment {idx} (Color {color}) has duration {duration_units} units which exceeds {max_duration}. Splitting.")

        num_full_segments = duration_units // max_duration
        remainder_duration = duration_units % max_duration

        for i in range(num_full_segments):
            new_segments.append((max_duration, color, pixels))
            print(f"[SPLIT]  - Added sub-segment {i+1}/{num_full_segments + (1 if remainder_duration > 0 else 0)} with duration {max_duration} units")

        if remainder_duration > 0:
            new_segments.append((remainder_duration, color, pixels))
            print(f"[SPLIT]  - Added sub-segment {num_full_segments+1}/{num_full_segments+1} with duration {remainder_duration} units")

    if split_occurred:
        print(f"[SPLIT] Segment splitting complete. Original: {original_segment_count} segments, New: {len(new_segments)} segments.")
    else:
        print("[SPLIT] No segments exceeded maximum duration.")
    return new_segments

def generate_prg_file(input_json, output_prg):
    """Generates the .prg file from the input JSON"""
    print(f"\n[INIT] Starting PRG generation from {input_json} to {output_prg}")

    try:
        with open(input_json, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Input JSON file not found: {input_json}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON file: {input_json} - {e}")
        sys.exit(1)


    print("[INIT] Loaded JSON data:")
    pprint.pprint(data, depth=2)

    default_pixels = data.get('default_pixels', 1)
    refresh_rate = data.get('refresh_rate', 1)
    end_time = data.get('end_time') # end_time is in TIME UNITS

    # Validate types
    if not isinstance(default_pixels, int) or not (1 <= default_pixels <= 4):
        print(f"[ERROR] Invalid 'default_pixels': {default_pixels}. Must be int 1-4.")
        sys.exit(1)
    if not isinstance(refresh_rate, int) or refresh_rate <= 0:
        print(f"[ERROR] Invalid 'refresh_rate': {refresh_rate}. Must be positive int.")
        sys.exit(1)
    if end_time is not None and not isinstance(end_time, int):
        print(f"[ERROR] Invalid 'end_time': {end_time}. Must be an int (time units).")
        sys.exit(1)


    print(f"[INIT] Config: Pixels={default_pixels}, RefreshRate={refresh_rate}Hz, EndTime={end_time} units")

    if 'sequence' not in data or not isinstance(data['sequence'], dict) or not data['sequence']:
        print("[ERROR] JSON 'sequence' is missing, not a dictionary, or empty.")
        sys.exit(1)

    try:
        # Keys are time in TIME UNITS
        sequence_items = sorted([(int(t), v) for t, v in data['sequence'].items()], key=lambda x: x[0])
    except ValueError:
        print("[ERROR] Sequence keys must be valid integers representing time units.")
        sys.exit(1)

    print(f"[INIT] Sorted sequence timestamps (units): {[t for t, _ in sequence_items]}")

    # --- Calculate Segments ---
    print("\n[SEGMENT_CALC] Processing sequence segments...")
    segments = [] # Store as (duration_in_units, color_tuple, pixels)
    if not sequence_items:
         print("[ERROR] No segments found in sequence after sorting.")
         sys.exit(1)

    for idx, (time_units, entry) in enumerate(sequence_items):
        if not isinstance(entry, dict):
            print(f"[ERROR] Entry for time {time_units} units is not a dictionary.")
            sys.exit(1)

        color = entry.get('color')
        if color is None:
             print(f"[ERROR] Segment at time {time_units} units is missing 'color'.")
             sys.exit(1)
        if not isinstance(color, list) or len(color) != 3:
            print(f"[ERROR] Segment at time {time_units} units has invalid color format: {color}. Expected [R, G, B].")
            sys.exit(1)
        try:
            # Ensure color values are valid bytes
            r,g,b = [int(c) for c in color]
            if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                raise ValueError("Color values out of range 0-255")
        except (ValueError, TypeError) as e:
            print(f"[ERROR] Invalid RGB color value in segment at time {time_units}: {color}. {e}")
            sys.exit(1)


        pixels = entry.get('pixels', default_pixels)
        if not isinstance(pixels, int) or not (1 <= pixels <= 4):
             print(f"[WARNING] Segment at time {time_units} units has invalid pixels value ({pixels}). Using default: {default_pixels}.")
             pixels = default_pixels

        # Calculate duration IN TIME UNITS
        if idx + 1 < len(sequence_items):
            next_time_units = sequence_items[idx + 1][0]
        elif end_time is not None:
            if end_time < time_units:
                 print(f"[ERROR] 'end_time' ({end_time}) is earlier than the start time of the last segment ({time_units}).")
                 sys.exit(1)
            next_time_units = end_time # end_time is already in units
        else:
            print(f"[WARNING] 'end_time' not specified in JSON. Assigning default duration ({refresh_rate} units) to the last segment.")
            next_time_units = time_units + refresh_rate

        duration_units = next_time_units - time_units
        if duration_units <= 0:
             print(f"[WARNING] Segment {idx} at time {time_units} units has non-positive duration ({duration_units} units). Skipping.")
             continue

        rgb_tuple = (r,g,b)

        print(f"[SEGMENT_CALC] - Segment {idx}: Time={time_units} units, NextTime={next_time_units} units, Duration={duration_units} units, Color={rgb_tuple}, Pixels={pixels}")
        segments.append((duration_units, rgb_tuple, pixels))

    if not segments:
        print("[ERROR] No valid segments could be calculated (check durations and times).")
        sys.exit(1)

    # Split segments if duration_units > 65535
    segments = split_long_segments(segments)
    segment_count = len(segments)

    if segment_count == 0:
         print("[ERROR] No segments remaining after processing/splitting.")
         sys.exit(1)

    print(f"\n[SUMMARY] Total segments to write: {segment_count}")

    # --- Calculate Header Values ---
    pointer1 = 21 + 19 * (segment_count - 1)
    rgb_start_pointer = HEADER_SIZE + segment_count * DURATION_BLOCK_SIZE
    # Duration for header field 0x1E is first segment's duration in units
    first_segment_duration_units = segments[0][0]

    print("\n[HEADER_CALC] Calculated Header Values:")
    print(f"[HEADER_CALC] - Pointer1 (0x10, <I): {pointer1} ({bytes_to_hex(pointer1)})")
    print(f"[HEADER_CALC] - SegmentCount (0x14, <H): {segment_count} ({bytes_to_hex(segment_count)})")
    print(f"[HEADER_CALC] - RGB Start Pointer (0x1A, <H): {rgb_start_pointer} ({bytes_to_hex(rgb_start_pointer)})")
    print(f"[HEADER_CALC] - Header Field 0x1C (<H): Constant 0 ({bytes_to_hex(HEADER_CONST_1C)})")
    print(f"[HEADER_CALC] - Header Field 0x1E (<H): First Duration Units {first_segment_duration_units} ({bytes_to_hex(first_segment_duration_units)})")

    # --- Write PRG File ---
    print(f"\n[WRITE] Writing PRG file: {output_prg}")
    try:
        with open(output_prg, 'wb') as f:
            current_offset = 0

            # --- Write Header (32 Bytes) ---
            print("[WRITE] Writing Header...")
            f.write(FILE_SIGNATURE); current_offset += len(FILE_SIGNATURE)
            f.write(struct.pack('>H', default_pixels)); current_offset += 2 # Pixels BE
            f.write(HEADER_CONST_0A); current_offset += len(HEADER_CONST_0A)
            f.write(struct.pack('<H', refresh_rate)); current_offset += 2 # Refresh LE
            f.write(HEADER_CONST_PI); current_offset += len(HEADER_CONST_PI)
            f.write(struct.pack('<I', pointer1)); current_offset += 4 # Pointer1 LE
            f.write(struct.pack('<H', segment_count)); current_offset += 2 # Seg Count LE
            f.write(HEADER_CONST_16); current_offset += len(HEADER_CONST_16) # Const 00 00 @ 0x16
            f.write(HEADER_CONST_18); current_offset += len(HEADER_CONST_18) # Const 64 00 @ 0x18
            f.write(struct.pack('<H', rgb_start_pointer)); current_offset += 2 # RGB Start LE @ 0x1A
            f.write(HEADER_CONST_1C); current_offset += len(HEADER_CONST_1C) # Const 00 00 @ 0x1C <-- CORRECTED
            f.write(struct.pack('<H', first_segment_duration_units)); current_offset += 2 # First Duration Units LE @ 0x1E <-- CORRECTED

            if current_offset != HEADER_SIZE:
                print(f"[ERROR] Header size mismatch! Expected {HEADER_SIZE}, wrote {current_offset}. Aborting.")
                sys.exit(1)
            print(f"[WRITE] Header complete ({current_offset} bytes).")

            # --- Write Duration Blocks (19 Bytes Each) ---
            print(f"\n[WRITE] Writing {segment_count} Duration Blocks...")
            for idx, (duration_units, _, pixels) in enumerate(segments):
                block_start_offset = current_offset
                # print(f"[WRITE] - Writing Block {idx} @0x{block_start_offset:04X}: Dur={duration_units} units, Pix={pixels}")

                try:
                    # Structure for segments 0 to n-2
                    if idx < segment_count - 1:
                        next_duration_units = segments[idx + 1][0]
                        index1_value = calculate_legacy_intro_pair(idx + 1, segment_count)

                        f.write(struct.pack('<H', pixels))               # +0 Pixels
                        f.write(BLOCK_CONST_02)                           # +2 Const
                        f.write(struct.pack('<H', duration_units))       # +5 Current Duration UNITS
                        f.write(BLOCK_CONST_07)                           # +7 Const
                        f.write(BLOCK_CONST_09)                           # +9 Const
                        f.write(struct.pack('<H', index1_value))         # +13 Index1
                        f.write(BLOCK_CONST_15)                           # +15 Const
                        f.write(struct.pack('<H', next_duration_units)) # +17 Next Duration UNITS
                        current_offset += DURATION_BLOCK_SIZE

                    # Structure for the LAST segment (n-1)
                    else:
                        index2_part1, index2_part2 = calculate_legacy_color_intro_parts(segment_count)

                        f.write(struct.pack('<H', pixels))               # +0 Pixels
                        f.write(BLOCK_CONST_02)                           # +2 Const
                        f.write(struct.pack('<H', duration_units))       # +5 Current Duration UNITS
                        f.write(BLOCK_CONST_07)                           # +7 Const
                        f.write(LAST_BLOCK_CONST_09)                      # +9 "CD"
                        f.write(struct.pack('<H', index2_part1))         # +11 Index2 Part1
                        f.write(LAST_BLOCK_CONST_13)                      # +13 Const
                        f.write(struct.pack('<H', index2_part2))         # +15 Index2 Part2
                        f.write(LAST_BLOCK_CONST_17)                      # +17 Const
                        current_offset += DURATION_BLOCK_SIZE

                except struct.error as e:
                     # This usually means duration_units or next_duration_units > 65535
                     print(f"[ERROR] Failed to pack data for duration block {idx}: {e}. Duration value likely exceeds 65535.")
                     print(f"        Duration={duration_units}, NextDuration={next_duration_units if idx < segment_count - 1 else 'N/A'}")
                     sys.exit(1)


                # Verify block size (redundant if struct.pack works, but good sanity check)
                if current_offset - block_start_offset != DURATION_BLOCK_SIZE:
                     print(f"[ERROR] Duration block {idx} size mismatch! Expected {DURATION_BLOCK_SIZE}, wrote {current_offset - block_start_offset}. Aborting.")
                     sys.exit(1)

            print(f"[WRITE] Duration blocks complete. Current offset: 0x{current_offset:04X} (Expected RGB start: 0x{rgb_start_pointer:04X})")
            if current_offset != rgb_start_pointer:
                 print(f"[ERROR] Offset mismatch before RGB data! Expected 0x{rgb_start_pointer:04X}, got 0x{current_offset:04X}. Aborting.")
                 sys.exit(1)

            # --- Write RGB Data ---
            print(f"\n[WRITE] Writing RGB Data (Starting @0x{current_offset:04X})...")
            total_rgb_bytes_written = 0
            for idx, (_, color, pixels) in enumerate(segments):
                r, g, b = color
                # Packing already validated during segment calculation
                rgb_bytes = struct.pack('BBB', r, g, b)

                segment_rgb_bytes = rgb_bytes * RGB_TRIPLE_COUNT
                f.write(segment_rgb_bytes)
                bytes_written_this_segment = len(segment_rgb_bytes)
                current_offset += bytes_written_this_segment
                total_rgb_bytes_written += bytes_written_this_segment
                # Reduce debug spew
                # if idx < 2 or idx == segment_count - 1:
                #     print(f"[WRITE]  - Segment {idx}: Wrote {bytes_written_this_segment} bytes for Color {color}")
                # elif idx == 2:
                #     print("[WRITE]  - (Skipping RGB details...)")

            print(f"[WRITE] RGB data complete. Total RGB bytes: {total_rgb_bytes_written}. Current offset: 0x{current_offset:04X}")

            # --- Write Footer ---
            print("\n[WRITE] Writing Footer...")
            f.write(FOOTER)
            current_offset += len(FOOTER)
            print(f"[WRITE] Footer complete. Final offset: 0x{current_offset:04X}")

    except IOError as e:
        print(f"[ERROR] Failed to write file {output_prg}: {e}")
        sys.exit(1)
    # Removed general struct.error catch here, handled it specifically in duration block writing

    # --- Final Verification ---
    final_size = os.path.getsize(output_prg)
    expected_size = HEADER_SIZE + (segment_count * DURATION_BLOCK_SIZE) + (segment_count * 3 * RGB_TRIPLE_COUNT) + len(FOOTER)
    print(f"\n[VERIFY] Final file size: {final_size} bytes.")
    print(f"[VERIFY] Expected size calculation: {expected_size} bytes.")
    if final_size != expected_size:
        print(f"[WARNING] Final file size ({final_size}) does not match expected calculation ({expected_size}).")
    else:
        print("[VERIFY] File size matches expected calculation.")

    print(f"\n[SUCCESS] Successfully generated {output_prg}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} input.json output.prg")
        sys.exit(1)

    input_json_path = sys.argv[1]
    output_prg_path = sys.argv[2]

    # Moved file existence check earlier
    # if not os.path.exists(input_json_path):
    #     print(f"[ERROR] Input JSON file not found: {input_json_path}")
    #     sys.exit(1)

    generate_prg_file(input_json_path, output_prg_path)