"""Generate JSON for each of the 12 reference PRG patterns, run our generator,
and verify header + duration blocks + footer are byte-identical."""
import json, subprocess, struct, os, sys
from pathlib import Path

REF_DIR = Path("/home/twain/Documents/4px_ball/LighTriX_Editor/Windows/editor_simple_red_green_fade")

# Each entry: (ref_filename, segments_in_seconds, end_seconds, default_pixels)
# segments_in_seconds: list of dicts {start, type, color/start_color/end_color}
# We'll synthesize the JSON in 100Hz tick form (refresh_rate=100, times in ticks).
REFS = [
    # Skip 1Hz file - sequence_maker pipeline always uses 100Hz
    ("editor_simple_red_green_100rf.prg",
     [("F", 1000, (255,0,0), (0,255,0)),
      ("S", 6000, (0,255,0), None)]),
    ("red-cyan-green.prg",
     [("F", 1000, (255,0,0), (0,255,255)),
      ("F", 1000, (0,255,255), (0,255,0)),
      ("S", 6000, (0,255,0), None)]),
    ("tier1_A_solid_fade_solid.prg",
     [("S", 600,  (255,0,0), None),
      ("F", 1000, (255,0,0), (0,255,0)),
      ("S", 600,  (0,255,0), None)]),
    ("tier1_B_fade_solid_fade_solid.prg",
     [("F", 1000, (255,0,0), (0,255,255)),
      ("S", 600,  (0,255,255), None),
      ("F", 1000, (0,255,255), (0,255,0)),
      ("S", 600,  (0,255,0), None)]),
    ("tier1_C_solid_fade_fade_solid.prg",
     [("S", 600,  (255,0,0), None),
      ("F", 1000, (255,0,0), (0,255,255)),
      ("F", 1000, (0,255,255), (0,255,0)),
      ("S", 600,  (0,255,0), None)]),
    ("Tier2_D_fade_solid_different_lengths.prg",
     [("F", 500, (255,0,0), (0,255,0)),
      ("S", 800, (0,255,0), None)]),
    ("Tier2_E_fade_solid_different_lengths_short solid.prg",
     [("F", 1000, (255,0,0), (0,255,0)),
      ("S", 50,   (0,255,0), None)]),
    ("Tier2_F_solid_fade_no_trailing.prg",
     [("S", 600,  (255,0,0), None),
      ("F", 1000, (255,0,0), (0,255,0))]),
    ("Tier2_G_rapid_fade.prg",
     [("F", 100, (255,0,0), (0,255,0))]),
    ("Tier2_H_350ticks.prg",
     [("S", 350, (255,0,0), None)]),
    ("Tier3_J_three_fades_and_solid.prg",
     [("F", 100, (0,255,255), (0,255,0)),  # cyan->green
      ("F", 100, (0,255,0), (255,255,0)),
      ("F", 100, (255,255,0), (255,0,0)),
      ("S", 100, (255,0,0), None)]),
    ("Tier3_K_fade_solid_fade_fade_solid_fade_irregular_times.prg",
     [("F", 100, (0,255,255), (0,255,0)),
      ("S", 1000, (0,255,0), None),
      ("F", 100, (0,255,0), (255,255,0)),
      ("F", 1007, (255,255,0), (255,0,0)),
      ("S", 455, (255,0,0), None),
      ("F", 480, (255,0,0), (0,0,255))]),
]

HEADER_SIZE = 32
DUR_BLOCK_SIZE = 19


def build_json(segs):
    """Build a sequence_maker-compatible JSON at refresh_rate=100, ticks units."""
    seq = {}
    t = 0
    for (typ, dur, c1, c2) in segs:
        if typ == 'F':
            seq[str(t)] = {
                "pixels": 4,
                "start_color": list(c1),
                "end_color": list(c2),
            }
        else:
            seq[str(t)] = {"pixels": 4, "color": list(c1)}
        t += dur
    end_time = t
    return {
        "default_pixels": 4,
        "color_format": "rgb",
        "refresh_rate": 100,
        "end_time": end_time,
        "sequence": seq,
    }


def cmp_files(name, segs):
    ref_path = REF_DIR / name
    j = build_json(segs)
    json_path = f"/tmp/ref_{name}.json"
    out_path = f"/tmp/our_{name}"
    with open(json_path, 'w') as fh:
        json.dump(j, fh)
    r = subprocess.run(["python3", "prg_generator.py", json_path, out_path],
                       capture_output=True, text=True, cwd="/home/twain/Projects/ltx_guru")
    if r.returncode != 0:
        return f"  FAIL: generator error: {r.stderr.splitlines()[-1] if r.stderr else 'unknown'}"

    a = open(out_path, 'rb').read()
    b = open(ref_path, 'rb').read()

    n = len(segs)
    hdr_dur_size = HEADER_SIZE + n * DUR_BLOCK_SIZE
    if len(a) < hdr_dur_size + 6 or len(b) < hdr_dur_size + 6:
        return f"  FAIL: file too small a={len(a)} b={len(b)}"

    hdr_match = a[:hdr_dur_size] == b[:hdr_dur_size]
    foot_match = a[-6:] == b[-6:]
    rgb_a = a[hdr_dur_size:-6]
    rgb_b = b[hdr_dur_size:-6]
    rgb_size_match = len(rgb_a) == len(rgb_b)
    rgb_diffs = sum(1 for x,y in zip(rgb_a, rgb_b) if x != y) if rgb_size_match else -1

    status = "PASS" if (hdr_match and foot_match and rgb_size_match) else "FAIL"
    line = f"  [{status}] {name}: hdr+dur={hdr_match} footer={foot_match} rgb_size={rgb_size_match} rgb_diffs={rgb_diffs}/{len(rgb_a)}"
    if not hdr_match:
        # Show first differing offset
        for i,(x,y) in enumerate(zip(a[:hdr_dur_size], b[:hdr_dur_size])):
            if x != y:
                line += f"\n    first hdr/dur diff @ offset {i} (0x{i:02X}): ours=0x{x:02X} ref=0x{y:02X}"
                break
    return line


print("=" * 70)
print("Verification against 11 official reference PRGs (100Hz only)")
print("=" * 70)
results = []
for name, segs in REFS:
    line = cmp_files(name, segs)
    results.append(line)
    print(line)

n_pass = sum(1 for r in results if "[PASS]" in r)
print(f"\n{n_pass}/{len(results)} byte-equivalent (header+duration+footer)")
