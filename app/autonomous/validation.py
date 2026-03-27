from __future__ import annotations

from typing import Any, Dict

from .config import SmartHireXConfig


class ValidationError(ValueError):
    pass


def validate_candidate_payload(candidate: Dict[str, Any], config: SmartHireXConfig) -> None:
    schema = config.input_schema
    required_fields = schema["required_fields"]

    for field in required_fields:
        if field not in candidate:
            raise ValidationError(f"Missing required field: {field}")

    if not isinstance(candidate["name"], str) or not candidate["name"].strip():
        raise ValidationError("Field 'name' must be a non-empty string")

    projects = candidate["projects"]
    if not isinstance(projects, list) or len(projects) < 1:
        raise ValidationError("Field 'projects' must be an array with at least one item")

    for optional_array in ["skills", "artifacts"]:
        if optional_array in candidate and not isinstance(candidate[optional_array], list):
            raise ValidationError(f"Field '{optional_array}' must be an array if provided")

    if "language" in candidate:
        allowed = set(schema["allowed_languages"])
        if candidate["language"] not in allowed:
            raise ValidationError(
                f"Unsupported language '{candidate['language']}'. Allowed: {sorted(allowed)}"
            )
