"""
Sequence Maker - Tests for AutosaveManager

This module contains tests for the AutosaveManager class.
"""

import os
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from managers.autosave_manager import AutosaveManager


def test_autosave_manager_initialization(app_fixture):
    """
    Test that the AutosaveManager initializes correctly.
    
    Args:
        app_fixture: The app_fixture fixture
    """
    # Create AutosaveManager
    autosave_manager = AutosaveManager(app_fixture)
    
    # Check that the autosave_manager was initialized correctly
    assert autosave_manager.app == app_fixture
    assert autosave_manager.max_versions == app_fixture.config.get("general", "max_autosave_files", 10)
    assert autosave_manager.autosave_dir is None


def test_ensure_autosave_directory(app_fixture, monkeypatch):
    """
    Test that the _ensure_autosave_directory method creates the directory correctly.
    
    Args:
        app_fixture: The app_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create a temporary project file
    with tempfile.NamedTemporaryFile(suffix=".smproj", delete=False) as temp_file:
        project_path = temp_file.name
    
    try:
        # Set the project file path
        app_fixture.project_manager.current_project.file_path = project_path
        
        # Create AutosaveManager
        autosave_manager = AutosaveManager(app_fixture)
        
        # Call _ensure_autosave_directory
        autosave_manager._ensure_autosave_directory()
        
        # Check that the autosave directory was created
        expected_dir = Path(project_path).parent / f"{Path(project_path).stem}_versions"
        assert autosave_manager.autosave_dir == expected_dir
        assert expected_dir.exists()
        
    finally:
        # Clean up the temporary file
        if os.path.exists(project_path):
            os.unlink(project_path)
        
        # Clean up the autosave directory
        if autosave_manager.autosave_dir and autosave_manager.autosave_dir.exists():
            autosave_manager.autosave_dir.rmdir()


def test_save_version(app_fixture, monkeypatch):
    """
    Test that the save_version method saves a version correctly.
    
    Args:
        app_fixture: The app_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create a temporary project file
    with tempfile.NamedTemporaryFile(suffix=".smproj", delete=False) as temp_file:
        project_path = temp_file.name
    
    try:
        # Set the project file path
        app_fixture.project_manager.current_project.file_path = project_path
        
        # Mock the project's to_dict method
        project_data = {"name": "Test Project", "timelines": []}
        monkeypatch.setattr(app_fixture.project_manager.current_project, "to_dict", MagicMock(return_value=project_data))
        
        # Create AutosaveManager
        autosave_manager = AutosaveManager(app_fixture)
        
        # Call save_version
        result = autosave_manager.save_version("Test Reason")
        
        # Check that the version was saved
        assert result is True
        
        # Check that the version file was created
        assert autosave_manager.autosave_dir.exists()
        version_files = list(autosave_manager.autosave_dir.glob("*.json"))
        assert len(version_files) == 1
        
        # Check the content of the version file
        with open(version_files[0], "r") as f:
            saved_data = json.load(f)
        
        # Check that the project data was saved correctly
        assert saved_data["name"] == "Test Project"
        assert saved_data["timelines"] == []
        
        # Check that the version metadata was added
        assert "version_metadata" in saved_data
        assert saved_data["version_metadata"]["reason"] == "Test Reason"
        assert saved_data["version_metadata"]["original_file"] == project_path
        
    finally:
        # Clean up the temporary file
        if os.path.exists(project_path):
            os.unlink(project_path)
        
        # Clean up the autosave directory
        if autosave_manager.autosave_dir and autosave_manager.autosave_dir.exists():
            for file in autosave_manager.autosave_dir.glob("*.json"):
                file.unlink()
            autosave_manager.autosave_dir.rmdir()


