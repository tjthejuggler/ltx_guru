"""
Sequence Maker - LLM Diagnostics Dialog

This module defines the LLMDiagnosticsDialog class, which displays LLM performance metrics and diagnostics.
"""

import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QBrush
# Temporarily commented out due to missing module
# from PyQt6.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis


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
        self.header_label = QLabel("LLM Diagnostics")
        self.header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.main_layout.addWidget(self.header_label)
        
        # Create token usage display
        self.token_layout = QHBoxLayout()
        self.main_layout.addLayout(self.token_layout)
        
        self.token_usage_label = QLabel("Total Token Usage: 0 tokens")
        self.token_usage_label.setFont(QFont("Arial", 12))
        self.token_layout.addWidget(self.token_usage_label)
        
        self.token_layout.addStretch()
        
        self.cost_label = QLabel("Estimated Cost: $0.0000")
        self.cost_label.setFont(QFont("Arial", 12))
        self.token_layout.addWidget(self.cost_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget, 1)
        
        # Create metrics tab
        self.metrics_tab = QWidget()
        self.metrics_layout = QVBoxLayout(self.metrics_tab)
        
        self.metrics_label = QLabel("Performance Metrics")
        self.metrics_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.metrics_layout.addWidget(self.metrics_label)
        
        self.metrics_list = QListWidget()
        self.metrics_list.setAlternatingRowColors(True)
        self.metrics_layout.addWidget(self.metrics_list)
        
        self.tab_widget.addTab(self.metrics_tab, "Performance Metrics")
        
        # Create usage history tab
        self.usage_tab = QWidget()
        self.usage_layout = QVBoxLayout(self.usage_tab)
        
        self.usage_label = QLabel("Token Usage History")
        self.usage_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.usage_layout.addWidget(self.usage_label)
        
        self.usage_table = QTableWidget()
        self.usage_table.setColumnCount(5)
        self.usage_table.setHorizontalHeaderLabels(["Timestamp", "Tokens", "Cost", "Model", "Provider"])
        self.usage_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.usage_layout.addWidget(self.usage_table)
        
        self.tab_widget.addTab(self.usage_tab, "Token Usage History")
        
        # Charts tab temporarily disabled due to missing PyQt6.QtChart module
        # Create a placeholder tab with a message
        self.charts_tab = QWidget()
        self.charts_layout = QVBoxLayout(self.charts_tab)
        
        self.charts_label = QLabel("Performance Charts")
        self.charts_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.charts_layout.addWidget(self.charts_label)
        
        # Add a message about the missing module
        self.charts_message = QLabel("Charts are temporarily unavailable. Please install PyQt6-Charts package.")
        self.charts_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.charts_layout.addWidget(self.charts_message)
        
        self.tab_widget.addTab(self.charts_tab, "Charts")
        
        # Create button layout
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        
        self.button_layout.addStretch()
        
        # Create refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._load_metrics)
        self.button_layout.addWidget(self.refresh_button)
        
        # Create close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.close_button)
    
    def _load_metrics(self):
        """Load metrics from the current project."""
        # Clear existing data
        self.metrics_list.clear()
        self.usage_table.setRowCount(0)
        # Chart-related code temporarily commented out
        # self.token_chart.removeAllSeries()
        # self.time_chart.removeAllSeries()
        
        # Check if project is loaded
        if not self.app.project_manager.current_project:
            return
        
        # Load performance metrics
        if hasattr(self.app.project_manager.current_project, "llm_performance_metrics"):
            metrics = self.app.project_manager.current_project.llm_performance_metrics
            
            # Add metrics to list
            for metric in metrics:
                # Create item
                item = QListWidgetItem()
                
                # Format timestamp
                timestamp = metric.get("timestamp", "")
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                
                # Set text
                item.setText(
                    f"{timestamp} - {metric.get('model', 'Unknown')} - "
                    f"{metric.get('tokens', 0)} tokens in {metric.get('duration', 0):.2f}s - "
                    f"{metric.get('tokens_per_second', 0):.2f} tokens/s"
                )
                
                # Add to list
                self.metrics_list.addItem(item)
            
            # Response time chart creation temporarily commented out due to missing PyQt6.QtChart module
            # if metrics:
            #     time_series = QLineSeries()
            #     time_series.setName("Response Time (s)")
            #
            #     for i, metric in enumerate(metrics):
            #         time_series.append(i, metric.get("duration", 0))
            #
            #     self.time_chart.addSeries(time_series)
            #
            #     # Create axes
            #     axis_x = QValueAxis()
            #     axis_x.setTitleText("Request Number")
            #     axis_x.setRange(0, len(metrics) - 1)
            #
            #     axis_y = QValueAxis()
            #     axis_y.setTitleText("Response Time (s)")
            #     axis_y.setRange(0, max(metric.get("duration", 0) for metric in metrics) * 1.1)
            #
            #     self.time_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            #     self.time_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            #
            #     time_series.attachAxis(axis_x)
            #     time_series.attachAxis(axis_y)
        
        # Load token usage
        if hasattr(self.app.project_manager.current_project, "llm_metadata"):
            metadata = self.app.project_manager.current_project.llm_metadata
            
            # Update token usage display
            token_usage = metadata.get("token_usage", 0)
            self.token_usage_label.setText(f"Total Token Usage: {token_usage:,} tokens")
            
            # Update cost display
            cost = metadata.get("estimated_cost", 0.0)
            self.cost_label.setText(f"Estimated Cost: ${cost:.4f}")
            
            # Add interactions to table
            interactions = metadata.get("interactions", [])
            self.usage_table.setRowCount(len(interactions))
            
            for i, interaction in enumerate(interactions):
                # Format timestamp
                timestamp = interaction.get("timestamp", "")
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                
                # Add timestamp
                self.usage_table.setItem(i, 0, QTableWidgetItem(timestamp))
                
                # Add tokens
                tokens_item = QTableWidgetItem(str(interaction.get("tokens", 0)))
                tokens_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.usage_table.setItem(i, 1, tokens_item)
                
                # Add cost
                cost_item = QTableWidgetItem(f"${interaction.get('cost', 0.0):.4f}")
                cost_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.usage_table.setItem(i, 2, cost_item)
                
                # Add model
                self.usage_table.setItem(i, 3, QTableWidgetItem(interaction.get("model", "Unknown")))
                
                # Add provider
                self.usage_table.setItem(i, 4, QTableWidgetItem(interaction.get("provider", "Unknown")))
            
            # Token usage chart creation temporarily commented out due to missing PyQt6.QtChart module
            # if interactions:
            #     token_series = QLineSeries()
            #     token_series.setName("Tokens")
            #
            #     cumulative_tokens = 0
            #     for i, interaction in enumerate(interactions):
            #         cumulative_tokens += interaction.get("tokens", 0)
            #         token_series.append(i, cumulative_tokens)
            #
            #     self.token_chart.addSeries(token_series)
            #
            #     # Create axes
            #     axis_x = QValueAxis()
            #     axis_x.setTitleText("Interaction Number")
            #     axis_x.setRange(0, len(interactions) - 1)
            #
            #     axis_y = QValueAxis()
            #     axis_y.setTitleText("Cumulative Tokens")
            #     axis_y.setRange(0, cumulative_tokens * 1.1)
            #
            #     self.token_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            #     self.token_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            #
            #     token_series.attachAxis(axis_x)
            #     token_series.attachAxis(axis_y)