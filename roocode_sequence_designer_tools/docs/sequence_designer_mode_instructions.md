# Sequence Designer Mode Instructions

## Guiding Principles
- **Efficiency First:** Always aim for the most direct and automated solution.
- **Tool-Centric:** Prioritize using existing tools in `roocode_sequence_designer_tools/` over manual file manipulation or creating new scripts for established tasks.
- **Schema Adherence:** Strictly follow the JSON schemas for all LTX Guru file formats (e.g., `.ball.json`, `.seqdesign.json`, `.lyrics.json`). Refer to schema documents in `roocode_sequence_designer_tools/docs/`.
- **Clear Communication:** If a user's request is ambiguous or a tool has limitations, clearly explain the situation and propose solutions or request clarification.
- **CRITICAL: Code Generation for Repetitive Content:** Use Python scripts to generate large, repetitive sequence files instead of manual writing. Never manually write repetitive JSON content.

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
    ├── song_name.prg.json    # Compiled program file for LTX balls (single ball or combined)
    ├── song_name_Ball_1.prg.json # Per-ball program files (for multi-ball sequences)
    ├── song_name_Ball_2.prg.json # Per-ball program files (for multi-ball sequences)
    ├── song_name_Ball_3.prg.json # Per-ball program files (for multi-ball sequences)
    └── song_name.smproj      # Sequence Maker project file (openable by Sequence Maker)
