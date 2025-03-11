"""
Sequence Maker - Ball Manager

This module defines the BallManager class, which handles communication with LTX balls.
"""

import logging
import socket
import threading
import time
import struct
from PyQt6.QtCore import QObject, pyqtSignal

from app.constants import BALL_DISCOVERY_TIMEOUT, BALL_CONTROL_PORT, BALL_BROADCAST_IDENTIFIER


class Ball:
    """
    Represents an LTX juggling ball.
    
    Attributes:
        ip (str): IP address of the ball.
        port (int): UDP port for communication.
        last_seen (float): Timestamp when the ball was last seen.
        timeline_index (int): Index of the timeline associated with this ball.
    """
    
    def __init__(self, ip, port=BALL_CONTROL_PORT):
        """
        Initialize a ball.
        
        Args:
            ip (str): IP address of the ball.
            port (int, optional): UDP port for communication. Defaults to BALL_CONTROL_PORT.
        """
        self.ip = ip
        self.port = port
        self.last_seen = time.time()
        self.timeline_index = -1  # -1 means not associated with any timeline
    
    def __str__(self):
        """Return a string representation of the ball."""
        timeline_str = f"Timeline {self.timeline_index}" if self.timeline_index >= 0 else "Not assigned"
        return f"Ball({self.ip}:{self.port}, {timeline_str})"


