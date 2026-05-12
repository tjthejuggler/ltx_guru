# ADR: Bulk Color Swap Feature

## Date: 2026-05-12

## Status: Accepted

## Context
Users need the ability to swap colors across the entire project or a time range. The swap must be simultaneous (not sequential) so that chained swaps like red↔green work correctly. The operation must be reversible with a single undo.

## Decision
- Created `BulkSwapManager` in `managers/bulk_swap_manager.py` that builds a color_map dict from all pairs, then applies all mappings in a single pass over every segment in every timeline.
- Created `BulkSwapDialog` in `ui/dialogs/bulk_swap_dialog.py` with scope selection (entire project / time range), dynamic color pair rows with a popup color picker showing common + project-specific colors, and a plus button for adding pairs.
- For time range scope, only segments entirely within the range are modified.
- Undo is handled by calling `undo_manager.save_state("bulk_color_swap")` before applying changes, leveraging the existing snapshot-based undo system.
- If no changes are made (no matching colors), the saved undo state is popped to avoid cluttering the stack.

## Files Added
- `sequence_maker/managers/bulk_swap_manager.py`
- `sequence_maker/ui/dialogs/bulk_swap_dialog.py`

## Files Modified
- `sequence_maker/app/application.py` — import and instantiate BulkSwapManager
- `sequence_maker/ui/main_window_parts/actions.py` — add bulk_swap_action
- `sequence_maker/ui/main_window_parts/menus.py` — add action to Timeline menu
- `sequence_maker/ui/main_window.py` — add `_on_bulk_swap` handler