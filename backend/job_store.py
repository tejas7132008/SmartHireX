from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class JobStore:
    def __init__(self) -> None:
        self.jobs: dict[str, dict[str, Any]] = {}

    def create(self, job_id: str) -> dict[str, Any]:
        state = {
            "job_id": job_id,
            "status": "queued",
            "steps": [],
            "result": None,
            "error": None,
            "context": None,
            "interview": None,
            "report": None,
        }
        self.jobs[job_id] = state
        return state

    def get(self, job_id: str) -> dict[str, Any] | None:
        return self.jobs.get(job_id)

    def append_step(self, job_id: str, step: str, status: str) -> None:
        state = self.jobs[job_id]
        state["steps"].append(
            {
                "step": step,
                "status": status,
                "timestamp": utc_now_iso(),
            }
        )
        if status == "running":
            state["status"] = "running"

    def update_status(self, job_id: str, status: str) -> None:
        state = self.jobs[job_id]
        state["status"] = status

    def set_context(self, job_id: str, context: dict[str, Any]) -> None:
        state = self.jobs[job_id]
        state["context"] = context

    def set_interview(self, job_id: str, interview_state: dict[str, Any]) -> None:
        state = self.jobs[job_id]
        state["interview"] = interview_state

    def set_report(self, job_id: str, report_state: dict[str, Any]) -> None:
        state = self.jobs[job_id]
        state["report"] = report_state

    def set_result(self, job_id: str, result: dict[str, Any]) -> None:
        state = self.jobs[job_id]
        state["result"] = result
        state["status"] = "done"

    def set_error(self, job_id: str, error_message: str) -> None:
        state = self.jobs[job_id]
        state["status"] = "failed"
        state["error"] = error_message
