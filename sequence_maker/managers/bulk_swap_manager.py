"""
Sequence Maker - Bulk Swap Manager

Handles simultaneous color swapping across all timelines in a project.
All swaps are applied in a single pass so that chained swaps
(e.g. red→green and green→red) work correctly.
"""

import logging


class BulkSwapManager:
    """Manages bulk color swap operations with undo support."""

    def __init__(self, app):
        """
        Initialize the bulk swap manager.

        Args:
            app: The main application instance.
        """
        self.logger = logging.getLogger("SequenceMaker.BulkSwapManager")
        self.app = app

    def get_project_colors(self):
        """Collect all unique colors used across all timelines in the project.

        Returns:
            list: Sorted list of unique RGB tuples.
        """
        colors = set()
        project = self.app.project_manager.current_project
        if not project:
            return []

        for timeline in project.timelines:
            for segment in timeline.segments:
                colors.add(tuple(segment.color))
                if segment.end_color is not None:
                    colors.add(tuple(segment.end_color))

        return sorted(colors)

    def apply_swap(self, config):
        """Apply a bulk color swap based on the dialog configuration.

        The swap is performed simultaneously: all color mappings are resolved
        first, then each segment's colors are replaced in a single pass.
        This ensures that swapping red↔green works correctly.

        Args:
            config (dict): Configuration from BulkSwapDialog.get_config():
                scope: 'entire_project' or 'time_range'
                start_time: float (only for time_range)
                end_time: float (only for time_range)
                color_pairs: list of (from_rgb, to_rgb) tuples

        Returns:
            bool: True if any changes were made, False otherwise.
        """
        project = self.app.project_manager.current_project
        if not project:
            self.logger.warning("No project loaded")
            return False

        color_pairs = config.get("color_pairs", [])
        if not color_pairs:
            self.logger.info("No color pairs specified")
            return False

        # Build the simultaneous mapping: from_color → to_color
        color_map = {}
        for from_color, to_color in color_pairs:
            from_key = tuple(from_color)
            to_val = tuple(to_color)
            color_map[from_key] = to_val

        scope = config.get("scope", "entire_project")
        start_time = config.get("start_time", 0.0)
        end_time = config.get("end_time", 0.0)

        # Save state for undo BEFORE making any changes
        self.app.undo_manager.save_state("bulk_color_swap")

        changed = False

        for timeline in project.timelines:
            for segment in timeline.segments:
                # For time_range scope, only apply to segments entirely
                # within the range
                if scope == "time_range":
                    if (segment.start_time < start_time or
                            segment.end_time > end_time):
                        continue

                # Apply simultaneous swap to segment color
                seg_color_key = tuple(segment.color)
                if seg_color_key in color_map:
                    segment.color = color_map[seg_color_key]
                    changed = True

                # Apply simultaneous swap to end_color (for fades)
                if segment.end_color is not None:
                    end_key = tuple(segment.end_color)
                    if end_key in color_map:
                        segment.end_color = color_map[end_key]
                        changed = True

        if changed:
            self.logger.info(
                f"Bulk color swap applied: {len(color_pairs)} pair(s), "
                f"scope={scope}"
            )
            # Refresh the timeline display
            self.app.timeline_manager.update_timelines()
        else:
            # No changes made — remove the saved undo state
            if self.app.undo_manager.undo_stack:
                self.app.undo_manager.undo_stack.pop()
                self.app.undo_manager.undo_stack_changed.emit()
            self.logger.info("Bulk color swap: no matching colors found")

        return changed
