#!/usr/bin/env python3
"""
LTX Ball PRG Generator - v7 - Modified to always output 100Hz PRG files.

Generates PRG files for LTX balls from a JSON color sequence.
The output PRG file will always have a refresh rate of 100Hz.
Timings from the input JSON (refresh_rate, sequence keys, end_time) are
interpreted and scaled to this target 100Hz PRG timing.

Usage:
    python3 prg_generator.py input.json output.prg
"""

import json
import struct
import sys
import pprint
import binascii
import os
import math

# --- Constants based on observed format (Simple Examples) ---
FILE_SIGNATURE = b'PR\x03IN\x05\x00\x00' # 8 bytes
HEADER_CONST_0A = b'\x00\x08'
HEADER_CONST_PI = b'PI'
HEADER_CONST_18 = b'\x64\x00' # Value 100 LE
HEADER_CONST_1C = b'\x00\x00' # Constant part of the 0x1C field

# Duration Block Constants (Simple Format)
BLOCK_CONST_02 = b'\x01\x00\x00'
BLOCK_CONST_07 = b'\x00\x00'
# Last Duration Block Constants
LAST_BLOCK_CONST_09 = b'\x43\x44' # "CD"

FOOTER = b'BT\x00\x00\x00\x00'
RGB_TRIPLE_COUNT = 100
DURATION_BLOCK_SIZE = 19
HEADER_SIZE = 32

TARGET_OUTPUT_PRG_REFRESH_RATE = 100 # <--- NEW: Our desired output PRG refresh rate
NOMINAL_BASE_FOR_HEADER_FIELDS = 100 # Base for calculating certain header/block fields
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


def _calculate_intermediate_block_index1_base(target_index, total_segments):
    """
    Calculates the base value for the Index1 field in intermediate duration blocks.
    This value can exceed 16 bits. The lower 16 bits go to field +0x0D,
    and the higher 16 bits (carry) go to field +0x0F.

    Args:
        target_index (int): The 1-based index for this value pair,
                             corresponding to (block_index + 1). Ranges from 1 to N-1.
        total_segments (int): The total number of segments (N) in the sequence.

    Returns:
        int: The calculated base value (potentially >16 bits).
    """
    if not (1 <= target_index < total_segments):
         print(f"[WARN] _calculate_intermediate_block_index1_base called with invalid target_index {target_index} for {total_segments} segments.")
         return 0

    base_value_n2_t1 = 370
    vertical_step = 19
    horizontal_step = 300

    value_n_t1 = base_value_n2_t1 + (total_segments - 2) * vertical_step
    value_pair_full = value_n_t1 + (target_index - 1) * horizontal_step
    return value_pair_full

def _calculate_last_block_index2_bases(total_segments):
    """
    Calculates the base values for Index2 Part1 and Part2 fields in the *last*
    duration block. These values can exceed 16 bits.
    Part1: Lower 16 bits to +0x0B, Higher 16 bits to +0x0D.
    Part2: Lower 16 bits to +0x0F, Higher 16 bits to +0x11.

    Args:
        total_segments (int): The total number of segments.

    Returns:
        tuple(int, int): (part1_full_value, part2_full_value).
    """
    part1_full = 304 + (total_segments - 1) * 300
    part2_full = 100 * total_segments
    return part1_full, part2_full

