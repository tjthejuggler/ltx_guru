ADR: Snippet "End of Word" Duration Mode

Date: 2026-05-11

Decision: Add a per-snippet `duration_mode` field with two values:
- "timed" (default, legacy): snippet uses its fixed `duration` value
- "end_of_word": when applied, the snippet's effective duration extends from the insertion position to the end of the next timestamped lyric word, clamped to `snippet.duration` as a maximum

Rationale: Users want snippets that automatically adapt to lyric word boundaries, so a color pattern fills exactly until the next word ends rather than requiring manual duration adjustment for each word.

Implementation:
- `Snippet.duration_mode` attribute with `DURATION_MODE_TIMED` / `DURATION_MODE_END_OF_WORD` constants
- Serialized as `durationMode` in JSON (backward-compatible: missing key defaults to "timed")
- UI: combo box toggle in snippet properties row; duration spin disabled in "end_of_word" mode
- `SnippetManager._get_end_of_word_duration()` finds next word from position; `get_effective_duration()` is the public API
- `apply_snippet()` computes effective duration based on mode before applying segments