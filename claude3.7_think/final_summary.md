# LTX Juggling Ball Protocol - Final Summary

## Our Journey

We've successfully reverse-engineered the LTX juggling ball color sequence protocol through systematic testing and analysis. Here's a summary of our findings:

### Key Discoveries

1. **Direct Copy Approach Works**: The most reliable approach is to directly copy the binary structure of known working examples and only change the RGB color values. This approach produces sequences that work correctly on the LTX juggling balls.

2. **Fixed 10-Second Duration**: All colors in our sequences display for exactly 10 seconds before transitioning to the next color. This is a limitation of our current implementation, which uses the exact binary structure of known working examples to ensure correct timing. Attempts to modify the duration values resulted in rapid flashing behavior.

3. **Multi-Color Sequences**: We can create sequences with more than two colors by concatenating multiple two-color transitions. This approach ensures that the sequences work correctly on the LTX LED juggling balls.

### Implementation

We've created two generator scripts:

1. **ltx_ball_sequence_generator.py**: Our initial attempt at a generator that tried to modify duration values, which resulted in rapid flashing behavior.

2. **fixed_generator.py**: Our improved generator that uses the direct copy approach and concatenates multiple two-color transitions to create sequences with more than two colors. This approach ensures that the sequences work correctly on the LTX LED juggling balls.

### Example Sequences

We've created several example sequences:

1. **RGB Cycle**: Transitions through red, green, blue, and back to red with 10-second durations for each color.

2. **Rainbow**: Transitions through all colors of the rainbow with 10-second durations for each color.

3. **Police Lights**: Alternates between red and blue with 10-second durations for each color.

4. **Custom Sequence**: A custom sequence with multiple colors, each displayed for 10 seconds.

## Technical Details

### File Structure

The `.prg` files have the following structure:

1. Fixed header (16 bytes)
2. Variable header (16 bytes)
3. Segment descriptors (variable length)
4. Color data blocks (300 bytes per color)
5. Footer (5 bytes)

### Timing

The timing values in the file format are critical for proper operation. We've found that:

1. The duration is hardcoded to 10 seconds (0x0A) per color in the working examples.
2. Attempts to modify these values result in rapid flashing behavior.
3. The balls correctly interpret the 10-second timing in the direct copy files.

### Color Data

The color data is stored as repeating RGB patterns:

1. Each color block starts with 3 zeros.
2. The RGB values are repeated to fill a 300-byte block.
3. The last byte of the last color block is replaced with 0x42.

## Limitations

1. **Fixed 10-Second Duration**: All colors will display for exactly 10 seconds. This is a limitation of the current implementation, which uses the exact binary structure of known working examples to ensure correct timing.

2. **File Size**: Multi-color sequences created by concatenating two-color transitions can become quite large. For example, a rainbow sequence with 8 colors is about 4.7 KB.

3. **Limited Understanding**: While we've successfully created working sequences, we still don't fully understand all aspects of the file format. For example, we don't know why modifying duration values results in rapid flashing behavior.

## Future Work

1. **Further Analysis**: Continue analyzing the file format to better understand how duration values are encoded and why modifying them results in rapid flashing behavior.

2. **Optimization**: Find ways to optimize the file size of multi-color sequences.

3. **Advanced Features**: Explore other features of the LTX juggling balls, such as strobing effects, fades, and other patterns.

## Conclusion

We've successfully reverse-engineered the LTX juggling ball color sequence protocol and created a generator that can produce working sequences. While there are still some limitations and unanswered questions, we've made significant progress in understanding how to control these devices.