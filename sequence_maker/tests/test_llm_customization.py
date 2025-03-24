"""
Sequence Maker - LLM Customization Tests

This module contains tests for the LLM customization features.
"""

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from models.llm_customization import LLMPreset, LLMTaskTemplate, create_default_presets, create_default_templates
from ui.dialogs.custom_instructions_dialog import CustomInstructionsDialog
from ui.dialogs.llm_presets_dialog import LLMPresetsDialog
from ui.dialogs.task_templates_dialog import TaskTemplatesDialog


def test_llm_preset_creation():
    """Test LLM preset creation."""
    # Create a preset
    preset = LLMPreset(
        name="Test Preset",
        provider="openai",
        model="gpt-4-turbo",
        temperature=0.7,
        max_tokens=1024,
        top_p=0.9,
        frequency_penalty=0.1,
        presence_penalty=0.1
    )
    
    # Check preset properties
    assert preset.name == "Test Preset"
    assert preset.provider == "openai"
    assert preset.model == "gpt-4-turbo"
    assert preset.temperature == 0.7
    assert preset.max_tokens == 1024
    assert preset.top_p == 0.9
    assert preset.frequency_penalty == 0.1
    assert preset.presence_penalty == 0.1
    
    # Test to_dict method
    preset_dict = preset.to_dict()
    assert preset_dict["name"] == "Test Preset"
    assert preset_dict["provider"] == "openai"
    assert preset_dict["model"] == "gpt-4-turbo"
    assert preset_dict["temperature"] == 0.7
    assert preset_dict["max_tokens"] == 1024
    assert preset_dict["top_p"] == 0.9
    assert preset_dict["frequency_penalty"] == 0.1
    assert preset_dict["presence_penalty"] == 0.1
    
    # Test from_dict method
    preset2 = LLMPreset.from_dict(preset_dict)
    assert preset2.name == preset.name
    assert preset2.provider == preset.provider
    assert preset2.model == preset.model
    assert preset2.temperature == preset.temperature
    assert preset2.max_tokens == preset.max_tokens
    assert preset2.top_p == preset.top_p
    assert preset2.frequency_penalty == preset.frequency_penalty
    assert preset2.presence_penalty == preset.presence_penalty


def test_llm_task_template_creation():
    """Test LLM task template creation."""
    # Create a template
    template = LLMTaskTemplate(
        name="Test Template",
        prompt="This is a test prompt",
        description="This is a test description"
    )
    
    # Check template properties
    assert template.name == "Test Template"
    assert template.prompt == "This is a test prompt"
    assert template.description == "This is a test description"
    
    # Test to_dict method
    template_dict = template.to_dict()
    assert template_dict["name"] == "Test Template"
    assert template_dict["prompt"] == "This is a test prompt"
    assert template_dict["description"] == "This is a test description"
    
    # Test from_dict method
    template2 = LLMTaskTemplate.from_dict(template_dict)
    assert template2.name == template.name
    assert template2.prompt == template.prompt
    assert template2.description == template.description


def test_default_presets():
    """Test default presets creation."""
    presets = create_default_presets()
    
    # Check that we have at least one preset
    assert len(presets) > 0
    
    # Check that all presets are valid
    for preset in presets:
        assert isinstance(preset, LLMPreset)
        assert preset.name
        assert preset.provider
        assert preset.model
        assert isinstance(preset.temperature, float)
        assert isinstance(preset.max_tokens, int)


def test_default_templates():
    """Test default templates creation."""
    templates = create_default_templates()
    
    # Check that we have at least one template
    assert len(templates) > 0
    
    # Check that all templates are valid
    for template in templates:
        assert isinstance(template, LLMTaskTemplate)
        assert template.name
        assert template.prompt
        assert isinstance(template.description, str)


