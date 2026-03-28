from backend.pipeline.parser import parse_candidate


def test_parse_candidate_success() -> None:
    parsed = parse_candidate(
        {
            "name": "Alex",
            "education": "BSc CS",
            "experience": 3,
            "projects": "Built API\nOptimized ETL",
            "github_url": "https://github.com/octocat",
        }
    )

    assert parsed["name"] == "Alex"
    assert parsed["experience_years"] == 3.0
    assert parsed["projects"] == ["Built API", "Optimized ETL"]


def test_parse_candidate_requires_project_lines() -> None:
    try:
        parse_candidate(
            {
                "name": "Alex",
                "education": "BSc CS",
                "experience": 3,
                "projects": "   ",
                "github_url": "https://github.com/octocat",
            }
        )
    except ValueError as exc:
        assert "project" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for empty projects")
