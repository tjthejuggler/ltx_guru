"""
Sequence Maker - Main Window Handlers

This module contains functions for handling events in the main window.
"""

import os
import logging
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from app.constants import PROJECT_FILE_EXTENSION, AUDIO_FILE_EXTENSIONS


def on_new(main_window):
    """Handle the 'New' action."""
    if not main_window._check_unsaved_changes():
        return
    main_window.app.project_manager.new_project()
    main_window._update_ui()


def on_open(main_window):
    """Handle the 'Open' action."""
    if not main_window._check_unsaved_changes():
        return
    
    # Show file dialog
    file_dialog = QFileDialog(main_window)
    file_dialog.setWindowTitle("Open Project")
    file_dialog.setNameFilter(f"Sequence Maker Projects (*{PROJECT_FILE_EXTENSION})")
    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    
    if file_dialog.exec():
        file_paths = file_dialog.selectedFiles()
        if file_paths:
            project_path = file_paths[0]
            try:
                main_window.app.project_manager.load_project(project_path)
                main_window._update_ui()
            except Exception as e:
                logging.error(f"Error loading project: {e}")
                QMessageBox.critical(main_window, "Error", f"Failed to load project: {str(e)}")


def on_save(main_window):
    """Handle the 'Save' action."""
    # If project has no path, prompt for save location
    if not main_window.app.project_manager.current_project or not main_window.app.project_manager.current_project.file_path:
        return on_save_as(main_window)
    
    try:
        main_window.app.project_manager.save_project()
        main_window._update_ui()
        main_window.statusBar().showMessage("Project saved", 3000)
        return True
    except Exception as e:
        logging.error(f"Error saving project: {e}")
        QMessageBox.critical(main_window, "Error", f"Failed to save project: {str(e)}")
        return False


def on_save_as(main_window):
    """Handle the 'Save As' action."""
    # Show file dialog
    file_dialog = QFileDialog(main_window)
    file_dialog.setWindowTitle("Save Project As")
    file_dialog.setNameFilter(f"Sequence Maker Projects (*{PROJECT_FILE_EXTENSION})")
    file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    file_dialog.setDefaultSuffix(PROJECT_FILE_EXTENSION[1:])  # Remove the dot
    
    if file_dialog.exec():
        file_paths = file_dialog.selectedFiles()
        if file_paths:
            project_path = file_paths[0]
            try:
                main_window.app.project_manager.save_project(project_path)
                main_window._update_ui()
                main_window.statusBar().showMessage("Project saved", 3000)
                return True
            except Exception as e:
                logging.error(f"Error saving project: {e}")
                QMessageBox.critical(main_window, "Error", f"Failed to save project: {str(e)}")
    
    return False


def on_load_audio(main_window):
    """Handle the 'Load Audio' action."""
    # Show file dialog
    file_dialog = QFileDialog(main_window)
    file_dialog.setWindowTitle("Load Audio File")
    
    # Create filter string for audio files
    filter_string = "Audio Files ("
    for ext in AUDIO_FILE_EXTENSIONS:
        filter_string += f"*{ext} "
    filter_string = filter_string.strip() + ")"
    
    file_dialog.setNameFilter(filter_string)
    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    
    if file_dialog.exec():
        file_paths = file_dialog.selectedFiles()
        if file_paths:
            audio_path = file_paths[0]
            try:
                main_window.app.audio_manager.load_audio(audio_path)
                main_window._update_ui()
            except Exception as e:
                logging.error(f"Error loading audio: {e}")
                QMessageBox.critical(main_window, "Error", f"Failed to load audio: {str(e)}")


