#!/usr/bin/env python3
"""
decode_pcap.py — Decode LTX juggling-ball traffic from a pcap file.

Pure stdlib (no scapy, no pyshark).  Reads pcap or pcap-ng-with-link-type-104,
reassembles TCP upload streams to port 8888, decodes UDP frames on port 41412,
and emits an annotated timeline plus a JSON sidecar.

Usage:
    python3 decode_pcap.py <file.pcap>          # text timeline to stdout
    python3 decode_pcap.py <file.pcap> --json   # also write <file>.events.json

The decoder knows about the LTX protocol primitives we have already nailed
down (see docs/official_prg_app_tests.md and
sequence_uploading_and_triggering/sequence_uploading_triggering_README.md).
For uncertain bytes (CB2, P1, P2) it just shows their values clearly so we
can spot patterns by eye and via the JSON.

This file is intentionally over-commented because it doubles as documentation.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


# --------------------------------------------------------------------------
# pcap file format (link-type Ethernet, the common case for tcpdump on Wi-Fi)
# --------------------------------------------------------------------------
# Global header (24 bytes):
#   uint32 magic_number      0xa1b2c3d4 (us-resolution, big or little)
#                            0xa1b23c4d (ns-resolution)
#   uint16 version_major
#   uint16 version_minor
#   int32  thiszone          (always 0)
#   uint32 sigfigs           (always 0)
#   uint32 snaplen
#   uint32 network           (link-layer type, e.g. 1=Ethernet, 113=Linux SLL)
#
# Per packet (16 bytes, then snap_bytes):
#   uint32 ts_sec
#   uint32 ts_usec  (or ts_nsec if ns-magic)
#   uint32 incl_len   (bytes captured)
#   uint32 orig_len   (bytes on wire)
#   <incl_len bytes of link-layer frame>


PCAP_MAGIC_LE_US = 0xA1B2C3D4
PCAP_MAGIC_LE_NS = 0xA1B23C4D
PCAP_MAGIC_BE_US = 0xD4C3B2A1
PCAP_MAGIC_BE_NS = 0x4D3CB2A1


def open_pcap(path: Path):
    """Yield (ts_seconds_float, link_type, frame_bytes) for every packet."""
    f = path.open("rb")
    raw_magic = f.read(4)
    if len(raw_magic) < 4:
        raise ValueError("pcap: file too small")
    magic = struct.unpack("<I", raw_magic)[0]
    if magic in (PCAP_MAGIC_LE_US, PCAP_MAGIC_LE_NS):
        endian = "<"
        ns = magic == PCAP_MAGIC_LE_NS
    elif magic in (PCAP_MAGIC_BE_US, PCAP_MAGIC_BE_NS):
        endian = ">"
        ns = magic == PCAP_MAGIC_BE_NS
    else:
        raise ValueError(f"unknown pcap magic 0x{magic:08x} "
                         f"(this script does not handle pcap-ng)")
    rest = f.read(20)
    (_v_maj, _v_min, _zone, _sigfigs, _snaplen, network) = struct.unpack(
        endian + "HHiIII", rest
    )
    while True:
        hdr = f.read(16)
        if not hdr:
            break
        if len(hdr) < 16:
            break
        ts_sec, ts_subsec, incl_len, _orig_len = struct.unpack(
            endian + "IIII", hdr
        )
        ts = ts_sec + (ts_subsec / 1e9 if ns else ts_subsec / 1e6)
        data = f.read(incl_len)
        if len(data) < incl_len:
            break
        yield ts, network, data
    f.close()


# --------------------------------------------------------------------------
# Link / IP / UDP / TCP parsing — just enough to extract payload + addrs
# --------------------------------------------------------------------------

LINKTYPE_ETHERNET = 1
LINKTYPE_LINUX_SLL = 113
LINKTYPE_LINUX_SLL2 = 276


def strip_link_header(link_type: int, frame: bytes) -> tuple[bytes, int]:
    """Return (ip_packet, ethertype) skipping the link layer."""
    if link_type == LINKTYPE_ETHERNET:
        if len(frame) < 14:
            return b"", 0
        ethertype = struct.unpack(">H", frame[12:14])[0]
        # Handle 802.1Q VLAN tag
        if ethertype == 0x8100 and len(frame) >= 18:
            ethertype = struct.unpack(">H", frame[16:18])[0]
            return frame[18:], ethertype
        return frame[14:], ethertype
    if link_type == LINKTYPE_LINUX_SLL:
        # 16-byte cooked header
        if len(frame) < 16:
            return b"", 0
        ethertype = struct.unpack(">H", frame[14:16])[0]
        return frame[16:], ethertype
    if link_type == LINKTYPE_LINUX_SLL2:
        # 20-byte cooked v2 header
        if len(frame) < 20:
            return b"", 0
        ethertype = struct.unpack(">H", frame[0:2])[0]
        return frame[20:], ethertype
    return b"", 0


def parse_ipv4(packet: bytes) -> dict | None:
    if len(packet) < 20:
        return None
    ver_ihl = packet[0]
    version = ver_ihl >> 4
    if version != 4:
        return None
    ihl = (ver_ihl & 0x0F) * 4
    if len(packet) < ihl:
        return None
    proto = packet[9]
    src = ".".join(str(b) for b in packet[12:16])
    dst = ".".join(str(b) for b in packet[16:20])
    return {
        "src": src,
        "dst": dst,
        "proto": proto,
        "payload": packet[ihl:],
    }


def parse_udp(payload: bytes) -> dict | None:
    if len(payload) < 8:
        return None
    sport, dport, _length, _csum = struct.unpack(">HHHH", payload[:8])
    return {"sport": sport, "dport": dport, "data": payload[8:]}


def parse_tcp(payload: bytes) -> dict | None:
    if len(payload) < 20:
        return None
    sport, dport, seq, ack, off_flags = struct.unpack(">HHIIH", payload[:14])
    data_off = (off_flags >> 12) * 4
    flags = off_flags & 0x01FF
    if len(payload) < data_off:
        return None
    return {
        "sport": sport,
        "dport": dport,
        "seq": seq,
        "ack": ack,
        "flags": flags,
        "data": payload[data_off:],
    }


# --------------------------------------------------------------------------
# LTX protocol decoders
# --------------------------------------------------------------------------

UDP_LTX_PORT = 41412
TCP_UPLOAD_PORT = 8888

CMD_GROUP_BYTE = 0x61


def decode_command_frame(data: bytes) -> dict | None:
    """Decode a 9-byte 0x61 command (Play / Stop / ...).  Returns None if
    it doesn't look like one."""
    if len(data) != 9 or data[0] != CMD_GROUP_BYTE:
        return None
    op_id = data[1]
    cb2 = data[2]
    pad = data[3:5]
    p1 = data[5]
    p2 = data[6]
    ts3 = data[7]
    ts4 = data[8]
    # Heuristic classification (pure naming aid; the wire bytes are the truth):
    #   OpID is a multiple of 0x14  -> looks like a Play
    #   OpID is (Play_OpID + 0x0A)  -> looks like a Stop
    #   suffix all zeros            -> Stop suffix style
    suffix_all_zero = data[5:] == b"\x00\x00\x00\x00"
    if suffix_all_zero:
        kind_guess = "STOP-style (zero suffix)"
    elif op_id % 0x14 == 0:
        kind_guess = "PLAY-style (OpID multiple of 0x14)"
    elif (op_id - 0x0A) % 0x14 == 0:
        kind_guess = "STOP-style (OpID = Play+0x0A)"
    else:
        kind_guess = "UNKNOWN command"
    return {
        "type": "command",
        "kind_guess": kind_guess,
        "op_id": op_id,
        "cb2": cb2,
        "pad": pad.hex(),
        "p1": p1,
        "p2": p2,
        "ts3": ts3,
        "ts4": ts4,
    }


