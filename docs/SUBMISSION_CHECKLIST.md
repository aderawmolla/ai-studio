# Submission Checklist

| Assignment requirement | Status | Evidence |
|------------------------|--------|----------|
| Working Python pipeline | Done (mock mode) | `main.py`, `python main.py generate` |
| 60–90s film | Done (sample = 75s + 4s end card) | `final-check` report |
| 9:16 and 16:9 MP4 | Done | `outputs/final/*.mp4` |
| English subtitles | Done | `outputs/subtitles/en.srt` |
| Narration + music ducking | Done (mock audio) | `generators/assembly/assembler.py` |
| End card | Done (placeholder) | `generators/assembly/end_card.py` |
| Storyboard schema | Done | `schemas/storyboard.schema.json` |
| Caching / selective regen | Done | `core/cache.py`, `tests/test_cache.py` |
| Tests without API cost | Done | `pytest` |
| Real Gemini/FLUX/Wan/ACE | Pending | Provider stubs in `providers/` |
| Audience testing (2×3 people) | **You must run** | `docs/DESIGN.md` |
| 10 experiments | **You must record** | `docs/EXPERIMENTS.md` |
| Costs / ethics evidence | **You must record** | `docs/COSTS.md`, `docs/ETHICS.md` |