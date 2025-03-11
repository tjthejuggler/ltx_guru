"""
Sequence Maker - Ball Scan Dialog

This module defines the BallScanDialog class, which allows users to scan for and connect to LTX balls.
"""

import logging
import socket
import struct
import threading
import time
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QProgressBar, QCheckBox,
    QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot

from app.constants import BALL_CONTROL_PORT


class BallScanDialog(QDialog):
    """
    Dialog for scanning and connecting to LTX balls.
    
    Signals:
        ball_selected: Emitted when a ball is selected.
    """
    
    # Signals
    ball_selected = pyqtSignal(str, int)  # ip, timeline_index
    
    def __init__(self, app, parent=None):
        """
        Initialize the ball scan dialog.
        
        Args:
            app: The main application instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("SequenceMaker.BallScanDialog")
        self.app = app
        
        # Dialog properties
        self.setWindowTitle("Scan for Balls")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        # Scanning state
        self.is_scanning = False
        self.scan_thread = None
        self.scan_stop_event = threading.Event()
        self.discovered_balls = {}  # ip -> last_seen_time
        
        # Create UI
        self._create_ui()
        
        # Start auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._update_ball_list)
        self.refresh_timer.start(2000)  # Update every 2 seconds to give more time for user interaction
        
    def _create_ui(self):
        """Create the user interface."""
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create scan controls
        self.scan_layout = QHBoxLayout()
        self.main_layout.addLayout(self.scan_layout)
        
        self.scan_button = QPushButton("Start Scanning")
        self.scan_button.clicked.connect(self._on_scan_clicked)
        self.scan_layout.addWidget(self.scan_button)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.hide()
        self.scan_layout.addWidget(self.progress_bar)
        
        # Create ball list
        self.list_label = QLabel("Available Balls:")
        self.main_layout.addWidget(self.list_label)
        
        self.ball_list = QListWidget()
        self.ball_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.ball_list.itemDoubleClicked.connect(self._on_ball_double_clicked)
        self.ball_list.itemClicked.connect(self._on_ball_clicked)
        # Pause refresh when user interacts with the list
        self.ball_list.entered.connect(self._pause_refresh)
        self.ball_list.viewportEntered.connect(self._pause_refresh)
        self.main_layout.addWidget(self.ball_list)
        
        # Create timeline selection
        self.timeline_layout = QHBoxLayout()
        self.main_layout.addLayout(self.timeline_layout)
        
        self.timeline_label = QLabel("Assign to Timeline:")
        self.timeline_layout.addWidget(self.timeline_label)
        
        self.timeline_buttons = []
        
        # Create a horizontal frame to contain timeline buttons
        self.timeline_frame = QFrame()
        self.timeline_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.timeline_button_layout = QHBoxLayout(self.timeline_frame)
        self.timeline_button_layout.setContentsMargins(5, 5, 5, 5)
        self.timeline_layout.addWidget(self.timeline_frame)
        
        # Create timeline buttons based on current project
        self._create_timeline_buttons()
        
        # Create dialog buttons
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self._on_connect_clicked)
        self.connect_button.setEnabled(False)
        self.button_layout.addWidget(self.connect_button)
        
        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.accept)
        self.button_layout.addWidget(self.done_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)
    
    def _create_timeline_buttons(self):
        """Create timeline selection buttons based on current project."""
        # Clear existing buttons
        for button in self.timeline_buttons:
            button.deleteLater()
        self.timeline_buttons.clear()
        
        # Get timelines from current project
        timelines = []
        if self.app.project_manager.current_project:
            timelines = self.app.project_manager.current_project.timelines
        
        # Create buttons for each timeline
        for i, timeline in enumerate(timelines):
            button = QPushButton(f"Ball {i+1}")
            button.setCheckable(True)
            button.setProperty("timeline_index", i)
            button.clicked.connect(self._on_timeline_button_clicked)
            
            self.timeline_button_layout.addWidget(button)
            self.timeline_buttons.append(button)
        
        # If no timelines, add a message
        if not timelines:
            label = QLabel("No timelines available")
            self.timeline_button_layout.addWidget(label)
            self.timeline_buttons.append(label)
            self.connect_button.setEnabled(False)
    
    def _on_scan_clicked(self):
        """Handle scan button click."""
        if self.is_scanning:
            # Stop scanning
            self._stop_scanning()
            self.scan_button.setText("Start Scanning")
            self.progress_bar.hide()
        else:
            # Start scanning
            self._start_scanning()
            self.scan_button.setText("Stop Scanning")
            self.progress_bar.show()
    
    def _on_ball_double_clicked(self, item):
        """Handle ball item double click."""
        # Get ball IP from item
        ball_ip = item.data(Qt.ItemDataRole.UserRole)
        
        # Make sure the item stays selected
        self.ball_list.setCurrentItem(item)
        
        # Select the first timeline by default if none is selected
        timeline_selected = False
        for button in self.timeline_buttons:
            if isinstance(button, QPushButton) and button.isChecked():
                timeline_selected = True
                break
                
        if not timeline_selected and self.timeline_buttons and isinstance(self.timeline_buttons[0], QPushButton):
            self.timeline_buttons[0].setChecked(True)
        
        # Enable connect button
        self.connect_button.setEnabled(True)
    
    def _on_timeline_button_clicked(self):
        """Handle timeline button click."""
        # Ensure only one button is checked
        sender = self.sender()
        for button in self.timeline_buttons:
            if isinstance(button, QPushButton) and button != sender:
                button.setChecked(False)
        
        # Enable connect button if a ball is selected
        self.connect_button.setEnabled(
            self.ball_list.currentItem() is not None and 
            any(button.isChecked() for button in self.timeline_buttons if isinstance(button, QPushButton))
        )
    
    def _on_connect_clicked(self):
        """Handle connect button click."""
        # Get selected ball
        item = self.ball_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No Ball Selected", "Please select a ball to connect.")
            return
        
        ball_ip = item.data(Qt.ItemDataRole.UserRole)
        
        # Get selected timeline
        timeline_index = -1
        for button in self.timeline_buttons:
            if isinstance(button, QPushButton) and button.isChecked():
                timeline_index = button.property("timeline_index")
                break
        
        if timeline_index == -1:
            QMessageBox.warning(self, "No Timeline Selected", "Please select a timeline to assign the ball to.")
            return
        
        # Emit signal
        self.ball_selected.emit(ball_ip, timeline_index)
        
        # Show success message
        QMessageBox.information(self, "Ball Connected",
                               f"Ball {ball_ip} connected to Timeline {timeline_index + 1}.\n\n"
                               f"You can connect more balls or close this dialog when done.")
        
        # Uncheck the timeline button to prevent accidentally connecting another ball to the same timeline
        for button in self.timeline_buttons:
            if isinstance(button, QPushButton) and button.isChecked():
                button.setChecked(False)
                break
        
        # Deselect the ball in the list
        self.ball_list.clearSelection()
        
        # Disable connect button until new selections are made
        self.connect_button.setEnabled(False)
    
    def _start_scanning(self):
        """Start scanning for balls."""
        if self.scan_thread and self.scan_thread.is_alive():
            return
        
        self.logger.info("Starting ball scanning")
        
        # Reset stop event
        self.scan_stop_event.clear()
        
        # Set scanning flag
        self.is_scanning = True
        
        # Start scan thread
        self.scan_thread = threading.Thread(
            target=self._scan_worker,
            daemon=True
        )
        self.scan_thread.start()
    
    def _stop_scanning(self):
        """Stop scanning for balls."""
        if not self.scan_thread or not self.scan_thread.is_alive():
            return
        
        self.logger.info("Stopping ball scanning")
        
        # Set stop event
        self.scan_stop_event.set()
        
        # Wait for thread to finish
        self.scan_thread.join(timeout=1.0)
        
        # Reset scanning flag
        self.is_scanning = False
    
    def _scan_worker(self):
        """Ball scanning worker thread function."""
        self.logger.info("Ball scanning worker started")
        
        try:
            # Create UDP socket for broadcasting
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(0.5)  # 500ms timeout
            
            # Create a separate socket for receiving responses
            recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            recv_sock.bind(('', BALL_CONTROL_PORT))  # Bind to all interfaces
            recv_sock.settimeout(0.1)  # 100ms timeout for quick scanning
            
            # Get network subnet from config
            subnet = self.app.config.get("ball_control", "network_subnet")
            if not subnet:
                # Try multiple common subnets
                subnets = ["192.168.43", "192.168.1", "192.168.0", "10.0.0"]
            else:
                subnets = [subnet]
            
            # Scan loop
            while not self.scan_stop_event.is_set():
                # Try each subnet
                for subnet in subnets:
                    if self.scan_stop_event.is_set():
                        break
                    
                    self.logger.info(f"Scanning subnet: {subnet}")
                    
                    # Send broadcast to the entire subnet
                    broadcast_ip = f"{subnet}.255"
                    
                    try:
                        # Create UDP header similar to the Python example
                        udp_header = struct.pack("!bIBH", 66, 0, 0, 0)
                        
                        # Send a ping packet to the broadcast address
                        sock.sendto(udp_header, (broadcast_ip, BALL_CONTROL_PORT))
                        
                        # Also try specific IPs from the Python example
                        known_ips = [f"{subnet}.23", f"{subnet}.81", f"{subnet}.35", f"{subnet}.85", f"{subnet}.240"]
                        for ip in known_ips:
                            try:
                                sock.sendto(udp_header, (ip, BALL_CONTROL_PORT))
                            except:
                                pass
                        
                        # Try to receive responses for a short period
                        start_time = time.time()
                        while time.time() - start_time < 1.0 and not self.scan_stop_event.is_set():
                            try:
                                data, addr = recv_sock.recvfrom(1024)
                                ball_ip = addr[0]
                                
                                # Ball responded
                                self.logger.info(f"Ball responded: {ball_ip}")
                                self.discovered_balls[ball_ip] = time.time()
                            except socket.timeout:
                                # No response yet, continue trying
                                pass
                    
                    except Exception as e:
                        self.logger.error(f"Error scanning subnet {subnet}: {e}")
                
                # Sleep before next scan cycle
                time.sleep(0.5)
        
        except Exception as e:
            self.logger.error(f"Error in scan worker: {e}")
        
        finally:
            # Close sockets
            try:
                sock.close()
            except:
                pass
                
            try:
                recv_sock.close()
            except:
                pass
            
            self.logger.info("Ball scanning worker stopped")
    
    def _update_ball_list(self):
        """Update the ball list with discovered balls."""
        # Check if any balls have been discovered
        if not self.discovered_balls:
            return
        
        # Get current time
        current_time = time.time()
        
        # Remember currently selected ball
        current_selection = None
        if self.ball_list.currentItem():
            current_selection = self.ball_list.currentItem().data(Qt.ItemDataRole.UserRole)
        
        # Update ball list without clearing if possible
        existing_ips = []
        for i in range(self.ball_list.count()):
            item = self.ball_list.item(i)
            ip = item.data(Qt.ItemDataRole.UserRole)
            existing_ips.append(ip)
        
        # Add new balls to list
        for ball_ip, last_seen in list(self.discovered_balls.items()):
            # Remove balls that haven't been seen for a while
            if current_time - last_seen > 10.0:  # 10 seconds timeout
                del self.discovered_balls[ball_ip]
                continue
            
            # Only add if not already in list
            if ball_ip not in existing_ips:
                # Create list item
                item = QListWidgetItem(f"Ball: {ball_ip}")
                item.setData(Qt.ItemDataRole.UserRole, ball_ip)
                self.ball_list.addItem(item)
        
        # Restore selection if possible
        if current_selection:
            for i in range(self.ball_list.count()):
                item = self.ball_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == current_selection:
                    self.ball_list.setCurrentItem(item)
                    break
        
        # Enable connect button if a ball is selected and a timeline is selected
        self.connect_button.setEnabled(
            self.ball_list.currentItem() is not None and
            any(button.isChecked() for button in self.timeline_buttons if isinstance(button, QPushButton))
        )
    
    def _pause_refresh(self):
        """Pause the refresh timer when user is interacting with the list."""
        self.refresh_timer.stop()
        
        # Resume after a delay to allow user interaction
        QTimer.singleShot(5000, self._resume_refresh)
    
    def _resume_refresh(self):
        """Resume the refresh timer."""
        if not self.refresh_timer.isActive() and not self.isHidden():
            self.refresh_timer.start(2000)
    
    def _on_ball_clicked(self, item):
        """Handle ball item click."""
        # Get ball IP from item
        ball_ip = item.data(Qt.ItemDataRole.UserRole)
        
        # Make sure the item stays selected
        self.ball_list.setCurrentItem(item)
        
        # Pause refresh to prevent selection loss
        self._pause_refresh()
        
        # Enable connect button if a timeline is selected
        self.connect_button.setEnabled(
            any(button.isChecked() for button in self.timeline_buttons if isinstance(button, QPushButton))
        )
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        # Stop scanning
        self._stop_scanning()
        
        # Stop refresh timer
        self.refresh_timer.stop()
        
        # Accept event
        event.accept()