"""Core orchestration for the Heritage Short pipeline."""

__all__ = ["Pipeline", "PipelineStage"]


def __getattr__(name: str):
    if name in ("Pipeline", "PipelineStage"):
        from core.pipeline import Pipeline, PipelineStage

        return Pipeline if name == "Pipeline" else PipelineStage
    raise AttributeError(name)