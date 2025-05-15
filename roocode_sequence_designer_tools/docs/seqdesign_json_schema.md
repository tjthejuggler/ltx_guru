# Designer-JSON (`.seqdesign.json`) Schema Documentation

## 1. Overview

The Designer-JSON format, using the `.seqdesign.json` file extension, is a high-level, human-readable, and Roocode-friendly way to define color sequences for LTX juggling balls. It describes sequences using abstract "effects" and timings in seconds, which are then compiled by `compile_seqdesign.py` into the more detailed PRG-JSON format (`.prg.json`) required by `prg_generator.py`.

## 2. File Extension

Files using this format should have the extension: `.seqdesign.json`

## 3. Top-Level Structure

A `.seqdesign.json` file is a JSON object with two main top-level keys:

*   `metadata`: An object containing global information about the sequence.
*   `effects_timeline`: An array of effect objects defining the sequence of visual changes.

```json
{
  "metadata": { ... },
  "effects_timeline": [ ... ]
}
```

## 4. `metadata` Object

The `metadata` object contains settings and information that apply to the entire sequence.

| Key                         | Type          | Required | Default (if not provided) | Description                                                                                                                                                              |
| :-------------------------- | :------------ | :------- | :------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `title`                     | String        | No       | `null`                    | A descriptive title for the sequence.                                                                                                                                    |
| `audio_file_path`           | String        | No       | `null`                    | Relative path to the audio file (e.g., "audio.mp3"). Path is relative to the parent directory of the `.seqdesign.json` file (i.e., the `[SequenceName]` directory).      |
| `total_duration_seconds`    | Number        | Yes*     | (Derived)                 | Total duration of the sequence in seconds. *Roocode should prompt for this. If still missing, `compile_seqdesign.py` will derive it from the end of the last effect.        |
| `target_prg_refresh_rate` | Integer       | Yes      | `100`                     | The desired refresh rate for the final PRG-JSON (e.g., 100 means 0.01s precision for time units).                                                                        |
| `default_pixels`            | Integer (1-4) | Yes      | `4`                       | The default number of pixels active on the LTX ball for effects that don't specify it.                                                                                   |
| `default_base_color`        | Color Object  | No       | `{"name": "black"}`       | The background color for any time periods not covered by an effect. See [Color Object Specification](#6-color-object-specification).                                         |

**Example `metadata`:**

```json
"metadata": {
  "title": "My Awesome Juggling Sequence",
  "audio_file_path": "my_track.mp3",
  "total_duration_seconds": 180.5,
  "target_prg_refresh_rate": 100,
  "default_pixels": 4,
  "default_base_color": {"rgb": [10, 0, 0]} // Dim red background
}
```

## 5. `effects_timeline` Array

The `effects_timeline` is an ordered array of "Effect Objects." The order is crucial as effects are applied sequentially, and later effects can override earlier ones for overlapping time periods.

Each **Effect Object** in the array has the following structure:

| Key             | Type         | Required | Description                                                                                                                                                                                          |
| :-------------- | :----------- | :------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`            | String       | Yes      | A unique identifier string for this specific effect instance within the timeline (e.g., "intro_fade_1", "chorus_pulse_main"). Chosen by Roocode or the user.                                        |
| `type`          | String       | Yes      | The type of effect to apply (e.g., "fade", "solid_color", "pulse_on_beat"). This name must correspond to an effect definition in the `tools_lookup.json` file.                                       |
| `description`   | String       | No       | An optional human-readable description of what this effect instance is intended to do.                                                                                                               |
| `timing`        | Timing Object| Yes      | An object defining the start and duration/end time of this effect. See [Timing Object Specification](#7-timing-object-specification).                                                                 |
| `params`        | Object       | Yes      | An object containing parameters specific to the `type` of effect. The structure of `params` varies based on the effect `type` (defined in `tools_lookup.json`). See examples below.                  |

**Example Effect Objects:**

```json
{
  "id": "intro_fade",
  "type": "fade",
  "description": "Initial fade in from black to blue",
  "timing": {
    "start_seconds": 0.0,
    "end_seconds": 5.0
  },
  "params": {
    "color_start": {"name": "black"},
    "color_end": {"rgb": [0, 0, 255]},
    "steps_per_second": 20
  }
},
{
  "id": "verse1_pulse",
  "type": "pulse_on_beat",
  "timing": {
    "start_seconds": 5.0,
    "duration_seconds": 25.0
  },
  "params": {
    "color": {"name": "yellow"},
    "beat_source": "all_beats",
    "pulse_duration_seconds": 0.15
  }
}
```

### 5.1. Layering and Override Logic

Effects in the `effects_timeline` are processed in order. If an effect's time range (`timing`) overlaps with a previous effect's time range, the later effect will take precedence ("paint over") the earlier effect for the duration of the overlap. The `compile_seqdesign.py` script handles the merging of these layers to produce a final, flat sequence of color changes.

## 6. Color Object Specification

Colors within effect `params` (and `metadata.default_base_color`) are specified using a "Color Object." This object must have exactly one of the following keys:

| Key      | Type                             | Example                      | Description                                                    |
| :------- | :------------------------------- | :--------------------------- | :------------------------------------------------------------- |
| `name`   | String                           | `{"name": "red"}`            | A common CSS color name (e.g., "red", "blue", "lightgreen"). |
| `hex`    | String (Hexadecimal color code)  | `{"hex": "#FF0000"}`         | A 3 or 6-digit hex color code, with leading `#`.             |
| `rgb`    | Array[Integer, Integer, Integer] | `{"rgb": [255, 0, 0]}`       | An array of [Red, Green, Blue] values, each from 0 to 255.     |
| `hsv`    | Array[Integer, Integer, Integer] | `{"hsv": [120, 100, 100]}`   | An array of [Hue, Saturation, Value]. Hue: 0-359, Saturation: 0-100, Value: 0-100. |

**Example Usage in `params`:**
```json
"params": {
  "color": {"hsv": [240, 75, 80]} // A specific shade of blue
}
```

## 7. Timing Object Specification

The `timing` object within each effect defines its temporal boundaries.

| Key                | Type   | Required | Description                                                                                                                                                   |
| :----------------- | :----- | :------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `start_seconds`    | Number | Yes      | The start time of the effect, in seconds, from the beginning of the sequence.                                                                                 |
| `end_seconds`      | Number | No*      | The end time of the effect, in seconds. *Required if `duration_seconds` is not provided.                                                                      |
| `duration_seconds` | Number | No*      | The duration of the effect, in seconds. *Required if `end_seconds` is not provided.                                                                           |

**Rules:**
*   Must contain `start_seconds`.
*   Must contain *either* `end_seconds` OR `duration_seconds`.
*   If both `end_seconds` and `duration_seconds` are provided:
    *   If they are consistent (`start_seconds` + `duration_seconds` == `end_seconds`), it's fine.
    *   If they are inconsistent, `compile_seqdesign.py` may prioritize `end_seconds` or issue a warning/error. It is recommended to provide only one.
*   `compile_seqdesign.py` will derive the missing field (either `end_seconds` or `duration_seconds`).

**Example `timing` Objects:**

```json
// Using start_seconds and end_seconds
"timing": {
  "start_seconds": 10.5,
  "end_seconds": 15.0
}

// Using start_seconds and duration_seconds
"timing": {
  "start_seconds": 15.0,
  "duration_seconds": 5.25
}
```

## 8. Complete Example `.seqdesign.json`

```json
{
  "metadata": {
    "title": "Demo Sequence with Fade and Pulse",
    "audio_file_path": "demo_audio.mp3",
    "total_duration_seconds": 30.0,
    "target_prg_refresh_rate": 100,
    "default_pixels": 4,
    "default_base_color": {"name": "black"}
  },
  "effects_timeline": [
    {
      "id": "initial_fade_in",
      "type": "fade",
      "description": "Fade from black to deep purple at the start.",
      "timing": {
        "start_seconds": 0.0,
        "end_seconds": 3.0
      },
      "params": {
        "color_start": {"name": "black"},
        "color_end": {"rgb": [75, 0, 130]},
        "steps_per_second": 25
      }
    },
    {
      "id": "main_beat_pulse",
      "type": "pulse_on_beat",
      "description": "Pulse bright cyan on every beat for the main section.",
      "timing": {
        "start_seconds": 3.0,
        "duration_seconds": 20.0
      },
      "params": {
        "color": {"hex": "#00FFFF"},
        "beat_source": "all_beats",
        "pulse_duration_seconds": 0.1
      }
    },
    {
      "id": "solid_highlight",
      "type": "solid_color",
      "description": "A short solid gold highlight.",
      "timing": {
        "start_seconds": 10.0,
        "end_seconds": 11.5
      },
      "params": {
        "color": {"name": "gold"}
      }
    },
    {
      "id": "outro_fade_out",
      "type": "fade",
      "description": "Fade from deep purple back to black at the end.",
      "timing": {
        "start_seconds": 23.0,
        "end_seconds": 30.0
      },
      "params": {
        "color_start": {"rgb": [75, 0, 130]},
        "color_end": {"name": "black"}
      }
    },
    {
      "id": "lyric_highlight",
      "type": "snap_on_flash_off",
      "description": "Quick flash on a key lyric word that fades back smoothly.",
      "timing": {
        "start_seconds": 15.0,
        "duration_seconds": 2.5
      },
      "params": {
        "pre_base_color": {"rgb": [75, 0, 130]},
        "target_color": {"name": "white"},
        "post_base_color": {"rgb": [75, 0, 130]},
        "fade_out_duration": 2.0
      }
    }
  ]
}
```

## 9. Relationship to `tools_lookup.json`

The `type` field in each Effect Object (e.g., `"fade"`, `"solid_color"`) directly corresponds to an effect definition in the `roocode_sequence_designer_tools/tools_lookup.json` file. This `tools_lookup.json` file catalogs available effects, their parameters, and how they should be used, acting as a schema and guide for both Roocode and `compile_seqdesign.py`.

## 10. Related File Types

The LTX Guru project uses several standardized file extensions for different types of data:

| File Type | Extension | Description |
|-----------|-----------|-------------|
| Sequence Design Files | `.seqdesign.json` | High-level sequence design files (this document) |
| PRG JSON Files | `.prg.json` | Compiled program files for LTX balls |
| Raw Song Lyrics | `.lyrics.txt` | Raw lyrics text files |
| Timestamped Song Lyrics | `.synced_lyrics.json` | Timestamped/aligned lyrics |
| Ball Color Change Sequences | `.ballseq.json` | Ball-specific color sequences |
| Audio Analysis Reports | `.analysis_report.json` | Audio analysis data |
| Beat Patterns | `.beatpattern.json` | Beat-synchronized patterns |
| Section Themes | `.sectiontheme.json` | Section-based color themes |

---
This documentation should provide a solid reference for understanding and creating `.seqdesign.json` files and related file types in the LTX Guru ecosystem.