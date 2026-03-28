from __future__ import annotations


def parse_candidate(candidate: dict) -> dict:
    name = str(candidate.get("name", "")).strip()
    education = str(candidate.get("education", "")).strip()
    github_url = str(candidate.get("github_url", "")).strip()

    if not name:
        raise ValueError("Candidate name is required")
    if not education:
        raise ValueError("Candidate education is required")
    if not github_url:
        raise ValueError("Candidate github_url is required")

    try:
        experience_years = float(candidate.get("experience", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("Candidate experience must be numeric") from exc

    if experience_years < 0:
        raise ValueError("Candidate experience cannot be negative")

    projects_text = str(candidate.get("projects", "")).strip()
    projects = [line.strip(" -\t") for line in projects_text.splitlines() if line.strip()]
    if not projects:
        raise ValueError("At least one project line is required")

    return {
        "name": name,
        "education": education,
        "experience_years": experience_years,
        "projects": projects,
        "github_url": github_url,
    }
