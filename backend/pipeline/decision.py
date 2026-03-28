from __future__ import annotations


def decide(signals: dict) -> dict:
    final_score = (
        float(signals["skill_score"]) * 0.4
        + float(signals["project_score"]) * 0.3
        + float(signals["activity_score"]) * 0.2
        + float(signals["communication_score"]) * 0.1
    )
    rounded_score = round(final_score, 2)

    if rounded_score >= 75:
        priority = "HIGH"
    elif rounded_score >= 50:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    reasoning = [
        f"Skill score contributed {signals['skill_score']:.2f} with 40% weight.",
        f"Project score contributed {signals['project_score']:.2f} with 30% weight.",
        f"GitHub activity score contributed {signals['activity_score']:.2f} with 20% weight.",
        f"Communication score contributed {signals['communication_score']:.2f} with 10% weight.",
    ]

    for item in signals.get("analysis_rationale", []):
        reasoning.append(item)

    return {
        "final_score": rounded_score,
        "priority": priority,
        "reasoning": reasoning,
    }
