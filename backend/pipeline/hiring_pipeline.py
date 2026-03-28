from __future__ import annotations

from collections.abc import Callable
from typing import Awaitable

from backend.pipeline.analyzer import CandidateAnalyzer
from backend.pipeline.decision import decide
from backend.pipeline.enrichment import CandidateEnricher
from backend.pipeline.parser import parse_candidate

StepCallback = Callable[[str, str], Awaitable[None]]


class HiringPipeline:
    def __init__(self, enricher: CandidateEnricher, analyzer: CandidateAnalyzer) -> None:
        self.enricher = enricher
        self.analyzer = analyzer

    async def run(self, candidate: dict, step_callback: StepCallback) -> dict:
        await step_callback("parsing", "running")
        parsed = parse_candidate(candidate)
        await step_callback("parsing", "done")

        await step_callback("enrichment", "running")
        enriched = await self.enricher.enrich(parsed)
        await step_callback("enrichment", "done")

        await step_callback("analysis", "running")
        signals = await self.analyzer.analyze(enriched)
        await step_callback("analysis", "done")

        await step_callback("decision", "running")
        decision = decide(signals)
        await step_callback("decision", "done")

        return {
            "candidate_summary": {
                "name": enriched["name"],
                "education": enriched["education"],
                "experience_years": enriched["experience_years"],
                "summary": signals["summary"],
            },
            "extracted_signals": {
                "skills": signals["skills"],
                "github": signals["github"],
                "component_scores": {
                    "skill_score": signals["skill_score"],
                    "project_score": signals["project_score"],
                    "activity_score": signals["activity_score"],
                    "communication_score": signals["communication_score"],
                },
            },
            "final_score": decision["final_score"],
            "priority_level": decision["priority"],
            "reasoning": decision["reasoning"],
        }

    async def run_pre_interview(self, candidate: dict, step_callback: StepCallback) -> dict:
        await step_callback("parsing", "running")
        parsed = parse_candidate(candidate)
        await step_callback("parsing", "done")

        await step_callback("enrichment", "running")
        enriched = await self.enricher.enrich(parsed)
        await step_callback("enrichment", "done")

        await step_callback("analysis", "running")
        signals = await self.analyzer.analyze(enriched)
        await step_callback("analysis", "done")

        return {
            "parsed": parsed,
            "enriched": enriched,
            "signals": signals,
        }
