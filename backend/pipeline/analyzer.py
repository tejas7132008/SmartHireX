from __future__ import annotations

from backend.services.llm_service import LLMService


class CandidateAnalyzer:
    def __init__(self, llm_service: LLMService) -> None:
        self.llm_service = llm_service

    async def analyze(self, enriched_candidate: dict) -> dict:
        llm_output = await self.llm_service.analyze_candidate(enriched_candidate)
        github = enriched_candidate["github"]
        activity_score = self._activity_score(
            repo_count=github.get("repo_count", 0),
            recent_commits_30d=github.get("recent_commits_30d", 0),
            language_count=len(github.get("languages", [])),
            followers=github.get("followers", 0),
        )

        return {
            "summary": llm_output["summary"],
            "skills": llm_output["inferred_skills"],
            "skill_score": llm_output["skill_score"],
            "project_score": llm_output["project_score"],
            "activity_score": activity_score,
            "communication_score": llm_output["communication_score"],
            "analysis_rationale": llm_output["rationale"],
            "github": github,
        }

    @staticmethod
    def _activity_score(repo_count: int, recent_commits_30d: int, language_count: int, followers: int) -> float:
        score = (
            float(repo_count) * 2.2
            + float(recent_commits_30d) * 1.1
            + float(language_count) * 7.0
            + float(followers) * 0.15
        )
        return max(0.0, min(100.0, round(score, 2)))
