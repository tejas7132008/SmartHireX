import json
from pathlib import Path


def test_demo_candidates_file_has_exact_three_profiles():
    data_file = Path("data/demo_candidates.json")
    payload = json.loads(data_file.read_text(encoding="utf-8"))

    assert len(payload) == 3
    assert [item["profile"] for item in payload] == [
        "Hidden Gem",
        "Overrated Candidate",
        "Balanced Candidate",
    ]

    for row in payload:
        assert "candidate" in row
        assert "artifacts" in row
        assert "activity" in row
