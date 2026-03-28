# SmartHireX PRD (Hackathon Extension)

## Phase 0: Problem Understanding

### Rewritten problem
We need to identify high-potential candidates beyond resume keywords by combining unconventional proof-of-work signals, adaptive interview intelligence, and multi-stakeholder AI hiring simulation.

### Core problem
- Resumes are shallow and bias-prone.
- Static interviews fail to probe actual depth.
- Single-score decisions hide perspective and increase bias.

### Users
- Tech Recruiters
- Hiring Managers
- Tech Leads

### Context
- Fast evaluation under hiring pressure.
- Limited interviewer bandwidth.
- Need traceability and explainability.

### Assumptions
- GitHub activity is a meaningful but non-exclusive competency signal.
- LLM can reason over structured candidate evidence.
- Candidate can answer interview prompts in the product UI.

## Phase 1: Deep Analysis

### Why resumes fail
- Over-index on formatting and keyword stuffing.
- Under-represent problem-solving depth and execution quality.
- Hard to infer signal authenticity from static text.

### Why static interviews fail
- One-size-fits-all question sets miss candidate-specific gaps.
- No adaptive probing based on prior answer quality.
- Reduces confidence in hiring decision quality.

### Why single-score decisions fail
- Aggregated score masks disagreement among stakeholders.
- Weak transparency for hiring committees.
- Hard to audit decision rationale.

### Opportunity
- Use real GitHub enrichment as verifiable signal.
- Generate dynamic follow-up questions based on answer depth.
- Produce explicit agent-wise opinions with weighted aggregation.

## Phase 2: User Research

### Persona 1: Tech Recruiter
- Tech level: Medium.
- Pain points: High volume screening, inconsistent interviewer notes, unclear confidence.
- Goals: Faster shortlisting, consistent candidate narrative, download-ready report.

### Persona 2: Engineering Manager
- Tech level: High.
- Pain points: Weak signal on ownership and delivery reliability.
- Goals: Understand execution strength and risk before final round.

### Persona 3: Fresher Candidate
- Tech level: Medium.
- Pain points: Resume undersells practical work.
- Goals: Demonstrate ability via dynamic interview and project evidence.

### Journey map
Input -> Analysis -> Interview -> Decision -> Report Download

1. Submit candidate profile + GitHub URL.
2. Pipeline runs parse/enrich/analyze.
3. System enters adaptive interview state with dynamic questions.
4. Multi-agent decision executes after interview completion.
5. User reviews dashboard and downloads full report.

## Phase 3: UX Strategy

### P0 (MVP, built)
- Candidate form.
- GitHub enrichment.
- Adaptive interview (3-5 dynamic questions).
- Multi-agent decision output.
- Downloadable report (PDF + JSON generation in backend).

### P1
- Visualization dashboard for interview quality trends and score decomposition.

### P2
- Historical comparisons across candidates and roles.

## Validation Rules
- Candidate form: required name, education, numeric experience >= 0, non-empty projects, valid GitHub URL.
- Interview answer: non-empty, max 2000 chars.
- Interview completion: minimum 3 questions, maximum 5 questions.
- Agent outputs: score clamped to [0,1].

## Edge Cases
- GitHub API rate limiting or unavailable profile.
- LLM malformed JSON response.
- Interview submitted after completion.
- Report requested before finalization.
- Missing context due to interrupted async job.

## Acceptance Criteria
- Candidate reaches adaptive interview after analysis is complete.
- Each interview question is generated dynamically by LLM.
- Final result includes tech lead, HR, and manager agent opinions.
- Final priority uses weighted aggregate thresholds.
- Report endpoint downloads PDF and JSON is generated server-side.
- End-to-end flow works locally with real APIs.

## Out of Scope
- ATS integrations.
- Identity/authn/authz hardening.
- Candidate ranking across historical cohorts.
- Multilingual interview localization.
