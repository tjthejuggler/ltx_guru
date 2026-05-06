"""
LTX Ball Network Client
=======================

Pure-protocol library for talking to LTX juggling balls over the WiFi
hotspot they create / join. Implements three operations:

1.  upload_prg(ball_ip, prg_path, filename_on_ball) -- TCP/8888 upload of a
    .prg sequence file. Format reversed from the official Android app
    (`com.lightrix.ltxremote`) on 2026-05-06.
2.  send_play(ball_ip)                              -- UDP/41412 PLAY frame.
3.  send_stop(ball_ip)                              -- UDP/41412 STOP frame.

Protocol summary (discovered 2026-05-06 by passive WiFi capture of the
official app driving real balls — see
``reverse_engineering/capture/captures/`` for raw pcaps):

UPLOAD (TCP, port 8888)
    bytes [0..3]   = 00 00 00 00       (4 NUL bytes)
    bytes [4..7]   = uint32 LE         file size in bytes (PRG body length)
    bytes [8..11]  = 4 random bytes    nonce (purpose unclear, ball ignores)
    byte  [12]     = 16 + filename_len (header length up to & inc. NUL)
    bytes [13..14] = 00 00             (2 NUL bytes)
    byte  [15]     = 00                (NUL separator)
    bytes [16..]   = filename ASCII    (NO trailing NUL; PRG body follows immediately)
    bytes [16+L..] = raw PRG body      (exactly file_size bytes)

    Total stream length = 16 + filename_len + file_size

PLAY/STOP (UDP, dst port 41412, src port should be 41413)
    9 bytes:
        42 00 00 00 00  <SEQ>  00 00  <ACTION>
    where SEQ is a 1-byte monotonically incrementing counter (mod 256)
    and ACTION is 0x01=PLAY, 0x02=STOP.

The seq counter is NOT a security primitive -- it is just a logical
ordering marker. The ball echoes the latest accepted seq back into byte
data[9] of its 94-byte status broadcast, and signals play state via
data[11] (0x01 playing / 0x00 stopped).

This module is self-contained — it depends on nothing other than the
Python standard library — so it can be reused by tools, scripts and the
sequence_maker GUI alike.
"""

from __future__ import annotations

import logging
import os
import secrets
import socket
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("SequenceMaker.LTXBallClient")

# Network constants
BALL_TCP_UPLOAD_PORT = 8888
BALL_UDP_CONTROL_PORT = 41412
APP_UDP_SOURCE_PORT = 41413  # Official app sends from this src port

# Protocol constants
PLAY_ACTION = 0x01
STOP_ACTION = 0x02
COMMAND_OPCODE = 0x42

# Byte 12 of upload prefix = 16 + filename_length
PREFIX_BASE_LEN = 16


# --------------------------------------------------------------------------- #
# Upload                                                                      #
# --------------------------------------------------------------------------- #


def build_upload_payload(prg_bytes: bytes, filename: str, nonce: Optional[bytes] = None) -> bytes:
    """Construct the full byte stream for a PRG upload.

    Args:
        prg_bytes:  Raw contents of the .prg file.
        filename:   Filename to store on the ball (ASCII; e.g. "Ball_1.prg").
        nonce:      Optional 4-byte nonce. Random if None.

    Returns:
        Bytes ready to write to the TCP socket.
    """
    if not prg_bytes:
        raise ValueError("prg_bytes is empty")
    if not filename:
        raise ValueError("filename is empty")
    try:
        filename_bytes = filename.encode("ascii")
    except UnicodeEncodeError as e:
        raise ValueError(f"filename must be ASCII: {filename!r}") from e
    if len(filename_bytes) > 255 - PREFIX_BASE_LEN:
        raise ValueError(f"filename too long ({len(filename_bytes)} bytes)")

    file_size = len(prg_bytes)
    if nonce is None:
        nonce = secrets.token_bytes(4)
    elif len(nonce) != 4:
        raise ValueError("nonce must be 4 bytes")

    byte12 = PREFIX_BASE_LEN + len(filename_bytes)

    # 16-byte fixed-shape prefix
    prefix = (
        b"\x00\x00\x00\x00"                       # [0..3]
        + file_size.to_bytes(4, "little")        # [4..7]
        + nonce                                   # [8..11]
        + bytes([byte12])                         # [12]
        + b"\x00\x00"                            # [13..14]
        + b"\x00"                                # [15]  separator
    )
    assert len(prefix) == PREFIX_BASE_LEN, len(prefix)

    return prefix + filename_bytes + prg_bytes


