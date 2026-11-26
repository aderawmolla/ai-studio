# Failure log — blockers, attempts, fixes

This file is the **explicit troubleshooting record** for grading. Each entry follows:

**Symptom → what we tried → fix or workaround → evidence**

Redacted lines committed for grading: **`docs/failure_log_excerpts.jsonl`**.  
Raw API and pipeline events are appended locally to **`logs/runs.jsonl`** (gitignored). To verify on a clone after `make film` or any stage, run:

```bash
make logs -n 20
grep -E '"success": false|Reused final|FLUX end card failed' logs/runs.jsonl | tail -20
```

---

## F01 — Gemini TTS wrong request schema

| | |
|--|--|
| **Symptom** | `400 INVALID_ARGUMENT` — unknown field `speechConfig` on first TTS call; narration stage aborted. |
| **Tried** | `gemini-2.5-flash-preview-tts` with camelCase `generation_config.speechConfig`. |
| **Fix** | Interactions API with `response_format` audio and `speech_config` in `providers/gemini_tts.py`; model `gemini-3.8-flash-tts` for Amharic lines. |
| **Evidence** | `logs/runs.jsonl` line 1 (`success: false`, model `gemini-2.5-flash-preview-tts`); then 45+ successful `gemini-3.8-flash-tts` calls in same file. |

---

## F02 — Gemini TTS daily rate limit (429)

| | |
|--|--|
| **Symptom** | Pipeline stopped at `sh_05` during narration regen: HTTP 429, free-tier cap on `gemini-3.8-flash-tts`. |
| **Tried** | Immediate re-run of full `make narration`. |
| **Fix / workflow** | Wait for quota reset; resume with `make narration` (completed shots cached). Spread regens across sessions; `make film ARGS='--resume narration'` after quota clears. |
| **Evidence** | `logs/runs.jsonl` ~2026-11-26T15:03:59Z — `stage: audio`, `shot_id: sh_05`, rate-limit message in `extra.detail`. |

---

## F03 — Narration / picture sync and perceived “overlap”

| | |
|--|--|
| **Symptom** | Voice seemed to start before the previous line finished, or picture continued after speech stopped; reviewer sync complaints. |
| **Tried** | Uniform 8s `duration_seconds` from word-count estimates; **trim** long TTS WAVs to slot length. |
| **Fix** | Stop trimming speech: extend each shot’s `duration_seconds` to natural TTS length + small margin; pad only when shorter (`generators/audio/narration.py`). Then `make videos` → `make subtitles` → `make assemble`. |
| **Evidence** | `storyboard.json` shot durations updated (e.g. 9.8s, 10.2s); `docs/DESIGN.md` notes; before/after in `outputs/narration/sh_*.wav`. |

---

## F04 — Assembly skipped export after end card change

| | |
|--|--|
| **Symptom** | New `make end-card` PNG but final MP4 still showed old end card; log said `Reused final outputs`. |
| **Tried** | `make assemble` only. |
| **Fix** | Include end card file signature in assembly cache fingerprint (`core/dependency.py` `assembly_inputs`). If still cached: delete `outputs/final/heritage_*.mp4` and `assembly:final` in `cache/index.json`, then `make assemble`. |
| **Evidence** | `logs/runs.jsonl` multiple `assemble` + `Reused final outputs` (e.g. 2026-11-26T15:57:07Z); README “End card” section. |

---

## F05 — Cloudflare FLUX 429 on end card

| | |
|--|--|
| **Symptom** | `make end-card` produced black/brown **placeholder** instead of hills art; garbled FLUX text when API worked. |
| **Tried** | Generating end card inside `make assemble`; FLUX prompt with title text in image. |
| **Fix** | Dedicated **`make end-card`** stage; prompt is **typography-free** hills; Pillow overlay for **“Made with AI”**; on 429 reuse `outputs/end_card/end_card_art.png` or `END_CARD_IMAGE`; retry FLUX later; WARN logged when fallback used. |
| **Evidence** | `logs/runs.jsonl` `stage: image`, `429 Client Error` for `flux-1-schnell` (~15:39–15:56Z); `stage: end-card`, `FLUX end card failed — using fallback art` (~15:56:47Z). |

---

## F06 — Ken Burns zoom / static feel

| | |
|--|--|
| **Symptom** | Some clips feel like pausing stills or aggressive zoom. |
| **Tried** | Heavy `camera_movement` strings in storyboard. |
| **Workaround** | Simpler motion strings; Ken Burns via `KenBurnsVideoProvider` (`providers/mock_media.py`). Wan TI2V deferred (F07). |

---

## F07 — Wan 2.2 TI2V not wired

| | |
|--|--|
| **Symptom** | `WanVideoProvider.generate_clip` raises `NotImplementedError`. |
| **Tried** | Kaggle notebook + `WAN_API_URL` plan. |
| **Workaround** | Ken Burns on FLUX stills for all real-mode clips; document GPU time in `docs/COSTS.md` if added later. |

---

## F08 — ACE-Step HTTP provider not wired

| | |
|--|--|
| **Symptom** | `AceStepMusicProvider` not implemented. |
| **Tried** | Manual Kaggle export. |
| **Workaround** | Mock heritage ambient via FFmpeg, or `MUSIC_FILE` env; licence note in `docs/ETHICS.md`. |

---

## F09 — FLUX reference images unused (character drift)

| | |
|--|--|
| **Symptom** | Faces/outfits drift between shots despite `outputs/references/`. |
| **Cause** | `FluxImageProvider` is text-only; reference PNGs not sent to Cloudflare API. |
| **Workaround** | Repeat `style_block` + character text in every `image_prompt`; future: img2img / edit endpoint. |

---

## F10 — Cache stale after manual delete

| | |
|--|--|
| **Symptom** | Stage logs **Reused** after deleting `outputs/narration/*.wav` or clips. |
| **Tried** | Re-run single stage only. |
| **Fix** | `rm -f cache/index.json` or `make film ARGS='--fresh'`; or remove one key from `cache/index.json`. |

---

## F11 — CLI outside venv

| | |
|--|--|
| **Symptom** | `ModuleNotFoundError: jsonschema` on `main.py validate`. |
| **Fix** | `make install`; run stages via `make …` or `.venv/bin/python3 main.py …`. |

---

## F12 — Long narration job interrupted

| | |
|--|--|
| **Symptom** | Full narration regen aborted mid-run (~12 min); `full.wav` missing while per-shot WAVs existed. |
| **Tried** | Single background command with `tail` on stdout only. |
| **Fix** | Re-run `make narration` to rebuild `full.wav` and save storyboard durations; then downstream stages. |
| **Evidence** | Partial regen 2026-11-26T15:20–15:32Z in `logs/runs.jsonl`; completed in a follow-up `make narration` run. |

---

## Quick reference — commands after a failure

| Failure type | Command |
|--------------|---------|
| TTS / schema / 429 | `make doctor`; wait on 429; `make narration` or `make film ARGS='--resume narration'` |
| Sync / overlap | `make narration` → `make videos` → `make subtitles` → `make assemble` |
| End card wrong / 429 | `make end-card`; optional `cp hills.png outputs/end_card/end_card_art.png`; `make assemble` |
| Stale cache | `rm -f cache/index.json` or clear `assembly:final` |
| Inspect | `make logs`, `make status` |

See also: `docs/EXPERIMENTS.md` (hypothesis trials), `docs/COSTS.md` (call counts), `core/failure_report.py` (terminal summary on stage abort).