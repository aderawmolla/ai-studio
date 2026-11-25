# Heritage Short — AI Content Generation Pipeline

**10 Academy — AI-Content Generation: The Heritage Short**

Orchestrates `storyboard.json` → keyframes, clips, Amharic narration, music, English subtitles, and dual-aspect MP4. Current film: **The Smile That Carried Him**.

## Quick start

```bash
cd heritage-film
make install
source .venv/bin/activate
make film                    # mock providers (no API keys)
make film ARGS='--real'    # FLUX images + Gemini TTS + Ken Burns clips
make test
```

Requires **FFmpeg** on `PATH`. Copy **`.env.example`** → **`.env`** for real AI (see [`docs/SETUP.md`](docs/SETUP.md)).

```bash
python3 main.py status
python3 main.py logs -n 30
python3 run_film.py --resume assemble   # after a failure
```

**Outputs**

- `outputs/final/heritage_vertical.mp4` (9:16)
- `outputs/final/heritage_horizontal.mp4` (16:9 reframe)
- `outputs/subtitles/en.srt`
- `logs/runs.jsonl` — every model call (`extra.type: model_call`)

## CLI stages

| Command | Purpose |
|---------|---------|
| `validate` | JSON Schema + duration rules |
| `references` / `images` | FLUX reference sheet + keyframes |
| `videos` | Clips (Ken Burns or mock Wan) |
| `narration` / `music` / `subtitles` | Audio + English SRT |
| `assemble` | Concat, ducking, burn-in subs, exports |
| `final-check` | Deliverable validation report |
| `generate` | Full pipeline; `--from-stage` to resume |

## Layout

| Path | Role |
|------|------|
| `storyboard.json` | Contract: shots, prompts, paths, music |
| `schemas/storyboard.schema.json` | Validation |
| `generators/`, `providers/`, `core/` | Pipeline implementation |
| `docs/` | Assignment documentation |

## Documentation

| File | Purpose |
|------|---------|
| [`docs/SETUP.md`](docs/SETUP.md) | API keys and `.env` |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Stages, caching, providers |
| [`docs/DESIGN.md`](docs/DESIGN.md) | Audience, intent, user tests |
| [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md) | Hypothesis → result log |
| [`docs/FAILURES.md`](docs/FAILURES.md) | Blockers and fixes |
| [`docs/COSTS.md`](docs/COSTS.md) | Latency and API usage |
| [`docs/ETHICS.md`](docs/ETHICS.md) | Consent, licences, labelling |

## Submission checklist

| Item | Status |
|------|--------|
| One command (`make film`) | ✓ |
| Schema + caching + `runs.jsonl` | ✓ |
| Real TTS + FLUX (with `.env`) | ✓ |
| Wan / ACE in Python providers | Stubs; Ken Burns + mock/import music |
| User tests in DESIGN.md | **Fill tables before submit** |
| Report PDF (Assignment 1) | **You write separately** |
| Film + walkthrough + post (Assignment 2) | **Upload / link separately** |

## Ethics

Fictional illustrated characters; stock Gemini voice. See [`docs/ETHICS.md`](docs/ETHICS.md). Enable platform AI labels when publishing.