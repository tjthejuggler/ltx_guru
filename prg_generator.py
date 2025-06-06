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

def hsv_to_rgb(h, s, v):
    """
    Convert HSV color to RGB.
    
    Args:
        h (float): Hue (0-360)
        s (float): Saturation (0-100)
        v (float): Value/Brightness (0-100)
    
    Returns:
        tuple: (r, g, b) values (0-255)
    """
    h = h % 360
    s = s / 100.0
    v = v / 100.0
    
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    r = int(round((r + m) * 255))
    g = int(round((g + m) * 255))
    b = int(round((b + m) * 255))
    
    return (r, g, b)

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


def _calculate_intermediate_block_index1_base(target_index, total_segments, segments_list):
    """
    Calculates the base value for the Index1 field in intermediate duration blocks.
    This value can exceed 16 bits. The lower 16 bits go to field +0x0D,
    and the higher 16 bits (carry) go to field +0x0F.

    Args:
        target_index (int): The 1-based index for this value pair,
                             corresponding to (block_index + 1). Ranges from 1 to N-1.
        total_segments (int): The total number of segments (N) in the sequence.
        segments_list (list): The list of processed segments, used for dynamic step calculation.
                              Each element is (s_block_dur_prg, s_color_info, s_pixels, s_type, s_json_dur_prg)

    Returns:
        int: The calculated base value (potentially >16 bits).
    """
    if not (1 <= target_index < total_segments):
         print(f"[WARN] _calculate_intermediate_block_index1_base called with invalid target_index {target_index} for {total_segments} segments.")
         return 0
    if not segments_list:
        print(f"[WARN] _calculate_intermediate_block_index1_base called with empty segments_list.")
        return 0


    base_value_n2_t1 = 370
    vertical_step = 19
    # horizontal_step = 300 # Replaced by dynamic calculation

    value_n_t1 = base_value_n2_t1 + (total_segments - 2) * vertical_step
    
    cumulative_horizontal_offset = 0
    # Iterate for segments 0 to target_index-2, which contribute to the offset for target_index
    for j in range(target_index - 1):
        if j >= len(segments_list):
            print(f"[WARN] _calculate_intermediate_block_index1_base: index j={j} out of bounds for segments_list (len={len(segments_list)})")
            break # or return error
        seg_j_block_dur = segments_list[j][0] # This is s_block_dur_prg
        seg_j_type = segments_list[j][3]
        
        if seg_j_type == 'solid':
            cumulative_horizontal_offset += 300 + (3 * seg_j_block_dur)
        elif seg_j_type == 'fade':
            cumulative_horizontal_offset += seg_j_block_dur
        else:
            print(f"[WARN] Unknown segment type '{seg_j_type}' at index {j} encountered in _calculate_intermediate_block_index1_base. Using default step 300.")
            cumulative_horizontal_offset += 300


    value_pair_full = value_n_t1 + cumulative_horizontal_offset
    return value_pair_full

def _calculate_last_block_index2_bases(total_segments, segments_list):
    """
    Calculates the base values for Index2 Part1 and Part2 fields in the *last*
    duration block. These values can exceed 16 bits.
    Part1: Lower 16 bits to +0x0B, Higher 16 bits to +0x0D.
    Part2: Lower 16 bits to +0x0F, Higher 16 bits to +0x11.

    Args:
        total_segments (int): The total number of segments.
        segments_list (list): The list of processed segments.

    Returns:
        tuple(int, int): (part1_full_value, part2_full_value).
    """
    cumulative_horizontal_offset_for_part1 = 0
    # Sum H_eff for j=0 to total_segments-2 (i.e., all segments *before* the last one)
    for j in range(total_segments - 1): # Corresponds to segments[0] through segments[total_segments-2]
        if j >= len(segments_list):
            print(f"[WARN] _calculate_last_block_index2_bases (part1): index j={j} out of bounds for segments_list (len={len(segments_list)})")
            break
        seg_j_block_dur = segments_list[j][0]
        seg_j_type = segments_list[j][3]
        if seg_j_type == 'solid':
            cumulative_horizontal_offset_for_part1 += 300 + (3 * seg_j_block_dur)
        elif seg_j_type == 'fade':
            cumulative_horizontal_offset_for_part1 += seg_j_block_dur
        else:
            print(f"[WARN] Unknown segment type '{seg_j_type}' at index {j} encountered in _calculate_last_block_index2_bases (part1). Using default step 300.")
            cumulative_horizontal_offset_for_part1 += 300
            
    part1_full = 304 + cumulative_horizontal_offset_for_part1

    part2_full_base = NOMINAL_BASE_FOR_HEADER_FIELDS
    if segments_list and total_segments > 0 and segments_list[0][3] == 'solid':
        part2_full_base = segments_list[0][0] # Use duration of the first segment if it's solid
    
    part2_full = part2_full_base * total_segments
    return part1_full, part2_full

