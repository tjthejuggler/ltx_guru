# Test Batch 003 - Long Duration Sequences

This batch of test files has been created using the `long_duration_generator.py` script which significantly increases the duration values in the .prg files. This is to test the hypothesis that the rapid flashing observed in previous tests might be due to very short time periods causing the program to loop rapidly.

## Single Color Tests with 100-Second Duration

These files should display a constant solid color for 100 seconds:

1. `long_red.prg` - Should display solid red for 100 seconds
   - Command: `python3 long_duration_generator.py single 4 255 0 0 long_red.prg 1000`
   - Duration value: 1000 deciseconds (100 seconds)

2. `long_green.prg` - Should display solid green for 100 seconds
   - Command: `python3 long_duration_generator.py single 4 0 255 0 long_green.prg 1000`
   - Duration value: 1000 deciseconds (100 seconds)

3. `long_blue.prg` - Should display solid blue for 100 seconds
   - Command: `python3 long_duration_generator.py single 4 0 0 255 long_blue.prg 1000`
   - Duration value: 1000 deciseconds (100 seconds)

## Two-Color Transition Tests with 100-Second Duration

These files should display a transition between two colors (100 seconds each):

1. `long_red_to_green.prg` - Should transition from red to green
   - Command: `python3 long_duration_generator.py dual 4 255 0 0 0 255 0 long_red_to_green.prg 1000`
   - Duration value: 1000 deciseconds (100 seconds) per color

2. `long_red_blink.prg` - Should blink between red and black/off
   - Command: `python3 long_duration_generator.py dual 4 255 0 0 0 0 0 long_red_blink.prg 1000`
   - Duration value: 1000 deciseconds (100 seconds) per state

## Extremely Long Duration Tests (500 Seconds)

These files use an even longer duration as an extreme test:

1. `very_long_red.prg` - Should display solid red for 500 seconds
   - Command: `python3 long_duration_generator.py single 4 255 0 0 very_long_red.prg 5000`
   - Duration value: 5000 deciseconds (500 seconds)

2. `very_long_red_to_green.prg` - Should transition from red to green with 500 seconds per color
   - Command: `python3 long_duration_generator.py dual 4 255 0 0 0 255 0 very_long_red_to_green.prg 5000`
   - Duration value: 5000 deciseconds (500 seconds) per color

## Key Changes from Previous Tests

1. **Much Longer Durations**: Increased from 10 seconds to 100-500 seconds
2. **Duration Values**: Changed all duration-related bytes in the file format
3. **Same Binary Structure**: Otherwise maintains the same binary structure as Batch 002

## Testing Process

1. Load each `.prg` file onto the ball one at a time
2. Note which patterns work as expected and which don't
3. For patterns that don't work as expected, note what actually happens
4. Pay special attention to whether the longer durations reduce or eliminate the flashing behavior