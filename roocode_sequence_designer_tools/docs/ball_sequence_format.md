# Ball Sequence Format (`.ball.json`)

The Ball Sequence format (`.ball.json`) is a standardized format for defining color sequences for a single LTX ball. It provides a simple, direct way to define color changes over time.

## File Structure

A `.ball.json` file is a JSON object with two main sections:

* `metadata`: Contains information about the sequence
* `segments`: An array of color segments that define the sequence

```json
{
  "metadata": {
    "name": "Ball Sequence Name",
    "default_pixels": 4,
    "refresh_rate": 50,
    "total_duration": 134.95,
    "audio_file": "path/to/audio.mp3"
  },
  "segments": [
    {
      "start_time": 0.0,
      "end_time": 10.7,
      "color": [0, 0, 0],
      "pixels": 4
    },
    {
      "start_time": 10.7,
      "end_time": 11.03,
      "color": [0, 0, 255],
      "pixels": 4
    }
    // Additional segments...
  ]
}
```

## Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Name of the sequence |
| `default_pixels` | Integer | Default number of pixels (1-4) |
| `refresh_rate` | Integer | Refresh rate in Hz (typically 50) |
| `total_duration` | Float | Total duration in seconds |
| `audio_file` | String | Path to the audio file (relative to the sequence directory) |

## Segment Fields

| Field | Type | Description |
|-------|------|-------------|
| `start_time` | Float | Start time in seconds |
| `end_time` | Float | End time in seconds |
| `color` | Array[3] | RGB color values [r, g, b] (0-255) |
| `pixels` | Integer | Number of pixels (1-4) |

## Converting to Other Formats

Ball Sequence files can be converted to other formats:

* To convert to Sequence Design format (`.seqdesign.json`), use the `convert_ball_to_seqdesign.py` script
* To convert to PRG format (`.prg.json`), use the `compile_seqdesign.py` script after converting to `.seqdesign.json`

## Importing into Sequence Maker

Ball Sequence files can be imported directly into Sequence Maker using the "Import Ball Sequence" option in the File menu.