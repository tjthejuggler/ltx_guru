# Sequence Designer Mode Instructions

## Guiding Principles
- **Efficiency First:** Always aim for the most direct and automated solution.
- **Tool-Centric:** Prioritize using existing tools in `roocode_sequence_designer_tools/` over manual file manipulation or creating new scripts for established tasks.
- **Schema Adherence:** Strictly follow the JSON schemas for all LTX Guru file formats (e.g., `.ball.json`, `.seqdesign.json`, `.lyrics.json`). Refer to schema documents in `roocode_sequence_designer_tools/docs/`.
- **Clear Communication:** If a user's request is ambiguous or a tool has limitations, clearly explain the situation and propose solutions or request clarification.

## File Organization and Types

Always organize project files in the `sequence_projects` directory using the following structure and file extensions:

```
sequence_projects/
└── song_name/                # Create a subdirectory for each song
    ├── artist_song_name.mp3  # Original audio file
    ├── lyrics.txt            # Raw lyrics text file (input for alignment)
    ├── song_name.lyrics.json # Timestamped/aligned lyrics (output of alignment)
    ├── song_name.ball.json   # Single ball sequence file (for single ball timelines)
    ├── song_name.analysis.json # Audio analysis data
    ├── song_name.seqdesign.json # High-level sequence design file (multi-ball or advanced effects)
    └── song_name.prg.json    # Compiled program file for LTX balls
```

### File Types and Extensions

| File Type                 | Extension         | Description                                      |
|---------------------------|-------------------|--------------------------------------------------|
| Sequence Design Files     | `.seqdesign.json` | High-level sequence design (multi-ball/advanced) |
| PRG JSON Files            | `.prg.json`       | Compiled program files for LTX balls             |
| Ball Sequence Files       | `.ball.json`      | Single ball color sequences                      |
| Lyrics Timestamps         | `.lyrics.json`    | Timestamped/aligned lyrics                       |
| Audio Analysis Reports    | `.analysis.json`  | Audio analysis data                              |
| Raw Lyrics Text           | `.txt`            | User-provided or raw lyrics text                 |

This organization:
- Keeps all related files together.
- Makes it easier to find and manage project files.
- Prevents clutter in the root directory.
- Simplifies backup and sharing of complete projects.

## Target Output File Formats

Understanding the user's need is key to selecting the correct output format:

1.  **Single Ball Sequences (`.ball.json`):**
    *   **Trigger:** When a user requests a sequence for a **"single ball"**, **"single LTX ball"**, or explicitly asks for a file to be used in a "single ball timeline" in Sequence Maker.
    *   **Primary Output:** The primary target output is a **`.ball.json`** file.
    *   **Schema:** Always consult [`roocode_sequence_designer_tools/docs/ball_sequence_format.md`](roocode_sequence_designer_tools/docs/ball_sequence_format.md) for the correct schema.
    *   **Generation:** Use dedicated converter tools (e.g., `convert_lyrics_to_ball.py`) as the first choice.

2.  **Multi-Ball or Advanced Sequences (`.seqdesign.json` then `.prg.json`):**
    *   **Trigger:** When the user requests sequences for multiple balls, or requires advanced design features unique to `.seqdesign.json` (like pattern templates, complex effect layering, audio-reactive effects not directly generatable into `.ball.json`).
    *   **Primary Output:** A `.seqdesign.json` file, which is then compiled into a `.prg.json` file using `compile_seqdesign.py`.
    *   **Schema:** Consult [`roocode_sequence_designer_tools/docs/seqdesign_json_schema.md`](roocode_sequence_designer_tools/docs/seqdesign_json_schema.md).

## Sequence Generation Workflows

### 1. Lyrics Processing (Alignment)

When extracting lyrics timestamps from audio files, follow this optimized workflow:

*   **Check Gentle Server First**:
    *   ALWAYS check if the Gentle server is running: `python -m sequence_maker.scripts.start_gentle`. This is essential.
*   **Gather Information**: Ask for the complete lyrics text in one prompt. Song title and artist can often be inferred from the MP3 filename.
*   **Use `align_lyrics.py` Directly**:
    *   Save user-provided lyrics to a `.txt` file (e.g., `sequence_projects/song_name/lyrics.txt`).
    *   Run:
        ```bash
        python align_lyrics.py sequence_projects/song_name/artist_song_name.mp3 sequence_projects/song_name/lyrics.txt sequence_projects/song_name/song_name.lyrics.json --song-title "Song Title" --artist-name "Artist Name"
        ```
*   **Present Results Efficiently**: Show only the first 5-10 timestamps. NEVER display the entire JSON.

### 2. Lyrics to `.ball.json` (Single Ball Sequence)

This is the **preferred workflow for single-ball requests based on lyrics**.

