"""Pipeline orchestration with resume support."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from config import AppConfig, load_config
from core.api_errors import parse_api_error, technical_detail
from core.errors import StageAbort
from core.failure_report import print_failure_summary
from core.cache import ArtifactCache
from core.logger import RunLogger
from core.registry import ProviderRegistry, build_registry
from generators.assembly.assembler import run_assembly
from generators.audio.music import run_music
from generators.audio.narration import run_narration
from generators.audio.subtitles import run_subtitles
from generators.image.generator import run_keyframes, run_references
from generators.story.generator import run_story
from generators.video.generator import run_videos
from validation.final_output import validate_final_outputs, write_report
from validation.media import validate_media
from validation.storyboard import load_storyboard, save_storyboard, validate_storyboard


class PipelineStage(str, Enum):
    VALIDATE = "validate"
    STORY = "story"
    REFERENCES = "references"
    IMAGES = "images"
    VIDEOS = "videos"
    NARRATION = "narration"
    MUSIC = "music"
    SUBTITLES = "subtitles"
    AUDIO = "audio"  # legacy: runs narration + music + subtitles
    VALIDATE_MEDIA = "validate-media"
    ASSEMBLE = "assemble"
    FINAL_CHECK = "final-check"


STAGE_ORDER: list[PipelineStage] = [
    PipelineStage.VALIDATE,
    PipelineStage.STORY,
    PipelineStage.REFERENCES,
    PipelineStage.IMAGES,
    PipelineStage.VIDEOS,
    PipelineStage.NARRATION,
    PipelineStage.MUSIC,
    PipelineStage.SUBTITLES,
    PipelineStage.VALIDATE_MEDIA,
    PipelineStage.ASSEMBLE,
    PipelineStage.FINAL_CHECK,
]


@dataclass
class Pipeline:
    config: AppConfig
    log: RunLogger
    cache: ArtifactCache
    registry: ProviderRegistry
    last_error: str | None = field(default=None, init=False)
    last_error_detail: str | None = field(default=None, init=False)
    last_error_stage: str | None = field(default=None, init=False)

    @classmethod
    def create(cls) -> Pipeline:
        config = load_config()
        return cls(
            config=config,
            log=RunLogger(config.logs_dir),
            cache=ArtifactCache(config.cache_dir),
            registry=build_registry(config),
        )

    def _load(self):
        return load_storyboard(self.config.storyboard_path)

    def _save(self, data) -> None:
        save_storyboard(self.config.storyboard_path, data)

    def _record_failure(self, stage: str, message: str, detail: str | None = None) -> None:
        self.last_error = message
        self.last_error_detail = detail
        self.last_error_stage = stage
        self.log.error(
            stage,
            message,
            reason=message,
            detail=detail or message,
        )

    def _resume_hint(self, stage: PipelineStage) -> str:
        return f"python3 run_film.py --resume {stage.value}"

    def run_stage(self, stage: PipelineStage, *, force_music: bool = False) -> bool:
        try:
            data = self._load()
            if stage == PipelineStage.VALIDATE:
                result = validate_storyboard(data, self.config.schema_path)
                if not result.ok:
                    summary = result.errors[0] if result.errors else "Storyboard validation failed"
                    detail = "; ".join(result.errors[:8])
                    if len(result.errors) > 8:
                        detail += f"; …and {len(result.errors) - 8} more"
                    for e in result.errors:
                        self.log.error("validate", e)
                    self._record_failure("validate", summary, detail=detail)
                    return False
                self.log.info("validate", "Storyboard OK")
                return True

            if stage == PipelineStage.STORY:
                data = run_story(data, self.registry, self.log)
            elif stage == PipelineStage.REFERENCES:
                data = run_references(data, self.config, self.registry, self.cache, self.log)
            elif stage == PipelineStage.IMAGES:
                data = run_keyframes(data, self.config, self.registry, self.cache, self.log)
            elif stage == PipelineStage.VIDEOS:
                data = run_videos(data, self.config, self.registry, self.cache, self.log)
            elif stage == PipelineStage.NARRATION:
                data = run_narration(data, self.config, self.registry, self.cache, self.log)
            elif stage == PipelineStage.MUSIC:
                data = run_music(
                    data,
                    self.config,
                    self.registry,
                    self.cache,
                    self.log,
                    force=force_music,
                )
            elif stage == PipelineStage.SUBTITLES:
                data = run_subtitles(data, self.config, self.cache, self.log)
            elif stage == PipelineStage.AUDIO:
                data = run_narration(data, self.config, self.registry, self.cache, self.log)
                data = run_music(data, self.config, self.registry, self.cache, self.log)
                data = run_subtitles(data, self.config, self.cache, self.log)
            elif stage == PipelineStage.VALIDATE_MEDIA:
                report = validate_media(data, self.config)
                for w in report.warnings:
                    self.log.warn("validate-media", w)
                if not report.ok:
                    for e in report.errors:
                        self.log.error("validate-media", e)
                    return False
                self.log.info("validate-media", "Media OK")
                self._save(data)
                return True
            elif stage == PipelineStage.ASSEMBLE:
                data = run_assembly(data, self.config, self.cache, self.log, self.registry)
            elif stage == PipelineStage.FINAL_CHECK:
                report = validate_final_outputs(data, self.config)
                out_path = self.config.outputs_dir / "final" / "validation_report.json"
                write_report(out_path, report)
                if not report.ok:
                    for e in report.errors:
                        self.log.error("final-check", e)
                    return False
                self.log.info("final-check", "Final outputs OK", report=str(out_path))
                self._save(data)
                return True

            self._save(data)
            return True
        except StageAbort as exc:
            self._record_failure(stage.value, exc.reason, detail=exc.detail)
            return False
        except Exception as exc:
            reason, detail = parse_api_error(exc)
            self._record_failure(stage.value, reason, detail=detail or technical_detail(exc))
            return False

    def run_all(self, from_stage: PipelineStage | None = None) -> bool:
        self.last_error = None
        self.last_error_detail = None
        self.last_error_stage = None
        start_idx = 0
        if from_stage:
            start_idx = STAGE_ORDER.index(from_stage)
        for stage in STAGE_ORDER[start_idx:]:
            self.log.info("pipeline", f"Running stage {stage.value}")
            if not self.run_stage(stage):
                summary = self.last_error or f"Stage {stage.value} failed (see logs)"
                self.log.error("pipeline", f"Stage failed: {stage.value} — {summary}")
                print_failure_summary(
                    stage.value,
                    summary,
                    detail=self.last_error_detail,
                    logs_path=self.log.jsonl_path,
                    resume_hint=self._resume_hint(stage),
                )
                return False
        return True


def stage_from_cli(name: str) -> PipelineStage:
    if name == "audio":
        return PipelineStage.NARRATION
    try:
        return PipelineStage(name)
    except ValueError as exc:
        raise SystemExit(f"Unknown stage: {name}. Valid: {[s.value for s in PipelineStage]}") from exc