def decode_status_broadcast(data: bytes) -> dict | None:
    """Decode a ball UDP status broadcast.  Many lengths exist (47, 62, 71…)
    but the structure of bytes 0..16 is consistent enough to extract."""
    if len(data) < 17:
        return None
    # Bytes 0..3 — usually 01 + last 3 bytes of MAC
    mac_id = data[0:4].hex()
    # Bytes 9..12 — internal state-machine bytes we care about
    state9 = data[9]
    cb2_src = data[10]   # the value the official app *might* copy into command CB2
    state11 = data[11]
    play_status = data[12]   # 0x00 idle, 0x01 playing
    # Bytes 13..16 — 4-byte timestamp/counter; bytes 15-16 are echoed by PLAY
    ts_b1, ts_b2, ts_b3, ts_b4 = data[13], data[14], data[15], data[16]
    # ASCII tail — find printable runs >=4 chars
    ascii_runs: list[str] = []
    cur = bytearray()
    for b in data[17:]:
        if 32 <= b < 127:
            cur.append(b)
        else:
            if len(cur) >= 4:
                ascii_runs.append(cur.decode("ascii", "replace"))
            cur = bytearray()
    if len(cur) >= 4:
        ascii_runs.append(cur.decode("ascii", "replace"))
    return {
        "type": "status",
        "len": len(data),
        "mac_id": mac_id,
        "state9": state9,
        "cb2_src_data10": cb2_src,
        "state11": state11,
        "play_status_data12": play_status,
        "ts_full": (ts_b1, ts_b2, ts_b3, ts_b4),
        "ts_b3_b4": (ts_b3, ts_b4),
        "ascii": ascii_runs,
    }


