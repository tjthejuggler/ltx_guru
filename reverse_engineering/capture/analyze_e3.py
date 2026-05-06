#!/usr/bin/env python3
"""Analyze E3 capture: 5x PLAY/STOP cycles, all successful."""
import json
import sys
from collections import Counter

PCAP_JSON = "captures/20260506_191044_E3_play_5cycles.pcap.events.json"

def main():
    data = json.load(open(PCAP_JSON))
    out = []
    out.append(f"Total events: {len(data)}")
    out.append(f"Kinds: {dict(Counter(e['kind'] for e in data))}")
    out.append("")

    cmds = [(i, e) for i, e in enumerate(data) if e['kind'] == 'udp_other']
    broads = [(i, e) for i, e in enumerate(data) if e['kind'] == 'udp_status']
    out.append(f"Commands (udp_other): {len(cmds)}")
    out.append(f"Status broadcasts: {len(broads)}")
    out.append("")

    out.append("=== ALL 10 PHONE->BALL COMMANDS ===")
    out.append("idx  time(rel)  src                sport  dst                 dport  len  hex")
    t0 = cmds[0][1]['ts'] if cmds else 0
    for n, (idx, c) in enumerate(cmds):
        d = c['detail']
        rel = c['ts'] - t0
        line = "%2d %4d %12.3f  %-18s %5d  %-18s %5d  %4d  %s" % (
            n, idx, rel, d['src'], d['sport'], d['dst'], d['dport'], d['len'], d['raw_hex'])
        out.append(line)
    out.append("")

    out.append("=== COMMAND CONTEXT (preceding broadcast = ball state when command was sent) ===")
    for n, (idx, c) in enumerate(cmds):
        cts = c['ts']
        prev_b = None
        next_b = None
        for bidx, b in broads:
            if b['ts'] < cts:
                prev_b = (bidx, b)
            elif b['ts'] >= cts and next_b is None:
                next_b = (bidx, b)
                break
        cmd_hex = c['detail']['raw_hex']
        cmd_bytes = [cmd_hex[i:i+2] for i in range(0, len(cmd_hex), 2)]
        out.append(f"--- CMD #{n} idx={idx} ---")
        out.append(f"  CMD hex: {cmd_hex}")
        out.append(f"  CMD bytes: {cmd_bytes}")
        if prev_b:
            pidx, p = prev_b
            pd = p['detail']
            dt = (cts - p['ts']) * 1000
            out.append("  PREV BCAST (dt=%.0fms before): len=%d d9=0x%02x d10=0x%02x d11=0x%02x d12_play=0x%02x TS=%s hex_head=%s" % (
                dt, pd['len'], pd['state9'], pd['cb2_src_data10'], pd['state11'], pd['play_status_data12'],
                str(pd['ts_full']), pd['raw_hex'][:80]))
        if next_b:
            nidx, nb = next_b
            nd = nb['detail']
            dt = (nb['ts'] - cts) * 1000
            out.append("  NEXT BCAST (dt=%.0fms after):   len=%d d9=0x%02x d10=0x%02x d11=0x%02x d12_play=0x%02x TS=%s hex_head=%s" % (
                dt, nd['len'], nd['state9'], nd['cb2_src_data10'], nd['state11'], nd['play_status_data12'],
                str(nd['ts_full']), nd['raw_hex'][:80]))
        out.append("")

    out.append("=== CMD BYTE-BY-BYTE TABLE ===")
    out.append("  " + " ".join("b%02d" % i for i in range(9)))
    for n, (idx, c) in enumerate(cmds):
        hx = c['detail']['raw_hex']
        bytes_str = " ".join(hx[i:i+2] for i in range(0, len(hx), 2))
        out.append("#%d %s" % (n, bytes_str))

    out.append("")
    out.append("=== UNIQUE VALUES PER POSITION ===")
    raws = [bytes.fromhex(c['detail']['raw_hex']) for _, c in cmds]
    if raws and all(len(r) == len(raws[0]) for r in raws):
        for pos in range(len(raws[0])):
            vals = [r[pos] for r in raws]
            uniq = sorted(set(vals))
            hex_vals = [f"0x{v:02x}" for v in vals]
            uniq_hex = [f"0x{v:02x}" for v in uniq]
            out.append(f"  byte[{pos}]: {hex_vals}  unique={uniq_hex}")

    open('/tmp/e3_analysis.txt', 'w').write('\n'.join(out))
    print(f"Wrote /tmp/e3_analysis.txt ({len(out)} lines)")

if __name__ == '__main__':
    sys.exit(main() or 0)
