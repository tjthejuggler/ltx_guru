"""
Sequence Maker - Tests for LLM Diagnostics Dialog

This module contains tests for the LLM Diagnostics Dialog.
"""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui.dialogs.llm_diagnostics_dialog import LLMDiagnosticsDialog


@pytest.fixture
def mock_app():
    """Create a mock application instance."""
    app = MagicMock()
    app.project_manager = MagicMock()
    app.project_manager.current_project = MagicMock()
    app.project_manager.current_project.llm_performance_metrics = [
        {
            "timestamp": "2025-03-24T12:00:00",
            "duration": 2.5,
            "tokens": 150,
            "prompt_length": 100,
            "response_length": 500,
            "tokens_per_second": 60.0,
            "characters_per_second": 200.0,
            "model": "gpt-4",
            "provider": "openai"
        },
        {
            "timestamp": "2025-03-24T12:05:00",
            "duration": 3.0,
            "tokens": 200,
            "prompt_length": 120,
            "response_length": 600,
            "tokens_per_second": 66.7,
            "characters_per_second": 200.0,
            "model": "gpt-4",
            "provider": "openai"
        }
    ]
    app.llm_manager = MagicMock()
    app.llm_manager.provider = "openai"
    app.llm_manager.model = "gpt-4"
    app.config = MagicMock()
    app.config.get.return_value = "info"
    return app


@pytest.fixture
def dialog(mock_app, qtbot):
    """Create a dialog instance."""
    dialog = LLMDiagnosticsDialog(mock_app)
    qtbot.addWidget(dialog)
    return dialog


def test_dialog_creation(dialog):
    """Test that the dialog is created correctly."""
    assert dialog.windowTitle() == "LLM Diagnostics"
    assert dialog.tab_widget.count() == 3  # Metrics, Logs, Settings tabs


def test_metrics_tab(dialog):
    """Test the metrics tab."""
    # Check that the metrics table has the correct number of rows
    assert dialog.metrics_table.rowCount() == 2
    
    # Check that the summary labels have the correct values
    assert dialog.total_requests_label.text() == "2"
    assert dialog.total_tokens_label.text() == "350"
    assert float(dialog.total_cost_label.text().replace("$", "")) > 0
    assert float(dialog.avg_response_time_label.text().split()[0]) == 2.75
    assert float(dialog.avg_tokens_per_request_label.text().split()[0]) == 175.0


def test_logs_tab(dialog):
    """Test the logs tab."""
    # Check that the log viewer exists
    assert dialog.log_viewer is not None
    
    # Check that the log level combo has the correct items
    assert dialog.log_level_combo.count() == 5
    assert dialog.log_level_combo.itemText(0) == "DEBUG"
    assert dialog.log_level_combo.itemText(1) == "INFO"
    assert dialog.log_level_combo.itemText(2) == "WARNING"
    assert dialog.log_level_combo.itemText(3) == "ERROR"
    assert dialog.log_level_combo.itemText(4) == "CRITICAL"


def test_settings_tab(dialog):
    """Test the settings tab."""
    # Check that the settings checkboxes exist
    assert dialog.enable_detailed_logging_checkbox is not None
    assert dialog.log_prompts_checkbox is not None
    assert dialog.enable_metrics_tracking_checkbox is not None
    
    # Check that the metrics retention combo has the correct items
    assert dialog.metrics_retention_combo.count() == 4
    assert dialog.metrics_retention_combo.itemText(0) == "Last 10 requests"
    assert dialog.metrics_retention_combo.itemText(1) == "Last 50 requests"
    assert dialog.metrics_retention_combo.itemText(2) == "Last 100 requests"
    assert dialog.metrics_retention_combo.itemText(3) == "All requests"


def test_update_plot(dialog, mock_app):
    """Test the plot update functionality."""
    # Mock the plot_metrics method
    dialog.plot_canvas.plot_metrics = MagicMock()
    
    # Call update_plot
    dialog._update_plot()
    
    # Check that plot_metrics was called with the correct arguments
    dialog.plot_canvas.plot_metrics.assert_called_once()
    args = dialog.plot_canvas.plot_metrics.call_args[0]
    assert args[0] == mock_app.project_manager.current_project.llm_performance_metrics
    assert args[1] in ["duration", "tokens", "tokens_per_second", "cost"]


def test_export_functionality(dialog, mock_app, qtbot, monkeypatch):
    """Test the export functionality."""
    # Mock QFileDialog.getSaveFileName
    with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=("test_export.json", "")):
        # Mock open and json.dump
        with patch('builtins.open', MagicMock()):
            with patch('json.dump', MagicMock()):
                # Mock QMessageBox.information
                with patch('PyQt6.QtWidgets.QMessageBox.information', MagicMock()):
                    # Click the export button
                    qtbot.mouseClick(dialog.export_button, Qt.MouseButton.LeftButton)
                    
                    # Check that json.dump was called
                    import json
                    assert json.dump.called


def test_update_logging_settings(dialog, mock_app, qtbot):
    """Test updating logging settings."""
    # Set checkbox states
    dialog.enable_detailed_logging_checkbox.setChecked(True)
    dialog.log_prompts_checkbox.setChecked(False)
    
    # Call update_logging_settings
    dialog._update_logging_settings()
    
    # Check that config.set was called with the correct arguments
    mock_app.config.set.assert_any_call("logging", "detailed_llm_logging", True)
    mock_app.config.set.assert_any_call("logging", "log_prompts", False)
    
    # Check that config.save was called
    mock_app.config.save.assert_called_once()


def test_update_metrics_settings(dialog, mock_app, qtbot):
    """Test updating metrics settings."""
    # Set checkbox and combo box states
    dialog.enable_metrics_tracking_checkbox.setChecked(True)
    dialog.metrics_retention_combo.setCurrentIndex(2)  # Last 100 requests
    
    # Call update_metrics_settings
    dialog._update_metrics_settings()
    
    # Check that config.set was called with the correct arguments
    mock_app.config.set.assert_any_call("llm", "metrics_tracking", True)
    mock_app.config.set.assert_any_call("llm", "metrics_retention", 100)
    
    # Check that config.save was called
    mock_app.config.save.assert_called_once()