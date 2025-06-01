#!/usr/bin/env python3
"""
LTX Ball PRG Generator - v6 - Incorporating Advanced Format Discoveries

Generates PRG files for LTX balls from a JSON color sequence, matching the
format observed in known-good examples by:
- Correctly handling conditional logic for Header fields 0x16 and 0x1E.
- Correctly structuring Duration Block fields +0x09 and +0x11.

Usage:
    python3 prg_generator.py input.prg.json output.prg
"""

import json
import struct
import sys
import pprint
import os

def round_timing_to_refresh_rate(time_value, refresh_rate=100):
    """
    Round timing values to match the refresh rate precision.
    For refresh_rate=100, this ensures all timings are multiples of 1 time unit
    (since 1 time unit = 1/100th of a second at 100Hz).
    
    Args:
        time_value: Time value in time units
        refresh_rate: Refresh rate in Hz (default 100)
    
    Returns:
        Rounded time value as integer
    """
    if refresh_rate <= 0:
        return time_value
    
    # For 100Hz refresh rate, we want to round to the nearest whole time unit
    # Since the system expects integer time units already, we just ensure
    # the value is a proper integer
    rounded_time_units = int(round(float(time_value)))
    
    return rounded_time_units

# --- Constants based on observed format ---
FILE_SIGNATURE = b'PR\x03IN\x05\x00\x00'  # 8 bytes
HEADER_CONST_0A = b'\x00\x08'
HEADER_CONST_PI = b'PI'
# HEADER_CONST_16 is now conditional
HEADER_RGB_REPETITION_COUNT_BYTES = b'\x64\x00'  # Value 100 LE (for 0x18)
HEADER_CONST_1C = b'\x00\x00'
# HEADER_FIELD_1E is now conditional

# Duration Block Constants
BLOCK_CONST_02 = b'\x01\x00\x00'
BLOCK_CONST_07 = b'\x00\x00'
# BLOCK_CONST_09 for intermediate blocks is now conditional (SegNum + Dur)
BLOCK_CONST_0F_INTERMEDIATE = b'\x00\x00' # Was BLOCK_CONST_15

# Last Duration Block Constants
LAST_BLOCK_CONST_09 = b'\x43\x44'  # "CD"
LAST_BLOCK_CONST_0D = b'\x00\x00' # Was LAST_BLOCK_CONST_13
LAST_BLOCK_CONST_11_LAST = b'\x00\x00' # Was LAST_BLOCK_CONST_17

FOOTER = b'BT\x00\x00\x00\x00'
RGB_TRIPLE_COUNT = 100  # This is Header field 0x18
DURATION_BLOCK_SIZE = 19
HEADER_SIZE = 32
# --- End Constants ---

def bytes_to_hex(data):
    """Convert bytes or int to a formatted hex string"""
    if isinstance(data, int):
        if data >= 0:
            if data <= 0xFFFF:
                return f"0x{data:04X}"
            else:
                return f"0x{data:X}"
        else:
            return f"-0x{abs(data):X}"
    elif isinstance(data, bytes):
        return ' '.join([f"{b:02X}" for b in data])
    return str(data)

def calculate_legacy_intro_pair(target_index, total_segments):
    """
    Calculates the 16-bit value for intermediate duration blocks (offset +0x0D)
    based on arithmetic progressions observed in known-good files.
    target_index: 1-based index for this value, (block_index + 1). Ranges 1 to N-1.
    total_segments: Total number of segments (N).
    """
    if not (1 <= target_index < total_segments):
        print(f"[WARN] calculate_legacy_intro_pair called with invalid target_index {target_index} for {total_segments} segments.")
        return 0

    base_value_n2_t1 = 370
    vertical_step = 19
    horizontal_step = 300
    value_n_t1 = base_value_n2_t1 + (total_segments - 2) * vertical_step
    value_pair = value_n_t1 + (target_index - 1) * horizontal_step
    value_pair &= 0xFFFF
    # print(f"[DEBUG][IntroPair] TargetIdx={target_index}, TotalSegs={total_segments} -> ValuePair=0x{value_pair:04X}")
    return value_pair

