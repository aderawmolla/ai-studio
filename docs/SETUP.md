# Setup and environment

Copy **`.env.example`** to **`.env`** in the project root. Never commit `.env`.

## One-command runs

| Goal | `.env` essentials | Command |
|------|-------------------|---------|
| Full film on mocks (no keys) | `USE_MOCK_PROVIDERS=true` | `make install && make film` |
| Real stills + Amharic voice | `USE_MOCK_PROVIDERS=false`, `TTS_PROVIDER=gemini`, `GEMINI_API_KEY`, Cloudflare FLUX vars | `make film ARGS='--real'` |
| Force regen narration/images | same + clear cache or `--fresh` | `make film ARGS='--real --fresh'` |

Requires **FFmpeg** on `PATH`. Use the project **venv** after `make install` so `jsonschema` is available (`source .venv/bin/activate`).

## Variables by stage

| Stage | Variables |
|-------|-----------|
| Narration | `GEMINI_API_KEY`, `TTS_PROVIDER=gemini`, optional `GEMINI_TTS_MODEL`, `GEMINI_TTS_VOICE` |
| Keyframes / end card | `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` |
| Video | `WAN_API_URL` (not implemented in repo) → default is Ken Burns over keyframes |
| Music | `ACE_STEP_URL` (not implemented) or `MUSIC_FILE=/path/to/track.wav` |
| Overrides | `END_CARD_IMAGE`, `STORYBOARD_PATH`, `OUTPUTS_DIR` |

## Cloudflare FLUX (Workers AI)

1. [dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages** → **Workers AI**.
2. Create an API token with **Workers AI Read**.
3. Set `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`.

## Gemini TTS

1. [aistudio.google.com](https://aistudio.google.com) → API key.
2. Set `GEMINI_API_KEY` and `TTS_PROVIDER=gemini`.

## Verify config (does not print secrets)

```bash
source .venv/bin/activate
python3 -c "
from config import load_config
c = load_config()
for k, v in {
  'mock_mode': c.use_mock_providers,
  'gemini': bool(c.gemini_api_key),
  'cloudflare': bool(c.cloudflare_account_id and c.cloudflare_api_token),
  'tts': c.tts_provider,
  'wan_url': bool(c.wan_api_url),
  'ace_url': bool(c.ace_step_url),
  'music_file': bool(c.music_file_override),
}.items():
    print(f'{k}: {v}')
"
```