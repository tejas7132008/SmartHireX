from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from backend.job_store import JobStore
from backend.pipeline.analyzer import CandidateAnalyzer
from backend.pipeline.enrichment import CandidateEnricher
from backend.pipeline.hiring_pipeline import HiringPipeline
from backend.pipeline.interview import AdaptiveInterviewEngine
from backend.pipeline.multi_decision import MultiAgentDecisionSystem
from backend.reporting.report_builder import build_report_payload, save_report_bundle
from backend.schemas import (
    CandidateSubmission,
    InterviewAnswerRequest,
    InterviewAnswerResponse,
    InterviewState,
    JobCreateResponse,
    JobStateResponse,
)
from backend.services.github_service import GitHubService
from backend.services.llm_service import LLMService

load_dotenv(override=True)

app = FastAPI(title="SmartHireX Autonomous Hiring")
frontend_dir = Path(__file__).resolve().parent / "frontend"
dist_dir = frontend_dir / "dist"
report_dir = Path(__file__).resolve().parent / "reports"

if dist_dir.exists() and (dist_dir / "assets").exists():
    app.mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets")
elif frontend_dir.exists() and (frontend_dir / "assets").exists():
    app.mount("/assets", StaticFiles(directory=frontend_dir / "assets"), name="assets")


def frontend_index_path() -> Path:
    candidate = dist_dir / "index.html"
    if candidate.exists():
        return candidate
    return frontend_dir / "index.html"

job_store = JobStore()


def build_pipeline() -> HiringPipeline:
    github_service = GitHubService()
    llm_service = LLMService()
    enricher = CandidateEnricher(github_service=github_service)
    analyzer = CandidateAnalyzer(llm_service=llm_service)
    return HiringPipeline(enricher=enricher, analyzer=analyzer)


def build_interview_engine() -> AdaptiveInterviewEngine:
    llm_service = LLMService()
    return AdaptiveInterviewEngine(llm_service=llm_service)


def build_multi_decision() -> MultiAgentDecisionSystem:
    llm_service = LLMService()
    return MultiAgentDecisionSystem(llm_service=llm_service)


def _status_from_upstream_error(exc: Exception) -> int:
    message = str(exc).lower()
    if "rate limit" in message or "429" in message:
        return 429
    if "api key" in message or "unauthorized" in message or "authentication" in message:
        return 401
    return 502


def _is_rate_limit_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "rate limit" in message or "429" in message


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(frontend_index_path())


@app.post("/api/pipeline/jobs", response_model=JobCreateResponse)
async def create_pipeline_job(payload: CandidateSubmission) -> JobCreateResponse:
    job_id = str(uuid.uuid4())
    job_store.create(job_id)
    candidate_payload = payload.model_dump()
    asyncio.create_task(_run_initial_job(job_id, candidate_payload))
    return JobCreateResponse(job_id=job_id)


@app.get("/api/pipeline/jobs/{job_id}", response_model=JobStateResponse)
async def get_pipeline_job(job_id: str) -> JobStateResponse:
    state = job_store.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")
    interview_payload = state.get("interview")
    interview_model = InterviewState(**interview_payload) if interview_payload else None
    report_payload = state.get("report") or {}
    return JobStateResponse(
        job_id=state["job_id"],
        status=state["status"],
        steps=state["steps"],
        interview=interview_model,
        report_url=report_payload.get("download_url"),
        result=state.get("result"),
        error=state.get("error"),
    )


