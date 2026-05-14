#!/usr/bin/env python3
"""Fix beat cycling from 276s onwards.
Collect all beat timestamps, sort them, reassign in B1→B2→B3 cycle,
then rebuild each ball's timeline with the sandwich pattern:
white → orange(0.25s) → cyan(0.25s beat) → orange(0.25s) → white
"""

import json
import copy

INPUT_FILE = 'sequence_projects/fast_car_ground_truth/fast_car_ground_truth3.smproj'
CUTOFF = 276.0
WHITE = [255, 255, 255]
CYAN = [0, 255, 255]
ORANGE = [255, 165, 0]
ORANGE_DUR = 0.25
BEAT_DUR = 0.25

with open(INPUT_FILE, 'r') as f:
    data = json.load(f)

# Step 1: Collect ALL beat timestamps from all balls (cyan segments >= CUTOFF)
all_beat_times = set()
for tl in data['timelines']:
    for s in tl['segments']:
        if s['startTime'] >= CUTOFF and s['color'] == CYAN:
            all_beat_times.add(round(s['startTime'], 4))

all_beat_times = sorted(all_beat_times)
print(f"Total unique beat times from 276s+: {len(all_beat_times)}")

# Step 2: Assign beats in B1→B2→B3 cycle
ball_names = ['Ball 1', 'Ball 2', 'Ball 3']
ball_beats = {name: [] for name in ball_names}

for i, bt in enumerate(all_beat_times):
    ball_idx = i % 3
    ball_beats[ball_names[ball_idx]].append(bt)

for name in ball_names:
    print(f"  {name}: {len(ball_beats[name])} beats")

# Step 3: Rebuild each ball's timeline
for tl in data['timelines']:
    # Keep pre-cutoff segments unchanged
    pre_cutoff = [copy.deepcopy(s) for s in tl['segments'] if s['endTime'] <= CUTOFF]
    
    end_time = max(s['endTime'] for s in tl['segments'])
    beats = ball_beats[tl['name']]
    
    # Build beat zones with sandwich pattern
    beat_zones = []
    for bt in beats:
        pre_start = round(bt - ORANGE_DUR, 4)
        beat_end = round(bt + BEAT_DUR, 4)
        post_end = round(beat_end + ORANGE_DUR, 4)
        beat_zones.append((pre_start, bt, ORANGE))
        beat_zones.append((bt, beat_end, CYAN))
        beat_zones.append((beat_end, post_end, ORANGE))
    
    beat_zones.sort(key=lambda x: x[0])
    
    # Merge overlapping/adjacent same-color zones
    merged = []
    for zone in beat_zones:
        if not merged:
            merged.append(list(zone))
        else:
            last = merged[-1]
            if zone[2] == last[2] and round(zone[0], 4) <= round(last[1], 4):
                last[1] = max(last[1], zone[1])
            elif round(zone[0], 4) < round(last[1], 4):
                # Different color overlap - trim previous
                last[1] = zone[0]
                merged.append(list(zone))
            else:
                merged.append(list(zone))
    
    # Build full timeline from CUTOFF
    result = []
    current = CUTOFF
    bz_idx = 0
    
    while current < end_time:
        while bz_idx < len(merged) and round(merged[bz_idx][1], 4) <= round(current, 4):
            bz_idx += 1
        
        if bz_idx < len(merged):
            bz_start, bz_end, bz_color = merged[bz_idx]
            
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
    
    # Remove zero-duration segments
    result = [s for s in result if round(s['endTime'] - s['startTime'], 4) > 0]
    
    tl['segments'] = pre_cutoff + result

# Save
with open(INPUT_FILE, 'w') as f:
    json.dump(data, f, indent=2)

# Verify
print("\nVerification - beat order from 276s:")
all_new_beats = []
for tl in data['timelines']:
    for s in tl['segments']:
        if s['startTime'] >= CUTOFF and s['color'] == CYAN:
            all_new_beats.append((s['startTime'], tl['name']))

all_new_beats.sort()
for i, (t, name) in enumerate(all_new_beats[:30]):
    short = 'B1' if name == 'Ball 1' else 'B2' if name == 'Ball 2' else 'B3'
    print(f"  {i}: {t:.2f}s - {short}")

# Check cycling
print("\nCycling check:")
for i in range(1, len(all_new_beats)):
    prev_ball = all_new_beats[i-1][1]
    curr_ball = all_new_beats[i][1]
    expected_order = {'Ball 1': 'Ball 2', 'Ball 2': 'Ball 3', 'Ball 3': 'Ball 1'}
    if prev_ball != 'Ball 3' and curr_ball != expected_order.get(prev_ball, ''):
        if not (prev_ball == 'Ball 3' and curr_ball == 'Ball 1'):
            pass  # B3->B1 is fine
    if prev_ball == 'Ball 1' and curr_ball != 'Ball 2':
        print(f"  ERROR at {all_new_beats[i][0]:.2f}: expected B2 after B1, got {curr_ball}")
    elif prev_ball == 'Ball 2' and curr_ball != 'Ball 3':
        print(f"  ERROR at {all_new_beats[i][0]:.2f}: expected B3 after B2, got {curr_ball}")
    elif prev_ball == 'Ball 3' and curr_ball != 'Ball 1':
        print(f"  ERROR at {all_new_beats[i][0]:.2f}: expected B1 after B3, got {curr_ball}")

# Summary
for tl in data['timelines']:
    post = [s for s in tl['segments'] if s['startTime'] >= CUTOFF]
    beats = [s for s in post if s['color'] == CYAN]
    oranges = [s for s in post if s['color'] == ORANGE]
    whites = [s for s in post if s['color'] == WHITE]
    print(f"{tl['name']}: {len(post)} segments ({len(beats)} cyan, {len(oranges)} orange, {len(whites)} white)")

print("\nDone!")
