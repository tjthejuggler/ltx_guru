"""
Sequence Maker - Tests for VersionHistoryDialog

This module contains tests for the VersionHistoryDialog class.
"""

import os
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from ui.dialogs.version_history_dialog import VersionHistoryDialog


def test_version_history_dialog_initialization(qtbot, app_fixture, monkeypatch):
    """
    Test that the VersionHistoryDialog initializes correctly.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Mock the autosave_manager's get_versions method
    monkeypatch.setattr(app_fixture.autosave_manager, "get_versions", MagicMock(return_value=[]))
    
    # Create dialog
    dialog = VersionHistoryDialog(app_fixture)
    qtbot.addWidget(dialog)
    
    # Check that the dialog was initialized correctly
    assert dialog.windowTitle() == "Version History"
    assert dialog.app == app_fixture
    
    # Check that the version list is empty
    assert dialog.version_list.count() == 0


def test_version_history_dialog_load_versions(qtbot, app_fixture, monkeypatch):
    """
    Test that the _load_versions method loads versions correctly.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create some test versions
    versions = [
        {
            "file_path": "/path/to/version1.json",
            "timestamp": "20250324_235959",
            "reason": "Test Reason 1",
            "file_name": "20250324_235959_Test_Reason_1.json"
        },
        {
            "file_path": "/path/to/version2.json",
            "timestamp": "20250325_000000",
            "reason": "Test Reason 2",
            "file_name": "20250325_000000_Test_Reason_2.json"
        }
    ]
    
    # Mock the autosave_manager's get_versions method
    monkeypatch.setattr(app_fixture.autosave_manager, "get_versions", MagicMock(return_value=versions))
    
    # Create dialog
    dialog = VersionHistoryDialog(app_fixture)
    qtbot.addWidget(dialog)
    
    # Check that the version list has the correct number of items
    assert dialog.version_list.count() == 2
    
    # Check that the items have the correct text and data
    item0 = dialog.version_list.item(0)
    assert "2025-03-24 23:59:59" in item0.text()
    assert "Test Reason 1" in item0.text()
    assert item0.data(Qt.ItemDataRole.UserRole) == "/path/to/version1.json"
    
    item1 = dialog.version_list.item(1)
    assert "2025-03-25 00:00:00" in item1.text()
    assert "Test Reason 2" in item1.text()
    assert item1.data(Qt.ItemDataRole.UserRole) == "/path/to/version2.json"


def test_version_history_dialog_restore_version(qtbot, app_fixture, monkeypatch):
    """
    Test that the _restore_version method restores a version correctly.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create some test versions
    versions = [
        {
            "file_path": "/path/to/version1.json",
            "timestamp": "20250324_235959",
            "reason": "Test Reason 1",
            "file_name": "20250324_235959_Test_Reason_1.json"
        }
    ]
    
    # Mock the autosave_manager's get_versions method
    monkeypatch.setattr(app_fixture.autosave_manager, "get_versions", MagicMock(return_value=versions))
    
    # Mock the autosave_manager's restore_version method
    monkeypatch.setattr(app_fixture.autosave_manager, "restore_version", MagicMock(return_value=True))
    
    # Mock QMessageBox.information
    monkeypatch.setattr(QMessageBox, "information", MagicMock())
    
    # Create dialog
    dialog = VersionHistoryDialog(app_fixture)
    qtbot.addWidget(dialog)
    
    # Call _restore_version
    dialog._restore_version("/path/to/version1.json")
    
    # Check that the autosave_manager's restore_version method was called with the correct path
    app_fixture.autosave_manager.restore_version.assert_called_once_with("/path/to/version1.json")
    
    # Check that QMessageBox.information was called
    QMessageBox.information.assert_called_once()
    
    # Check that the dialog was accepted
    assert dialog.result() == QApplication.instance().exec()


def test_version_history_dialog_restore_version_failure(qtbot, app_fixture, monkeypatch):
    """
    Test that the _restore_version method handles failure correctly.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create some test versions
    versions = [
        {
            "file_path": "/path/to/version1.json",
            "timestamp": "20250324_235959",
            "reason": "Test Reason 1",
            "file_name": "20250324_235959_Test_Reason_1.json"
        }
    ]
    
    # Mock the autosave_manager's get_versions method
    monkeypatch.setattr(app_fixture.autosave_manager, "get_versions", MagicMock(return_value=versions))
    
    # Mock the autosave_manager's restore_version method to return False (failure)
    monkeypatch.setattr(app_fixture.autosave_manager, "restore_version", MagicMock(return_value=False))
    
    # Mock QMessageBox.warning
    monkeypatch.setattr(QMessageBox, "warning", MagicMock())
    
    # Create dialog
    dialog = VersionHistoryDialog(app_fixture)
    qtbot.addWidget(dialog)
    
    # Call _restore_version
    dialog._restore_version("/path/to/version1.json")
    
    # Check that the autosave_manager's restore_version method was called with the correct path
    app_fixture.autosave_manager.restore_version.assert_called_once_with("/path/to/version1.json")
    
    # Check that QMessageBox.warning was called
    QMessageBox.warning.assert_called_once()
    
    # Check that the dialog was not accepted
    assert dialog.result() != QApplication.instance().exec()