def on_export_json(main_window):
    """Handle the 'Export JSON' action."""
    # Show directory selection dialog
    export_dir = QFileDialog.getExistingDirectory(
        main_window,
        "Select Directory for JSON Export",
        "",
        QFileDialog.Option.ShowDirsOnly
    )
    
    if not export_dir:
        return  # User cancelled
    
    # Get a base filename (optional)
    base_filename, ok = QFileDialog.getSaveFileName(
        main_window,
        "Enter Base Filename (Optional)",
        os.path.join(export_dir, "export"),
        "JSON Files (*.json)",
        options=QFileDialog.Option.DontConfirmOverwrite
    )
    
    if not ok and not base_filename:
        # User cancelled or didn't provide a filename
        # We'll still proceed with export using default naming
        base_filename = None
    
    try:
        from export.json_exporter import JSONExporter
        exporter = JSONExporter(main_window.app)
        success_count, total_count, exported_files = exporter.export_project(
            export_dir,
            os.path.basename(base_filename) if base_filename else None
        )
        
        # Show success message
        main_window.statusBar().showMessage(
            f"Exported {success_count}/{total_count} JSON files to {export_dir}",
            3000
        )
        
        # Ask if user wants to open the export directory
        reply = QMessageBox.question(
            main_window,
            "Export Complete",
            f"JSON files exported to {export_dir}. Would you like to open this directory?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Open the directory with the default file manager
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(export_dir)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', export_dir))
            else:  # Linux
                subprocess.call(('xdg-open', export_dir))
    except Exception as e:
        logging.error(f"Error exporting JSON: {e}")
        QMessageBox.critical(main_window, "Error", f"Failed to export JSON: {str(e)}")


def on_export_prg(main_window):
    """Handle the 'Export PRG' action."""
    # Check if a project is loaded
    if not main_window.app.project_manager.current_project:
        QMessageBox.warning(
            main_window,
            "No Project",
            "No project is loaded. Please create or open a project first."
        )
        return
    
    # Show directory selection dialog
    export_dir = QFileDialog.getExistingDirectory(
        main_window,
        "Select Directory for PRG and JSON Export",
        "",
        QFileDialog.Option.ShowDirsOnly
    )
    
    if not export_dir:
        return  # User cancelled
    
    try:
        # Import exporters
        from export.prg_exporter import PRGExporter
        from export.json_exporter import JSONExporter
        
        # Create exporter instances
        prg_exporter = PRGExporter(main_window.app)
        json_exporter = JSONExporter(main_window.app)
        
        # Get the current project - be cautious about how we access it
        project = main_window.app.project_manager.current_project
        
        # Check the project type to avoid attribute errors
        if not hasattr(project, 'name') or not isinstance(project.name, str):
            logging.warning(f"Project name has unexpected type: {type(project)}/{type(project.name) if hasattr(project, 'name') else 'no name attribute'}")
            project_name = "project"  # Default name if we can't get the real one
        else:
            # Sanitize project name (replace spaces with underscores)
            project_name = project.name.replace(' ', '_')
        
        # Check if project has timelines
        if not hasattr(project, 'timelines') or not isinstance(project.timelines, list):
            logging.error(f"Project timelines has unexpected type: {type(project)}/{type(project.timelines) if hasattr(project, 'timelines') else 'no timelines attribute'}")
            QMessageBox.critical(main_window, "Error", "Unable to access project timelines. The project may be corrupted.")
            return
            
        # Track success counts
        json_success_count = 0
        prg_success_count = 0
        total_count = len(project.timelines)
        
        if total_count == 0:
            QMessageBox.warning(main_window, "No Timelines", "The current project does not contain any timelines to export.")
            return
        
        # Export each timeline
        for i, timeline in enumerate(project.timelines):
            # Make sure the timeline has a valid name
            if not hasattr(timeline, 'name') or not isinstance(timeline.name, str):
                timeline_name = f"Ball_{i+1}"
            else:
                timeline_name = timeline.name
                
            # Generate filenames with project name and ball number
            base_name = f"{project_name}_Ball_{i+1}"
            json_path = os.path.join(export_dir, f"{base_name}.json")
            prg_path = os.path.join(export_dir, f"{base_name}.prg")
            
            # Export JSON
            if json_exporter.export_timeline(timeline, json_path, refresh_rate=100):
                json_success_count += 1
            
            # Export PRG (Use refresh_rate=100 for consistency with exported JSON)
            if prg_exporter.export_timeline(timeline, prg_path, refresh_rate=100):
                prg_success_count += 1
        
        # Show success message
        main_window.statusBar().showMessage(
            f"Exported {json_success_count}/{total_count} JSON files and "
            f"{prg_success_count}/{total_count} PRG files to {export_dir}",
            5000
        )
        
        # Ask if user wants to open the export directory
        reply = QMessageBox.question(
            main_window,
            "Export Complete",
            f"Files exported to {export_dir}. Would you like to open this directory?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Open the directory with the default file manager
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(export_dir)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', export_dir))
            else:  # Linux
                subprocess.call(('xdg-open', export_dir))
    except Exception as e:
        logging.error(f"Error exporting files: {e}")
        QMessageBox.critical(main_window, "Error", f"Failed to export files: {str(e)}")


def on_version_history(main_window):
    """Handle the 'Version History' action."""
    from ui.dialogs.version_history_dialog import VersionHistoryDialog
    
    dialog = VersionHistoryDialog(main_window.app, main_window)
    dialog.exec()
    
    # Update UI in case a version was restored
    main_window._update_ui()


def on_undo(main_window):
    """Handle the 'Undo' action."""
    if main_window.app.undo_manager.can_undo():
        main_window.app.undo_manager.undo()
        main_window._update_ui()


def on_redo(main_window):
    """Handle the 'Redo' action."""
    if main_window.app.undo_manager.can_redo():
        main_window.app.undo_manager.redo()
        main_window._update_ui()


def on_cut(main_window):
    """Handle the 'Cut' action."""
    # Get the focused widget
    focused_widget = main_window.focusWidget()
    
    # If it's a text edit, call its cut method
    if hasattr(focused_widget, 'cut'):
        focused_widget.cut()


def on_copy(main_window):
    """Handle the 'Copy' action."""
    # Get the focused widget
    focused_widget = main_window.focusWidget()
    
    # If it's a text edit, call its copy method
    if hasattr(focused_widget, 'copy'):
        focused_widget.copy()


def on_paste(main_window):
    """Handle the 'Paste' action."""
    # Get the focused widget
    focused_widget = main_window.focusWidget()
    
    # If it's a text edit, call its paste method
    if hasattr(focused_widget, 'paste'):
        focused_widget.paste()


def on_delete(main_window):
    """Handle the 'Delete' action."""
    # Get the focused widget
    focused_widget = main_window.focusWidget()
    
    # If it's a text edit, call its clear method
    if hasattr(focused_widget, 'clear'):
        focused_widget.clear()


def on_select_all(main_window):
    """Handle the 'Select All' action."""
    # Get the focused widget
    focused_widget = main_window.focusWidget()
    
    # If it's a text edit, call its selectAll method
    if hasattr(focused_widget, 'selectAll'):
        focused_widget.selectAll()


def on_preferences(main_window):
    """Handle the 'Preferences' action."""
    from ui.dialogs.settings_dialog import SettingsDialog
    
    dialog = SettingsDialog(main_window.app, main_window)
    result = dialog.exec()
    
    # If dialog was accepted, reload LLM manager configuration
    if result:
        # Update LLM manager with new settings
        if hasattr(main_window.app, 'llm_manager'):
            main_window.app.llm_manager.reload_configuration()


def on_zoom_in(main_window):
    """Handle the 'Zoom In' action."""
    main_window.timeline_widget.zoom_in()


def on_zoom_out(main_window):
    """Handle the 'Zoom Out' action."""
    main_window.timeline_widget.zoom_out()


def on_zoom_fit(main_window):
    """Handle the 'Zoom Fit' action."""
    main_window.timeline_widget.zoom_fit()


def on_play(main_window):
    """Handle the 'Play' action."""
    if hasattr(main_window.app, 'audio_manager'):
        main_window.app.audio_manager.play()
        main_window._update_ui()


def on_pause(main_window):
    """Handle the 'Pause' action."""
    if hasattr(main_window.app, 'audio_manager'):
        main_window.app.audio_manager.pause()
        main_window._update_ui()


def on_stop(main_window):
    """Handle the 'Stop' action."""
    if hasattr(main_window.app, 'audio_manager'):
        main_window.app.audio_manager.stop()
        main_window._update_ui()


def on_loop(main_window, checked):
    """Handle the 'Loop' action."""
    if hasattr(main_window.app, 'audio_manager'):
        main_window.app.audio_manager.set_loop(checked)


def on_key_mapping(main_window):
    """Handle the 'Key Mapping' action."""
    from ui.dialogs.key_mapping_dialog import KeyMappingDialog
    
    dialog = KeyMappingDialog(main_window.app, main_window)
    dialog.exec()


def on_connect_balls(main_window):
    """Handle the 'Connect Balls' action."""
    from ui.dialogs.ball_scan_dialog import BallScanDialog
    
    dialog = BallScanDialog(main_window.app, main_window)
    dialog.exec()


def on_llm_chat(main_window):
    """Handle the 'LLM Chat' action."""
    # Create the chat window if it doesn't exist
    if not hasattr(main_window, 'llm_chat_window') or main_window.llm_chat_window is None:
        main_window._create_llm_chat_window()
    
    # Show the chat window
    main_window.llm_chat_window.show()
    main_window.llm_chat_window.raise_()
    main_window.llm_chat_window.activateWindow()


def on_llm_diagnostics(main_window):
    """Handle the 'LLM Diagnostics' action."""
    from ui.dialogs.llm_diagnostics_dialog import LLMDiagnosticsDialog
    
    dialog = LLMDiagnosticsDialog(main_window.app, main_window)
    dialog.exec()


def on_about(main_window):
    """Handle the 'About' action."""
    from ui.dialogs.about_dialog import AboutDialog
    
    dialog = AboutDialog(main_window)
    dialog.exec()