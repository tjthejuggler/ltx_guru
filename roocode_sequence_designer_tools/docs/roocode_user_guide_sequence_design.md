# Roocode Sequence Designer: User Guide

Welcome to Roocode Sequence Designer! This guide will help you understand how to interact with Roocode to create and manage your custom light sequences.

## 1. Introduction to Roocode Sequence Designer

Roocode is your conversational assistant for designing intricate light sequences for your projects, whether it's for a juggling act, a stage performance, or any creative endeavor involving programmable lights.

You'll tell Roocode what you want your lights to do using natural language, and Roocode will translate your instructions into a special design file. The primary goal is to create a **`.seqdesign.json`** file. This file contains all the details of your light sequence, which can then be "compiled" by another tool into a `.prg.json` format that your lighting hardware can understand and play.

## 2. Getting Started

To begin designing a light sequence, you'll start a conversation with Roocode.

**Initiating a Design Task:**
You can start by saying something like:
*   "Roocode, let's design a new light sequence."
*   "Hey Roocode, I want to create a light show for my new song."
*   "Roocode, help me make a sequence for my juggling act."

**Initial Information:**
Roocode will likely ask for some initial details to set up your project:
*   **Project Name:** A general name for the overall project (e.g., "My Juggling Show," "Summer Concert Series").
*   **Sequence Name:** A specific name for this particular light sequence (e.g., "Opening Act v1," "Firefly Dance").
*   **Audio File (Optional):** If your sequence is synchronized to music, you'll tell Roocode the name of the audio file (e.g., `my_song.mp3`, `juggling_intro_music.wav`). Roocode will expect this file to be available.

**Directory Structure:**
Roocode will help manage your sequence design files by organizing them into a standard directory structure. For a project named "My_Juggling_Show" and a sequence named "Opening_Act_v1", the files would typically be stored in:
`sequence_projects/My_Juggling_Show/Opening_Act_v1/`
This directory will contain your `Opening_Act_v1.seqdesign.json` file and potentially the associated audio file or its analysis.

## 3. Basic Sequence Creation

Once the basics are set up, you can start telling Roocode how you want your sequence to look and feel.

**Defining Overall Sequence Properties (Metadata):**
You can set general properties for your sequence:
*   "Set the total duration to 60 seconds."
*   "The audio file for this sequence is 'juggling_intro_music.mp3'."
*   "Let's use 4 pixels by default for all effects."
*   "The refresh rate should be 100 Hz." (This tells the compiler how many light updates per second are expected).

**Adding Effects to the Timeline:**
Effects are the core of your light sequence. You describe them conversationally:
*   "Add a fade effect from 0 seconds to 5 seconds, going from black to bright blue."
*   "From 5 seconds to 25 seconds, I want a yellow pulse on every beat. Make each pulse last 0.15 seconds."
*   "Make a solid green color from 30 seconds to 45 seconds."
*   "At 10 seconds, add a strobe effect for 2 seconds, flashing red and white at 5 Hz."

Roocode will take these instructions and translate them into structured entries within your `.seqdesign.json` file. Each effect will have a start time, end time (or duration), and specific parameters like colors.

## 4. Understanding Effects (`tools_lookup.json`)

Roocode has a built-in knowledge base of predefined effect types. This information is conceptually stored in a file like [`tools_lookup.json`](./tools_lookup.json).

**Asking About Available Effects:**
You can ask Roocode what it can do:
*   "Roocode, what effects can you do?"
*   "Tell me about the 'fade' effect."
*   "What parameters does the 'strobe' effect take?"

Roocode will then list the available effects or describe a specific one, including the parameters it needs. For example, for a 'fade' effect, it would tell you it needs a start color and an end color. The `prg_generator.py` script handles the smooth interpolation automatically when creating the final `.prg` file. An optional `steps_per_second` parameter exists in the schema but is not used by `compile_seqdesign.py` for generating `.prg.json` files intended for `prg_generator.py`'s native fade handling; it might be relevant for other visualizers or direct effect implementations.

## 5. Specifying Effect Parameters

When you add an effect, Roocode needs to know all its required details.

**Roocode Asks for Missing Information:**
If you don't provide all necessary parameters in your initial command, Roocode will ask for them:
*   **User:** "Add a fade effect from 0 to 5 seconds."
*   **Roocode:** "Okay, for the fade effect, what should be the starting color?"
*   **User:** "Start with black."
*   **Roocode:** "And what should be the ending color?"
*   **User:** "End with red."

**Specifying Colors:**
You can specify colors in various ways:
*   **By name:** "make it red," "use cyan," "the color should be orange."
*   **By hex code:** "use hex code #00FF00 for green," "set the color to #FF00FF."
*   **By RGB values:** "RGB 0,0,255 for blue," "the color is 255, 165, 0."

