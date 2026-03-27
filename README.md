# SmartHireX 🚀

SmartHireX — Discover Talent Beyond Resumes

## Section 1: Project Overview

Project Name: SmartHireX

One-line description:
SmartHireX is an autonomous hiring intelligence system that evaluates candidates beyond resume-only screening.

Problem it solves:
Traditional hiring pipelines over-index on static resume signals. SmartHireX introduces an evidence-driven approach that combines profile depth, adaptive interviews, and stakeholder reasoning to make more nuanced decisions.

Key innovation:
SmartHireX goes beyond resumes by continuously updating confidence using interview evidence, behavioral activity, and stakeholder-level consensus.

## Section 2: System Architecture

Overall flow:
Input -> Candidate Discovery -> Adaptive Interview -> Evaluation Updates -> Multi-Stakeholder Decision -> Final Output

Component roles:
- TalentDiscoveryAgent (implemented as CandidateDiscoveryAgent): builds initial candidate evidence profile.
- InterviewAgent: runs adaptive interview turns.
- Evaluation logic (EvaluationAgent): updates dimension scores and confidence trajectory.
- DecisionAgent: simulates recruiter, hiring manager, and tech lead decisions.
- OrchestratorAgent: coordinates the full pipeline from input validation to final output.

## Section 3: Agent Breakdown

TalentDiscoveryAgent / CandidateDiscoveryAgent:
- Purpose: Build the first talent profile from profile signals, artifacts, activity, and optional web context.
- Inputs: candidate payload, artifacts, activity, optional github_url and portfolio_url.
- Outputs: candidate_summary and initial talent_scores.
- Key logic: computes bounded scores for skill, initiative, consistency, and communication dimensions.
- Decision approach: weighted evidence + controlled randomness under seed control.

InterviewAgent:
- Purpose: Evaluate candidate depth through adaptive questioning.
- Inputs: current score state and interview configuration.
- Outputs: interview_report including turns, final confidence, final difficulty, and trend.
- Key logic: targets weak dimensions and adapts question difficulty per performance.
- Decision approach: focuses on weakest dimensions first to maximize evidence quality.

EvaluationAgent:
- Purpose: Convert each turn into updated beliefs.
- Inputs: response evaluation metrics and prior state.
- Outputs: revised score dimensions and updated confidence.
- Key logic: blends prior and new evidence, tracks stability over recent turns.
- Decision approach: confidence rises with both quality and trend stability.

DecisionAgent:
- Purpose: Produce final hiring decision through multi-stakeholder simulation.
- Inputs: final scores, artifacts/activity-derived evidence bonuses.
- Outputs: stakeholder_decisions and final_decision.
- Key logic: weighted voting, veto logic, hard-fail checks, tie-break policy.
- Decision approach: combine stakeholder judgments with explicit thresholds.

OrchestratorAgent:
- Purpose: End-to-end controller.
- Inputs: validated candidate payload and seed.
- Outputs: full structured pipeline response.
- Key logic: execute analyze -> interview -> decision pipeline.
- Decision approach: deterministic flow with seeded variation where configured.

## Section 4: Adaptive Interview System

How questions are generated:
- InterviewAgent selects low-scoring dimensions.
- It chooses prompts from a dimension-specific question bank.
- Prompt framing changes by difficulty (foundational, intermediate, advanced).

How difficulty adapts:
- Increase when response score passes configured threshold.
- Decrease when response score drops below configured threshold.
- Maintain when within stable range.

Metrics evaluated each turn:
- correctness
- thinking
- clarity
- consistency

## Section 5: Multi-Stakeholder Decision System

Recruiter role:
- Emphasizes communication and delivery readiness.

Hiring Manager role:
- Emphasizes execution reliability and expected team impact.

Tech Lead role:
- Emphasizes technical depth, problem framing, and failure analysis capability.

Disagreement handling:
- If stakeholders disagree, SmartHireX resolves via weighted consensus and configured tie-break policy.

Final decision derivation:
- Apply hard-fail/veto rules first.
- Aggregate stakeholder votes.
- Use confidence thresholds to map to final labels.

## Section 6: Autonomous Pipeline

Single API trigger:
- POST /run-smarthirex-pipeline

Step-by-step execution:
1. Validate input schema and seed requirement.
2. Run candidate discovery.
3. Run adaptive interview loop.
4. Run multi-stakeholder decision stage.
5. Return final structured output with confidence and reasoning.

Logging style:
- [SmartHireX] Analyzing candidate...
- [SmartHireX] Running adaptive interview...
- [SmartHireX] Final decision generated

## Section 7: Input & Output Format (FINAL VERSION)

