# ADR: Backslash Hotkey and Zero Key Color Configuration

**Date:** 2026-05-11
**Status:** Accepted

## Context
Two new hotkey features were requested:
1. `\` key to jump the position marker back to the previous timeline marker
2. `0` key to add configurable per-timeline colors at the current position

## Decision
1. **Backslash key**: In `MainWindow.keyPressEvent()`, when `\` is pressed, find the last marker strictly before the current position and jump there (or to 0.0 if none exists). Also seeks audio to keep in sync.
2. **Zero key**: Added `zero_key_colors` attribute to `Project` model (list of 3 RGB tuples or None). When `0` is pressed, each non-None color is applied to its respective timeline via `add_color_at_position()`. The configuration dialog is accessible from Timeline → "Configure '0' Key Colors…".
3. **ZeroKeyColorDialog**: New dialog in `ui/dialogs/zero_key_color_dialog.py` with 3 rows (one per ball), each having quick-pick color buttons (matching the segment context menu), a "Custom…" QColorDialog button, and a "None" button to skip that timeline.

## Impact
- `sequence_maker/ui/main_window.py` — added `\` and `0` key handlers, `_on_configure_zero_key()` method, `QDialog` import
- `sequence_maker/models/project.py` — added `zero_key_colors` attribute, serialization in `to_dict`/`from_dict`
- `sequence_maker/ui/actions/timeline_actions.py` — added `configure_zero_key_action`
- `sequence_maker/ui/main_window_parts/actions.py` — registered `configure_zero_key_action`
- `sequence_maker/ui/main_window_parts/menus.py` — added menu item to Timeline menu
- `sequence_maker/ui/dialogs/zero_key_color_dialog.py` — new file