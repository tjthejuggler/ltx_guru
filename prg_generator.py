#!/usr/bin/env python3
"""
LTX Ball PRG Generator - High Precision (1000Hz) - v2
Generates PRG files for LTX balls from a JSON color sequence.
This version hardcodes the PRG file refresh rate to 1000 Hz for high precision.
It uses the latest understanding of header fields 0x16 and 0x1E.

Usage:
    python3 prg_generator_new.py input.prg.json output.prg
"""

import json
import struct
import sys
import pprint
import os
import math

def round_timing_to_refresh_rate(time_value, json_refresh_rate_hz=100):
    """
    Round timing values from JSON to match the JSON's refresh rate precision.
    Returns integer time units based on JSON's refresh rate.
    """
    if json_refresh_rate_hz <= 0:
        return int(time_value) # Or raise error
    return int(round(float(time_value)))

# --- Constants based on observed format ---
FILE_SIGNATURE = b'PR\x03IN\x05\x00\x00'
HEADER_CONST_0A = b'\x00\x08'
HEADER_CONST_PI = b'PI'
HEADER_RGB_REPETITION_COUNT_BYTES = b'\x64\x00' # Value 100 LE (for 0x18)
HEADER_CONST_1C = b'\x00\x00'

BLOCK_CONST_02 = b'\x01\x00\x00'
BLOCK_CONST_07 = b'\x00\x00'
BLOCK_CONST_0F_INTERMEDIATE = b'\x00\x00'

LAST_BLOCK_CONST_09 = b'\x43\x44'  # "CD"
LAST_BLOCK_CONST_0D = b'\x00\x00'
LAST_BLOCK_CONST_11_LAST = b'\x00\x00'

FOOTER = b'BT\x00\x00\x00\x00'
RGB_TRIPLE_COUNT_PER_SEGMENT_COLOR_BLOCK = 100 # How many times a color is repeated in its block
DURATION_BLOCK_SIZE = 19
HEADER_SIZE = 32
PRG_FILE_REFRESH_RATE = 1000 # Fixed for this generator
NOMINAL_BASE_FOR_HEADER_FIELDS = 100 # Used in 0x16/0x1E calculations
# --- End Constants ---

def bytes_to_hex(data):
    if isinstance(data, int):
        return f"0x{data:04X}" if data <= 0xFFFF else f"0x{data:X}"
    elif isinstance(data, bytes):
        return ' '.join([f"{b:02X}" for b in data])
    return str(data)

def calculate_legacy_intro_pair(target_index, total_segments):
    if not (1 <= target_index < total_segments): return 0
    base_value_n2_t1 = 370
    vertical_step = 19
    horizontal_step = 300
    value_n_t1 = base_value_n2_t1 + (total_segments - 2) * vertical_step
    value_pair = value_n_t1 + (target_index - 1) * horizontal_step
    return value_pair & 0xFFFF

def calculate_legacy_color_intro_parts(total_segments):
    part1_full = 304 + (total_segments - 1) * 300
    part2_full = 100 * total_segments
    return part1_full & 0xFFFF, part2_full & 0xFFFF

def split_long_segments(segments_in, max_duration=65535):
    new_segments = []
    for duration_units, color, pixels in segments_in:
        if duration_units <= max_duration:
            new_segments.append((duration_units, color, pixels))
            continue
        print(f"[SPLIT] Segment (Color {color}) duration {duration_units} exceeds {max_duration}. Splitting.")
        num_full = duration_units // max_duration
        rem_dur = duration_units % max_duration
        for _ in range(num_full):
            new_segments.append((max_duration, color, pixels))
        if rem_dur > 0:
            new_segments.append((rem_dur, color, pixels))
    return new_segments

