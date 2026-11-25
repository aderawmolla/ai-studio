# Project Specification — Heritage Short Pipeline

## Requirements traceability (summary)

| ID | Requirement | Implementation | Evidence |
|----|-------------|----------------|----------|
| R1 | 60–90s dual-aspect MP4 | `generators/assembly/assembler.py`, `validation/final_output.py` | `outputs/final/*.mp4`, `final-check` report |
| R2 | Storyboard contract | `schemas/storyboard.schema.json`, `storyboard.json` | `validate` command |
| R3 | Staged workflow | `core/pipeline.py`, `main.py` | CLI commands |
| R4 | Caching / selective regen | `core/cache.py`, `core/dependency.py` | `tests/test_cache.py` |
| R5 | Provider abstraction | `providers/base.py`, `providers/mock.py` | Mock `generate` run |
| R6 | Media validation | `validation/media.py` | `validate-media` |
| R7 | Documentation | `docs/*`, `README.md` | Submission checklist |
| R8 | Automated tests | `tests/` | `pytest` |

See `docs/SUBMISSION_CHECKLIST.md` for the full mapping.

## Sample heritage project

Default configuration targets **Lalibela rock-hewn churches (Ethiopia)** — UNESCO World Heritage, suitable for a short educational film.

## Execution modes

- `USE_MOCK_PROVIDERS=true` (default): no API keys; synthetic media via FFmpeg/Pillow.
- `USE_MOCK_PROVIDERS=false`: requires configured keys and optional GPU services (see `.env.example`).