"""
Effect Implementations Package for Roocode Sequence Designer Tools

This package contains modules that implement various lighting effects
for the Roocode Sequence Designer system.
"""

# Import common effects for easier access
from roocode_sequence_designer_tools.effect_implementations.common_effects import (
    apply_solid_color_effect,
    apply_fade_effect,
    apply_strobe_effect,
    apply_snap_on_flash_off_effect
)

# Import audio-driven effects
from roocode_sequence_designer_tools.effect_implementations.audio_driven_effects import (
    apply_pulse_on_beat_effect,
    apply_section_theme_from_audio_effect
)