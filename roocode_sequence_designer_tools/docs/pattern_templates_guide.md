# Pattern Templates Guide

## Overview

Pattern Templates are a powerful feature of the Sequence Designer that allows you to define high-level, parameterized "meta-effects" that get expanded into multiple concrete effects during compilation. This approach provides a way to encapsulate common, complex temporal relationships and behaviors into reusable, configurable units.

## Concept

Instead of manually creating dozens of individual effects for repetitive patterns (like flashing on every occurrence of a word, or warning effects before main events), Pattern Templates let you define the pattern once with parameters, and the system automatically generates all the individual effects based on triggers from lyrics, audio analysis, or custom timing.

## Key Benefits

1. **Efficiency**: Define complex patterns once instead of creating many individual effects
2. **Consistency**: Ensures all instances of a pattern use the same timing and visual parameters
3. **Maintainability**: Easy to modify pattern behavior by changing parameters in one place
4. **Intelligent Ball Selection**: Automatic ball cycling and selection strategies
5. **Data Integration**: Seamless integration with lyrics timestamps and audio analysis

## Supported Pattern Types

### 1. WarningThenEvent

Creates a warning effect before a main event, triggered by lyrics, beats, or custom times.

**Use Cases:**
- Flash a warning color before key lyric words
- Build anticipation before musical events
- Create call-and-response visual patterns

**Key Features:**
- Configurable warning offset timing
- Multiple trigger types (lyrics, custom times, beats)
- Independent effect definitions for warning and main event
- Ball selection strategies

### 2. LyricHighlight

Highlights specific words or phrases in lyrics with visual effects.

**Use Cases:**
- Emphasize emotional words in songs
- Create thematic visual responses to lyrics
- Highlight recurring phrases or choruses

**Key Features:**
- Multiple word targeting
- Case-sensitive or insensitive matching
- Flexible effect definitions
- Automatic timestamp extraction from lyrics

### 3. BeatSync

Synchronizes effects with audio beats within a specified time window.

**Use Cases:**
- Create beat-synchronized light shows
- Emphasize downbeats or specific beat patterns
- Time-windowed beat effects for specific song sections

**Key Features:**
- All beats or downbeats targeting
- Time window constraints
- Audio analysis integration
- Rhythm-based ball cycling

## Ball Selection Strategies

Pattern Templates support intelligent ball selection strategies:

- **`round_robin`**: Cycles through balls 1, 2, 3, 4 for each trigger occurrence
- **`ball_1`**, **`ball_2`**, **`ball_3`**, **`ball_4`**: Always uses the specified ball
- **`random`**: Pseudo-random ball selection for varied patterns

## Workflow

### 1. Design Phase
Define your pattern templates in the `.seqdesign.json` file under the `pattern_templates` array.

### 2. Expansion Phase
Use the `pattern_templates.py` tool to expand templates into concrete effects:

```bash
python -m roocode_sequence_designer_tools.pattern_templates \
    input.seqdesign.json \
    expanded.seqdesign.json \
    --lyrics-file lyrics.synced_lyrics.json
```

### 3. Compilation Phase
Compile the expanded file normally:

```bash
python -m roocode_sequence_designer_tools.compile_seqdesign \
    expanded.seqdesign.json \
    output.prg.json
```

## Example: WarningThenEvent Pattern

```json
{
  "pattern_templates": [
    {
      "id": "love_word_warnings",
      "pattern_type": "WarningThenEvent",
      "description": "Yellow warning 0.5s before 'love' words flash red",
      "params": {
        "trigger_type": "lyric",
        "trigger_lyric": "love",
        "warning_offset_seconds": -0.5,
        "target_ball_selection_strategy": "round_robin",
        "case_sensitive": false,
        "event_definition": {
          "type": "solid_color",
          "params": {
            "color": {"name": "red"},
            "duration_seconds": 0.4
          }
        },
        "warning_definition": {
          "type": "solid_color",
          "params": {
            "color": {"name": "yellow"},
            "duration_seconds": 0.2
          }
        }
      }
    }
  ]
}
```

