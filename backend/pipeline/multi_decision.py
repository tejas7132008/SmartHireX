from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from backend.services.llm_service import LLMService


@dataclass(frozen=True)
class AgentSpec:
    name: str
    weight: float
    rubric: str


class MultiAgentDecisionSystem:
    def __init__(self, llm_service: LLMService) -> None:
        self.llm_service = llm_service
        self.agent_specs = [
            AgentSpec(
                name="tech_lead",
                weight=0.45,
                rubric=(
                    "Evaluate technical competence, engineering depth, GitHub code signals, "
                    "problem-solving quality, and project complexity."
                ),
            ),
            AgentSpec(
                name="hr",
                weight=0.2,
                rubric=(
                    "Evaluate communication clarity, confidence, collaboration potential, "
                    "and structured articulation in interview answers."
                ),
            ),
            AgentSpec(
                name="manager",
                weight=0.35,
                rubric=(
                    "Evaluate ownership, delivery reliability, consistency under pressure, and "
                    "ability to convert plans into outcomes."
                ),
            ),
        ]

    async def evaluate(
        self,
        candidate_context: dict[str, Any],
        signals: dict[str, Any],
        interview_state: dict[str, Any],
    ) -> dict[str, Any]:
        transcript = list(interview_state.get("transcript") or [])

        agent_outputs: dict[str, dict[str, Any]] = {}
        weighted_sum = 0.0
        weight_total = 0.0

        async def _run_agent(spec: AgentSpec) -> tuple[AgentSpec, dict[str, Any]]:
            output = await self.llm_service.evaluate_hiring_agent(
                agent_name=spec.name,
                rubric=spec.rubric,
                candidate_context=candidate_context,
                transcript=transcript,
                signals=signals,
            )
            return spec, output

        # Run panel evaluations concurrently to cut end-to-end decision latency.
        results = await asyncio.gather(*(_run_agent(spec) for spec in self.agent_specs))

        for spec, output in results:
            normalized_score = self._clamp_ratio(output.get("score", 0.0))
            agent_outputs[spec.name] = {
                "score": normalized_score,
                "weight": spec.weight,
                "reasoning": output.get("reasoning", []),
                "strengths": output.get("strengths", []),
                "risks": output.get("risks", []),
            }
            weighted_sum += normalized_score * spec.weight
            weight_total += spec.weight

        final_score_ratio = 0.0 if weight_total == 0 else round(weighted_sum / weight_total, 4)
        final_score = round(final_score_ratio * 100.0, 2)
        priority = self._priority_from_score(final_score_ratio)

        return {
            "agents": agent_outputs,
            "final_score": final_score,
            "final_score_ratio": final_score_ratio,
            "priority": priority,
            "aggregator": {
                "weights": {spec.name: spec.weight for spec in self.agent_specs},
                "formula": "weighted_average(tech_lead, hr, manager)",
            },
        }

    @staticmethod
    def _priority_from_score(score: float) -> str:
        if score > 0.75:
            return "HIGH"
        if score > 0.5:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _clamp_ratio(value: Any) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, numeric))
