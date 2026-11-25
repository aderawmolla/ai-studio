#!/usr/bin/env python3
"""
Run the entire Heritage Short pipeline in one go.

Normal users: use only this file (or `make film`).

  python3 run_film.py           # full run from the start
  python3 run_film.py --resume videos   # continue from the videos stage
"""

from __future__ import annotations

import sys

from core.pipeline import Pipeline, stage_from_cli


def main() -> int:
    resume = None
    if len(sys.argv) > 1:
        if sys.argv[1] in ("-h", "--help"):
            print(__doc__)
            return 0
        if sys.argv[1] == "--resume" and len(sys.argv) > 2:
            resume = stage_from_cli(sys.argv[2])
        else:
            print("Usage: python3 run_film.py [--resume STAGE]")
            print("Stages: validate, story, references, images, videos, audio, validate-media, assemble, final-check")
            return 2

    pipeline = Pipeline.create()
    ok = pipeline.run_all(from_stage=resume)
    if ok:
        print("\nDone. Watch outputs/final/heritage_vertical.mp4 and heritage_horizontal.mp4")
        print("Logs: logs/runs.jsonl  |  Progress: python main.py status")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())