from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def build_report_payload(
    *,
    candidate_summary: dict[str, Any],
    github_signals: dict[str, Any],
    interview_state: dict[str, Any],
    ai_summary: dict[str, Any],
    multi_agent_decision: dict[str, Any],
) -> dict[str, Any]:
    transcript = []
    for turn in interview_state.get("transcript", []):
        transcript.append(
            {
                "question": turn.get("question", {}).get("question", ""),
                "focus_area": turn.get("question", {}).get("focus_area", ""),
                "answer": turn.get("answer", ""),
                "evaluation": turn.get("evaluation", {}),
            }
        )

    return {
        "candidate_info": candidate_summary,
        "github_signals": github_signals,
        "interview_transcript": transcript,
        "interview_summary": interview_state.get("summary", {}),
        "ai_summary": ai_summary,
        "agent_decisions": multi_agent_decision.get("agents", {}),
        "aggregator": multi_agent_decision.get("aggregator", {}),
        "final_score": multi_agent_decision.get("final_score", 0.0),
        "final_priority": multi_agent_decision.get("priority", "LOW"),
        "reasoning": ai_summary.get("recommendation_reasoning", []),
    }


def save_report_bundle(job_id: str, report_payload: dict[str, Any], root_dir: Path) -> dict[str, str]:
    root_dir.mkdir(parents=True, exist_ok=True)
    json_path = root_dir / f"{job_id}.json"
    pdf_path = root_dir / f"{job_id}.pdf"

    json_path.write_text(json.dumps(report_payload, indent=2, ensure_ascii=True), encoding="utf-8")
    _write_pdf_report(pdf_path, report_payload)

    return {
        "json_path": str(json_path),
        "pdf_path": str(pdf_path),
    }


def _write_pdf_report(path: Path, payload: dict[str, Any]) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    x = 50
    y = height - 50
    line_height = 14

    def write_line(text: str, bold: bool = False) -> None:
        nonlocal y
        if y < 60:
            c.showPage()
            y = height - 50
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 10)
        c.drawString(x, y, text[:140])
        y -= line_height

    write_line("SmartHireX Candidate Hiring Report", bold=True)
    write_line("", bold=False)

    candidate = payload.get("candidate_info", {})
    write_line("Candidate Info", bold=True)
    write_line(f"Name: {candidate.get('name', 'N/A')}")
    write_line(f"Education: {candidate.get('education', 'N/A')}")
    write_line(f"Experience (years): {candidate.get('experience_years', 'N/A')}")

    write_line("", bold=False)
    github = payload.get("github_signals", {})
    write_line("GitHub Signals", bold=True)
    write_line(f"Username: {github.get('github_username', 'N/A')}")
    write_line(f"Repo Count: {github.get('repo_count', 'N/A')}")
    write_line(f"Commits (30d): {github.get('recent_commits_30d', 'N/A')}")
    write_line(f"Languages: {', '.join(github.get('languages', []))}")

    write_line("", bold=False)
    write_line("Interview Transcript", bold=True)
    for idx, turn in enumerate(payload.get("interview_transcript", []), start=1):
        write_line(f"Q{idx}: {turn.get('question', '')}")
        write_line(f"A{idx}: {turn.get('answer', '')}")

    write_line("", bold=False)
    write_line("Agent Decisions", bold=True)
    for agent_name, opinion in payload.get("agent_decisions", {}).items():
        score = opinion.get("score", 0)
        write_line(f"{agent_name}: score={score}")
        for reason in opinion.get("reasoning", [])[:3]:
            write_line(f"- {reason}")

    write_line("", bold=False)
    write_line("Final Decision", bold=True)
    write_line(f"Final Score: {payload.get('final_score', 0)}")
    write_line(f"Final Priority: {payload.get('final_priority', 'LOW')}")

    c.save()
