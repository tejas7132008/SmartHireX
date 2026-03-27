from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Literal, Optional


Decision = Literal["strong_hire", "hire", "hold", "reject"]


@dataclass
class InterviewTurn:
    turn: int
    dimension: str
    difficulty: int
    question: str
    response: str
    response_quality: str
    response_score: float
    evaluation: Dict[str, float]
    evaluation_reasoning: str
    running_confidence: float


@dataclass
class GlobalHiringState:
    candidate: Dict[str, Any]
    scores: Dict[str, float] = field(default_factory=dict)
    interview_history: List[InterviewTurn] = field(default_factory=list)
    performance_trend: List[float] = field(default_factory=list)
    final_decision: Optional[Decision] = None
    reasoning_trace: List[str] = field(default_factory=list)
    stakeholder_decisions: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class HiringPipelineResult:
    candidate_summary: Dict[str, Any]
    talent_scores: Dict[str, float]
    interview_report: Dict[str, Any]
    stakeholder_decisions: Dict[str, Dict[str, Any]]
    final_decision: Decision
    confidence_score: float
    reasoning: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
