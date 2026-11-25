# Heritage Short — AI Content Generation Pipeline

**10 Academy — AI-Content Generation: The Heritage Short**

`storyboard.json` drives the pipeline: keyframes → clips → narration → music → subtitles → **9:16** and **16:9** MP4. Sample film: **The Smile That Carried Him**.

## Quick start (install and run)

```bash
# 1. Prerequisites: Python 3.10+, FFmpeg on PATH (see below)
cd heritage-film

# 2. Install Python deps into .venv (requirements.txt)
make install

# 3. Config (mock mode works with defaults)
cp .env.example .env

# 4. Build the full film
make film                    # no API keys
make film ARGS='--real'      # FLUX + Gemini TTS (keys in .env)

# 5. Optional checks
make final-check
```

One stage only: `make audio`, `make assemble`, `make images`, … — run `make help`.

---

## Who may use this repo

| You are… | What to do |
|----------|------------|
| Grader | `make install && make film` (mock works without API keys). |
| Forking for your own assignment | Replace **your** `storyboard.json`; do not submit this story as yours. |
| Reproducing this submission | Same commands + optional `make film ARGS='--real'` with keys in `.env`. |

---

## Prerequisites

| Need | Notes |
|------|--------|
| **Python 3.10+** | `python3 --version` |
| **FFmpeg + ffprobe** | On `PATH`. Ubuntu: `sudo apt install ffmpeg`. macOS: `brew install ffmpeg`. |
| **make** | Optional; otherwise use `.venv/bin/python3` (see below). |
| **`.env`** | Copy from `.env.example`. Mock mode needs no keys. |

After **git clone**, `outputs/` is usually empty (gitignored). Run the pipeline to create MP4s.

**Python packages** (installed by `make install` from `requirements.txt`): `jsonschema`, `Pillow`, `python-dotenv`, `google-genai`, `requests`, `pytest`, `kaggle` (optional).

---

## Install (once)

```bash
cd heritage-film
make install
```

Or manually:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip && pip install -r requirements.txt
```

- **`make …`** uses `.venv/bin/python3` — no need to activate venv.
- **`python3 main.py …`** — activate venv first, or use `.venv/bin/python3 main.py …`.

```bash
make help    # list all make targets
make test    # pytest, no API cost
```

---

## Environment (`.env`)

```bash
cp .env.example .env
make doctor   # which vars are set (no secrets printed)
```

| Mode | Settings |
|------|----------|
| **Mock** | `USE_MOCK_PROVIDERS=true` (default in `.env.example`) |
| **Real** | `USE_MOCK_PROVIDERS=false`, `TTS_PROVIDER=gemini`, `GEMINI_API_KEY`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` |

Keys: [Google AI Studio](https://aistudio.google.com) (Gemini TTS), Cloudflare → Workers AI (FLUX).

**Optional in `.env`:**

| Variable | Use |
|----------|-----|
| `MUSIC_FILE=/path/to.wav` | Your music (e.g. ACE-Step from Kaggle) instead of mock score |
| `END_CARD_IMAGE=/path/to.png` | Custom end card |
| `FFMPEG_PATH` / `FFPROBE_PATH` | Non-standard FFmpeg location |

`make film ARGS='--real'` turns off mocks and sets `TTS_PROVIDER=gemini` for that run (keys still required in `.env`).

### What this repo actually calls

| Piece | Mock | Real (current code) |
|-------|------|---------------------|
| Images | Pillow | Cloudflare FLUX |
| Voice | Silent WAV | Gemini TTS |
| Motion | Ken Burns | Ken Burns on FLUX stills (**Wan API not wired**) |
| Music | FFmpeg bed | Same, unless `MUSIC_FILE` set |

---

## Full pipeline

```bash
make film
make film ARGS='--real'
make film ARGS='--real --fresh'      # clears cache/index.json first
make film ARGS='--resume assemble' # after a failure
```

Outputs: `outputs/final/heritage_vertical.mp4`, `heritage_horizontal.mp4`, `outputs/subtitles/en.srt`, `logs/runs.jsonl`, `validation_report.json` after `make final-check`.

---

## Single stages

Run after `make install`:

| Command | Stage |
|---------|--------|
| `make validate` | Schema check |
| `make references` / `make images` | Reference sheet + keyframes |
| `make videos` | Clips |
| `make narration` / `make music` / `make subtitles` | Audio parts |
| **`make audio`** | narration + music + subtitles |
| `make validate-media` | Files exist before edit |
| **`make assemble`** | Final MP4s |
| `make final-check` | Deliverable report |

**Examples**

```bash
make audio && make assemble          # redo sound + export
make validate-media && make assemble # re-export only
```

Keep existing music: `source .venv/bin/activate && python3 main.py music --reuse`

**After editing `storyboard.json`**

| You changed | Then run |
|-------------|----------|
| `image_prompt` | `make images` → `make videos` → `make assemble` |
| `narration_text` | `make narration` → `make subtitles` → `make assemble` |
| `duration_seconds` | `make videos` → `make assemble` |

```bash
make status    # progress
make logs
```

Without Make: `.venv/bin/python3 main.py generate --from-stage videos`

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: jsonschema` | `make install`; use `make` or `.venv/bin/python3` |
| `ffmpeg not found` | Install FFmpeg; check `which ffmpeg` |
| `validate-media` fails | Run earlier stages (`make film` or `make audio` + `images` + `videos`) |
| Deleted files but stage says **Reused** | `rm -f cache/index.json` or `make film ARGS='--fresh'` |
| No real images/voice | `make doctor`; set Cloudflare + Gemini; use `make film ARGS='--real'` |
| Voice/picture out of sync | Set `duration_seconds` from measured TTS WAV; `make videos` → `make assemble` |

More context: `docs/FAILURES.md`.

---

## Project layout

| Path | Role |
|------|------|
| `storyboard.json` | Shots, prompts, durations |
| `run_film.py` / `main.py` | Full run vs single stage |
| `generators/`, `providers/`, `core/` | Implementation |
| `schemas/storyboard.schema.json` | Contract validation |

## Assignment documentation (required by brief)

These stay in **`docs/`** for grading (design, architecture, experiments, etc.). Running the pipeline needs **only this README** + `.env.example`.

| File | Purpose |
|------|---------|
| [`docs/DESIGN.md`](docs/DESIGN.md) | Audience, intent, user tests |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Stages, caching, contracts |
| [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md) | Hypothesis → change → result |
| [`docs/FAILURES.md`](docs/FAILURES.md) | Blockers and fixes |
| [`docs/COSTS.md`](docs/COSTS.md) | Latency and API usage |
| [`docs/ETHICS.md`](docs/ETHICS.md) | Consent, licences, labelling |

Also in repo: `README.md`, `storyboard.json`, `schemas/`, `logs/runs.jsonl`, pipeline code under `generators/` / `core/`.

## Ethics

Fictional illustrations; stock Gemini voice. See `docs/ETHICS.md`. Use platform **AI labels** when publishing.