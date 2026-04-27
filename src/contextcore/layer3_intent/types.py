"""Layer 3 intent types and result containers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TaskType(str, Enum):
    """Supported intent task modes for context routing."""

    DEBUG = "DEBUG"
    REFACTOR = "REFACTOR"
    SCAFFOLD = "SCAFFOLD"
    ONBOARD = "ONBOARD"
    REVIEW = "REVIEW"
    SECURITY = "SECURITY"


@dataclass(frozen=True)
class IntentResult:
    """Classification output for a natural-language developer query."""

    query: str
    task_type: TaskType
    confidence: float
    rationale: str