def calculate_legacy_color_intro_parts(total_segments):
    """
    Calculates Index2 Part 1 & 2 for the *last* duration block.
    """
    part1_full = 304 + (total_segments - 1) * 300
    part2_full = 100 * total_segments
    part1_16bit = part1_full & 0xFFFF
    part2_16bit = part2_full & 0xFFFF
    # print(f"[DEBUG][ColorIntroParts] Segs={total_segments}: P1=0x{part1_16bit:04X}, P2=0x{part2_16bit:04X}")
    return part1_16bit, part2_16bit

def split_long_segments(segments, max_duration=65535):
    """
    Split segments with durations *in time units* exceeding max_duration.
    """
    print("[SPLIT] Checking for segments exceeding maximum duration (65535 time units)...")
    new_segments = []
    split_occurred = False
    original_segment_count = len(segments)

    if original_segment_count == 0:
        return []

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
    refresh_rate = data.get('refresh_rate', 1) # Hz
    end_time_units = data.get('end_time')     # in TIME UNITS

    if not isinstance(default_pixels, int) or not (1 <= default_pixels <= 4):
        print(f"[ERROR] Invalid 'default_pixels': {default_pixels}. Must be int 1-4.")
        sys.exit(1)
    if not isinstance(refresh_rate, int) or refresh_rate <= 0:
        print(f"[ERROR] Invalid 'refresh_rate': {refresh_rate}. Must be positive int.")
        sys.exit(1)
    if end_time_units is not None and not isinstance(end_time_units, int):
        print(f"[ERROR] Invalid 'end_time': {end_time_units}. Must be an int (time units).")
        sys.exit(1)

    # Round end_time to refresh rate precision if provided
    if end_time_units is not None:
        original_end_time = end_time_units
        end_time_units = round_timing_to_refresh_rate(end_time_units, refresh_rate)
        if original_end_time != end_time_units:
            print(f"[TIMING] Rounded end_time: {original_end_time} -> {end_time_units} units")

    print(f"[INIT] Config: DefaultPixels={default_pixels}, RefreshRate={refresh_rate}Hz, EndTime={end_time_units} units")

    if 'sequence' not in data or not isinstance(data['sequence'], dict) or not data['sequence']:
        print("[ERROR] JSON 'sequence' is missing, not a dictionary, or empty.")
        sys.exit(1)

    try:
        # Parse sequence items and round timing values to refresh rate precision
        raw_sequence_items = []
        timing_adjustments = []
        
        for t, v in data['sequence'].items():
            # Convert string to float first, then round to nearest integer
            original_time = float(t)
            rounded_time = round_timing_to_refresh_rate(original_time, refresh_rate)
            raw_sequence_items.append((rounded_time, v))
            
            # Track adjustments for logging
            if abs(original_time - rounded_time) > 0.001:  # Only log significant changes
                timing_adjustments.append((original_time, rounded_time))
        
        # Sort by rounded time values
        sequence_items = sorted(raw_sequence_items, key=lambda x: x[0])
        
        # Log any timing adjustments
        if timing_adjustments:
            print(f"[TIMING] Applied timing rounding for {refresh_rate}Hz refresh rate:")
            for orig, rounded in timing_adjustments:
                print(f"[TIMING]   {orig} -> {rounded} units")
        
    except ValueError:
        print("[ERROR] Sequence keys must be valid numbers representing time units.")
        sys.exit(1)

    print(f"[INIT] Sorted sequence timestamps (units): {[t for t, _ in sequence_items]}")

    print("\n[SEGMENT_CALC] Processing sequence segments...")
    segments_data = []  # Store as (duration_units, color_tuple, pixels, nominal_duration_for_header_0x16)
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
            r, g, b = [int(c) for c in color]
            if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                raise ValueError("Color values out of range 0-255")
        except (ValueError, TypeError) as e:
            print(f"[ERROR] Invalid RGB color value in segment at time {time_units}: {color}. {e}")
            sys.exit(1)

        pixels = entry.get('pixels', default_pixels)
        if not isinstance(pixels, int) or not (1 <= pixels <= 4):
            print(f"[WARNING] Segment at time {time_units} units has invalid pixels value ({pixels}). Using default: {default_pixels}.")
            pixels = default_pixels

        if idx + 1 < len(sequence_items):
            next_time_units = sequence_items[idx + 1][0]
        elif end_time_units is not None:
            if end_time_units < time_units:
                print(f"[ERROR] 'end_time' ({end_time_units}) is earlier than the start time of the last segment ({time_units}).")
                sys.exit(1)
            next_time_units = end_time_units
        else:
            print(f"[WARNING] 'end_time' not specified. Assigning default duration ({refresh_rate} units, i.e., 1 sec at current RR) to the last segment.")
            next_time_units = time_units + refresh_rate

        duration_units = next_time_units - time_units
        if duration_units <= 0:
            print(f"[WARNING] Segment {idx} at time {time_units} units has non-positive duration ({duration_units} units). Skipping.")
            continue

        # Calculate nominal duration (e.g., for 10s, it's 10)
        # This logic might need refinement based on how "nominal duration" is truly derived by the official software.
        # For now, if refresh_rate is 1, nominal is duration_units. If refresh_rate is >1 (e.g., 100), assume duration_units / refresh_rate.
        # This is primarily for Header field 0x16 when N=1.
        nominal_duration = 0
        if refresh_rate == 1:
            nominal_duration = duration_units
        elif refresh_rate > 0 : # Avoid division by zero, though already checked
             # If duration_units is 100 for 1s at 100Hz, nominal is 1.
             # If duration_units is 1000 for 10s at 100Hz, nominal is 10.
            nominal_duration = duration_units // refresh_rate if duration_units % refresh_rate == 0 else duration_units / refresh_rate
            # Ensure it's an int if possible for cleaner representation if it's a whole number
            if isinstance(nominal_duration, float) and nominal_duration.is_integer():
                nominal_duration = int(nominal_duration)


        rgb_tuple = (r, g, b)
        print(f"[SEGMENT_CALC] - Segment {idx}: Time={time_units}, NextTime={next_time_units}, DurUnits={duration_units}, NomDur={nominal_duration}, Color={rgb_tuple}, Pix={pixels}")
        segments_data.append((duration_units, rgb_tuple, pixels, nominal_duration))

    if not segments_data:
        print("[ERROR] No valid segments could be calculated.")
        sys.exit(1)

    # Split segments if duration_units > 65535
    # We need to carry the nominal_duration through, though it's only used for the *original* first segment.
    # For simplicity, we'll use the nominal_duration of the original segment for all its split parts if needed,
    # but it won't affect header 0x16 calculations as that depends on the *original* first segment.
    processed_segments_for_blocks = []
    for dur_u, col, pix, nom_dur in segments_data:
        split_parts = split_long_segments([(dur_u, col, pix)], max_duration=65535) # Pass as list of one
        for part_dur, part_col, part_pix in split_parts:
            processed_segments_for_blocks.append((part_dur, part_col, part_pix, nom_dur)) # Keep nom_dur for reference if needed later

    segments_for_blocks = processed_segments_for_blocks
    segment_count = len(segments_for_blocks)

    if segment_count == 0:
        print("[ERROR] No segments remaining after processing/splitting.")
        sys.exit(1)

    print(f"\n[SUMMARY] Total segments to write (after splitting): {segment_count}")

    # --- Calculate Header Values ---
    pointer1 = 21 + 19 * (segment_count - 1)
    rgb_start_pointer = HEADER_SIZE + segment_count * DURATION_BLOCK_SIZE

    # Logic for Header Field 0x16
    dur0_units_original = segments_data[0][0] # Duration of the *original* first segment
    dur0_nominal_original = segments_data[0][3] # Nominal duration of the *original* first segment
    header_field_16_val = 0
    if dur0_units_original == 100:
        header_field_16_val = 0x0100 # 1 00 LE
    elif len(segments_data) == 1: # Original N == 1
        header_field_16_val = int(dur0_nominal_original) & 0xFFFF # Use nominal if N=1 and dur != 100
    else: # N > 1 and Dur0Units != 100
        header_field_16_val = 0x0000

    # Logic for Header Field 0x1E
    header_field_1E_val = 0
    if dur0_units_original == 100:
        header_field_1E_val = 0x0000
    else:
        header_field_1E_val = dur0_units_original & 0xFFFF

    print("\n[HEADER_CALC] Calculated Header Values:")
    print(f"[HEADER_CALC] - Pointer1 (0x10, <I): {pointer1} ({bytes_to_hex(pointer1)})")
    print(f"[HEADER_CALC] - SegmentCount (0x14, <H): {segment_count} ({bytes_to_hex(segment_count)}) (after splits)")
    print(f"[HEADER_CALC] - Field 0x16 (<H): {header_field_16_val} ({bytes_to_hex(header_field_16_val)}) (based on original N={len(segments_data)}, Dur0Units={dur0_units_original}, Nom0Dur={dur0_nominal_original})")
    print(f"[HEADER_CALC] - Field 0x18 (<H): RGB Repetition Count {RGB_TRIPLE_COUNT} ({bytes_to_hex(HEADER_RGB_REPETITION_COUNT_BYTES)})")
    print(f"[HEADER_CALC] - RGB Start Pointer (0x1A, <H): {rgb_start_pointer} ({bytes_to_hex(rgb_start_pointer)})")
    print(f"[HEADER_CALC] - Field 0x1C (<H): Constant 0 ({bytes_to_hex(HEADER_CONST_1C)})")
    print(f"[HEADER_CALC] - Field 0x1E (<H): {header_field_1E_val} ({bytes_to_hex(header_field_1E_val)}) (based on Dur0Units={dur0_units_original})")


    # --- Write PRG File ---
    print(f"\n[WRITE] Writing PRG file: {output_prg}")
    try:
        with open(output_prg, 'wb') as f:
            current_offset = 0

            # --- Write Header (32 Bytes) ---
            print("[WRITE] Writing Header...")
            f.write(FILE_SIGNATURE); current_offset += len(FILE_SIGNATURE)
            f.write(struct.pack('>H', default_pixels)); current_offset += 2
            f.write(HEADER_CONST_0A); current_offset += len(HEADER_CONST_0A)
            f.write(struct.pack('<H', refresh_rate)); current_offset += 2
            f.write(HEADER_CONST_PI); current_offset += len(HEADER_CONST_PI)
            f.write(struct.pack('<I', pointer1)); current_offset += 4
            f.write(struct.pack('<H', segment_count)); current_offset += 2 # N after splits
            f.write(struct.pack('<H', header_field_16_val)); current_offset += 2 # Field 0x16
            f.write(HEADER_RGB_REPETITION_COUNT_BYTES); current_offset += 2 # Field 0x18
            f.write(struct.pack('<H', rgb_start_pointer)); current_offset += 2
            f.write(HEADER_CONST_1C); current_offset += 2 # Field 0x1C
            f.write(struct.pack('<H', header_field_1E_val)); current_offset += 2 # Field 0x1E

            if current_offset != HEADER_SIZE:
                print(f"[ERROR] Header size mismatch! Expected {HEADER_SIZE}, wrote {current_offset}. Aborting.")
                sys.exit(1)
            print(f"[WRITE] Header complete ({current_offset} bytes).")

            # --- Write Duration Blocks (19 Bytes Each) ---
            print(f"\n[WRITE] Writing {segment_count} Duration Blocks...")
            for idx, (dur_k_units, _, pix_k, _) in enumerate(segments_for_blocks):
                block_start_offset = current_offset
                # print(f"[WRITE] - Writing Block {idx} @0x{block_start_offset:04X}: Dur={dur_k_units} units, Pix={pix_k}")

                try:
                    # Structure for INTERMEDIATE segments (0 to N-2)
                    if idx < segment_count - 1:
                        dur_k_plus_1_units = segments_for_blocks[idx + 1][0]
                        index1_value = calculate_legacy_intro_pair(idx + 1, segment_count)
                        
                        # Field +0x09: Segment Index & Duration (NEW LOGIC ATTEMPT 2)
                        field_plus_09_part1 = 0
                        field_plus_09_part2 = 0
                        
                        current_segment_0_indexed = idx # dur_k_units, pix_k are already for current segment

                        if current_segment_0_indexed == 0:
                            field_plus_09_part1 = 0x0000
                            if dur_k_units < 256:
                                field_plus_09_part2 = dur_k_units
                            else:
                                field_plus_09_part2 = 100 # 0x64
                        else: # idx > 0
                            field_plus_09_part1 = current_segment_0_indexed + 1 # 1-based segment number
                            field_plus_09_part2 = dur_k_units
                        
                        field_plus_09_bytes = struct.pack('<H', field_plus_09_part1) + \
                                            struct.pack('<H', field_plus_09_part2)

                        # Field +0x11: Next Segment Info (Conditional)
                        field_plus_11_val = 0
                        if dur_k_plus_1_units < 100:
                            field_plus_11_val = dur_k_plus_1_units
                        else: # dur_k_plus_1_units >= 100
                            if dur_k_units == 100:
                                field_plus_11_val = pix_k
                            else: # dur_k_units != 100
                                if dur_k_plus_1_units == 100:
                                    field_plus_11_val = 0x0000
                                else: # dur_k_plus_1_units > 100 AND dur_k_units != 100
                                    field_plus_11_val = dur_k_units
                        
                        f.write(struct.pack('<H', pix_k))              # +0x00 Pixels
                        f.write(BLOCK_CONST_02)                        # +0x02 Const
                        f.write(struct.pack('<H', dur_k_units))        # +0x05 Current Duration UNITS
                        f.write(BLOCK_CONST_07)                        # +0x07 Const
                        f.write(field_plus_09_bytes)                   # +0x09 SegNum_1based + CurrentDurUnits
                        f.write(struct.pack('<H', index1_value))      # +0x0D Index1
                        f.write(BLOCK_CONST_0F_INTERMEDIATE)           # +0x0F Const
                        f.write(struct.pack('<H', field_plus_11_val))  # +0x11 Next Segment Info (Conditional)
                        current_offset += DURATION_BLOCK_SIZE

                    # Structure for the LAST segment (N-1)
                    else:
                        index2_part1, index2_part2 = calculate_legacy_color_intro_parts(segment_count)

                        f.write(struct.pack('<H', pix_k))               # +0x00 Pixels
                        f.write(BLOCK_CONST_02)                        # +0x02 Const
                        f.write(struct.pack('<H', dur_k_units))        # +0x05 Current Duration UNITS
                        f.write(BLOCK_CONST_07)                        # +0x07 Const
                        f.write(LAST_BLOCK_CONST_09)                   # +0x09 "CD"
                        f.write(struct.pack('<H', index2_part1))      # +0x0B Index2 Part1
                        f.write(LAST_BLOCK_CONST_0D)                   # +0x0D Const
                        f.write(struct.pack('<H', index2_part2))      # +0x0F Index2 Part2
                        f.write(LAST_BLOCK_CONST_11_LAST)              # +0x11 Const
                        current_offset += DURATION_BLOCK_SIZE

                except struct.error as e:
                    print(f"[ERROR] Failed to pack data for duration block {idx}: {e}. Value likely exceeds 65535.")
                    print(f"        Dur_k={dur_k_units}, Dur_k+1={dur_k_plus_1_units if idx < segment_count - 1 else 'N/A'}")
                    sys.exit(1)

                if current_offset - block_start_offset != DURATION_BLOCK_SIZE:
                    print(f"[ERROR] Duration block {idx} size mismatch! Expected {DURATION_BLOCK_SIZE}, wrote {current_offset - block_start_offset}. Aborting.")
                    sys.exit(1)

            print(f"[WRITE] Duration blocks complete. Current offset: 0x{current_offset:04X}")
            if current_offset != rgb_start_pointer:
                print(f"[ERROR] Offset mismatch before RGB data! Expected 0x{rgb_start_pointer:04X}, got 0x{current_offset:04X}. Aborting.")
                sys.exit(1)

            # --- Write RGB Data ---
            print(f"\n[WRITE] Writing RGB Data (Starting @0x{current_offset:04X})...")
            total_rgb_bytes_written = 0
            for idx, (_, color_tuple, _, _) in enumerate(segments_for_blocks):
                r, g, b = color_tuple
                rgb_bytes = struct.pack('BBB', r, g, b)
                segment_rgb_bytes = rgb_bytes * RGB_TRIPLE_COUNT
                f.write(segment_rgb_bytes)
                total_rgb_bytes_written += len(segment_rgb_bytes)
                current_offset += len(segment_rgb_bytes)

            print(f"[WRITE] RGB data complete. Total RGB bytes: {total_rgb_bytes_written}. Current offset: 0x{current_offset:04X}")

            # --- Write Footer ---
            print("\n[WRITE] Writing Footer...")
            f.write(FOOTER)
            current_offset += len(FOOTER)
            print(f"[WRITE] Footer complete. Final offset: 0x{current_offset:04X}")

    except IOError as e:
        print(f"[ERROR] Failed to write file {output_prg}: {e}")
        sys.exit(1)

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

    generate_prg_file(input_json_path, output_prg_path)