def test_version_history_dialog_on_restore_clicked_no_selection(qtbot, app_fixture, monkeypatch):
    """
    Test that the _on_restore_clicked method handles no selection correctly.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create some test versions
    versions = [
        {
            "file_path": "/path/to/version1.json",
            "timestamp": "20250324_235959",
            "reason": "Test Reason 1",
            "file_name": "20250324_235959_Test_Reason_1.json"
        }
    ]
    
    # Mock the autosave_manager's get_versions method
    monkeypatch.setattr(app_fixture.autosave_manager, "get_versions", MagicMock(return_value=versions))
    
    # Mock QMessageBox.warning
    monkeypatch.setattr(QMessageBox, "warning", MagicMock())
    
    # Create dialog
    dialog = VersionHistoryDialog(app_fixture)
    qtbot.addWidget(dialog)
    
    # Call _on_restore_clicked without selecting an item
    dialog._on_restore_clicked()
    
    # Check that QMessageBox.warning was called
    QMessageBox.warning.assert_called_once()


def test_version_history_dialog_on_restore_clicked_with_selection(qtbot, app_fixture, monkeypatch):
    """
    Test that the _on_restore_clicked method handles selection correctly.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create some test versions
    versions = [
        {
            "file_path": "/path/to/version1.json",
            "timestamp": "20250324_235959",
            "reason": "Test Reason 1",
            "file_name": "20250324_235959_Test_Reason_1.json"
        }
    ]
    
    # Mock the autosave_manager's get_versions method
    monkeypatch.setattr(app_fixture.autosave_manager, "get_versions", MagicMock(return_value=versions))
    
    # Mock QMessageBox.question to return QMessageBox.StandardButton.Yes
    monkeypatch.setattr(QMessageBox, "question", MagicMock(return_value=QMessageBox.StandardButton.Yes))
    
    # Mock the _restore_version method
    monkeypatch.setattr(VersionHistoryDialog, "_restore_version", MagicMock())
    
    # Create dialog
    dialog = VersionHistoryDialog(app_fixture)
    qtbot.addWidget(dialog)
    
    # Select the first item
    dialog.version_list.setCurrentRow(0)
    
    # Call _on_restore_clicked
    dialog._on_restore_clicked()
    
    # Check that QMessageBox.question was called
    QMessageBox.question.assert_called_once()
    
    # Check that _restore_version was called with the correct path
    dialog._restore_version.assert_called_once_with("/path/to/version1.json")


def test_version_history_dialog_on_version_double_clicked(qtbot, app_fixture, monkeypatch):
    """
    Test that the _on_version_double_clicked method works correctly.
    
    Args:
        qtbot: The qtbot fixture from pytest-qt
        app_fixture: The app_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create some test versions
    versions = [
        {
            "file_path": "/path/to/version1.json",
            "timestamp": "20250324_235959",
            "reason": "Test Reason 1",
            "file_name": "20250324_235959_Test_Reason_1.json"
        }
    ]
    
    # Mock the autosave_manager's get_versions method
    monkeypatch.setattr(app_fixture.autosave_manager, "get_versions", MagicMock(return_value=versions))
    
    # Mock QMessageBox.question to return QMessageBox.StandardButton.Yes
    monkeypatch.setattr(QMessageBox, "question", MagicMock(return_value=QMessageBox.StandardButton.Yes))
    
    # Mock the _restore_version method
    monkeypatch.setattr(VersionHistoryDialog, "_restore_version", MagicMock())
    
    # Create dialog
    dialog = VersionHistoryDialog(app_fixture)
    qtbot.addWidget(dialog)
    
    # Get the first item
    item = dialog.version_list.item(0)
    
    # Call _on_version_double_clicked
    dialog._on_version_double_clicked(item)
    
    # Check that QMessageBox.question was called
    QMessageBox.question.assert_called_once()
    
    # Check that _restore_version was called with the correct path
    dialog._restore_version.assert_called_once_with("/path/to/version1.json")