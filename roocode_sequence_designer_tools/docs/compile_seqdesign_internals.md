# `compile_seqdesign.py` Internals

## 1. Introduction

The [`compile_seqdesign.py`](../compile_seqdesign.py) script is the core "compiler" of the Roocode Sequence Designer system. Its primary purpose is to translate a high-level sequence definition file, typically named with a `.seqdesign.json` extension, into a hardware-ready `.prg.json` file. This `.prg.json` file contains the precise, timed instructions that the Roocode hardware uses to control LED lighting effects.

## 2. Core Processing Steps (High-Level Flow)

The script executes the following main stages to perform the compilation:

1.  **Command-Line Argument Parsing:**
    *   The script begins by parsing command-line arguments using `argparse`.
    *   It expects the path to the input `.seqdesign.json` file and the desired path for the output `.prg.json` file.
    *   An optional `--audio-dir` argument can be provided to specify the base directory for resolving relative audio file paths referenced in the sequence design. If not provided, it defaults to the parent directory of the input file's location (e.g., the `[SequenceName]` directory).
    *   See lines [264-287 in `compile_seqdesign.py`](../compile_seqdesign.py:264-287).

2.  **Loading and Validating `.seqdesign.json` (Metadata Processing):**
    *   The input `.seqdesign.json` file is loaded using the [`load_seqdesign_json`](../compile_seqdesign.py:97) function.
    *   The script extracts and validates essential metadata from the `metadata` object within the JSON. This includes:
        *   `target_prg_refresh_rate`: The target refresh rate for the PRG hardware (e.g., 100 Hz).
        *   `default_pixels`: The default number of pixels the sequence targets.
        *   `default_base_color`: The background color for the sequence, parsed by [`parse_color`](../compile_seqdesign.py:27).
    *   This validation is primarily handled by the [`validate_metadata`](../compile_seqdesign.py:123) function.
    *   The `total_duration_seconds` for the sequence is determined. It's either taken directly from `metadata.total_duration_seconds` or calculated as the maximum end time of all effects in the `effects_timeline` by the [`calculate_total_duration`](../compile_seqdesign.py:179) function.
    *   The path to an associated audio file (`metadata.audio_file_path`) is resolved to an absolute path using the [`resolve_audio_path`](../compile_seqdesign.py:237) function and the `audio_dir`.

3.  **Audio Analysis (Conditional):**
    *   The script checks if any effects in the `effects_timeline` are audio-dependent (e.g., `pulse_on_beat`, `apply_section_theme_from_audio`).
    *   If audio-dependent effects are present and a valid audio file path has been resolved:
        *   An instance of `roo-code-sequence-maker.AudioAnalyzer` is created.
        *   The `analyze_audio` method of the analyzer is called to process the audio file and extract features (e.g., beats, segments).
        *   The resulting `audio_analysis_data` is stored for use by audio-dependent effect implementation functions.
    *   If no audio-dependent effects are found, or if the audio file is not specified or accessible, this step is skipped or a warning is issued.
    *   See lines [323-347 in `compile_seqdesign.py`](../compile_seqdesign.py:323-347).

4.  **Effect Timeline Processing & Segment Generation:**
    *   This is the core logic where high-level effects are translated into a concrete timeline of color states. This process is detailed further in Section 3.
    *   See lines [349-531 in `compile_seqdesign.py`](../compile_seqdesign.py:349-531).

5.  **PRG-JSON Construction:**
    *   The `final_segments` list (output from the previous step) is transformed into the `sequence` dictionary required by the `.prg.json` format.
    *   This involves converting segment start times from seconds to "time units" based on the `target_prg_refresh_rate`.
    *   This process is detailed further in Section 4.
    *   See lines [535-560 in `compile_seqdesign.py`](../compile_seqdesign.py:535-560).

6.  **Output to `.prg.json` File:**
    *   The constructed `prg_json_data` dictionary is written to the specified output file path as a formatted JSON string.
    *   The script ensures that the output directory exists, creating it if necessary.
    *   See lines [570-594 in `compile_seqdesign.py`](../compile_seqdesign.py:570-594).

## 3. Detailed: Effect Timeline Processing & Segment Generation

This stage is responsible for taking the abstract `effects_timeline` from the `.seqdesign.json` and converting it into a flat, ordered list of "segments". Each segment represents a specific color applied to a set of pixels for a defined duration.

*   **Segment Data Structure:**
    A "segment" is represented internally as a tuple:
    `(start_time_sec, end_time_sec, rgb_color_tuple, pixels_int)`
    *   `start_time_sec`: Float, start time of the segment in seconds.
    *   `end_time_sec`: Float, end time of the segment in seconds.
    *   `rgb_color_tuple`: A tuple `(R, G, B)` representing the color.
    *   `pixels_int`: An integer representing the number of pixels this segment applies to (often the `default_pixels` value).

