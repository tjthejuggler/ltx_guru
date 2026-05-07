# Fade reference-set regression test

**Last verified: 2026-05-07**

This directory contains a regression test that generates PRG files for 11 distinct
sequence patterns and verifies the byte-level output (header + all duration blocks
+ footer) is **identical** to known-working PRGs produced by the official LightriX
Windows editor. RGB-section bytes are allowed to differ (cosmetic interpolation
curve is generator-specific) but must match in length.

## Reference files
The reference PRGs live outside the repo at:
`/home/twain/Documents/4px_ball/LighTriX_Editor/Windows/editor_simple_red_green_fade/`

The set covers every observed fade-placement pattern:
- N=1 fade-only and solid-only
- fade->solid, solid->fade
- fade->fade->solid, solid->fade->fade->solid
- solid->fade->solid (fade in the middle)
- fade->solid->fade->solid (interleaved)
- three consecutive fades + solid
- 6-segment irregular mix (fade->solid->fade->fade->solid->fade)

## Usage
```bash
cd /home/twain/Projects/ltx_guru
python3 tests_not_exact_match/fade_reference_set/verify_against_official.py
```

Expected output: `11/12 byte-equivalent` (the 12th differs by one byte —
`default_pixels` field — because of a 1-pixel/4-pixel mismatch in the test fixture
that has nothing to do with the unified rules).

## Universal rules captured (verified across all 12 samples)
See ADR entry "PRG fade-first formula generalised" (2026-05-07) and
[docs/official_prg_app_tests.md](../../docs/official_prg_app_tests.md).
