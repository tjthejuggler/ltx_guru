#!/usr/bin/env python3
"""diff_uploads.py — compare two TCP upload pcaps byte-for-byte.

Usage:
    ./diff_uploads.py <reference.pcap> <ours.pcap>

Prints:
    * Per-byte diff of the assembled TCP stream (0..N bytes), with first 64
      bytes always shown in hex.
    * TCP-level differences: number of packets, segment sizes, flags,
      shutdown timing, post-PRG-body bytes, source-port choice.
    * Any UDP traffic that appears in the same window (in case there is
      something the official app sends/receives that we don't).

This is a read-only tool; it does not modify any code.
"""

from __future__ import annotations

import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


# ---------------------------------------------------------------------------
# Tiny pcap reader
# ---------------------------------------------------------------------------

PCAP_MAGIC = b"\xd4\xc3\xb2\xa1"  # microsecond, little-endian


def read_pcap(path: Path) -> Iterable[tuple[float, bytes, int]]:
    with open(path, "rb") as f:
        magic = f.read(4)
        if magic != PCAP_MAGIC:
            raise SystemExit(f"{path}: bad pcap magic {magic.hex()}")
        gh = f.read(20)
        link_type = struct.unpack("<I", gh[16:20])[0]
        while True:
            hdr = f.read(16)
            if len(hdr) < 16:
                break
            ts_sec, ts_usec, incl_len, _orig_len = struct.unpack("<IIII", hdr)
            ts = ts_sec + ts_usec / 1e6
            data = f.read(incl_len)
            yield ts, data, link_type


def parse_eth_ip_tcp_or_udp(frame: bytes, link_type: int) -> dict | None:
    if link_type == 1:           # Ethernet
        ip = frame[14:]
    elif link_type == 113:       # Linux SLL
        ip = frame[16:]
    elif link_type == 101:       # Raw IP
        ip = frame
    else:
        return None
    if len(ip) < 20 or (ip[0] >> 4) != 4:
        return None
    ihl = (ip[0] & 0x0F) * 4
    proto = ip[9]
    src = ".".join(str(b) for b in ip[12:16])
    dst = ".".join(str(b) for b in ip[16:20])
    if proto == 6:
        tcp = ip[ihl:]
        if len(tcp) < 20:
            return None
        sport, dport = struct.unpack("!HH", tcp[0:4])
        seq, ack = struct.unpack("!II", tcp[4:12])
        data_off = (tcp[12] >> 4) * 4
        flags = tcp[13]
        payload = tcp[data_off:]
        return dict(proto="tcp", src=src, dst=dst, sport=sport, dport=dport,
                    seq=seq, ack=ack, flags=flags, payload=payload)
    elif proto == 17:
        udp = ip[ihl:]
        if len(udp) < 8:
            return None
        sport, dport = struct.unpack("!HH", udp[0:4])
        payload = udp[8:]
        return dict(proto="udp", src=src, dst=dst, sport=sport, dport=dport,
                    payload=payload)
    return None


# ---------------------------------------------------------------------------
# TCP stream assembly
# ---------------------------------------------------------------------------

@dataclass
class TcpStream:
    key: tuple[str, int, str, int]
    pkts: list[tuple[float, dict]] = field(default_factory=list)

    def add(self, ts: float, p: dict) -> None:
        self.pkts.append((ts, p))

    def assemble_appside(self) -> bytes:
        """Reassemble the bytes the APP -> BAL direction sent, in seq order."""
        # The "app side" is whichever side has src -> dst matching key forward.
        # We expect 4 packets per direction; do simple seq-ordered reassembly.
        forward = [(ts, p) for ts, p in self.pkts
                   if (p["src"], p["sport"], p["dst"], p["dport"]) == self.key
                   and p["payload"]]
        forward.sort(key=lambda x: x[1]["seq"])
        out = bytearray()
        if not forward: return bytes(out)
        first_seq = forward[0][1]["seq"]
        for _, p in forward:
            offset = (p["seq"] - first_seq) & 0xFFFFFFFF
            if offset > len(out):
                # gap (retransmission ahead?); pad
                out.extend(b"\x00" * (offset - len(out)))
            elif offset < len(out):
                # overlap (retransmission); skip already-have bytes
                start = len(out) - offset
                out.extend(p["payload"][start:])
                continue
            out.extend(p["payload"])
        return bytes(out)


