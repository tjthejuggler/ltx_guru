ADR: Auto-discovery of LTX Balls at Startup

Date: 2026-05-10

Context:
Users previously had to manually type IP addresses for each ball via the Ball IP Dialog. The official LTX app auto-detects balls on the network.

Decision:
- Leverage the existing `_discovery_worker` (passive UDP listener on port 41412, matching "NPLAYLTXBALL" broadcasts) that was already present in BallManager.
- Start discovery automatically at app startup (in `application.py run()`).
- Add `_schedule_auto_assign` / `_auto_assign_ips` methods with 500ms debounce to auto-assign discovered balls to the 3 IP/timeline slots in discovery order (1st→Ball 1, 2nd→Ball 2, 3rd→Ball 3).
- Auto-assignment overwrites any existing IPs (as requested).
- Emit `ball_ips_auto_updated` signal so the UI (BallWidget) can update button states and auto-start streaming.
- Persist auto-assigned IPs to config so they survive restarts.

Consequences:
- Users no longer need to manually enter ball IPs when balls are on the network.
- The manual Ball IP Dialog still works as a fallback (with a note about auto-discovery).
- The BallScanDialog (manual scan) still works for advanced use cases.
- Port 41412 is bound by the passive listener at startup; the scan dialog's active scan may conflict (pre-existing issue, not worsened).