### Example Input JSON

```json
{
  "candidate": {
    "name": "Ravi Kumar",
    "education": "Tier-3 College",
    "years_experience": 1,
    "resume_score": 4,
    "projects": [
      "Built a custom database engine in C",
      "Implemented distributed caching system",
      "Created competitive coding toolkit"
    ],
    "activity": {
      "commits_per_week": 18,
      "consistency": 9
    },
    "communication_hint": "average",
    "github_url": "https://github.com/torvalds"
  },
  "config": {
    "seed": 42
  }
}
```

### Final Output Structure

```json
{
  "candidate_summary": {
    "name": "Ravi Kumar",
    "education": "Tier-3 College",
    "experience": 1
  },
  "talent_scores": {
    "skill": 8.5,
    "initiative": 9.0,
    "consistency": 8.2,
    "communication": 6.5
  },
  "interview_report": {
    "turns": 5,
    "final_difficulty": "advanced",
    "confidence_trend": "increasing"
  },
  "stakeholder_decisions": {
    "recruiter": "hold",
    "tech_lead": "strong_hire",
    "hiring_manager": "hire"
  },
  "final_decision": "strong_hire",
  "confidence_score": 0.91,
  "reasoning": [
    "Strong technical depth demonstrated in adaptive interview",
    "High project complexity and consistency signals",
    "Minor communication concerns but outweighed by skill"
  ]
}
```

## Section 8: Demo Candidates

SmartHireX demo includes three candidate archetypes:

1. Hidden Gem
- Demonstrates high technical depth and consistency despite weaker pedigree signals.

2. Overrated Candidate
- Demonstrates that resume prestige alone cannot pass evidence-based hiring.

3. Balanced Candidate
- Demonstrates realistic mid-band outcomes where interview performance drives final direction.

## Section 9: Key Features

- Talent discovery beyond resumes
- Adaptive interview intelligence
- Multi-stakeholder decision making
- Autonomous execution with one trigger
- Explainable reasoning trace

## Section 10: Configuration

Environment variables used:
- FEATHERLESS_API_KEY
- FEATHERLESS_MODEL
- BRIGHTDATA_API_KEY
- BRIGHTDATA_ZONE
- TEMPERATURE
- MAX_TOKENS
- REQUEST_TIMEOUT
- MAX_RETRIES
- SIMULATION_MODE
- USE_SEED
- DEFAULT_SEED
- PORT
- LOG_LEVEL

Model configuration:
- Primary/fallback model, token limits, timeout, retry policy are centralized in config.

Randomness and seed usage:
- Seed is required when reproducibility is enabled.
- Controlled variability is applied through bounded random mechanisms.

## Section 11: Integrations Status

Featherless.ai:
- Integrated for LLM reasoning at environment/runtime layer.

Bright Data:
- Planned as a core signal source; integration point prepared and currently wired for URL-based candidate enrichment with fallback behavior.

Execution approach:
- controlled simulation aligned with real-world hiring dynamics

## Section 12: Project Structure

```text
app/
  autonomous/
    agents.py
    models.py
    orchestrator.py
    config.py
    config.json
    validation.py
  integrations/
    brightdata_client.py
  static/
    smarthirex.html
  app_methods.py
data/
  demo_candidates.json
scripts/
  run_demo_pipeline.py
```

## Section 13: Current Completion Status

Fully complete:
- Core autonomous pipeline
- Adaptive interview loop
- Multi-stakeholder decision system
- Structured output with confidence and reasoning
- Demo runner and candidate scenarios

Partially complete:
- Extended production-grade integration hardening and monitoring around external signal providers.

Pending focus area:
- Bright Data reliability hardening and deeper extraction fidelity tuning.

## Section 14: Strengths

- System-based architecture over one-off scoring scripts.
- Real-world hiring relevance with explainability.
- Decision intelligence through stakeholder simulation and adaptive evidence collection.

## Section 15: Demo Flow

1. Launch SmartHireX service.
2. Submit candidate payload to /run-smarthirex-pipeline.
3. Observe discovery scoring.
4. Observe adaptive interview turns and confidence updates.
5. Observe stakeholder-level decisions.
6. Review final decision, confidence_score, and reasoning trace.

## Section 16: Why SmartHireX is Different

Unlike traditional hiring tools that rely on static scoring or keyword matching, SmartHireX operates as a decision-making system.

It continuously updates its belief about candidate quality using:
- multi-source signals,
- adaptive evidence gathering,
- and stakeholder-level reasoning.

This makes SmartHireX not just an evaluator, but a simulated hiring ecosystem capable of making nuanced, explainable decisions.
