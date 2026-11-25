from core.dependency import REGENERATION_MAP
from core.pipeline import STAGE_ORDER, PipelineStage


def test_stage_order():
    assert STAGE_ORDER[0] == PipelineStage.VALIDATE
    assert STAGE_ORDER[-1] == PipelineStage.FINAL_CHECK


def test_regeneration_map_documents_video_prompt():
    assert "video" in REGENERATION_MAP["video_prompt"]