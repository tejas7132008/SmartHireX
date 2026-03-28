from pathlib import Path

from backend.reporting.report_builder import build_report_payload, save_report_bundle


def test_report_payload_and_files(tmp_path: Path) -> None:
    payload = build_report_payload(
        candidate_summary={"name": "Alex", "education": "BSc", "experience_years": 2},
        github_signals={"github_username": "alex", "repo_count": 3, "languages": ["Python"]},
        interview_state={
            "transcript": [
                {
                    "question": {"question": "How did you design X?", "focus_area": "architecture"},
                    "answer": "By balancing tradeoffs",
                    "evaluation": {"depth": 0.8},
                }
            ],
            "summary": {"avg_depth": 0.8},
        },
        ai_summary={"executive_summary": "Strong", "recommendation_reasoning": ["evidence"]},
        multi_agent_decision={
            "agents": {"tech_lead": {"score": 0.8, "reasoning": ["good"]}},
            "final_score": 0.8,
            "priority": "HIGH",
            "aggregator": {"weights": {"tech_lead": 1.0}},
        },
    )

    paths = save_report_bundle(job_id="job-1", report_payload=payload, root_dir=tmp_path)

    assert Path(paths["json_path"]).exists()
    assert Path(paths["pdf_path"]).exists()
