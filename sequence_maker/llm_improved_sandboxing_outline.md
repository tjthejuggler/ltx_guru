Okay, thank you for providing the detailed context, code snippets, test results, and insightful feedback. This is extremely helpful.

Based on the analysis of the project context, the recent debugging journey, the provided test cases (successes and failures), and your goals for robustness and future iterative capabilities, here is a detailed multi-step plan to improve the Sequence Maker LLM integration. This plan aims to address the identified issues (sandbox errors, tool confusion, lack of error recovery) and streamline the system for better reliability and future expansion.

**Guiding Principles:**

1.  **Prioritize the Sandbox:** Make `execute_sequence_code` the primary mechanism for sequence generation, especially for anything beyond the simplest, most direct commands.
2.  **Simplify Tooling:** Reduce the number of specific tools exposed directly to the LLM where sandbox code offers equivalent or greater flexibility. Keep only essential, highly reliable, high-level tools.
3.  **Enhance Robustness:** Implement mechanisms for detecting and potentially recovering from errors in tool/sandbox execution.
4.  **Improve LLM Guidance:** Refine the system prompt to be clearer, more focused on the sandbox, and provide better examples and constraints.
5.  **Prepare for Iteration:** Lay the groundwork for future capabilities where the LLM can evaluate its own output.

---

**Multi-Step Improvement Plan:**

**Phase 1: Core Bug Fixes & Sandbox Stabilization** [COMPLETED]

**Step 1: Permanently Fix the Sandbox `_print_` Error** [COMPLETED]

*   **Problem:** Test 5 failed with `NameError: name '_print_' is not defined`. This indicates `RestrictedPython`'s internal mechanism for handling the `print()` built-in is not correctly configured in the sandbox environment, despite previous fixes attempting to address it by providing `safe_print` as `print`.
*   **Analysis:** `RestrictedPython` requires specific guard functions for built-ins it handles. While we provide `safe_print` for the `print` *name*, the compiled code likely uses an internal reference like `_print_`. We need to ensure this internal reference points to a compatible guard. `safe_builtins` *should* provide this, but something is still amiss in our setup.
*   **Action:** Modify `sandbox_manager.py` -> `_create_sandbox_globals`.
    *   **Ensure `safe_builtins` is the Base:** Double-check that `sandbox_globals` starts *directly* with `safe_builtins.copy()`.
    *   **Explicitly Add `_print_` Guard:** Even though `safe_builtins` should handle it, let's explicitly add the standard `RestrictedPython` print guard to the `sandbox_globals`. This guard is usually obtained from `RestrictedPython.PrintCollector`.
    ```python
    # In sandbox_manager.py, near imports
    from RestrictedPython.PrintCollector import PrintCollector

    # In SandboxManager._create_sandbox_globals method
    def _create_sandbox_globals(self, safe_wrappers: Dict[str, Any], safe_utilities: Dict[str, Any],
                                available_context: Dict[str, Any]) -> Dict[str, Any]:
        # Start with a minimal set of safe builtins
        sandbox_globals = safe_builtins.copy()

        # *** Add this line ***
        # Ensure RestrictedPython's internal print mechanism is correctly wired
        # This links the execution of 'print()' statements to a safe collector.
        sandbox_globals['_print_'] = PrintCollector

        # Add safe wrappers
        sandbox_globals.update(safe_wrappers)

        # Add safe utilities (including our logging 'print' function)
        sandbox_globals.update(safe_utilities)
        # Make sure 'print' still points to our safe_print for logging:
        if 'print' not in safe_utilities: # Should already be there from _create_safe_utilities
             self.logger.warning("safe_print utility missing, adding fallback.")
             safe_utilities['print'] = self._create_safe_utilities()['print'] # Ensure it's created
             sandbox_globals['print'] = safe_utilities['print']
        else:
             sandbox_globals['print'] = safe_utilities['print'] # Explicitly ensure it's set

        # ... (rest of the method adding other builtins, math, context) ...

        return sandbox_globals
    ```
    *   **Modify `safe_print`:** Ensure `safe_print` in `_create_safe_utilities` *only* logs and returns `None`. It should *not* be the `PrintCollector` itself. The `_print_` key handles the internal execution, while the `print` key provides our logging wrapper.
    ```python
     # In SandboxManager._create_safe_utilities
     def safe_print(*args, **kwargs):
         try:
             output = " ".join(str(arg) for arg in args)
             self.logger.info(f"Sandbox print: {output}")
             # IMPORTANT: Return None, as expected by standard print
             return None
         except Exception as e:
             self.logger.error(f"Error in safe_print: {e}", exc_info=True)
             return None # Return None even on error
     safe_utilities["print"] = safe_print
     # Do NOT add safe_utilities["_print_"] = safe_print here. Let _create_sandbox_globals handle _print_.
    ```
