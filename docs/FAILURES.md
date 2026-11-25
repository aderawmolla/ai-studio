# Failures and workarounds

## Gemini TTS — wrong request schema

- **Symptom:** `400 INVALID_ARGUMENT`, unknown field `speechConfig`.
- **Tried:** Older model id `gemini-2.5-flash-preview-tts`.
- **Fix:** Switched to Interactions API with `response_format` audio and `speech_config` list (`providers/gemini_tts.py`). Logged failed call in `logs/runs.jsonl`.

## Narration vs storyboard duration

- **Symptom:** Voice finishes early/late vs picture; “sync” complaints in review.
- **Tried:** Fixed `duration_seconds` from word-count estimates.
- **Fix / workflow:** `_probe_audio_duration` + pad/trim in `generators/audio/narration.py`; **better fix** is set each shot’s `duration_seconds` from measured TTS, then `python3 main.py videos && python3 main.py assemble`.

## Ken Burns zoom / static feel

- **Symptom:** Some clips feel like pausing stills or aggressive zoom (`providers/mock_media.make_video_from_image`).
- **Tried:** Varying `camera_movement` in storyboard.
- **Workaround:** Simpler motion strings; trim clip tails in assembly if needed. Wan TI2V deferred (see below).

## Wan 2.2 TI2V not wired

- **Symptom:** `WanVideoProvider.generate_clip` raises `NotImplementedError`.
- **Tried:** Plan Kaggle notebook + `WAN_API_URL`.
- **Workaround:** `KenBurnsVideoProvider` for all shots with real FLUX stills. Document GPU quota/time in COSTS if notebook used later.

## ACE-Step HTTP provider not wired

- **Symptom:** `AceStepMusicProvider` not implemented.
- **Tried:** Mock ambient generator; optional `MUSIC_FILE` env to drop in a Kaggle-generated WAV.
- **Workaround:** Accept mock/imported music for submit; note licence in ETHICS.

## FLUX reference images unused

- **Symptom:** Character drift between shots.
- **Cause:** `FluxImageProvider` is text-to-image only; reference `image_path` not sent to API.
- **Workaround:** Heavy `style_block` + character description in every prompt; future: img2img or Cloudflare edit endpoint.

## End card

- **Symptom:** Occasional mismatch between generated card and title/disclosure layout.
- **Tried:** FLUX prompt vs Pillow placeholder.
- **Workaround:** `END_CARD_IMAGE` env or `final.end_card_text` = “Made with AI”.

## Running CLI outside venv

- **Symptom:** `ModuleNotFoundError: jsonschema` on `main.py validate`.
- **Fix:** `make install` and `source .venv/bin/activate` before pipeline commands.

## Cache stale after manual file delete

- **Symptom:** Stage skips regen after deleting `outputs/narration/*.wav`.
- **Fix:** Remove affected cache keys in `cache/index.json` or `make film ARGS='--fresh'` for a full regen.