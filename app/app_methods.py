import chainlit as cl
import uuid
import asyncio
import logging
from pathlib import Path
from engine import engine
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

try:
    from app.autonomous.orchestrator import OrchestratorAgent
    from app.autonomous.config import load_config
except Exception:
    from autonomous.orchestrator import OrchestratorAgent
    from autonomous.config import load_config

try:
    from chainlit.server import app as chainlit_app
except Exception:
    chainlit_app = None

AGENT_KEY = "agent"
JUDGEMENT_HISTORY_KEY = "judgement_history"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("smarthirex")
STATIC_DIR = Path(__file__).resolve().parent / "static"
AUTONOMOUS_CONFIG = load_config()


class PipelineConfig(BaseModel):
    seed: int = Field(
        ...,
        description="Seed used for reproducible SmartHireX pipeline execution.",
    )


class HiringPipelineRequest(BaseModel):
    candidate: Dict[str, Any] = Field(
        ...,
        description="Candidate payload used by the autonomous hiring pipeline.",
    )
    config: PipelineConfig = Field(
        ...,
        description="SmartHireX runtime configuration for a single request.",
    )
    artifacts: Optional[List[str]] = Field(
        default=None,
        description="Optional work artifacts used as deeper technical evidence.",
    )
    activity: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional activity signals such as commits_per_week and open_source_contributions.",
    )


def _difficulty_label(final_difficulty: int) -> str:
    if final_difficulty >= 4:
        return "advanced"
    if final_difficulty <= 2:
        return "foundational"
    return "intermediate"


def _confidence_trend_label(performance_trend: List[float]) -> str:
    if len(performance_trend) < 2:
        return "stable"
    delta = performance_trend[-1] - performance_trend[0]
    if delta > 0.02:
        return "increasing"
    if delta < -0.02:
        return "decreasing"
    return "stable"


def _format_final_output(raw_result: Dict[str, Any], candidate_payload: Dict[str, Any]) -> Dict[str, Any]:
    scores = raw_result.get("talent_scores", {})
    interview = raw_result.get("interview_report", {})
    stakeholder_bundle = raw_result.get("stakeholder_decisions", {})

    return {
        "candidate_summary": {
            "name": candidate_payload.get("name", raw_result.get("candidate_summary", {}).get("name", "Unknown Candidate")),
            "education": candidate_payload.get("education", "Not specified"),
            "experience": float(candidate_payload.get("years_experience", raw_result.get("candidate_summary", {}).get("years_experience", 0))),
        },
        "talent_scores": {
            "skill": round(float(scores.get("skill", 0.0)) * 10, 1),
            "initiative": round(float(scores.get("initiative", 0.0)) * 10, 1),
            "consistency": round(float(scores.get("consistency", 0.0)) * 10, 1),
            "communication": round(float(scores.get("communication", 0.0)) * 10, 1),
        },
        "interview_report": {
            "turns": int(interview.get("turn_count", 0)),
            "final_difficulty": _difficulty_label(int(interview.get("final_difficulty", 3))),
            "confidence_trend": _confidence_trend_label(interview.get("performance_trend", [])),
        },
        "stakeholder_decisions": {
            role: details.get("decision", "hold")
            for role, details in stakeholder_bundle.items()
        },
        "final_decision": raw_result.get("final_decision", "hold"),
        "confidence_score": raw_result.get("confidence_score", 0.0),
        "reasoning": raw_result.get("reasoning", []),
    }


class CandidateOnlyRequest(BaseModel):
    candidate: Dict[str, Any]
    seed: int


