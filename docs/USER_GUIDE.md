# User guide — run, test, logs, and what each part does

## I just want to run everything (normal user)

**One file:**

```bash
cd /path/to/heritage-film
source .venv/bin/activate   # after: make install once
python3 run_film.py
```

**Or one Make target:**

```bash
make film
```

That runs all stages in order. You do **not** need to run `references`, `images`, `videos`, etc. by hand unless you are debugging one step.

After a successful run, open:

- `outputs/final/heritage_vertical.mp4`
- `outputs/final/heritage_horizontal.mp4`

---

## How to test like a grader / new user

1. Clone the repo.
2. `make install` (or `pip install -r requirements.txt` in a venv).
3. Confirm FFmpeg: `ffmpeg -version`.
4. `make test` — quick checks (schema, cache, no AI cost).
5. `make film` — full mock film (~1–2 minutes).
6. `make status` — checklist of stages.
7. `python3 main.py final-check` — writes `outputs/final/validation_report.json`.

To prove **selective regeneration** (walkthrough):

1. Edit one shot’s `image_prompt` in `storyboard.json`.
2. Run `python3 run_film.py --resume images` (or `python main.py images` then later stages).
3. Check `cache/index.json` and logs — only that shot’s keyframe (and downstream) should regenerate.

---

## Logs — where they are and how to manage them

| What | Where |
|------|--------|
| Main log file | `logs/runs.jsonl` |
| Format | One JSON object per line: timestamp, level, stage, message, optional `extra` |

**View recent activity:**

```bash
python3 main.py logs          # last 30 lines, readable
python3 main.py logs -n 100   # more lines
python3 main.py logs --summary  # INFO / WARN / ERROR counts
```

**During a run:** the same messages print in the terminal (`[INFO] stage: message`).

**Reset logs (optional):** delete or rename `logs/runs.jsonl` before a clean run. Do not commit secrets into logs.

**Assignment note:** graders want **one line per model call** (model, seed, latency, cost). Today’s log is stage-oriented; when you wire Gemini/FLUX/Wan, extend logging in `providers/` to append those fields.

---

## Divided tasks (pipeline stages)

| Order | Stage | What it does | Main code |
|------:|-------|--------------|-----------|
| 1 | validate | Check `storyboard.json` against schema and 60–90s total | `validation/storyboard.py` |
| 2 | story | Story/script step (Gemini or mock) | `generators/story/generator.py` |
| 3 | references | Character/location reference PNGs | `generators/image/generator.py` |
| 4 | images | Per-shot keyframes | `generators/image/generator.py` |
| 5 | videos | Image-to-video clips | `generators/video/generator.py` |
| 6 | narration | TTS per shot | `generators/audio/narration.py` |
| 7 | music | Background track (ACE-Step / your WAV) | `generators/audio/music.py` |
| 8 | subtitles | English SRT | `generators/audio/subtitles.py` |
| — | audio | All three above (legacy one-shot) | `generators/audio/*.py` |
| 9 | validate-media | Files exist before edit | `validation/media.py` |
| 10 | assemble | Concat, ducking, burn subs, 9:16 + 16:9 | `generators/assembly/assembler.py` |
| 11 | final-check | MP4 aspect, duration, report | `validation/final_output.py` |

**See progress anytime:** `python3 main.py status`

---

## What each important file / folder does

```
heritage-film/
├── run_film.py              ← START HERE (runs all stages)
├── main.py                  ← Advanced: status, logs, single stages
├── Makefile                 ← make film | test | status | logs
├── config.py                ← Paths, env vars, output folders
├── storyboard.json          ← Contract: shots, prompts, narration, paths
├── schemas/storyboard.schema.json   ← Rules for storyboard.json
│
├── core/
│   ├── pipeline.py          ← Runs stages in order, resume support
│   ├── cache.py             ← Reuse artifacts when inputs unchanged
│   ├── dependency.py        ← Which fields affect which stage (regen map)
│   ├── registry.py          ← Picks mock vs real AI providers
│   ├── logger.py            ← Writes logs/runs.jsonl
│   ├── status.py            ← Task checklist for `main.py status`
│   └── log_view.py          ← `main.py logs`
│
├── generators/              ← One folder per pipeline feature
│   ├── story/               ← Script / story stage
│   ├── image/               ← References + keyframes
│   ├── video/               ← Clips
│   ├── audio/               ← Narration, music, subtitles
│   └── assembly/            ← FFmpeg final edit + end card
│
├── providers/               ← Gemini, FLUX, Wan, TTS, ACE-Step (+ mocks)
├── validation/              ← Storyboard, media, final MP4 checks
├── outputs/                 ← Generated images, audio, video (inspect here)
├── cache/                   ← index.json — what was reused vs regenerated
├── logs/                    ← runs.jsonl
├── tests/                   ← pytest (no GPU)
└── docs/                    ← ARCHITECTURE, DESIGN, assignment docs
```

---

## Commands cheat sheet

| Goal | Command |
|------|---------|
| Run full pipeline | `python3 run_film.py` or `make film` |
| Resume after failure | `python3 run_film.py --resume videos` |
| Task checklist | `python3 main.py status` |
| View logs | `python3 main.py logs` |
| Unit tests | `make test` |
| One stage only | `python3 main.py assemble` |
| Music only | `python3 main.py music` (always regenerates; use `--reuse` to keep cache) |
| Use your own music file | Set `MUSIC_FILE=/path/to/track.wav` in `.env`, then `python3 main.py music` |
| All audio (legacy) | `python3 main.py audio` |