from pathlib import Path

from validation.storyboard import load_storyboard, validate_storyboard


def test_sample_storyboard_valid():
    root = Path(__file__).resolve().parents[1]
    data = load_storyboard(root / "storyboard.json")
    result = validate_storyboard(data, root / "schemas" / "storyboard.schema.json")
    assert result.ok, result.errors