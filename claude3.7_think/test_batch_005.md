# Test Batch 005 - Multi-Color Sequences

This batch of test files has been created using the `multi_color_generator.py` script which extends our successful direct copy approach to support sequences with more than two colors.

## Test Files

1. `rgb_cycle.prg` - Should cycle through RGB colors with 10-second durations:
   - Red (10 seconds)
   - Green (10 seconds)
   - Blue (10 seconds)
   - Back to Red
   - Command: `python3 multi_color_generator.py rgb_cycle 4 100 rgb_cycle.prg`

2. `rainbow.prg` - Should cycle through rainbow colors with 10-second durations:
   - Red (10 seconds)
   - Orange (10 seconds)
   - Yellow (10 seconds)
   - Green (10 seconds)
   - Blue (10 seconds)
   - Indigo (10 seconds)
   - Violet (10 seconds)
   - Back to Red
   - Command: `python3 multi_color_generator.py rainbow 4 100 rainbow.prg`

3. `custom_sequence.prg` - Custom sequence with varying durations:
   - Red (10 seconds)
   - Green (15 seconds)
   - Blue (20 seconds)
   - Red (10 seconds)
   - Command: `python3 multi_color_generator.py custom 4 custom_sequence.prg 255 0 0 100 0 255 0 150 0 0 255 200 255 0 0 100`

## Implementation Details

1. Based on the successful "direct copy" approach from Test Batch 004
2. Extends the two-color transition format to support multiple colors
3. Maintains exact binary structure but adds additional segments for more colors
4. Uses same segment format and timing mechanisms as working examples

## Expected Behavior

Each sequence should:
1. Display solid colors (no flashing)
2. Hold each color for the specified duration
3. Transition cleanly between colors
4. Loop back to the beginning when complete

## Testing Process

1. Load each `.prg` file onto the ball one at a time
2. Note which patterns work as expected and which don't
3. For patterns that don't work as expected, note what actually happens
4. Pay special attention to:
   - Color accuracy
   - Duration accuracy
   - Transition smoothness
   - Looping behavior

## Important Notes

This test batch represents our first attempt at sequences with more than two colors using the successful "direct copy" approach. The results will help us understand:

1. If our understanding of the multi-segment format is correct
2. Whether the balls support more than two colors in a sequence
3. If segment timing works the same way for multiple segments
4. Whether our segment linking approach is correct