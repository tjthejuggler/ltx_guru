
## ADR — 2026-05-07 — Fade-first PRG file format (cmm-code session)

### Context
sequence_maker exports timelines through `sequence_maker/export/prg_exporter.py` → `prg_generator.py` (subprocess). When a timeline started with a *fade* segment, the resulting PRG file made the LTX ball play a rapid orange/yellow flicker instead of a smooth red→green fade.

Reverse-engineering against two reference PRGs from the official Windows LightriX editor — `editor_simple_red_green_fade.prg` (1Hz, 10-tick fade + 60-tick green) and `editor_simple_red_green_100rf.prg` (100Hz, 1000-tick fade + 6000-tick green) — showed that prg_generator.py's existing duration-block formulas were derived from solid-only sequences and the N=1 full-program fade case. They produced wrong values for fade-first N≥2 sequences in: header field 0x18, header field 0x1E, the fade-block's f09/idx1/f11, and the last-block's idx2_p1/idx2_p2.

### Decision
Treat **fade-first N≥2 sequences** as a separate code path (`is_fade_first_with_solids`) in [`prg_generator.py.generate_prg_file()`](prg_generator.py:273) with these formulas (verified byte-identical to both reference PRGs at the header + duration-block region):

- Header: `f16 = 1`, `f18 = fade_dur`, `f1E = 0`.
- Block 0 (the fade): `f9 = (floor(next_solid_dur/100), 100)`, `idx1 = 3*fade_dur + 70`, `f11 = next_solid_dur % 100`.
- Last block: `idx2_p1 = 304 + 3*fade_dur + 300*(N-2)`, `idx2_p2 = total_RGB_triple_count_in_file`.

The N=2 case is fully verified. The `300*(N-2)` extension for N>2 is a hypothesis based on the standard solid-step constant; it needs at least one more reference PRG (e.g. fade → solid → solid) to be confirmed.

### Consequences
- Fades now upload to balls and play correctly.
- The 5 existing tests (all solid-only or solid-first) continue to pass byte-for-byte.
- Untouched paths: N=1 full-program fade, N=1 solid, N≥2 solid-first (with or without embedded fades that are NOT segment 0). These remain governed by the original solid-derived formulas.

### Related change
[`sequence_maker/models/timeline.py`](sequence_maker/models/timeline.py:222): the auto-extension default for the **last** color block was reduced from 3600 s (1 hour) to 60 s (1 minute). The hour-long default forced `split_long_segments()` to chop the trailing solid into 6+ blocks, bloating PRG output and making fade-block bugs much harder to diagnose.

### Open questions / future work
1. The official editor's RGB fade interpolation uses a non-linear "256 levels spread over N steps with ~3 samples per level" algorithm rather than `round(i*delta/(N-1))`. Currently cosmetic; revisit if the ball's playback engine is found to be sensitive to the exact sample distribution.
2. The `300*(N-2)` step for fade-first N>2 last-block idx2_p1 is unverified.
3. Embedded fades that are NOT the first segment still go through `_calculate_intermediate_block_index1_base()` and `_calculate_last_block_index2_bases()` — these may have similar bugs but no evidence yet.
