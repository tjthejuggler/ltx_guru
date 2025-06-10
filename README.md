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

### 2025-06-10 16:19 UTC+7 - Sequence Designer Efficiency Improvements
- **Updated Sequence Designer roomode** to use code generation for repetitive content instead of manual writing
- **Added explicit guidelines** for when to use Python scripts vs manual file creation
- **Key improvement:** For ball sequences, .smproj files, or any repetitive JSON content (>20 segments, flasher patterns, color cycles), the roomode now automatically uses Python code generation
- **Files updated:**
  - [`.roomodes`](.roomodes) - Added section 2a with critical code generation directive
  - [`roocode_sequence_designer_tools/docs/sequence_designer_mode_instructions.md`](roocode_sequence_designer_tools/docs/sequence_designer_mode_instructions.md) - Enhanced Tool Usage Guidelines
  - [`roocode_sequence_designer_tools/docs/self_improvement_log.md`](roocode_sequence_designer_tools/docs/self_improvement_log.md) - Documented the learning

---
*Timestamp: 2025-06-10 16:19 UTC+7*