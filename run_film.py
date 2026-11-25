#!/usr/bin/env python3
"""
Run the entire Heritage Short pipeline in one go.

  python3 run_film.py
  python3 run_film.py --resume videos

Named film (topic + output file):

  python3 run_film.py --real "Rock-hewn churches of Lalibela" lalibela.mp4

Makefile:

  make film ARGS='--real "Rock-hewn churches of Lalibela" lalibela.mp4'
"""

from __future__ import annotations

import argparse
import sys

from config import load_config
from core.film_job import configure_film_job, print_film_banner
from core.pipeline import Pipeline, stage_from_cli
from validation.storyboard import load_storyboard


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Make a heritage short film from storyboard.json")
    p.add_argument(
        "topic",
        nargs="?",
        help='Film subject, e.g. "Rock-hewn churches of Lalibela"',
    )
    p.add_argument(
        "output",
        nargs="?",
        help="Final vertical MP4 filename, e.g. lalibela.mp4",
    )
    p.add_argument(
        "--real",
        action="store_true",
        help="Use real FLUX images + Gemini TTS (needs .env keys)",
    )
    p.add_argument(
        "--fresh",
        action="store_true",
        help="Clear cache/index.json so narration/images regenerate",
    )
    p.add_argument(
        "--resume",
        metavar="STAGE",
        help="Resume from a pipeline stage",
    )
    return p


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--resume" and len(sys.argv) > 2:
        pipeline = Pipeline.create()
        ok = pipeline.run_all(from_stage=stage_from_cli(sys.argv[2]))
        return 0 if ok else 1

    args = build_parser().parse_args()
    cfg_pre = load_config()

    if args.topic and args.output:
        vertical, horizontal = configure_film_job(
            topic=args.topic,
            output_mp4=args.output,
            storyboard_path=cfg_pre.storyboard_path,
            use_real=args.real,
            fresh=args.fresh,
            cache_dir=cfg_pre.cache_dir,
        )
        print_film_banner(args.topic, vertical, horizontal, args.real)
    elif args.real or args.fresh:
        data = load_storyboard(cfg_pre.storyboard_path)
        topic = data.get("project", {}).get("topic", "Heritage short")
        configure_film_job(
            topic=topic,
            output_mp4=cfg_pre.final_vertical_filename,
            storyboard_path=cfg_pre.storyboard_path,
            use_real=args.real,
            fresh=args.fresh,
            cache_dir=cfg_pre.cache_dir,
        )

    pipeline = Pipeline.create()
    cfg = pipeline.config
    resume = stage_from_cli(args.resume) if args.resume else None
    ok = pipeline.run_all(from_stage=resume)

    if ok:
        print("\nDone.")
        print(f"  Vertical (9:16): {cfg.final_vertical_path()}")
        print(f"  Horizontal:      {cfg.final_horizontal_path()}")
        print("Logs: logs/runs.jsonl  |  Progress: python3 main.py status")
    elif pipeline.last_error:
        print(f"\nFailed at stage '{pipeline.last_error_stage}'")
        print(f"  Reason: {pipeline.last_error}")
        if pipeline.last_error_detail:
            print(f"  Detail: {pipeline.last_error_detail}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())