def find_upload_stream(pcap_path: Path) -> tuple[TcpStream, list[tuple[float, dict]]]:
    """Return the upload TcpStream and a list of UDP packets in the same window."""
    streams: dict[tuple, TcpStream] = {}
    udp_pkts: list[tuple[float, dict]] = []
    for ts, frame, lt in read_pcap(pcap_path):
        p = parse_eth_ip_tcp_or_udp(frame, lt)
        if not p:
            continue
        if p["proto"] == "tcp" and (p["sport"] == 8888 or p["dport"] == 8888):
            # Forward key = whichever side has dport==8888
            if p["dport"] == 8888:
                k = (p["src"], p["sport"], p["dst"], p["dport"])
            else:
                k = (p["dst"], p["dport"], p["src"], p["sport"])
            streams.setdefault(k, TcpStream(key=k)).add(ts, p)
        elif p["proto"] == "udp":
            udp_pkts.append((ts, p))

    if not streams:
        raise SystemExit(f"{pcap_path}: no TCP traffic on port 8888")
    # Pick the stream with the most bytes in forward direction.
    best = max(streams.values(),
               key=lambda s: sum(len(p["payload"]) for _, p in s.pkts
                                 if (p["src"], p["sport"], p["dst"], p["dport"]) == s.key))
    # Trim UDP to the upload window
    if best.pkts:
        t0 = min(ts for ts, _ in best.pkts) - 0.5
        t1 = max(ts for ts, _ in best.pkts) + 2.0
        udp_pkts = [(ts, p) for ts, p in udp_pkts if t0 <= ts <= t1]
    return best, udp_pkts


# ---------------------------------------------------------------------------
# Diff & report
# ---------------------------------------------------------------------------

def hexdump(prefix: str, b: bytes, width: int = 16) -> str:
    out = []
    for i in range(0, len(b), width):
        chunk = b[i:i + width]
        hex_part = " ".join(f"{x:02x}" for x in chunk)
        ascii_part = "".join((chr(x) if 32 <= x < 127 else ".") for x in chunk)
        out.append(f"{prefix}{i:04x}  {hex_part:<{width*3}}  {ascii_part}")
    return "\n".join(out)