def split_long_segments(segments, max_duration=65535):
    """
    Split segments with durations *in PRG time units* exceeding max_duration (65535 for <H).
    This function should ONLY operate on 'solid' type segments based on their s_block_dur_prg.
    Fade segments (N=1 full or embedded) are NOT split by this function.
    Ensures returned segments are 5-element tuples: (duration, color_data, pixels, segment_type, json_dur_original_unsplit)
    """
    print(f"[SPLIT] Checking for segments exceeding maximum duration ({max_duration} PRG time units)...")
    new_segments = []
    split_occurred = False
    original_segment_count = len(segments)

    if original_segment_count == 0:
        return []

    for idx, segment_tuple in enumerate(segments):
        if len(segment_tuple) != 5:
            print(f"[ERROR] Segment {idx} in split_long_segments has unexpected format (length {len(segment_tuple)} instead of 5). Skipping.")
            # Or raise an error: raise ValueError(f"Segment {idx} has unexpected format")
            continue
        
        duration_prg_units, color_data, pixels, segment_type, original_json_dur = segment_tuple # original_json_dur is from the unsplit segment
        
        # Fade segments are NOT split by this function
        # The N=1 full fade has its own 65535 limit check. Embedded fades are always 100.
        if segment_type == 'fade':
            new_segments.append(segment_tuple) # Keep as 5-element tuple
            continue
            
        if duration_prg_units <= max_duration:
            new_segments.append(segment_tuple) # Keep as 5-element tuple
            continue

        split_occurred = True
        print(f"[SPLIT] WARNING: Segment {idx} (Color {color_data}, Type {segment_type}) has PRG duration {duration_prg_units} PRG units which exceeds {max_duration}. Splitting.")

        num_full_segments = duration_prg_units // max_duration
        remainder_duration = duration_prg_units % max_duration

        for i in range(num_full_segments):
            # Each split part retains the original_json_dur of the segment it came from.
            # If individual split json_dur is needed, this would need adjustment.
            new_segments.append((max_duration, color_data, pixels, segment_type, original_json_dur)) # 5-element tuple
            print(f"[SPLIT]  - Added sub-segment {i+1}/{num_full_segments + (1 if remainder_duration > 0 else 0)} with PRG duration {max_duration} PRG units")

        if remainder_duration > 0:
            new_segments.append((remainder_duration, color_data, pixels, segment_type, original_json_dur)) # 5-element tuple
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
    color_format = data.get('color_format', 'rgb')  # Default to RGB if not specified

    # Validate types
    if not isinstance(default_pixels, int) or not (1 <= default_pixels <= 4):
        print(f"[ERROR] Invalid 'default_pixels': {default_pixels}. Must be int 1-4.")
        sys.exit(1)
    if not isinstance(json_refresh_rate, int) or json_refresh_rate <= 0:
        print(f"[ERROR] Invalid 'refresh_rate' in JSON: {json_refresh_rate}. Must be positive int.")
        sys.exit(1)
    if end_time_json_units is not None and not isinstance(end_time_json_units, (int, float)):
        print(f"[ERROR] Invalid 'end_time' in JSON: {end_time_json_units}. Must be a number (JSON time units).")
        sys.exit(1)

    time_unit_scaling_factor = TARGET_OUTPUT_PRG_REFRESH_RATE / json_refresh_rate

    print(f"[INIT] Config: DefaultPixels={default_pixels}, ColorFormat={color_format}")
    print(f"[INIT] Input JSON: RefreshRate={json_refresh_rate}Hz, EndTime={end_time_json_units} JSON_units (if specified)")
    print(f"[INIT] Time Unit Scaling Factor (Target_PRG_units / JSON_unit): {time_unit_scaling_factor:.4f}")

    if 'sequence' not in data or not isinstance(data['sequence'], dict) or not data['sequence']:
        print("[ERROR] JSON 'sequence' is missing, not a dictionary, or empty.")
        sys.exit(1)

    try:
        sequence_items_json_units = sorted([(round(float(t)), v) for t, v in data['sequence'].items()], key=lambda x: x[0])
    except ValueError:
        print("[ERROR] Sequence keys must be valid numbers representing JSON time units.")
        sys.exit(1)

    print(f"[INIT] Sorted sequence timestamps (JSON units, rounded): {[t for t, _ in sequence_items_json_units]}")

    print("\n[SEGMENT_CALC] Processing sequence segments (times will be scaled to PRG units)...")
    parsed_segments = []
    if not sequence_items_json_units:
         print("[ERROR] No segments found in sequence after sorting.")
         sys.exit(1)

    # Segment Parsing and Mode Detection
    for idx, (time_json_units, entry) in enumerate(sequence_items_json_units):
        if not isinstance(entry, dict):
            print(f"[ERROR] Entry for JSON time {time_json_units} units is not a dictionary.")
            sys.exit(1)

        start_color = entry.get('start_color')
        end_color = entry.get('end_color')
        color = entry.get('color')
        
        segment_type = None
        color_data = None

        # If an entry has start_color and end_color, mark it as type='fade'. Store start_rgb and end_rgb.
        if start_color is not None and end_color is not None:
            segment_type = 'fade'
            if not isinstance(start_color, list) or len(start_color) != 3:
                print(f"[ERROR] Segment at JSON time {time_json_units} units has invalid start_color format: {start_color}. Expected [R, G, B] or [H, S, V].")
                sys.exit(1)
            if not isinstance(end_color, list) or len(end_color) != 3:
                print(f"[ERROR] Segment at JSON time {time_json_units} units has invalid end_color format: {end_color}. Expected [R, G, B] or [H, S, V].")
                sys.exit(1)
            try:
                if color_format.lower() == 'hsv':
                    start_rgb = hsv_to_rgb(start_color[0], start_color[1], start_color[2])
                    end_rgb = hsv_to_rgb(end_color[0], end_color[1], end_color[2])
                else:
                    start_rgb = tuple(int(c) for c in start_color)
                    end_rgb = tuple(int(c) for c in end_color)
                    for c_val in start_rgb + end_rgb:
                        if not (0 <= c_val <= 255): raise ValueError("RGB values must be 0-255")
                color_data = (start_rgb, end_rgb)
            except (ValueError, TypeError) as e:
                print(f"[ERROR] Invalid color values in fade segment at JSON time {time_json_units}: start={start_color}, end={end_color}. {e}")
                sys.exit(1)
                
        # Otherwise, mark as type='solid'. Store color_rgb.
        elif color is not None:
            segment_type = 'solid'
            if not isinstance(color, list) or len(color) != 3:
                print(f"[ERROR] Segment at JSON time {time_json_units} units has invalid color format: {color}. Expected [R, G, B] or [H, S, V].")
                sys.exit(1)
            try:
                if color_format.lower() == 'hsv':
                    color_data = hsv_to_rgb(color[0], color[1], color[2])
                else:
                    color_data = tuple(int(c) for c in color)
                    for c_val in color_data:
                        if not (0 <= c_val <= 255): raise ValueError("RGB values must be 0-255")
            except (ValueError, TypeError) as e:
                print(f"[ERROR] Invalid color value in segment at JSON time {time_json_units}: {color}. {e}")
                sys.exit(1)
        else:
            print(f"[ERROR] Segment at JSON time {time_json_units} units is missing both 'color' and 'start_color'/'end_color'.")
            sys.exit(1)

        pixels = entry.get('pixels', default_pixels)
        if not isinstance(pixels, int) or not (1 <= pixels <= 4):
             print(f"[WARNING] Segment at JSON time {time_json_units} units has invalid pixels value ({pixels}). Using default: {default_pixels}.")
             pixels = default_pixels

        current_segment_prg_start_time = round(time_json_units * time_unit_scaling_factor)
        next_segment_prg_start_time = 0
        if idx + 1 < len(sequence_items_json_units):
            next_segment_start_json_units = sequence_items_json_units[idx + 1][0]
            next_segment_prg_start_time = round(next_segment_start_json_units * time_unit_scaling_factor)
        elif end_time_json_units is not None:
            rounded_end_time_json_units = round(float(end_time_json_units))
            if rounded_end_time_json_units < time_json_units:
                 print(f"[ERROR] JSON 'end_time' ({rounded_end_time_json_units} JSON units) is earlier than the start time ({time_json_units} JSON units) of the last segment.")
                 sys.exit(1)
            next_segment_prg_start_time = round(rounded_end_time_json_units * time_unit_scaling_factor)
        else:
            default_duration_prg_units = TARGET_OUTPUT_PRG_REFRESH_RATE
            print(f"[WARNING] 'end_time' not specified in JSON. Assigning default duration ({default_duration_prg_units} PRG units = 1s) to the last segment.")
            next_segment_prg_start_time = current_segment_prg_start_time + default_duration_prg_units

        json_duration_prg = next_segment_prg_start_time - current_segment_prg_start_time
        if json_duration_prg <= 0:
             print(f"[WARNING] Segment {idx} (JSON time {time_json_units} units) has non-positive PRG duration ({json_duration_prg} PRG units after scaling/rounding). Skipping.")
             continue

        print(f"[SEGMENT_CALC] - Seg {idx}: JSON_Time={time_json_units} units -> PRG_Start_Time={current_segment_prg_start_time} PRG_units.")
        print(f"                 Next PRG_Start_Time={next_segment_prg_start_time} -> Duration={json_duration_prg} PRG_units, Type={segment_type}, Pixels={pixels}")
        
        parsed_segments.append({
            'type': segment_type,
            'json_duration_prg': json_duration_prg,
            'color_data': color_data,
            'pixels': pixels
        })

    if not parsed_segments:
        print("[ERROR] No valid segments could be calculated (check durations and times after scaling).")
        sys.exit(1)

    # After parsing, determine: is_n1_full_program_fade = (len(parsed_segments) == 1 and parsed_segments[0]['type'] == 'fade')
    is_n1_full_program_fade = (len(parsed_segments) == 1 and parsed_segments[0]['type'] == 'fade')
    
    # Segment List Finalization (segments)
    segments = []
    
    for p_seg in parsed_segments:
        s_type = p_seg['type']
        s_json_dur_prg = p_seg['json_duration_prg'] # calculated_duration_in_prg_units_from_json_times_and_scaling
        s_color_info = p_seg['color_data'] # either (r,g,b) or ((r1,g1,b1), (r2,g2,b2))
        s_pixels = p_seg['pixels']
        
        if is_n1_full_program_fade:
            s_block_dur_prg = s_json_dur_prg
            # Crucial Check: If s_block_dur_prg > 65535, print error and exit (or cap and warn).
            if s_block_dur_prg > 65535:
                print(f"[ERROR] N=1 Full Program Fade duration {s_block_dur_prg} PRG units exceeds 65535. Max is 655.35s at 100Hz.")
                sys.exit(1)
            if s_block_dur_prg <= 0:
                print(f"[ERROR] N=1 Full Program Fade duration {s_block_dur_prg} PRG units must be positive.")
                sys.exit(1)
        else:  # mixed sequence or N=1 solid - s_block_dur_prg is the JSON duration
            s_block_dur_prg = s_json_dur_prg
            # Removed specific handling for embedded fade's s_block_dur_prg to be 100.
            # It will now be its s_json_dur_prg.
            # The number of RGB steps for an embedded fade is handled separately during RGB writing.
            
        # Add (s_block_dur_prg, s_color_info, s_pixels, s_type, s_json_dur_prg) to segments
        segments.append((s_block_dur_prg, s_color_info, s_pixels, s_type, s_json_dur_prg))

    if not segments:
        print("[ERROR] No valid segments could be created.")
        sys.exit(1)

    segments = split_long_segments(segments) 
    segment_count = len(segments)

    if segment_count == 0:
         print("[ERROR] No segments remaining after processing/splitting.")
         sys.exit(1)

    print(f"\n[SUMMARY] Total PRG segments to write: {segment_count}")

    # Header Value Calculation
    # After segments are finalized and split_long_segments may have run
    is_n1_full_program_fade = (segment_count == 1 and segments[0][3] == 'fade')

    if is_n1_full_program_fade:
        # N=1 TRUE FADE MODE
        s_block_dur, _, _, _, _ = segments[0]
        
        pointer1 = 21
        header_field_16_calculated_val = 1  # Always 1 for fade segments (regardless of duration)
        header_field_18_dynamic_val = s_block_dur   # Actual duration
        rgb_start_pointer = HEADER_SIZE + 1 * DURATION_BLOCK_SIZE # 51
        header_field_1E_calculated_val = 0
    else:
        # SOLID N=1 or MIXED SEQUENCE (N>1, may include embedded fades)
        first_seg_block_dur = segments[0][0]
        first_seg_type = segments[0][3]  # Get the type of the first segment
        
        pointer1 = 21 + 19 * (segment_count - 1) if segment_count > 0 else 0
        
        # Header field 0x16: Always 1 for fade segments, floor(duration/100) for solid segments
        if first_seg_type == 'fade':
            header_field_16_calculated_val = 1  # Always 1 for fade segments
        else:
            header_field_16_calculated_val = math.floor(first_seg_block_dur / NOMINAL_BASE_FOR_HEADER_FIELDS)
            
        header_field_18_dynamic_val = NOMINAL_BASE_FOR_HEADER_FIELDS # Always 100
        rgb_start_pointer = HEADER_SIZE + segment_count * DURATION_BLOCK_SIZE
        
        val_0x1E_dec = 0 # Standard 0x1E calculation
        nominal_base = NOMINAL_BASE_FOR_HEADER_FIELDS
        if segment_count == 1: # Must be N=1 Solid here
            if first_seg_block_dur == nominal_base: val_0x1E_dec = 0
            elif first_seg_block_dur % nominal_base == 0:
                if first_seg_block_dur <= 400: val_0x1E_dec = 0
                else: val_0x1E_dec = first_seg_block_dur
            else: val_0x1E_dec = first_seg_block_dur % nominal_base
        elif segment_count > 1:
            if first_seg_block_dur == 1000: val_0x1E_dec = 1000
            elif first_seg_block_dur % nominal_base == 0: val_0x1E_dec = 0
            else: val_0x1E_dec = first_seg_block_dur % nominal_base
        header_field_1E_calculated_val = val_0x1E_dec & 0xFFFF

    print("\n[HEADER_CALC] Calculated Header Values:")
    print(f"[HEADER_CALC] - Target PRG Refresh Rate (0x0C, <H): {TARGET_OUTPUT_PRG_REFRESH_RATE} ({bytes_to_hex(TARGET_OUTPUT_PRG_REFRESH_RATE)})")
    print(f"[HEADER_CALC] - Pointer1 (0x10, <I): {pointer1} ({bytes_to_hex(pointer1)})")
    print(f"[HEADER_CALC] - SegmentCount (0x14, <H): {segment_count} ({bytes_to_hex(segment_count)})")
    print(f"[HEADER_CALC] - Field 0x16 (<H) Calculated: {header_field_16_calculated_val} ({bytes_to_hex(header_field_16_calculated_val)})")
    print(f"[HEADER_CALC] - Field 0x18 (<H) Dynamic: {header_field_18_dynamic_val} ({bytes_to_hex(header_field_18_dynamic_val)})")
    print(f"[HEADER_CALC] - RGB Start Pointer (0x1A, <H): {rgb_start_pointer} ({bytes_to_hex(rgb_start_pointer)})")
    print(f"[HEADER_CALC] - Field 0x1E (<H) Calculated: {header_field_1E_calculated_val} ({bytes_to_hex(header_field_1E_calculated_val)})")
    print(f"[HEADER_CALC] - Mode: {'N=1 True Fade' if is_n1_full_program_fade else 'Standard (Solid/Mixed)'}")

    print(f"\n[WRITE] Writing PRG file: {output_prg}")
    try:
        with open(output_prg, 'wb') as f:
            current_offset = 0

            print("[WRITE] Writing Header...")
            f.write(FILE_SIGNATURE); current_offset += len(FILE_SIGNATURE)
            f.write(struct.pack('>H', default_pixels)); current_offset += 2
            f.write(HEADER_CONST_0A); current_offset += len(HEADER_CONST_0A)
            f.write(struct.pack('<H', TARGET_OUTPUT_PRG_REFRESH_RATE)); current_offset += 2
            f.write(HEADER_CONST_PI); current_offset += len(HEADER_CONST_PI)
            f.write(struct.pack('<I', pointer1)); current_offset += 4
            f.write(struct.pack('<H', segment_count)); current_offset += 2
            f.write(struct.pack('<H', header_field_16_calculated_val)); current_offset += 2
            f.write(struct.pack('<H', header_field_18_dynamic_val)); current_offset += 2
            f.write(struct.pack('<H', rgb_start_pointer)); current_offset += 2
            f.write(HEADER_CONST_1C); current_offset += len(HEADER_CONST_1C)
            f.write(struct.pack('<H', header_field_1E_calculated_val)); current_offset += 2

            if current_offset != HEADER_SIZE:
                print(f"[ERROR] Header size mismatch! Expected {HEADER_SIZE}, wrote {current_offset}. Aborting.")
                sys.exit(1)
            print(f"[WRITE] Header complete ({current_offset} bytes).")

            print(f"\n[WRITE] Writing {segment_count} Duration Blocks...")
            # segments contains: (block_duration_prg, color_data, pixels, segment_type, json_duration_prg_original)
            # The first element is block_duration_prg, third is pixels.
            for idx, (block_duration_prg_current_seg, _, pixels_for_block, _, _) in enumerate(segments): # MODIFIED: Unpack 5 elements
                block_start_offset = current_offset
                
                try:
                    if idx < segment_count - 1:
                        next_block_duration_prg_units = segments[idx + 1][0] # Get block_duration of next segment
                        
                        index1_full_base_value = _calculate_intermediate_block_index1_base(idx + 1, segment_count, segments)
                        index1_value_at_0D = index1_full_base_value & 0xFFFF
                        index1_carry_at_0F = (index1_full_base_value >> 16) & 0xFFFF

                        # field_09 logic modification
                        next_seg_actual_block_dur = segments[idx+1][0] # s_block_dur_prg of next segment
                        next_seg_type = segments[idx+1][3]
                        next_seg_json_dur_original = segments[idx+1][4] # s_json_dur_prg of next segment

                        if next_seg_type == 'fade':
                            field_09_part1 = 1
                            field_09_part2 = next_seg_json_dur_original # Use its original JSON duration (scaled to PRG units)
                        else: # solid
                            field_09_part1 = math.floor(next_seg_actual_block_dur / NOMINAL_BASE_FOR_HEADER_FIELDS)
                            field_09_part2 = NOMINAL_BASE_FOR_HEADER_FIELDS
                        field_09_bytes = struct.pack('<H', field_09_part1) + struct.pack('<H', field_09_part2)
                        
                        field_11_val = 0
                        dur_k = block_duration_prg_current_seg # current block_duration
                        dur_k_plus_1 = next_block_duration_prg_units # next block_duration

                        # This logic for field_11_val seems highly specific and based on observed patterns.
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
                        
                        f.write(struct.pack('<H', pixels_for_block))
                        f.write(BLOCK_CONST_02)
                        f.write(struct.pack('<H', block_duration_prg_current_seg)) 
                        f.write(BLOCK_CONST_07)
                        f.write(field_09_bytes)
                        f.write(struct.pack('<H', index1_value_at_0D))
                        f.write(struct.pack('<H', index1_carry_at_0F))
                        f.write(struct.pack('<H', field_11_val))
                        current_offset += DURATION_BLOCK_SIZE
                    else: # Last block
                        s_block_dur, _, pixels, segment_type, _ = segments[idx]

                        if segment_type == 'fade' and segment_count == 1: # is_n1_full_program_fade
                            # N=1 TRUE FADE MODE - Special Index2 calculation
                            dur_val = s_block_dur
                            index2_part1_full = (3 * dur_val) + 4 # For N=1 True Fade, s_block_dur is dur_val
                            index2_part2_full = dur_val         # For N=1 True Fade, s_block_dur is dur_val
                        else:
                            # Standard N=1 Solid or N>1 Last Block
                            index2_part1_full, index2_part2_full = _calculate_last_block_index2_bases(segment_count, segments)
                        
                        index2_part1_at_0B = index2_part1_full & 0xFFFF
                        index2_part1_carry_at_0D = (index2_part1_full >> 16) & 0xFFFF
                        index2_part2_at_0F = index2_part2_full & 0xFFFF
                        index2_part2_carry_at_11 = (index2_part2_full >> 16) & 0xFFFF

                        f.write(struct.pack('<H', pixels_for_block))
                        f.write(BLOCK_CONST_02)
                        f.write(struct.pack('<H', block_duration_prg_current_seg)) 
                        f.write(BLOCK_CONST_07)
                        f.write(LAST_BLOCK_CONST_09)
                        f.write(struct.pack('<H', index2_part1_at_0B))
                        f.write(struct.pack('<H', index2_part1_carry_at_0D))
                        f.write(struct.pack('<H', index2_part2_at_0F))
                        f.write(struct.pack('<H', index2_part2_carry_at_11))
                        current_offset += DURATION_BLOCK_SIZE
                except struct.error as e:
                     print(f"[ERROR] Failed to pack data for duration block {idx}: {e}. Duration value likely exceeds 65535.")
                     print(f"        Duration_PRG_Block={block_duration_prg_current_seg}, NextDuration_PRG_Block={next_block_duration_prg_units if idx < segment_count - 1 else 'N/A'}")
                     sys.exit(1)

                if current_offset - block_start_offset != DURATION_BLOCK_SIZE:
                     print(f"[ERROR] Duration block {idx} size mismatch! Expected {DURATION_BLOCK_SIZE}, wrote {current_offset - block_start_offset}. Aborting.")
                     sys.exit(1)

            print(f"[WRITE] Duration blocks complete. Current offset: 0x{current_offset:04X} (Expected RGB start: 0x{rgb_start_pointer:04X})")
            if current_offset != rgb_start_pointer:
                 print(f"[ERROR] Offset mismatch before RGB data! Expected 0x{rgb_start_pointer:04X}, got 0x{current_offset:04X}. Aborting.")
                 sys.exit(1)

            print(f"\n[WRITE] Writing RGB Data (Starting @0x{current_offset:04X})...")
            total_rgb_bytes_written = 0
            
            # RGB Data Writing
            for idx, (s_block_dur, color_info, pixels, segment_type, s_json_dur) in enumerate(segments):
                if segment_type == 'fade':
                    start_c_rgb, end_c_rgb = color_info # Assumed to be RGB tuples already

                    # For all fades (N=1 True Fade or Embedded Fade),
                    # the number of interpolation steps now matches their s_block_dur
                    # (which is their s_json_dur_prg).
                    num_steps_for_interpolation = s_block_dur
                    print(f"[WRITE_FADE] Segment {idx} ({'N=1 True Fade' if is_n1_full_program_fade else 'Embedded Fade'}): Writing {num_steps_for_interpolation} interpolated RGB steps (Block dur {s_block_dur} PRG units, JSON intended {s_json_dur} PRG units).")
                    
                    if num_steps_for_interpolation <= 0:
                        print(f"[WARN_FADE] Segment {idx} has {num_steps_for_interpolation} steps, skipping RGB write for this fade.")
                        continue

                    for i in range(num_steps_for_interpolation):
                        if num_steps_for_interpolation == 1:
                            r, g, b = start_c_rgb
                        else:
                            r = int(round(start_c_rgb[0] + i * (end_c_rgb[0] - start_c_rgb[0]) / (num_steps_for_interpolation - 1.0)))
                            g = int(round(start_c_rgb[1] + i * (end_c_rgb[1] - start_c_rgb[1]) / (num_steps_for_interpolation - 1.0)))
                            b = int(round(start_c_rgb[2] + i * (end_c_rgb[2] - start_c_rgb[2]) / (num_steps_for_interpolation - 1.0)))
                        # Clamp r,g,b
                        f.write(struct.pack('BBB', max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))))
                        current_offset += 3
                        total_rgb_bytes_written += 3
                elif segment_type == 'solid':
                    # Existing logic: write color_info (r,g,b) RGB_TRIPLE_COUNT (100) times
                    r_solid, g_solid, b_solid = color_info
                    rgb_bytes_solid = struct.pack('BBB', r_solid, g_solid, b_solid)
                    f.write(rgb_bytes_solid * RGB_TRIPLE_COUNT)
                    bytes_written_this_segment = RGB_TRIPLE_COUNT * 3
                    current_offset += bytes_written_this_segment
                    total_rgb_bytes_written += bytes_written_this_segment
            print(f"[WRITE] RGB data complete. Total RGB bytes: {total_rgb_bytes_written}. Current offset: 0x{current_offset:04X}")

            print("\n[WRITE] Writing Footer...")
            f.write(FOOTER)
            current_offset += len(FOOTER)
            print(f"[WRITE] Footer complete. Final offset: 0x{current_offset:04X}")

    except IOError as e:
        print(f"[ERROR] Failed to write file {output_prg}: {e}")
        sys.exit(1)

    # File Size Verification
    expected_rgb_data_size = 0
    is_n1_full_program_fade = (segment_count == 1 and segments[0][3] == 'fade')

    if is_n1_full_program_fade:
        expected_rgb_data_size = segments[0][0] * 3 # s_block_dur * 3 (number of steps * 3 bytes/step)
    else:
        for s_block_dur, _, _, segment_type, _ in segments:
            if segment_type == 'fade': # Embedded fade
                expected_rgb_data_size += 100 * 3 # 100 steps * 3 bytes/step
            else: # Solid
                expected_rgb_data_size += RGB_TRIPLE_COUNT * 3 # 100 repeats * 3 bytes/color
    
    expected_size = HEADER_SIZE + (segment_count * DURATION_BLOCK_SIZE) + expected_rgb_data_size + len(FOOTER)
    
    final_size = os.path.getsize(output_prg)
    print(f"\n[VERIFY] Final file size: {final_size} bytes.")
    print(f"[VERIFY] Expected size calculation: {expected_size} bytes.")
    print(f"[VERIFY] RGB data size: {expected_rgb_data_size} bytes.")
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