# Roocode Sequence Designer Tools Examples

This directory contains example files demonstrating various effects and features of the Roocode Sequence Designer Tools.

## Python Examples

These Python scripts demonstrate how to use the effect implementation functions directly:

- **`snap_on_flash_off_example.py`**: Demonstrates the snap_on_flash_off effect, which quickly changes from a pre-base color to a target color, then smoothly fades back to a post-base color.

To run a Python example:

```bash
# From the project root directory
python -m roocode_sequence_designer_tools.examples.snap_on_flash_off_example
```

## Sequence Design Examples

These `.seqdesign.json` files demonstrate how to structure sequence designs with various effects:

- **`snap_on_flash_off_example.seqdesign.json`**: A sequence design that demonstrates the snap_on_flash_off effect for highlighting key moments in lyrics or music.

To compile a sequence design example:

```bash
# From the project root directory
python -m roocode_sequence_designer_tools.compile_seqdesign \
    roocode_sequence_designer_tools/examples/snap_on_flash_off_example.seqdesign.json \
    output.prg.json
```

## Effect Descriptions

### snap_on_flash_off

The `snap_on_flash_off` effect is designed for quickly highlighting key moments in a sequence, such as specific words in lyrics. It works by:

1. Starting with a pre-base color
2. Instantly changing to a target color (the "flash")
3. Smoothly fading back to a post-base color over a specified duration

#### Parameters:

- **pre_base_color**: The starting color before the flash
- **target_color**: The color to flash to
- **post_base_color**: The color to fade back to after the flash
- **fade_out_duration**: Duration of the fade-out in seconds
- **steps_per_second** (optional): Granularity of the fade-out (default: 20)

This effect is particularly useful for highlighting specific moments in lyrics or emphasizing beats in music.