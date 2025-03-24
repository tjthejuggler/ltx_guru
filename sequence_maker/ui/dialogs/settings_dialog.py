"""
Sequence Maker - Settings Dialog

This module defines the SettingsDialog class, which allows users to configure application settings.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QComboBox, QColorDialog, QPushButton, QFormLayout,
    QDialogButtonBox, QGroupBox, QSlider
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QColor


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""
    
    def __init__(self, app, parent=None):
        """
        Initialize the settings dialog.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.SettingsDialog")
        self.app = app
        
        # Set dialog properties
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Create UI
        self._create_ui()
        
        # Load settings
        self._load_settings()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_general_tab()
        self._create_timeline_tab()
        self._create_audio_tab()
        self._create_ball_tab()
        self._create_llm_tab()
        
        # Create button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)
    
    def _create_general_tab(self):
        """Create the general settings tab."""
        # Create tab widget
        self.general_tab = QWidget()
        self.tab_widget.addTab(self.general_tab, "General")
        
        # Create layout
        self.general_layout = QFormLayout(self.general_tab)
        
        # Create settings
        self.autosave_interval_spin = QSpinBox()
        self.autosave_interval_spin.setRange(10, 3600)
        self.autosave_interval_spin.setSuffix(" seconds")
        self.general_layout.addRow("Autosave Interval:", self.autosave_interval_spin)
        
        self.max_autosave_files_spin = QSpinBox()
        self.max_autosave_files_spin.setRange(1, 100)
        self.max_autosave_files_spin.setSuffix(" files")
        self.general_layout.addRow("Max Autosave Files:", self.max_autosave_files_spin)
        
        self.default_project_dir_edit = QLineEdit()
        self.default_project_dir_edit.setReadOnly(True)
        self.default_project_dir_button = QPushButton("Browse...")
        self.default_project_dir_button.clicked.connect(self._on_browse_project_dir)
        
        default_project_dir_layout = QHBoxLayout()
        default_project_dir_layout.addWidget(self.default_project_dir_edit)
        default_project_dir_layout.addWidget(self.default_project_dir_button)
        
        self.general_layout.addRow("Default Project Directory:", default_project_dir_layout)
        
        # Create UI settings group
        self.ui_group = QGroupBox("User Interface")
        self.general_layout.addRow(self.ui_group)
        
        ui_layout = QFormLayout(self.ui_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        ui_layout.addRow("Theme:", self.theme_combo)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setSuffix(" pt")
        ui_layout.addRow("Font Size:", self.font_size_spin)
    
    def _create_timeline_tab(self):
        """Create the timeline settings tab."""
        # Create tab widget
        self.timeline_tab = QWidget()
        self.tab_widget.addTab(self.timeline_tab, "Timeline")
        
        # Create layout
        self.timeline_layout = QFormLayout(self.timeline_tab)
        
        # Create settings
        self.default_duration_spin = QSpinBox()
        self.default_duration_spin.setRange(1, 3600)
        self.default_duration_spin.setSuffix(" seconds")
        self.timeline_layout.addRow("Default Duration:", self.default_duration_spin)
        
        self.default_pixels_spin = QSpinBox()
        self.default_pixels_spin.setRange(1, 4)
        self.default_pixels_spin.setSuffix(" pixels")
        self.timeline_layout.addRow("Default Pixels:", self.default_pixels_spin)
        
        self.default_refresh_rate_spin = QSpinBox()
        self.default_refresh_rate_spin.setRange(1, 1000)
        self.default_refresh_rate_spin.setSuffix(" Hz")
        self.timeline_layout.addRow("Default Refresh Rate:", self.default_refresh_rate_spin)
        
        self.default_ball_count_spin = QSpinBox()
        self.default_ball_count_spin.setRange(1, 10)
        self.default_ball_count_spin.setSuffix(" balls")
        self.timeline_layout.addRow("Default Ball Count:", self.default_ball_count_spin)
        
        self.timeline_height_spin = QSpinBox()
        self.timeline_height_spin.setRange(50, 500)
        self.timeline_height_spin.setSuffix(" pixels")
        self.timeline_layout.addRow("Timeline Height:", self.timeline_height_spin)
        
        self.segment_min_width_spin = QSpinBox()
        self.segment_min_width_spin.setRange(1, 50)
        self.segment_min_width_spin.setSuffix(" pixels")
        self.timeline_layout.addRow("Segment Min Width:", self.segment_min_width_spin)
    
    def _create_audio_tab(self):
        """Create the audio settings tab."""
        # Create tab widget
        self.audio_tab = QWidget()
        self.tab_widget.addTab(self.audio_tab, "Audio")
        
        # Create layout
        self.audio_layout = QFormLayout(self.audio_tab)
        
        # Create settings
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setSingleStep(1)
        self.volume_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.volume_slider.setTickInterval(10)
        
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(QLabel("0%"))
        volume_layout.addWidget(QLabel("100%"))
        
        self.audio_layout.addRow("Volume:", volume_layout)
        
        # Create visualization settings group
        self.visualization_group = QGroupBox("Visualizations")
        self.audio_layout.addRow(self.visualization_group)
        
        visualization_layout = QFormLayout(self.visualization_group)
        
        self.waveform_check = QCheckBox("Waveform")
        visualization_layout.addRow(self.waveform_check)
        
        self.waveform_color_button = QPushButton("Choose Color...")
        self.waveform_color_button.clicked.connect(self._on_waveform_color)
        visualization_layout.addRow("Waveform Color:", self.waveform_color_button)
        
        self.beats_check = QCheckBox("Beats")
        visualization_layout.addRow(self.beats_check)
        
        self.beats_color_button = QPushButton("Choose Color...")
        self.beats_color_button.clicked.connect(self._on_beats_color)
        visualization_layout.addRow("Beats Color:", self.beats_color_button)
        
        self.beat_detection_threshold_spin = QDoubleSpinBox()
        self.beat_detection_threshold_spin.setRange(0.1, 1.0)
        self.beat_detection_threshold_spin.setSingleStep(0.1)
        visualization_layout.addRow("Beat Detection Threshold:", self.beat_detection_threshold_spin)
    
    def _create_ball_tab(self):
        """Create the ball settings tab."""
        # Create tab widget
        self.ball_tab = QWidget()
        self.tab_widget.addTab(self.ball_tab, "Ball Control")
        
        # Create layout
        self.ball_layout = QFormLayout(self.ball_tab)
        
        # Create settings
        self.discovery_timeout_spin = QSpinBox()
        self.discovery_timeout_spin.setRange(1, 60)
        self.discovery_timeout_spin.setSuffix(" seconds")
        self.ball_layout.addRow("Discovery Timeout:", self.discovery_timeout_spin)
        
        self.network_subnet_edit = QLineEdit()
        self.ball_layout.addRow("Network Subnet:", self.network_subnet_edit)
        
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.ball_layout.addRow("UDP Port:", self.port_spin)
    def _create_llm_tab(self):
        """Create the LLM settings tab."""
        # Create tab widget
        self.llm_tab = QWidget()
        self.tab_widget.addTab(self.llm_tab, "LLM Integration")
        
        # Create layout
        self.llm_layout = QVBoxLayout(self.llm_tab)
        
        # Create general LLM settings group
        general_llm_group = QGroupBox("General Settings")
        general_llm_layout = QFormLayout(general_llm_group)
        
        self.llm_enabled_check = QCheckBox("Enable LLM Integration")
        general_llm_layout.addRow(self.llm_enabled_check)
        
        self.llm_provider_combo = QComboBox()
        self.llm_provider_combo.addItems(["OpenAI", "Anthropic", "Local"])
        self.llm_provider_combo.currentTextChanged.connect(self._on_llm_provider_changed)
        general_llm_layout.addRow("Provider:", self.llm_provider_combo)
        
        self.llm_api_key_edit = QLineEdit()
        self.llm_api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        general_llm_layout.addRow("API Key:", self.llm_api_key_edit)
        
        self.llm_model_edit = QLineEdit()
        general_llm_layout.addRow("Model:", self.llm_model_edit)
        
        self.llm_local_endpoint_edit = QLineEdit()
        self.llm_local_endpoint_edit.setPlaceholderText("http://localhost:8000/v1/completions")
        general_llm_layout.addRow("Local Endpoint:", self.llm_local_endpoint_edit)
        
        self.llm_layout.addWidget(general_llm_group)
        
        # Create model parameters group
        model_params_group = QGroupBox("Model Parameters")
        model_params_layout = QFormLayout(model_params_group)
        
        self.llm_temperature_spin = QDoubleSpinBox()
        self.llm_temperature_spin.setRange(0.0, 2.0)
        self.llm_temperature_spin.setSingleStep(0.1)
        self.llm_temperature_spin.setValue(0.7)
        model_params_layout.addRow("Temperature:", self.llm_temperature_spin)
        
        self.llm_max_tokens_spin = QSpinBox()
        self.llm_max_tokens_spin.setRange(100, 8000)
        self.llm_max_tokens_spin.setSingleStep(100)
        self.llm_max_tokens_spin.setValue(1000)
        model_params_layout.addRow("Max Tokens:", self.llm_max_tokens_spin)
        
        # Add presets button
        presets_button_layout = QHBoxLayout()
        self.manage_presets_button = QPushButton("Manage Presets")
        self.manage_presets_button.clicked.connect(self._on_manage_presets_clicked)
        presets_button_layout.addWidget(self.manage_presets_button)
        model_params_layout.addRow("Presets:", presets_button_layout)
        
        self.llm_layout.addWidget(model_params_group)
        
        # Create user interface group
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout(ui_group)
        
        self.llm_confirmation_mode_combo = QComboBox()
        self.llm_confirmation_mode_combo.addItems(["Full Confirmation", "Selective Confirmation", "Full Automation"])
        ui_layout.addRow("Default Confirmation Mode:", self.llm_confirmation_mode_combo)
        
        # Add customization buttons
        customization_layout = QHBoxLayout()
        
        self.custom_instructions_button = QPushButton("Custom Instructions")
        self.custom_instructions_button.clicked.connect(self._on_custom_instructions_clicked)
        customization_layout.addWidget(self.custom_instructions_button)
        
        self.task_templates_button = QPushButton("Task Templates")
        self.task_templates_button.clicked.connect(self._on_task_templates_clicked)
        customization_layout.addWidget(self.task_templates_button)
        
        ui_layout.addRow("Customization:", customization_layout)
        
        self.llm_layout.addWidget(ui_group)
        
        # Create token usage group
        token_usage_group = QGroupBox("Token Usage")
        token_usage_layout = QFormLayout(token_usage_group)
        
        self.llm_token_usage_label = QLabel("0 tokens used")
        token_usage_layout.addRow("Current Session:", self.llm_token_usage_label)
        
        self.llm_cost_label = QLabel("$0.00")
        token_usage_layout.addRow("Estimated Cost:", self.llm_cost_label)
        
        self.llm_reset_usage_button = QPushButton("Reset Usage Statistics")
        self.llm_reset_usage_button.clicked.connect(self._on_reset_usage_clicked)
        token_usage_layout.addRow(self.llm_reset_usage_button)
        
        self.llm_layout.addWidget(token_usage_group)
        
        # Add stretch to push everything to the top
        self.llm_layout.addStretch()
        self.llm_layout.addStretch()
    
    def _load_settings(self):
        """Load settings from the application configuration."""
        # General settings
        self.autosave_interval_spin.setValue(self.app.config.get("general", "autosave_interval"))
        self.max_autosave_files_spin.setValue(self.app.config.get("general", "max_autosave_files"))
        self.default_project_dir_edit.setText(self.app.config.get("general", "default_project_dir"))
        
        # UI settings
        self.theme_combo.setCurrentText(self.app.config.get("ui", "theme").capitalize())
        self.font_size_spin.setValue(self.app.config.get("ui", "font_size"))
        
        # Timeline settings
        self.default_duration_spin.setValue(self.app.config.get("timeline", "default_duration"))
        self.default_pixels_spin.setValue(self.app.config.get("timeline", "default_pixels"))
        self.default_refresh_rate_spin.setValue(self.app.config.get("timeline", "default_refresh_rate"))
        self.default_ball_count_spin.setValue(self.app.config.get("timeline", "default_ball_count"))
        self.timeline_height_spin.setValue(self.app.config.get("timeline", "timeline_height"))
        self.segment_min_width_spin.setValue(self.app.config.get("timeline", "segment_min_width"))
        
        # Audio settings
        self.volume_slider.setValue(int(self.app.config.get("audio", "volume") * 100))
        
        visualizations = self.app.config.get("audio", "visualizations")
        self.waveform_check.setChecked("waveform" in visualizations)
        self.beats_check.setChecked("beats" in visualizations)
        
        self.waveform_color = self.app.config.get("audio", "waveform_color")
        self.beats_color = self.app.config.get("audio", "beats_color")
        
        self.beat_detection_threshold_spin.setValue(self.app.config.get("audio", "beat_detection_threshold"))
        
        # Ball settings
        self.discovery_timeout_spin.setValue(self.app.config.get("ball_control", "discovery_timeout"))
        self.network_subnet_edit.setText(self.app.config.get("ball_control", "network_subnet"))
        self.port_spin.setValue(self.app.config.get("ball_control", "port"))
        
        # LLM settings
        self.llm_enabled_check.setChecked(self.app.config.get("llm", "enabled"))
        
        provider = self.app.config.get("llm", "provider")
        if provider:
            self.llm_provider_combo.setCurrentText(provider.capitalize())
        
        self.llm_api_key_edit.setText(self.app.config.get("llm", "api_key"))
        self.llm_model_edit.setText(self.app.config.get("llm", "model"))
        self.llm_temperature_spin.setValue(self.app.config.get("llm", "temperature"))
        self.llm_max_tokens_spin.setValue(self.app.config.get("llm", "max_tokens", 1000))
        self.llm_local_endpoint_edit.setText(self.app.config.get("llm", "local_endpoint", ""))
        
        # Set confirmation mode
        confirmation_mode = self.app.config.get("llm", "confirmation_mode", "full_confirmation")
        confirmation_mode = confirmation_mode.replace("_", " ").title()
        index = self.llm_confirmation_mode_combo.findText(confirmation_mode)
        if index >= 0:
            self.llm_confirmation_mode_combo.setCurrentIndex(index)
        
        # Update token usage display
        if self.app.llm_manager:
            tokens = self.app.llm_manager.token_usage
            cost = self.app.llm_manager.estimated_cost
            self.llm_token_usage_label.setText(f"{tokens} tokens used")
            self.llm_cost_label.setText(f"${cost:.2f}")
        
        # Update visibility based on provider
        self._on_llm_provider_changed(self.llm_provider_combo.currentText())
    
    def _save_settings(self):
        """Save settings to the application configuration."""
        # General settings
        self.app.config.set("general", "autosave_interval", self.autosave_interval_spin.value())
        self.app.config.set("general", "max_autosave_files", self.max_autosave_files_spin.value())
        self.app.config.set("general", "default_project_dir", self.default_project_dir_edit.text())
        
        # UI settings
        self.app.config.set("ui", "theme", self.theme_combo.currentText().lower())
        self.app.config.set("ui", "font_size", self.font_size_spin.value())
        
        # Timeline settings
        self.app.config.set("timeline", "default_duration", self.default_duration_spin.value())
        self.app.config.set("timeline", "default_pixels", self.default_pixels_spin.value())
        self.app.config.set("timeline", "default_refresh_rate", self.default_refresh_rate_spin.value())
        self.app.config.set("timeline", "default_ball_count", self.default_ball_count_spin.value())
        self.app.config.set("timeline", "timeline_height", self.timeline_height_spin.value())
        self.app.config.set("timeline", "segment_min_width", self.segment_min_width_spin.value())
        
        # Audio settings
        self.app.config.set("audio", "volume", self.volume_slider.value() / 100.0)
        
        visualizations = []
        if self.waveform_check.isChecked():
            visualizations.append("waveform")
        if self.beats_check.isChecked():
            visualizations.append("beats")
        
        self.app.config.set("audio", "visualizations", visualizations)
        self.app.config.set("audio", "waveform_color", self.waveform_color)
        self.app.config.set("audio", "beats_color", self.beats_color)
        self.app.config.set("audio", "beat_detection_threshold", self.beat_detection_threshold_spin.value())
        
        # Ball settings
        self.app.config.set("ball_control", "discovery_timeout", self.discovery_timeout_spin.value())
        self.app.config.set("ball_control", "network_subnet", self.network_subnet_edit.text())
        self.app.config.set("ball_control", "port", self.port_spin.value())
        
        # LLM settings
        self.app.config.set("llm", "enabled", self.llm_enabled_check.isChecked())
        self.app.config.set("llm", "provider", self.llm_provider_combo.currentText().lower())
        self.app.config.set("llm", "api_key", self.llm_api_key_edit.text())
        self.app.config.set("llm", "model", self.llm_model_edit.text())
        self.app.config.set("llm", "temperature", self.llm_temperature_spin.value())
        self.app.config.set("llm", "max_tokens", self.llm_max_tokens_spin.value())
        self.app.config.set("llm", "local_endpoint", self.llm_local_endpoint_edit.text())
        self.app.config.set("llm", "confirmation_mode", self.llm_confirmation_mode_combo.currentText().lower().replace(" ", "_"))
        
        # Save configuration
        self.app.config.save()
    
    def _on_browse_project_dir(self):
        """Handle Browse button click for project directory."""
        from PyQt6.QtWidgets import QFileDialog
        
        # Show directory dialog
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Default Project Directory",
            self.default_project_dir_edit.text()
        )
        
        if directory:
            self.default_project_dir_edit.setText(directory)
    
    def _on_waveform_color(self):
        """Handle Choose Color button click for waveform color."""
        # Show color dialog
        color = QColor(*self.waveform_color)
        
        dialog = QColorDialog(color, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get selected color
            color = dialog.selectedColor()
            
            # Update color
            self.waveform_color = (color.red(), color.green(), color.blue())
            
            # Update button style
            self.waveform_color_button.setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()})"
            )
    
    def _on_beats_color(self):
        """Handle Choose Color button click for beats color."""
        # Show color dialog
        color = QColor(*self.beats_color)
        
        dialog = QColorDialog(color, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get selected color
            color = dialog.selectedColor()
            
            # Update color
            self.beats_color = (color.red(), color.green(), color.blue())
            
            # Update button style
            self.beats_color_button.setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()})"
            )
    
    def _on_llm_provider_changed(self, provider):
        """
        Handle LLM provider change.
        
        Args:
            provider (str): Selected provider.
        """
        # Show/hide API key field based on provider
        show_api_key = provider != "Local"
        self.llm_api_key_edit.setVisible(show_api_key)
        self.llm_layout.labelForField(self.llm_api_key_edit).setVisible(show_api_key)
        
        # Show/hide local endpoint field based on provider
        show_local_endpoint = provider == "Local"
        self.llm_local_endpoint_edit.setVisible(show_local_endpoint)
        self.llm_layout.labelForField(self.llm_local_endpoint_edit).setVisible(show_local_endpoint)
        
        # Update model field placeholder based on provider
        if provider == "OpenAI":
            self.llm_model_edit.setPlaceholderText("gpt-4-turbo")
        elif provider == "Anthropic":
            self.llm_model_edit.setPlaceholderText("claude-3-opus-20240229")
        else:  # Local
            self.llm_model_edit.setPlaceholderText("local-model")
    
    def _on_reset_usage_clicked(self):
        """Handle Reset Usage Statistics button click."""
        # Reset token usage in LLM manager
        if self.app.llm_manager:
            self.app.llm_manager.reset_token_usage()
            
            # Update labels
            self.llm_token_usage_label.setText("0 tokens used")
            self.llm_cost_label.setText("$0.00")
    
    def _on_manage_presets_clicked(self):
        """Handle Manage Presets button click."""
        from ui.dialogs.llm_presets_dialog import LLMPresetsDialog
        
        # Create and show dialog
        dialog = LLMPresetsDialog(self.app, self)
        dialog.exec()
    
    def _on_custom_instructions_clicked(self):
        """Handle Custom Instructions button click."""
        from ui.dialogs.custom_instructions_dialog import CustomInstructionsDialog
        
        # Create and show dialog
        dialog = CustomInstructionsDialog(self.app, self)
        dialog.exec()
    
    def _on_task_templates_clicked(self):
        """Handle Task Templates button click."""
        from ui.dialogs.task_templates_dialog import TaskTemplatesDialog
        
        # Create and show dialog
        dialog = TaskTemplatesDialog(self.app, self)
        dialog.exec()
    
    def accept(self):
        """Handle dialog acceptance."""
        # Save settings
        self._save_settings()
        
        # Accept dialog
        super().accept()