def decode_udp_ltx(data: bytes) -> dict | None:
    """Try every known LTX UDP shape; return the first that fits."""
    if not data:
        return None
    if (cmd := decode_command_frame(data)) is not None:
        return cmd
    if (status := decode_status_broadcast(data)) is not None:
        return status
    return {"type": "udp_unknown", "len": len(data), "hex": data.hex()}


# --------------------------------------------------------------------------
# TCP upload reassembly
# --------------------------------------------------------------------------

@dataclass
class TcpStream:
    key: tuple[str, int, str, int]   # (src_ip, src_port, dst_ip, dst_port)
    chunks: dict[int, bytes] = field(default_factory=dict)   # seq -> payload
    first_seq: int | None = None
    first_ts: float | None = None
    last_ts: float | None = None
    fin_seen: bool = False

    def add(self, ts: float, seq: int, payload: bytes) -> None:
        if not payload:
            return
        if self.first_seq is None:
            self.first_seq = seq
            self.first_ts = ts
        self.chunks[seq] = payload
        self.last_ts = ts

    def assemble(self) -> bytes:
        """Reassemble in seq order from first_seq, dropping retransmits."""
        if self.first_seq is None:
            return b""
        out = bytearray()
        cur = self.first_seq
        while cur in self.chunks:
            payload = self.chunks[cur]
            out += payload
            cur = (cur + len(payload)) & 0xFFFFFFFF
        return bytes(out)


