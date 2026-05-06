#!/usr/bin/env python3
"""Synthesise a tiny pcap with hand-rolled LTX packets and verify decode_pcap.py
prints what we expect.  Run it before trusting the decoder on real captures.
"""

from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
DECODER = HERE / "decode_pcap.py"


def eth(src_mac: bytes, dst_mac: bytes, ethertype: int, payload: bytes) -> bytes:
    return dst_mac + src_mac + struct.pack(">H", ethertype) + payload


def ipv4(src: str, dst: str, proto: int, payload: bytes) -> bytes:
    sa = bytes(int(x) for x in src.split("."))
    da = bytes(int(x) for x in dst.split("."))
    total_len = 20 + len(payload)
    hdr = struct.pack(
        ">BBHHHBBH4s4s",
        0x45,        # version=4 ihl=5
        0x00,        # tos
        total_len,
        0x0001,      # id
        0x0000,      # flags+frag
        64,          # ttl
        proto,
        0x0000,      # checksum (we don't bother)
        sa,
        da,
    )
    return hdr + payload


def udp(sport: int, dport: int, payload: bytes) -> bytes:
    length = 8 + len(payload)
    return struct.pack(">HHHH", sport, dport, length, 0) + payload


def write_pcap(path: Path, packets: list[tuple[float, bytes]]) -> None:
    with path.open("wb") as f:
        # global header — link-type 1 (Ethernet), microsecond timestamps
        f.write(struct.pack("<IHHiIII",
                            0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
        for ts, frame in packets:
            ts_sec = int(ts)
            ts_usec = int((ts - ts_sec) * 1e6)
            f.write(struct.pack("<IIII", ts_sec, ts_usec,
                                len(frame), len(frame)))
            f.write(frame)


def main() -> int:
    # Synthesise:
    #  - one ball status broadcast
    #  - one PLAY command from app → broadcast
    #  - one ball status broadcast showing play_status=0x01
    #  - one STOP command from app → broadcast
    #  - one ball status broadcast showing play_status=0x00
    BALL_MAC = bytes.fromhex("a4cf12b92225")
    APP_MAC  = bytes.fromhex("0a2a306af5ef")
    BCAST_MAC = b"\xff\xff\xff\xff\xff\xff"

    # ---- status broadcast: 47-byte beacon ----
    status_data_idle = bytes([
        0x01, 0xb9, 0x22, 0x25,       # MAC-derived ID
        0x00, 0x00, 0x00, 0x00, 0x00, # zeros
        0xfc,                         # data[9]
        0x00,                         # data[10] (CB2 source)
        0x00,                         # data[11]
        0x00,                         # data[12] (play status: idle)
        0x12, 0x34, 0xab, 0xcd,       # 4-byte TS (TS3=0xab, TS4=0xcd)
    ]) + b"NPLAYLTXBALL\x00F" + b"\x00" * 14 + b"z"
    assert len(status_data_idle) <= 80
    pkt_status_idle = eth(BALL_MAC, BCAST_MAC, 0x0800,
                           ipv4("10.42.0.80", "10.42.0.255", 17,
                                udp(41412, 41412, status_data_idle)))

    # ---- PLAY command app → broadcast ----
    play_cmd = bytes([0x61, 0x14, 0x01, 0x00, 0x00,
                      0x99, 0x6f,        # P1, P2
                      0xab, 0xcd])       # echoed TS3, TS4
    pkt_play = eth(APP_MAC, BCAST_MAC, 0x0800,
                   ipv4("10.42.0.144", "255.255.255.255", 17,
                        udp(54321, 41412, play_cmd)))

    # ---- status broadcast showing playing ----
    status_data_playing = bytearray(status_data_idle)
    status_data_playing[12] = 0x01   # data[12] now = playing
    status_data_playing[10] = 0x01   # data[10] mirrors
    status_data_playing[15] = 0xab
    status_data_playing[16] = 0xd0
    pkt_status_play = eth(BALL_MAC, BCAST_MAC, 0x0800,
                          ipv4("10.42.0.80", "10.42.0.255", 17,
                               udp(41412, 41412, bytes(status_data_playing))))

    # ---- STOP command app → broadcast ----
    stop_cmd = bytes([0x61, 0x1e, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    pkt_stop = eth(APP_MAC, BCAST_MAC, 0x0800,
                   ipv4("10.42.0.144", "255.255.255.255", 17,
                        udp(54321, 41412, stop_cmd)))

    # ---- status idle again ----
    status_data_idle2 = bytearray(status_data_idle)
    status_data_idle2[15] = 0xab
    status_data_idle2[16] = 0xff
    pkt_status_idle2 = eth(BALL_MAC, BCAST_MAC, 0x0800,
                           ipv4("10.42.0.80", "10.42.0.255", 17,
                                udp(41412, 41412, bytes(status_data_idle2))))

    packets = [
        (1700000000.000, pkt_status_idle),
        (1700000000.500, pkt_play),
        (1700000000.520, pkt_status_play),
        (1700000003.000, pkt_stop),
        (1700000003.020, pkt_status_idle2),
    ]

    with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tf:
        tmp_path = Path(tf.name)
    write_pcap(tmp_path, packets)

    print(f"[test] wrote synthetic pcap to {tmp_path}")
    print()
    result = subprocess.run(
        [sys.executable, str(DECODER), str(tmp_path)],
        capture_output=True, text=True, check=False,
    )
    print(result.stdout)
    if result.returncode != 0:
        print("STDERR:", result.stderr, file=sys.stderr)
        return result.returncode

    # Sanity assertions on the output text
    expected_substrings = [
        "CMD  op=0x14",          # play
        "CMD  op=0x1e",          # stop
        "STAT play=0x00",        # idle
        "STAT play=0x01",        # playing
        "ctx: status",           # context annotation present
    ]
    missing = [s for s in expected_substrings if s not in result.stdout]
    if missing:
        print(f"[test] FAIL — missing substrings in decoder output: {missing}",
              file=sys.stderr)
        return 1
    print("[test] PASS — decoder produces expected substrings.")
    tmp_path.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
