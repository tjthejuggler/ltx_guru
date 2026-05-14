#!/usr/bin/env python3
"""Recolor all 3 balls from 276s onwards:
Pattern: white → orange(0.25s) → cyan(0.25s beat) → orange(0.25s) → white
Merges overlapping orange zones when beats are close together.
"""

import json
import copy

INPUT_FILE = 'sequence_projects/fast_car_ground_truth/fast_car_ground_truth3.smproj'
CUTOFF = 276.0
WHITE = [255, 255, 255]
CYAN = [0, 255, 255]
ORANGE = [255, 165, 0]
ORANGE_DUR = 0.25

with open(INPUT_FILE, 'r') as f:
    data = json.load(f)

for timeline in data['timelines']:
    segments = timeline['segments']
    
    # Step 1: Find all cyan beat positions in post-cutoff region
    beat_starts = []
    for seg in segments:
        if seg['startTime'] >= CUTOFF and seg['color'] == CYAN:
            beat_starts.append(seg['startTime'])
    
    beat_starts.sort()
    print(f"{timeline['name']}: found {len(beat_starts)} beats")
    
    # Step 2: Keep only pre-cutoff segments
    pre_cutoff = [copy.deepcopy(s) for s in segments if s['endTime'] <= CUTOFF]
    
    # Step 3: Find end time
    end_time = max(s['endTime'] for s in segments)
    
    # Step 4: Build beat zones and merge overlapping ones
    beat_zones = []
    for bt in beat_starts:
        pre_start = round(bt - ORANGE_DUR, 4)
        beat_end = round(bt + 0.25, 4)
        post_end = round(beat_end + ORANGE_DUR, 4)
        beat_zones.append((pre_start, bt, ORANGE))
        beat_zones.append((bt, beat_end, CYAN))
        beat_zones.append((beat_end, post_end, ORANGE))
    
    beat_zones.sort(key=lambda x: x[0])
    
    # Merge overlapping/adjacent zones with same color
    merged_zones = []
    for zone in beat_zones:
        if not merged_zones:
            merged_zones.append(list(zone))
        else:
            last = merged_zones[-1]
            # If same color and overlapping or adjacent, merge
            if zone[2] == last[2] and round(zone[0], 4) <= round(last[1], 4):
                last[1] = max(last[1], zone[1])
            # If different color but overlapping, the later zone wins (trim previous)
            elif round(zone[0], 4) < round(last[1], 4):
                # Trim the previous zone to end where this one starts
                last[1] = zone[0]
                merged_zones.append(list(zone))
            else:
                merged_zones.append(list(zone))
    
    # Step 5: Build full timeline from CUTOFF to end
    result = []
    current = CUTOFF
    bz_idx = 0
    
    while current < end_time:
        # Skip zones that are entirely before current
        while bz_idx < len(merged_zones) and round(merged_zones[bz_idx][1], 4) <= round(current, 4):
            bz_idx += 1
        
        if bz_idx < len(merged_zones):
            bz_start, bz_end, bz_color = merged_zones[bz_idx]
            
            # If zone starts at or before current, use it from current
            if round(bz_start, 4) <= round(current, 4):
                actual_end = max(bz_end, current)
                result.append({
                    'startTime': current,
                    'endTime': actual_end,
                    'color': bz_color,
                    'pixels': 4,
                    'effects': [],
                    'segment_type': 'solid'
                })
                current = actual_end
                bz_idx += 1
            else:
                # Gap before this zone - fill with white
                result.append({
                    'startTime': current,
                    'endTime': bz_start,
                    'color': WHITE,
                    'pixels': 4,
                    'effects': [],
                    'segment_type': 'solid'
                })
                current = bz_start
        else:
            # No more zones, fill rest with white
            if current < end_time:
                result.append({
                    'startTime': current,
                    'endTime': end_time,
                    'color': WHITE,
                    'pixels': 4,
                    'effects': [],
                    'segment_type': 'solid'
                })
            current = end_time
    
    timeline['segments'] = pre_cutoff + result

# Save
with open(INPUT_FILE, 'w') as f:
    json.dump(data, f, indent=2)

# Print summary & verify
for timeline in data['timelines']:
    post = [s for s in timeline['segments'] if s['startTime'] >= CUTOFF]
    beats = [s for s in post if s['color'] == CYAN]
    oranges = [s for s in post if s['color'] == ORANGE]
    whites = [s for s in post if s['color'] == WHITE]
    other = [s for s in post if s['color'] not in [CYAN, ORANGE, WHITE]]
    print(f"{timeline['name']}: {len(post)} segments ({len(beats)} cyan, {len(oranges)} orange, {len(whites)} white, {len(other)} other)")
    
    # Verify contiguity
    for j in range(1, len(timeline['segments'])):
        prev = timeline['segments'][j-1]
        curr = timeline['segments'][j]
        if round(prev['endTime'], 4) != round(curr['startTime'], 4):
            print(f"  GAP/OVERLAP: {prev['endTime']} vs {curr['startTime']}")

print("\nDone!")