def decode_upload_payload(payload: bytes) -> dict:
    """Decode the TCP upload payload.

    Corrected format (verified 2026-05-06 against capture E2):

        [ 0: 4]   four fixed NUL bytes
        [ 4: 8]   uint32 LE file size on disk (= len of PRG body)
        [ 8:12]   4-byte client-chosen nonce
        [12:15]   3 bytes whose first byte appears to be related to
                  filename length; bytes 13,14 are NUL.  Previously
                  documented as ASCII space (0x20) + 2 NULs but observed
                  as 0x30 + 2 NULs for a 32-char filename.  Hypothesis:
                  byte 12 = 16 + filename_length (= offset where PRG starts).
        [15:16]   one NUL separator
        [16: ?]   filename, ASCII, NOT NUL-terminated
        [?: end]  raw PRG file content (length matches the size at offset 4)

    The PRG file's own magic header is "PR\x03IN\x05", which is what
    confused earlier reverse-engineering attempts: they saw the "PR" as
    a marker following the filename rather than as the start of the PRG
    body.  Filenames just end where the PRG body begins.
    """
    info: dict[str, Any] = {"raw_len": len(payload)}
    if len(payload) < 17:
        info["error"] = "payload too short for upload header"
        return info
    prefix = payload[:15]
    info["prefix_hex"] = prefix.hex()
    info["prefix_fixed_start"] = prefix[0:4].hex()
    file_size_decl = struct.unpack("<I", prefix[4:8])[0]
    info["prefix_file_size_decl"] = file_size_decl
    info["prefix_nonce"] = prefix[8:12].hex()
    info["prefix_byte12"] = prefix[12]   # variable, see docstring
    info["prefix_byte13"] = prefix[13]
    info["prefix_byte14"] = prefix[14]
    if payload[15] != 0:
        info["error"] = "byte 15 expected NUL separator, got 0x%02x" % payload[15]
        return info
    # PRG file size is given in the prefix; everything before the last
    # `file_size_decl` bytes (and after byte 16) is the filename.
    if file_size_decl > 0 and len(payload) >= 16 + file_size_decl:
        prg_start = len(payload) - file_size_decl
        info["filename"] = payload[16:prg_start].decode("ascii", "replace")
        info["prg_offset"] = prg_start
        info["prg_bytes_observed"] = file_size_decl
        info["prg_magic_first_8_bytes_hex"] = payload[prg_start:prg_start+8].hex()
        info["prg_first_64_bytes_hex"] = payload[prg_start:prg_start+64].hex()
        # Sanity check: byte 12 hypothesis
        info["filename_length"] = len(info["filename"])
        info["byte12_minus_16"] = prefix[12] - 16
        info["matches_filename_len_hypothesis"] = (
            prefix[12] == 16 + len(info["filename"])
        )
    else:
        info["error"] = (
            f"size mismatch: payload={len(payload)} but "
            f"declared file size={file_size_decl}"
        )
    return info


# --------------------------------------------------------------------------
# Top-level event-stream decoder
# --------------------------------------------------------------------------

@dataclass
class Event:
    ts: float
    kind: str   # "udp_cmd", "udp_status", "udp_other", "tcp_upload"
    summary: str
    detail: dict[str, Any]


