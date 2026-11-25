# Environment variables — what you need and how to get them

## Summary table

| Variable | Required when? | What it’s for |
|----------|----------------|---------------|
| `USE_MOCK_PROVIDERS` | Always | `true` = test pipeline without keys |
| `GEMINI_API_KEY` | Real script + TTS | Story, storyboard, **narration** |
| `CLOUDFLARE_ACCOUNT_ID` | Real keyframes | FLUX on Workers AI |
| `CLOUDFLARE_API_TOKEN` | Real keyframes | FLUX on Workers AI |
| `WAN_API_URL` | Real video clips | Wan 2.2 (often Kaggle notebook) |
| `ACE_STEP_URL` | Real music | ACE-Step (often Kaggle/Colab) |
| `TTS_PROVIDER` | Real voice | Set `gemini` when TTS is wired |

Wan and ACE-Step are often **notebooks**, not a single URL on day one. You can leave those blank and use mock video/music until Phase 2.

---

## Step 1 — Gemini API key (do this first)

1. Open https://aistudio.google.com/
2. Sign in with Google.
3. Click **Get API key** → **Create API key**.
4. Copy the key (starts with `AIza…`).
5. In the project folder:

   ```bash
   cp .env.example .env
   ```

6. Edit `.env`:

   ```env
   GEMINI_API_KEY=paste_key_here
   USE_MOCK_PROVIDERS=true
   ```

   Keep `USE_MOCK_PROVIDERS=true` until we wire Gemini in code; then switch to `false`.

7. Test load (does not print the key):

   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   python3 -c "from config import load_config; c=load_config(); print('gemini:', bool(c.gemini_api_key))"
   ```

---

## Step 2 — Cloudflare (FLUX keyframes)

1. Create account: https://dash.cloudflare.com/sign-up
2. Left menu: **Workers & Pages** → **Workers AI**.
3. Note your **Account ID** (right sidebar or URL).
4. **My Profile** → **API Tokens** → **Create Token**  
   Use a template with **Workers AI Read** (or custom with Workers AI + Account read).
5. In `.env`:

   ```env
   CLOUDFLARE_ACCOUNT_ID=...
   CLOUDFLARE_API_TOKEN=...
   FLUX_API_KEY=...   # can duplicate the token until code uses account+token explicitly
   ```

6. Check free tier limits in the dashboard; note what you see in `docs/COSTS.md`.

---

## Step 3 — Kaggle (Wan 2.2 video)

1. https://www.kaggle.com/ → register.
2. **Settings** → **Phone verification** (required for GPU).
3. Create a **Notebook** with GPU (T4): add Wan 2.2 from the assignment links.
4. For this repo, either:
   - Run video in the notebook and copy clips into `outputs/clips/`, or
   - Later set `WAN_API_URL` if you add a small HTTP wrapper.

Until then leave `WAN_API_URL` empty and use mock video (`USE_MOCK_PROVIDERS=true`) or FFmpeg Ken Burns fallback.

---

## Step 4 — ACE-Step (music)

1. Same Kaggle/Colab account.
2. Run ACE-Step 1.5 notebook; export WAV to `outputs/music/`.
3. Or set `ACE_STEP_URL` when you host an endpoint.

---

## What not to do

- Do **not** commit `.env` or paste keys in Slack/chat with classmates.
- Do **not** put keys in `storyboard.json`.

---

## When you’re ready for a “real” run

```env
USE_MOCK_PROVIDERS=false
GEMINI_API_KEY=...
CLOUDFLARE_ACCOUNT_ID=...
CLOUDFLARE_API_TOKEN=...
TTS_PROVIDER=gemini
```

Then:

```bash
python3 run_film.py
```

Today, mock mode still works with only:

```env
USE_MOCK_PROVIDERS=true
```