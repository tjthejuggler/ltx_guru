# Roocode Sequence Designer Tools

## Overview

This directory, [`roocode_sequence_designer_tools/`](./), contains Python tools and configurations that are integral to the Roocode Sequence Designer System. These components are primarily utilized by the Roocode agent (the LLM) and the [`compile_seqdesign.py`](./compile_seqdesign.py) script to interpret, process, and compile lighting sequence designs.

The tools within this directory facilitate the translation of abstract effect descriptions (as understood by Roocode) into concrete, executable lighting programs. Advanced features include **Pattern Templates** for creating sophisticated sequences with minimal manual work.
**Update (2025-06-06):** Fade effect handling has been improved. [`compile_seqdesign.py`](./compile_seqdesign.py) now prepares fade definitions in `.seqdesign.json` files for native processing by `prg_generator.py`, allowing for smoother and more accurate fade transitions in the final `.prg` files.

For details on the structure of `.seqdesign.json` files, please refer to the [Sequence Design JSON Schema](./docs/seqdesign_json_schema.md).

## Sequence Designer Mode - Proactive Tool Evolution

*Timestamp: 5/30/2025, 9:06 AM (Asia/Bangkok, UTC+7:00)*

The Sequence Designer mode has been enhanced with a proactive mechanism for tool and feature evolution. As detailed in its operational instructions ([`docs/sequence_designer_mode_instructions.md`](roocode_sequence_designer_tools/docs/sequence_designer_mode_instructions.md:1)), the mode is now guided to:

1.  **Identify Potential Enhancements:** When performing tasks, if a new tool, or a feature for an existing tool, could significantly improve efficiency or capability, this potential is recognized.
2.  **Assess Usefulness:** The mode evaluates if the identified enhancement is broadly applicable for future sequence design tasks or if it's too specific to the current context.
3.  **Act Accordingly:**
    *   **Generally Useful:** If deemed broadly beneficial, the mode is instructed to attempt to create and document the new tool/feature *on the spot*. This includes adding new Python scripts to [`roocode_sequence_designer_tools/`](roocode_sequence_designer_tools/), updating documentation in [`docs/`](roocode_sequence_designer_tools/docs/), and potentially updating [`tools_lookup.json`](roocode_sequence_designer_tools/tools_lookup.json).
    *   **Specific/Uncertain:** If the enhancement is too niche or its general utility is unclear, it's logged with details in [`roocode_sequence_designer_tools/potential_tools_and_features.md`](roocode_sequence_designer_tools/potential_tools_and_features.md) for future review and potential development. The mode will create this file if it doesn't already exist.

This continuous improvement loop aims to organically grow the capabilities of the Sequence Designer toolset, making it more powerful and efficient over time.
## Sequence Designer Mode - Enhanced Self-Improvement Mechanism

*Timestamp: 5/30/2025, 9:23 AM (Asia/Bangkok, UTC+7:00)*

The Sequence Designer mode's self-improvement capabilities have been further refined. Building upon its ability to codify learnings into documentation, the mode now incorporates:

1.  **Self-Improvement Journaling:** The mode is instructed to keep a timestamped journal or history of its own self-identified improvements. This can be part of its main operational instructions ([`docs/sequence_designer_mode_instructions.md`](roocode_sequence_designer_tools/docs/sequence_designer_mode_instructions.md:1)) or a separate log. This practice aims to ensure that lessons learned are tracked and built upon, preventing regression or repetition of inefficient workflows.
2.  **Selective Improvement:** The mode understands that not every task interaction will yield a significant new learning. It will focus on documenting improvements when it clearly identifies inefficiencies in its process or discovers a demonstrably better approach *after* completing a task, particularly for sequence creation. If a task is handled with optimal efficiency, extensive self-critique and documentation for that instance are not mandatory.

These enhancements aim to make the self-improvement process more targeted and sustainable, ensuring that the Sequence Designer mode becomes progressively more effective and efficient in its core tasks.
## File Naming Conventions

The LTX Guru project uses standardized file extensions for different types of data:

