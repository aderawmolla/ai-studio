# Experiments

Format: **hypothesis → change → result** (evidence in code, `logs/runs.jsonl`, or outputs).

## E01 — Mock pipeline baseline

- **Hypothesis:** A stranger can clone the repo and run end-to-end without API keys.
- **Change:** `USE_MOCK_PROVIDERS=true`, `make film`.
- **Result:** Full 9:16 + 16:9 MP4 with Pillow/FFmpeg mocks; pytest covers cache and schema (`tests/`).

## E02 — Gemini TTS API shape

- **Hypothesis:** First Gemini TTS SDK call would work with camelCase `speechConfig`.
- **Change:** Initial client used `generation_config.speechConfig`.
- **Result:** One failed call logged (`gemini-2.5-flash-preview-tts`, `400 INVALID_ARGUMENT`). Fixed to Interactions API + `speech_config` in `providers/gemini_tts.py`; subsequent Amharic calls succeed (`extra.type: model_call` in `logs/runs.jsonl`).

## E03 — Amharic narration voice

- **Hypothesis:** Stock Gemini TTS can carry Amharic documentary tone without voice cloning.
- **Change:** `TTS_PROVIDER=gemini`, style instruction per language, voice `Kore`, 9 per-shot lines.
- **Result:** 45+ successful TTS calls on `gemini-3.8-flash-tts`; latency often 5–45 s per line (see COSTS). Fit/pad in `generators/audio/narration.py` aligns WAV to storyboard shot length.

## E04 — FLUX on Cloudflare for look

- **Hypothesis:** Shared `style_block` + per-shot `image_prompt` gives a coherent gouache look.
- **Change:** `@cf/black-forest-labs/flux-1-schnell`, 1080×1920, 4 references + 9 keyframes.
- **Result:** ~42 logged image calls; style is consistent at illustration level but faces still drift shot-to-shot (no image conditioning in API wrapper yet).

## E05 — Reference sheet before keyframes

- **Hypothesis:** Generating `references/` first improves continuity.
- **Change:** Pipeline order `references` → `images`; fingerprint includes reference IDs.
- **Result:** References anchor descriptions in cache keys; FLUX still text-only so drift reduced only via prompt text, not pixels.

## E06 — Video without Wan API

- **Hypothesis:** Ken Burns on keyframes is acceptable when `WAN_API_URL` is unset.
- **Change:** `KenBurnsVideoProvider` in `core/registry.py`.
- **Result:** All clips generated locally; some shots show noticeable zoom/pause (see FAILURES). Faster than queuing Kaggle Wan for this deadline.

## E07 — Music: mock vs manual ACE

- **Hypothesis:** Underscore must stay thin under Amharic voice.
- **Change:** Long `music_prompt` + metadata in storyboard; mock `make_heritage_ambient_wav` or `MUSIC_FILE` override.
- **Result:** Mock bed ducks cleanly; ACE-Step provider in code still `NotImplementedError` — final track may be mock or imported WAV (document in ETHICS/COSTS).

## E08 — Caching one shot

- **Hypothesis:** Editing one `image_prompt` regenerates only that keyframe.
- **Change:** `core/dependency.shot_keyframe_inputs` fingerprint per `shot_id`.
- **Result:** `tests/test_cache.py` + log lines `Reused keyframe sh_XX` when unchanged (walkthrough demo).

## E09 — Assembly ducking

- **Hypothesis:** FFmpeg `sidechaincompress` keeps narration intelligible.
- **Change:** `generators/assembly/assembler.py` mix music + full narration.
- **Result:** Narration readable on phone speaker in manual listen; tune threshold/ratio if music still fights voice.

## E10 — End card

- **Hypothesis:** FLUX `end_card_prompt` gives on-brand “Made with AI” card.
- **Change:** `make end-card` / `generators/assembly/end_card.py` calls image provider when `USE_MOCK_PROVIDERS=false` (assemble only appends the clip).
- **Result:** `outputs/end_card/end_card.png` generated or placeholder with title + “Made with AI” text.