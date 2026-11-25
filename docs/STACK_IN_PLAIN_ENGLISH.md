# What each service does (simple)

Think of your film as **5 jobs**. Each job can use a different tool.

```
Your story (storyboard.json)
        │
        ├─► GEMINI ────────► voice reads your script (narration)
        │
        ├─► CLOUDFLARE/FLUX ► still pictures per shot (keyframes)
        │
        ├─► KAGGLE + WAN ──► short video clips from those pictures
        │
        ├─► KAGGLE + ACE ──► background music
        │
        └─► FFMPEG (free) ─► final MP4 (cut, subtitles, ducking)
```

## Gemini (`GEMINI_API_KEY`)

- **What:** Google’s AI for **text** and **text-to-speech**.
- **Your film:** narration in your language; later help with script/storyboard.
- **Runs on:** Google’s servers (free tier).
- **You do:** put key in `.env`. Pipeline will call it when we wire TTS.

## Cloudflare (`CLOUDFLARE_ACCOUNT_ID` + `CLOUDFLARE_API_TOKEN`)

- **What:** Host that runs **FLUX** image models.
- **Your film:** character sheet + one **photo** per shot before video.
- **Runs on:** Cloudflare (free daily image allowance).
- **You do:** put account id + token in `.env`.

## Kaggle (`KAGGLE_API_TOKEN`)

- **What:** Website that lends you a **free GPU** for heavy models.
- **Your film:** **Wan 2.2** (picture → 5s video) and **ACE-Step** (music).
- **Runs in:** **Kaggle notebooks in your browser**, not inside `run_film.py` today.
- **Token purpose:** proves it’s you so Kaggle lets you use GPU and API tools.
- **You do:**
  1. Put `KAGGLE_API_TOKEN=KGAT_...` in `.env` (only `.env`, never GitHub).
  2. Open notebooks, generate clips/music, download into `outputs/`.
  3. Run `python3 run_film.py` to assemble.

The token does **not** replace video generation inside your laptop script unless we build extra automation later.

## `WAN_API_URL` and `ACE_STEP_URL`

- **What:** Addresses of **your own** video/music servers (advanced).
- **Most students:** leave **empty** and use Kaggle + copy files instead.

## `USE_MOCK_PROVIDERS`

- **true:** laptop fakes pictures/sounds — good to learn the pipeline.
- **false:** try real Gemini/Cloudflare when code supports it.

---

## What I still need from you (to make *your* film)

| # | You provide | Why |
|---|-------------|-----|
| 1 | **Your story** (person/place/family) | Assignment is personal heritage |
| 2 | **`GEMINI_API_KEY`** in `.env` | Real narration |
| 3 | **Narration language** (e.g. Amharic, English) | TTS settings |
| 4 | **Cloudflare** in `.env` | Real keyframes (Phase 2) |
| 5 | **`KAGGLE_API_TOKEN`** in `.env` | GPU work in Kaggle |
| 6 | **8–12 shots** in `storyboard.json` | Assignment length |
| 7 | **Audience notes** in `docs/DESIGN.md` | Grading (design thinking) |

You do **not** need to give me keys in chat — only fill `.env` locally.

**Test Kaggle:** `pip install -r requirements.txt` then `python3 main.py doctor --kaggle`