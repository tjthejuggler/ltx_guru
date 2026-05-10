# Timeline Markers Feature (2026-05-10)

## Decision
Add visual-only timeline markers (dotted vertical lines) that users can place at any time position for reference. Markers do not affect sequences or playback.

## Implementation
- New model: `models/marker.py` — `TimelineMarker` class with `id`, `time`, `color`, `created` fields, plus `to_dict`/`from_dict` serialization (mirrors `TimelineNote` pattern).
- 6 basic colors: Red, Green, Blue, Yellow, Cyan, Magenta (defined in `MARKER_COLORS` dict).
- Project model: Added `self.markers = []` in `__init__`, serialized in `to_dict()`, deserialized in `from_dict()`.
- UI: Right-click on timeline → "Add Marker Here" opens `MarkerColorDialog` (simple 6-button popup). Marker drawn as dotted vertical line + diamond indicator.
- Right-click on marker line → "Delete Marker" to remove.
- Markers are saved/loaded with the `.smproj` file.

## Rationale
Markers are simpler than notes (no text content) and serve as quick visual bookmarks. Keeping them as a separate list from notes avoids cluttering the note system with empty-text entries.