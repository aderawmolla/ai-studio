# Heritage Short — AI Content Generation Pipeline

Python application for **AI-Content Generation: The Heritage Short** (10 Academy). It orchestrates storyboard-driven stages from script to dual-aspect MP4 deliverables, with **mock providers** for local reproduction without API keys.

## Quick start (normal user — one command)

```bash
cd heritage-film
make install          # once: venv + dependencies
source .venv/bin/activate
make film             # runs the entire pipeline (mock or per .env)

# Named output + real FLUX + Gemini TTS:
make film ARGS='--real --fresh "Rock-hewn churches of Lalibela" lalibela.mp4'
# → outputs/final/lalibela.mp4 and lalibela_16x9.mp4

# same without Make:
python3 run_film.py --real --fresh "Rock-hewn churches of Lalibela" lalibela.mp4
```

Requires **FFmpeg** on PATH. See **`docs/USER_GUIDE.md`** for testing, logs, task checklist, and file map.

```bash
python3 main.py status   # which stages are done
python3 main.py logs       # tail logs/runs.jsonl
make test                  # pytest, no AI cost
```

Outputs:

- `outputs/final/heritage_vertical.mp4` (9:16)
- `outputs/final/heritage_horizontal.mp4` (16:9, reframed)
- `outputs/subtitles/en.srt`
- `outputs/final/validation_report.json`

## CLI

| Command | Purpose |
|---------|---------|
| `validate` | JSON Schema + duration rules |
| `story` | Story stage (mock Gemini) |
| `references` | Location/character reference images |
| `images` | Shot keyframes |
| `videos` | TI2V clips (mock Wan) |
| `audio` | Narration, music, English subtitles |
| `validate-media` | Pre-assembly checks |
| `assemble` | FFmpeg concat, ducking, subs, 16:9 reframe |
| `final-check` | Deliverable validation |
| `generate` | Full pipeline (`--from-stage` to resume) |

## Configuration

- `storyboard.json` — central contract (see `schemas/storyboard.schema.json`)
- `config.py` — paths and env vars
- Copy `.env.example` to `.env` for secrets — see **`docs/ENV_MAP.md`** (which var → which stage)

Set `USE_MOCK_PROVIDERS=false` and provide API keys to wire Gemini, FLUX, Wan, and ACE-Step (stubs raise `NotImplementedError` until you implement them per current vendor docs).

## Project layout

See `docs/ARCHITECTURE.md` and `docs/PROJECT_SPEC.md`.

## Tests

```bash
pytest -q
```

## Documentation (assignment)

| Doc | Purpose |
|-----|---------|
| `docs/ASSIGNMENT_BRIEF.md` | Requirements (paste official brief when available) |
| `docs/SUBMISSION_CHECKLIST.md` | Traceability |
| `docs/DESIGN.md`, `EXPERIMENTS.md`, etc. | Fill with your real process |

## Ethics

Mock mode uses synthetic media only. For production runs, disclose AI-generated content and document model licenses in `docs/ETHICS.md`.