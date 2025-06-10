# Generate SMPROJ from PRG Tool

## Overview
The `generate_smproj_from_prg.py` tool creates properly formatted Sequence Maker project files (`.smproj`) from compiled PRG JSON files (`.prg.json`). This tool is essential for creating project files that can be opened in Sequence Maker with visible color segments.

## Purpose
When creating multi-ball sequences, the compilation process generates separate `.prg.json` files for each ball. However, Sequence Maker requires a `.smproj` file with properly structured timeline segments to display the colors correctly. This tool bridges that gap by converting the PRG data back into the segment format expected by Sequence Maker.

## Usage

```bash
python roocode_sequence_designer_tools/generate_smproj_from_prg.py \
    ball1.prg.json ball2.prg.json ball3.prg.json \
    --project-name "My Project" \
    --output project.smproj
```

### Arguments
- **prg_files**: One or more paths to `.prg.json` files (one per ball)
- **--project-name**: Name for the project (required)
- **--output**: Output path for the `.smproj` file (required)

## Example
```bash
cd sequence_projects/my_sequence/
python ../../roocode_sequence_designer_tools/generate_smproj_from_prg.py \
    my_sequence_Ball_1.prg.json \
    my_sequence_Ball_2.prg.json \
    my_sequence_Ball_3.prg.json \
    --project-name "My Sequence" \
    --output my_sequence.smproj
```

## Output Structure
The tool generates a complete `.smproj` file with:
- **Metadata**: Project name, creation time, version info
- **Settings**: Refresh rate, duration, default pixels from PRG data
- **Timelines**: One timeline per ball with properly formatted segments
- **Segments**: Each segment has `startTime`, `endTime`, `color`, `pixels`, and `segment_type`

## Segment Conversion
The tool converts PRG sequence entries into timeline segments by:
1. Sorting PRG entries by time unit
2. Converting time units to seconds using refresh rate
3. Creating segments when colors change
4. Properly formatting colors as RGB arrays
5. Setting appropriate segment types (currently "solid")

## Integration with Workflow
This tool is typically used after:
1. Creating a `.seqdesign.json` file
2. Compiling it with `compile_seqdesign.py` to generate `.prg.json` files
3. Splitting multi-ball sequences into per-ball `.prg.json` files

The resulting `.smproj` file can be opened directly in Sequence Maker and will display the correct colors and timing for each ball.

## Technical Notes
- Automatically handles different refresh rates from PRG data
- Supports up to 3 balls (pads with empty timelines if fewer provided)
- Preserves exact timing from the original PRG files
- Creates proper segment boundaries for color changes

Created: 2025-06-10 16:27 UTC+7