def test_project_customization_storage(qtbot, app_with_project):
    """Test project customization storage."""
    app = app_with_project
    project = app.project_manager.current_project
    
    # Set custom instructions
    custom_instructions = "These are custom instructions for testing"
    project.llm_custom_instructions = custom_instructions
    
    # Create and add a preset
    preset = LLMPreset(
        name="Test Preset",
        provider="openai",
        model="gpt-4-turbo",
        temperature=0.7,
        max_tokens=1024
    )
    project.llm_presets = [preset.to_dict()]
    
    # Create and add a template
    template = LLMTaskTemplate(
        name="Test Template",
        prompt="This is a test prompt",
        description="This is a test description"
    )
    project.llm_task_templates = [template.to_dict()]
    
    # Set active preset
    project.llm_active_preset = "Test Preset"
    
    # Save and reload project
    app.project_manager.save_project()
    app.project_manager.close_project()
    app.project_manager.load_project(project.file_path)
    
    # Check that customization data was saved and loaded correctly
    project = app.project_manager.current_project
    assert project.llm_custom_instructions == custom_instructions
    assert len(project.llm_presets) == 1
    assert project.llm_presets[0]["name"] == "Test Preset"
    assert len(project.llm_task_templates) == 1
    assert project.llm_task_templates[0]["name"] == "Test Template"
    assert project.llm_active_preset == "Test Preset"


@pytest.mark.skip(reason="Manual test requiring UI interaction")
def test_custom_instructions_dialog(qtbot, app_with_project):
    """Test custom instructions dialog."""
    app = app_with_project
    
    # Create dialog
    dialog = CustomInstructionsDialog(app)
    qtbot.addWidget(dialog)
    
    # Set instructions
    instructions = "These are test instructions"
    dialog.instructions_editor.setText(instructions)
    
    # Click save button
    qtbot.mouseClick(dialog.save_button, Qt.MouseButton.LeftButton)
    
    # Check that instructions were saved
    assert app.project_manager.current_project.llm_custom_instructions == instructions


@pytest.mark.skip(reason="Manual test requiring UI interaction")
def test_llm_presets_dialog(qtbot, app_with_project):
    """Test LLM presets dialog."""
    app = app_with_project
    
    # Create dialog
    dialog = LLMPresetsDialog(app)
    qtbot.addWidget(dialog)
    
    # Check that default presets are loaded
    assert dialog.preset_list.count() > 0
    
    # Add a new preset
    qtbot.mouseClick(dialog.add_button, Qt.MouseButton.LeftButton)
    
    # Set preset properties
    dialog.name_edit.setText("Test Preset")
    dialog.provider_combo.setCurrentText("OpenAI")
    dialog.model_edit.setText("gpt-4-turbo")
    dialog.temperature_spin.setValue(0.5)
    dialog.max_tokens_spin.setValue(2000)
    
    # Save preset
    qtbot.mouseClick(dialog.save_preset_button, Qt.MouseButton.LeftButton)
    
    # Close dialog
    qtbot.mouseClick(dialog.close_button, Qt.MouseButton.LeftButton)
    
    # Check that preset was saved
    presets = app.project_manager.current_project.llm_presets
    assert any(preset["name"] == "Test Preset" for preset in presets)


@pytest.mark.skip(reason="Manual test requiring UI interaction")
def test_task_templates_dialog(qtbot, app_with_project):
    """Test task templates dialog."""
    app = app_with_project
    
    # Create dialog
    dialog = TaskTemplatesDialog(app)
    qtbot.addWidget(dialog)
    
    # Check that default templates are loaded
    assert dialog.template_list.count() > 0
    
    # Add a new template
    qtbot.mouseClick(dialog.add_button, Qt.MouseButton.LeftButton)
    
    # Set template properties
    dialog.name_edit.setText("Test Template")
    dialog.description_edit.setText("Test Description")
    dialog.prompt_edit.setText("This is a test prompt")
    
    # Save template
    qtbot.mouseClick(dialog.save_template_button, Qt.MouseButton.LeftButton)
    
    # Close dialog
    qtbot.mouseClick(dialog.close_button, Qt.MouseButton.LeftButton)
    
    # Check that template was saved
    templates = app.project_manager.current_project.llm_task_templates
    assert any(template["name"] == "Test Template" for template in templates)