**Specifying Timing:**
You can define when effects happen and for how long:
*   **Start and End Times:** "From 2 seconds to 7.5 seconds..."
*   **Start Time and Duration:** "Start at 10 seconds and run for 3 seconds."

## 6. Using Audio-Dependent Effects

Some effects are designed to work closely with an audio track. Roocode will use an analysis of the audio file you provided (like beat timings or musical section markers) to drive these effects.

**Examples of Audio-Dependent Commands:**
*   "For the section from 10 to 30 seconds, apply a theme with a base color of purple for the 'verse' sections and orange for 'chorus' sections. Map the audio energy to brightness." (This uses an effect like `apply_section_theme_from_audio`).
*   "I want a blue pulse on every downbeat from the start of the song until 15 seconds. Each pulse should be 0.2 seconds long." (This uses an effect like `pulse_on_beat`).
*   "At 45 seconds, when the lyrics say 'shine', I want a quick flash of bright white that smoothly fades back to blue over 2 seconds." (This uses an effect like `snap_on_flash_off`).

Roocode will use the pre-analyzed data from your audio file (e.g., beat locations, section labels like 'verse', 'chorus') to place and shape these effects accurately.

## 7. Editing Existing Sequences

You can always come back and modify your designs.

**Loading an Existing Design:**
*   "Roocode, load the 'Opening_Act_v1' sequence from the 'My_Juggling_Show' project."
*   "Let's work on the 'Chorus_Highlight' sequence in the 'Band_Performance' project."

**Modification Commands:**
Once a sequence is loaded, you can ask Roocode to make changes:
*   "Change the color of the 'intro_fade' effect (that's the first effect) to green."
*   "Make the 'verse1_pulse' effect 2 seconds longer by extending its end time."
*   "Remove the 'chorus_solid' effect."
*   "Add a new strobe effect after 'verse1_pulse' from 25 to 30 seconds, strobing red and white at 10 Hz."
*   "In the 'intro_fade' effect, change the start color to dark blue."

Roocode will identify the effect you're referring to (you might need to be specific if there are many similar effects) and update its properties in the `.seqdesign.json` file.

## 8. Creating Variations

Sometimes you'll want to create a new version of a sequence based on an existing one.

**Examples of Creating Variations:**
*   "Take the current sequence and create a variation called 'Opening_Act_v1_blue_theme'. In this new version, I want you to try and shift all the primary colors towards blue." (This is a more conceptual command; Roocode would need some internal logic to interpret "shift towards blue" for various colors).
*   "Make a copy of this sequence called 'Fast_Version' and in it, make all effects happen twice as fast, and shorten their durations by half."

Roocode would save the new variation as a separate `.seqdesign.json` file, allowing you to experiment without losing your original work.

## 9. Saving and Compiling

**Saving Your Design:**
Roocode will typically save the `.seqdesign.json` file automatically as you make changes, or you can explicitly ask:
*   "Roocode, save the current sequence."

**Compiling Your Design:**
Once you're happy with your `.seqdesign.json` file, you need to compile it into a format your lighting hardware can use (a `.prg.json` file).
*   "Roocode, compile this sequence."
*   "Compile 'Opening_Act_v1' from 'My_Juggling_Show'."

Roocode will then conceptually invoke a separate tool, like the [`compile_seqdesign.py`](./compile_seqdesign.py) script, providing it with your `.seqdesign.json` file and any other necessary information (like the path to audio analysis files).

**Manual Compilation (Command Line):**

