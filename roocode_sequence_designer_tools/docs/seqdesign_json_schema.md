# Designer-JSON (`.seqdesign.json`) Schema Documentation

## 1. Overview

The Designer-JSON format, using the `.seqdesign.json` file extension, is a high-level, human-readable, and Roocode-friendly way to define color sequences for LTX juggling balls. It describes sequences using abstract "effects" and timings in seconds, which are then compiled by `compile_seqdesign.py` into the more detailed PRG-JSON format (`.prg.json`) required by `prg_generator.py`.

## 2. File Extension

Files using this format should have the extension: `.seqdesign.json`

## 3. Top-Level Structure

A `.seqdesign.json` file is a JSON object with three main top-level keys:

*   `metadata`: An object containing global information about the sequence.
*   `effects_timeline`: An array of effect objects defining the sequence of visual changes.
*   `pattern_templates`: An optional array of pattern template objects that get expanded into concrete effects.

```json
{
  "metadata": { ... },
  "effects_timeline": [ ... ],
  "pattern_templates": [ ... ]
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
| `type`          | String       | Yes      | The type of effect to apply (e.g., "fade", "solid_color", "pulse_on_beat"). While the compiler is case-insensitive (e.g., handling "SolidColor" or "solidcolor"), the recommended convention is lowercase with underscores. This name must correspond to an effect definition in `tools_lookup.json`. |
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

Colors within effect `params` (and `metadata.default_base_color`) can be specified in several ways:
- As a direct RGB array: `[R, G, B]` (e.g., `[255, 255, 0]`)
- As a "Color Object" dictionary, which must have exactly one of the following keys:

| Format / Key | Type                             | Example                      | Description                                                    |
| :----------- | :------------------------------- | :--------------------------- | :------------------------------------------------------------- |
| `name`       | String                           | `{"name": "red"}`            | A common CSS color name (e.g., "red", "blue", "lightgreen"). |
| `hex`        | String (Hexadecimal color code)  | `{"hex": "#FF0000"}`         | A 3 or 6-digit hex color code, with or without leading `#`.  |
| `rgb` (dict) | Array[Integer, Integer, Integer] | `{"rgb": [255, 0, 0]}`       | An array of [Red, Green, Blue] values, each from 0 to 255, within a dictionary. |
| `hsv` (dict) | Array[Integer, Integer, Integer] | `{"hsv": [120, 100, 100]}`   | An array of [Hue, Saturation, Value]. Hue: 0-359, Saturation: 0-100, Value: 0-100, within a dictionary. |

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

## 9. Using Lyrics Timestamps in Sequence Designs

Lyrics timestamps extracted using the `align_lyrics.py` or other lyrics extraction tools can be incorporated into sequence designs to create effects that synchronize with specific words in a song.

### 9.1. Lyrics Timestamp Format

The lyrics extraction tools produce a JSON file with the following structure:

```json
{
  "song_title": "Song Title",
  "artist_name": "Artist Name",
  "raw_lyrics": "Full lyrics text...",
  "word_timestamps": [
    {
      "word": "first",
      "start": 10.2,
      "end": 10.5
    },
    {
      "word": "word",
      "start": 10.6,
      "end": 10.9
    },
    ...
  ]
}
```

### 9.2. Using Word Timestamps with `pulse_on_beat`

The `pulse_on_beat` effect can be used with custom timestamps from lyrics:

```json
{
  "id": "lyrics_pulse",
  "type": "pulse_on_beat",
  "description": "Pulse on specific lyrics",
  "timing": {
    "start_seconds": 0.0,
    "end_seconds": 180.0
  },
  "params": {
    "color": {"name": "red"},
    "beat_source": "custom_times: [10.2, 10.6, 15.3, 20.1]",
    "pulse_duration_seconds": 0.3
  }
}
```

The `beat_source` parameter accepts a string in the format `"custom_times: [t1, t2, t3, ...]"` where each `t` is a timestamp in seconds. These timestamps can be extracted from the `word_timestamps` array in the lyrics JSON file.

### 9.3. Using Word Timestamps with `snap_on_flash_off`

For highlighting specific words with a flash effect:

```json
{
  "id": "key_word_highlight",
  "type": "snap_on_flash_off",
  "description": "Flash on key lyrics",
  "timing": {
    "start_seconds": 10.2,  // Start time of the word
    "duration_seconds": 0.5  // Slightly longer than the word duration
  },
  "params": {
    "pre_base_color": {"rgb": [0, 0, 100]},
    "target_color": {"name": "white"},
    "post_base_color": {"rgb": [0, 0, 100]},
    "fade_out_duration": 0.4
  }
}
```

### 9.4. Creating Multiple Effects for Different Words

You can create multiple effects for different words or phrases:

