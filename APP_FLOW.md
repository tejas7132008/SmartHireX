# SmartHireX App Flow

## Information Architecture (Phase 4)

Dashboard
-> Submit Candidate
-> Pipeline Running
-> Adaptive Interview Screen
-> Final Decision Screen
-> Download Report

## Screen-level Flow

1. Input Screen
- Recruiter enters candidate details and GitHub URL.
- Submits to POST /api/pipeline/jobs.

2. Pipeline Tracker
- Polls GET /api/pipeline/jobs/{job_id}.
- Shows parse/enrichment/analysis states.

3. Interview Screen (chat-style)
- Appears at status awaiting_interview/interviewing.
- Displays transcript + current dynamic question.
- Submits answer to POST /api/pipeline/jobs/{job_id}/interview.

4. Results Dashboard
- Displays extracted signals, AI summary, multi-agent scores, final priority.

5. Download Report
- Enabled when report_url exists.
- Opens GET /api/report/{job_id}.

## End-to-End State Machine

queued -> running -> awaiting_interview -> interviewing -> processing_decision -> done

Failure path: any state -> failed
