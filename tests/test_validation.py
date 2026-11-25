from pathlib import Path

from validation.storyboard import validate_duration_budget, load_storyboard


def test_duration_budget_rejects_short_film():
    root = Path(__file__).resolve().parents[1]
    data = load_storyboard(root / "storyboard.json")
    for shot in data["shots"]:
        shot["duration_seconds"] = 5
    result = validate_duration_budget(data)
    assert not result.ok