def test_get_versions(app_fixture, monkeypatch):
    """
    Test that the get_versions method returns the correct versions.
    
    Args:
        app_fixture: The app_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create a temporary project file
    with tempfile.NamedTemporaryFile(suffix=".smproj", delete=False) as temp_file:
        project_path = temp_file.name
    
    try:
        # Set the project file path
        app_fixture.project_manager.current_project.file_path = project_path
        
        # Create AutosaveManager
        autosave_manager = AutosaveManager(app_fixture)
        
        # Create autosave directory
        autosave_manager._ensure_autosave_directory()
        
        # Create some version files
        version_data = {
            "name": "Test Project",
            "timelines": [],
            "version_metadata": {
                "timestamp": "20250324_235959",
                "reason": "Test Reason",
                "original_file": project_path
            }
        }
        
        version_file1 = autosave_manager.autosave_dir / "20250324_235959_Test_Reason.json"
        with open(version_file1, "w") as f:
            json.dump(version_data, f)
        
        version_data["version_metadata"]["timestamp"] = "20250325_000000"
        version_data["version_metadata"]["reason"] = "Another Reason"
        version_file2 = autosave_manager.autosave_dir / "20250325_000000_Another_Reason.json"
        with open(version_file2, "w") as f:
            json.dump(version_data, f)
        
        # Call get_versions
        versions = autosave_manager.get_versions()
        
        # Check that the versions were returned correctly
        assert len(versions) == 2
        assert versions[0]["timestamp"] == "20250325_000000"
        assert versions[0]["reason"] == "Another Reason"
        assert versions[1]["timestamp"] == "20250324_235959"
        assert versions[1]["reason"] == "Test Reason"
        
    finally:
        # Clean up the temporary file
        if os.path.exists(project_path):
            os.unlink(project_path)
        
        # Clean up the autosave directory
        if autosave_manager.autosave_dir and autosave_manager.autosave_dir.exists():
            for file in autosave_manager.autosave_dir.glob("*.json"):
                file.unlink()
            autosave_manager.autosave_dir.rmdir()


def test_restore_version(app_fixture, monkeypatch):
    """
    Test that the restore_version method restores a version correctly.
    
    Args:
        app_fixture: The app_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create a temporary project file
    with tempfile.NamedTemporaryFile(suffix=".smproj", delete=False) as temp_file:
        project_path = temp_file.name
    
    try:
        # Set the project file path
        app_fixture.project_manager.current_project.file_path = project_path
        
        # Create AutosaveManager
        autosave_manager = AutosaveManager(app_fixture)
        
        # Create autosave directory
        autosave_manager._ensure_autosave_directory()
        
        # Create a version file
        version_data = {
            "name": "Test Project",
            "timelines": [],
            "version_metadata": {
                "timestamp": "20250324_235959",
                "reason": "Test Reason",
                "original_file": project_path
            }
        }
        
        version_file = autosave_manager.autosave_dir / "20250324_235959_Test_Reason.json"
        with open(version_file, "w") as f:
            json.dump(version_data, f)
        
        # Mock the project manager's load_from_dict method
        mock_project = MagicMock()
        monkeypatch.setattr(app_fixture.project_manager, "load_from_dict", MagicMock(return_value=mock_project))
        
        # Mock the project manager's set_current_project method
        monkeypatch.setattr(app_fixture.project_manager, "set_current_project", MagicMock())
        
        # Call restore_version
        result = autosave_manager.restore_version(str(version_file))
        
        # Check that the version was restored
        assert result is True
        
        # Check that the project manager's load_from_dict method was called with the correct data
        app_fixture.project_manager.load_from_dict.assert_called_once()
        args = app_fixture.project_manager.load_from_dict.call_args[0][0]
        assert args["name"] == "Test Project"
        assert args["timelines"] == []
        assert "version_metadata" not in args  # Metadata should be removed
        
        # Check that the project manager's set_current_project method was called with the correct project
        app_fixture.project_manager.set_current_project.assert_called_once_with(mock_project)
        
    finally:
        # Clean up the temporary file
        if os.path.exists(project_path):
            os.unlink(project_path)
        
        # Clean up the autosave directory
        if autosave_manager.autosave_dir and autosave_manager.autosave_dir.exists():
            for file in autosave_manager.autosave_dir.glob("*.json"):
                file.unlink()
            autosave_manager.autosave_dir.rmdir()


def test_prune_old_versions(app_fixture, monkeypatch):
    """
    Test that the _prune_old_versions method removes old versions correctly.
    
    Args:
        app_fixture: The app_fixture fixture
        monkeypatch: The monkeypatch fixture from pytest
    """
    # Create a temporary project file
    with tempfile.NamedTemporaryFile(suffix=".smproj", delete=False) as temp_file:
        project_path = temp_file.name
    
    try:
        # Set the project file path
        app_fixture.project_manager.current_project.file_path = project_path
        
        # Set max_versions to 2
        monkeypatch.setattr(app_fixture.config, "get", lambda section, key, default=None: 2 if key == "max_autosave_files" else default)
        
        # Create AutosaveManager
        autosave_manager = AutosaveManager(app_fixture)
        
        # Create autosave directory
        autosave_manager._ensure_autosave_directory()
        
        # Create some version files
        for i in range(5):
            version_data = {
                "name": "Test Project",
                "timelines": [],
                "version_metadata": {
                    "timestamp": f"2025032{i}_235959",
                    "reason": f"Test Reason {i}",
                    "original_file": project_path
                }
            }
            
            version_file = autosave_manager.autosave_dir / f"2025032{i}_235959_Test_Reason_{i}.json"
            with open(version_file, "w") as f:
                json.dump(version_data, f)
        
        # Call _prune_old_versions
        autosave_manager._prune_old_versions()
        
        # Check that only the 2 newest versions remain
        version_files = list(autosave_manager.autosave_dir.glob("*.json"))
        assert len(version_files) == 2
        
        # Check that the newest versions remain
        version_files = sorted(version_files)
        assert "20250323_235959" in version_files[0].name
        assert "20250324_235959" in version_files[1].name
        
    finally:
        # Clean up the temporary file
        if os.path.exists(project_path):
            os.unlink(project_path)
        
        # Clean up the autosave directory
        if autosave_manager.autosave_dir and autosave_manager.autosave_dir.exists():
            for file in autosave_manager.autosave_dir.glob("*.json"):
                file.unlink()
            autosave_manager.autosave_dir.rmdir()