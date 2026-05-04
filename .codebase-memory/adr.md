# ADR: Lyrics Timestamping — Switch from Gentle to Deepgram Nova-3 ASR

**Date:** 2026-05-04  
**Status:** Accepted

## Context

The original lyrics timestamping pipeline used Gentle forced-alignment (Docker-based). For "Fast Car" (Tracy Chapman), this produced completely wrong timestamps — Gentle's conservative mode silently dropped ~20–30% of words on sung music, and even non-conservative mode failed because the singer improvises lines that differ from the written lyrics text.

Multiple attempts were made to fix the Gentle pipeline:
1. Disabled conservative mode → still bad (singer improvises)
2. Built `align_with_anchors.py` to use ASR timestamps as anchors + interpolation → complex, still had 31 out-of-order timestamps after 3 iterations

## Decision

**Use Deepgram Nova-3 via ppq.ai as the primary lyrics timestamping method.**

The key insight: the ASR transcribes what the singer actually sang. The output IS the synced lyrics — no alignment step needed. The `transcribe_lyrics.py` tool output is used directly as `fast_car_synced_lyrics.json`.

**Workflow:**
```
transcribe_lyrics.py audio.mp3 → synced_lyrics.json (direct, no post-processing)
```

**NOT:**
```
transcribe_lyrics.py → ASR JSON → align_with_anchors.py → synced_lyrics.json
```

## Implementation

- Tool: `roocode_sequence_designer_tools/transcribe_lyrics.py`
- API: `POST https://api.ppq.ai/v1/audio/transcriptions`, model=nova-3, response_format=verbose_json
- API key: `sequence_maker/ppq_api_key.txt`
- Chunking: 30s chunks with 3s overlap for long audio; prompt passed to every chunk
- Output format: `{"word_timestamps": [{"word": str, "start": float, "end": float, "confidence": float}], ...}`
- Result for Fast Car: 280 words, 27.69s–275.84s, 0 out-of-order timestamps

## Consequences

- **Positive:** 100% of words have timestamps, 0 out-of-order, no Docker dependency
- **Positive:** Works even when singer improvises (transcribes what is heard, not what is written)
- **Negative:** Requires ppq.ai API key and internet access
- **Negative:** ASR words may differ from written lyrics (singer improvises) — this is correct behaviour, not a bug
- **Neutral:** `align_with_anchors.py` is now unused for this workflow; kept for potential future use

## GUI Fixes (same session)

- `sequence_maker/ui/handlers/file_handlers.py`: filter `None` start/end at import boundary
- `sequence_maker/ui/lyrics_widget.py`: defensive None guards in display
- `sequence_maker/models/lyrics.py`: None-safe `get_word_at_time`
