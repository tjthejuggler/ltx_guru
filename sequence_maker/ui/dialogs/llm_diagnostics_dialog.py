"""
Sequence Maker - LLM Diagnostics Dialog

This module defines the LLMDiagnosticsDialog class, which displays diagnostic information
about LLM operations.
"""

import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem, QTextEdit,
    QComboBox, QGroupBox, QFormLayout, QHeaderView, QSplitter,
    QWidget, QCheckBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MetricsPlotCanvas(FigureCanvas):
    """Canvas for plotting LLM performance metrics."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """
        Initialize the plot canvas.
        
        Args:
            parent: Parent widget.
            width: Plot width in inches.
            height: Plot height in inches.
            dpi: Dots per inch.
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Set background color
        self.fig.patch.set_facecolor('#f0f0f0')
        
        # Set title
        self.axes.set_title('LLM Performance Metrics')
        
        # Hide the plot initially
        self.axes.set_visible(False)
    
    def plot_metrics(self, metrics, metric_type='duration'):
        """
        Plot LLM performance metrics.
        
        Args:
            metrics (list): List of metric dictionaries.
            metric_type (str): Type of metric to plot ('duration', 'tokens', etc.).
        """
        # Clear the plot
        self.axes.clear()
        
        # Show the plot
        self.axes.set_visible(True)
        
        # Check if we have metrics
        if not metrics:
            self.axes.text(0.5, 0.5, 'No metrics available', 
                          horizontalalignment='center',
                          verticalalignment='center',
                          transform=self.axes.transAxes)
            self.draw()
            return
        
        # Extract timestamps and values
        timestamps = []
        values = []
        
        for metric in metrics:
            try:
                # Parse timestamp
                dt = datetime.fromisoformat(metric['timestamp'])
                timestamps.append(dt)
                
                # Get value based on metric type
                if metric_type == 'duration':
                    values.append(metric['duration'])
                    ylabel = 'Duration (seconds)'
                    title = 'Response Time'
                elif metric_type == 'tokens':
                    values.append(metric['tokens'])
                    ylabel = 'Tokens'
                    title = 'Token Usage'
                elif metric_type == 'tokens_per_second':
                    values.append(metric['tokens_per_second'])
                    ylabel = 'Tokens/Second'
                    title = 'Processing Speed'
                elif metric_type == 'cost':
                    values.append(metric['cost'])
                    ylabel = 'Cost ($)'
                    title = 'Cost per Request'
                else:
                    values.append(0)
                    ylabel = 'Value'
                    title = 'Metrics'
            except (KeyError, ValueError) as e:
                # Skip metrics with missing or invalid data
                continue
        
        # Plot the data
        self.axes.plot(timestamps, values, 'o-', color='#007bff')
        
        # Format the plot
        self.axes.set_title(title)
        self.axes.set_ylabel(ylabel)
        self.axes.set_xlabel('Time')
        
        # Rotate x-axis labels for better readability
        plt.setp(self.axes.get_xticklabels(), rotation=45, ha='right')
        
        # Adjust layout
        self.fig.tight_layout()
        
        # Draw the plot
        self.draw()