```

### File Types and Extensions

| File Type                 | Extension         | Description                                      |
|---------------------------|-------------------|--------------------------------------------------|
| Sequence Design Files     | `.seqdesign.json` | High-level sequence design (multi-ball/advanced) |
| PRG JSON Files            | `.prg.json`       | Compiled program files for LTX balls             |
| Ball Sequence Files       | `.ball.json`      | Single ball color sequences                      |
| Sequence Maker Projects   | `.smproj`         | Project files openable by Sequence Maker        |
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
    *   **Primary Output:** A `.seqdesign.json` file, which is then compiled into per-ball `.prg.json` files using `compile_seqdesign.py`.
    *   **Schema:** Consult [`roocode_sequence_designer_tools/docs/seqdesign_json_schema.md`](roocode_sequence_designer_tools/docs/seqdesign_json_schema.md).

3.  **Project Files for Sequence Maker (`.smproj`):**
    *   **Trigger:** When the user requests a "project file" or a file "openable by Sequence Maker."
    *   **Primary Output:** A properly formatted `.smproj` file with populated timeline segments.
    *   **Critical:** Use [`generate_smproj_from_prg.py`](roocode_sequence_designer_tools/generate_smproj_from_prg.py) to convert compiled `.prg.json` files into `.smproj` format. Never create `.smproj` files with empty timeline segments.

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
        2.  **Current Best Practice (Programmatic Modification when a tool is close but misses a feature):**
            If a tool is close but misses a feature (e.g., color cycling for `convert_lyrics_to_ball.py`), you have several options:
            a.  **Programmatically modify the tool's output (Preferred Method):**
                i.  Run the existing tool (e.g., `convert_lyrics_to_ball.py`) with placeholder values to get a base file.
                    ```bash
                    python roocode_sequence_designer_tools/converters/convert_lyrics_to_ball.py input.lyrics.json temp_output.ball.json --color "255,255,255" --background "0,0,0" --pixels 1
                    ```
                ii. **Create a temporary Python script** (e.g., in the `sequence_projects/song_name/` directory or a more general `roocode_sequence_designer_tools/modifiers/` if reusable) to:
                    - Read the `temp_output.ball.json`.
                    - Iterate through its `segments`.
                    - Apply the desired logic (e.g., color cycling, complex data mapping).
                    - Write the final, modified content to the target `output.ball.json`.
                iii. Execute this script.
                iv. **This approach of creating and executing a script for modification is strongly preferred over embedding complex logic solely within the LLM's internal reasoning before a single `write_to_file` of the final state.** It promotes clarity, reusability, and auditable steps.
            b.  **Delegate Tool Enhancement:** If the missing feature seems generally useful for future tasks, you can ask the user if you should use the `new_task` tool to delegate the creation or enhancement of this feature in the original tool (e.g., adding a `--color-cycle` flag to `convert_lyrics_to_ball.py`) to Code mode. This is a good option for building a more robust permanent toolset.
            c.  **Manual Modification (Least Preferred for Complex Changes):** For very minor, trivial changes, direct `apply_diff` might be acceptable, but avoid this for anything involving loops, conditional logic, or significant structural changes to JSON.
*   **Execute Conversion:** Run the tool with correct paths and parameters.
    Example (for single color blue, off between words, 1 pixel):
    ```bash
    python roocode_sequence_designer_tools/converters/convert_lyrics_to_ball.py sequence_projects/song_name/song_name.lyrics.json sequence_projects/song_name/song_name.ball.json --color "0,0,255" --background "0,0,0" --pixels 1
    ```
*   **Verify Output:** Briefly check the generated `.ball.json` for correctness against the schema.

### 3. Sequence Design (`.seqdesign.json`) and Compilation (`.prg.json`)

Use this for multi-ball sequences or when advanced effects from the `.seqdesign.json` schema are needed.

*   **Understand Requirements:** Clearly define colors, timings, effects (fades, pulses, etc.), and pixel usage.
    *   **For Fades:** When a user requests a fade effect, Roocode should ask for the `start_color` and `end_color`. The `compile_seqdesign.py` script, in conjunction with `prg_generator.py`, will handle the smooth transition. The `steps_per_second` parameter for fades in the `.seqdesign.json` schema is not used by `compile_seqdesign.py` for generating `.prg.json` files intended for native PRG fade handling by `prg_generator.py`.
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

### 4. Multi-Ball Sequence Workflow (Complete Process)

For multi-ball sequences (e.g., alternating flash patterns, synchronized effects), follow this complete workflow:

*   **Step 1: Generate `.seqdesign.json`**
    *   Use Python scripts to generate complex, repetitive patterns programmatically
    *   Ensure `metadata.num_balls` is set correctly (e.g., 3 for 3-ball sequences)
    *   Use `ball_ids` in effect `params` to target specific balls (e.g., "ball1", "ball2", "ball3")

*   **Step 2: Compile to Combined `.prg.json`**
    ```bash
    python roocode_sequence_designer_tools/compile_seqdesign.py input.seqdesign.json combined.prg.json
    ```

*   **Step 3: Split into Per-Ball `.prg.json` Files**
    *   Create a script to filter the combined sequence by ball colors/IDs
    *   Generate separate `.prg.json` files for each ball (e.g., `project_Ball_1.prg.json`, `project_Ball_2.prg.json`)

*   **Step 4: Generate Proper `.smproj` File**
    ```bash
    python roocode_sequence_designer_tools/generate_smproj_from_prg.py \
        project_Ball_1.prg.json project_Ball_2.prg.json project_Ball_3.prg.json \
        --project-name "Project Name" --output project.smproj
    ```

*   **Step 5: Verify in Sequence Maker**
    *   ALWAYS test the generated `.smproj` file in Sequence Maker to ensure colors display correctly
    *   The file should show proper timeline segments with colors, not empty timelines

**Critical Notes:**
- Never create `.smproj` files manually with empty segments
- Always use `generate_smproj_from_prg.py` for proper segment structure
- Each timeline segment needs: `startTime`, `endTime`, `color` (RGB array), `pixels`, `effects` (empty array), `segment_type` ("solid")

## Tool Usage Guidelines (Reinforced)

1.  **ALWAYS first search for existing tools** in the `roocode_sequence_designer_tools` directory (especially in `converters/` and `effect_implementations/`) that can accomplish your task or part of it. This is especially critical for standard file conversions (e.g., lyrics to `.ball.json`, `.seqdesign.json` to `.prg.json`). **Prioritize using these tools over manual JSON construction via `write_to_file` or `apply_diff` for generating entire structured files.**

2.  **CRITICAL: Code Generation for Repetitive Sequence Content:**
    *   **When to Use Code Generation:** For any sequence file that contains large amounts of repetitive data, you MUST use Python code generation instead of manual writing. Examples include:
        - Ball sequences with >20 segments
        - Flasher patterns with repeated timing cycles
        - Color sequences with repetitive patterns
        - .smproj files with large timeline arrays
        - Any JSON file where you would be copy-pasting similar structures multiple times
    *   **Process:**
        1. Write a Python script that generates the complete JSON structure programmatically
        2. Use `execute_command` to run the script and write output directly to the target file
        3. NEVER paste large, script-generated outputs into `write_to_file` content tags
    *   **Exception:** Only write files manually when they are small, non-repetitive, or when editing documentation/code.

3.  **Augmenting Existing Tools / Handling Complex Manipulations:** If an existing tool provides a base output that needs further programmatic transformation (like color cycling, complex data mapping, or significant JSON restructuring), **the preferred method is to create a small, focused Python script** (either a temporary one in the project's directory or a reusable one in `roocode_sequence_designer_tools/modifiers/`) to perform these modifications. Execute this script after the base tool runs. This is more robust and maintainable than complex internal LLM logic. Note such limitations or patterns for potential future enhancements to the base tool itself or for the creation of new, dedicated tools.

4.  **Creating New Reusable Tools:** If a new, generally useful utility or a complex transformation not covered by existing tools is needed, propose and create a well-documented Python script within `roocode_sequence_designer_tools/`. Ensure it's added to `tools_lookup.json` if appropriate.

5.  When using CLI tools, always verify their expected arguments (e.g., via `--help` or by reading their source/documentation).

6.  **Temporary vs. Reusable Scripts:**
    *   **Temporary Scripts:** For modifications highly specific to one project or sequence, a script can be created within that project's subfolder (e.g., `sequence_projects/song_name/apply_custom_logic.py`).
    *   **Reusable Tools:** If the logic is likely to be useful for other sequences, create it as a new tool in `roocode_sequence_designer_tools/` (e.g., `roocode_sequence_designer_tools/modifiers/apply_color_cycle.py`) with proper documentation.

## Token Efficiency Guidelines

*   **Minimize Redundant Data:** NEVER read or display entire large JSON files in your responses. Show only small, relevant samples or summaries.
*   **Focused Prompts:** Ask for all necessary information from the user in a single, clear step if possible.
*   **Direct Tools:** Use the most direct tool for the job (e.g., `align_lyrics.py` over older methods).

## Self-Improvement Mechanism

After completing any task, especially when creating a new sequence:

1.  **Reflect on the Process:** Consider the overall efficiency of the task execution.
2.  **Journaling Improvements:**
    *   Maintain a timestamped journal/history of self-identified improvements. This could be a dedicated section at the end of this document or a separate `self_improvement_log.md` file within the `roocode_sequence_designer_tools/docs/` directory.
    *   This journal helps track progress, ensures learning retention, and avoids repeating past inefficiencies.
    *   **Entry for 5/30/2025:** Learned to favor external script creation (temporary or reusable) for programmatic modifications of tool outputs or complex JSON manipulations, rather than internal-only logic followed by a direct `write_to_file` of the final state. This applies even for seemingly simple, one-off modifications, as it aligns better with the tool-building persona and improves process clarity. Temporary scripts in project folders are acceptable for highly task-specific logic.
    *   **Entry for 5/30/2025 (Interaction 2):** Encountered and resolved argument errors for `convert_lyrics_to_ball.py` (used `--word-color` and `--gap-color` instead of `--default-color` and `--background`) and `apply_rgb_cycling_and_off_states.py` (incorrectly provided `--colors` and `--off-color` which are not accepted arguments as the script uses hardcoded values). Reinforces the need to carefully check tool arguments, potentially by reading script source or `--help` output, before execution. Updated `sequence_designer_mode_instructions.md` to reflect correct argument for `convert_lyrics_to_ball.py`.
3.  **Selective Improvement:**
    *   If the process felt optimally efficient for the given task, explicitly documenting self-improvement for that specific interaction is not mandatory.
    *   The primary goal is to capture and codify improvements when clear inefficiencies are identified or when a better approach becomes evident post-task.
4.  **Identify Inefficiencies:** If the task could have been performed more efficiently (e.g., fewer steps, better tool utilization, clearer initial understanding needed), pinpoint these specific areas. Note if you had to perform excessive manual data manipulation that a tool should ideally handle.
5.  **Update Knowledge (Internal):** Mentally document more efficient approaches.
6.  **CRITICAL FINAL STEP - Codify Learnings:** If improvements to workflows, tool usage, or understanding are identified (especially after user feedback or encountering inefficiencies):
    *   **Actively update these operational instructions (`sequence_designer_mode_instructions.md`) and/or the high-level directives in `.roomodes`** to codify these learnings.
    *   Update the self-improvement journal with the timestamped learning.
    *   Propose these documentation changes as part of the task completion or as a follow-up action. This ensures continuous, tangible improvement.
7.  **Apply Learnings:** Prioritize the most efficient and tool-driven workflows, informed by the updated documentation and journaled learnings, in future interactions.
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

## Clarification on Global Instruction #3 ("Simplicity is key!")

Global Instruction #3 states: *"Simplicity is key! Never over-engineer the solutions. Instead go for the simplest possible solution while maintaining functionality."*

In the context of Roocode's operations, especially when dealing with programmatic modifications of sequence files or complex JSON structures:
*   **Creating a small, well-defined Python script is often the *simplest and clearest* path.** It encapsulates logic, makes the process auditable, and can be easier to debug and maintain than complex, multi-step manipulations performed via direct `apply_diff` or internal LLM reasoning that culminates in a single large `write_to_file`.
*   **It is generally *not* considered over-engineering** to create such a script if it improves the robustness, clarity, or reusability of the sequence design process, or if it contributes to Roocode's toolset (either as a temporary helper or a new permanent tool).
*   The "simplest possible solution" should be evaluated in terms of overall workflow clarity and maintainability, not just the raw number of tool calls in a single interaction.

## Song Data Persistence (CRITICAL)

*Added: 2026-04-03*

Every song project has a `song_data.json` file that stores all gathered data persistently. This is managed by [`roocode_sequence_designer_tools/song_data_manager.py`](roocode_sequence_designer_tools/song_data_manager.py).

### Why This Matters

Previously, every time a new session started, lyrics had to be re-extracted, audio had to be re-analyzed, and all prior work was lost. The `song_data.json` system ensures that **once data is gathered for a song, it is saved permanently** and never needs to be re-gathered (unless explicitly requested by the user).

### What Gets Stored

The `song_data.json` file stores:
- **Metadata:** Song title, artist, audio file path, duration, genre
- **Lyrics:** Raw text, synced/aligned lyrics data, word count, file paths
- **Audio Analysis:** Tempo, time signature, key, beats, downbeats, sections, energy profile, onsets, spectral features
- **Sequence Versions:** All versions of sequences created for this song, with descriptions, file references, tags, and derivation history

### Workflow

1. **Before ANY work on a song:** Check if `song_data.json` exists and what data is already available:
   ```bash
   python -m roocode_sequence_designer_tools.song_data_manager sequence_projects/<song_name> show
   ```

2. **After extracting lyrics:** Save immediately:
   ```bash
   python -m roocode_sequence_designer_tools.song_data_manager sequence_projects/<song_name> set lyrics.raw_text '<text>'
   python -m roocode_sequence_designer_tools.song_data_manager sequence_projects/<song_name> set lyrics.synced_lyrics_file 'song_name.synced_lyrics.json'
   ```

3. **After audio analysis:** Save all results:
   ```bash
   python -m roocode_sequence_designer_tools.song_data_manager sequence_projects/<song_name> set audio_analysis.estimated_tempo 120
   python -m roocode_sequence_designer_tools.song_data_manager sequence_projects/<song_name> set audio_analysis.beats '[0.5, 1.0, 1.5, ...]'
   ```
   For large data (beats arrays, sections), you can also write a small Python script that loads the analysis report and saves relevant fields to song_data.json.

4. **Check before re-doing work:**
   ```bash
   python -m roocode_sequence_designer_tools.song_data_manager sequence_projects/<song_name> has lyrics.synced_lyrics_data
   python -m roocode_sequence_designer_tools.song_data_manager sequence_projects/<song_name> has audio_analysis.beats
   ```

## Sequence Versioning

*Added: 2026-04-03*

Every sequence created for a song MUST be registered as a version with a clear, descriptive description. This enables:
- Users to compare different versions at a glance
- The Sequence Maker GUI to display version descriptions when loading sequences
- Tracking of how versions relate to each other (derivation history)

### Registering a Version

```bash
python -m roocode_sequence_designer_tools.song_data_manager sequence_projects/<song_name> register-version v1_beat_pulse \
  --description "Beat-synchronized pulse pattern: Red pulses on every beat during verses, blue pulses on downbeats during choruses. Energy-mapped brightness makes high-energy sections brighter. Background is dim purple." \
  --files '{"seqdesign": "song_v1_beat_pulse.seqdesign.json", "prg": "song_v1_beat_pulse.prg.json", "smproj": "song_v1_beat_pulse.smproj"}' \
  --tags "beat-sync,energy-mapped,verse-chorus-contrast"
