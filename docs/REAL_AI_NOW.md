# Switch to real AI (checklist)

## What becomes real automatically

| Stage | Real when `USE_MOCK_PROVIDERS=false` | Needs |
|-------|--------------------------------------|-------|
| Narration | Gemini TTS | `GEMINI_API_KEY`, `TTS_PROVIDER=gemini` |
| Keyframes + refs | Cloudflare FLUX | `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` |
| Video | Ken Burns on **real** stills | No `WAN_API_URL` (Wan = Kaggle later) |
| Music | Still placeholder tone | `ACE_STEP_URL` **or** Kaggle WAV → `outputs/music/background.wav` |
| Assembly | FFmpeg | Already real |

## Your `.env` for first real run

```env
USE_MOCK_PROVIDERS=false
TTS_PROVIDER=gemini
GEMINI_API_KEY=...
CLOUDFLARE_ACCOUNT_ID=...
CLOUDFLARE_API_TOKEN=...
# WAN_API_URL=
# ACE_STEP_URL=
```

Use a Gemini key from **AI Studio** (usually starts with `AIza`).

## Commands

```bash
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py doctor

# Regenerate everything (clear cache if you had mock outputs)
rm -f cache/index.json
python3 run_film.py
```

Watch `logs/runs.jsonl` for lines with `"type": "model_call"`.

## Still manual (full assignment)

1. **Wan 2.2** clips — Kaggle notebook → copy to `outputs/clips/`
2. **ACE-Step** music — Kaggle notebook → `outputs/music/background.wav` then `python3 main.py assemble`
3. **8–12 shots**, your story, **DESIGN.md** audience tests