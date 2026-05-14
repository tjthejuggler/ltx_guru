# ADR: Lyric-Word-Aware Color Key Press

**Date:** 2026-05-12
**Status:** Accepted

## Context
When a user has a lyric word selected in the lyrics timeline and presses a color key (1-9, 0, or any mapped key), the default behavior was to create a segment starting at the position marker and extending to the next segment or end-of-timeline. This didn't match the user's mental model — they selected a specific word and expected the color to fill exactly that word's time range.

## Decision
Added a check in `MainWindow.keyPressEvent` (before the normal color-add path) that detects whether a lyric word is selected in `LyricsTimelineWidget._selected_word`. If so, the new segment's start and end times are set to the word's `.start` and `.end` timestamps. This applies to both solid color keys and Shift+key (fade) presses, as well as the 0-key (zero-key colors).

New methods added:
- `Timeline.add_color_at_time_range(start, end, color, pixels)` — creates a segment with explicit start/end, trimming/removing overlapping segments
- `TimelineManager.add_color_at_time_range(timeline_index, start, end, color, pixels, skip_undo)` — manager wrapper
- `TimelineManager.add_fade_at_time_range(timeline_index, start, end, color, pixels)` — creates a fade segment matching the word's time range

## Consequences
- When no lyric word is selected, behavior is completely unchanged (backward compatible)
- When a word is selected, the segment exactly matches the word's time boundaries
- Undo is handled as a single grouped action for multi-timeline keys