# Test Batch 004 - Direct Copy Sequences

This batch of test files has been created using the `direct_copy_generator.py` script which takes a different approach: instead of trying to interpret the file format, it directly copies the binary structure of known working examples, only changing the color values.

## Single Color Tests (Direct Copy)

These files should display a constant solid color for 10 seconds:

1. `direct_red.prg` - Should display solid red for 10 seconds
   - Command: `python3 direct_copy_generator.py single 4 255 0 0 direct_red.prg`
   - Direct copy of working 4px_10_red.prg with only color values changed

2. `direct_green.prg` - Should display solid green for 10 seconds
   - Command: `python3 direct_copy_generator.py single 4 0 255 0 direct_green.prg`
   - Direct copy of working 4px_10_red.prg with only color values changed

3. `direct_blue.prg` - Should display solid blue for 10 seconds
   - Command: `python3 direct_copy_generator.py single 4 0 0 255 direct_blue.prg`
   - Direct copy of working 4px_10_red.prg with only color values changed

## Two-Color Transition Tests (Direct Copy)

These files should display a transition between two colors (10 seconds each):

1. `direct_red_to_green.prg` - Should transition from red to green
   - Command: `python3 direct_copy_generator.py dual 4 255 0 0 0 255 0 direct_red_to_green.prg`
   - Direct copy of working 4px_red_10_green_10.prg with only color values changed

2. `direct_red_blink.prg` - Should blink between red and black/off
   - Command: `python3 direct_copy_generator.py dual 4 255 0 0 0 0 0 direct_red_blink.prg`
   - Direct copy of working 4px_red_10_green_10.prg with only color values changed

## Key Differences from Previous Tests

1. **Direct Binary Copy**: Instead of trying to interpret the file format, this approach directly copies the binary structure of known working examples
2. **Minimal Changes**: Only the RGB color values are changed, all other bytes remain identical to the working examples
3. **Exact File Size**: The generated files have exactly the same size as the original working examples
4. **Original Timing**: Uses the original 10-second timing from the working examples

## Testing Process

1. Load each `.prg` file onto the ball one at a time
2. Note which patterns work as expected and which don't
3. For patterns that don't work as expected, note what actually happens
4. Compare results with previous test batches to identify what factors affect the behavior