class BallManager(QObject):
    """
    Manages communication with LTX juggling balls.
    
    Signals:
        ball_discovered: Emitted when a ball is discovered.
        ball_lost: Emitted when a ball is lost.
        ball_assigned: Emitted when a ball is assigned to a timeline.
        ball_unassigned: Emitted when a ball is unassigned from a timeline.
        color_sent: Emitted when a color is sent to a ball.
    """
    
    # Signals
    ball_discovered = pyqtSignal(object)  # ball
    ball_lost = pyqtSignal(object)  # ball
    ball_assigned = pyqtSignal(object, int)  # ball, timeline_index
    ball_unassigned = pyqtSignal(object)  # ball
    color_sent = pyqtSignal(object, tuple)  # ball, color
    
    def __init__(self, app):
        """
        Initialize the ball manager.
        
        Args:
            app: The main application instance.
        """
        super().__init__()
        
        self.logger = logging.getLogger("SequenceMaker.BallManager")
        self.app = app
        
        # Ball discovery
        self.discovery_socket = None
        self.discovery_thread = None
        self.discovery_stop_event = threading.Event()
        self.discovery_timeout = app.config.get("ball_control", "discovery_timeout")
        self.network_subnet = app.config.get("ball_control", "network_subnet")
        
        # Known balls
        self.balls = {}  # ip -> Ball
        
        # Real-time streaming
        self.streaming = False
        self.streaming_thread = None
        self.streaming_stop_event = threading.Event()
    
    def start_discovery(self):
        """
        Start ball discovery.
        
        Returns:
            bool: True if discovery started, False otherwise.
        """
        if self.discovery_thread and self.discovery_thread.is_alive():
            self.logger.warning("Ball discovery already running")
            return False
        
        self.logger.info("Starting ball discovery")
        
        # Reset stop event
        self.discovery_stop_event.clear()
        
        # Start discovery thread
        self.discovery_thread = threading.Thread(
            target=self._discovery_worker,
            daemon=True
        )
        self.discovery_thread.start()
        
        return True
    
    def stop_discovery(self):
        """
        Stop ball discovery.
        
        Returns:
            bool: True if discovery stopped, False otherwise.
        """
        if not self.discovery_thread or not self.discovery_thread.is_alive():
            return False
        
        self.logger.info("Stopping ball discovery")
        
        # Set stop event
        self.discovery_stop_event.set()
        
        # Wait for thread to finish
        self.discovery_thread.join(timeout=1.0)
        
        # Close socket if open
        if self.discovery_socket:
            try:
                self.discovery_socket.close()
            except:
                pass
            finally:
                self.discovery_socket = None
        
        return True
    
    def connect_balls(self):
        """
        Connect to balls by starting discovery.
        
        Returns:
            bool: True if connection process started, False otherwise.
        """
        # Start passive discovery
        self.start_discovery()
        
        # Show ball scan dialog
        from ui.dialogs.ball_scan_dialog import BallScanDialog
        dialog = BallScanDialog(self.app)
        dialog.ball_selected.connect(self._on_ball_selected)
        dialog.exec()
        
        return True
    
    def _on_ball_selected(self, ball_ip, timeline_index):
        """
        Handle ball selected from scan dialog.
        
        Args:
            ball_ip (str): IP address of the selected ball.
            timeline_index (int): Timeline index to assign the ball to.
        """
        self.logger.info(f"Ball selected: {ball_ip} for timeline {timeline_index}")
        
        # Check if ball already exists
        if ball_ip in self.balls:
            ball = self.balls[ball_ip]
        else:
            # Create new ball
            ball = Ball(ball_ip)
            self.balls[ball_ip] = ball
            
            # Emit discovered signal
            self.ball_discovered.emit(ball)
        
        # Assign ball to timeline
        self.assign_ball_to_timeline(ball, timeline_index)
    
    def disconnect_balls(self):
        """
        Disconnect from balls by stopping discovery and streaming.
        
        Returns:
            bool: True if disconnection successful, False otherwise.
        """
        # Stop streaming
        self.stop_streaming()
        
        # Stop discovery
        return self.stop_discovery()
    
    def assign_ball_to_timeline(self, ball, timeline_index):
        """
        Assign a ball to a timeline.
        
        Args:
            ball (Ball): Ball to assign.
            timeline_index (int): Timeline index to assign the ball to.
        
        Returns:
            bool: True if assignment successful, False otherwise.
        """
        if ball.ip not in self.balls:
            self.logger.warning(f"Cannot assign ball: Ball {ball.ip} not found")
            return False
        
        # Check if another ball is already assigned to this timeline
        for other_ball in self.balls.values():
            if other_ball.timeline_index == timeline_index:
                # Unassign the other ball
                other_ball.timeline_index = -1
                self.ball_unassigned.emit(other_ball)
        
        # Assign the ball
        ball.timeline_index = timeline_index
        
        # Emit signal
        self.ball_assigned.emit(ball, timeline_index)
        
        return True
    
    def unassign_ball(self, ball):
        """
        Unassign a ball from its timeline.
        
        Args:
            ball (Ball): Ball to unassign.
        
        Returns:
            bool: True if unassignment successful, False otherwise.
        """
        if ball.ip not in self.balls:
            self.logger.warning(f"Cannot unassign ball: Ball {ball.ip} not found")
            return False
        
        # Unassign the ball
        ball.timeline_index = -1
        
        # Emit signal
        self.ball_unassigned.emit(ball)
        
        return True
    
    def get_ball_for_timeline(self, timeline_index):
        """
        Get the ball assigned to a timeline.
        
        Args:
            timeline_index (int): Timeline index.
        
        Returns:
            Ball: The ball assigned to the timeline, or None if no ball is assigned.
        """
        for ball in self.balls.values():
            if ball.timeline_index == timeline_index:
                return ball
        return None
    
    def send_color(self, ball, color):
        """
        Send a color command to a ball.
        
        Args:
            ball (Ball): Ball to send the command to.
            color (tuple): RGB color tuple.
        
        Returns:
            bool: True if command sent successfully, False otherwise.
        """
        if ball.ip not in self.balls:
            self.logger.warning(f"Cannot send color: Ball {ball.ip} not found")
            return False
        
        try:
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Create color command packet
            packet = self._create_color_packet(color)
            
            # Send packet
            sock.sendto(packet, (ball.ip, ball.port))
            
            # Close socket
            sock.close()
            
            # Emit signal
            self.color_sent.emit(ball, color)
            
            return True
        except Exception as e:
            self.logger.error(f"Error sending color to ball: {e}")
            return False
    
    def send_color_to_timeline(self, timeline_index, color):
        """
        Send a color command to the ball assigned to a timeline.
        
        Args:
            timeline_index (int): Timeline index.
            color (tuple): RGB color tuple.
        
        Returns:
            bool: True if command sent successfully, False otherwise.
        """
        ball = self.get_ball_for_timeline(timeline_index)
        if not ball:
            self.logger.warning(f"Cannot send color: No ball assigned to timeline {timeline_index}")
            return False
        
        return self.send_color(ball, color)
    
    def start_streaming(self):
        """
        Start real-time color streaming based on timeline position.
        
        Returns:
            bool: True if streaming started, False otherwise.
        """
        if self.streaming_thread and self.streaming_thread.is_alive():
            self.logger.warning("Color streaming already running")
            return False
        
        self.logger.info("Starting color streaming")
        
        # Reset stop event
        self.streaming_stop_event.clear()
        
        # Set streaming flag
        self.streaming = True
        
        # Start streaming thread
        self.streaming_thread = threading.Thread(
            target=self._streaming_worker,
            daemon=True
        )
        self.streaming_thread.start()
        
        return True
    
    def stop_streaming(self):
        """
        Stop real-time color streaming.
        
        Returns:
            bool: True if streaming stopped, False otherwise.
        """
        if not self.streaming_thread or not self.streaming_thread.is_alive():
            return False
        
        self.logger.info("Stopping color streaming")
        
        # Set stop event
        self.streaming_stop_event.set()
        
        # Wait for thread to finish
        self.streaming_thread.join(timeout=1.0)
        
        # Reset streaming flag
        self.streaming = False
        
        return True
    
    def _discovery_worker(self):
        """Ball discovery worker thread function."""
        self.logger.info("Ball discovery worker started")
        
        try:
            # Create UDP socket for receiving broadcast packets
            self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.discovery_socket.bind(('', BALL_CONTROL_PORT))
            self.discovery_socket.settimeout(1.0)  # 1 second timeout for recv
            
            # Discovery loop
            while not self.discovery_stop_event.is_set():
                try:
                    # Receive broadcast packet
                    data, addr = self.discovery_socket.recvfrom(1024)
                    
                    # Check if it's a ball broadcast
                    if BALL_BROADCAST_IDENTIFIER in data.decode('latin-1'):
                        ball_ip = addr[0]
                        
                        # Check if this is a new ball
                        if ball_ip not in self.balls:
                            self.logger.info(f"Discovered ball: {ball_ip}")
                            
                            # Create new ball
                            ball = Ball(ball_ip)
                            
                            # Add to known balls
                            self.balls[ball_ip] = ball
                            
                            # Emit signal
                            self.ball_discovered.emit(ball)
                        else:
                            # Update last seen timestamp
                            self.balls[ball_ip].last_seen = time.time()
                
                except socket.timeout:
                    # Check for lost balls
                    current_time = time.time()
                    for ball_ip in list(self.balls.keys()):
                        ball = self.balls[ball_ip]
                        if current_time - ball.last_seen > self.discovery_timeout:
                            self.logger.info(f"Ball lost: {ball_ip}")
                            
                            # Emit signal
                            self.ball_lost.emit(ball)
                            
                            # Remove from known balls
                            del self.balls[ball_ip]
                
                except Exception as e:
                    self.logger.error(f"Error in discovery worker: {e}")
        
        except Exception as e:
            self.logger.error(f"Error in discovery worker: {e}")
        
        finally:
            # Close socket
            if self.discovery_socket:
                try:
                    self.discovery_socket.close()
                except:
                    pass
                finally:
                    self.discovery_socket = None
            
            self.logger.info("Ball discovery worker stopped")
    
    def _streaming_worker(self):
        """Color streaming worker thread function."""
        self.logger.info("Color streaming worker started")
        
        try:
            # Streaming loop
            while not self.streaming_stop_event.is_set():
                # Get current position
                position = self.app.timeline_manager.position
                self.logger.debug(f"Streaming worker position: {position:.2f}s")
                
                # Get timelines
                timelines = self.app.timeline_manager.get_timelines()
                
                # Send colors to balls
                for timeline_index, timeline in enumerate(timelines):
                    # Get color at current position
                    color = timeline.get_color_at_time(position)
                    self.logger.debug(f"Timeline {timeline_index} color at {position:.2f}s: {color}")
                    
                    # Skip if no color defined
                    if not color:
                        continue
                    
                    # Send color to ball
                    self.send_color_to_timeline(timeline_index, color)
                
                # Ensure timeline manager position is updated from audio manager
                audio_position = self.app.audio_manager.position
                if abs(position - audio_position) > 0.01:  # If positions differ by more than 10ms
                    self.logger.debug(f"Syncing timeline position ({position:.2f}s) with audio position ({audio_position:.2f}s)")
                    self.app.timeline_manager.set_position(audio_position)
                
                # Sleep to reduce CPU usage and network traffic
                time.sleep(0.05)
        
        except Exception as e:
            self.logger.error(f"Error in streaming worker: {e}")
        
        finally:
            self.logger.info("Color streaming worker stopped")
    
    def send_brightness(self, ball, brightness):
        """
        Send a brightness command to a ball.
        
        Args:
            ball (Ball): Ball to send the command to.
            brightness (int): Brightness value (0-15).
        
        Returns:
            bool: True if command sent successfully, False otherwise.
        """
        if ball.ip not in self.balls:
            self.logger.warning(f"Cannot send brightness: Ball {ball.ip} not found")
            return False
        
        try:
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Create brightness command packet
            packet = self._create_brightness_packet(brightness)
            
            # Send packet
            sock.sendto(packet, (ball.ip, ball.port))
            
            # Close socket
            sock.close()
            
            return True
        except Exception as e:
            self.logger.error(f"Error sending brightness to ball: {e}")
            return False
    
    def send_brightness_to_timeline(self, timeline_index, brightness):
        """
        Send a brightness command to the ball assigned to a timeline.
        
        Args:
            timeline_index (int): Timeline index.
            brightness (int): Brightness value (0-15).
        
        Returns:
            bool: True if command sent successfully, False otherwise.
        """
        ball = self.get_ball_for_timeline(timeline_index)
        if not ball:
            self.logger.warning(f"Cannot send brightness: No ball assigned to timeline {timeline_index}")
            return False
        
        return self.send_brightness(ball, brightness)
    
    def _create_brightness_packet(self, brightness):
        """
        Create a brightness command packet.
        
        Args:
            brightness (int): Brightness value (0-15).
        
        Returns:
            bytes: Brightness command packet.
        """
        # Ensure brightness is in valid range
        brightness = max(0, min(15, brightness))
        
        # Create UDP header
        udp_header = struct.pack("!bIBH", 66, 0, 0, 0)
        
        # Create brightness command data
        # Byte 0: Command opcode (0x10 for brightness)
        # Byte 1: Brightness value
        data = struct.pack("!BB", 0x10, brightness)
        
        # Combine header and data
        packet = udp_header + data
        
        return packet
    
    def _create_color_packet(self, color):
        """
        Create a color command packet.
        
        Args:
            color (tuple): RGB color tuple.
        
        Returns:
            bytes: Color command packet.
        """
        r, g, b = color
        
        # Create UDP header similar to the Python example
        # Byte 0:    66 (ASCII 'B')
        # Bytes 1-4: 32-bit integer (0)
        # Byte 5:    8-bit integer (0)
        # Bytes 6-7: 16-bit integer (0)
        udp_header = struct.pack("!bIBH", 66, 0, 0, 0)
        
        # Create color command data
        # Byte 0:    Command opcode (0x0A for color)
        # Bytes 1-3: RGB values (doubled for brightness as in the example)
        data = struct.pack("!BBBB", 0x0A, min(255, r*2), min(255, g*2), min(255, b*2))
        
        # Combine header and data
        packet = udp_header + data
        
        return packet