def split_long_segments(segments, max_duration=65535):
    """
    Split segments with durations *in PRG time units* exceeding max_duration (65535 for <H).
    """
    print(f"[SPLIT] Checking for segments exceeding maximum duration ({max_duration} PRG time units)...")
    new_segments = []
    split_occurred = False
    original_segment_count = len(segments)

    if original_segment_count == 0:
        return []

    for idx, (duration_prg_units, color, pixels) in enumerate(segments): # duration_prg_units is already in PRG units
        if duration_prg_units <= max_duration:
            new_segments.append((duration_prg_units, color, pixels))
            continue

        split_occurred = True
        print(f"[SPLIT] WARNING: Segment {idx} (Color {color}) has PRG duration {duration_prg_units} PRG units which exceeds {max_duration}. Splitting.")

        num_full_segments = duration_prg_units // max_duration
        remainder_duration = duration_prg_units % max_duration

        for i in range(num_full_segments):
            new_segments.append((max_duration, color, pixels))
            print(f"[SPLIT]  - Added sub-segment {i+1}/{num_full_segments + (1 if remainder_duration > 0 else 0)} with PRG duration {max_duration} PRG units")

        if remainder_duration > 0:
            new_segments.append((remainder_duration, color, pixels))
            print(f"[SPLIT]  - Added sub-segment {num_full_segments+1}/{num_full_segments+1} with PRG duration {remainder_duration} PRG units")

    if split_occurred:
        print(f"[SPLIT] Segment splitting complete. Original: {original_segment_count} segments, New: {len(new_segments)} segments.")
    else:
        print("[SPLIT] No segments exceeded maximum duration.")
    return new_segments

