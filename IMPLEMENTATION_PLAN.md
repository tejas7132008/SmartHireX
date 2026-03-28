# Implementation Plan

## Phase 6 Documents Delivered
- PRD.md
- APP_FLOW.md
- TECH_STACK.md
- FRONTEND_GUIDELINES.md
- BACKEND_STRUCTURE.md
- IMPLEMENTATION_PLAN.md

## Build Plan (Completed)

1. Extend pipeline into two-stage orchestration
- Stage A: parse/enrich/analyze.
- Stage B: adaptive interview -> multi-agent decision -> reporting.

2. Adaptive Interview Intelligence
- LLM-generated first question.
- Per-answer evaluation: depth, clarity, confidence.
- Dynamic follow-up strategy with 3-5 question bounds.

3. Multi-Agent Decision System
- Agent rubrics:
  - tech_lead
  - hr
  - manager
- Weighted aggregate formula:
  - final_score = weighted_average(agent_scores)
- Priority:
  - HIGH > 0.75
  - MEDIUM > 0.5
  - LOW otherwise

4. Reporting
- Generate structured report payload with all required sections.
- Persist report as JSON + PDF.
- Expose downloadable report endpoint.

5. Frontend extension
- Added interview chat panel with transcript and adaptive question rendering.
- Added status timeline and multi-agent result cards.
- Added Download Report flow.

## Local Setup Commands (Exact)

Backend
1. uv sync
2. uv run uvicorn main:app --reload --host 0.0.0.0 --port 8010

Frontend
1. cd frontend
2. npm install
3. npm run dev

## Test Flow (Phase 7)
1. Submit candidate.
2. Watch parse/enrichment/analysis steps.
3. Complete adaptive interview (3-5 dynamic questions).
4. Wait for multi-agent aggregation.
5. View result and download report.

## Hackathon Edge (Phase 8)
- Adaptive intelligence: question tree adapts to answer quality.
- Multi-agent reasoning: explicit stakeholder perspectives.
- Real signals: GitHub + LLM reasoning + transcript evidence.

## Scalability to 1M users
- Move job state to Redis + durable event queue (Kafka/SQS equivalent).
- Split workers: enrichment, interview, decision, report generation.
- Store reports in object storage + CDN signed URLs.
- Add model gateway with caching, rate limits, and fallback routing.
- Partition candidate processing by tenant/job shard keys.
- Add observability: latency SLOs, queue depth, token and cost telemetry.

## 60-second pitch (Phase 9)
Hiring today is noisy, biased, and slow because resumes are shallow, interviews are static, and final decisions often hide reasoning. SmartHireX changes that with a live AI hiring pipeline that starts from real GitHub signals, adapts interview questions in real time based on answer quality, and simulates a full hiring panel with tech, HR, and manager agents. Instead of one opaque score, teams get transparent multi-agent opinions, weighted final priority, and a downloadable report that is audit-ready. The outcome is faster, fairer, and more explainable hiring under real-world pressure.
