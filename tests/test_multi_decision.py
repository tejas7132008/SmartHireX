import asyncio

from backend.pipeline.multi_decision import MultiAgentDecisionSystem


class FakeLLMService:
    def __init__(self, scores):
        self.scores = scores

    async def evaluate_hiring_agent(self, agent_name, rubric, candidate_context, transcript, signals):
        return {
            "score": self.scores[agent_name],
            "reasoning": [f"{agent_name} reasoning"],
            "risks": [],
            "strengths": ["signal quality"],
        }


def test_multi_agent_weighted_priority_high() -> None:
    decision = MultiAgentDecisionSystem(
        llm_service=FakeLLMService(
            {
                "tech_lead": 0.9,
                "hr": 0.8,
                "manager": 0.85,
            }
        )
    )

    result = asyncio.run(
        decision.evaluate(
            candidate_context={"name": "A"},
            signals={"skill_score": 90},
            interview_state={"transcript": []},
        )
    )

    assert result["priority"] == "HIGH"
    assert result["final_score"] > 75
    assert result["final_score_ratio"] > 0.75
    assert set(result["agents"].keys()) == {"tech_lead", "hr", "manager"}
