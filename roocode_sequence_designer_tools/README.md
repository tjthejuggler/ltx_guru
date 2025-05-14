# Roocode Sequence Designer Tools

## Overview

This directory, [`roocode_sequence_designer_tools/`](./), contains Python tools and configurations that are integral to the Roocode Sequence Designer System. These components are primarily utilized by the Roocode agent (the LLM) and the [`compile_seqdesign.py`](./compile_seqdesign.py) script to interpret, process, and compile lighting sequence designs.

The tools within this directory facilitate the translation of abstract effect descriptions (as understood by Roocode) into concrete, executable lighting programs.

For details on the structure of `.seqdesign.json` files, please refer to the [Sequence Design JSON Schema](./docs/seqdesign_json_schema.md).

## Directory Structure

Below is an overview of the key subdirectories and files within `roocode_sequence_designer_tools/`:

*   **[`compile_seqdesign.py`](./compile_seqdesign.py):**
    *   The main script responsible for compiling `.seqdesign.json` files (Roocode's high-level design format) into `.prg.json` files (the low-level executable sequence format for the lighting hardware).

*   **[`extract_audio_features.py`](./extract_audio_features.py):**
    *   A command-line interface (CLI) tool used for analyzing audio files and extracting relevant features (e.g., beats, onsets, loudness). The output is typically a JSON file consumed by audio-driven effects.

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

## Important Considerations & Troubleshooting

*   **Python Package Naming:** When creating or referencing Python packages (directories containing an `__init__.py` file), ensure directory names use underscores (e.g., `my_package`) rather than hyphens (e.g., `my-package`). Hyphens are not valid in Python import statements. If a script needs to import modules from a sibling directory that is a package, ensure the package directory is named appropriately.
*   **Running Scripts as Modules:** If a script within a package uses relative imports (e.g., `from . import my_module`), it should typically be run as a module using `python -m package_name.script_name` from the parent directory of the package. This allows Python to correctly resolve the relative imports.
*   **Code Quality:**
    *   **Variable Shadowing:** Be mindful of variable names. Avoid using local variable names that shadow imported modules or built-in functions (e.g., naming a loop variable `os` if the `os` module is also used in the same scope). This can lead to `UnboundLocalError` or unexpected behavior.
    *   **Testing:** Thoroughly test new effects and changes to the compilation scripts to catch errors early.

### `extract_audio_features.py`

*   **Purpose:** A CLI tool designed to analyze an audio file and extract various features like beats, onsets, tempo, and loudness contours. The extracted features are saved in a JSON format, which can then be used by audio-driven effects in [`compile_seqdesign.py`](./compile_seqdesign.py).
*   **Command-Line Usage:**
    ```bash
    python roocode_sequence_designer_tools/extract_audio_features.py <audio_file_path> --features <feature1_name> [<feature2_name> ...] [--output_json <output_json_path>]
    ```
    *   `<audio_file_path>`: Path to the audio file to be analyzed (e.g., `.wav`, `.mp3`).
    *   `--features <feature1_name> [<feature2_name> ...]`: A list of one or more features to extract (e.g., `beats`, `onsets`, `tempo`, `loudness`).
    *   `--output_json <output_json_path>`: (Optional) Path to save the extracted features as a JSON file. If not provided, output might go to stdout or a default filename.