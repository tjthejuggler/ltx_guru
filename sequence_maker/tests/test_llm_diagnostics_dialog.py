"""
Tests for the LLM diagnostics dialog.
"""

import pytest
from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from ui.dialogs.llm_diagnostics_dialog import LLMDiagnosticsDialog


def test_llm_diagnostics_dialog_creation(qtbot, app_fixture, mocker):
    """Test that the LLM diagnostics dialog can be created."""
    # Create dialog
    dialog = LLMDiagnosticsDialog(app_fixture)
    qtbot.addWidget(dialog)
    
    # Check dialog properties
    assert dialog.windowTitle() == "LLM Diagnostics"
    assert dialog.isHidden()  # Dialog should be hidden by default


def test_llm_diagnostics_dialog_load_metrics(qtbot, app_fixture, mocker):
    """Test that the LLM diagnostics dialog loads metrics correctly."""
    # Mock project with metrics
    mock_project = mocker.MagicMock()
    mock_project.llm_performance_metrics = [
        {
            "timestamp": datetime.now().isoformat(),
            "duration": 2.5,
            "tokens": 500,
            "prompt_length": 100,
            "response_length": 400,
            "tokens_per_second": 200,
            "characters_per_second": 160,
            "model": "gpt-3.5-turbo",
            "provider": "openai"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "duration": 3.0,
            "tokens": 600,
            "prompt_length": 120,
            "response_length": 480,
            "tokens_per_second": 200,
            "characters_per_second": 160,
            "model": "gpt-3.5-turbo",
            "provider": "openai"
        }
    ]
    
    # Mock token usage
    mock_project.llm_metadata = {
        "token_usage": 1100,
        "estimated_cost": 0.0022,
        "interactions": [
            {
                "timestamp": datetime.now().isoformat(),
                "tokens": 500,
                "cost": 0.001,
                "model": "gpt-3.5-turbo",
                "provider": "openai"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "tokens": 600,
                "cost": 0.0012,
                "model": "gpt-3.5-turbo",
                "provider": "openai"
            }
        ]
    }
    
    # Mock project manager
    app_fixture.project_manager.current_project = mock_project
    
    # Create dialog
    dialog = LLMDiagnosticsDialog(app_fixture)
    qtbot.addWidget(dialog)
    
    # Check that metrics were loaded
    assert dialog.metrics_list.count() > 0
    assert dialog.token_usage_label.text() == "Total Token Usage: 1,100 tokens"
    assert dialog.cost_label.text() == "Estimated Cost: $0.0022"


def test_llm_diagnostics_dialog_no_metrics(qtbot, app_fixture, mocker):
    """Test that the LLM diagnostics dialog handles no metrics gracefully."""
    # Mock project with no metrics
    mock_project = mocker.MagicMock()
    mock_project.llm_performance_metrics = []
    
    # Mock no token usage
    mock_project.llm_metadata = {
        "token_usage": 0,
        "estimated_cost": 0.0,
        "interactions": []
    }
    
    # Mock project manager
    app_fixture.project_manager.current_project = mock_project
    
    # Create dialog
    dialog = LLMDiagnosticsDialog(app_fixture)
    qtbot.addWidget(dialog)
    
    # Check that no metrics message is shown
    assert dialog.metrics_list.count() == 0
    assert dialog.token_usage_label.text() == "Total Token Usage: 0 tokens"
    assert dialog.cost_label.text() == "Estimated Cost: $0.0000"


def test_llm_diagnostics_dialog_refresh(qtbot, app_fixture, mocker):
    """Test that the LLM diagnostics dialog refresh button works."""
    # Mock project with metrics
    mock_project = mocker.MagicMock()
    mock_project.llm_performance_metrics = [
        {
            "timestamp": datetime.now().isoformat(),
            "duration": 2.5,
            "tokens": 500,
            "prompt_length": 100,
            "response_length": 400,
            "tokens_per_second": 200,
            "characters_per_second": 160,
            "model": "gpt-3.5-turbo",
            "provider": "openai"
        }
    ]
    
    # Mock token usage
    mock_project.llm_metadata = {
        "token_usage": 500,
        "estimated_cost": 0.001,
        "interactions": [
            {
                "timestamp": datetime.now().isoformat(),
                "tokens": 500,
                "cost": 0.001,
                "model": "gpt-3.5-turbo",
                "provider": "openai"
            }
        ]
    }
    
    # Mock project manager
    app_fixture.project_manager.current_project = mock_project
    
    # Create dialog
    dialog = LLMDiagnosticsDialog(app_fixture)
    qtbot.addWidget(dialog)
    
    # Check initial metrics
    assert dialog.metrics_list.count() == 1
    assert dialog.token_usage_label.text() == "Total Token Usage: 500 tokens"
    
    # Update metrics
    mock_project.llm_performance_metrics.append({
        "timestamp": datetime.now().isoformat(),
        "duration": 3.0,
        "tokens": 600,
        "prompt_length": 120,
        "response_length": 480,
        "tokens_per_second": 200,
        "characters_per_second": 160,
        "model": "gpt-3.5-turbo",
        "provider": "openai"
    })
    
    mock_project.llm_metadata["token_usage"] = 1100
    mock_project.llm_metadata["estimated_cost"] = 0.0022
    mock_project.llm_metadata["interactions"].append({
        "timestamp": datetime.now().isoformat(),
        "tokens": 600,
        "cost": 0.0012,
        "model": "gpt-3.5-turbo",
        "provider": "openai"
    })
    
    # Click refresh button
    qtbot.mouseClick(dialog.refresh_button, Qt.MouseButton.LeftButton)
    
    # Check updated metrics
    assert dialog.metrics_list.count() == 2
    assert dialog.token_usage_label.text() == "Total Token Usage: 1,100 tokens"
    assert dialog.cost_label.text() == "Estimated Cost: $0.0022"