def report(ref_path: Path, ours_path: Path) -> None:
    ref_stream, ref_udp = find_upload_stream(ref_path)
    our_stream, our_udp = find_upload_stream(ours_path)

    ref_bytes = ref_stream.assemble_appside()
    our_bytes = our_stream.assemble_appside()

    print(f"=== Comparing TCP upload streams ===")
    print(f"  REF file:  {ref_path}")
    print(f"  OUR file:  {ours_path}")
    print()
    print(f"  REF stream (APP->BAL): {len(ref_bytes)} bytes, "
          f"src={ref_stream.key[0]}:{ref_stream.key[1]} -> dst={ref_stream.key[2]}:{ref_stream.key[3]}")
    print(f"  OUR stream (APP->BAL): {len(our_bytes)} bytes, "
          f"src={our_stream.key[0]}:{our_stream.key[1]} -> dst={our_stream.key[2]}:{our_stream.key[3]}")
    print()

    print("--- First 64 bytes (header region) ---")
    print(hexdump("  REF ", ref_bytes[:64]))
    print()
    print(hexdump("  OUR ", our_bytes[:64]))
    print()

    # Byte-level diff
    print("--- Byte-level diff in header (first 64) ---")
    n = min(64, len(ref_bytes), len(our_bytes))
    diffs = [(i, ref_bytes[i], our_bytes[i]) for i in range(n)
             if ref_bytes[i] != our_bytes[i]]
    if not diffs:
        print("  (no differences in first 64 bytes)")
    else:
        for i, r, o in diffs:
            print(f"  byte {i:3d}: REF=0x{r:02x} ({chr(r) if 32<=r<127 else '?'})  "
                  f"OUR=0x{o:02x} ({chr(o) if 32<=o<127 else '?'})")
    print()

    # Length difference
    if len(ref_bytes) != len(our_bytes):
        print(f"!!! TOTAL LENGTH DIFFERS: REF={len(ref_bytes)}  OUR={len(our_bytes)}")
        # Show the TAIL of each (where the discrepancy might be)
        tail_n = 32
        print(f"  REF last {tail_n} bytes:")
        print(hexdump("    ", ref_bytes[-tail_n:]))
        print(f"  OUR last {tail_n} bytes:")
        print(hexdump("    ", our_bytes[-tail_n:]))
    else:
        # Check for full body differences (PRG body is huge, summarize)
        diffs_total = sum(1 for i in range(len(ref_bytes)) if ref_bytes[i] != our_bytes[i])
        print(f"  Total byte-level diffs across the full {len(ref_bytes)}-byte stream: {diffs_total}")

    print()
    print("--- TCP-level facts ---")
    for label, s in [("REF", ref_stream), ("OUR", our_stream)]:
        forward = [p for _, p in s.pkts
                   if (p["src"], p["sport"], p["dst"], p["dport"]) == s.key]
        backward = [p for _, p in s.pkts
                    if (p["src"], p["sport"], p["dst"], p["dport"]) != s.key]
        print(f"  {label}: forward_pkts={len(forward)} backward_pkts={len(backward)}")
        flags_seen_fwd = set()
        for p in forward:
            f = p["flags"]
            for bit, ch in ((0x02, "S"), (0x10, "A"), (0x08, "P"), (0x01, "F"), (0x04, "R")):
                if f & bit: flags_seen_fwd.add(ch)
        flags_seen_bwd = set()
        for p in backward:
            f = p["flags"]
            for bit, ch in ((0x02, "S"), (0x10, "A"), (0x08, "P"), (0x01, "F"), (0x04, "R")):
                if f & bit: flags_seen_bwd.add(ch)
        print(f"        forward flags seen: {''.join(sorted(flags_seen_fwd))}")
        print(f"        backward flags seen: {''.join(sorted(flags_seen_bwd))}")
        # Did app send FIN?
        app_fin = any((p["flags"] & 0x01) for p in forward)
        ball_fin = any((p["flags"] & 0x01) for p in backward)
        ball_rst = any((p["flags"] & 0x04) for p in backward)
        print(f"        app sent FIN: {app_fin} | ball sent FIN: {ball_fin} | ball sent RST: {ball_rst}")

    print()
    print("--- UDP packets in the upload window (both pcaps) ---")
    for label, lst in [("REF", ref_udp), ("OUR", our_udp)]:
        if not lst:
            print(f"  {label}: none")
            continue
        kinds: dict[str, int] = {}
        for _, p in lst:
            k = f"{p['src']}:{p['sport']} -> {p['dst']}:{p['dport']}"
            kinds[k] = kinds.get(k, 0) + 1
        print(f"  {label}: {len(lst)} packets:")
        for k, c in sorted(kinds.items(), key=lambda x: -x[1]):
            print(f"    {c:5d}  {k}")


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    ref_path = Path(sys.argv[1])
    ours_path = Path(sys.argv[2])
    if not ref_path.exists():
        print(f"missing: {ref_path}"); return 2
    if not ours_path.exists():
        print(f"missing: {ours_path}"); return 2
    report(ref_path, ours_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
