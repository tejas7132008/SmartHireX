from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.services.llm_service import LLMService


@dataclass
class InterviewConfig:
    min_questions: int = 2
    max_questions: int = 3
    depth_threshold: float = 0.58


class AdaptiveInterviewEngine:
    def __init__(self, llm_service: LLMService, config: InterviewConfig | None = None) -> None:
        self.llm_service = llm_service
        self.config = config or InterviewConfig()

    async def start(self, candidate_context: dict[str, Any]) -> dict[str, Any]:
        first_question = await self.llm_service.generate_interview_question(
            candidate_context=candidate_context,
            transcript=[],
            question_index=1,
            previous_answer_eval=None,
        )
        return {
            "current_question": first_question,
            "transcript": [],
            "question_count": 1,
            "min_questions": self.config.min_questions,
            "max_questions": self.config.max_questions,
            "completed": False,
            "summary": None,
        }

    async def submit_answer(
        self,
        state: dict[str, Any],
        answer: str,
        candidate_context: dict[str, Any],
    ) -> dict[str, Any]:
        cleaned = answer.strip()
        if not cleaned:
            raise ValueError("Interview answer cannot be empty")
        if state.get("completed"):
            raise ValueError("Interview is already completed")

        current_question = state.get("current_question")
        if not current_question or not isinstance(current_question, dict):
            raise RuntimeError("Interview current question is missing")

        transcript = list(state.get("transcript") or [])
        evaluation = await self.llm_service.evaluate_interview_answer(
            candidate_context=candidate_context,
            question=str(current_question.get("question", "")),
            answer=cleaned,
            transcript=transcript,
        )

        transcript.append(
            {
                "question": current_question,
                "answer": cleaned,
                "evaluation": evaluation,
            }
        )

        answered_count = len(transcript)
        should_continue = self._should_continue(answered_count, evaluation)

        if should_continue:
            next_question = await self.llm_service.generate_interview_question(
                candidate_context=candidate_context,
                transcript=transcript,
                question_index=answered_count + 1,
                previous_answer_eval=evaluation,
            )
            return {
                **state,
                "current_question": next_question,
                "transcript": transcript,
                "question_count": answered_count + 1,
                "completed": False,
                "summary": None,
            }

        return {
            **state,
            "current_question": None,
            "transcript": transcript,
            "question_count": answered_count,
            "completed": True,
            "summary": self._summarize(transcript),
        }

    def _should_continue(self, answered_count: int, evaluation: dict[str, Any]) -> bool:
        if answered_count < self.config.min_questions:
            return True
        if answered_count >= self.config.max_questions:
            return False

        depth = float(evaluation.get("depth", 0.0))
        follow_up_needed = bool(evaluation.get("follow_up_needed", False))
        return follow_up_needed or depth < self.config.depth_threshold

    @staticmethod
    def _summarize(transcript: list[dict[str, Any]]) -> dict[str, Any]:
        if not transcript:
            return {
                "avg_depth": 0.0,
                "avg_clarity": 0.0,
                "avg_confidence": 0.0,
                "question_count": 0,
            }

        total_depth = 0.0
        total_clarity = 0.0
        total_confidence = 0.0

        for turn in transcript:
            evaluation = turn.get("evaluation") or {}
            total_depth += float(evaluation.get("depth", 0.0))
            total_clarity += float(evaluation.get("clarity", 0.0))
            total_confidence += float(evaluation.get("confidence", 0.0))

        count = len(transcript)
        return {
            "avg_depth": round(total_depth / count, 3),
            "avg_clarity": round(total_clarity / count, 3),
            "avg_confidence": round(total_confidence / count, 3),
            "question_count": count,
        }
