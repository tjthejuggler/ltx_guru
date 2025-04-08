# PRG Export Refactoring Plan

## Problem

The current PRG export functionality in Sequence Maker is failing with an `AttributeError: 'bool' object has no attribute 'replace'` and does not meet the desired workflow.

**Desired Workflow:**

1.  User clicks "Export PRG".
2.  Application prompts the user to select an output **directory**.
3.  For **each timeline** in the current project:
    *   Generate a JSON file named `{project_name}_Ball_{timeline_index + 1}.json`.
    *   Generate a PRG file named `{project_name}_Ball_{timeline_index + 1}.prg`.
    *   Spaces in the project name should be replaced with underscores (`_`).
4.  Display a success message indicating the number of files exported and the output directory.
5.  Ask the user if they want to open the output directory.

## Analysis

*   The error `AttributeError: 'bool' object has no attribute 'replace'` likely occurs because `timeline.name` is unexpectedly a boolean value when accessed during the export process in `sequence_maker/export/prg_exporter.py`.
*   Investigation of `Timeline` model (`models/timeline.py`), `Project` model (`models/project.py`), and `ProjectManager` (`managers/project_manager.py`) did not reveal obvious sources for `timeline.name` becoming a boolean.
*   The UI handler `on_export_prg` in `ui/main_window_parts/handlers.py` was identified as the likely point of failure and the area needing modification.
*   The current `on_export_prg` implementation:
    *   Incorrectly imports and calls a non-existent `export_prg` function instead of using the `PRGExporter` class.
    *   Prompts for a single *file*, not a directory.
    *   Only exports PRG, not JSON.
    *   Does not use the desired `{project_name}_Ball_{number}` naming convention.

## Proposed Solution

Modify the `on_export_prg` function in `sequence_maker/ui/main_window_parts/handlers.py` as follows:

1.  **Change File Dialog:** Use `QFileDialog.getExistingDirectory` to get an output directory path.
2.  **Import Correct Classes:** Import `PRGExporter` from `export.prg_exporter` and `JSONExporter` from `export.json_exporter`.
3.  **Instantiate Exporters:** Create instances: `prg_exporter = PRGExporter(main_window.app)` and `json_exporter = JSONExporter(main_window.app)`.
4.  **Get Project:** Retrieve the current project: `project = main_window.app.project_manager.current_project`. Add error handling for no project loaded.
5.  **Get Project Name:** Sanitize the project name: `project_name = project.name.replace(' ', '_')`.
6.  **Iterate Timelines:** Loop through `project.timelines` using `enumerate`.
7.  **Generate Filenames:** Construct the base filename for each timeline: `base_name = f"{project_name}_Ball_{i+1}"`.
8.  **Construct Paths:** Create full paths for JSON and PRG files: `json_path = os.path.join(directory, f"{base_name}.json")` and `prg_path = os.path.join(directory, f"{base_name}.prg")`.
9.  **Export JSON:** Call `json_exporter.export_timeline(timeline, json_path, refresh_rate=100)`.
10. **Export PRG:** Call `prg_exporter.export_timeline(timeline, prg_path, refresh_rate=project.refresh_rate)`.
11. **Track Success:** Maintain counts for successful JSON and PRG exports.
12. **Update Status Message:** Show a status message like: `f"Exported {json_success}/{total} JSON and {prg_success}/{total} PRG files to {directory}"`.
13. **Update "Open" Prompt:** Modify the `QMessageBox` to ask about opening the *directory*.

**No changes** are required in `sequence_maker/export/prg_exporter.py` itself, as the `export_timeline` method is sufficient.

## Visual Flow

```mermaid
sequenceDiagram
    participant User
    participant MainWindow
    participant Handlers (on_export_prg)
    participant QFileDialog
    participant ProjectManager
    participant JSONExporter
    participant PRGExporter
    participant OS/Filesystem

    User->>MainWindow: Clicks "Export PRG"
    MainWindow->>Handlers: Calls on_export_prg()
    Handlers->>QFileDialog: getExistingDirectory()
    QFileDialog-->>User: Shows directory dialog
    User-->>QFileDialog: Selects directory
    QFileDialog-->>Handlers: Returns selected directory path
    Handlers->>ProjectManager: Gets current_project
    ProjectManager-->>Handlers: Returns project object
    Handlers->>JSONExporter: Instantiates
    Handlers->>PRGExporter: Instantiates
    loop For each timeline in project
        Handlers->>Handlers: Generates filenames (project_Ball_N.json/prg)
        Handlers->>JSONExporter: Calls export_timeline(timeline, json_path)
        JSONExporter->>OS/Filesystem: Writes JSON file
        OS/Filesystem-->>JSONExporter: Success/Failure
        JSONExporter-->>Handlers: Returns success/failure
        Handlers->>PRGExporter: Calls export_timeline(timeline, prg_path)
        PRGExporter->>OS/Filesystem: Writes PRG file (via prg_generator.py)
        OS/Filesystem-->>PRGExporter: Success/Failure
        PRGExporter-->>Handlers: Returns success/failure
    end
    Handlers->>MainWindow: Updates status bar (counts, directory)
    Handlers->>QMessageBox: Asks "Open directory?"
    QMessageBox-->>User: Shows dialog
    User-->>QMessageBox: Clicks Yes/No
    QMessageBox-->>Handlers: Returns choice
    alt User clicks Yes
        Handlers->>OS/Filesystem: Opens directory
    end