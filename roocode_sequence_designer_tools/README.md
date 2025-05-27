# Roocode Sequence Designer Tools

## Overview

This directory, [`roocode_sequence_designer_tools/`](./), contains Python tools and configurations that are integral to the Roocode Sequence Designer System. These components are primarily utilized by the Roocode agent (the LLM) and the [`compile_seqdesign.py`](./compile_seqdesign.py) script to interpret, process, and compile lighting sequence designs.

The tools within this directory facilitate the translation of abstract effect descriptions (as understood by Roocode) into concrete, executable lighting programs. Advanced features include **Pattern Templates** for creating sophisticated sequences with minimal manual work.

For details on the structure of `.seqdesign.json` files, please refer to the [Sequence Design JSON Schema](./docs/seqdesign_json_schema.md).

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

*   **[`pattern_templates.py`](./pattern_templates.py):**
    *   A powerful tool for expanding "Pattern Templates" or "Parameterized Meta-Effects" into concrete effects.
    *   Supports WarningThenEvent, LyricHighlight, and BeatSync pattern types.
    *   Enables sophisticated sequence creation with minimal manual effect definition.
    *   Integrates with lyrics timestamps and audio analysis data for intelligent effect generation.

*   **[`effect_implementations/`](./effect_implementations/):**
    *   This directory houses Python modules that contain the actual logic for various lighting effects.
    *   **[`common_effects.py`](./effect_implementations/common_effects.py):** Implements common, often non-audio-driven, lighting effects (e.g., static color, fade, snap_on_flash_off).
    *   **[`audio_driven_effects.py`](./effect_implementations/audio_driven_effects.py):** Implements effects that dynamically respond to audio features extracted from a music track.

*   **[`tool_utils/`](./tool_utils/):**
    *   Contains shared utility functions used by various tools and effect implementations.
    *   **[`color_parser.py`](./tool_utils/color_parser.py):** A utility for parsing color representations (e.g., color names, hex codes) into a standardized RGB format.

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
*   **Command-Line Usage:**
    ```bash
    python roocode_sequence_designer_tools/extract_audio_features.py <audio_file_path> --features <feature1_name> [<feature2_name> ...] [--output <output_json_path>]
    ```
    *   `<audio_file_path>`: Path to the audio file to be analyzed (e.g., `.wav`, `.mp3`).
    *   `--features <feature1_name> [<feature2_name> ...]`: A list of one or more features to extract (e.g., `beats`, `onsets`, `tempo`, `loudness`).
    *   `--output <output_json_path>`: (Optional) Path to save the extracted features as a JSON file. If not provided, output might go to stdout or a default filename.

### `audio_analysis_report.py`

*   **Purpose:** A comprehensive tool for generating detailed audio analysis reports with visualizations and capability testing. This tool provides a complete assessment of all audio analysis capabilities, creates visual plots of audio features, and generates a structured JSON report.
*   **Command-Line Usage:**
    ```bash
    python -m roocode_sequence_designer_tools.audio_analysis_report <audio_file_path> [--output-dir <dir>] [--start-time <seconds>] [--end-time <seconds>] [--features <feature1,feature2,...>] [--check-size-only]
    ```
    *   `<audio_file_path>`: Path to the audio file to be analyzed.
    *   `--output-dir <dir>`: (Optional) Directory to save the report (as `analysis_report.json`) and visualizations. If not provided, uses the directory containing the audio file.
    *   `--start-time <seconds>`: (Optional) Start time in seconds for time-range analysis.
    *   `--end-time <seconds>`: (Optional) End time in seconds for time-range analysis.
    *   `--features <feature1,feature2,...>`: (Optional) Comma-separated list of features to include in the report (e.g., beats,sections,energy,lyrics).
    *   `--check-size-only`: (Optional) Only check the size of an existing report without generating a new one.
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
    python align_lyrics.py <audio_file> <lyrics_file> <output_file> [--song-title "Song Title"] [--artist-name "Artist Name"] [--no-conservative]
    ```
    *   `<audio_file>`: Path to the audio file to extract lyrics from.
    *   `<lyrics_file>`: Path to a text file containing the lyrics.
    *   `<output_file>`: Path to save the output JSON file with timestamps.
    *   `--song-title "Song Title"`: (Optional) Title of the song.
    *   `--artist-name "Artist Name"`: (Optional) Name of the artist.
    *   `--no-conservative`: (Optional) Disable conservative alignment mode (not recommended).

### `extract_lyrics.py`

*   **Purpose:** A dedicated tool for extracting and processing lyrics from audio files. It can identify songs, fetch lyrics, and align them with the audio.
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
    python -m roocode_sequence_designer_tools.extract_lyrics <audio_file_path> [--output <output_path>] [--start-time <seconds>] [--end-time <seconds>] [--conservative] [--lyrics-file <path>] [--format-text] [--include-timestamps]
    ```
    *   `<audio_file_path>`: Path to the audio file to extract lyrics from.
    *   `--output <output_path>`: (Optional) Path to save the lyrics JSON file. If not provided, only prints summary.
    *   `--start-time <seconds>`: (Optional) Start time in seconds for time-range extraction.
    *   `--end-time <seconds>`: (Optional) End time in seconds for time-range extraction.
    *   `--conservative`: (Optional) Use conservative alignment for lyrics processing (recommended when providing your own lyrics).
    *   `--lyrics-file <path>`: (Optional) Path to a text file containing user-provided lyrics.
    *   `--format-text`: (Optional) Format lyrics as readable text instead of JSON.
    *   `--include-timestamps`: (Optional) Include timestamps in formatted text output.

### `pattern_templates.py`

*   **Purpose:** A powerful tool for expanding "Pattern Templates" or "Parameterized Meta-Effects" into concrete effects. This enables sophisticated sequence creation with minimal manual work by defining high-level patterns that get automatically expanded based on lyrics, audio analysis, or custom timing data.
*   **Key Features:**
    - **WarningThenEvent**: Creates warning effects before main events triggered by lyrics, beats, or custom times
    - **LyricHighlight**: Highlights specific words or phrases with visual effects
    - **BeatSync**: Synchronizes effects with audio beats within specified time windows
    - **Intelligent Ball Selection**: Supports various ball selection strategies (round-robin, specific balls, random)
    - **Data Integration**: Seamlessly integrates with lyrics timestamps and audio analysis data

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