@app.post("/api/pipeline/jobs/{job_id}/interview", response_model=InterviewAnswerResponse)
async def submit_interview_answer(job_id: str, payload: InterviewAnswerRequest) -> InterviewAnswerResponse:
    state = job_store.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")

    if state.get("status") not in {"awaiting_interview", "interviewing"}:
        raise HTTPException(status_code=409, detail="Interview is not currently active for this job")

    context = state.get("context")
    interview_state = state.get("interview")
    if not context or not interview_state:
        raise HTTPException(status_code=409, detail="Interview context missing")

    try:
        engine = build_interview_engine()
        updated_interview = await engine.submit_answer(
            state=interview_state,
            answer=payload.answer,
            candidate_context=context,
        )
        job_store.set_interview(job_id, updated_interview)

        if updated_interview.get("completed"):
            job_store.append_step(job_id, "adaptive_interview", "done")
            job_store.update_status(job_id, "processing_decision")
            asyncio.create_task(_finalize_job(job_id))
        else:
            job_store.update_status(job_id, "interviewing")

        refreshed = job_store.get(job_id)
        return InterviewAnswerResponse(
            job_id=job_id,
            status=refreshed["status"],
            interview=InterviewState(**updated_interview),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        if _is_rate_limit_error(exc):
            # Demo-safe behavior: close the interview with current evidence and continue pipeline.
            transcript = list((interview_state or {}).get("transcript") or [])
            current_question = (interview_state or {}).get("current_question") or {}
            transcript.append(
                {
                    "question": current_question,
                    "answer": payload.answer,
                    "evaluation": {
                        "depth": 0.6,
                        "clarity": 0.6,
                        "confidence": 0.6,
                        "follow_up_needed": False,
                        "recommended_focus": "general",
                        "evaluation_notes": ["Interview auto-closed after upstream rate limit."],
                    },
                }
            )
            summary = AdaptiveInterviewEngine._summarize(transcript)
            emergency_interview_state = {
                **(interview_state or {}),
                "current_question": None,
                "transcript": transcript,
                "question_count": len(transcript),
                "completed": True,
                "summary": summary,
            }
            job_store.set_interview(job_id, emergency_interview_state)
            job_store.append_step(job_id, "adaptive_interview", "done")
            job_store.update_status(job_id, "processing_decision")
            asyncio.create_task(_finalize_job(job_id))

            refreshed = job_store.get(job_id)
            return InterviewAnswerResponse(
                job_id=job_id,
                status=refreshed["status"],
                interview=InterviewState(**emergency_interview_state),
            )
        job_store.set_error(job_id, str(exc))
        raise HTTPException(status_code=_status_from_upstream_error(exc), detail=str(exc)) from exc


@app.get("/api/report/{job_id}")
async def download_report(job_id: str) -> FileResponse:
    state = job_store.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")

    report = state.get("report") or {}
    pdf_path = report.get("pdf_path")
    if not pdf_path or not Path(pdf_path).exists():
        raise HTTPException(status_code=404, detail="Report is not ready yet")

    return FileResponse(Path(pdf_path), filename=f"smarthirex_report_{job_id}.pdf", media_type="application/pdf")


@app.get("/api/report/{job_id}/json")
async def fetch_report_json(job_id: str) -> JSONResponse:
    state = job_store.get(job_id)
    if not state:
        raise HTTPException(status_code=404, detail="Job not found")

    report = state.get("report") or {}
    json_path = report.get("json_path")
    if not json_path or not Path(json_path).exists():
        raise HTTPException(status_code=404, detail="Report is not ready yet")

    payload = json.loads(Path(json_path).read_text(encoding="utf-8"))
    return JSONResponse(content=payload)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


async def _run_initial_job(job_id: str, candidate_payload: dict) -> None:
    async def step_callback(step: str, status: str) -> None:
        job_store.append_step(job_id, step, status)

    try:
        pipeline = build_pipeline()
        precomputed = await pipeline.run_pre_interview(candidate_payload, step_callback)

        interview_engine = build_interview_engine()
        await step_callback("adaptive_interview", "running")
        interview_state = await interview_engine.start(precomputed)

        job_store.set_context(job_id, precomputed)
        job_store.set_interview(job_id, interview_state)
        job_store.update_status(job_id, "awaiting_interview")

        partial_result = {
            "candidate_summary": {
                "name": precomputed["enriched"]["name"],
                "education": precomputed["enriched"]["education"],
                "experience_years": precomputed["enriched"]["experience_years"],
                "summary": precomputed["signals"]["summary"],
            },
            "extracted_signals": {
                "skills": precomputed["signals"]["skills"],
                "github": precomputed["signals"]["github"],
            },
        }
        current_state = job_store.get(job_id)
        if current_state is not None:
            current_state["result"] = partial_result
    except Exception as exc:
        job_store.set_error(job_id, str(exc))


async def _finalize_job(job_id: str) -> None:
    async def step_callback(step: str, status: str) -> None:
        job_store.append_step(job_id, step, status)

    state = job_store.get(job_id)
    if not state:
        return

    context = state.get("context")
    interview_state = state.get("interview")
    if not context or not interview_state:
        job_store.set_error(job_id, "Cannot finalize without context and completed interview")
        return

    try:
        await step_callback("multi_agent_decision", "running")
        decision_system = build_multi_decision()
        multi_decision = await decision_system.evaluate(
            candidate_context=context,
            signals=context["signals"],
            interview_state=interview_state,
        )
        await step_callback("multi_agent_decision", "done")

        llm_service = LLMService()
        ai_summary = await llm_service.summarize_final_report(
            {
                "candidate": context["enriched"],
                "signals": context["signals"],
                "interview": interview_state,
                "multi_agent_decision": multi_decision,
            }
        )

        final_result = {
            "candidate_summary": {
                "name": context["enriched"]["name"],
                "education": context["enriched"]["education"],
                "experience_years": context["enriched"]["experience_years"],
                "summary": context["signals"]["summary"],
            },
            "extracted_signals": {
                "skills": context["signals"]["skills"],
                "github": context["signals"]["github"],
                "component_scores": {
                    "skill_score": context["signals"]["skill_score"],
                    "project_score": context["signals"]["project_score"],
                    "activity_score": context["signals"]["activity_score"],
                    "communication_score": context["signals"]["communication_score"],
                },
            },
            "interview": interview_state,
            "ai_summary": ai_summary,
            "agent_decisions": multi_decision["agents"],
            "aggregator": multi_decision["aggregator"],
            "final_score": multi_decision["final_score"],
            "priority_level": multi_decision["priority"],
            "reasoning": ai_summary.get("recommendation_reasoning", []),
        }

        report_payload = build_report_payload(
            candidate_summary=final_result["candidate_summary"],
            github_signals=final_result["extracted_signals"]["github"],
            interview_state=interview_state,
            ai_summary=ai_summary,
            multi_agent_decision=multi_decision,
        )
        report_paths = save_report_bundle(job_id=job_id, report_payload=report_payload, root_dir=report_dir)
        report_state = {
            **report_paths,
            "download_url": f"/api/report/{job_id}",
            "json_url": f"/api/report/{job_id}/json",
        }

        job_store.set_report(job_id, report_state)
        job_store.set_result(job_id, final_result)
    except Exception as exc:
        job_store.set_error(job_id, str(exc))
