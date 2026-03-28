from __future__ import annotations

from backend.services.github_service import GitHubService


class CandidateEnricher:
    def __init__(self, github_service: GitHubService) -> None:
        self.github_service = github_service

    async def enrich(self, parsed_candidate: dict) -> dict:
        github_signals = await self.github_service.fetch_profile_signals(parsed_candidate["github_url"])
        enriched = dict(parsed_candidate)
        enriched["github"] = github_signals
        return enriched