*   **Obtain Timestamps:** Ensure you have a valid `.lyrics.json` file (see "Lyrics Processing" above).
*   **Identify Tool:** Use [`roocode_sequence_designer_tools/converters/convert_lyrics_to_ball.py`](roocode_sequence_designer_tools/converters/convert_lyrics_to_ball.py).
*   **Understand Tool Parameters:** Before use, determine arguments for input/output files, color(s), background color, and pixel count. Read the script's `--help` or its source if necessary.
    *   **Current `convert_lyrics_to_ball.py` parameters:**
        *   `input_file`: Path to `.lyrics.json`.
        *   `output_file`: Path for the new `.ball.json`.
        *   `--color`: Single RGB color for words (e.g., `"0,0,255"`).
        *   `--background`: RGB color for gaps (e.g., `"0,0,0"`).
        *   `--pixels`: Number of pixels (1-4, default is 4). For a single ball request, this should often be `1` if the user implies one light source or the entire ball as one unit. Clarify if unsure.
*   **Handling Color Cycling/Multiple Colors for Words:**
    *   The current `convert_lyrics_to_ball.py` only accepts a single `--color`.
    *   **If color cycling (e.g., Red, Green, Blue per word) is requested:**
        1.  **Ideal Long-Term:** Note that the tool could be enhanced to accept a list/sequence of colors.
        2.  **Current Best Practice (Programmatic Modification):**
            a.  Run `convert_lyrics_to_ball.py` with a placeholder color (e.g., white) and the desired background (e.g., black for "off between words").
                ```bash
                python roocode_sequence_designer_tools/converters/convert_lyrics_to_ball.py input.lyrics.json output.ball.json --color "255,255,255" --background "0,0,0" --pixels 1
                ```
            b.  **Create a temporary Python script** (or use a general-purpose JSON editing tool if available and suitable) to read the generated `output.ball.json`.
            c.  Iterate through the `segments` in the `output.ball.json`. Identify segments corresponding to words (i.e., those not using the background color).
            d.  Apply the color cycling logic (e.g., Red, Green, Blue) to these word segments.
            e.  Overwrite the `output.ball.json` with the modified content.
            f.  **This programmatic modification is strongly preferred over the LLM manually constructing the entire cycling JSON.**
*   **Execute Conversion:** Run the tool with correct paths and parameters.
    Example (for single color blue, off between words, 1 pixel):
    ```bash
    python roocode_sequence_designer_tools/converters/convert_lyrics_to_ball.py sequence_projects/song_name/song_name.lyrics.json sequence_projects/song_name/song_name.ball.json --color "0,0,255" --background "0,0,0" --pixels 1
    ```
*   **Verify Output:** Briefly check the generated `.ball.json` for correctness against the schema.

### 3. Sequence Design (`.seqdesign.json`) and Compilation (`.prg.json`)

Use this for multi-ball sequences or when advanced effects from the `.seqdesign.json` schema are needed.

*   **Understand Requirements:** Clearly define colors, timings, effects (fades, pulses, etc.), and pixel usage.
*   **Consult Schema:** Strictly adhere to [`roocode_sequence_designer_tools/docs/seqdesign_json_schema.md`](roocode_sequence_designer_tools/docs/seqdesign_json_schema.md).
*   **Tool-Assisted Generation:**
    *   If generating from lyrics or audio analysis, look for tools in `roocode_sequence_designer_tools/` that can output or help construct `.seqdesign.json` elements (e.g., pattern templates).
    *   **Avoid manual construction of large `.seqdesign.json` files by the LLM.** If a complex design is needed from basic data, a dedicated Python script should be created or used.
*   **Create `.seqdesign.json`:**
    *   If programmatic generation is not fully possible, ensure all required fields (metadata, effect IDs, types, timings, params) are present and correct.
*   **Compile to `.prg.json`:** Use [`roocode_sequence_designer_tools/compile_seqdesign.py`](roocode_sequence_designer_tools/compile_seqdesign.py).
    ```bash
    python roocode_sequence_designer_tools/compile_seqdesign.py input.seqdesign.json output.prg.json
    ```
*   **Troubleshoot:** Address any compilation errors by re-checking the `.seqdesign.json` against its schema.

## Tool Usage Guidelines (Reinforced)

1.  **ALWAYS first search for existing tools** in the `roocode_sequence_designer_tools` directory (especially in `converters/` and `effect_implementations/`) that can accomplish your task or part of it. This is especially critical for standard file conversions (e.g., lyrics to `.ball.json`, `.seqdesign.json` to `.prg.json`). **Prioritize using these tools over manual JSON construction via `write_to_file` or `apply_diff` for generating entire structured files.**
2.  If a tool exists but lacks a specific feature (e.g., color cycling), consider if programmatically post-processing the tool's output is feasible and more efficient than full manual creation. Note such limitations for potential future tool enhancements.
3.  If a new, reusable utility or complex transformation is needed, propose creating a well-documented Python script within `roocode_sequence_designer_tools/`.
4.  When using CLI tools, always verify their expected arguments (e.g., via `--help` or by reading their source/documentation).

## Token Efficiency Guidelines

*   **Minimize Redundant Data:** NEVER read or display entire large JSON files in your responses. Show only small, relevant samples or summaries.
*   **Focused Prompts:** Ask for all necessary information from the user in a single, clear step if possible.
*   **Direct Tools:** Use the most direct tool for the job (e.g., `align_lyrics.py` over older methods).

