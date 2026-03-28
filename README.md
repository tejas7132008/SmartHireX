# SmartHireX Autonomous Hiring Pipeline

SmartHireX is an end-to-end hiring intelligence system that combines:

- Structured backend pipeline (`parse -> enrich -> analyze`)
- Adaptive interview intelligence (dynamic 3-5 question loop)
- Multi-agent hiring simulation (`tech_lead`, `hr`, `manager`)
- Downloadable report generation (JSON + PDF)

## Project Structure

```text
frontend/
  index.html
backend/
  schemas.py
  job_store.py
  pipeline/
    parser.py
    enrichment.py
    analyzer.py
    interview.py
    multi_decision.py
    hiring_pipeline.py
  reporting/
    report_builder.py
  services/
    github_service.py
    llm_service.py
main.py
```

## Required Environment Variables

- `OPENAI_API_KEY`: API key used by `backend/services/llm_service.py`
- `OPENAI_MODEL` (optional): model name (default `gpt-4.1-mini`)
- `GITHUB_TOKEN` (optional): raises GitHub rate limits for enrichment

Provider selection for `LLMService`:

- `FEATHERLESS_API_KEY` is preferred by default when present.
- Optional `LLM_PROVIDER` can force provider: `featherless`, `groq`, or `openai`.
- Featherless defaults:
  - `FEATHERLESS_BASE_URL=https://api.featherless.ai/v1`
  - `FEATHERLESS_MODEL=moonshotai/Kimi-K2-Instruct` (if not set)

## Run Locally

```bash
uv sync
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8010
```

Frontend (React/Vite):

```bash
cd frontend
npm install
npm run dev
```

Backend is available at `http://localhost:8010`.

## API Endpoints

- `POST /api/pipeline/jobs`
  - Creates a job and starts parse/enrich/analyze pipeline.
- `GET /api/pipeline/jobs/{job_id}`
  - Returns live status, interview state, and final result.
- `POST /api/pipeline/jobs/{job_id}/interview`
  - Submits adaptive interview answer and advances interview.
- `GET /api/report/{job_id}`
  - Downloads final PDF report.
- `GET /api/report/{job_id}/json`
  - Returns final JSON report payload.
- `GET /api/health`
  - Health check.

## Final Output Shape

The final job result returns:

- `candidate_summary`
- `extracted_signals`
- `interview` transcript + summary
- `agent_decisions` with per-agent score and reasoning
- `final_score` and `priority_level`
- `reasoning` (final recommendation rationale)
