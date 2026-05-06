#!/usr/bin/env bash
# capture.sh — Capture LTX juggling-ball traffic on the PLAYLTX hotspot.
#
# Usage:
#   ./capture.sh <experiment_label>
#
# Example:
#   ./capture.sh E2_single_play
#
# This will write to:   captures/<timestamp>_<label>.pcap
# Press Ctrl-C to stop.  After stopping, run decode_pcap.py on the .pcap.

set -euo pipefail

IFACE="${LTX_IFACE:-wlx8c902dbd3be7}"   # The PLAYLTX hotspot adapter
LABEL="${1:-unlabeled}"
TS="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="$(dirname "$0")/captures"
mkdir -p "$OUT_DIR"
PCAP="$OUT_DIR/${TS}_${LABEL}.pcap"

# BPF filter: every UDP packet on the LTX status/control port and every TCP
# packet on the upload port, in either direction.  Catches:
#   - Ball status broadcasts          (UDP src/dst 41412)
#   - App -> ball control commands    (UDP dst 41412)
#   - Ball -> app command echoes      (UDP src 41412 to ephemeral)
#   - Sequence uploads                (TCP dst 8888)
FILTER='udp port 41412 or tcp port 8888'

echo "=========================================================="
echo " LTX capture starting"
echo " Interface : $IFACE"
echo " Label     : $LABEL"
echo " Output    : $PCAP"
echo " Filter    : $FILTER"
echo "=========================================================="
echo " Press Ctrl-C to stop the capture."
echo

# -U  = packet-buffered (write each packet immediately)
# -s 0 = capture full packets (no truncation)
exec sudo tcpdump -i "$IFACE" -U -s 0 -w "$PCAP" "$FILTER"