def upload_prg(
    ball_ip: str,
    prg_path: str,
    filename_on_ball: Optional[str] = None,
    timeout: float = 15.0,
) -> bool:
    """Upload a .prg file to a ball via TCP/8888.

    Args:
        ball_ip:           IPv4 address of the ball.
        prg_path:          Local filesystem path to the .prg file.
        filename_on_ball:  ASCII name to store on the ball.
                           Defaults to ``os.path.basename(prg_path)``.
        timeout:           TCP connect/send timeout in seconds.

    Returns:
        True on send completion (does not yet verify ball ack via broadcast).
    """
    if not os.path.isfile(prg_path):
        logger.error(f"upload_prg: file not found: {prg_path}")
        return False

    with open(prg_path, "rb") as f:
        prg_bytes = f.read()

    if filename_on_ball is None:
        filename_on_ball = os.path.basename(prg_path)

    payload = build_upload_payload(prg_bytes, filename_on_ball)
    logger.info(
        f"upload_prg: ip={ball_ip} file={prg_path} size={len(prg_bytes)} "
        f"name='{filename_on_ball}' total_payload={len(payload)}"
    )

    sock: Optional[socket.socket] = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ball_ip, BALL_TCP_UPLOAD_PORT))
        sock.sendall(payload)
        # Half-close so the ball knows we're done sending.
        try:
            sock.shutdown(socket.SHUT_WR)
        except OSError:
            pass
        # Some firmwares send a tiny ack-shaped reply over TCP; read+discard.
        try:
            sock.settimeout(2.0)
            _ = sock.recv(64)
        except (socket.timeout, OSError):
            pass
        return True
    except Exception as e:
        logger.error(f"upload_prg: failed to upload to {ball_ip}: {e}")
        return False
    finally:
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass


# --------------------------------------------------------------------------- #
# Play / Stop                                                                 #
# --------------------------------------------------------------------------- #


def build_command_frame(seq: int, action: int) -> bytes:
    """Build the 9-byte UDP command frame.

    Args:
        seq:    Sequence counter (any int; only low byte is used).
        action: 0x01 PLAY, 0x02 STOP.
    """
    return bytes([
        COMMAND_OPCODE,  # 0x42
        0x00, 0x00, 0x00, 0x00,
        seq & 0xFF,
        0x00, 0x00,
        action & 0xFF,
    ])


@dataclass
class CommandSocket:
    """Wraps a UDP socket bound to APP_UDP_SOURCE_PORT for sending commands.

    The official app appears to bind src=41413; we mimic that. If the port is
    busy we fall back to an ephemeral source port (still works, but mimicry
    is preferred).
    """

    bind_source_port: bool = True
    _sock: Optional[socket.socket] = None

    def _ensure(self) -> socket.socket:
        if self._sock is not None:
            return self._sock
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.bind_source_port:
            try:
                s.bind(("0.0.0.0", APP_UDP_SOURCE_PORT))
            except OSError as e:
                logger.warning(
                    f"CommandSocket: could not bind src=:{APP_UDP_SOURCE_PORT}, "
                    f"falling back to ephemeral: {e}"
                )
        self._sock = s
        return s

    def send(self, ball_ip: str, frame: bytes) -> bool:
        try:
            s = self._ensure()
            s.sendto(frame, (ball_ip, BALL_UDP_CONTROL_PORT))
            return True
        except Exception as e:
            logger.error(f"CommandSocket.send: {e}")
            return False

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None


class LTXController:
    """Stateful controller for one or many balls.

    Maintains a single monotonic seq counter (the official app appears to
    use one counter shared across all balls when sending broadcast-style
    fan-out; we send unicast and reuse the same counter for simplicity).
    """

    def __init__(self) -> None:
        self._seq = 0
        self._sock = CommandSocket()

    def _next_seq(self) -> int:
        self._seq = (self._seq + 1) & 0xFF
        # Avoid seq=0; we don't yet know whether the ball treats 0 as "uninit".
        if self._seq == 0:
            self._seq = 1
        return self._seq

    def play(self, ball_ips: list[str]) -> dict[str, bool]:
        """Send PLAY to one or more balls. Returns ip->ok map."""
        out: dict[str, bool] = {}
        for ip in ball_ips:
            if not ip:
                continue
            seq = self._next_seq()
            frame = build_command_frame(seq, PLAY_ACTION)
            ok = self._sock.send(ip, frame)
            logger.info(f"PLAY  ip={ip} seq={seq} ok={ok}")
            out[ip] = ok
        return out

    def stop(self, ball_ips: list[str]) -> dict[str, bool]:
        """Send STOP to one or more balls. Returns ip->ok map."""
        out: dict[str, bool] = {}
        for ip in ball_ips:
            if not ip:
                continue
            seq = self._next_seq()
            frame = build_command_frame(seq, STOP_ACTION)
            ok = self._sock.send(ip, frame)
            logger.info(f"STOP  ip={ip} seq={seq} ok={ok}")
            out[ip] = ok
        return out

    def close(self) -> None:
        self._sock.close()
