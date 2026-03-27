import json
from pathlib import Path

from app.autonomous.orchestrator import OrchestratorAgent


def _load_demo():
    return json.loads(Path("data/demo_candidates.json").read_text(encoding="utf-8"))


def test_hidden_gem_should_be_hired():
    demo = _load_demo()
    hidden = demo[0]
    payload = {
        **hidden["candidate"],
        "artifacts": hidden["artifacts"],
        "activity": hidden["activity"],
    }
    out = OrchestratorAgent(seed=101).run(payload)
    assert out["final_decision"] in {"hire", "strong_hire"}


def test_overrated_should_be_rejected_or_hold():
    demo = _load_demo()
    overrated = demo[1]
    payload = {
        **overrated["candidate"],
        "artifacts": overrated["artifacts"],
        "activity": overrated["activity"],
    }
    out = OrchestratorAgent(seed=102).run(payload)
    assert out["final_decision"] in {"reject", "hold"}


def test_balanced_should_be_hold_or_hire():
    demo = _load_demo()
    balanced = demo[2]
    payload = {
        **balanced["candidate"],
        "artifacts": balanced["artifacts"],
        "activity": balanced["activity"],
    }
    out = OrchestratorAgent(seed=103).run(payload)
    assert out["final_decision"] in {"hold", "hire", "strong_hire"}
