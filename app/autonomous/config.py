from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


CONFIG_PATH = Path(__file__).with_name("config.json")


@dataclass(frozen=True)
class SmartHireXConfig:
    raw: Dict[str, Any]

    @property
    def model(self) -> Dict[str, Any]:
        return self.raw["model"]

    @property
    def decision(self) -> Dict[str, Any]:
        return self.raw["decision"]

    @property
    def stakeholders(self) -> Dict[str, Any]:
        return self.raw["stakeholders"]

    @property
    def interview(self) -> Dict[str, Any]:
        return self.raw["interview"]

    @property
    def input_schema(self) -> Dict[str, Any]:
        return self.raw["input_schema"]

    @property
    def sources(self) -> Dict[str, Any]:
        return self.raw["sources"]

    @property
    def anti_static(self) -> Dict[str, Any]:
        return self.raw["anti_static"]

    @property
    def compliance(self) -> Dict[str, Any]:
        return self.raw["compliance"]

    @property
    def deployment(self) -> Dict[str, Any]:
        return self.raw["deployment"]


def _validate_required_sections(cfg: Dict[str, Any]) -> None:
    required = {
        "model",
        "decision",
        "stakeholders",
        "interview",
        "input_schema",
        "sources",
        "anti_static",
        "compliance",
        "deployment",
        "success",
    }
    missing = required.difference(cfg.keys())
    if missing:
        raise ValueError(f"Missing required config sections: {sorted(missing)}")


def load_config() -> SmartHireXConfig:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        cfg = json.load(f)
    _validate_required_sections(cfg)
    return SmartHireXConfig(raw=cfg)
