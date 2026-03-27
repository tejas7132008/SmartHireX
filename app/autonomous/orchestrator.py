from __future__ import annotations

import logging
import random
from typing import Any, Dict, Optional

from .agents import CandidateDiscoveryAgent, DecisionAgent, EvaluationAgent, InterviewAgent
from .config import SmartHireXConfig, load_config
from .models import GlobalHiringState, HiringPipelineResult
from .validation import validate_candidate_payload


logger = logging.getLogger("smarthirex")


class OrchestratorAgent:
    """Coordinates all autonomous hiring stages and owns the global state."""

    def __init__(self, seed: Optional[int] = None, config: Optional[SmartHireXConfig] = None):
        self.config = config or load_config()

        reproducibility_cfg = self.config.anti_static["reproducibility"]
        if reproducibility_cfg["enabled"] and reproducibility_cfg["use_seed"]:
            if seed is None:
                raise ValueError("Seed is required because reproducibility.use_seed is enabled in config")
        self.rng = random.Random(seed)

        self.discovery_agent = CandidateDiscoveryAgent(self.rng, self.config)
        self.interview_agent = InterviewAgent(self.rng, self.config)
        self.evaluation_agent = EvaluationAgent(self.rng, self.config)
        self.decision_agent = DecisionAgent(self.rng, self.config)

    def analyze_candidate(self, state: GlobalHiringState) -> Dict[str, Any]:
        logger.info("[SmartHireX] Analyzing candidate...")
        summary = self.discovery_agent.run(state)
        state.reasoning_trace.append("OrchestratorAgent: candidate analysis completed.")
        return summary

    def run_interview(self, state: GlobalHiringState) -> Dict[str, Any]:
        logger.info("[SmartHireX] Running adaptive interview...")
        report = self.interview_agent.run_loop(state, self.evaluation_agent)
        state.reasoning_trace.append("OrchestratorAgent: interview loop completed.")
        return report

    def finalize_decision(self, state: GlobalHiringState) -> Dict[str, Any]:
        logger.info("[SmartHireX] Final decision generated.")
        final_decision, stakeholder_decisions = self.decision_agent.run(state)
        state.reasoning_trace.append("OrchestratorAgent: decision simulation completed.")
        return {
            "final_decision": final_decision,
            "stakeholder_decisions": stakeholder_decisions,
        }

    def run(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("[SmartHireX] Starting full autonomous hiring pipeline.")
        validate_candidate_payload(candidate, self.config)
        state = GlobalHiringState(candidate=candidate)
        state.reasoning_trace.append("OrchestratorAgent: starting autonomous hiring pipeline.")

        candidate_summary = self.analyze_candidate(state)
        interview_report = self.run_interview(state)
        decision_bundle = self.finalize_decision(state)

        confidence_score = round(interview_report.get("final_confidence", 0.0), 3)
        state.reasoning_trace.append(f"OrchestratorAgent: final confidence score={confidence_score}.")

        result = HiringPipelineResult(
            candidate_summary=candidate_summary,
            talent_scores=state.scores,
            interview_report=interview_report,
            stakeholder_decisions=decision_bundle["stakeholder_decisions"],
            final_decision=decision_bundle["final_decision"],
            confidence_score=confidence_score,
            reasoning=state.reasoning_trace,
        )
        return result.to_dict()