## Self-Improvement Mechanism

After completing any task:

1.  **Analyze Efficiency:** Identify steps that were inefficient, could have been skipped, or where a better tool/approach could have been used. Note if you had to perform excessive manual data manipulation that a tool should handle.
2.  **Update Knowledge (Internal):** Mentally document more efficient approaches. Focus on reducing token usage, manual steps, and error potential.
3.  **CRITICAL FINAL STEP - Codify Learnings:** If improvements to workflows, tool usage, or understanding are identified (especially after user feedback or encountering inefficiencies), **actively update these operational instructions (`sequence_designer_mode_instructions.md`) and/or the high-level directives in `.roomodes`** to codify these learnings. Propose these documentation changes as part of the task completion or as a follow-up action. This ensures continuous, tangible improvement.
4.  **Apply Learnings:** Prioritize the most efficient and tool-driven workflows, informed by the updated documentation, in future interactions.
### Proactive Tool/Feature Identification and Management

Beyond refining existing workflows, actively look for opportunities to enhance the toolset available for sequence design.

1.  **Identify Potential Enhancements:** During any sequence creation task, if you encounter a situation where:
    *   A new tool could significantly simplify or automate a recurring sub-task.
    *   An existing tool could be made more powerful or flexible with a new feature.
    *   A manual process is frequently repeated and could be toolified.
    be sure to note this potential enhancement.

2.  **Assess General Usefulness:**
    *   **Likely Useful:** If the potential tool or feature seems broadly applicable and likely to benefit future sequence design tasks (not overly specific to the current, unique request), then:
        *   **Create & Document:** Your primary goal is to design, create (e.g., as a new Python script in [`roocode_sequence_designer_tools/`](roocode_sequence_designer_tools/) or by modifying an existing one), and thoroughly document this new tool or feature *on the spot*. This documentation should include its purpose, usage, arguments, and examples, typically in a new `.md` file within [`roocode_sequence_designer_tools/docs/`](roocode_sequence_designer_tools/docs/) or by updating an existing tool's documentation. The new tool should also be added to [`roocode_sequence_designer_tools/tools_lookup.json`](roocode_sequence_designer_tools/tools_lookup.json) if appropriate.
        *   Ensure the new tool/feature adheres to the guiding principles (efficiency, schema adherence, etc.).
    *   **Unclear/Too Specific:** If the potential tool or feature is highly specific to the current task, or its general future usefulness is uncertain, then:
        *   **Log for Future Consideration:** Add a detailed description of the tool/feature, its potential benefits, and the context in which it was conceived to a file named [`potential_tools_and_features.md`](roocode_sequence_designer_tools/potential_tools_and_features.md) located at `/home/twain/Projects/ltx_guru/roocode_sequence_designer_tools/potential_tools_and_features.md`.
        *   If this file does not exist, create it. Each entry should be clear and provide enough context for later review and potential implementation.

3.  **Integrate and Inform:** After creating and documenting a new tool/feature, ensure these instructions ([`sequence_designer_mode_instructions.md`](roocode_sequence_designer_tools/docs/sequence_designer_mode_instructions.md)) are updated to reflect its availability and guide its usage if necessary.

## Pattern Templates (for `.seqdesign.json`)

Pattern Templates are for advanced `.seqdesign.json` creation, allowing high-level definitions for complex, repetitive, or synchronized effects.

*   **When to Use:** Repetitive lyric-based effects, warning systems, beat synchronization, complex patterns where manual creation is tedious.
*   **Types:** "WarningThenEvent", "LyricHighlight", "BeatSync".
*   **Workflow:** Design in `.seqdesign.json` -> Expand with `pattern_templates.py` -> Compile expanded `.seqdesign.json`.
    ```bash
    python -m roocode_sequence_designer_tools.pattern_templates input.seqdesign.json expanded.seqdesign.json --lyrics-file lyrics.json
    python -m roocode_sequence_designer_tools.compile_seqdesign expanded.seqdesign.json output.prg.json
    ```
*   Refer to [`roocode_sequence_designer_tools/docs/pattern_templates_guide.md`](roocode_sequence_designer_tools/docs/pattern_templates_guide.md) and the schema.

## Additional Resources
- [`roocode_sequence_designer_tools/docs/lyrics_extraction_guide.md`](roocode_sequence_designer_tools/docs/lyrics_extraction_guide.md)
- [`roocode_sequence_designer_tools/docs/lyrics_extraction_efficiency.md`](roocode_sequence_designer_tools/docs/lyrics_extraction_efficiency.md)
- [`roocode_sequence_designer_tools/docs/seqdesign_json_schema.md`](roocode_sequence_designer_tools/docs/seqdesign_json_schema.md)
- [`roocode_sequence_designer_tools/docs/ball_sequence_format.md`](roocode_sequence_designer_tools/docs/ball_sequence_format.md)

By following these updated instructions, future Roocode instances will be better equipped to handle sequence design tasks efficiently and accurately, particularly for single-ball requests.