from __future__ import annotations

import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import httpx


class GitHubService:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")

    @staticmethod
    def extract_username(github_url: str) -> str:
        parsed = urlparse(github_url)
        if "github.com" not in parsed.netloc.lower():
            raise ValueError("github_url must be a valid GitHub profile URL")
        parts = [p for p in parsed.path.split("/") if p]
        if not parts:
            raise ValueError("github_url must include a username")
        return parts[0]

    async def _get_json(self, client: httpx.AsyncClient, path: str, params: dict | None = None) -> dict | list:
        response = await client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    async def fetch_profile_signals(self, github_url: str) -> dict:
        username = self.extract_username(github_url)
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "smarthirex-autonomous-pipeline",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        async with httpx.AsyncClient(base_url=self.BASE_URL, headers=headers, timeout=20) as client:
            user = await self._get_json(client, f"/users/{username}")
            repos = await self._get_json(
                client,
                f"/users/{username}/repos",
                params={"per_page": 100, "sort": "updated"},
            )
            events = await self._get_json(
                client,
                f"/users/{username}/events/public",
                params={"per_page": 100},
            )

            repo_count = int(user.get("public_repos", 0))
            language_counter: Counter[str] = Counter()
            for repo in repos[:20]:
                if repo.get("fork"):
                    continue
                lang = repo.get("language")
                if lang:
                    language_counter[lang] += 1

            commits_30d = 0
            push_events_30d = 0
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            for event in events:
                event_type = event.get("type")
                created_raw = event.get("created_at")
                if not created_raw:
                    continue
                created_at = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
                if created_at < cutoff:
                    continue
                if event_type == "PushEvent":
                    push_events_30d += 1
                    commits_30d += int(event.get("payload", {}).get("size", 0))

            return {
                "github_username": username,
                "repo_count": repo_count,
                "languages": [lang for lang, _ in language_counter.most_common(8)],
                "recent_commits_30d": commits_30d,
                "push_events_30d": push_events_30d,
                "followers": int(user.get("followers", 0)),
                "public_gists": int(user.get("public_gists", 0)),
            }