def generate_prg_file(input_json_path, output_prg_path):
    print(f"\n[INIT] Starting PRG High-Precision (1000Hz) generation from {input_json_path} to {output_prg_path}")

    try:
        with open(input_json_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Loading JSON failed: {e}"); sys.exit(1)

    default_pixels = data.get('default_pixels', 1)
    json_refresh_rate = data.get('refresh_rate', 100) # For interpreting input JSON timings
    json_end_time_units = data.get('end_time')

    if not (isinstance(default_pixels, int) and 1 <= default_pixels <= 4):
        print(f"[ERROR] Invalid 'default_pixels': {default_pixels}."); sys.exit(1)
    if not (isinstance(json_refresh_rate, int) and json_refresh_rate > 0):
        print(f"[ERROR] Invalid JSON 'refresh_rate': {json_refresh_rate}."); sys.exit(1)
    if json_end_time_units is None:
        print(f"[ERROR] 'end_time' (in JSON units) is required."); sys.exit(1)
    
    original_json_end_time = json_end_time_units
    json_end_time_units = round_timing_to_refresh_rate(json_end_time_units, json_refresh_rate)
    if abs(original_json_end_time - json_end_time_units) > 0.001:
        print(f"[TIMING] Rounded JSON end_time: {original_json_end_time} -> {json_end_time_units} units (at JSON {json_refresh_rate}Hz)")

    print(f"[INIT] JSON Config: DefaultPixels={default_pixels}, JSON RefreshRate={json_refresh_rate}Hz, JSON EndTime={json_end_time_units} units")
    print(f"[INIT] PRG File Config: Output RefreshRate={PRG_FILE_REFRESH_RATE}Hz")

    if 'sequence' not in data or not isinstance(data['sequence'], dict) or not data['sequence']:
        print("[ERROR] JSON 'sequence' is missing, not a dictionary, or empty."); sys.exit(1)

    # Parse sequence items from JSON, convert timings to PRG_FILE_REFRESH_RATE units
    parsed_prg_sequence_items = []
    for t_str, entry_dict in data['sequence'].items():
        json_time_units = round_timing_to_refresh_rate(float(t_str), json_refresh_rate)
        # Convert JSON time units to PRG time units (1000Hz)
        prg_time_units = int(round((json_time_units / json_refresh_rate) * PRG_FILE_REFRESH_RATE))

        color_list = entry_dict.get('color')
        try:
            r, g, b = [int(c) for c in color_list]
            if not all(0 <= val <= 255 for val in (r,g,b)): raise ValueError("Color out of range")
            color_tuple = (r,g,b)
        except Exception: print(f"[ERROR] Invalid color for time {t_str}."); sys.exit(1)
        
        pixels_val = entry_dict.get('pixels', default_pixels)
        if not (isinstance(pixels_val, int) and 1 <= pixels_val <= 4): pixels_val = default_pixels
            
        parsed_prg_sequence_items.append((prg_time_units, {'color': color_tuple, 'pixels': pixels_val}))
    
    parsed_prg_sequence_items.sort(key=lambda x: x[0])
    
    # Convert json_end_time_units to PRG_FILE_REFRESH_RATE units
    prg_total_duration_units = int(round((json_end_time_units / json_refresh_rate) * PRG_FILE_REFRESH_RATE))

    print(f"[INIT] Sorted PRG sequence timestamps (units @ {PRG_FILE_REFRESH_RATE}Hz): {[t for t, _ in parsed_prg_sequence_items]}")
    print(f"[INIT] Total PRG duration: {prg_total_duration_units} units @ {PRG_FILE_REFRESH_RATE}Hz")

    # Calculate actual PRG segments data: (duration_prg_units, color_tuple, pixels)
    actual_prg_segments = []
    if not parsed_prg_sequence_items: print("[ERROR] No segments in sequence."); sys.exit(1)

    for idx, (time_units, entry) in enumerate(parsed_prg_sequence_items):
        next_time_units = prg_total_duration_units
        if idx + 1 < len(parsed_prg_sequence_items):
            next_time_units = parsed_prg_sequence_items[idx+1][0]
        
        duration_prg_units = next_time_units - time_units
        if duration_prg_units <= 0: continue # Skip zero/negative duration segments

        actual_prg_segments.append((duration_prg_units, entry['color'], entry['pixels']))
        print(f"[SEG_CALC] PRG Segment {len(actual_prg_segments)-1}: Start={time_units}, Dur={duration_prg_units}, Color={entry['color']}, Pix={entry['pixels']}")

    if not actual_prg_segments: print("[ERROR] No valid PRG segments calculated."); sys.exit(1)

    # Split long segments
    final_prg_segments_for_blocks = split_long_segments(actual_prg_segments)
    prg_segment_count_n = len(final_prg_segments_for_blocks)
    if prg_segment_count_n == 0: print("[ERROR] No segments after splitting."); sys.exit(1)
    print(f"\n[SUMMARY] Total PRG segments to write (after splitting): {prg_segment_count_n}")

    # --- Calculate Header Values ---
    pointer1 = 21 + 19 * (prg_segment_count_n - 1) if prg_segment_count_n > 0 else 0
    rgb_start_pointer = HEADER_SIZE + prg_segment_count_n * DURATION_BLOCK_SIZE

    dur0_units_actual_prg = final_prg_segments_for_blocks[0][0]

    # Field 0x16 ("Hypothesis 8")
    val_0x16_dec = math.floor(dur0_units_actual_prg / NOMINAL_BASE_FOR_HEADER_FIELDS)
    header_field_16_val = val_0x16_dec

    # Field 0x1E (Logic refined to "Hypothesis 4 Simplified" / "Final Refined Logic" from docs)
    # val_0x16_dec is already calculated as floor(dur0_units_actual_prg / NOMINAL_BASE_FOR_HEADER_FIELDS)
    calculated_remainder = dur0_units_actual_prg - (val_0x16_dec * NOMINAL_BASE_FOR_HEADER_FIELDS)

    if calculated_remainder == 0 and dur0_units_actual_prg >= 1000: # Threshold condition
        val_0x1E_dec = dur0_units_actual_prg
    else:
        val_0x1E_dec = calculated_remainder
    header_field_1E_val = val_0x1E_dec & 0xFFFF
    
    print("\n[HEADER_CALC] Calculated Header Values:")
    print(f"  Default Pixels (0x08, >H): {default_pixels} ({bytes_to_hex(default_pixels)})")
    print(f"  PRG Refresh Rate (0x0C, <H): {PRG_FILE_REFRESH_RATE} ({bytes_to_hex(PRG_FILE_REFRESH_RATE)})")
    print(f"  Pointer1 (0x10, <I): {pointer1} ({bytes_to_hex(pointer1)})")
    print(f"  PRG SegmentCount (0x14, <H): {prg_segment_count_n} ({bytes_to_hex(prg_segment_count_n)})")
    print(f"  Field 0x16 (<H): {header_field_16_val} ({bytes_to_hex(header_field_16_val)}) (Dur0_PRG={dur0_units_actual_prg})")
    print(f"  Field 0x18 (<H): RGB Repetition Count {RGB_TRIPLE_COUNT_PER_SEGMENT_COLOR_BLOCK} ({bytes_to_hex(HEADER_RGB_REPETITION_COUNT_BYTES)})")
    print(f"  RGB Start Pointer (0x1A, <H): {rgb_start_pointer} ({bytes_to_hex(rgb_start_pointer)})")
    print(f"  Field 0x1E (<H): {header_field_1E_val} ({bytes_to_hex(header_field_1E_val)}) (Dur0_PRG={dur0_units_actual_prg})")

    # --- Write PRG File ---
    try:
        with open(output_prg_path, 'wb') as f:
            f.write(FILE_SIGNATURE)
            f.write(struct.pack('>H', default_pixels))
            f.write(HEADER_CONST_0A)
            f.write(struct.pack('<H', PRG_FILE_REFRESH_RATE)) # Hardcoded 1000Hz
            f.write(HEADER_CONST_PI)
            f.write(struct.pack('<I', pointer1))
            f.write(struct.pack('<H', prg_segment_count_n))
            f.write(struct.pack('<H', header_field_16_val))
            f.write(HEADER_RGB_REPETITION_COUNT_BYTES)
            f.write(struct.pack('<H', rgb_start_pointer))
            f.write(HEADER_CONST_1C)
            f.write(struct.pack('<H', header_field_1E_val))
            print(f"[WRITE] Header complete.")

            for idx, (dur_k_prg, color_k, pix_k) in enumerate(final_prg_segments_for_blocks):
                if idx < prg_segment_count_n - 1: # Intermediate block
                    dur_k_plus_1_prg = final_prg_segments_for_blocks[idx+1][0]
                    index1_val = calculate_legacy_intro_pair(idx + 1, prg_segment_count_n)
                    
                    # Field +0x09 logic for intermediate blocks (Revised 2025-06-01 based on R0.1_B0.1_G10_1000hz.prg)
                    field_09_part2 = dur_k_prg # CurrentSegmentDurationUnits
                    if idx == 0:
                        field_09_part1 = idx + 1 # SegmentNumber_1_based is 1 for the first block
                    else: # idx > 0
                        dur_k_minus_1_prg = final_prg_segments_for_blocks[idx-1][0]
                        if dur_k_prg == dur_k_minus_1_prg:
                            field_09_part1 = dur_k_prg
                        else:
                            field_09_part1 = idx + 1
                    field_09_bytes = struct.pack('<H', field_09_part1) + struct.pack('<H', field_09_part2)

                    # Field +0x11 logic (Hypothesis F - Revised 2025-06-01)
                    field_11_val = 0
                    if dur_k_plus_1_prg < 100:
                        field_11_val = dur_k_plus_1_prg
                    elif dur_k_plus_1_prg == 100:
                        # This covers:
                        # - Dur0=100, Dur1=100 (e.g., Block 0 of R0.1_B0.1_G10_1000hz) -> field_11_val = 0
                        # - Dur0!=100, Dur1=100 (e.g., 2px_r1_g100_1r) -> field_11_val = 0
                        field_11_val = 0
                    else: # dur_k_plus_1_prg > 100
                        if dur_k_prg == 100:
                             # This covers Dur0=100, Dur1>100 (e.g., Block 1 of R0.1_B0.1_G10_1000hz, where Dur0=100, Dur1=10000) -> field_11_val = 0
                            field_11_val = 0
                        else: # dur_k != 100 AND dur_k_plus_1_prg > 100
                             # This covers Dur0!=100, Dur1>100 (e.g., red_1s_blue_2s_1r, if Dur0=1, Dur1=2. Here it would be Dur_k_plus_1_prg)
                            field_11_val = dur_k_plus_1_prg
                    
                    f.write(struct.pack('<H', pix_k))
                    f.write(BLOCK_CONST_02)
                    f.write(struct.pack('<H', dur_k_prg))
                    f.write(BLOCK_CONST_07)
                    f.write(field_09_bytes)
                    f.write(struct.pack('<H', index1_val))
                    f.write(BLOCK_CONST_0F_INTERMEDIATE)
                    f.write(struct.pack('<H', field_11_val))
                else: # Last block
                    idx2_p1, idx2_p2 = calculate_legacy_color_intro_parts(prg_segment_count_n)
                    f.write(struct.pack('<H', pix_k))
                    f.write(BLOCK_CONST_02)
                    f.write(struct.pack('<H', dur_k_prg))
                    f.write(BLOCK_CONST_07)
                    f.write(LAST_BLOCK_CONST_09)
                    f.write(struct.pack('<H', idx2_p1))
                    f.write(LAST_BLOCK_CONST_0D)
                    f.write(struct.pack('<H', idx2_p2))
                    f.write(LAST_BLOCK_CONST_11_LAST)
            print(f"[WRITE] Duration blocks complete.")

            for _, color_tuple, _, in final_prg_segments_for_blocks:
                r, g, b = color_tuple
                rgb_bytes = struct.pack('BBB', r, g, b)
                f.write(rgb_bytes * RGB_TRIPLE_COUNT_PER_SEGMENT_COLOR_BLOCK)
            print(f"[WRITE] RGB data complete.")
            f.write(FOOTER)
            print(f"[WRITE] Footer complete.")
    except Exception as e:
        print(f"[ERROR] Writing PRG file failed: {e}"); import traceback; traceback.print_exc(); sys.exit(1)
        
    # Verification
    final_size = os.path.getsize(output_prg_path)
    expected_size = HEADER_SIZE + (prg_segment_count_n * DURATION_BLOCK_SIZE) + \
                    (prg_segment_count_n * 3 * RGB_TRIPLE_COUNT_PER_SEGMENT_COLOR_BLOCK) + len(FOOTER)
    if final_size != expected_size:
        print(f"[WARNING] File size mismatch. Expected: {expected_size}, Actual: {final_size}")
    else:
        print("[VERIFY] File size matches expected calculation.")
    print(f"\n[SUCCESS] Successfully generated {output_prg_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} input.json output.prg")
        sys.exit(1)
    generate_prg_file(sys.argv[1], sys.argv[2])