def generate_prg_file(input_json, output_prg):
    """Generates the .prg file from the input JSON, always outputting a 100Hz PRG."""
    print(f"\n[INIT] Starting PRG generation from {input_json} to {output_prg}")
    print(f"[INIT] Target output PRG refresh rate is fixed at: {TARGET_OUTPUT_PRG_REFRESH_RATE}Hz")

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
    json_refresh_rate = data.get('refresh_rate', 1) # Refresh rate specified in the input JSON
    end_time_json_units = data.get('end_time')     # End time from JSON, in JSON time units

    # Validate types
    if not isinstance(default_pixels, int) or not (1 <= default_pixels <= 4):
        print(f"[ERROR] Invalid 'default_pixels': {default_pixels}. Must be int 1-4.")
        sys.exit(1)
    if not isinstance(json_refresh_rate, int) or json_refresh_rate <= 0:
        print(f"[ERROR] Invalid 'refresh_rate' in JSON: {json_refresh_rate}. Must be positive int.")
        sys.exit(1)
    if end_time_json_units is not None and not isinstance(end_time_json_units, (int, float)):
        # README: "end_time: ... Fractional values will be rounded..."
        print(f"[ERROR] Invalid 'end_time' in JSON: {end_time_json_units}. Must be a number (JSON time units).")
        sys.exit(1)

    # Calculate scaling factor to convert JSON time units to Target PRG time units
    time_unit_scaling_factor = TARGET_OUTPUT_PRG_REFRESH_RATE / json_refresh_rate

    print(f"[INIT] Config: DefaultPixels={default_pixels}")
    print(f"[INIT] Input JSON: RefreshRate={json_refresh_rate}Hz, EndTime={end_time_json_units} JSON_units (if specified)")
    print(f"[INIT] Time Unit Scaling Factor (Target_PRG_units / JSON_unit): {time_unit_scaling_factor:.4f}")

    if 'sequence' not in data or not isinstance(data['sequence'], dict) or not data['sequence']:
        print("[ERROR] JSON 'sequence' is missing, not a dictionary, or empty.")
        sys.exit(1)

    try:
        # Sequence keys are time in JSON TIME UNITS. README: "Can be integers or floating-point numbers,
        # but will be rounded to the nearest integer to match refresh rate precision."
        # (This refers to JSON's refresh rate precision for interpreting the keys).
        sequence_items_json_units = sorted([(round(float(t)), v) for t, v in data['sequence'].items()], key=lambda x: x[0])
    except ValueError:
        print("[ERROR] Sequence keys must be valid numbers representing JSON time units.")
        sys.exit(1)

    print(f"[INIT] Sorted sequence timestamps (JSON units, rounded): {[t for t, _ in sequence_items_json_units]}")

    # --- Calculate Segments ---
    print("\n[SEGMENT_CALC] Processing sequence segments (times will be scaled to PRG units)...")
    segments = [] # Store as (duration_in_PRG_units, color_tuple, pixels)
    if not sequence_items_json_units:
         print("[ERROR] No segments found in sequence after sorting.")
         sys.exit(1)

    for idx, (time_json_units, entry) in enumerate(sequence_items_json_units):
        if not isinstance(entry, dict):
            print(f"[ERROR] Entry for JSON time {time_json_units} units is not a dictionary.")
            sys.exit(1)

        color = entry.get('color')
        # ... (color validation: type, length, values 0-255) ...
        if color is None:
             print(f"[ERROR] Segment at JSON time {time_json_units} units is missing 'color'.")
             sys.exit(1)
        if not isinstance(color, list) or len(color) != 3:
            print(f"[ERROR] Segment at JSON time {time_json_units} units has invalid color format: {color}. Expected [R, G, B].")
            sys.exit(1)
        try:
            r,g,b = [int(c) for c in color]
            if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                raise ValueError("Color values out of range 0-255")
        except (ValueError, TypeError) as e:
            print(f"[ERROR] Invalid RGB color value in segment at JSON time {time_json_units}: {color}. {e}")
            sys.exit(1)

        pixels = entry.get('pixels', default_pixels)
        if not isinstance(pixels, int) or not (1 <= pixels <= 4):
             print(f"[WARNING] Segment at JSON time {time_json_units} units has invalid pixels value ({pixels}). Using default: {default_pixels}.")
             pixels = default_pixels

        # Calculate duration IN TARGET PRG TIME UNITS
        # Convert current segment's JSON start time to PRG start time (scaled and rounded)
        current_segment_prg_start_time = round(time_json_units * time_unit_scaling_factor)

        next_segment_prg_start_time = 0 # Initialize
        if idx + 1 < len(sequence_items_json_units):
            next_segment_start_json_units = sequence_items_json_units[idx + 1][0]
            next_segment_prg_start_time = round(next_segment_start_json_units * time_unit_scaling_factor)
        elif end_time_json_units is not None:
            # README: "end_time: ... in time units." (JSON time units)
            # "Note: Fractional values will be rounded to the nearest integer..."
            rounded_end_time_json_units = round(float(end_time_json_units))
            if rounded_end_time_json_units < time_json_units: # Compare JSON units with JSON units
                 print(f"[ERROR] JSON 'end_time' ({rounded_end_time_json_units} JSON units) is earlier than the start time ({time_json_units} JSON units) of the last segment.")
                 sys.exit(1)
            next_segment_prg_start_time = round(rounded_end_time_json_units * time_unit_scaling_factor)
        else:
            # Default duration for the last segment if 'end_time' not specified.
            # This should be 1 second, represented in Target PRG time units.
            default_duration_prg_units = TARGET_OUTPUT_PRG_REFRESH_RATE # e.g., 100 units for 100Hz PRG
            print(f"[WARNING] 'end_time' not specified in JSON. Assigning default duration ({default_duration_prg_units} PRG units = 1s) to the last segment.")
            next_segment_prg_start_time = current_segment_prg_start_time + default_duration_prg_units

        duration_prg_units = next_segment_prg_start_time - current_segment_prg_start_time
        if duration_prg_units <= 0:
             print(f"[WARNING] Segment {idx} (JSON time {time_json_units} units) has non-positive PRG duration ({duration_prg_units} PRG units after scaling/rounding). Skipping.")
             continue

        rgb_tuple = (r,g,b)

        print(f"[SEGMENT_CALC] - Seg {idx}: JSON_Time={time_json_units} units -> PRG_Start_Time={current_segment_prg_start_time} PRG_units.")
        print(f"                 Next PRG_Start_Time={next_segment_prg_start_time} -> Duration={duration_prg_units} PRG_units, Color={rgb_tuple}, Pixels={pixels}")
        segments.append((duration_prg_units, rgb_tuple, pixels))

    if not segments:
        print("[ERROR] No valid segments could be calculated (check durations and times after scaling).")
        sys.exit(1)

    segments = split_long_segments(segments) # Operates on PRG units
    segment_count = len(segments)

    if segment_count == 0:
         print("[ERROR] No segments remaining after processing/splitting.")
         sys.exit(1)

    print(f"\n[SUMMARY] Total PRG segments to write: {segment_count}")

    # --- Calculate Header Values ---
    pointer1 = 21 + 19 * (segment_count - 1) if segment_count > 0 else 0
    rgb_start_pointer = HEADER_SIZE + segment_count * DURATION_BLOCK_SIZE
    
    # Duration for header fields 0x16/0x1E is first segment's duration in PRG units
    first_segment_duration_prg_units = segments[0][0] if segment_count > 0 else 0

    val_0x16_dec = math.floor(first_segment_duration_prg_units / NOMINAL_BASE_FOR_HEADER_FIELDS)
    header_field_16_calculated_val = val_0x16_dec

    val_0x1E_dec = 0
    nominal_base = NOMINAL_BASE_FOR_HEADER_FIELDS # Typically 100

    if segment_count == 1:
        if first_segment_duration_prg_units == nominal_base:
            val_0x1E_dec = 0
        elif first_segment_duration_prg_units % nominal_base == 0:
            if first_segment_duration_prg_units <= 400:
                val_0x1E_dec = 0
            else: 
                val_0x1E_dec = first_segment_duration_prg_units
        else:
            val_0x1E_dec = first_segment_duration_prg_units % nominal_base
    elif segment_count > 1:
        if first_segment_duration_prg_units == 1000:
            val_0x1E_dec = 1000
        elif first_segment_duration_prg_units % nominal_base == 0:
            val_0x1E_dec = 0
        else:
            val_0x1E_dec = first_segment_duration_prg_units % nominal_base

    header_field_1E_calculated_val = val_0x1E_dec & 0xFFFF

    print("\n[HEADER_CALC] Calculated Header Values:")
    print(f"[HEADER_CALC] - Target PRG Refresh Rate (0x0C, <H): {TARGET_OUTPUT_PRG_REFRESH_RATE} ({bytes_to_hex(TARGET_OUTPUT_PRG_REFRESH_RATE)})")
    print(f"[HEADER_CALC] - Pointer1 (0x10, <I): {pointer1} ({bytes_to_hex(pointer1)})")
    print(f"[HEADER_CALC] - SegmentCount (0x14, <H): {segment_count} ({bytes_to_hex(segment_count)})")
    print(f"[HEADER_CALC] - Field 0x16 (<H) Calculated: {header_field_16_calculated_val} ({bytes_to_hex(header_field_16_calculated_val)}) (Dur0_PRG={first_segment_duration_prg_units} PRG_units)")
    print(f"[HEADER_CALC] - RGB Start Pointer (0x1A, <H): {rgb_start_pointer} ({bytes_to_hex(rgb_start_pointer)})")
    print(f"[HEADER_CALC] - Field 0x1E (<H) Calculated: {header_field_1E_calculated_val} ({bytes_to_hex(header_field_1E_calculated_val)}) (Dur0_PRG={first_segment_duration_prg_units} PRG_units)")

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
            f.write(struct.pack('<H', TARGET_OUTPUT_PRG_REFRESH_RATE)); current_offset += 2 # Use target refresh rate
            f.write(HEADER_CONST_PI); current_offset += len(HEADER_CONST_PI)
            f.write(struct.pack('<I', pointer1)); current_offset += 4
            f.write(struct.pack('<H', segment_count)); current_offset += 2
            f.write(struct.pack('<H', header_field_16_calculated_val)); current_offset += 2
            f.write(HEADER_CONST_18); current_offset += len(HEADER_CONST_18)
            f.write(struct.pack('<H', rgb_start_pointer)); current_offset += 2
            f.write(HEADER_CONST_1C); current_offset += len(HEADER_CONST_1C)
            f.write(struct.pack('<H', header_field_1E_calculated_val)); current_offset += 2

            if current_offset != HEADER_SIZE:
                print(f"[ERROR] Header size mismatch! Expected {HEADER_SIZE}, wrote {current_offset}. Aborting.")
                sys.exit(1)
            print(f"[WRITE] Header complete ({current_offset} bytes).")

            # --- Write Duration Blocks (19 Bytes Each) ---
            # duration_units and next_duration_units here are already in PRG units due to earlier scaling.
            print(f"\n[WRITE] Writing {segment_count} Duration Blocks...")
            for idx, (duration_prg_units_current_seg, _, pixels) in enumerate(segments): # Renamed for clarity
                block_start_offset = current_offset
                
                try:
                    if idx < segment_count - 1:
                        next_duration_prg_units = segments[idx + 1][0]
                        
                        index1_full_base_value = _calculate_intermediate_block_index1_base(idx + 1, segment_count)
                        index1_value_at_0D = index1_full_base_value & 0xFFFF
                        index1_carry_at_0F = (index1_full_base_value >> 16) & 0xFFFF

                        field_09_part1 = math.floor(next_duration_prg_units / NOMINAL_BASE_FOR_HEADER_FIELDS)
                        field_09_part2 = NOMINAL_BASE_FOR_HEADER_FIELDS
                        field_09_bytes = struct.pack('<H', field_09_part1) + struct.pack('<H', field_09_part2)

                        field_11_val = 0
                        dur_k = duration_prg_units_current_seg
                        dur_k_plus_1 = next_duration_prg_units

                        if dur_k_plus_1 == 1930: field_11_val = 30
                        elif dur_k_plus_1 == 103: field_11_val = 3
                        elif dur_k_plus_1 == 100: field_11_val = 0
                        elif dur_k_plus_1 > 100 and dur_k_plus_1 % 100 == 0:
                            if dur_k == dur_k_plus_1: field_11_val = dur_k_plus_1
                            elif dur_k >= 1000 and dur_k_plus_1 >= 600: field_11_val = dur_k_plus_1
                            else: field_11_val = 0
                        elif dur_k_plus_1 == 150:
                            if dur_k >= 100: field_11_val = 150
                            else: field_11_val = 50
                        elif dur_k_plus_1 < 100: field_11_val = dur_k_plus_1
                        else:
                            if dur_k >= 100: field_11_val = dur_k_plus_1
                            else: field_11_val = dur_k_plus_1 % 100
                        
                        f.write(struct.pack('<H', pixels))
                        f.write(BLOCK_CONST_02)
                        f.write(struct.pack('<H', duration_prg_units_current_seg)) # Current segment's PRG duration
                        f.write(BLOCK_CONST_07)
                        f.write(field_09_bytes)
                        f.write(struct.pack('<H', index1_value_at_0D))
                        f.write(struct.pack('<H', index1_carry_at_0F))
                        f.write(struct.pack('<H', field_11_val))
                        current_offset += DURATION_BLOCK_SIZE
                    else: # Last block
                        index2_part1_full, index2_part2_full = _calculate_last_block_index2_bases(segment_count)
                        index2_part1_at_0B = index2_part1_full & 0xFFFF
                        index2_part1_carry_at_0D = (index2_part1_full >> 16) & 0xFFFF
                        index2_part2_at_0F = index2_part2_full & 0xFFFF
                        index2_part2_carry_at_11 = (index2_part2_full >> 16) & 0xFFFF

                        f.write(struct.pack('<H', pixels))
                        f.write(BLOCK_CONST_02)
                        f.write(struct.pack('<H', duration_prg_units_current_seg)) # Current (last) segment's PRG duration
                        f.write(BLOCK_CONST_07)
                        f.write(LAST_BLOCK_CONST_09)
                        f.write(struct.pack('<H', index2_part1_at_0B))
                        f.write(struct.pack('<H', index2_part1_carry_at_0D))
                        f.write(struct.pack('<H', index2_part2_at_0F))
                        f.write(struct.pack('<H', index2_part2_carry_at_11))
                        current_offset += DURATION_BLOCK_SIZE
                except struct.error as e:
                     print(f"[ERROR] Failed to pack data for duration block {idx}: {e}. Duration value likely exceeds 65535.")
                     print(f"        Duration_PRG={duration_prg_units_current_seg}, NextDuration_PRG={next_duration_prg_units if idx < segment_count - 1 else 'N/A'}")
                     sys.exit(1)

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
                rgb_bytes = struct.pack('BBB', r, g, b)
                segment_rgb_bytes = rgb_bytes * RGB_TRIPLE_COUNT
                f.write(segment_rgb_bytes)
                bytes_written_this_segment = len(segment_rgb_bytes)
                current_offset += bytes_written_this_segment
                total_rgb_bytes_written += bytes_written_this_segment
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