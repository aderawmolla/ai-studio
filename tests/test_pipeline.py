from core.dependency import REGENERATION_MAP
from core.pipeline import STAGE_ORDER, PipelineStage


def test_stage_order():
    assert STAGE_ORDER[0] == PipelineStage.VALIDATE
    assert STAGE_ORDER[-1] == PipelineStage.FINAL_CHECK


def test_end_card_before_assemble():
    i_ec = STAGE_ORDER.index(PipelineStage.END_CARD)
    i_asm = STAGE_ORDER.index(PipelineStage.ASSEMBLE)
    i_val = STAGE_ORDER.index(PipelineStage.VALIDATE_MEDIA)
    assert i_ec < i_val < i_asm


def test_regeneration_map_documents_video_prompt():
    assert "video" in REGENERATION_MAP["video_prompt"]