*   **Initialization:**
    *   A list named `final_segments` is initialized.
    *   If `total_duration_seconds` is greater than zero, `final_segments` starts with a single, base segment. This segment spans the entire `total_duration_seconds` of the sequence, uses the `default_base_rgb` color, and applies to `default_pixels`.
    *   Example: `final_segments = [(0.0, 60.0, (0, 0, 0), 4)]` for a 60-second sequence with a black base color and 4 default pixels.
    *   See lines [360-363 in `compile_seqdesign.py`](../compile_seqdesign.py:360-363).

*   **Iterating Through `effects_timeline`:**
    *   The script iterates through each `effect_data` object in the `effects_timeline` array from the input `.seqdesign.json`.
    *   **Crucially, effects are processed in the order they appear in the `effects_timeline`. This order dictates the layering behavior: later effects can override or modify the state established by earlier effects.**

*   **For Each Effect:**

    1.  **Timing Resolution:**
        *   The `start_seconds`, `end_seconds`, and `duration_seconds` for the current effect are extracted from its `timing` object.
        *   The script ensures valid timing information is present and converts values to floats. If `end_seconds` is missing, it's calculated from `start_seconds + duration_seconds`. If `duration_seconds` is missing, it's calculated from `end_seconds - start_seconds`.
        *   `effect_start_sec` and `effect_end_sec` are then clamped to be within the bounds of `0.0` and `total_duration_seconds`.
        *   If, after clamping, the effect has zero or negative duration (`effect_end_sec <= effect_start_sec`), it is skipped.
        *   See lines [373-429 in `compile_seqdesign.py`](../compile_seqdesign.py:373-429).

    2.  **Calling Effect Implementation Functions:**
        *   The `effect_type` (e.g., `"solid_color"`, `"fade"`, `"pulse_on_beat"`) is used to dispatch to the appropriate Python function responsible for implementing that effect. These functions reside in modules like [`common_effects.py`](../effect_implementations/common_effects.py) and [`audio_driven_effects.py`](../effect_implementations/audio_driven_effects.py).
        *   Examples:
            *   `effect_type: "solid_color"` calls [`common_effects.apply_solid_color_effect()`](../effect_implementations/common_effects.py).
            *   `effect_type: "fade"` calls [`common_effects.apply_fade_effect()`](../effect_implementations/common_effects.py).
            *   `effect_type: "pulse_on_beat"` calls [`audio_driven_effects.apply_pulse_on_beat_effect()`](../effect_implementations/audio_driven_effects.py).
        *   These effect implementation functions receive the effect's timing (`effect_start_sec`, `effect_end_sec`), its `params`, the processed `metadata` (including `default_pixels`, `target_prg_refresh_rate`), and `audio_analysis_data` (if applicable).
        *   Each effect function returns a list of `newly_generated_segments_for_this_effect`. This list contains segment tuples `(start_sec, end_sec, color_rgb, pixels)` specific to how that particular effect instance should manifest on the timeline. For example, a "strobe" effect would return multiple short segments of alternating colors.
        *   See lines [442-477 in `compile_seqdesign.py`](../compile_seqdesign.py:442-477).

    3.  **Segment Merging/Layering Logic (Crucial Detail):**
        *   This is where the `newly_generated_segments_for_this_effect` are "stamped" or "painted over" the existing `final_segments`. The script iterates through each `new_segment` produced by the current effect.
        *   For each `new_segment = (ns, ne, nc, np)`:
            *   A `temp_final_segments` list is created to build the updated timeline.
            *   The script iterates through each `old_segment = (os, oe, oc, op)` in the current `final_segments`.
            *   **Overlap Analysis:**
                *   If `old_segment` is entirely before `new_segment` (`oe <= ns`), it's added to `temp_final_segments` as is.
                *   If `old_segment` is entirely after `new_segment` (`os >= ne`), it's added to `temp_final_segments` as is.
                *   If `old_segment` overlaps with `new_segment`:
                    *   The part of `old_segment` that occurs *before* `new_segment` (if `os < ns`) is preserved and added to `temp_final_segments` as `(os, ns, oc, op)`.
                    *   The part of `old_segment` that occurs *after* `new_segment` (if `oe > ne`) is preserved and added to `temp_final_segments` as `(ne, oe, oc, op)`.
                    *   The `new_segment` itself effectively replaces the portion of any `old_segment`(s) it overlaps.
            *   After processing all `old_segment`s against the current `new_segment`, the `new_segment` itself is added to `temp_final_segments`.
            *   `temp_final_segments` is then sorted by start time.
            *   **Cleaning and Consolidation:**
                *   The sorted `temp_final_segments` are "cleaned". This involves:
                    *   Removing any segments with zero or negative duration (where `end_time <= start_time`).
                    *   Merging adjacent segments if they have the exact same start/end times, color, and pixel count. (Note: The current implementation merges if `next_s == curr_e` and color & pixels match, effectively extending the `current_segment`'s end time).
                *   The `cleaned_segments` become the new `final_segments` for the next iteration (either the next segment from the current effect or the next effect in the timeline).
        *   **Conceptual Example:**
            Suppose `final_segments` is `[(0.0, 10.0, (255,0,0), 4)]` (RED from 0s to 10s).
            A new effect generates `new_segment = (2.0, 5.0, (0,0,255), 4)` (BLUE from 2s to 5s).
            1.  The original RED segment `(0.0, 10.0, ...)` overlaps.
            2.  The part before BLUE: `(0.0, 2.0, (255,0,0), 4)` is kept.
            3.  The part after BLUE: `(5.0, 10.0, (255,0,0), 4)` is kept.
            4.  The new BLUE segment `(2.0, 5.0, (0,0,255), 4)` is added.
            5.  After sorting and cleaning, `final_segments` becomes:
                `[(0.0, 2.0, (255,0,0), 4), (2.0, 5.0, (0,0,255), 4), (5.0, 10.0, (255,0,0), 4)]`
        *   See lines [479-530 in `compile_seqdesign.py`](../compile_seqdesign.py:479-530).

*   **Final State:**
    *   After all effects in `effects_timeline` have been processed, the `final_segments` list contains a definitive, flattened, non-overlapping, and consolidated timeline of color states for the entire sequence duration.

## 4. Detailed: PRG-JSON Construction

Once `final_segments` is fully generated, it's used to construct the `prg_json_data` dictionary, which will be written to the `.prg.json` file.

1.  **Initialization of `prg_json_data`:**
    *   A dictionary `prg_json_data` is created with top-level keys:
        *   `"default_pixels"`: Copied from processed metadata.
        *   `"refresh_rate"`: Copied from `target_prg_refresh_rate`.
        *   `"end_time"`: Calculated as `round(total_duration_seconds * target_prg_refresh_rate)`. This represents the total duration in "time units".
        *   `"color_format"`: Hardcoded to `"RGB"`.
        *   `"sequence"`: An empty dictionary, to be populated next.
    *   See lines [538-545 in `compile_seqdesign.py`](../compile_seqdesign.py:538-545).

2.  **Populating the `"sequence"` Dictionary:**
    *   The script iterates through each `segment` in the `final_segments` list.
    *   For each `segment = (start_time_sec, end_time_sec, rgb_color_tuple, pixels_int)`:
        *   `start_time_units` is calculated: `round(start_time_sec * target_prg_refresh_rate)`. This converts the segment's start time from seconds to an integer time unit based on the hardware's refresh rate.
        *   An entry is added to the `prg_json_data['sequence']` dictionary.
            *   The **key** for this entry is the `start_time_units` converted to a **string**.
            *   The **value** is a dictionary: `{"color": list(rgb_color_tuple), "pixels": pixels_int}`.
    *   Example: If a segment is `(2.5, 3.0, (0,255,0), 4)` and `refresh_rate` is 100:
        *   `start_time_units = round(2.5 * 100) = 250`.
        *   The entry in `prg_json_data['sequence']` would be:
            `"250": {"color": [0, 255, 0], "pixels": 4}`
    *   Note: The `end_time_sec` from the segment tuple is implicitly defined by the start time of the *next* segment in the PRG-JSON sequence or by the global `end_time` if it's the last segment.
    *   See lines [547-559 in `compile_seqdesign.py`](../compile_seqdesign.py:547-559).

## 5. Data Structures

*   **Internal Segment Tuple:**
    As mentioned in Section 3, the primary internal data structure for representing a piece of the timeline is:
    `(start_time_sec: float, end_time_sec: float, rgb_color_tuple: Tuple[int,int,int], pixels_int: int)`

*   **`.seqdesign.json` (Input):**
    Refer to `roocode_sequence_designer_tools/docs/seqdesign_json_schema.md` for its structure. Key parts used by this script are `metadata` and `effects_timeline`.

*   **`.prg.json` (Output):**
    Refer to `prg_json_format_README.md` for its structure. This script generates the `sequence` dictionary within it.

## 6. Dependencies

*   **Standard Python Libraries:**
    *   `json`: For loading and saving JSON data.
    *   `argparse`: For command-line argument parsing.
    *   `os`: For file path operations.
    *   `sys`: For `sys.exit()`.
    *   `typing`: For type hints.

*   **Internal Project Modules:**
    *   [`roo-code-sequence-maker.AudioAnalyzer`](../../roo-code-sequence-maker/audio_analyzer.py): Used for audio analysis if audio-dependent effects are present. (Imported as `from roo_code_sequence_maker.audio_analyzer import AudioAnalyzer`)
    *   [`roocode_sequence_designer_tools.effect_implementations.common_effects`](../effect_implementations/common_effects.py): Contains functions like `apply_solid_color_effect`, `apply_fade_effect`, `apply_strobe_effect`.
    *   [`roocode_sequence_designer_tools.effect_implementations.audio_driven_effects`](../effect_implementations/audio_driven_effects.py): Contains functions like `apply_pulse_on_beat_effect`, `apply_section_theme_from_audio_effect`.
    *   The script also includes an embedded simplified [`parse_color`](../compile_seqdesign.py:27) function (lines [27-94](../compile_seqdesign.py:27-94)) to handle basic color name strings and RGB dictionary inputs, reducing external dependencies for this specific utility when run standalone. This is a simplified version of what might be in a more comprehensive `tool_utils.color_parser`.