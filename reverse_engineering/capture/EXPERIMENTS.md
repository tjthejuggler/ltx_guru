# LTX Ball Protocol — Capture Experiments Runbook

*Created 2026-05-06.*

We have a reliable upload mechanism but unreliable PLAY/STOP control via our
own Python scripts.  The remaining unknowns are the algorithms for:

- **Command Byte 2 (CB2)** — currently hard-coded to `0x01`, sometimes works
- **Play nonces P1, P2** — currently random; reportedly fails after a few cycles
- The exact relationship between ball broadcast bytes
  `data[9]`, `data[10]`, `data[11]` and what the official app sends
- Whether STOP suffix is always zeros or sometimes encodes something

We now know (from APK decompile) that the official Android app contains these
methods inside `package:ltxremote/engines/showengine.dart` and
`package:ltxremote/engines/nodeengine.dart`:

- `sendShowCommand`     ← almost certainly fires PLAY
- `startShow`, `startShowNoSync`, `stopShow`, `stopShowNoSync`
- `sendStrobe`, `sendBrightness`, `sendColor`
- `sendGlobalStateCommand`, `sendEventCommand`, `sendPacket`
- `eventHandlerSendData` (the low-level send)

The plan is to drive the **official Android app** through a deterministic
script of UI actions while capturing every packet on `wlx8c902dbd3be7`
(the `PLAYLTX` hotspot interface).  The decoder
([`decode_pcap.py`](decode_pcap.py)) annotates every packet so byte-level
comparison across runs is trivial.

## Mechanics — read this once

### Each experiment follows the same template

1. **Reset state** (this varies per experiment; see below).
2. Open a terminal and start the capture:
   ```bash
   cd /home/twain/Projects/ltx_guru/reverse_engineering/capture
   ./capture.sh <ExperimentLabel>
   ```
   It will print the `.pcap` filename it is writing to.  Leave this running.
3. **Perform the actions** listed for the experiment.  Speak aloud (or type
   into a notes file) the exact tap-by-tap sequence with rough timestamps —
   we will line these up against the capture.
4. **Stop the capture** with `Ctrl-C` in the capture terminal.
5. **Decode**:
   ```bash
   python3 decode_pcap.py captures/<that-file>.pcap --json | tee captures/<that-file>.txt
   ```
6. The `.txt` (annotated timeline) and `.events.json` (machine-parseable) go
   into the report.  I will read them and propose the next experiment.

### State reset levels (used in different experiments)

- **Soft reset**: stop any playing show in the app, wait 5 s.
- **App reset**: force-stop the LTX Remote app on the phone, relaunch.
- **Ball power-cycle**: physically turn the ball off, wait 5 s, turn it on,
  wait until it joins the `PLAYLTX` Wi-Fi (it will appear in the app's node
  list).
- **Cold boot**: app reset *and* ball power-cycle.

### Notes file convention

Each experiment also wants a small `.notes.txt` next to the pcap describing
what you did, e.g.:

```
captures/20260506_173000_E2_single_play.notes.txt:
  17:30:08  capture started
  17:30:14  tapped "Play" once on uploaded show "4px_blue_10.prg"
  17:30:18  ball lit blue, sequence playing (no red LED)
  17:30:25  tapped "Stop"
  17:30:27  ball went dark
  17:30:29  capture stopped
```

A real wall-clock time per UI action is enough — we will correlate to the
pcap by relative ordering.

---

## Experiments (run in order)

### E1 — Baseline: just listen for ~30 s with nothing happening

**Goal**: verify the capture pipeline; record what an idle ball broadcast
looks like.

State: app open, no show playing, ball idle.
Actions: none, just wait 30 s.
Expected output: a stream of ~1 Hz `udp_status` events, no `udp_cmd`, no
`tcp_upload`.

If this is empty, the capture interface is wrong; check
[`capture.sh`](capture.sh) `IFACE` env var.

---

### E2 — Single upload of a known PRG

**Goal**: confirm our existing upload spec matches what the official app
sends, byte-for-byte.

State: cold boot.  Pick one specific show in the app (note its filename).
Actions:
1. Open the app, wait until ball is shown as connected.
2. Tap "Upload" or whatever the equivalent gesture is to push the show.
3. Wait 5 s after upload completes.
4. Stop capture.

What we want to learn:
- The 15-byte prefix matches our spec.
- The full TCP body matches what we already send.
- Whether the app sends *additional* setup UDP commands either side of the
  upload that we may have missed.

---

### E3 — Single PLAY after upload, on a fresh ball

