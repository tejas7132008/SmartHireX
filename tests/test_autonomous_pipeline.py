from app.autonomous.orchestrator import OrchestratorAgent


def _candidate_payload():
    return {
        "name": "Asha Karim",
        "target_role": "Senior ML Engineer",
        "years_experience": 6,
        "skills": ["python", "pytorch", "mlops", "feature engineering"],
        "projects": [
            "fraud detection with real-time scoring",
            "recommendation ranking optimization",
        ],
        "artifacts": [
            "Implemented feature store consistency checks",
            "Published a postmortem on model rollback",
        ],
        "activity": {
            "commits_per_week": 10,
            "projects_completed": 4,
            "open_source_contributions": 1,
        },
    }


def _minimal_candidate_payload():
    return {
        "name": "Rahul",
        "education": "B.Tech CSE",
        "skills": ["Python", "Data Structures"],
        "projects": [
            "Built a chat application using sockets",
            "Solved 300+ DSA problems",
        ],
    }


def test_pipeline_runs_end_to_end():
    orchestrator = OrchestratorAgent(seed=42)
    output = orchestrator.run(_candidate_payload())

    expected_keys = {
        "candidate_summary",
        "talent_scores",
        "interview_report",
        "stakeholder_decisions",
        "final_decision",
        "confidence_score",
        "reasoning",
    }
    assert expected_keys.issubset(output.keys())

    assert output["interview_report"]["turn_count"] >= 3
    assert len(output["interview_report"]["turns"]) == output["interview_report"]["turn_count"]
    assert len(output["talent_scores"]) >= 6
    assert "recruiter" in output["stakeholder_decisions"]
    assert "hiring_manager" in output["stakeholder_decisions"]
    assert "tech_lead" in output["stakeholder_decisions"]

    first_turn = output["interview_report"]["turns"][0]
    assert "evaluation" in first_turn
    assert "correctness" in first_turn["evaluation"]
    assert "thinking" in first_turn["evaluation"]
    assert "clarity" in first_turn["evaluation"]
    assert "consistency" in first_turn["evaluation"]


def test_pipeline_is_dynamic_with_seed_change():
    payload = _candidate_payload()

    out_seed_1 = OrchestratorAgent(seed=1).run(payload)
    out_seed_2 = OrchestratorAgent(seed=2).run(payload)

    assert out_seed_1["interview_report"]["turns"] != out_seed_2["interview_report"]["turns"]


def test_same_seed_same_output():
    payload = _candidate_payload()
    out_1 = OrchestratorAgent(seed=11).run(payload)
    out_2 = OrchestratorAgent(seed=11).run(payload)

    assert out_1 == out_2


def test_candidate_only_input_is_sufficient():
    output = OrchestratorAgent(seed=3).run(_minimal_candidate_payload())
    assert output["candidate_summary"]["name"] == "Rahul"
    assert output["interview_report"]["turn_count"] >= 3


def test_artifacts_and_activity_enrich_candidate_summary():
    enriched = OrchestratorAgent(seed=9).run(_candidate_payload())
    minimal = OrchestratorAgent(seed=9).run(_minimal_candidate_payload())

    assert enriched["candidate_summary"]["artifacts_count"] > 0
    assert enriched["candidate_summary"]["initial_signal_strength"] >= minimal["candidate_summary"]["initial_signal_strength"]