def decode_pcap(path: Path) -> list[Event]:
    events: list[Event] = []
    tcp_streams: dict[tuple, TcpStream] = {}
    finished_streams: list[TcpStream] = []

    # When tcpdump runs on an AP / hotspot interface, broadcast and multicast
    # frames may be observed twice (once "rx-from-air" and once "tx-to-air"
    # via the bridge).  Deduplicate by (src,sport,dst,dport,payload-bytes)
    # within a small time window.  Real consecutive packets with identical
    # bytes within 5ms are extremely rare and would only collapse what is
    # functionally a retransmit.
    seen: dict[tuple, float] = {}
    DEDUP_WINDOW_S = 0.005

    for ts, link_type, frame in open_pcap(path):
        ip_packet, ethertype = strip_link_header(link_type, frame)
        if ethertype != 0x0800:    # not IPv4
            continue
        ip = parse_ipv4(ip_packet)
        if ip is None:
            continue

        # Per-flow dedup key: protocol-aware
        if ip["proto"] == 17:
            udp_hdr = parse_udp(ip["payload"])
            if udp_hdr is not None:
                dedup_key = (
                    "udp",
                    ip["src"], udp_hdr["sport"],
                    ip["dst"], udp_hdr["dport"],
                    udp_hdr["data"],
                )
                prev = seen.get(dedup_key)
                if prev is not None and (ts - prev) < DEDUP_WINDOW_S:
                    continue
                seen[dedup_key] = ts
        elif ip["proto"] == 6:
            tcp_hdr = parse_tcp(ip["payload"])
            if tcp_hdr is not None:
                dedup_key = (
                    "tcp",
                    ip["src"], tcp_hdr["sport"],
                    ip["dst"], tcp_hdr["dport"],
                    tcp_hdr["seq"],
                    tcp_hdr["flags"],
                    tcp_hdr["data"],
                )
                prev = seen.get(dedup_key)
                if prev is not None and (ts - prev) < DEDUP_WINDOW_S:
                    continue
                seen[dedup_key] = ts

        # ---- UDP path ----
        if ip["proto"] == 17:
            udp = parse_udp(ip["payload"])
            if udp is None:
                continue
            if UDP_LTX_PORT not in (udp["sport"], udp["dport"]):
                continue
            decoded = decode_udp_ltx(udp["data"])
            direction = ""
            if udp["dport"] == UDP_LTX_PORT and udp["sport"] != UDP_LTX_PORT:
                direction = "APP→BALL"
            elif udp["sport"] == UDP_LTX_PORT and udp["dport"] != UDP_LTX_PORT:
                direction = "BALL→APP"
            else:
                direction = "BCAST   "
            base = (
                f"{direction} {ip['src']}:{udp['sport']} → "
                f"{ip['dst']}:{udp['dport']}  len={len(udp['data'])}"
            )
            if decoded and decoded.get("type") == "command":
                summary = (
                    f"{base}  CMD  op={decoded['op_id']:#04x}  "
                    f"cb2={decoded['cb2']:#04x}  "
                    f"P1P2={decoded['p1']:02x}{decoded['p2']:02x}  "
                    f"TS={decoded['ts3']:02x}{decoded['ts4']:02x}  "
                    f"[{decoded['kind_guess']}]"
                )
                kind = "udp_cmd"
            elif decoded and decoded.get("type") == "status":
                ascii_tail = " ".join(
                    s for s in decoded["ascii"] if s.strip()
                )[:60]
                summary = (
                    f"{base}  STAT play={decoded['play_status_data12']:#04x} "
                    f"d10={decoded['cb2_src_data10']:#04x} "
                    f"d9={decoded['state9']:#04x} d11={decoded['state11']:#04x} "
                    f"TS3,4={decoded['ts_b3_b4'][0]:02x}{decoded['ts_b3_b4'][1]:02x}"
                    f"  «{ascii_tail}»"
                )
                kind = "udp_status"
            else:
                summary = f"{base}  ???  hex={udp['data'].hex()}"
                kind = "udp_other"
            events.append(Event(
                ts=ts,
                kind=kind,
                summary=summary,
                detail={
                    "src": ip["src"],
                    "sport": udp["sport"],
                    "dst": ip["dst"],
                    "dport": udp["dport"],
                    "raw_hex": udp["data"].hex(),
                    **(decoded or {}),
                },
            ))

        # ---- TCP path ----
        elif ip["proto"] == 6:
            tcp = parse_tcp(ip["payload"])
            if tcp is None:
                continue
            if TCP_UPLOAD_PORT not in (tcp["sport"], tcp["dport"]):
                continue
            key = (ip["src"], tcp["sport"], ip["dst"], tcp["dport"])
            stream = tcp_streams.setdefault(key, TcpStream(key=key))
            if tcp["data"]:
                stream.add(ts, tcp["seq"], tcp["data"])
            FIN = 0x01
            if tcp["flags"] & FIN:
                stream.fin_seen = True
                # Only consider this an upload stream if some data was sent
                # *to* port 8888 (i.e. dst_port == 8888 and we collected data).
                if tcp["dport"] == TCP_UPLOAD_PORT or tcp["sport"] == TCP_UPLOAD_PORT:
                    finished_streams.append(stream)
                tcp_streams.pop(key, None)

    # Emit any incomplete streams (capture cut short)
    for stream in tcp_streams.values():
        finished_streams.append(stream)

    for stream in finished_streams:
        # Only the app→ball direction is interesting for upload (dst port 8888)
        src_ip, sport, dst_ip, dport = stream.key
        if dport != TCP_UPLOAD_PORT:
            continue
        payload = stream.assemble()
        if not payload:
            continue
        info = decode_upload_payload(payload)
        summary = (
            f"APP→BALL {src_ip}:{sport} → {dst_ip}:{dport}  "
            f"TCP UPLOAD  total={info['raw_len']} B  "
            f"declared_size={info.get('prefix_file_size_decl')}  "
            f"file='{info.get('filename')}'  "
            f"prg_obs={info.get('prg_bytes_observed')}"
        )
        events.append(Event(
            ts=stream.first_ts or 0.0,
            kind="tcp_upload",
            summary=summary,
            detail={
                "src": src_ip, "sport": sport,
                "dst": dst_ip, "dport": dport,
                "ts_first": stream.first_ts,
                "ts_last": stream.last_ts,
                **info,
            },
        ))

    events.sort(key=lambda e: e.ts)
    return events


