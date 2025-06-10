# Alternating Flash 3 Balls Sequence

## Overview
This project contains a 3-ball alternating flash sequence where each ball takes turns flashing on for 0.1 seconds with a specific color pattern.

## Timing Pattern
- **Ball 1 (Red)**: Flashes at 0.25s, 1.0s, 1.75s, 2.5s, etc. (every 0.75s starting at 0.25s)
- **Ball 2 (Blue)**: Flashes at 0.5s, 1.25s, 2.0s, 2.75s, etc. (every 0.75s starting at 0.5s)  
- **Ball 3 (Green)**: Flashes at 0.75s, 1.5s, 2.25s, 3.0s, etc. (every 0.75s starting at 0.75s)

Each flash lasts exactly 0.1 seconds, and the sequence continues for 2 minutes (120 seconds total).

## Files Generated

### Core Sequence Files
- **`alternating_flash_3balls.seqdesign.json`** - High-level sequence design file (479 flash effects)
- **`alternating_flash_3balls_fixed.smproj`** - Sequence Maker project file (openable by Sequence Maker) ⭐ **USE THIS FILE**
- **`alternating_flash_3balls.smproj`** - ❌ Initial version with empty timelines (do not use)

### Compiled Program Files
- **`alternating_flash_3balls.prg.json`** - Combined sequence for all balls (959 segments)
- **`alternating_flash_3balls_Ball_1.prg.json`** - Red ball sequence (640 entries)
- **`alternating_flash_3balls_Ball_2.prg.json`** - Blue ball sequence (640 entries)
- **`alternating_flash_3balls_Ball_3.prg.json`** - Green ball sequence (639 entries)

### Generation Scripts
- **`generate_flash_sequence.py`** - Script that generated the .seqdesign.json file
- **`split_to_per_ball_prg.py`** - Script that split the combined .prg.json into per-ball files

## Technical Details
- **Refresh Rate**: 100 Hz (0.01 second precision)
- **Default Pixels**: 4 pixels per ball
- **Total Duration**: 120 seconds (2 minutes)
- **Color Format**: RGB
- **Ball Colors**: 
  - Ball 1: Red (255, 0, 0)
  - Ball 2: Blue (0, 0, 255)
  - Ball 3: Green (0, 255, 0)

## Usage
The `.smproj` file can be opened directly in Sequence Maker. The individual `.prg.json` files can be uploaded to their respective LTX balls for synchronized playback.

## Pattern Verification
The timing has been verified to match the exact specifications:
- Ball 1 red flash: 0.25-0.35s, 1.0-1.1s, 1.75-1.85s...
- Ball 2 blue flash: 0.5-0.6s, 1.25-1.35s, 2.0-2.1s...
- Ball 3 green flash: 0.75-0.85s, 1.5-1.6s, 2.25-2.35s...

Created: 2025-06-10 16:24 UTC+7