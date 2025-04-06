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
    # Show file dialog
    file_dialog = QFileDialog(main_window)
    file_dialog.setWindowTitle("Export PRG")
    file_dialog.setNameFilter("PRG Files (*.prg)")
    file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    file_dialog.setDefaultSuffix("prg")
    
    if file_dialog.exec():
        file_paths = file_dialog.selectedFiles()
        if file_paths:
            prg_path = file_paths[0]
            try:
                from export.prg_exporter import export_prg
                export_prg(main_window.app.project_manager.project, prg_path)
                main_window.statusBar().showMessage(f"Exported PRG to {prg_path}", 3000)
                
                # Ask if user wants to open the exported file
                reply = QMessageBox.question(
                    main_window, "Export Complete",
                    f"PRG exported to {prg_path}. Would you like to open it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Open the file with the default application
                    import subprocess
                    import platform
                    
                    if platform.system() == 'Windows':
                        os.startfile(prg_path)
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.call(('open', prg_path))
                    else:  # Linux
                        subprocess.call(('xdg-open', prg_path))
            except Exception as e:
                logging.error(f"Error exporting PRG: {e}")
                QMessageBox.critical(main_window, "Error", f"Failed to export PRG: {str(e)}")


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