**What this creates:**
If "love" appears at timestamps 45.2s, 67.8s, and 123.4s in the lyrics, this pattern will generate:

1. Warning effect at 44.7s on ball 1 (yellow, 0.2s duration)
2. Main effect at 45.2s on ball 1 (red, 0.4s duration)
3. Warning effect at 67.3s on ball 2 (yellow, 0.2s duration)
4. Main effect at 67.8s on ball 2 (red, 0.4s duration)
5. Warning effect at 122.9s on ball 3 (yellow, 0.2s duration)
6. Main effect at 123.4s on ball 3 (red, 0.4s duration)

## Example: LyricHighlight Pattern

```json
{
  "id": "emotional_words",
  "pattern_type": "LyricHighlight",
  "description": "Highlight emotional words with white flash",
  "params": {
    "target_words": ["love", "heart", "soul", "dream", "hope"],
    "target_ball_selection_strategy": "round_robin",
    "case_sensitive": false,
    "effect_definition": {
      "type": "snap_on_flash_off",
      "params": {
        "pre_base_color": {"rgb": [20, 20, 50]},
        "target_color": {"name": "white"},
        "post_base_color": {"rgb": [20, 20, 50]},
        "fade_out_duration": 0.8,
        "duration_seconds": 1.0
      }
    }
  }
}
```

## Example: BeatSync Pattern

```json
{
  "id": "chorus_beats",
  "pattern_type": "BeatSync",
  "description": "Pulse cyan on every beat during chorus",
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

## Advanced Features

### State-Aware Effects

Pattern Templates can create effects that are aware of the current state of balls. For example, a "brighten_existing" warning effect could brighten whatever color is currently active on a ball rather than using a fixed color.

### Complex Trigger Logic

Future enhancements could include:
- Multiple trigger conditions (AND/OR logic)
- Trigger filtering based on context
- Dynamic parameter adjustment based on audio features

### Pattern Composition

Patterns can be combined and layered to create complex visual narratives that respond to multiple aspects of the music simultaneously.

## Best Practices

1. **Start Simple**: Begin with basic patterns and gradually add complexity
2. **Test Incrementally**: Expand and test patterns with small datasets first
3. **Use Descriptive IDs**: Make pattern IDs descriptive for easier debugging
4. **Consider Ball Distribution**: Choose ball selection strategies that create visually pleasing distributions
5. **Timing Considerations**: Account for human perception when setting warning offsets and effect durations
6. **Lyrics Quality**: Ensure lyrics files are accurately timestamped for best results

## Troubleshooting

### Common Issues

1. **No Effects Generated**: Check that lyrics file exists and contains the target words
2. **Timing Issues**: Verify warning offsets don't create negative timestamps
3. **Ball Conflicts**: Consider how multiple patterns might compete for the same balls
4. **Performance**: Large numbers of generated effects may impact compilation time

### Debugging Tips

1. Use the `--verbose` flag when available to see expansion details
2. Check the expanded `.seqdesign.json` file to verify generated effects
3. Test with simple patterns first before adding complexity
4. Validate lyrics timestamps independently

## Integration with Sequence Designer Mode

The Sequence Designer mode in the LTX Guru system is fully aware of Pattern Templates and can:

1. **Generate Patterns**: Create pattern templates from natural language descriptions
2. **Validate Parameters**: Check pattern parameters against available data
3. **Suggest Improvements**: Recommend optimizations and alternatives
4. **Handle Dependencies**: Automatically manage lyrics and audio analysis requirements

## Future Enhancements

Planned improvements to Pattern Templates include:

1. **Visual Preview**: GUI tools for previewing pattern effects
2. **Pattern Library**: Shared library of common patterns
3. **Advanced Triggers**: More sophisticated trigger conditions
4. **Real-time Adjustment**: Dynamic parameter modification during playback
5. **Machine Learning**: AI-assisted pattern optimization based on visual effectiveness

---

Pattern Templates represent a significant advancement in sequence design efficiency and capability, enabling creators to focus on high-level creative decisions while the system handles the detailed implementation.