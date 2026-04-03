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

### 2026-04-03 17:37 UTC-6 - LLM GUI Removal & Hot-Swap System
- **Removed all LLM integration from the Sequence Maker GUI** — menus, actions, handlers, settings tab, manager initialization, and imports have been gutted
- **Created hot-swap system** ([`sequence_maker/managers/sequence_swap_manager.py`](sequence_maker/managers/sequence_swap_manager.py)) — uses QFileSystemWatcher to monitor `~/.sequence_maker/sequence_swap_inbox.json` for new sequences pushed by the Sequence Designer Roo mode
- **Auto-save before swap** — current project is automatically saved before loading a new sequence
- **Sequence description display** — GUI status bar shows the description of the currently loaded sequence (blue italic label)
- **Updated Sequence Designer mode** — [`.roomodes`](.roomodes) and [`sequence_designer_mode_instructions.md`](roocode_sequence_designer_tools/docs/sequence_designer_mode_instructions.md) now include complete hot-swap system documentation
- **Files created:**
  - [`sequence_maker/managers/sequence_swap_manager.py`](sequence_maker/managers/sequence_swap_manager.py) — Hot-swap inbox watcher
- **Files modified:**
  - [`sequence_maker/app/application.py`](sequence_maker/app/application.py) — Replaced LLMManager with SequenceSwapManager
  - [`sequence_maker/ui/main_window.py`](sequence_maker/ui/main_window.py) — Removed LLM imports/handlers, added swap handlers
  - [`sequence_maker/ui/main_window_parts/menus.py`](sequence_maker/ui/main_window_parts/menus.py) — Removed LLM menu items, added description label
  - [`sequence_maker/ui/main_window_parts/actions.py`](sequence_maker/ui/main_window_parts/actions.py) — Removed LLM actions
  - [`sequence_maker/ui/main_window_parts/signals.py`](sequence_maker/ui/main_window_parts/signals.py) — Removed LLM signal connections
  - [`sequence_maker/ui/main_window_parts/handlers.py`](sequence_maker/ui/main_window_parts/handlers.py) — Removed LLM handlers
  - [`sequence_maker/ui/actions/tools_actions.py`](sequence_maker/ui/actions/tools_actions.py) — Removed LLM action creation
  - [`sequence_maker/ui/handlers/tools_handlers.py`](sequence_maker/ui/handlers/tools_handlers.py) — Removed LLM handler methods
  - [`sequence_maker/ui/dialogs/settings_dialog.py`](sequence_maker/ui/dialogs/settings_dialog.py) — Removed LLM settings tab
  - [`sequence_maker/ui/dialogs/__init__.py`](sequence_maker/ui/dialogs/__init__.py) — Removed LLMChatDialog import
  - [`sequence_maker/api/audio_action_api.py`](sequence_maker/api/audio_action_api.py) — Removed LLM manager registration
  - [`sequence_maker/api/timeline_action_api.py`](sequence_maker/api/timeline_action_api.py) — Removed LLM manager registration

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
*Timestamp: 2026-04-03 17:37 UTC-6*