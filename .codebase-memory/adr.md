## ADR — LTX Ball Sequence Upload & Trigger: Reverse-Engineering Strategy (2026-05-06)

### Context

Existing state: TCP upload (port 8888) is fully solved. UDP play/stop control (port 41412) is partially solved — commands are 9-byte `61 OPID CB2 00 00 P1 P2 TS3 TS4` frames; OpID cycling and TS-echo are understood; CB2 and P1/P2 algorithms are NOT and our scripts get a "red LED" rejection intermittently.

The official Android app **`com.lightrix.ltxremote`** (`/home/twain/Documents/4px_ball/LTX_Remote/Android/app-release-1.0.0+18.apk`, July 2020 build, 18 MB) is the working oracle — it controls the balls reliably. We had not yet used it as a reference.

### Decision

1. **Decompile the APK** with `jadx` (installed at `reverse_engineering/tools/jadx/`). The Android Java/Kotlin shell is a Flutter wrapper; the actual Dart logic is AOT-compiled into `resources/lib/{arm64-v8a,armeabi-v7a,x86_64}/libapp.so`.

2. **Skip dynamic instrumentation as the first step.** The phone is non-rooted, and Frida-gadget would require repacking + signing + reinstalling the APK (loses saved sequences, adds risk). Instead, drive the working app and capture wire traffic.

3. **Capture wire traffic on the laptop's existing PLAYLTX Wi-Fi hotspot** (`wlx8c902dbd3be7`, USB Wi-Fi adapter, `10.42.0.1/24`). The phone and the balls are already both clients of this AP, so the laptop sees every packet. Use `tcpdump` filtered to `udp port 41412 or tcp port 8888`.

4. **Decode captures with a stdlib-only Python pcap parser** (`reverse_engineering/capture/decode_pcap.py`) that knows the LTX protocol. It pairs every command with the surrounding ball broadcast state, making CB2/P1/P2 dependencies visible by inspection.

5. **Run a fixed sequence of named experiments** (`reverse_engineering/capture/EXPERIMENTS.md`) that isolate one variable at a time (E1 idle baseline → E2 upload → E3 single play → E4 cycles → E5 app restarts → E6 ball power-cycles → E7 effect commands → E8 red-LED recovery).

6. **Escalate to Frida-gadget instrumentation only if** the experiments fail to reveal the CB2/P1/P2 algorithm (i.e. they look truly random and stateless to ball- and app-side reset).

### Findings already from the decompile (no captures yet)

The APK is a Flutter app whose Dart class/method names survive in `libapp.so` strings:

- Source files inferred: `package:ltxremote/{main.dart, common/{brightness,colorpicker,effects}.dart, engines/{node,nodeengine,nodemanager,showengine}.dart, pages/{livecontrol,nodelist,showcontrol}.dart}`.
- Key methods: `sendShowCommand`, `startShow`, `startShowNoSync`, `stopShow`, `stopShowNoSync`, `sendStrobe`, `sendBrightness`, `sendColor`, `sendGlobalStateCommand`, `sendEventCommand`, `sendPacket`, `eventHandlerSendData`, `batchUploadPressed`, `uploadFirmware`.
- Strings in binary: `"PLAYLTXBALL"`, `"upload ok"`, `"Unrecognized command "`, `"UDP sender bound to "`, `"] Node is not connected, not uploading."`, `"] Upload complete"`, `"Error uploading firmware : "`.
- `CommandIDs` exists as a class with static int constants — values are inlined at call sites, not preserved as symbols. Bodies of the relevant functions are pure ARM machine code in `libapp.so`; Frida hook of `Socket_SendTo` is the cheapest way to read them at runtime if static analysis becomes necessary.

### Tooling artefacts created

- `reverse_engineering/tools/jadx/`              — jadx 1.5.1 standalone
- `reverse_engineering/decompiled/ltx_remote/`   — full APK decompile
- `reverse_engineering/analysis/libapp_strings.txt` (11k strings)
- `reverse_engineering/analysis/{class_names,protocol_hits,ltxremote_files,all_enums}.txt`
- `reverse_engineering/capture/capture.sh`       — `sudo tcpdump` wrapper
- `reverse_engineering/capture/decode_pcap.py`   — stdlib pcap decoder + LTX annotator
- `reverse_engineering/capture/test_decoder.py`  — synthetic-pcap unit test (passing)
- `reverse_engineering/capture/EXPERIMENTS.md`   — runbook for E1-E8

### Status

Tooling complete and validated. Awaiting capture data from physical experiments E1-E8 to nail CB2 and P1/P2 algorithms. Once those are pinned, `ltx_ball_client.py` will replace the existing `sequence_uploading_and_triggering/trigger_sequence_*.py` family.