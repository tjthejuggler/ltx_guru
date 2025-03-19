# PRG JSON Format Guide

This guide explains how to create JSON files that can be converted to .prg files for LTX juggling balls, with special focus on handling non-integer durations.

## Basic JSON Structure

The PRG generator accepts JSON files with the following structure:

```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 1,
  "end_time": 10,
  "sequence": {
    "0": {"color": [255, 0, 0], "pixels": 4},
    "1": {"color": [0, 255, 0], "pixels": 4}
  }
}
```

Let's break down each field:

- `default_pixels`: Number of pixels to use (1-4) when not specified for a color segment
- `color_format`: Color format, either "rgb" or "hsv"
- `refresh_rate`: Timing resolution in Hz (crucial for handling non-integer durations)
- `end_time`: Total duration of the sequence in time units
- `sequence`: Dictionary mapping time points to colors

## Understanding the Refresh Rate

The `refresh_rate` parameter is the key to handling non-integer durations. It defines the timing resolution of your sequence:

- `refresh_rate = 1`: Each time unit equals 1 second
- `refresh_rate = 10`: Each time unit equals 0.1 seconds
- `refresh_rate = 100`: Each time unit equals 0.01 seconds

The formula is: **Time Unit = 1 / refresh_rate seconds**

## Handling Non-Integer Durations

To create a sequence with non-integer durations (like 0.63 seconds, 1.44 seconds, etc.), follow these steps:

### Step 1: Choose an Appropriate Refresh Rate

Select a refresh rate that can accurately represent your smallest time increment. For example:
- If your smallest increment is 0.01 seconds, use `refresh_rate = 100`
- If your smallest increment is 0.1 seconds, use `refresh_rate = 10`

### Step 2: Convert Times to Time Units

Convert all your time points to time units based on the refresh rate:

```
Time Units = Time in Seconds × Refresh Rate
```

For example, with `refresh_rate = 100`:
- 0.63 seconds = 0.63 × 100 = 63 time units
- 1.44 seconds = 1.44 × 100 = 144 time units
- 12.99 seconds = 12.99 × 100 = 1299 time units

### Step 3: Create Your Sequence Dictionary

Use the time units as keys in your sequence dictionary:

```json
"sequence": {
  "0": {"color": [255, 0, 0], "pixels": 4},
  "63": {"color": [0, 0, 255], "pixels": 4},
  "207": {"color": [0, 0, 255], "pixels": 4},
  "1506": {"color": [0, 255, 0], "pixels": 4}
}
```

### Step 4: Set the End Time

Set the `end_time` to the total duration in time units:

```
end_time = Total Duration in Seconds × Refresh Rate
```

## Complete Example with Non-Integer Durations

Here's a complete example for a sequence with the following timing:
- Red for 0.63 seconds
- Blue for 1.44 seconds
- Blue for 12.99 seconds

Using a refresh rate of 100 (for 0.01 second precision):

```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 100,
  "end_time": 1506,
  "sequence": {
    "0": {"color": [255, 0, 0], "pixels": 4},
    "63": {"color": [0, 0, 255], "pixels": 4},
    "207": {"color": [0, 0, 255], "pixels": 4}
  }
}
```

Let's break down the calculations:
1. Start with red at time 0
2. Switch to blue at 0.63 seconds = 63 time units
3. Stay blue at 0.63 + 1.44 = 2.07 seconds = 207 time units
4. End time is 2.07 + 12.99 = 15.06 seconds = 1506 time units

Note that in this example, we have a blue-to-blue transition at time unit 207. This might seem redundant, but it's included to demonstrate how to handle multiple segments with precise timing.

## Important Considerations

1. **Precision**: Choose a refresh rate that provides enough precision for your needs. Higher refresh rates allow for more precise timing but create larger PRG files.

2. **Rounding**: When converting seconds to time units, you may need to round to the nearest integer since time units must be whole numbers:
   ```
   Time Units = round(Time in Seconds × Refresh Rate)
   ```

3. **Segment Duration Calculation**: The duration of each segment is calculated as the difference between its start time and the next segment's start time (or the end time for the last segment).

4. **Redundant Color Transitions**: If you have consecutive segments with the same color (like our blue-to-blue example), you can omit the redundant transition to simplify your JSON.

5. **Maximum Refresh Rate**: While you can use very high refresh rates for extreme precision, keep in mind that the LTX balls have hardware limitations. Very short durations (less than 0.01 seconds) may not display correctly on all ball models.

## Using the PRG Generator

Once you've created your JSON file, use the PRG generator to convert it to a .prg file:

```bash
python3 prg_generator.py input.json output.prg
```

The generator will:
1. Parse your JSON file
2. Calculate segment durations based on time points
3. Generate a binary .prg file according to the LTX ball specification
4. Output debug information about the conversion process

## Advanced Example: Complex Color Sequence

Here's a more complex example with multiple colors and varying durations:

```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 100,
  "end_time": 1000,
  "sequence": {
    "0": {"color": [255, 0, 0], "pixels": 4},
    "63": {"color": [0, 0, 255], "pixels": 4},
    "207": {"color": [0, 255, 0], "pixels": 4},
    "350": {"color": [255, 255, 0], "pixels": 4},
    "425": {"color": [255, 0, 255], "pixels": 4},
    "572": {"color": [0, 255, 255], "pixels": 4},
    "750": {"color": [255, 255, 255], "pixels": 4}
  }
}
```

This creates a sequence with:
- Red for 0.63 seconds
- Blue for 1.44 seconds
- Green for 1.43 seconds
- Yellow for 0.75 seconds
- Magenta for 1.47 seconds
- Cyan for 1.78 seconds
- White for 2.50 seconds

## Summary

Creating JSON files for the PRG generator with non-integer durations involves:

1. Selecting an appropriate refresh rate for your timing precision
2. Converting all time points to time units based on that refresh rate
3. Using those time units as keys in your sequence dictionary
4. Setting the end time to the total duration in time units

By following these steps, you can create complex color sequences with precise timing for LTX juggling balls.