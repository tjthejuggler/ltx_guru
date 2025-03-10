# Test Batch 002 - Accurate Format Sequences

This batch of test files has been created using the `accurate_generator.py` script which carefully reproduces the exact binary format of working .prg files based on hex dump analysis.

## Single Color Tests

These files should display a constant solid color:

1. `accurate_red.prg` - Should display solid red
   - Command: `python3 accurate_generator.py single 4 255 0 0 accurate_red.prg`
   - Exact format match to successful 4px_10_red.prg

2. `accurate_green.prg` - Should display solid green
   - Command: `python3 accurate_generator.py single 4 0 255 0 accurate_green.prg`
   - Exact format match to successful 4px_green_100.prg (with different color)

3. `accurate_blue.prg` - Should display solid blue
   - Command: `python3 accurate_generator.py single 4 0 0 255 accurate_blue.prg`
   - Exact format match to successful 4px_blue_10.prg

## Two-Color Transition Tests

These files should display a transition between two colors (10 seconds each):

1. `accurate_red_to_green.prg` - Should transition from red to green
   - Command: `python3 accurate_generator.py dual 4 255 0 0 0 255 0 accurate_red_to_green.prg`
   - Format matches successful 4px_red_10_green_10.prg

2. `accurate_green_to_blue.prg` - Should transition from green to blue
   - Command: `python3 accurate_generator.py dual 4 0 255 0 0 0 255 accurate_green_to_blue.prg`
   - Format matches successful 4px_red_10_green_10.prg (with different colors)

3. `accurate_blue_to_red.prg` - Should transition from blue to red
   - Command: `python3 accurate_generator.py dual 4 0 0 255 255 0 0 accurate_blue_to_red.prg`
   - Format matches successful 4px_red_10_green_10.prg (with different colors)

4. `accurate_red_blink.prg` - Should blink between red and black (off)
   - Command: `python3 accurate_generator.py dual 4 255 0 0 0 0 0 accurate_red_blink.prg`
   - Format matches successful 4px_red_10_green_10.prg (with black as second color)

## Key Improvements

1. Exact binary structure matching working examples
2. Proper header format and segment structure
3. Correct length and byte offsets
4. Properly formatted RGB color data section

## Testing Process

1. Load each `.prg` file onto the ball one at a time
2. Note which patterns work as expected and which don't
3. For patterns that don't work as expected, note what actually happens
4. Based on results, we can further refine our understanding of the format