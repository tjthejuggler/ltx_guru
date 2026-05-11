## 2026-05-11 — Snippet lyric-synced duration: remove clamp, stretch mini-timeline, anchor at marker

**Context.** The new `duration_mode` feature on `Snippet` allows
`end_of_word` / `beginning_of_word` modes that drive the apply-time
window length from the next timestamped lyric word. The initial
implementation (commit `bec9b4d`) had three usability bugs:

1. The lyric-synced duration was *clamped* by the snippet's configured
   `duration`, so a 2 s authored snippet inserted near a 5 s word
   boundary would still only run for 2 s — defeating the purpose of the
   feature.
2. The snippet's authored mini-timeline segments were not stretched to
   fill the effective window, leaving blank space when the lyric window
   was longer than the authored snippet.
3. In `Snippet Mode: END` + lyric `duration_mode`, the start position
   was computed as `marker - snippet.duration`, which is meaningless
   when `snippet.duration` no longer represents the runtime length.

**Decision.**

- `_get_end_of_word_duration` / `_get_beginning_of_word_duration` no
  longer clamp to `snippet.duration`. The configured duration is only
  used as a *fallback* when no word boundary is found after the
  insertion point. Parameter renamed `max_duration` → `fallback_duration`.
- `apply_snippet` computes
  `time_scale = effective_duration / snippet.duration` in lyric modes
  (1.0 otherwise) and multiplies each authored segment's `start_time` /
  `end_time` by it before offsetting by `position`. The whole authored
  pattern always fills the actual window.
- `MainWindow.keyPressEvent` always anchors the apply position at the
  current marker when `duration_mode` is lyric-synced, regardless of
  whether `snippet_mode` is `begin` or `end`. The `marker - duration`
  back-shift is only applied for `end` + `timed`.

**Alternatives considered.** Stretch only when effective > authored
(fill from the right with the last segment's colour); rejected as more
surprising than uniform scaling for the typical "single colour" or
"two-colour fade" snippet authoring pattern.

**Affected symbols.**
- `SnippetManager._get_end_of_word_duration`
- `SnippetManager._get_beginning_of_word_duration`
- `SnippetManager.apply_snippet`
- `MainWindow.keyPressEvent` (snippet-mode branch)
- `Snippet` docstring