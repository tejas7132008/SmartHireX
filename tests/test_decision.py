from backend.pipeline.decision import decide


def test_decision_high_priority() -> None:
    result = decide(
        {
            "skill_score": 90,
            "project_score": 85,
            "activity_score": 75,
            "communication_score": 80,
            "analysis_rationale": ["Strong technical depth"],
        }
    )

    assert result["priority"] == "HIGH"
    assert result["final_score"] >= 75
    assert len(result["reasoning"]) >= 5


def test_decision_low_priority() -> None:
    result = decide(
        {
            "skill_score": 20,
            "project_score": 25,
            "activity_score": 15,
            "communication_score": 30,
            "analysis_rationale": [],
        }
    )

    assert result["priority"] == "LOW"
    assert result["final_score"] < 50
