## 2026-05-11 — Lyrics timeline: fix word selection + backtick navigation

### Context
Clicking a word in the lyrics timeline often selected the *previous* word. This happened because: (1) adjacent/overlapping words share boundary timestamps, and (2) `mouseReleaseEvent` emitted `word_clicked(wt.start)` which triggered `set_position()` — a time-based lookup that could match the wrong word when timestamps overlap.

### Decision
1. **Direct selection on click**: `mouseReleaseEvent` now sets `_selected_word` directly to the clicked word before emitting `word_clicked`, bypassing the time-based lookup entirely.
2. **Sticky selection in `set_position()`**: Added early return if the new position is still within the currently selected word's range. This prevents `set_position()` (called via the `word_clicked` signal chain) from overriding the just-set selection with a wrong word.
3. **Half-open interval**: Boundary check uses `wt.start <= position < wt.end` (not `<=` on end) for the fallback lookup.
4. **Backtick key navigation**: Changed from Tab to backtick (`) for next-word navigation, since Tab is reserved for widget focus traversal in Qt.
5. **StrongFocus**: Changed from `NoFocus` to `StrongFocus` so the widget can receive keyboard events.

### Consequences
- Clicking a word now reliably selects that word, even when timestamps overlap.
- Backtick key advances to the next lyric word (wrapping around).
- The widget now participates in the Qt focus chain.