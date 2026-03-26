"""
Sequence Maker - LED Ball Controller

Handles sending color commands to a real LTX LED ball via UDP.
Uses the ball's native protocol: an 8-byte UDP header followed by
a 4-byte color command (0x0a, R, G, B).
"""

import socket
import struct
import logging

logger = logging.getLogger("SequenceMaker.LEDBallController")

BALL_PORT = 41412


class LEDBallController:
    """Controller for a single external LED ball via UDP."""

    def __init__(self, ip="", port=BALL_PORT):
        self.ip = ip
        self.port = port

    def send_color(self, r, g, b):
        """Send an RGB color command to the LED ball.

        Args:
            r: Red value 0-255
            g: Green value 0-255
            b: Blue value 0-255
        """
        if not self.ip:
            return

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                udp_header = struct.pack("!bIBH", 66, 0, 0, 0)
                color_data = struct.pack("!BBBB", 0x0A, r, g, b)
                full_command = udp_header + color_data
                s.sendto(full_command, (self.ip, self.port))
            finally:
                s.close()
        except Exception as e:
            logger.error(f"Failed to send color to ball {self.ip}: {e}")

    def set_ip(self, ip):
        self.ip = ip
