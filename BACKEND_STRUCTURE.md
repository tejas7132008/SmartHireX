# Backend Structure

## Existing modules preserved
- backend/pipeline/parser.py
- backend/pipeline/enrichment.py
- backend/pipeline/analyzer.py
- backend/pipeline/hiring_pipeline.py (extended, not removed)

## New extension modules
- backend/pipeline/interview.py
  - AdaptiveInterviewEngine
  - Dynamic Q generation and answer evaluation loop
- backend/pipeline/multi_decision.py
  - Tech lead / HR / manager agent evaluations
  - Weighted aggregation and priority mapping
- backend/reporting/report_builder.py
  - Structured report payload builder
  - JSON + PDF persistence

## API extension
- POST /api/pipeline/jobs
- GET /api/pipeline/jobs/{job_id}
- POST /api/pipeline/jobs/{job_id}/interview
- GET /api/report/{job_id}
- GET /api/report/{job_id}/json

## Job model additions
- context: pre-interview computed signals
- interview: adaptive interview state + transcript
- report: generated file paths and download URLs

## Operational guarantees
- Existing parse->enrich->analyze chain remains intact.
- Decision layer now executes after adaptive interview completion.
- All LLM interactions use real API calls (no mocks in runtime logic).
