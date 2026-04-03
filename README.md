# LTX Guru Project

This repository contains tools and projects for creating light sequences for LTX juggling balls.

## Sequence Projects

### Three Ball Flasher
- **Created:** 2025-06-10 16:00 UTC+7
- **Description:** A 2-minute sequence for three balls. Each ball takes a turn flashing its designated color (Red, Blue, Green) for 0.1 seconds. The sequence is:
    - Ball 1 (Red): On from 0.25s to 0.35s, then every 0.75s thereafter.
    - Ball 2 (Blue): On from 0.50s to 0.60s, then every 0.75s thereafter.
    - Ball 3 (Green): On from 0.75s to 0.85s, then every 0.75s thereafter.
- **Files:**
    - [`sequence_projects/three_ball_flasher/ball1_red.seqdesign.json`](sequence_projects/three_ball_flasher/ball1_red.seqdesign.json)
    - [`sequence_projects/three_ball_flasher/ball2_blue.seqdesign.json`](sequence_projects/three_ball_flasher/ball2_blue.seqdesign.json)
    - [`sequence_projects/three_ball_flasher/ball3_green.seqdesign.json`](sequence_projects/three_ball_flasher/ball3_green.seqdesign.json)
- **Compilation:**
  Each `.seqdesign.json` file can be compiled into a `.prg.json` file using the `compile_seqdesign.py` tool. For example:
  ```bash
  python -m roocode_sequence_designer_tools.compile_seqdesign sequence_projects/three_ball_flasher/ball1_red.seqdesign.json sequence_projects/three_ball_flasher/ball1_red.prg.json
  ```
  Repeat for `ball2_blue.seqdesign.json` and `ball3_green.seqdesign.json`.

## Recent Updates

### 2026-04-03 11:48 UTC-6 - Sequence Designer Major Overhaul
- **Comprehensive Sequence Designer mode rewrite** — The `.roomodes` Sequence Designer mode has been completely rewritten with:
  - All available tools cataloged with usage examples
  - Full music analysis capabilities (beats, tempo, sections, energy, onsets, spectral features, key detection)
  - Lyrics processing workflow (extraction, alignment via Gentle, synced timestamps)
  - Pattern creation capabilities (beat-sync, section themes, lyric-triggered effects)
- **Song Data Persistence** — New [`song_data_manager.py`](roocode_sequence_designer_tools/song_data_manager.py) tool that stores all gathered data (lyrics, audio analysis, metadata) in a per-project `song_data.json` file. Once data is gathered for a song, it never needs to be re-gathered.
- **Sequence Versioning** — Multiple sequence versions per song with descriptions, file references, tags, and derivation history. Descriptions are designed to be displayed in the Sequence Maker GUI.
- **Files created/updated:**
  - [`roocode_sequence_designer_tools/song_data_manager.py`](roocode_sequence_designer_tools/song_data_manager.py) — New persistent song data manager
  - [`.roomodes`](.roomodes) — Complete Sequence Designer mode rewrite
  - [`roocode_sequence_designer_tools/docs/sequence_designer_mode_instructions.md`](roocode_sequence_designer_tools/docs/sequence_designer_mode_instructions.md) — Added song data persistence, versioning, and music analysis docs
  - [`roocode_sequence_designer_tools/tools_lookup.json`](roocode_sequence_designer_tools/tools_lookup.json) — Added song_data_manager tool entry
  - [`roocode_sequence_designer_tools/README.md`](roocode_sequence_designer_tools/README.md) — Added song_data_manager documentation

### 2025-06-10 16:19 UTC+7 - Sequence Designer Efficiency Improvements
- **Updated Sequence Designer roomode** to use code generation for repetitive content instead of manual writing
- **Added explicit guidelines** for when to use Python scripts vs manual file creation
- **Key improvement:** For ball sequences, .smproj files, or any repetitive JSON content (>20 segments, flasher patterns, color cycles), the roomode now automatically uses Python code generation
- **Files updated:**
  - [`.roomodes`](.roomodes) - Added section 2a with critical code generation directive
  - [`roocode_sequence_designer_tools/docs/sequence_designer_mode_instructions.md`](roocode_sequence_designer_tools/docs/sequence_designer_mode_instructions.md) - Enhanced Tool Usage Guidelines
  - [`roocode_sequence_designer_tools/docs/self_improvement_log.md`](roocode_sequence_designer_tools/docs/self_improvement_log.md) - Documented the learning

---
*Timestamp: 2026-04-03 11:48 UTC-6*