*   **Verification:** Rerun Test 5. The `_print_` error should be gone. The `print()` call in the sandbox code should now log correctly via `safe_print` without crashing execution.

**Step 2: Stabilize Basic Tool Argument Handling (`clear_timeline` Example)** [COMPLETED]

*   **Problem:** Test 3 failed because the LLM called `clear_timeline` with empty arguments (`{}`), but the tool requires `timeline_index`. Test 4 succeeded when the LLM provided the correct argument.
*   **Analysis:** The LLM is inconsistently extracting/providing required arguments based on the schema. While the handler correctly reported the error, the LLM didn't fix it. This points to LLM interpretation issues or potential schema/prompt confusion.
*   **Action:**
    1.  **Verify `clear_timeline` Schema:** In `tool_manager.py` -> `timeline_functions`, double-check the schema for `clear_timeline`. Ensure `timeline_index` is listed in the `"required"` array. (It currently is, which is good).
    ```json
     {
         "name": "clear_timeline",
         "description": "Clear all segments from a timeline",
         "parameters": {
             "type": "object",
             "properties": {
                 "timeline_index": {
                     "type": "integer",
                     "description": "Index of the timeline to clear"
                 }
             },
             "required": ["timeline_index"] // Ensure this is present
         }
     }
    ```
    2.  **Strengthen `_handle_function_call` Parsing (Minor):** While the JSON parsing seems okay, add logging *before* `json.loads` to see the *exact* string being parsed, especially when errors occur. The current logging might truncate it.
    3.  **Refine System Prompt (See Step 6):** Explicitly address potential confusion between `clear_timeline(index)` and `clear_all_timelines()`.
    4.  **Consider Tool-Specific Handlers:** Currently, `clear_timeline` is likely handled via the sandbox wrappers (`safe_clear_timeline`) even when called directly as a tool. This might add unnecessary layers. Consider adding a *direct* handler in `LLMToolManager` specifically for the `clear_timeline` *tool call* (if it's kept after Step 4). This handler would *only* be used for direct tool calls, not sandbox execution.
        ```python
        # In LLMToolManager.__init__
        # self.register_action_handler("clear_timeline", self._handle_clear_timeline_direct) # Add this if keeping the tool

        # Add a new method to LLMToolManager
        # def _handle_clear_timeline_direct(self, parameters):
        #     self.logger.debug("Handling direct call to clear_timeline tool")
        #     timeline_index = parameters.get("timeline_index")
        #     if timeline_index is None:
        #         return {"success": False, "error": "Missing required parameter: timeline_index"}
        #
        #     # Basic validation (can reuse parts of safe_clear_timeline's validation)
        #     if not isinstance(timeline_index, int):
        #         return {"success": False, "error": "TypeError: timeline_index must be an integer"}
        #     # ... add bounds checking ...
        #
        #     try:
        #         # Directly call the application logic (or a simplified wrapper)
        #         timeline = self.app.timeline_manager.get_timeline(timeline_index)
        #         if not timeline:
        #              return {"success": False, "error": f"Timeline {timeline_index} not found"}
        #         timeline.clear()
        #         self.app.timeline_manager.timeline_modified.emit(timeline) # Ensure UI updates
        #         return {"success": True, "message": f"Timeline {timeline_index} cleared."}
        #     except Exception as e:
        #         self.logger.error(f"Error in _handle_clear_timeline_direct: {e}", exc_info=True)
        #         return {"success": False, "error": f"Error clearing timeline: {str(e)}"}
        ```
        *Note: This adds complexity. Only do this if `clear_timeline` is kept as a distinct tool AND the sandbox wrapper path proves problematic for direct calls.*
*   **Verification:** Test variations of asking the LLM to clear a specific timeline. See if it more reliably provides the `timeline_index`.

**Phase 2: Enhancing Robustness and Streamlining** [COMPLETED]

**Step 3: Implement Error Handling & Retry Loop in `LLMManager`** [COMPLETED]

*   **Problem:** Failures (like Test 3 and Test 5) are reported but not acted upon. The LLM doesn't know its attempt failed or why.
*   **Analysis:** The system needs a feedback loop. When a function call returns `success: False`, the `LLMManager` should intercept this, construct a new prompt explaining the failure, and ask the LLM to try again.
*   **Action:** Modify `llm_manager.py` -> `_process_response`.
    1.  Inside the `if function_name:` block, examine the `result` from `self.tool_manager._handle_function_call`.
    2.  If `result.get('success') is False`:
        *   Log the failure clearly.
        *   **Construct a new prompt** to send back to the LLM. This prompt should include:
            *   The original user request.
            *   The function call the LLM attempted (`function_name`, `arguments`).
            *   The error message received (`result.get('error')`, `result.get('error_details')`).
            *   A clear instruction to try again, correcting the call based on the error. Example: "Your previous attempt to call function '{function_name}' failed with the error: '{error_message}'. Please analyze the error and the function definition, then provide a corrected function call or Python code."
        *   **Maintain Context:** Add the failed function call and its result to the ongoing chat history (as a system message) so the LLM has context for the retry.
        *   **Re-invoke `send_request`:** Call `self.send_request` with this new corrective prompt. Include the existing chat history (including the failure message).
        *   **Implement Retry Limit:** Add a counter (e.g., in the `send_request` call or as a state variable) to prevent infinite loops. Limit retries to 1 or 2 attempts. If it still fails, report the final error to the user.
    3.  If `result.get('success') is True`: Proceed as normal (emit signals, save version).
*   **Verification:** Rerun Test 3. The LLM should initially fail (missing argument). The manager should catch this, send a corrective prompt. The LLM *should* then hopefully provide the correct call `clear_timeline(timeline_index=2)`. Rerun Test 5. The LLM should fail (`_print_` error initially, assuming Step 1 wasn't perfect, or maybe a *new* error). The manager should report the Python error back, asking the LLM to fix its code.

**Step 4: Review and Consolidate LLM Tools** [COMPLETED]

*   **Problem:** Potential tool redundancy (`find_first_word` vs. sandbox) and confusion between similar tools (`clear_timeline` vs. `clear_all_timelines`, `create_segment_for_word` vs. sandbox).
*   **Analysis:** Simplifying the toolset makes it easier for the LLM and reduces maintenance. The sandbox is powerful; leverage it.
*   **Action:**
    1.  **Identify Redundant Tools:**
        *   `find_first_word`: Definitely redundant. Sandbox code can easily get `get_lyrics_info()` or `get_all_word_timestamps()` and find the first entry.
        *   `get_word_timestamps` (as a direct tool): Likely redundant. The sandbox function `get_word_timestamps` is more flexible.
        *   `get_lyrics_info` (as a direct tool): Might be redundant if `get_all_word_timestamps` is added to the sandbox, but could be kept for simple queries. Evaluate based on LLM usage.
        *   `create_segment`, `modify_segment`, `delete_segment` (as direct tools): Redundant. These are the core functions *within* the sandbox. Calling them directly bypasses the sandbox's power.
    2.  **Identify Essential/Reliable Tools:**
        *   `execute_sequence_code`: Absolutely essential. The core of the new approach.
        *   `create_segment_for_word`: Test 1 showed it works well for its specific, simple use case. *Keep this* as a high-level shortcut, but emphasize in the prompt *when* to use it vs. the sandbox.
        *   `clear_all_timelines`: Useful high-level command. Keep.
        *   `clear_timeline`: Keep *if* Step 2 shows direct calls are still preferred by the LLM sometimes, otherwise consider removing and forcing sandbox usage (`clear_timeline(index)`) for single clears.
        *   Audio tools (`play_audio`, etc.): Keep, as they control app state outside sequence data.
        *   Pattern tools (`apply_beat_pattern`, etc.): Review. If these implement complex logic not easily replicated by simple sandbox code, keep them. If they are simple patterns, encourage sandbox usage instead.
        *   Music data tools (`get_tempo`, etc.): Keep, provide context.
    3.  **Update `LLMToolManager`:**
        *   Remove the function definitions (from properties like `timeline_functions`) for deprecated tools.
        *   Remove the corresponding `register_action_handler` calls and handler methods (`_handle_...`).
*   **Verification:** Check the available functions logged by `LLMManager` upon sending a request. Ensure only the intended, streamlined set is present. Test LLM interactions to see if it correctly uses the remaining tools and the sandbox.

**Step 5: Enhance Sandbox Environment & Security**

*   **Problem:** LLM used `import random` (violating instructions) and inefficiently got word timestamps in Test 5.
*   **Analysis:** Need to provide necessary utilities directly and potentially block disallowed actions more strictly.
*   **Action:** Modify `sandbox_manager.py`.
    1.  **Block Imports:** In `_create_sandbox_globals`, explicitly remove or disable the `__import__` built-in. `RestrictedPython` *should* do this by default, but being explicit adds a layer of safety.
        ```python
        # In SandboxManager._create_sandbox_globals
        sandbox_globals = safe_builtins.copy()
        # ... other additions ...

        # Explicitly disable __import__
        if '__import__' in sandbox_globals:
            del sandbox_globals['__import__']
        # Or assign a guard that always raises an error
        # sandbox_globals['__import__'] = lambda *args, **kwargs: (_ for _ in ()).throw(ImportError("Imports are disabled in this sandbox"))

        # ... rest of the method ...
        ```
    2.  **Provide Random Utilities:** In `_create_safe_utilities`, add wrappers for common `random` functions needed for sequence generation.
        ```python
        # In SandboxManager._create_safe_utilities
        import random as py_random # Use alias to avoid name clash if 'random' is used elsewhere

        def safe_random_randint(a, b):
            # Add validation if needed
            return py_random.randint(a, b)

        def safe_random_choice(seq):
            # Add validation if needed
            return py_random.choice(seq)

        def safe_random_uniform(a, b):
             # Add validation if needed
             return py_random.uniform(a, b)

        # Add to dictionary
        safe_utilities["random_randint"] = safe_random_randint
        safe_utilities["random_choice"] = safe_random_choice
        safe_utilities["random_uniform"] = safe_random_uniform
        # Keep existing random_color, random_float etc.
        ```
        Ensure these are added to `sandbox_globals` in `_create_sandbox_globals`.
    3.  **Provide Efficient Word Timestamps:** Add a dedicated utility/wrapper to get *all* word timestamps easily.
        ```python
        # In SandboxManager._create_safe_wrappers (or _create_safe_utilities)
        def safe_get_all_word_timestamps():
            # Reuse logic from safe_get_word_timestamps but without filters
            try:
                # ... (checks for lyrics_manager, project, lyrics, timestamps) ...
                lyrics = self.app.project_manager.current_project.lyrics
                all_timestamps = []
                if hasattr(lyrics, 'word_timestamps') and lyrics.word_timestamps:
                     for w in lyrics.word_timestamps:
                         if hasattr(w, 'start') and w.start is not None:
                             all_timestamps.append({
                                 "word": w.word if hasattr(w, 'word') else "",
                                 "start_time": w.start,
                                 "end_time": w.end
                             })
                self.logger.debug(f"safe_get_all_word_timestamps returning {len(all_timestamps)} timestamps.")
                return all_timestamps
            except Exception as e:
                self.logger.error(f"Error in safe_get_all_word_timestamps: {e}", exc_info=True)
                raise RuntimeError(f"Error getting all word timestamps: {str(e)}")

        # Add to the returned dictionary
        safe_wrappers["get_all_word_timestamps"] = safe_get_all_word_timestamps

        # Ensure it's added to sandbox_globals in _create_sandbox_globals
        # sandbox_globals.update(safe_wrappers)
        ```
*   **Verification:** Rerun Test 5 (or a variation). The LLM should now fail if it tries `import`. It should be able to use `random_randint` etc., directly. Test its ability to use `get_all_word_timestamps()`.

**Phase 3: Refining Guidance and Preparing for Future** [NEXT]

**Step 5: Enhance Sandbox Environment & Security**

*   **Problem:** LLM used `import random` (violating instructions) and inefficiently got word timestamps in Test 5.
*   **Analysis:** Need to provide necessary utilities directly and potentially block disallowed actions more strictly.
*   **Action:** Modify `sandbox_manager.py`.
    1.  **Block Imports:** In `_create_sandbox_globals`, explicitly remove or disable the `__import__` built-in. `RestrictedPython` *should* do this by default, but being explicit adds a layer of safety.
        ```python
        # In SandboxManager._create_sandbox_globals
        sandbox_globals = safe_builtins.copy()
        # ... other additions ...

        # Explicitly disable __import__
        if '__import__' in sandbox_globals:
            del sandbox_globals['__import__']
        # Or assign a guard that always raises an error
        # sandbox_globals['__import__'] = lambda *args, **kwargs: (_ for _ in ()).throw(ImportError("Imports are disabled in this sandbox"))

        # ... rest of the method ...
        ```
    2.  **Provide Random Utilities:** In `_create_safe_utilities`, add wrappers for common `random` functions needed for sequence generation.
        ```python
        # In SandboxManager._create_safe_utilities
        import random as py_random # Use alias to avoid name clash if 'random' is used elsewhere

        def safe_random_randint(a, b):
            # Add validation if needed
            return py_random.randint(a, b)

        def safe_random_choice(seq):
            # Add validation if needed
            return py_random.choice(seq)

        def safe_random_uniform(a, b):
             # Add validation if needed
             return py_random.uniform(a, b)

        # Add to dictionary
        safe_utilities["random_randint"] = safe_random_randint
        safe_utilities["random_choice"] = safe_random_choice
        safe_utilities["random_uniform"] = safe_random_uniform
        # Keep existing random_color, random_float etc.
        ```
        Ensure these are added to `sandbox_globals` in `_create_sandbox_globals`.
    3.  **Provide Efficient Word Timestamps:** Add a dedicated utility/wrapper to get *all* word timestamps easily.
        ```python
        # In SandboxManager._create_safe_wrappers (or _create_safe_utilities)
        def safe_get_all_word_timestamps():
            # Reuse logic from safe_get_word_timestamps but without filters
            try:
                # ... (checks for lyrics_manager, project, lyrics, timestamps) ...
                lyrics = self.app.project_manager.current_project.lyrics
                all_timestamps = []
                if hasattr(lyrics, 'word_timestamps') and lyrics.word_timestamps:
                     for w in lyrics.word_timestamps:
                         if hasattr(w, 'start') and w.start is not None:
                             all_timestamps.append({
                                 "word": w.word if hasattr(w, 'word') else "",
                                 "start_time": w.start,
                                 "end_time": w.end
                             })
                self.logger.debug(f"safe_get_all_word_timestamps returning {len(all_timestamps)} timestamps.")
                return all_timestamps
            except Exception as e:
                self.logger.error(f"Error in safe_get_all_word_timestamps: {e}", exc_info=True)
                raise RuntimeError(f"Error getting all word timestamps: {str(e)}")

        # Add to the returned dictionary
        safe_wrappers["get_all_word_timestamps"] = safe_get_all_word_timestamps

        # Ensure it's added to sandbox_globals in _create_sandbox_globals
        # sandbox_globals.update(safe_wrappers)
        ```
*   **Verification:** Rerun Test 5 (or a variation). The LLM should now fail if it tries `import`. It should be able to use `random_randint` etc., directly. Test its ability to use `get_all_word_timestamps()`.

**Step 6: Refine System Prompt (`_create_system_message`)**

*   **Problem:** LLM confusion about tool usage, sandbox constraints, and argument requirements.
*   **Analysis:** The system prompt is the primary way to guide the LLM. It needs to be updated to reflect the streamlined tooling and reinforced sandbox rules.
*   **Action:** Modify `llm_chat_window.py` -> `_create_system_message`.
    1.  **Emphasize Sandbox:** State clearly that `execute_sequence_code` is the *preferred* method for creating/modifying sequences, especially involving loops, conditions, randomness, or multiple steps.
    2.  **List Remaining Direct Tools:** Clearly list the few high-level tools remaining (e.g., `create_segment_for_word`, `clear_all_timelines`, audio controls). Provide concise use cases for them.
    3.  **Detail Sandbox Environment:**
        *   Explicitly state: "**Do not use `import` statements.**"
        *   List *all* available functions *within* the sandbox (`create_segment`, `clear_timeline`, `modify_segment`, `delete_segment`, `get_word_timestamps`, `get_all_word_timestamps`).
        *   List *all* available utilities (`random_randint`, `random_choice`, `interpolate_color`, `hsv_to_rgb`, `color_from_name`, `print` for logging, etc.).
        *   List available context variables (`BEAT_TIMES`, `NUM_BALLS`, `SONG_DURATION`).
    4.  **Update Examples:** Provide clear, concise examples focused on using `execute_sequence_code`, showcasing the available functions and utilities (like using `get_all_word_timestamps()` and `random_choice`). Remove examples using deprecated tools.
    5.  **Clarify Tool Usage Guidelines:** Reinforce when to use `create_segment_for_word` vs. the sandbox for word-based coloring. Add guidance for `clear_timeline` vs. `clear_all_timelines` if both are kept.
    6.  **Address Argument Issues:** Add a sentence like: "When calling functions directly (not using the sandbox), ensure you provide all required arguments as specified in their descriptions."
*   **Verification:** Review the generated system prompt. Test LLM interactions with various requests, observing if its behavior aligns better with the updated instructions. Does it use the sandbox more readily? Does it avoid imports? Does it handle `clear_timeline` arguments better?

**Step 7: Introduce Result Feedback (Foundation for Recursion)**

*   **Problem:** The LLM currently has no information about the *outcome* of its actions, preventing self-correction or iteration.
*   **Analysis:** To enable future recursive editing, the LLM needs feedback on what its code/tool call actually did.
*   **Action:**
    1.  **Enhance Tool/Sandbox Results:** Modify handlers (like `_handle_execute_sequence_code`, `_handle_create_segment_for_word`, sandbox wrappers like `safe_create_segment`) to return more detailed success information.
        *   `execute_sequence_code`: The `safe_` wrappers already return dictionaries. Aggregate these. The sandbox result could include a summary like `{"segments_created": 188, "timelines_cleared": 1, "errors_encountered": 0}`. Collect this summary within the sandbox execution if possible, or by modifying the safe wrappers to report back more structured data.
        *   `create_segment_for_word`: Already returns good detail (`segments_created`, `total_segments`).
    2.  **Feed Summary Back to LLM:** In `LLMManager._process_response`, after a *successful* function call:
        *   Extract the summary from the `result` dictionary.
        *   Format this summary into a concise string (e.g., "Action '{function_name}' completed successfully. Result: {summary_string}").
        *   Add this summary string as a *system message* to the chat history *before* potentially sending the next user prompt or handling the LLM's response text. This ensures the summary is part of the context for the LLM's *next* turn.
    3.  **(Optional/Advanced):** Modify the system prompt slightly to tell the LLM it will receive a summary of the results after successful actions and can use this information in subsequent requests.
*   **Verification:** Check the chat history/logs. After a successful action (like Test 2), verify that a system message summarizing the outcome (e.g., number of segments created) appears in the context before the LLM generates its final text response ("I've created an alternating pattern...").

**Phase 4: Testing and Iteration**

**Step 8: Comprehensive Testing**

*   **Action:** After implementing the above steps, perform thorough testing:
    *   Retest all provided examples (Tests 1-5).
    *   Test variations of commands that previously failed.
    *   Test complex sandbox code involving loops, conditionals, `get_all_word_timestamps`, and random utilities.
    *   Test edge cases (empty timelines, no lyrics loaded, etc.).
    *   Specifically test the error-handling loop (e.g., deliberately give a command that will cause a sandbox error).
    *   Monitor logs closely for errors and unexpected behavior.
*   **Goal:** Ensure the system is significantly more robust, predictable, and correctly utilizes the sandbox and remaining tools according to the refined guidance.

---

This plan addresses the immediate bugs, improves robustness through error handling, streamlines the tooling around the sandbox, refines LLM guidance, and introduces a basic feedback mechanism as a step towards your goal of iterative editing. Each step builds upon the previous ones.