```

### Description Best Practices

The description should answer:
1. **What does it look like?** — Describe the visual effect in plain language
2. **What music features drive it?** — Beats, lyrics, sections, energy?
3. **How does it differ from other versions?** — What's unique about this approach?
4. **What colors are used?** — Primary color palette

Example good description:
> "Lyric-driven rainbow: Each word triggers a color flash cycling through the rainbow spectrum. Between words, balls fade to black. Chorus sections use brighter, more saturated colors. Designed for 3 balls with round-robin word assignment."

### Listing Versions

```bash
python -m roocode_sequence_designer_tools.song_data_manager sequence_projects/<song_name> list-versions
```

## Music Analysis Capabilities

*Added: 2026-04-03*

The Sequence Designer can extract and use the following audio features (via `extract_audio_features.py` and `audio_analysis_report.py`):

| Feature | Description | Use in Sequences |
|---------|-------------|-----------------|
| Beat times | Timestamps of all detected beats | Pulse/flash on beat, beat-sync patterns |
| Downbeat times | Timestamps of measure starts | Accent effects on downbeats |
| Tempo (BPM) | Estimated beats per minute | Calculate timing intervals |
| Time signature | Estimated time signature (e.g., 4/4) | Group beats into measures |
| Sections | Labeled sections with start/end times | Section-based color themes |
| Energy profile | Per-frame energy values | Brightness/intensity mapping |
| Onset times | Note onset timestamps | Rhythmic flash effects |
| Spectral centroid | Brightness of sound over time | Map sound brightness to color brightness |
| Spectral contrast | Tonal vs noise content | Distinguish melodic vs percussive sections |
| Chroma | Pitch class profiles | Harmonic-based color mapping |
| Key | Estimated musical key | Thematic color selection |

### Pattern Types for Music-Driven Sequences

| Pattern | Trigger | Description |
|---------|---------|-------------|
| `pulse_on_beat` | Beats/downbeats | Flash a color on each beat |
| `BeatSync` | Beats | Synchronize any effect to beats |
| `LyricHighlight` | Specific words | Highlight when certain words are sung |
| `WarningThenEvent` | Lyrics/beats/times | Warning flash before main event |
| `section_theme_energy` | Sections + energy | Color themes per section with energy modulation |
| `apply_section_theme` | Sections | Simple color per section |
| `apply_beat_pattern` | Beats | Pulse/toggle/fade patterns on beats |

## Additional Resources
- [`roocode_sequence_designer_tools/docs/lyrics_extraction_guide.md`](roocode_sequence_designer_tools/docs/lyrics_extraction_guide.md)
- [`roocode_sequence_designer_tools/docs/lyrics_extraction_efficiency.md`](roocode_sequence_designer_tools/docs/lyrics_extraction_efficiency.md)
- [`roocode_sequence_designer_tools/docs/seqdesign_json_schema.md`](roocode_sequence_designer_tools/docs/seqdesign_json_schema.md)
- [`roocode_sequence_designer_tools/docs/ball_sequence_format.md`](roocode_sequence_designer_tools/docs/ball_sequence_format.md)
- [`roocode_sequence_designer_tools/song_data_manager.py`](roocode_sequence_designer_tools/song_data_manager.py) — Song data persistence and versioning
- [`roocode_sequence_designer_tools/tools_lookup.json`](roocode_sequence_designer_tools/tools_lookup.json) — Complete tool and effect catalog

---
**Last Updated:** 2026-04-03 11:47 UTC-6

By following these updated instructions, future Roocode instances will be better equipped to handle sequence design tasks efficiently and accurately, with persistent song data that eliminates redundant work and versioned sequences with clear descriptions.