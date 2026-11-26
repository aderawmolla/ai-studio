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
cd ai-studio
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
| `END_CARD_IMAGE=/path/to.png` | Custom end card art (`Made with AI` bar added in code) |
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
| **`make end-card`** | End card PNG + `end_card.mp4` (`outputs/end_card/`) |
| `make validate-media` | Files exist before edit (includes end card) |
| **`make assemble`** | Final MP4s (requires `make end-card` first) |
| `make final-check` | Deliverable report |

**Examples**

```bash
make audio && make end-card && make assemble   # redo sound + card + export
make end-card && make assemble                 # new card only, then export
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

### End card (`Made with AI`)

End card assets are **only** created by **`make end-card`** (not during `make assemble`).

| Output | Path |
|--------|------|
| Still + disclosure bar | `outputs/end_card/end_card.png` |
| 4s clip appended in edit | `outputs/end_card/end_card.mp4` |

```bash
make end-card      # FLUX/placeholder + “Made with AI” + clip
make assemble      # concat shots + end_card.mp4 → finals (re-runs when end card files change)

If `assemble` still says **Reused final outputs**, delete finals and cache for assembly:

```bash
rm -f outputs/final/heritage_vertical.mp4 outputs/final/heritage_horizontal.mp4
python3 -c "import json; p='cache/index.json'; i=json.load(open(p)); i.pop('assembly:final',None); json.dump(i,open(p,'w'),indent=2)"
make assemble
```
```

Full pipeline order includes `end-card` after subtitles and before `validate-media`.

**Storyboard:** `project.end_card_prompt` (FLUX art, no text), `final.end_card_text` (default `Made with AI`).

**Reuse your own hills art (no FLUX call):**

```bash
cp /path/to/hills.png outputs/end_card/end_card_art.png
make end-card
make assemble
```

CLI: `.venv/bin/python3 main.py end-card`

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: jsonschema` | `make install`; use `make` or `.venv/bin/python3` |
| `ffmpeg not found` | Install FFmpeg; check `which ffmpeg` |
| `validate-media` fails | Run earlier stages (`make film` or `make audio` + `images` + `videos`) |
| Deleted files but stage says **Reused** | `rm -f cache/index.json` or `make film ARGS='--fresh'` |
| No real images/voice | `make doctor`; set Cloudflare + Gemini; use `make film ARGS='--real'` |
| End card is black/brown placeholder, not hills | Cloudflare **429** — wait and `make end-card` again, or `END_CARD_IMAGE` / `end_card_art.png` |
| Voice/picture out of sync | Set `duration_seconds` from measured TTS WAV; `make videos` → `make assemble` |
| `assemble` / `validate-media`: end card missing | Run `make end-card` first |

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

**Grading criteria (100 pts):** software engineering & reproducibility (28), documentation (14), design & audience (14), experimentation (14), troubleshooting (14), measurement (8), consent & labelling (8). See **[`docs/RUBRIC.md`](docs/RUBRIC.md)** for a checklist and where each piece of evidence lives in the repo.

| File | Purpose |
|------|---------|
| [`docs/RUBRIC.md`](docs/RUBRIC.md) | Rubric → evidence map (start here for grading) |
| [`docs/DESIGN.md`](docs/DESIGN.md) | Audience, intent, user tests |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Stages, caching, contracts |
| [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md) | Hypothesis → change → result |
| [`docs/FAILURES.md`](docs/FAILURES.md) | Blockers and fixes |
| [`docs/COSTS.md`](docs/COSTS.md) | Latency and API usage |
| [`docs/ETHICS.md`](docs/ETHICS.md) | Consent, licences, labelling |

Also in repo: `README.md`, `storyboard.json`, `schemas/`, `logs/runs.jsonl`, pipeline code under `generators/` / `core/`.

## Ethics

Fictional illustrations; stock Gemini voice. See `docs/ETHICS.md`. Use platform **AI labels** when publishing.
