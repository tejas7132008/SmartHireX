import asyncio

from backend.pipeline.interview import AdaptiveInterviewEngine, InterviewConfig


class FakeLLMService:
    async def generate_interview_question(self, candidate_context, transcript, question_index, previous_answer_eval):
        return {
            "question": f"Dynamic question {question_index}",
            "focus_area": "reasoning",
            "difficulty": "intermediate",
            "why_this_question": "probe deeper",
        }

    async def evaluate_interview_answer(self, candidate_context, question, answer, transcript):
        if len(transcript) < 2:
            return {
                "depth": 0.3,
                "clarity": 0.7,
                "confidence": 0.6,
                "follow_up_needed": True,
                "recommended_focus": "depth",
                "evaluation_notes": ["go deeper"],
            }
        return {
            "depth": 0.9,
            "clarity": 0.9,
            "confidence": 0.9,
            "follow_up_needed": False,
            "recommended_focus": "advanced",
            "evaluation_notes": ["strong"],
        }


def test_adaptive_interview_completes_after_min_questions() -> None:
    engine = AdaptiveInterviewEngine(
        llm_service=FakeLLMService(),
        config=InterviewConfig(min_questions=3, max_questions=5, depth_threshold=0.6),
    )

    state = asyncio.run(engine.start({"candidate": "x"}))
    assert state["current_question"]["question"]

    state = asyncio.run(engine.submit_answer(state, "Answer 1", {"candidate": "x"}))
    assert not state["completed"]

    state = asyncio.run(engine.submit_answer(state, "Answer 2", {"candidate": "x"}))
    assert not state["completed"]

    state = asyncio.run(engine.submit_answer(state, "Answer 3", {"candidate": "x"}))
    assert state["completed"]
    assert state["summary"]["question_count"] == 3