```json
"effects_timeline": [
  {
    "id": "chorus_word_1",
    "type": "snap_on_flash_off",
    "timing": {
      "start_seconds": 60.5,  // Timestamp of first chorus word
      "duration_seconds": 0.4
    },
    "params": {
      "pre_base_color": {"name": "blue"},
      "target_color": {"name": "yellow"},
      "post_base_color": {"name": "blue"},
      "fade_out_duration": 0.3
    }
  },
  {
    "id": "chorus_word_2",
    "type": "snap_on_flash_off",
    "timing": {
      "start_seconds": 61.2,  // Timestamp of second chorus word
      "duration_seconds": 0.4
    },
    "params": {
      "pre_base_color": {"name": "blue"},
      "target_color": {"name": "yellow"},
      "post_base_color": {"name": "blue"},
      "fade_out_duration": 0.3
    }
  }
]
```

## 10. Relationship to `tools_lookup.json`

The `type` field in each Effect Object (e.g., `"fade"`, `"solid_color"`) directly corresponds to an effect definition in the `roocode_sequence_designer_tools/tools_lookup.json` file. This `tools_lookup.json` file catalogs available effects, their parameters, and how they should be used, acting as a schema and guide for both Roocode and `compile_seqdesign.py`.

## 11. Related File Types

The LTX Guru project uses several standardized file extensions for different types of data:

| File Type | Extension | Description |
|-----------|-----------|-------------|
| Sequence Design Files | `.seqdesign.json` | High-level sequence design files (this document) |
| PRG JSON Files | `.prg.json` | Compiled program files for LTX balls |
| Raw Song Lyrics | `.lyrics.txt` | Raw lyrics text files |
| Timestamped Song Lyrics | `.synced_lyrics.json` | Timestamped/aligned lyrics from tools like align_lyrics.py |
| Ball Color Change Sequences | `.ballseq.json` | Ball-specific color sequences |
| Audio Analysis Reports | `.analysis_report.json` | Audio analysis data |
| Beat Patterns | `.beatpattern.json` | Beat-synchronized patterns |
| Section Themes | `.sectiontheme.json` | Section-based color themes |

## 12. Pattern Templates

Pattern templates are high-level, parameterized meta-effects that get expanded into multiple concrete effects during compilation. They provide a way to encapsulate common, complex temporal relationships and behaviors into reusable, configurable units.

### 12.1. Pattern Templates Array

The optional `pattern_templates` array contains pattern template objects that define high-level patterns like "WarningThenEvent" or "LyricHighlight". These patterns are expanded into concrete effects before compilation.

```json
{
  "metadata": { ... },
  "effects_timeline": [ ... ],
  "pattern_templates": [
    {
      "id": "chorus_warning_pattern",
      "pattern_type": "WarningThenEvent",
      "description": "Flash warning before chorus words",
      "params": { ... }
    }
  ]
}
```

### 12.2. Pattern Template Object Structure

Each pattern template object has the following structure:

| Key             | Type         | Required | Description                                                                                                                                                                                          |
| :-------------- | :----------- | :------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`            | String       | Yes      | A unique identifier for this pattern template instance (e.g., "chorus_warning", "verse_highlights").                                                                                                |
| `pattern_type`  | String       | Yes      | The type of pattern template (e.g., "WarningThenEvent", "LyricHighlight", "BeatSync").                                                                                                              |
| `description`   | String       | No       | An optional human-readable description of what this pattern template does.                                                                                                                          |
| `params`        | Object       | Yes      | An object containing parameters specific to the pattern type. The structure varies based on the pattern type.                                                                                       |

### 12.3. WarningThenEvent Pattern

Creates a warning effect before a main event, triggered by lyrics, beats, or custom times.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `trigger_type` | String | Yes | - | Type of trigger: "lyric", "custom_times", or "beat_number" |
| `trigger_lyric` | String | Conditional | - | Word to trigger on (required if trigger_type is "lyric") |
| `custom_times` | Array | Conditional | - | Array of timestamps in seconds (required if trigger_type is "custom_times") |
| `warning_offset_seconds` | Float | No | -1.0 | Time offset for warning before main event (negative means before) |
| `event_definition` | Object | Yes | - | Definition of the main event effect (standard effect object) |
| `warning_definition` | Object | Yes | - | Definition of the warning effect (standard effect object) |
| `target_ball_selection_strategy` | String | No | "round_robin" | Strategy for selecting target balls: "round_robin", "ball_1", "ball_2", "ball_3", "ball_4", "random" |
| `case_sensitive` | Boolean | No | false | Whether lyric matching is case sensitive |

**Example:**

```json
{
  "id": "love_word_warning",
  "pattern_type": "WarningThenEvent",
  "description": "Flash white warning 0.5s before 'love' words turn red",
  "params": {
    "trigger_type": "lyric",
    "trigger_lyric": "love",
    "warning_offset_seconds": -0.5,
    "target_ball_selection_strategy": "round_robin",
    "event_definition": {
      "type": "solid_color",
      "params": {
        "color": {"name": "red"},
        "duration_seconds": 0.3
      }
    },
    "warning_definition": {
      "type": "solid_color",
      "params": {
        "color": {"name": "white"},
        "duration_seconds": 0.2
      }
    }
  }
}
```

### 12.4. LyricHighlight Pattern

Highlights specific words or phrases in lyrics with visual effects.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target_words` | Array | Yes | - | Array of words to highlight |
| `effect_definition` | Object | Yes | - | Definition of the highlight effect (standard effect object) |
| `target_ball_selection_strategy` | String | No | "round_robin" | Strategy for selecting target balls |
| `case_sensitive` | Boolean | No | false | Whether word matching is case sensitive |