# --------------------------------------------------------------------------
# Cross-event analysis: pair commands with neighbouring status broadcasts
# --------------------------------------------------------------------------

def annotate_with_context(events: list[Event]) -> None:
    """For each command event, find the most-recent ball status broadcast
    immediately preceding it and the first one after.  Useful for spotting
    the relationship between command CB2 and broadcast d10."""
    last_status_per_ball: dict[str, Event] = {}
    pending_cmds: list[Event] = []
    for ev in events:
        if ev.kind == "udp_status":
            ball = ev.detail.get("src", "?")
            last_status_per_ball[ball] = ev
            # Resolve any pending commands targeting this ball
            for cmd in pending_cmds:
                if cmd.detail.get("dst") in (ball, "255.255.255.255",
                                             "10.42.0.255"):
                    cmd.detail["status_after"] = {
                        "ts_delta_ms": (ev.ts - cmd.ts) * 1000.0,
                        "play_status": ev.detail.get("play_status_data12"),
                        "d10": ev.detail.get("cb2_src_data10"),
                        "ts3_4": ev.detail.get("ts_b3_b4"),
                    }
            pending_cmds = [c for c in pending_cmds
                            if "status_after" not in c.detail]
        elif ev.kind == "udp_cmd":
            # Attach the most recent status broadcast (any ball)
            if last_status_per_ball:
                # Pick the one with most-recent ts
                latest = max(last_status_per_ball.values(), key=lambda e: e.ts)
                ev.detail["status_before"] = {
                    "ts_delta_ms": (ev.ts - latest.ts) * 1000.0,
                    "from_ball": latest.detail.get("src"),
                    "play_status": latest.detail.get("play_status_data12"),
                    "d10": latest.detail.get("cb2_src_data10"),
                    "ts3_4": latest.detail.get("ts_b3_b4"),
                }
            pending_cmds.append(ev)


# --------------------------------------------------------------------------
# Output formatting
# --------------------------------------------------------------------------

def print_timeline(events: list[Event]) -> None:
    if not events:
        print("(no LTX events found in capture)")
        return
    t0 = events[0].ts
    counts: dict[str, int] = defaultdict(int)
    for ev in events:
        counts[ev.kind] += 1
        rel = ev.ts - t0
        print(f"  t+{rel:8.3f}s  {ev.summary}")
        if ev.kind == "udp_cmd":
            sb = ev.detail.get("status_before")
            sa = ev.detail.get("status_after")
            if sb:
                print(
                    f"               ↑ ctx: status {sb['ts_delta_ms']:+.1f}ms "
                    f"earlier from {sb['from_ball']} "
                    f"play={sb['play_status']:#04x} d10={sb['d10']:#04x} "
                    f"TS={sb['ts3_4'][0]:02x}{sb['ts3_4'][1]:02x}"
                )
            if sa:
                print(
                    f"               ↓ next status {sa['ts_delta_ms']:+.1f}ms "
                    f"play={sa['play_status']:#04x} d10={sa['d10']:#04x} "
                    f"TS={sa['ts3_4'][0]:02x}{sa['ts3_4'][1]:02x}"
                )
    print()
    print("Summary:")
    for k, v in sorted(counts.items()):
        print(f"  {k:12s} {v}")


def write_json_sidecar(events: list[Event], path: Path) -> None:
    out = [
        {
            "ts": ev.ts,
            "kind": ev.kind,
            "summary": ev.summary,
            "detail": ev.detail,
        }
        for ev in events
    ]
    path.write_text(json.dumps(out, indent=2, default=str))
    print(f"[wrote] {path}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Decode LTX juggling-ball pcap")
    ap.add_argument("pcap", type=Path)
    ap.add_argument("--json", action="store_true",
                    help="also write <pcap>.events.json")
    args = ap.parse_args()

    if not args.pcap.exists():
        print(f"error: {args.pcap} not found", file=sys.stderr)
        return 2

    events = decode_pcap(args.pcap)
    annotate_with_context(events)
    print_timeline(events)
    if args.json:
        sidecar = args.pcap.with_suffix(args.pcap.suffix + ".events.json")
        write_json_sidecar(events, sidecar)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
