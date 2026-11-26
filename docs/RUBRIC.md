# Grading criteria — evidence map (100 pts)

| Criterion | Pts | Primary evidence in this repo |
|-----------|----:|-------------------------------|
| Software engineering & reproducibility | 28 | `README.md`, `Makefile`, `tests/`, `schemas/`, `make film` (mock) |
| Documentation | 14 | `README.md`, `docs/*`, report PDF/HTML |
| Design thinking & audience | 14 | `docs/DESIGN.md`, `storyboard.json` (`reason`, audience fields) |
| Experimentation & iteration | 14 | `docs/EXPERIMENTS.md` (E01–E10+) |
| **Troubleshooting & persistence** | **14** | **`docs/FAILURES.md` (F01–F12)** + `docs/failure_log_excerpts.jsonl` |
| Measurement | 8 | `docs/COSTS.md`, `logs/runs.jsonl` (local), `make final-check` |
| Consent & labelling | 8 | `docs/ETHICS.md`, end card “Made with AI”, `make end-card` |

**Troubleshooting (start here if reviewing persistence):** Open [`FAILURES.md`](FAILURES.md) — numbered failure log with symptom → tried → fix → evidence. Redacted log lines in [`failure_log_excerpts.jsonl`](failure_log_excerpts.jsonl).

```bash
make install && make test && make film    # reproducibility
make logs -n 30                         # after any local run
```