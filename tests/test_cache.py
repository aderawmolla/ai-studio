from pathlib import Path

from core.cache import ArtifactCache, fingerprint_payload
from core.dependency import shot_video_inputs, fingerprint


def test_fingerprint_stable():
    a = fingerprint_payload({"x": 1, "y": 2})
    b = fingerprint_payload({"y": 2, "x": 1})
    assert a == b


def test_cache_reuse(tmp_path: Path):
    cache = ArtifactCache(tmp_path)
    p = tmp_path / "artifact.txt"
    p.write_text("ok")
    fp = fingerprint({"k": "v"})
    cache.store("key1", fp, p, reason="test", stage="t")
    assert cache.lookup("key1", fp) is not None
    assert cache.lookup("key1", "other") is None


def test_shot_video_dependency():
    shot = {"shot_id": "s1", "video_prompt": "pan", "camera_movement": "pan", "duration_seconds": 5}
    fp = fingerprint(shot_video_inputs(shot, "/tmp/kf.png"))
    assert len(fp) == 64