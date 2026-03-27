import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.autonomous.orchestrator import OrchestratorAgent


def main() -> None:
    demo_file = REPO_ROOT / "data" / "demo_candidates.json"

    with demo_file.open("r", encoding="utf-8") as f:
        demo_candidates = json.load(f)

    print("=" * 88)
    print("SmartHireX Demo Runner")
    print("=" * 88)

    for idx, row in enumerate(demo_candidates, start=1):
        payload = {
            "candidate": row["candidate"],
            "artifacts": row["artifacts"],
            "activity": row["activity"],
        }

        orchestrator = OrchestratorAgent(seed=100 + idx)
        result = orchestrator.run(
            {
                **payload["candidate"],
                "artifacts": payload["artifacts"],
                "activity": payload["activity"],
            }
        )

        print("\n" + "-" * 88)
        print(f"Candidate {idx}: {row['profile']} ({row['candidate']['name']})")
        print("-" * 88)
        print("Talent scores:")
        print(json.dumps(result["talent_scores"], indent=2))
        print("\nInterview report (summary):")
        interview_report = {
            "turn_count": result["interview_report"]["turn_count"],
            "final_confidence": result["interview_report"]["final_confidence"],
            "performance_trend": result["interview_report"]["performance_trend"],
        }
        print(json.dumps(interview_report, indent=2))
        print("\nStakeholder decisions:")
        print(json.dumps(result["stakeholder_decisions"], indent=2))
        print("\nFinal decision:", result["final_decision"])
        print("Confidence score:", result["confidence_score"])


if __name__ == "__main__":
    main()