class LLMDiagnosticsDialog(QDialog):
    """Dialog for displaying LLM diagnostics."""
    
    def __init__(self, app, parent=None):
        """
        Initialize the LLM diagnostics dialog.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.app = app
        self.logger = logging.getLogger("SequenceMaker.LLMDiagnosticsDialog")
        
        # Set dialog properties
        self.setWindowTitle("LLM Diagnostics")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Create UI
        self._create_ui()
        
        # Load metrics
        self._load_metrics()
    
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create header
        self.header_label = QLabel("LLM Diagnostics and Performance Metrics")
        self.header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.main_layout.addWidget(self.header_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_metrics_tab()
        self._create_logs_tab()
        self._create_settings_tab()
        
        # Create button layout
        self.button_layout = QHBoxLayout()
        
        # Create export button
        self.export_button = QPushButton("Export Diagnostics")
        self.export_button.clicked.connect(self._on_export_clicked)
        self.button_layout.addWidget(self.export_button)
        
        # Create refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._load_metrics)
        self.button_layout.addWidget(self.refresh_button)
        
        # Create close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.button_layout.addWidget(self.close_button)
        
        self.main_layout.addLayout(self.button_layout)
    
    def _create_metrics_tab(self):
        """Create the metrics tab."""
        # Create tab widget
        self.metrics_tab = QWidget()
        self.tab_widget.addTab(self.metrics_tab, "Performance Metrics")
        
        # Create layout
        self.metrics_layout = QVBoxLayout(self.metrics_tab)
        
        # Create splitter for resizable sections
        self.metrics_splitter = QSplitter(Qt.Orientation.Vertical)
        self.metrics_layout.addWidget(self.metrics_splitter)
        
        # Create metrics summary group
        self.metrics_summary_group = QGroupBox("Summary")
        self.metrics_summary_layout = QFormLayout(self.metrics_summary_group)
        
        # Add summary fields
        self.total_requests_label = QLabel("0")
        self.metrics_summary_layout.addRow("Total Requests:", self.total_requests_label)
        
        self.total_tokens_label = QLabel("0")
        self.metrics_summary_layout.addRow("Total Tokens:", self.total_tokens_label)
        
        self.total_cost_label = QLabel("$0.00")
        self.metrics_summary_layout.addRow("Total Cost:", self.total_cost_label)
        
        self.avg_response_time_label = QLabel("0.00 seconds")
        self.metrics_summary_layout.addRow("Average Response Time:", self.avg_response_time_label)
        
        self.avg_tokens_per_request_label = QLabel("0")
        self.metrics_summary_layout.addRow("Average Tokens per Request:", self.avg_tokens_per_request_label)
        
        # Add to splitter
        self.metrics_splitter.addWidget(self.metrics_summary_group)
        
        # Create plot controls
        self.plot_controls_layout = QHBoxLayout()
        
        # Create metric type selector
        self.metric_type_label = QLabel("Metric:")
        self.plot_controls_layout.addWidget(self.metric_type_label)
        
        self.metric_type_combo = QComboBox()
        self.metric_type_combo.addItems(["Response Time", "Token Usage", "Processing Speed", "Cost per Request"])
        self.metric_type_combo.currentIndexChanged.connect(self._update_plot)
        self.plot_controls_layout.addWidget(self.metric_type_combo)
        
        # Add plot controls to metrics layout
        self.metrics_layout.addLayout(self.plot_controls_layout)
        
        # Create plot canvas
        self.plot_canvas = MetricsPlotCanvas(self.metrics_tab, width=5, height=4, dpi=100)
        self.metrics_layout.addWidget(self.plot_canvas)
        
        # Create metrics table
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(7)
        self.metrics_table.setHorizontalHeaderLabels([
            "Timestamp", "Duration (s)", "Tokens", "Tokens/Second", 
            "Prompt Length", "Response Length", "Cost ($)"
        ])
        
        # Set table properties
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.metrics_table.horizontalHeader().setStretchLastSection(True)
        self.metrics_table.verticalHeader().setVisible(False)
        self.metrics_table.setAlternatingRowColors(True)
        self.metrics_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Add to splitter
        self.metrics_splitter.addWidget(self.metrics_table)
        
        # Set initial splitter sizes
        self.metrics_splitter.setSizes([100, 300, 200])
    
    def _create_logs_tab(self):
        """Create the logs tab."""
        # Create tab widget
        self.logs_tab = QWidget()
        self.tab_widget.addTab(self.logs_tab, "Logs")
        
        # Create layout
        self.logs_layout = QVBoxLayout(self.logs_tab)
        
        # Create log viewer
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.log_viewer.setFont(QFont("Courier New", 10))
        self.logs_layout.addWidget(self.log_viewer)
        
        # Create log controls
        self.log_controls_layout = QHBoxLayout()
        
        # Create log level selector
        self.log_level_label = QLabel("Log Level:")
        self.log_controls_layout.addWidget(self.log_level_label)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentIndex(1)  # INFO by default
        self.log_level_combo.currentIndexChanged.connect(self._update_logs)
        self.log_controls_layout.addWidget(self.log_level_combo)
        
        # Create log filter
        self.log_filter_label = QLabel("Filter:")
        self.log_controls_layout.addWidget(self.log_filter_label)
        
        self.log_filter_combo = QComboBox()
        self.log_filter_combo.addItems(["All Logs", "LLM Only"])
        self.log_filter_combo.currentIndexChanged.connect(self._update_logs)
        self.log_controls_layout.addWidget(self.log_filter_combo)
        
        # Add log controls to logs layout
        self.logs_layout.addLayout(self.log_controls_layout)
    
    def _create_settings_tab(self):
        """Create the settings tab."""
        # Create tab widget
        self.settings_tab = QWidget()
        self.tab_widget.addTab(self.settings_tab, "Settings")
        
        # Create layout
        self.settings_layout = QVBoxLayout(self.settings_tab)
        
        # Create logging settings group
        self.logging_settings_group = QGroupBox("Logging Settings")
        self.logging_settings_layout = QFormLayout(self.logging_settings_group)
        
        # Add logging settings
        self.enable_detailed_logging_checkbox = QCheckBox("Enable Detailed LLM Logging")
        self.enable_detailed_logging_checkbox.setChecked(True)
        self.enable_detailed_logging_checkbox.stateChanged.connect(self._update_logging_settings)
        self.logging_settings_layout.addRow("", self.enable_detailed_logging_checkbox)
        
        self.log_prompts_checkbox = QCheckBox("Log Full Prompts and Responses")
        self.log_prompts_checkbox.setChecked(False)
        self.log_prompts_checkbox.stateChanged.connect(self._update_logging_settings)
        self.logging_settings_layout.addRow("", self.log_prompts_checkbox)
        
        # Add to settings layout
        self.settings_layout.addWidget(self.logging_settings_group)
        
        # Create metrics settings group
        self.metrics_settings_group = QGroupBox("Metrics Settings")
        self.metrics_settings_layout = QFormLayout(self.metrics_settings_group)
        
        # Add metrics settings
        self.enable_metrics_tracking_checkbox = QCheckBox("Enable Performance Metrics Tracking")
        self.enable_metrics_tracking_checkbox.setChecked(True)
        self.enable_metrics_tracking_checkbox.stateChanged.connect(self._update_metrics_settings)
        self.metrics_settings_layout.addRow("", self.enable_metrics_tracking_checkbox)
        
        self.metrics_retention_combo = QComboBox()
        self.metrics_retention_combo.addItems(["Last 10 requests", "Last 50 requests", "Last 100 requests", "All requests"])
        self.metrics_retention_combo.setCurrentIndex(2)  # Last 100 requests by default
        self.metrics_retention_combo.currentIndexChanged.connect(self._update_metrics_settings)
        self.metrics_settings_layout.addRow("Metrics Retention:", self.metrics_retention_combo)
        
        # Add to settings layout
        self.settings_layout.addWidget(self.metrics_settings_group)
        
        # Add spacer
        self.settings_layout.addStretch()
    
    def _load_metrics(self):
        """Load LLM performance metrics."""
        self.logger.info("Loading LLM performance metrics")
        
        # Get metrics from project
        metrics = []
        
        if self.app.project_manager.current_project:
            # Get metrics from llm_performance_metrics attribute
            if hasattr(self.app.project_manager.current_project, "llm_performance_metrics"):
                metrics = self.app.project_manager.current_project.llm_performance_metrics
            
            # Also check llm_metadata for older format
            elif hasattr(self.app.project_manager.current_project, "llm_metadata"):
                llm_metadata = self.app.project_manager.current_project.llm_metadata
                if "interactions" in llm_metadata:
                    # Convert old format to new format
                    for interaction in llm_metadata["interactions"]:
                        metrics.append({
                            "timestamp": interaction.get("timestamp", ""),
                            "duration": 0,  # Not available in old format
                            "tokens": interaction.get("tokens", 0),
                            "cost": interaction.get("cost", 0),
                            "model": interaction.get("model", ""),
                            "provider": interaction.get("provider", ""),
                            "prompt_length": 0,  # Not available in old format
                            "response_length": 0,  # Not available in old format
                            "tokens_per_second": 0  # Not available in old format
                        })
        
        # Update metrics table
        self._update_metrics_table(metrics)
        
        # Update metrics summary
        self._update_metrics_summary(metrics)
        
        # Update plot
        self._update_plot()
        
        # Update logs
        self._update_logs()
    
    def _update_metrics_table(self, metrics):
        """
        Update the metrics table with the provided metrics.
        
        Args:
            metrics (list): List of metric dictionaries.
        """
        # Clear table
        self.metrics_table.setRowCount(0)
        
        # Add metrics to table
        for metric in metrics:
            row = self.metrics_table.rowCount()
            self.metrics_table.insertRow(row)
            
            # Format timestamp
            timestamp = metric.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            # Add cells
            self.metrics_table.setItem(row, 0, QTableWidgetItem(timestamp))
            self.metrics_table.setItem(row, 1, QTableWidgetItem(f"{metric.get('duration', 0):.2f}"))
            self.metrics_table.setItem(row, 2, QTableWidgetItem(str(metric.get("tokens", 0))))
            self.metrics_table.setItem(row, 3, QTableWidgetItem(f"{metric.get('tokens_per_second', 0):.2f}"))
            self.metrics_table.setItem(row, 4, QTableWidgetItem(str(metric.get("prompt_length", 0))))
            self.metrics_table.setItem(row, 5, QTableWidgetItem(str(metric.get("response_length", 0))))
            self.metrics_table.setItem(row, 6, QTableWidgetItem(f"${metric.get('cost', 0):.4f}"))
            
            # Color expensive requests
            if metric.get("cost", 0) > 0.05:
                for col in range(self.metrics_table.columnCount()):
                    item = self.metrics_table.item(row, col)
                    item.setBackground(QColor(255, 200, 200))
        
        # Sort by timestamp (newest first)
        self.metrics_table.sortItems(0, Qt.SortOrder.DescendingOrder)
    
    def _update_metrics_summary(self, metrics):
        """
        Update the metrics summary with the provided metrics.
        
        Args:
            metrics (list): List of metric dictionaries.
        """
        # Calculate summary statistics
        total_requests = len(metrics)
        total_tokens = sum(metric.get("tokens", 0) for metric in metrics)
        total_cost = sum(metric.get("cost", 0) for metric in metrics)
        
        # Calculate average response time
        durations = [metric.get("duration", 0) for metric in metrics if metric.get("duration", 0) > 0]
        avg_response_time = sum(durations) / len(durations) if durations else 0
        
        # Calculate average tokens per request
        avg_tokens_per_request = total_tokens / total_requests if total_requests > 0 else 0
        
        # Update labels
        self.total_requests_label.setText(str(total_requests))
        self.total_tokens_label.setText(str(total_tokens))
        self.total_cost_label.setText(f"${total_cost:.4f}")
        self.avg_response_time_label.setText(f"{avg_response_time:.2f} seconds")
        self.avg_tokens_per_request_label.setText(f"{avg_tokens_per_request:.1f}")
    
    def _update_plot(self):
        """Update the metrics plot."""
        # Get selected metric type
        metric_type_index = self.metric_type_combo.currentIndex()
        
        if metric_type_index == 0:
            metric_type = "duration"
        elif metric_type_index == 1:
            metric_type = "tokens"
        elif metric_type_index == 2:
            metric_type = "tokens_per_second"
        elif metric_type_index == 3:
            metric_type = "cost"
        else:
            metric_type = "duration"
        
        # Get metrics from project
        metrics = []
        
        if self.app.project_manager.current_project:
            if hasattr(self.app.project_manager.current_project, "llm_performance_metrics"):
                metrics = self.app.project_manager.current_project.llm_performance_metrics
        
        # Update plot
        self.plot_canvas.plot_metrics(metrics, metric_type)
    
    def _update_logs(self):
        """Update the log viewer."""
        # Get selected log level
        log_level_index = self.log_level_combo.currentIndex()
        
        if log_level_index == 0:
            log_level = "DEBUG"
        elif log_level_index == 1:
            log_level = "INFO"
        elif log_level_index == 2:
            log_level = "WARNING"
        elif log_level_index == 3:
            log_level = "ERROR"
        elif log_level_index == 4:
            log_level = "CRITICAL"
        else:
            log_level = "INFO"
        
        # Get selected log filter
        log_filter_index = self.log_filter_combo.currentIndex()
        llm_only = log_filter_index == 1
        
        # Get log file path
        log_file = self.app.config.get("logging", "log_file", fallback=None)
        
        if not log_file or not os.path.exists(log_file):
            self.log_viewer.setText("Log file not found.")
            return
        
        # Read log file
        try:
            with open(log_file, "r") as f:
                log_lines = f.readlines()
            
            # Filter logs
            filtered_logs = []
            
            for line in log_lines:
                # Check log level
                if log_level == "DEBUG":
                    pass  # Include all levels
                elif log_level == "INFO" and ("DEBUG" in line):
                    continue
                elif log_level == "WARNING" and any(level in line for level in ["DEBUG", "INFO"]):
                    continue
                elif log_level == "ERROR" and any(level in line for level in ["DEBUG", "INFO", "WARNING"]):
                    continue
                elif log_level == "CRITICAL" and any(level in line for level in ["DEBUG", "INFO", "WARNING", "ERROR"]):
                    continue
                
                # Check LLM filter
                if llm_only and "LLMManager" not in line:
                    continue
                
                filtered_logs.append(line)
            
            # Update log viewer
            self.log_viewer.setText("".join(filtered_logs[-1000:]))  # Show last 1000 lines
            
            # Scroll to bottom
            self.log_viewer.verticalScrollBar().setValue(self.log_viewer.verticalScrollBar().maximum())
            
        except Exception as e:
            self.logger.error(f"Error reading log file: {e}")
            self.log_viewer.setText(f"Error reading log file: {e}")
    
    def _update_logging_settings(self):
        """Update logging settings."""
        # Get settings
        enable_detailed_logging = self.enable_detailed_logging_checkbox.isChecked()
        log_prompts = self.log_prompts_checkbox.isChecked()
        
        # Update config
        self.app.config.set("logging", "detailed_llm_logging", enable_detailed_logging)
        self.app.config.set("logging", "log_prompts", log_prompts)
        
        # Save config
        self.app.config.save()
        
        self.logger.info(f"Updated logging settings: detailed_llm_logging={enable_detailed_logging}, log_prompts={log_prompts}")
    
    def _update_metrics_settings(self):
        """Update metrics settings."""
        # Get settings
        enable_metrics_tracking = self.enable_metrics_tracking_checkbox.isChecked()
        
        metrics_retention_index = self.metrics_retention_combo.currentIndex()
        if metrics_retention_index == 0:
            metrics_retention = 10
        elif metrics_retention_index == 1:
            metrics_retention = 50
        elif metrics_retention_index == 2:
            metrics_retention = 100
        else:
            metrics_retention = 0  # 0 means all
        
        # Update config
        self.app.config.set("llm", "metrics_tracking", enable_metrics_tracking)
        self.app.config.set("llm", "metrics_retention", metrics_retention)
        
        # Save config
        self.app.config.save()
        
        self.logger.info(f"Updated metrics settings: metrics_tracking={enable_metrics_tracking}, metrics_retention={metrics_retention}")
        
        # Prune metrics if needed
        if metrics_retention > 0 and self.app.project_manager.current_project:
            if hasattr(self.app.project_manager.current_project, "llm_performance_metrics"):
                metrics = self.app.project_manager.current_project.llm_performance_metrics
                
                if len(metrics) > metrics_retention:
                    # Sort by timestamp (newest first)
                    metrics.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                    
                    # Keep only the newest metrics
                    self.app.project_manager.current_project.llm_performance_metrics = metrics[:metrics_retention]
                    
                    # Mark project as changed
                    self.app.project_manager.project_changed.emit()
                    
                    # Reload metrics
                    self._load_metrics()
    
    def _on_export_clicked(self):
        """Handle Export button click."""
        # Ask for export file
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Diagnostics",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Ensure file has .json extension
        if not file_path.lower().endswith(".json"):
            file_path += ".json"
        
        # Collect diagnostic data
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "app_version": self.app.version if hasattr(self.app, "version") else "Unknown",
            "llm_config": {
                "provider": self.app.llm_manager.provider,
                "model": self.app.llm_manager.model,
                "enabled": self.app.llm_manager.enabled
            },
            "metrics_summary": {
                "total_requests": int(self.total_requests_label.text()),
                "total_tokens": int(self.total_tokens_label.text()),
                "total_cost": float(self.total_cost_label.text().replace("$", "")),
                "avg_response_time": float(self.avg_response_time_label.text().split()[0]),
                "avg_tokens_per_request": float(self.avg_tokens_per_request_label.text())
            },
            "metrics": []
        }
        
        # Add metrics
        if self.app.project_manager.current_project:
            if hasattr(self.app.project_manager.current_project, "llm_performance_metrics"):
                diagnostics["metrics"] = self.app.project_manager.current_project.llm_performance_metrics
        
        # Export to file
        try:
            with open(file_path, "w") as f:
                json.dump(diagnostics, f, indent=2)
            
            self.logger.info(f"Exported diagnostics to {file_path}")
            
            # Show success message
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Export Successful",
                f"Diagnostics exported to {file_path}"
            )
            
        except Exception as e:
            self.logger.error(f"Error exporting diagnostics: {e}")
            
            # Show error message
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Export Failed",
                f"Failed to export diagnostics: {e}"
            )