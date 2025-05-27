# Sequence Maker Changes

## Features Added

### 1. Sequence Length Input

- Added a sequence length text input field to the audio widget
- The sequence length automatically updates when an audio file is loaded, matching the audio duration
- The sequence length is used to determine the total duration of the project

### 2. Key Press Color Block Creation

- Added key press handling to create color blocks on timelines
- When a mapped key is pressed, a new color block is created on the appropriate timeline
- The color block extends from the current marker position to:
  - The next color block on the timeline (if one exists after the current position)
  - The end of the timeline (if no color block exists after the current position)

### 3. Position Marker Movement Without Audio

- Modified the play button to move the current position marker even when no audio is loaded
- The marker moves at a real-time pace from the current position to the end of the sequence

### 4. Bug Fixes

- Fixed a crash that occurred when pressing keys to add color blocks
  - The issue was related to the QLinearGradient constructor in the timeline widget
- Fixed an issue where color blocks were not starting at the current position marker
  - Modified the key press handler to use the timeline's add_color_at_time method directly
  - This ensures the color block starts exactly at the current position marker and extends to the next color block or the end of the timeline

## Implementation Details

### Sequence Length Input

- Added a text input field and label to the audio widget UI
- Connected the input field to update the project's total_duration property
- Modified the audio loading code to update the sequence length when an audio file is loaded

### Key Press Color Block Creation

- Added a keyPressEvent handler to the MainWindow class
- The handler checks if the pressed key is mapped to a color and timeline
- If mapped, it adds a color block at the current position on the appropriate timeline
- Modified the Timeline.add_color_at_time method to make the color block extend to the end of the timeline

### Position Marker Movement

- Modified the AudioManager.play method to work even when no audio is loaded
- Added a position update worker thread that updates the position marker in real-time
- The marker moves from the current position to the end of the sequence

## Usage

1. Load an audio file to automatically set the sequence length (optional)
2. Enter the desired sequence length in the text input field
3. Press the play button to start the position marker moving
4. Position the marker where you want to add a color (or let it move automatically)
5. Press a key mapped to a color to create a color block
   - The color block will extend from the current marker to the next color block or the end of the timeline
6. Continue adding colors by positioning the marker and pressing keys

## Key Mappings

The default key mappings are:
- Top row (q, w, e, r, t, y, u, i, o) - Colors for Ball 1
- Middle row (a, s, d, f, g, h, j, k, l) - Colors for Ball 2
- Bottom row (z, x, c, v, b, n, m, ,, .) - Colors for Ball 3
- Number row (1-9) - Colors for all balls