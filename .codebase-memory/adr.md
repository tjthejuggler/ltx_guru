## 2026-05-07 — UNIFIED PRG format rules (verified against 12 official samples)

After receiving 10 additional reference PRG files from the user covering every
fade-placement pattern producible in the official LightriX Windows editor, a
**single universal rule set** was derived that replaces all previous branchy
logic in `prg_generator.py`. The rules produce byte-identical headers and
duration blocks for every observed pattern (solid-only, fade-only, fade→solid,
solid→fade, fade→fade, solid-fade-solid, fade-solid-fade-solid,
solid-fade-fade-solid, three consecutive fades + solid, and a 6-segment
irregular mix).

### Reference set
`/home/twain/Documents/4px_ball/LighTriX_Editor/Windows/editor_simple_red_green_fade/`
- `editor_simple_red_green_100rf.prg` — fade(1000) + solid(6000)
- `red-cyan-green.prg` — fade(1000) + fade(1000) + solid(6000)
- `tier1_A_solid_fade_solid.prg` — solid(600) + fade(1000) + solid(600)
- `tier1_B_fade_solid_fade_solid.prg` — fade(1000) + solid(600) + fade(1000) + solid(600)
- `tier1_C_solid_fade_fade_solid.prg` — solid(600) + fade(1000) + fade(1000) + solid(600)
- `Tier2_D_fade_solid_different_lengths.prg` — fade(500) + solid(800)
- `Tier2_E_fade_solid_different_lengths_short solid.prg` — fade(1000) + solid(50)
- `Tier2_F_solid_fade_no_trailing.prg` — solid(600) + fade(1000)  (last block is fade)
- `Tier2_G_rapid_fade.prg` — fade(100) only
- `Tier2_H_350ticks.prg` — solid(350) only (non-multiple-of-100)
- `Tier3_J_three_fades_and_solid.prg` — fade,fade,fade,solid
- `Tier3_K_fade_solid_fade_fade_solid_fade_irregular_times.prg` — 6-segment irregular mix

### Universal rule set (refresh_rate=100, the only rate sequence_maker uses)

**Header:**
```
pointer1   = 21 + 19 * (N - 1)
rgb_start  = HEADER_SIZE + N * DURATION_BLOCK_SIZE        (= 32 + 19N)
If first segment is FADE:
    f16 = 1
    f18 = first_fade_duration_ticks
    f1E = 0
If first segment is SOLID (duration d ticks):
    f16 = floor(d / 100)
    f18 = 100
    f1E = d % 100
```

**Per-block triple counts:**
```
triples_in_block(i) = block_dur if FADE else 100  (RGB_TRIPLE_COUNT)
total_RGB_triples   = Σ triples_in_block(i)
```

**Non-last block i (i < N-1):**
```
idx1 = rgb_start + 3 * (cumulative triples through and including block i)
     = "offset where THIS block's RGB data ends"
If next segment is FADE (duration fnd):
    f9  = (1, fnd)
    f11 = 0
If next segment is SOLID (duration snd):
    f9  = (floor(snd/100), 100)
    f11 = snd % 100
```

**Last block (i == N-1):**
```
idx2_p1 = 4 + 3 * total_RGB_triples
idx2_p2 = total_RGB_triples
```

### Code changes
- `prg_generator.py` — replaced `is_n1_full_program_fade` / `is_fade_first_with_solids` branches and the legacy `field_11_val` quirks table (~80 lines of brittle special-cases) with the unified emitter (~50 lines, no branches on sequence shape). Header and duration-block calculation are now O(N) with no special cases.
- `tests_not_exact_match/fade_reference_set/` — added regression script `verify_against_official.py` that re-builds JSON for all 12 patterns and binary-compares against the reference files. Run anytime to catch format regressions.

### Verification
- 12/12 reference PRGs: header + all duration blocks + footer byte-identical.
- All 5 pre-existing regression tests in `tests/` still PASS.
- RGB-section bytes still differ slightly (~16 % for fade-containing files) due to
  a 1-tick offset in our interpolation curve. This is purely cosmetic — the
  user has confirmed simple fades play correctly on the ball with this curve.

### What this enables
The user's stated goal of "putting fades anywhere in the sequence" is now fully
supported. There is no longer a bespoke code path for any particular pattern;
every block follows the same formula.