If you need to compile a `.seqdesign.json` file manually using the command line (for example, if Roocode's automated process encounters an issue or for advanced use), you should use the following method. This ensures the script runs correctly within its package structure.

1.  **Navigate to the project root directory:** Open your terminal in the root directory of the `ltx_guru` project (or wherever the `roocode_sequence_designer_tools` package is located).
2.  **Run as a module:** Execute the script as a Python module using the `-m` flag.
3.  **Provide paths:** The script takes two main arguments:
    *   `input_seqdesign_json_path`: The path to your `.seqdesign.json` file.
    *   `output_prg_json_path`: The desired path for the compiled `.prg.json` output file.

**Command Format:**
```bash
python -m roocode_sequence_designer_tools.compile_seqdesign <path_to_your_input.seqdesign.json> <path_to_your_output.prg.json>
```

**Example:**
Assuming your input file is `sequences/my_sequence.seqdesign.json` and you want the output in the same directory:
```bash
python -m roocode_sequence_designer_tools.compile_seqdesign sequences/my_sequence.seqdesign.json sequences/my_sequence.prg.json
```
This command will compile `my_sequence.seqdesign.json` and create `my_sequence.prg.json`.

**Compilation Feedback:**
Roocode will report back on the compilation process:
*   "Okay, I've compiled 'Opening_Act_v1.seqdesign.json' to 'Opening_Act_v1.prg.json' successfully."
*   "There was an error during compilation: [Error message from compiler]. You might need to check the parameters for the 'main_strobe' effect."

## 10. Creating Single-Ball Sequences for Sequence Maker

If your goal is to create a sequence for a single LTX ball that can be directly imported into the `sequence_maker` application (using "File -> Import -> Import Ball Sequence"), there's a specific final output format required: a **`.ball.json`** file.

Roocode can guide you through this process:

1.  **Design Your Sequence**: Use Roocode as usual to define your effects on the timeline. This will result in a `.seqdesign.json` file.
    *   Example: "Roocode, for 'MySong', make the ball yellow every time the word 'you' is sung."

2.  **Compile to `.prg.json`**: Roocode will first compile your `.seqdesign.json` into the standard `.prg.json` format.
    *   Roocode internal step: Uses `compile_seqdesign.py`.

3.  **Convert `.prg.json` to `.ball.json`**: This is the crucial step for `sequence_maker` compatibility.
    *   **Roocode Command**: "Roocode, now convert the compiled program for 'MySong' into a `.ball.json` file suitable for single ball import."
    *   Roocode will use the `roocode_sequence_designer_tools/converters/convert_prg_to_ball.py` script to perform this conversion.
    *   This script takes the `.prg.json` file as input and produces a `.ball.json` file. It will attempt to carry over relevant metadata, including the audio file path (often inferred from the original `.seqdesign.json`).

4.  **Result**: You will get a `[sequence_name].ball.json` file in your project directory (e.g., `sequence_projects/MySong/MySong.ball.json`). This is the file you should import into `sequence_maker`.

**Key File Formats in this Workflow:**

*   Input to Roocode: Your verbal descriptions.
*   Intermediate Design: `.seqdesign.json`
*   Intermediate Compiled: `.prg.json`
*   **Final Output for `sequence_maker` single ball import: `.ball.json`**

Make sure to specify to Roocode if your intended final output is a `.ball.json` for `sequence_maker` import.

## 11. File Types in the LTX Guru Ecosystem

Throughout your work with Roocode Sequence Designer, you'll encounter various file types with standardized extensions:

| File Type | Extension | Description |
|-----------|-----------|-------------|
| Sequence Design Files | `.seqdesign.json` | High-level sequence design files that you create with Roocode |
| PRG JSON Files | `.prg.json` | Compiled program files for LTX balls (created from .seqdesign.json) |
| Raw Song Lyrics | `.lyrics.txt` | Raw lyrics text files (input for lyrics processing) |
| Timestamped Song Lyrics | `.synced_lyrics.json` | Timestamped/aligned lyrics (output from lyrics processing) |
| Ball Color Change Sequences | `.ballseq.json` | Ball-specific color sequences |
| Audio Analysis Reports | `.analysis_report.json` | Audio analysis data from the audio analysis tool |
| Beat Patterns | `.beatpattern.json` | Beat-synchronized patterns |
| Section Themes | `.sectiontheme.json` | Section-based color themes |

When working with these files, always maintain the correct file extension to ensure compatibility with all tools in the ecosystem.

## 10. (Briefly) Proposing New Effects (Tool Creation Workflow)

What if you want an effect that Roocode doesn't know about?

You can describe the effect you're imagining:
*   **User:** "Roocode, I want an effect that makes the lights twinkle like stars, with random pixels lighting up in a soft white color and then fading out slowly."

If Roocode doesn't recognize this as a known effect, it might respond:
*   **Roocode:** "That sounds like an interesting effect! I don't have a 'star twinkle' effect right now. Would you like me to help you define it? We can give it a name and list the parameters it would need, like 'twinkle_color', 'density_of_stars', and 'fade_out_speed'."

If you agree, Roocode would guide you through defining the new effect. This definition (name, parameters, description) would conceptually be added to its knowledge base (e.g., the [`tools_lookup.json`](./tools_lookup.json) file).

**Important Note:** Roocode can help *define* the new effect, but a human developer would then need to write the actual Python code to implement the logic for this new effect and integrate it into the compiler system. Once implemented, the new effect would become available for everyone to use.

---
**Last Updated:** 2025-06-06 12:06 UTC+7

This guide provides a conceptual overview of how you might interact with Roocode Sequence Designer. As the system is developed, specific commands and capabilities may evolve. Happy sequencing!