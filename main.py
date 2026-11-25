#!/usr/bin/env python3
"""CLI for the Heritage Short AI production pipeline."""

from __future__ import annotations

import argparse
import sys

from config import load_config
from core.log_view import count_log_levels, tail_runs_jsonl
from core.pipeline import Pipeline, PipelineStage, stage_from_cli
from core.credentials import format_credential_report, verify_kaggle_token
from core.status import format_status_report


def build_parser() -> argparse.ArgumentParser:
    stages = [s.value for s in PipelineStage]
    p = argparse.ArgumentParser(
        description="Heritage Short — advanced CLI (normal users: python3 run_film.py)",
    )
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show which pipeline tasks are done (checklist)")
    doctor = sub.add_parser("doctor", help="Show which .env credentials are set (no secrets printed)")
    doctor.add_argument(
        "--kaggle",
        action="store_true",
        help="Test KAGGLE_API_TOKEN against Kaggle API",
    )
    logs = sub.add_parser("logs", help="View recent run log lines")
    logs.add_argument("-n", type=int, default=30, help="Number of lines to show (default 30)")
    logs.add_argument("--summary", action="store_true", help="Count INFO/WARN/ERROR only")

    for cmd in stages:
        stage_p = sub.add_parser(cmd, help=f"Run stage only: {cmd}")
        if cmd == PipelineStage.MUSIC.value:
            stage_p.add_argument(
                "--reuse",
                action="store_true",
                help="Keep cache / existing background.wav (default: always regenerate)",
            )

    gen = sub.add_parser("generate", help="Same as run_film.py — full pipeline")
    gen.add_argument(
        "--from-stage",
        type=str,
        default=None,
        choices=stages,
        help="Resume from this stage",
    )
    sub.add_parser("film", help="Alias for generate — run all stages")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config()

    if args.command == "doctor":
        print(format_credential_report(config))
        if args.kaggle and config.kaggle_api_token:
            ok, msg = verify_kaggle_token(config.kaggle_api_token)
            print(msg)
            return 0 if ok else 1
        if args.kaggle and not config.kaggle_api_token:
            print("Set KAGGLE_API_TOKEN in .env first.")
            return 1
        return 0

    if args.command == "status":
        print(format_status_report(config.storyboard_path))
        return 0

    if args.command == "logs":
        path = config.logs_dir / "runs.jsonl"
        if args.summary:
            print(count_log_levels(path))
        else:
            print(tail_runs_jsonl(path, args.n))
        return 0

    pipeline = Pipeline.create()

    if args.command in ("generate", "film"):
        from_stage = getattr(args, "from_stage", None)
        from_stage = stage_from_cli(from_stage) if from_stage else None
        ok = pipeline.run_all(from_stage=from_stage)
        if not ok and pipeline.last_error:
            print(f"\nFailed at stage '{pipeline.last_error_stage}'")
            print(f"  Reason: {pipeline.last_error}")
            if pipeline.last_error_detail:
                print(f"  Detail: {pipeline.last_error_detail}")
        return 0 if ok else 1

    force_music = args.command == PipelineStage.MUSIC.value and not getattr(args, "reuse", False)
    ok = pipeline.run_stage(stage_from_cli(args.command), force_music=force_music)
    if not ok and pipeline.last_error:
        print(f"\nFailed at stage '{pipeline.last_error_stage}'")
        print(f"  Reason: {pipeline.last_error}")
        if pipeline.last_error_detail:
            print(f"  Detail: {pipeline.last_error_detail}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())