if chainlit_app is not None:
    chainlit_app.add_middleware(
        CORSMiddleware,
        allow_origins=AUTONOMOUS_CONFIG.deployment["cors"]["allowed_origins"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @chainlit_app.get("/smarthirex")
    async def smarthirex_frontend():
        return FileResponse(STATIC_DIR / "smarthirex.html")

    @chainlit_app.post("/run-smarthirex-pipeline")
    async def run_hiring_pipeline(payload: HiringPipelineRequest):
        logger.info("[SmartHireX] Pipeline trigger received at /run-smarthirex-pipeline")
        orchestrator = OrchestratorAgent(seed=payload.config.seed, config=AUTONOMOUS_CONFIG)
        candidate_payload = dict(payload.candidate)
        if payload.artifacts is not None:
            candidate_payload["artifacts"] = payload.artifacts
        if payload.activity is not None:
            candidate_payload["activity"] = payload.activity
        raw_result = orchestrator.run(candidate_payload)
        return _format_final_output(raw_result, candidate_payload)

    @chainlit_app.post("/run-smarthirex-pipeline/analyze")
    async def analyze_candidate(payload: CandidateOnlyRequest):
        logger.info("[SmartHireX] Stage trigger received at /run-smarthirex-pipeline/analyze")
        orchestrator = OrchestratorAgent(seed=payload.seed, config=AUTONOMOUS_CONFIG)
        from app.autonomous.models import GlobalHiringState

        state = GlobalHiringState(candidate=dict(payload.candidate))
        return {
            "candidate_summary": orchestrator.analyze_candidate(state),
            "talent_scores": state.scores,
            "reasoning": state.reasoning_trace,
        }

    @chainlit_app.post("/run-smarthirex-pipeline/interview")
    async def interview_candidate(payload: CandidateOnlyRequest):
        logger.info("[SmartHireX] Stage trigger received at /run-smarthirex-pipeline/interview")
        orchestrator = OrchestratorAgent(seed=payload.seed, config=AUTONOMOUS_CONFIG)
        from app.autonomous.models import GlobalHiringState

        state = GlobalHiringState(candidate=dict(payload.candidate))
        orchestrator.analyze_candidate(state)
        interview_report = orchestrator.run_interview(state)
        return {
            "interview_report": interview_report,
            "talent_scores": state.scores,
            "reasoning": state.reasoning_trace,
        }

    @chainlit_app.post("/run-smarthirex-pipeline/decision")
    async def decision_candidate(payload: CandidateOnlyRequest):
        logger.info("[SmartHireX] Stage trigger received at /run-smarthirex-pipeline/decision")
        orchestrator = OrchestratorAgent(seed=payload.seed, config=AUTONOMOUS_CONFIG)
        from app.autonomous.models import GlobalHiringState

        state = GlobalHiringState(candidate=dict(payload.candidate))
        orchestrator.analyze_candidate(state)
        orchestrator.run_interview(state)
        decision = orchestrator.finalize_decision(state)
        return {
            "stakeholder_decisions": decision["stakeholder_decisions"],
            "final_decision": decision["final_decision"],
            "reasoning": state.reasoning_trace,
        }


async def refresh_rubric_sidebar(judgement_history: list):
    widget = cl.CustomElement(
        name="RubricWidget",
        props={"judgements": {"history": judgement_history}},
    )

    await cl.ElementSidebar.set_title("Belief")
    await cl.ElementSidebar.set_elements([widget], key=f"rubric-{uuid.uuid4()}")


async def thinking_spinner(message: cl.Message, interval: float = 0.6):
    dots = 0
    try:
        while True:
            suffix = "." * dots
            message.content = f"Thinking (this can take up to 60s){suffix}"
            await message.update()
            dots = (dots + 1) % 4  # "", ".", "..", "..."
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        return


@cl.on_chat_start
async def start():
    files = None
    while files is None:
        files = await cl.AskFileMessage(
            content="Welcome to SmartHireX. Please upload your resume to begin the interview simulation.",
            accept=["application/pdf"],
        ).send()

    text_file = files[0]
    agent = engine.construct_next_message(text_file.path)
    cl.user_session.set(AGENT_KEY, agent)

    # init history
    cl.user_session.set(JUDGEMENT_HISTORY_KEY, [])

    status = cl.Message(content="Thinking (this can take up to 60s)")
    await status.send()

    spinner_task = asyncio.create_task(thinking_spinner(status, interval=0.6))
    try:
        first_msg, judgement = await anext(agent)
    finally:
        spinner_task.cancel()

    status.content = first_msg
    await status.update()

    hist = cl.user_session.get(JUDGEMENT_HISTORY_KEY) or []
    hist.append(judgement)
    cl.user_session.set(JUDGEMENT_HISTORY_KEY, hist)

    await refresh_rubric_sidebar(hist)


@cl.on_message
async def on_message(msg: cl.Message):
    agent = cl.user_session.get(AGENT_KEY)
    if not agent:
        await cl.Message("Agent has exited. Please create a new conversation.").send()
        return

    status = cl.Message(content="Thinking (this can take up to 60s)")
    await status.send()

    agent_task = asyncio.create_task(agent.asend(msg.content))
    spinner_task = asyncio.create_task(thinking_spinner(status, interval=0.6))

    try:
        next_msg, judgement = await agent_task
    finally:
        spinner_task.cancel()
        try:
            await spinner_task
        except asyncio.CancelledError:
            pass

    status.content = next_msg
    await status.update()

    hist = cl.user_session.get(JUDGEMENT_HISTORY_KEY) or []
    hist.append(judgement)
    cl.user_session.set(JUDGEMENT_HISTORY_KEY, hist)

    await refresh_rubric_sidebar(hist)


@cl.on_chat_end
async def end():
    logger.info("[SmartHireX] Chat session ended.")