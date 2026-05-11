ADR-008: Arrow Keys Clone/Move Segments Between Timelines

Date: 2026-05-11
Status: Accepted

Context:
Users need to quickly copy or move color segments (chunks) from one ball timeline to another. Previously, Up/Down arrow keys adjusted segment duration (extend/shrink end time), which is less useful than cross-timeline operations for a 3-ball juggling sequence editor.

Decision:
- Up/Down arrow keys now navigate between timelines instead of adjusting duration.
- Up arrow: moves segment to previous timeline (Ball 1→3, Ball 2→1, Ball 3→2 — cyclic).
- Down arrow: moves segment to next timeline (Ball 1→2, Ball 2→3, Ball 3→1 — cyclic).
- A "Arrows Clone" checkbox on the main toolbar controls whether the operation is copy (checked, default) or cut (unchecked).
- When unchecked (cut mode), the original segment is removed by merging it with its previous neighbour, or simply deleted if it's the first segment.
- Left/Right arrow keys still nudge segments by 0.01s as before.
- The new segment on the target timeline overwrites whatever was there (overlap resolution via _resolve_segment_overlap).
- Undo is handled as a single step using is_dragging to suppress intermediate saves.

Consequences:
- Users lose the Up/Down duration adjustment shortcut (extend/shrink end time). This was rarely used and can be done via the segment editor panel.
- The cyclic wrapping means pressing Up from Ball 1 goes to Ball 3 (not "no action"), matching the user's specification.
- The checkbox defaults to checked (clone/copy mode) so the most common use case preserves the original segment.