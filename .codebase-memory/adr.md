
## 2026-05-05 — Snippet duration is the single source of truth

**Context.** A snippet is a short, reusable colour pattern (per-ball mini-timelines)
that the user can splat onto the main timelines via a hotkey. Originally the
snippet builder reused `Timeline.add_color_at_time()` (the same helper the main
editor uses), which extends a freshly-added segment open-endedly to the next
segment or `time + 3600s` when the timeline is empty. Combined with
`Snippet.get_duration()` returning `max(self.duration, max_segment_end_time)`,
this caused a 2-second snippet to actually report a 3600-second duration as
soon as the user added a colour to it — and `apply_snippet` therefore
overwrote up to an hour of the main timeline.

**Decision.**
1. `Snippet.duration` is the **only** source of truth for a snippet's length.
   `Snippet.get_duration()` now returns `self.duration` unconditionally.
2. Snippets must never contain segments whose `end_time` exceeds
   `self.duration`. `Snippet._clamp_segments_to_duration()` enforces this
   defensively at load time (`from_dict`) and after `set_snippet_duration`.
3. `SnippetManager.add_color_to_snippet` no longer delegates to
   `Timeline.add_color_at_time`. It splices segments into the snippet directly,
   using the same overlap rules as `apply_snippet`, with the new segment
   hard-clamped to `[position, snippet.duration]`.
4. `SnippetManager.apply_snippet` uses `snippet.duration` directly (not
   `get_duration()`) when computing the apply range.

**Consequences.** Inserting a snippet of length N at cursor position P only
ever modifies `[P, P + N]` of each enabled main timeline. The colours present
before/after that range are preserved exactly. Legacy projects with the old
3600s segments are auto-sanitised when the project is loaded.

**Affected files.**
- `sequence_maker/models/snippet.py`
- `sequence_maker/managers/snippet_manager.py`