| File Type | Extension | Description |
|-----------|-----------|-------------|
| Sequence Design Files | `.seqdesign.json` | High-level sequence design files |
| PRG JSON Files | `.prg.json` | Compiled program files for LTX balls |
| Raw Song Lyrics | `.lyrics.txt` | Raw lyrics text files |
| Timestamped Song Lyrics | `.synced_lyrics.json` | Timestamped/aligned lyrics |
| Ball Color Change Sequences | `.ballseq.json` | Ball-specific color sequences |
| Audio Analysis Reports | `.analysis_report.json` | Audio analysis data |
| Beat Patterns | `.beatpattern.json` | Beat-synchronized patterns |
| Section Themes | `.sectiontheme.json` | Section-based color themes |

Using these standardized extensions helps ensure compatibility with all tools in the ecosystem.

## Directory Structure

Below is an overview of the key subdirectories and files within `roocode_sequence_designer_tools/`:

*   **[`compile_seqdesign.py`](./compile_seqdesign.py):**
    *   The main script responsible for compiling `.seqdesign.json` files (Roocode's high-level design format) into `.prg.json` files (the low-level executable sequence format for the lighting hardware).

*   **[`extract_audio_features.py`](./extract_audio_features.py):**
    *   A command-line interface (CLI) tool used for analyzing audio files and extracting relevant features (e.g., beats, onsets, loudness). The output is typically a JSON file consumed by audio-driven effects.

*   **[`audio_analysis_report.py`](./audio_analysis_report.py):**
    *   A comprehensive tool for generating detailed audio analysis reports (`.analysis_report.json`) with visualizations and capability testing. This tool provides a complete assessment of all audio analysis capabilities and creates visual plots of audio features.
    *   Supports time range filtering and feature selection to prevent context overflow with large reports.

*   **[`check_report_size.py`](./check_report_size.py):**
    *   A utility tool for checking the size of audio analysis reports before viewing them. This helps prevent context overflow when working with large reports.
    *   Provides a summary of report contents and recommendations for handling large reports.

*   **[`extract_lyrics.py`](./extract_lyrics.py):**
    *   A dedicated tool for extracting and processing lyrics from audio files. It can identify songs, fetch lyrics, and align them with the audio.
    *   Produces `.synced_lyrics.json` files from raw `.lyrics.txt` files or automatically fetched lyrics.
    *   Supports time range filtering and formatted text output.
    *   Requires the Gentle Docker container to be running for lyrics alignment.
    *   Supports caching of extracted lyrics data. Usage: `... [--no-cache] [--clear-all-cache]`

*   **[`combine_audio_data.py`](./combine_audio_data.py):**
    *   A CLI tool to merge multiple audio analysis JSON files into a single, consolidated timeline.
    *   Offsets timestamps from subsequent audio files based on the durations of preceding ones.
    *   Prefixes section labels to avoid naming conflicts (e.g., "File1-Verse1", "File2-Verse1").
    *   Useful for creating sequences that span multiple audio tracks.

*   **[`pattern_templates.py`](./pattern_templates.py):**
    *   A powerful tool for expanding "Pattern Templates" or "Parameterized Meta-Effects" into concrete effects.
    *   Supports `WarningThenEvent`, `LyricHighlight`, `BeatSync`, and `section_theme_energy` pattern types.
    *   Enables sophisticated sequence creation with minimal manual effect definition.
    *   Integrates with lyrics timestamps and audio analysis data for intelligent effect generation.

*   **[`converters/convert_prg_to_ball.py`](./converters/convert_prg_to_ball.py):**
    *   A CLI tool to convert compiled `.prg.json` files into `.ball.json` format.
    *   This is particularly useful for creating single-ball sequences that can be directly imported into the `sequence_maker` application.
    *   Usage: `python roocode_sequence_designer_tools/converters/convert_prg_to_ball.py <input.prg.json> <output.ball.json> [--audio-file <path_to_audio.mp3>]`

*   **[`effect_implementations/`](./effect_implementations/):**
    *   This directory houses Python modules that contain the actual logic for various lighting effects.
    *   **[`common_effects.py`](./effect_implementations/common_effects.py):** Implements common, often non-audio-driven, lighting effects (e.g., static color, fade, snap_on_flash_off).
    *   **[`audio_driven_effects.py`](./effect_implementations/audio_driven_effects.py):** Implements effects that dynamically respond to audio features extracted from a music track.

*   **[`tool_utils/`](./tool_utils/):**
    *   Contains shared utility functions used by various tools and effect implementations.
    *   **[`color_parser.py`](./tool_utils/color_parser.py):** A utility for parsing color representations (e.g., color names, hex codes) into a standardized RGB format.
    *   **[`cache_manager.py`](./tool_utils/cache_manager.py):** A utility for persistent, cross-session caching of data like audio analysis results. It handles cache key generation, storage, and retrieval. Default cache location: `~/.roocode_sequence_designer/cache/` (can be overridden by `ROOCODE_CACHE_DIR` environment variable).

*   **[`tools_lookup.json`](./tools_lookup.json):**
    *   A crucial JSON file that serves as a catalog or manifest of all available effects and CLI tools that Roocode can utilize.

*   **[`examples/`](./examples/):**
    *   Contains example files demonstrating various effects and features.
    *   Includes Python scripts showing how to use effect implementation functions directly.
    *   Contains sample `.seqdesign.json` files showing how to structure sequence designs with different effects.

*   **[`docs/`](./docs/):**
    *   Contains documentation for the various tools and components.
    *   **[`seqdesign_json_schema.md`](./docs/seqdesign_json_schema.md):** Documents the schema for `.seqdesign.json` files including pattern templates.
    *   **[`pattern_templates_guide.md`](./docs/pattern_templates_guide.md):** Comprehensive guide to using pattern templates for sophisticated sequence design.
    *   **[`sequence_designer_mode_instructions.md`](./docs/sequence_designer_mode_instructions.md):** Optimized workflows and instructions for the Sequence Designer mode.
    *   **[`audio_analysis_report_tool.md`](./docs/audio_analysis_report_tool.md):** Detailed documentation for the audio analysis report tool.

## `tools_lookup.json`

The [`tools_lookup.json`](./tools_lookup.json) file is the primary interface through which Roocode discovers and understands the capabilities of the sequence designer tools. It acts as a manifest, detailing the available effects and command-line utilities.

The file has two main top-level keys:

*   **`"effects"`**: An array of objects, where each object defines a lighting effect. Key properties for an effect entry include:
    *   `type_name`: (String) A unique identifier for the effect type (e.g., "static_color", "pulse_beat").
    *   `description`: (String) A human-readable description of what the effect does.
    *   `parameters`: (Array of Objects) Defines the parameters the effect accepts. Each parameter object has:
        *   `name`: (String) Parameter name.
        *   `type`: (String) Expected data type (e.g., "color", "float", "integer", "string", "boolean").
        *   `required`: (Boolean) Whether the parameter is mandatory.
        *   `description`: (String) Explanation of the parameter.
        *   `default`: (Optional) A default value if the parameter is not provided.
    *   `timing_options`: (Array of Strings) Specifies how the timing for this effect can be determined (e.g., "manual_duration", "match_audio_segment").
    *   `requires_audio_analysis`: (Boolean) Indicates if the effect depends on pre-computed audio analysis data.

*   **`"cli_tools"`**: An array of objects, where each object defines a command-line tool. Key properties for a CLI tool entry include:
    *   `name`: (String) A unique identifier for the tool.
    *   `description`: (String) A human-readable description of the tool's purpose.
    *   `command_template`: (String) A template for the command to be executed, often with placeholders for parameters.
    *   `parameters`: (Array of Objects) Defines the parameters the CLI tool accepts, similar in structure to effect parameters.

This file is the bridge between Roocode's abstract understanding of desired lighting behaviors and the concrete Python functions or CLI commands that implement them. Maintaining its accuracy is critical for the system's functionality.

## Adding New Effects (Developer Workflow)

To add a new lighting effect type to the Roocode Sequence Designer System, developers should follow these steps:

1.  **Define the Effect in [`tools_lookup.json`](./tools_lookup.json):**
    *   Add a new JSON object to the `"effects"` array in [`tools_lookup.json`](./tools_lookup.json).
    *   Carefully specify the `type_name`, `description`, and `parameters`. For each parameter, define its `name`, `type` (e.g., "color", "float", "integer", "string", "boolean", "pixel_selection"), `required` status, `description`, and an optional `default` value.
    *   Define appropriate `timing_options` (e.g., "manual_duration", "to_next_beat", "full_segment").
    *   Set `requires_audio_analysis` to `true` if the effect uses audio features, `false` otherwise.

2.  **Implement the Python Function:**
    *   Create a new Python module (e.g., [`new_custom_effects.py`](./effect_implementations/new_custom_effects.py)) within the [`effect_implementations/`](./effect_implementations/) directory, or add your function to an existing relevant module like [`common_effects.py`](./effect_implementations/common_effects.py) or [`audio_driven_effects.py`](./effect_implementations/audio_driven_effects.py).
    *   The Python function implementing the effect should generally follow this signature:
        ```python
        from typing import List, Tuple, Dict, Any

        def apply_<effect_type_name>_effect(
            effect_start_sec: float,
            effect_end_sec: float,
            params: Dict[str, Any],
            metadata: Dict[str, Any], # Contains project-level or segment-level metadata
            audio_analysis_data: Dict[str, Any] # Contains data from extract_audio_features.py if required
        ) -> List[Tuple[float, float, Tuple[int, int, int], int]]:
            # Function implementation
            pass
        ```
    *   Inside the function:
        *   Parse the specific parameters required for this effect from the `params` dictionary, validating them as necessary.
        *   Use the [`color_parser.py`](./tool_utils/color_parser.py) utility (e.g., `tool_utils.color_parser.parse_color(params.get("color_param"))`) for handling any color inputs.
        *   The function must return a list of segment tuples. Each tuple represents a continuous lighting state and has the format: `(start_time_seconds, end_time_seconds, (R, G, B), pixel_mask_integer)`.
            *   `start_time_seconds`: Absolute start time of this light segment within the sequence.
            *   `end_time_seconds`: Absolute end time of this light segment.
            *   `(R, G, B)`: A tuple of integers (0-255) representing the color.
            *   `pixel_mask_integer`: An integer where bits represent which pixels are affected (e.g., for an 8-pixel strip, `0b11111111` or `255` means all pixels, `0b00000001` or `1` means the first pixel).

3.  **Update [`effect_implementations/__init__.py`](./effect_implementations/__init__.py):**
    *   If you created a new module, ensure it's imported in [`effect_implementations/__init__.py`](./effect_implementations/__init__.py).
    *   Make sure your new effect function (e.g., `apply_<effect_type_name>_effect`) is imported and accessible from the `effect_implementations` package, typically by adding it to the `__all__` list or importing it directly into the `__init__.py`'s namespace if that's the project convention. This allows [`compile_seqdesign.py`](./compile_seqdesign.py) to find and call it.

4.  **Update [`compile_seqdesign.py`](./compile_seqdesign.py):**
    *   Import your new effect function or the module containing it at the top of [`compile_seqdesign.py`](./compile_seqdesign.py). For example:
        ```python
        from .effect_implementations.new_custom_effects import apply_my_new_effect_effect
        # or if added to an existing, already imported module:
        # from .effect_implementations import common_effects (if it's now part of common_effects)
        ```
    *   If your new effect is audio-dependent (i.e., `requires_audio_analysis` is `true` in [`tools_lookup.json`](./tools_lookup.json)), add its `type_name` (string) to the `AUDIO_DEPENDENT_EFFECT_TYPES` list within [`compile_seqdesign.py`](./compile_seqdesign.py). This list helps the compiler ensure audio data is available when needed.
        ```python
        AUDIO_DEPENDENT_EFFECT_TYPES = [
            "pulse_beat",
            "strobe_on_beat",
            # ... other audio effects
            "your_new_effect_type_name" # Add your new effect type name here
        ]
        ```
    *   In the main effect processing loop within [`compile_seqdesign.py`](./compile_seqdesign.py) (usually a large `if/elif/else` structure that switches on `effect_type`), add a new `elif` block to handle your effect:
        ```python
        # ... existing effect handling ...
        elif effect_type == "your_new_effect_type_name":
            # Ensure effect_params, effect_meta, audio_data are correctly populated
            segments.extend(
                apply_your_new_effect_type_name_effect(
                    current_time,
                    current_time + effect_duration, # Or however duration is determined
                    effect_params,
                    effect_meta,
                    audio_data if effect_type in AUDIO_DEPENDENT_EFFECT_TYPES else None
                )
            )
        # ...
        ```
        Ensure you pass the correct arguments, especially `effect_start_sec`, `effect_end_sec`, `params` (as `effect_params`), `metadata` (as `effect_meta`), and `audio_analysis_data` (as `audio_data`).

## Key Scripts

### `compile_seqdesign.py`

*   **Purpose:** This is the core compiler that takes a high-level sequence design specified in a `.seqdesign.json` file (often generated or manipulated by Roocode) and transforms it into a low-level, hardware-executable `.prg.json` file. It resolves effect parameters, timings, and calls the appropriate Python effect implementation functions.
*   **Command-Line Usage:**
    ```bash
    python -m roocode_sequence_designer_tools.compile_seqdesign <input_seqdesign_json_path> <output_prg_json_path> [--audio-dir <path_to_audio_analysis_directory>]
    ```
    *   `<input_seqdesign_json_path>`: Path to the input `.seqdesign.json` file.
    *   `<output_prg_json_path>`: Path where the output `.prg.json` file will be saved.
    *   `--audio-dir <path_to_audio_analysis_directory>`: (Optional) Path to a directory containing JSON files with audio analysis data (e.g., output from [`extract_audio_features.py`](./extract_audio_features.py)). Required if the sequence uses audio-dependent effects.

### `extract_audio_features.py`

*   **Purpose:** A CLI tool designed to analyze an audio file and extract various features like beats, onsets, tempo, and loudness contours. The extracted features are saved in a JSON format, which can then be used by audio-driven effects in [`compile_seqdesign.py`](./compile_seqdesign.py).
*   **Caching:** This tool supports persistent caching of analysis results to speed up subsequent runs with the same audio file and parameters.
    *   `--no-cache`: Forces re-analysis and prevents saving to cache.
    *   `--clear-all-cache`: Clears all cache entries managed by the `CacheManager` (this is a global clear for the default cache directory).
*   **Command-Line Usage:**
    ```bash
    python roocode_sequence_designer_tools/extract_audio_features.py <audio_file_path> --features <feature1_name>[,<feature2_name>...] [--output <output_json_path>] [--no-cache] [--clear-all-cache]
    ```
    *   `<audio_file_path>`: Path to the audio file to be analyzed (e.g., `.wav`, `.mp3`).
    *   `--features <feature1_name>[,<feature2_name>...]`: A comma-separated list of features to extract (e.g., `beats`, `onsets`, `tempo`, `loudness`).
    *   `--output <output_json_path>`: (Optional) Path to save the extracted features as a JSON file. If not provided, output might go to stdout or a default filename.

### `audio_analysis_report.py`

*   **Purpose:** A comprehensive tool for generating detailed audio analysis reports with visualizations and capability testing. This tool provides a complete assessment of all audio analysis capabilities, creates visual plots of audio features, and generates a structured JSON report.
*   **Caching:** Supports caching of the generated report.
    *   `--no-cache`: Forces re-analysis and prevents saving to cache.
    *   `--clear-all-cache`: Clears all cache entries.
*   **Command-Line Usage:**
    ```bash
    python -m roocode_sequence_designer_tools.audio_analysis_report <audio_file_path> [--output-dir <dir>] [--start-time <seconds>] [--end-time <seconds>] [--features <feature1,feature2,...>] [--check-size-only] [--no-cache] [--clear-all-cache]
    ```
    *   Parameters are as described above, with added caching flags.
*   **For detailed documentation, see [Audio Analysis Report Tool Documentation](./docs/audio_analysis_report_tool.md).**

### `check_report_size.py`

*   **Purpose:** A utility tool for checking the size of audio analysis reports before viewing them. This helps prevent context overflow when working with large reports.
*   **Command-Line Usage:**
    ```bash
    python -m roocode_sequence_designer_tools.check_report_size <report_path.analysis_report.json>
    ```
    *   `<report_path.analysis_report.json>`: Path to the report file to check.
*   **Output:** Provides a summary of the report size, content, and recommendations for handling large reports.

### `align_lyrics.py`

*   **Purpose:** A direct lyrics alignment tool that uses the Gentle API to generate precise word-level timestamps. This is the most efficient method for extracting lyrics timestamps.
*   **Key Features:**
    - Automatically starts the Gentle server if needed
    - Handles all alignment steps in a single command
    - Uses conservative alignment for better results
    - Supports song title and artist name metadata

*   **Command-Line Usage:**
    ```bash
    python align_lyrics.py <audio_file> <lyrics_file> <output_file> [--song-title "Song Title"] [--artist-name "Artist Name"] [--no-conservative] [--no-cache] [--clear-all-cache]
    ```
    *   Parameters are as described above.
    *   **Caching:** Supports caching of alignment results. New flags: `--no-cache`, `--clear-all-cache`.

### `extract_lyrics.py`

*   **Purpose:** A dedicated tool for extracting and processing lyrics from audio files. It can identify songs, fetch lyrics, and align them with the audio.
*   **Caching:** Supports caching of extracted lyrics data.
    *   `--no-cache`: Forces re-extraction and prevents saving to cache.
    *   `--clear-all-cache`: Clears all cache entries.
*   **Optimized Workflow:**
    1. **Start the Gentle server first** (critical prerequisite):
       ```bash
       python -m sequence_maker.scripts.start_gentle
       ```
    2. **Check for API keys** - if missing, skip directly to step 4
    3. **Try automatic lyrics extraction** (if API keys are available):
       ```bash
       python -m roocode_sequence_designer_tools.extract_lyrics <audio_file_path> --output lyrics_data.json
       ```
    4. **If automatic extraction fails, save lyrics to a text file** and use with conservative alignment:
       ```bash
       python -m roocode_sequence_designer_tools.extract_lyrics <audio_file_path> --lyrics-file lyrics.txt --output lyrics_timestamps.json --conservative
       ```
       The `--conservative` flag is crucial for successful alignment.

*   **Command-Line Usage:**
    ```bash
    python -m roocode_sequence_designer_tools.extract_lyrics <audio_file_path> [--output <output_path>] [--start-time <seconds>] [--end-time <seconds>] [--conservative] [--lyrics-file <path>] [--format-text] [--include-timestamps] [--no-cache] [--clear-all-cache]
    ```
    *   Parameters are as described above, with added caching flags.

### `combine_audio_data.py`

*   **Purpose:** This script combines multiple audio analysis JSON files into a single, coherent timeline. It's essential for creating sequences that span multiple songs or audio segments.
*   **Key Features:**
    *   Accepts multiple analysis JSON files and their corresponding original audio files.
    *   Calculates accurate durations for each audio file (using `AudioAnalyzer`).
    *   Offsets all timestamps (beats, sections, energy points, lyric events, etc.) in subsequent files by the cumulative duration of preceding files.
    *   Prefixes section labels with a file identifier (e.g., "File1-Verse1", "File2-Chorus") to ensure uniqueness.
    *   Merges all time-stamped events into a single data structure.
    *   Outputs a new JSON file containing the combined analysis.
*   **Command-Line Usage:**
    ```bash
    python -m roocode_sequence_designer_tools.combine_audio_data --analysis-jsons <file1.json> <file2.json> ... --audio-files <audio1.mp3> <audio2.mp3> ... --output-json <combined_output.json>
    ```
    *   `--analysis-jsons`: Space-separated list of paths to the input audio analysis JSON files.
    *   `--audio-files`: Space-separated list of paths to the original audio files, in the same order as `--analysis-jsons`. These are used to determine accurate durations for offsetting.
    *   `--output-json`: Path to save the combined audio analysis JSON file (e.g., `project_combined.analysis.json`).
*   **Workflow:**
    1. Generate individual audio analysis JSON files for each audio track using tools like `extract_audio_features.py` or `audio_analysis_report.py`.
    2. Use `combine_audio_data.py` to merge these individual analysis files.
    3. Use the resulting combined analysis JSON with `compile_seqdesign.py` and a `.seqdesign.json` file designed for the full combined timeline.

### `pattern_templates.py`

*   **Purpose:** A powerful tool for expanding "Pattern Templates" or "Parameterized Meta-Effects" into concrete effects. This enables sophisticated sequence creation with minimal manual work by defining high-level patterns that get automatically expanded based on lyrics, audio analysis, or custom timing data.
*   **Key Features:**
    *   **WarningThenEvent**: Creates warning effects before main events triggered by lyrics, beats, or custom times.
    *   **LyricHighlight**: Highlights specific words or phrases with visual effects.
    *   **BeatSync**: Synchronizes effects with audio beats within specified time windows.
    *   **Section Theme with Energy Mapping (`section_theme_energy`)**: Applies themes to song sections, modulating a base color (e.g., its brightness or saturation) based on the audio's energy level within that section. This allows for dynamic visual responses to the music's intensity changes across different parts of a song.
        *   **Parameters:**
            *   `themes_definition`: An array of theme objects, e.g., `{ "section_label": "Verse 1", "base_color": "blue", "energy_mapping": "brightness", "energy_factor": 1.0 }`.
            *   `default_color` (optional): Color for sections not matching any defined theme.
            *   `audio_analysis_path`: Path to the JSON file containing audio analysis data (must include section and energy information). (Note: The actual data is passed to the expander function by the `compile_seqdesign.py` or `pattern_templates.py` script runner, this path is for metadata).
        *   **Expansion Logic:** The expander function loads audio analysis (sections, energy timeseries), matches themes to sections, and generates fine-grained `solid_color` effect segments where the color is modulated by energy at each time step.
    *   **Intelligent Ball Selection**: Supports various ball selection strategies (round-robin, specific balls, random).
    *   **Data Integration**: Seamlessly integrates with lyrics timestamps and audio analysis data.

*   **Command-Line Usage:**
    ```bash
    python -m roocode_sequence_designer_tools.pattern_templates <input.seqdesign.json> <output.seqdesign.json> [--lyrics-file <synced_lyrics.json>] [--audio-analysis <analysis.json>]
    ```
    *   `<input.seqdesign.json>`: Path to the input `.seqdesign.json` file containing pattern templates.
    *   `<output.seqdesign.json>`: Path for the output `.seqdesign.json` file with expanded concrete effects.
    *   `--lyrics-file <synced_lyrics.json>`: (Optional) Path to synced lyrics file for lyric-based patterns.
    *   `--audio-analysis <analysis.json>`: (Optional) Path to audio analysis data for beat-based patterns.

*   **Workflow:**
    1. **Design Phase**: Add pattern templates to the `pattern_templates` array in your `.seqdesign.json`
    2. **Expansion Phase**: Use this tool to expand templates into concrete effects
    3. **Compilation Phase**: Compile the expanded file normally with `compile_seqdesign.py`

*   **For detailed documentation, see [Pattern Templates Guide](./docs/pattern_templates_guide.md).**

## Important Considerations & Troubleshooting

### Handling Large Audio Analysis Reports

*   **Check Report Size First:** Always check the size of audio analysis reports before attempting to view them directly. Large reports can cause context overflow issues with LLMs.
    ```bash
    python -m roocode_sequence_designer_tools.check_report_size <report_path>
    ```

*   **Use Time Range Filtering:** When analyzing long audio files, use the time range filtering options to focus on specific sections:
    ```bash
    python -m roocode_sequence_designer_tools.audio_analysis_report <audio_file> --start-time 0 --end-time 60
    ```

*   **Use Feature Selection:** When you only need specific audio features, use the feature selection option:
    ```bash
    python -m roocode_sequence_designer_tools.audio_analysis_report <audio_file> --features beats,sections
    ```

*   **Use Dedicated Tools:** For specific tasks like lyrics processing, use the dedicated tools:
    ```bash
    python -m roocode_sequence_designer_tools.extract_lyrics <audio_file>
    ```

### File Organization

*   **Project Organization:** Always organize related files in the same subdirectory within the sequence_projects folder:
    ```
    sequence_projects/
    └── song_name/                # Create a subdirectory for each song
        ├── artist_song_name.mp3  # Original audio file
        ├── lyrics.txt            # Raw lyrics text file
        ├── lyrics_timestamps.json # Generated timestamps
        ├── analysis_report.json  # Audio analysis data
        └── song_name.seqdesign.json # Sequence design file
    ```
    This organization:
    - Keeps all related files together
    - Makes it easier to find and manage project files
    - Prevents clutter in the root directory
    - Simplifies backup and sharing of complete projects

### Lyrics Processing Considerations (CRITICAL WORKFLOW)

*   **RECOMMENDED APPROACH: Use align_lyrics.py** This is the most efficient method for extracting lyrics timestamps:
    ```bash
    python align_lyrics.py sequence_projects/song_name/artist_song_name.mp3 sequence_projects/song_name/lyrics.txt sequence_projects/song_name/lyrics_timestamps.json --song-title "Song Title" --artist-name "Artist Name"
    ```
    This single command handles everything automatically, including starting the Gentle server if needed.

*   **TOKEN EFFICIENCY GUIDELINES:**
    - Ask for all needed information in a single step
    - NEVER display the entire JSON output - only show a sample of 5-10 timestamps
    - Infer song title and artist from filename when possible
    - Skip automatic identification attempts when API keys are missing
    - Use the most direct approach (align_lyrics.py) whenever possible

*   **Start Gentle Server First:** Always check if the Gentle Docker container is running before attempting lyrics alignment:
    ```bash
    python -m sequence_maker.scripts.start_gentle
    ```

*   **Use Conservative Alignment:** When providing user-supplied lyrics, always use the `--conservative` flag for better alignment results:
    ```bash
    python -m roocode_sequence_designer_tools.extract_lyrics sequence_projects/song_name/artist_song_name.mp3 --lyrics-file sequence_projects/song_name/lyrics.txt --output sequence_projects/song_name/lyrics_timestamps.json --conservative
    ```

*   **Optimized Workflow Summary:**
    1. **RECOMMENDED:** Use align_lyrics.py for a one-step process
       ```bash
       python align_lyrics.py sequence_projects/song_name/artist_song_name.mp3 sequence_projects/song_name/lyrics.txt sequence_projects/song_name/lyrics_timestamps.json --song-title "Song Title" --artist-name "Artist Name"
       ```
    
    2. **ALTERNATIVE:** If align_lyrics.py is not available:
       - Start Gentle server first
       - Ask for lyrics in a single step
       - Save user-provided lyrics to a text file in the same directory as the MP3 file
       - Process with conservative alignment
       
    3. **ALWAYS maintain proper file organization:**
       - Store all related files in the same subdirectory as the MP3 file
       - Use the sequence_projects directory structure
       - Keep project files organized by song

*   **For detailed documentation, see:**
    - [Lyrics Extraction Guide](./docs/lyrics_extraction_guide.md) - Comprehensive documentation on all lyrics extraction tools
    - [Lyrics Extraction Efficiency](./docs/lyrics_extraction_efficiency.md) - Best practices for efficient lyrics extraction
    - [Pattern Templates Guide](./docs/pattern_templates_guide.md) - Comprehensive guide to using pattern templates for sophisticated sequence design
    - [Sequence Designer Mode Instructions](./docs/sequence_designer_mode_instructions.md) - Optimized workflows for the Sequence Designer mode

*   **Example Implementation:**
    - [Efficient Lyrics Extraction Example](./examples/efficient_lyrics_extraction.py) - A reference implementation of the most efficient approach

### Python Package Considerations

*   **Python Package Naming:** When creating or referencing Python packages (directories containing an `__init__.py` file), ensure directory names use underscores (e.g., `my_package`) rather than hyphens (e.g., `my-package`). Hyphens are not valid in Python import statements. If a script needs to import modules from a sibling directory that is a package, ensure the package directory is named appropriately.
*   **Running Scripts as Modules:** If a script within a package uses relative imports (e.g., `from . import my_module`), it should typically be run as a module using `python -m package_name.script_name` from the parent directory of the package. This allows Python to correctly resolve the relative imports.
*   **Code Quality:**
    *   **Variable Shadowing:** Be mindful of variable names. Avoid using local variable names that shadow imported modules or built-in functions (e.g., naming a loop variable `os` if the `os` module is also used in the same scope). This can lead to `UnboundLocalError` or unexpected behavior.
    *   **Testing:** Thoroughly test new effects and changes to the compilation scripts to catch errors early.

---
Last Updated: 2025-06-06 12:08 UTC+7