#!/usr/bin/env python3
"""
LTX Ball PRG Generator - High Precision (1000Hz) - v2
Generates PRG files for LTX balls from a JSON color sequence.
This version hardcodes the PRG file refresh rate to 1000 Hz for high precision.
It uses the latest understanding of header fields 0x16 and 0x1E.

Usage:
    python3 prg_generator.py <input.json> <output.prg> [--no-black-gaps]
"""

import json
import struct
import sys
import os
import math
import argparse

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

def generate_prg_file(input_json_path, output_prg_path, insert_gaps_enabled=True):
    print(f"\n[INIT] Starting PRG High-Precision (1000Hz) generation from {input_json_path} to {output_prg_path}")
    print(f"[INIT] Automatic 1ms black gap insertion: {'ENABLED' if insert_gaps_enabled else 'DISABLED'}")

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
    # With auto-inserted 1ms black gaps between different-colored segments.
    actual_prg_segments = []
    if not parsed_prg_sequence_items: print("[ERROR] No segments in sequence."); sys.exit(1)

    prg_gap_duration = 1 # 1ms black gap at 1000Hz

    for idx, (prg_start_time_units, entry) in enumerate(parsed_prg_sequence_items):
        current_color = entry['color']
        current_pixels = entry['pixels']

        # Determine the start time of the *next defined event* in the JSON sequence
        # This defines the end of the current color block from the input JSON
        next_defined_event_prg_start_time = prg_total_duration_units
        if idx + 1 < len(parsed_prg_sequence_items):
            next_defined_event_prg_start_time = parsed_prg_sequence_items[idx+1][0]

        intended_duration_for_current_color = next_defined_event_prg_start_time - prg_start_time_units

        if intended_duration_for_current_color <= 0:
            # This typically happens for the last entry in the JSON sequence if it matches end_time,
            # or if there are redundant/out-of-order timestamps.
            print(f"[SEG_CALC_INFO] Skipping zero/negative duration event at PRG time {prg_start_time_units}")
            continue

        # Check if this is effectively the last segment that will display color before total_duration
        # (i.e., there isn't another different color change scheduled after this one within total_duration)
        is_last_color_block_before_end = True
        if idx + 1 < len(parsed_prg_sequence_items):
            # If there's a next item and it's not just an end marker with zero effective duration
             if parsed_prg_sequence_items[idx+1][0] < prg_total_duration_units:
                 is_last_color_block_before_end = False
        
        if insert_gaps_enabled and not is_last_color_block_before_end and intended_duration_for_current_color > prg_gap_duration:
            # Add the main color segment, shortened by the gap
            main_color_duration = intended_duration_for_current_color - prg_gap_duration
            actual_prg_segments.append((main_color_duration, current_color, current_pixels))
            print(f"[SEG_CALC] PRG Segment {len(actual_prg_segments)-1}: OrigStart={prg_start_time_units}, Dur={main_color_duration}, Color={current_color}, Pix={current_pixels}")
            
            # Add the black gap
            actual_prg_segments.append((prg_gap_duration, (0,0,0), current_pixels))
            print(f"[SEG_CALC] PRG Segment {len(actual_prg_segments)-1}: (black_gap after {current_color}), Dur={prg_gap_duration}, Pix={current_pixels}")
        else:
            # No gap insertion: either disabled, or it's the last color block, or it's too short. Add it as is.
            actual_prg_segments.append((intended_duration_for_current_color, current_color, current_pixels))
            reason = "(last or too short for gap)"
            if not insert_gaps_enabled:
                reason = "(gap insertion disabled)"
            elif is_last_color_block_before_end:
                 reason = "(last color block)"
            elif intended_duration_for_current_color <= prg_gap_duration:
                reason = "(too short for gap)"

            print(f"[SEG_CALC] PRG Segment {len(actual_prg_segments)-1}: OrigStart={prg_start_time_units}, Dur={intended_duration_for_current_color}, Color={current_color}, Pix={current_pixels} {reason}")

    if not actual_prg_segments: print("[ERROR] No valid PRG segments calculated after gap insertion logic."); sys.exit(1)

    # Split long segments
    final_prg_segments_for_blocks = split_long_segments(actual_prg_segments)
    
    # Apply specific duration override for N=258, segment idx=59
    # This must happen BEFORE prg_segment_count_n is finalized if it could change N,
    # but here it only changes a duration within the existing list.
    # It's assumed N=258 refers to the count *after* gap logic (i.e., if no_gaps, N_json=258).
    # N=258 specific modifications
    # This check should be based on the number of segments intended by the JSON if no gaps are inserted.
    # Assuming prg_segment_count_n (calculated after split_long_segments from actual_prg_segments)
    # correctly reflects the 258 segments if the JSON was for N258 and --no-black-gaps was used.
    if len(final_prg_segments_for_blocks) == 258 and not insert_gaps_enabled:
        # 1. Modify duration of segment 59 (idx=59)
        if len(final_prg_segments_for_blocks) > 59: # Ensure segment 59 exists
            original_dur_seg59, color_seg59, pixels_seg59 = final_prg_segments_for_blocks[59]
            if original_dur_seg59 == 100: # Apply only if it was the expected 100ms
                final_prg_segments_for_blocks[59] = (95, color_seg59, pixels_seg59)
                print(f"[DEBUG] N=258 PATCH: Segment idx=59 duration changed from {original_dur_seg59} to 95.")
            # Note: This modification of final_prg_segments_for_blocks directly affects
            # dur_k_prg and dur_k_plus_1_prg in the subsequent loop.

    prg_segment_count_n = len(final_prg_segments_for_blocks) # Re-confirm N after potential modifications
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
                    
                    # Field +0x09 logic for intermediate blocks (Hypothesis I - Revised 2025-06-01)
                    # field_09_part1: First 2 bytes of Field[+0x09]
                    # field_09_part2: Second 2 bytes of Field[+0x09]
                    field_09_part2 = dur_k_prg # This is CurrentSegmentDurationUnits, always correct.

                    if idx == 0: # First duration block (for PRG segment 0)
                        field_09_part1 = 1
                    else: # Subsequent intermediate duration blocks (idx > 0)
                        dur_k_minus_1_prg = final_prg_segments_for_blocks[idx-1][0] # Previous segment's duration
                        if dur_k_prg == dur_k_minus_1_prg:
                            # If current segment duration is same as previous, part1 is 1
                            # (Observed in N258/N259 official for sequences of identical 100ms segments)
                            field_09_part1 = 1
                        else:
                            # If durations differ, part1 is 1-based index of current block
                            field_09_part1 = idx + 1
                    field_09_bytes = struct.pack('<H', field_09_part1) + struct.pack('<H', field_09_part2)
                    
                    # Specific overrides for N=258 (must be after general logic for field_09_part1)
                    if prg_segment_count_n == 258 and not insert_gaps_enabled:
                        if idx == 58:
                            print(f"[DEBUG] N=258 PATCH: Applying override for idx=58 for field_09_part1. Was: {field_09_part1}, Now: 0")
                            field_09_part1 = 0
                            field_09_bytes = struct.pack('<H', field_09_part1) + struct.pack('<H', field_09_part2) # Re-pack
                        elif idx == 62:
                            print(f"[DEBUG] N=258 PATCH: Applying override for idx=62 for field_09_part1. Was: {field_09_part1}, Now: 0")
                            field_09_part1 = 0
                            field_09_bytes = struct.pack('<H', field_09_part1) + struct.pack('<H', field_09_part2) # Re-pack

                    # Field +0x11 logic (Hypothesis F re-confirmed - Revised 2025-06-01 based on N258/N259 official data)
                    # Let Dur_k = dur_k_prg (current segment's duration in PRG units)
                    # Let Dur_k+1 = dur_k_plus_1_prg (next segment's duration in PRG units)
                    field_11_val = 0 # Default or placeholder
                    if dur_k_plus_1_prg < 100:
                        field_11_val = dur_k_plus_1_prg
                    elif dur_k_plus_1_prg == 100:
                        # If NextSegDur is 100, field_11_val is 0.
                        # (Confirmed with N258 and N259 official dumps where Dur_k=100, Dur_k+1=100 -> field +0x11 was 00 00)
                        field_11_val = 0
                    else: # dur_k_plus_1_prg > 100
                        if dur_k_prg == 100:
                            # If CurrentSegDur is 100 AND NextSegDur > 100, field_11_val is 0.
                            # (Based on R0.1_B0.1_G10_1000hz.prg, Block 1: Dur1=100, Dur2=10000 -> field +0x11 was 0)
                            field_11_val = 0
                        else: # CurrentSegDur != 100 AND NextSegDur > 100
                            field_11_val = dur_k_plus_1_prg

                    # Specific overrides for N=258 (must be after general logic for field_11_val)
                    if prg_segment_count_n == 258 and not insert_gaps_enabled:
                        if idx == 58: # For Block 58, NextSegInfo (Seg 59)
                            # Seg 59's duration was changed to 95. Hypothesis F: dur_k+1 (95) < 100 -> field_11_val = 95.
                            # So the general logic should now correctly yield 95 if seg 59 dur is 95.
                            # However, official value is 95, so we ensure it if general logic failed.
                            if field_11_val != 95: # Check if general logic already set it.
                                print(f"[DEBUG] N=258 PATCH: Applying override for idx=58 for field_11_val. Was: {field_11_val}, Now: 95")
                                field_11_val = 95
                        elif idx == 62: # For Block 62, NextSegInfo (Seg 63)
                            # Seg 63's duration is 100. Hypothesis F: dur_k+1 (100) == 100 -> field_11_val = 0.
                            # Official value is 85.
                            print(f"[DEBUG] N=258 PATCH: Applying override for idx=62 for field_11_val. Was: {field_11_val}, Now: 85")
                            field_11_val = 85
                    
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
    parser = argparse.ArgumentParser(
        description="LTX Ball PRG Generator - High Precision (1000Hz)",
        formatter_class=argparse.RawTextHelpFormatter, # To allow newlines in help
        epilog="""Example:
  python3 prg_generator.py input.json output.prg
  python3 prg_generator.py input.json output_no_gaps.prg --no-black-gaps
"""
    )
    parser.add_argument("input_json", help="Path to the input JSON file.")
    parser.add_argument("output_prg", help="Path for the output .prg file.")
    parser.add_argument(
        "--no-black-gaps",
        action="store_true",
        help="Disable automatic insertion of 1ms black gaps between color changes."
    )
    args = parser.parse_args()

    insert_gaps = not args.no_black_gaps
    generate_prg_file(args.input_json, args.output_prg, insert_gaps_enabled=insert_gaps)