**Example:**

```json
{
  "id": "key_words_highlight",
  "pattern_type": "LyricHighlight",
  "description": "Highlight key emotional words",
  "params": {
    "target_words": ["love", "heart", "soul", "dream"],
    "target_ball_selection_strategy": "round_robin",
    "effect_definition": {
      "type": "snap_on_flash_off",
      "params": {
        "pre_base_color": {"name": "blue"},
        "target_color": {"name": "yellow"},
        "post_base_color": {"name": "blue"},
        "fade_out_duration": 0.4,
        "duration_seconds": 0.6
      }
    }
  }
}
```

### 12.5. BeatSync Pattern

Synchronizes effects with audio beats within a specified time window.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `beat_type` | String | No | "all_beats" | Type of beats to sync with: "all_beats" or "downbeats" |
| `effect_definition` | Object | Yes | - | Definition of the beat-synchronized effect |
| `target_ball_selection_strategy` | String | No | "round_robin" | Strategy for selecting target balls |
| `time_window` | Object | No | - | Time window with start_seconds and end_seconds |

**Example:**

```json
{
  "id": "chorus_beat_sync",
  "pattern_type": "BeatSync",
  "description": "Pulse on every beat during chorus",
  "params": {
    "beat_type": "all_beats",
    "target_ball_selection_strategy": "round_robin",
    "time_window": {
      "start_seconds": 60.0,
      "end_seconds": 120.0
    },
    "effect_definition": {
      "type": "pulse_on_beat",
      "params": {
        "color": {"name": "cyan"},
        "pulse_duration_seconds": 0.1,
        "duration_seconds": 0.1
      }
    }
  }
}
```

### 12.6. Pattern Template Processing

Pattern templates are processed by the [`pattern_templates.py`](../pattern_templates.py) tool before compilation:

1. **Expansion Phase**: Pattern templates are expanded into concrete effect objects based on their parameters and external data (lyrics, audio analysis).

2. **Integration Phase**: The generated effects are added to the `effects_timeline` array.

3. **Compilation Phase**: The standard compilation process handles the expanded effects normally.

**Usage:**

```bash
python -m roocode_sequence_designer_tools.pattern_templates input.seqdesign.json output.seqdesign.json --lyrics-file lyrics.synced_lyrics.json
```

### 12.7. Ball Selection Strategies

Pattern templates support various ball selection strategies:

- **`round_robin`**: Cycles through balls 1, 2, 3, 4 for each trigger occurrence
- **`ball_1`**, **`ball_2`**, **`ball_3`**, **`ball_4`**: Always uses the specified ball
- **`random`**: Pseudo-random ball selection (currently uses modulo for deterministic results)

### 12.8. Complete Example with Pattern Templates

```json
{
  "metadata": {
    "title": "Song with Pattern Templates",
    "audio_file_path": "song.mp3",
    "total_duration_seconds": 180.0,
    "target_prg_refresh_rate": 100,
    "default_pixels": 4,
    "default_base_color": {"name": "black"}
  },
  "effects_timeline": [
    {
      "id": "base_color",
      "type": "solid_color",
      "timing": {
        "start_seconds": 0.0,
        "end_seconds": 180.0
      },
      "params": {
        "color": {"rgb": [20, 20, 50]}
      }
    }
  ],
  "pattern_templates": [
    {
      "id": "chorus_warnings",
      "pattern_type": "WarningThenEvent",
      "description": "Warning flashes before chorus words",
      "params": {
        "trigger_type": "lyric",
        "trigger_lyric": "chorus",
        "warning_offset_seconds": -0.8,
        "target_ball_selection_strategy": "round_robin",
        "event_definition": {
          "type": "solid_color",
          "params": {
            "color": {"name": "red"},
            "duration_seconds": 0.5
          }
        },
        "warning_definition": {
          "type": "solid_color",
          "params": {
            "color": {"name": "yellow"},
            "duration_seconds": 0.3
          }
        }
      }
    },
    {
      "id": "emotional_highlights",
      "pattern_type": "LyricHighlight",
      "description": "Highlight emotional words",
      "params": {
        "target_words": ["love", "heart", "dream", "hope"],
        "effect_definition": {
          "type": "snap_on_flash_off",
          "params": {
            "pre_base_color": {"rgb": [20, 20, 50]},
            "target_color": {"name": "white"},
            "post_base_color": {"rgb": [20, 20, 50]},
            "fade_out_duration": 1.0,
            "duration_seconds": 1.2
          }
        }
      }
    }
  ]
}
```

---
This documentation should provide a solid reference for understanding and creating `.seqdesign.json` files and related file types in the LTX Guru ecosystem.