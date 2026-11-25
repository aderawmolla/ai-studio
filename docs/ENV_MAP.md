# Environment variables → assignment requirements

Use **`.env`** for secrets (copy from `.env.example`). Run any command from the project root; `config.py` loads `.env` automatically.

## By pipeline stage

| Stage | What the assignment wants | Environment variables | Can leave empty? |
|-------|---------------------------|----------------------|------------------|
| **Test pipeline** | Prove `storyboard.json` → MP4 | `USE_MOCK_PROVIDERS=true` | — |
| **Story / script** | Gemini writes or refines narration | `GEMINI_API_KEY`, optional `GEMINI_MODEL` | Yes until real Gemini story |
| **Radio cut** | Gemini TTS, your language | `GEMINI_API_KEY`, `TTS_PROVIDER=gemini` | No for real voice |
| **Reference sheet** | FLUX character/style | `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` | Yes if mock |
| **Keyframes** | FLUX per shot | Same Cloudflare vars | Yes if mock |
| **Moving shots** | Wan 2.2 TI2V | `WAN_API_URL` **or** Kaggle + manual files | Yes (mock / Ken Burns) |
| **Music** | ACE-Step 1.5 | `ACE_STEP_URL` **or** Kaggle + manual WAV | Yes if mock |
| **Assembly** | FFmpeg | `FFMPEG_PATH` only if needed | Usually yes |

## By assignment phase

| Phase | Minimum `.env` |
|-------|----------------|
| Phase 1 — story + radio cut | `GEMINI_API_KEY`, `TTS_PROVIDER=gemini`, keep `USE_MOCK_PROVIDERS=true` until TTS wired |
| Phase 2 — pictures | + `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, then `USE_MOCK_PROVIDERS=false` for images |
| Phase 2 — video/music on Kaggle | `KAGGLE_USERNAME`, `KAGGLE_KEY` (for **you** in notebooks; URLs optional) |
| Phase 3 — full film | All above + Wan/ACE files or URLs |

## Variables not used by Python yet

`KAGGLE_USERNAME` / `KAGGLE_KEY` are documented for your Kaggle notebooks. The repo does not call Kaggle API for Wan/ACE until we add that integration.

## Verify (never prints secrets)

```bash
python3 -c "
from config import load_config
c = load_config()
checks = {
  'mock_mode': c.use_mock_providers,
  'gemini': bool(c.gemini_api_key),
  'cloudflare': bool(c.cloudflare_account_id and c.cloudflare_api_token),
  'wan_url': bool(c.wan_api_url),
  'ace_url': bool(c.ace_step_url),
  'tts': c.tts_provider,
}
for k, v in checks.items():
    print(f'{k}: {v}')
"
```