**Goal**: capture the very first PLAY of a session.  The previous summary
notes the first PLAY uses `OpID=0x14` with specific known nonces — we need
to verify and capture exact CB2/P1/P2.

State: cold boot, then E2 first to upload one show.  Don't tap Play yet.
Actions:
1. Start a *new* capture for E3.
2. Tap Play once.
3. Wait until the show is clearly running on the ball (~3 s).
4. Tap Stop.
5. Wait 3 s.  Stop capture.

What we want to learn:
- The exact 9 bytes of the first PLAY.
- What `data[10]` was on the most-recent broadcast immediately before that
  PLAY (the decoder shows this as "ctx: status …earlier" right under each
  command).  Critical hypothesis: app's `cb2 == data[10]`.
- The 9 bytes of the STOP and what changed in broadcasts between PLAY and
  STOP.

---

### E4 — Five PLAY/STOP cycles in a row, no reset

**Goal**: see whether CB2 changes across cycles, and whether P1/P2 follow a
pattern.

State: continue from E3 (or start a fresh session and skip to here).  Ball
is uploaded with one show, currently stopped.
Actions:
1. Start capture.
2. Tap Play, wait 2 s, Tap Stop, wait 2 s.  Repeat **5 times**.
3. Stop capture.

What we want to learn:
- Does OpID really increment by `+0x14` each cycle?
- Does CB2 stay constant (e.g. always `0x01`) or change?
- Do P1/P2 look random, or counter-like, or hash-like?
- Compare consecutive PLAY commands' P1P2 bytes — are they monotonically
  increasing? bit-related? always-different? coincidental with broadcast TS?

---

### E5 — Five PLAYs **after restarting the official app** between each

**Goal**: see whether app-side state is reset on relaunch.  If P1/P2 are
generated fresh each session, restarting the app should reset them.

State: ball is uploaded and stopped.
Actions for each iteration (×5):
1. Start (or resume) capture.
2. Force-stop the LTX Remote app on the phone.  Relaunch it.  Wait for the
   ball to appear connected.
3. Tap Play.  Wait 2 s.  Tap Stop.  Wait 2 s.

Stop capture once.  We compare the 5 PLAYs across the 5 sessions.

What we want to learn:
- If P1/P2 of the first PLAY in each session are identical → the app
  "starts" with a fixed value.
- If OpID resets (e.g. always `0x14` first) or persists across launches.

---

### E6 — Five PLAYs **after power-cycling the ball** between each

**Goal**: distinguish ball-side state from app-side state.

Actions for each iteration (×5):
1. Power-cycle the ball.  Wait until it rejoins the AP and shows as
   connected.
2. Tap Play.  Wait 2 s.  Tap Stop.

What we want to learn:
- If the ball insists on `OpID=0x14` after every reboot → ball-side state.
- If P1/P2 reset only with the app, not the ball → app-side state.
- If the ball still accepts the next-expected OpID after reboot → the
  ball persists state across power cycles (less likely but possible).

---

### E7 — Strobe / Brightness / Direct color

**Goal**: enumerate the *other* command bytes besides 0x61 PLAY/STOP.  We
expect at least three more command groups (strobe, brightness, color) and
this maps them.

Actions:
1. Start capture.
2. In the app, drag the brightness slider through several values (e.g.
   100% → 25% → 75%).  Note what you tapped and roughly when.
3. Adjust the strobe slider similarly.
4. Use the color picker to set 3 different solid colors directly.
5. Stop capture.

What we want to learn:
- The byte-level command shapes for strobe / brightness / direct color.
- Whether they share the OpID/CB2/nonce structure or are simpler.

---

### E8 — Try to induce a Red-LED state with our Python script, then rescue with the official app

**Goal**: capture exactly what the official app sends to recover a ball
that's stuck in the error state.

Actions:
1. Make sure the ball has a show uploaded.
2. Start capture.
3. Run our `trigger_sequence_15.py` (or similar) with a *deliberately* bad
   nonce to push the ball into a red LED.  This may take 1–3 attempts.
4. Once the red LED is on, switch to the official app and tap Play.
5. Observe whether the ball recovers.  If yes, also tap Stop.
6. Stop capture.

What we want to learn:
- The recovery sequence — likely a normal PLAY whose CB2/nonce/TS-echo *do*
  satisfy the ball.

---

## What to send me after each experiment

For each experiment, please paste (or open in VS Code) the corresponding
files in `reverse_engineering/capture/captures/`:

1. The `.txt` decoded timeline.
2. The `.events.json` sidecar.
3. The `.notes.txt` describing what you did and when.

That is enough for me to do byte-level diffing.  I do not need the raw
`.pcap` (but please keep them — we may want to re-decode with new logic).
