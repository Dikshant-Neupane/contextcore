"""Layer 3 heuristic intent classifier."""

from __future__ import annotations

import re
from collections import Counter

from contextcore.layer3_intent.types import IntentResult, TaskType

TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")
AMBIGUOUS_CONFIDENCE = 0.20

KEYWORDS: dict[TaskType, tuple[str, ...]] = {
    TaskType.DEBUG: ("debug", "error", "bug", "fix", "fail", "trace", "exception", "missing"),
    TaskType.REFACTOR: ("refactor", "rename", "extract", "cleanup", "simplify", "organize"),
    TaskType.SCAFFOLD: ("add", "create", "new", "implement", "build", "generate"),
    TaskType.ONBOARD: ("where", "overview", "explain", "understand", "entry", "flow", "start"),
    TaskType.REVIEW: ("review", "inspect", "audit", "score", "quality", "format", "summarize", "summary"),
    TaskType.SECURITY: (
        "security",
        "vulnerability",
        "auth",
        "permission",
        "secret",
        "rbac",
        "telemetry",
        "network",
        "off",
        "machine",
        "enforcement",
    ),
}


def classify_query(query: str) -> IntentResult:
    """Classify query text into one of six task types with confidence."""
    cleaned = query.strip().lower()
    if not cleaned:
        return IntentResult(query=query, task_type=TaskType.REVIEW, confidence=AMBIGUOUS_CONFIDENCE, rationale="empty query")

    tokens = TOKEN_PATTERN.findall(cleaned)
    if not tokens:
        return IntentResult(query=query, task_type=TaskType.REVIEW, confidence=AMBIGUOUS_CONFIDENCE, rationale="no lexical tokens")

    scores = _score_by_keywords(tokens)
    override_task = _priority_override(tokens, cleaned)
    if override_task is not None:
        confidence = 0.85
        rationale = f"selected={override_task.value}; priority-rule"
        return IntentResult(query=query, task_type=override_task, confidence=confidence, rationale=rationale)

    selected, confidence = _select_task(scores)
    rationale = _build_rationale(selected, scores)
    return IntentResult(query=query, task_type=selected, confidence=confidence, rationale=rationale)


def _priority_override(tokens: list[str], cleaned: str) -> TaskType | None:
    """Apply deterministic precedence rules for high-signal intent markers."""
    token_set = set(tokens)

    security_markers = {"security", "telemetry", "network", "exfiltration", "rbac"}
    if token_set.intersection(security_markers):
        return TaskType.SECURITY
    if "off-machine" in cleaned or "off machine" in cleaned:
        return TaskType.SECURITY
    if "sending source code" in cleaned:
        return TaskType.SECURITY

    debug_markers = {"debug", "error", "failing", "missing", "fail"}
    if token_set.intersection(debug_markers):
        return TaskType.DEBUG

    review_markers = {"summarize", "summary", "review"}
    if token_set.intersection(review_markers):
        return TaskType.REVIEW

    return None


def _score_by_keywords(tokens: list[str]) -> dict[TaskType, int]:
    """Score each task type by counting keyword matches in tokens."""
    token_counts = Counter(tokens)
    scores: dict[TaskType, int] = {task: 0 for task in TaskType}
    for task, words in KEYWORDS.items():
        scores[task] = sum(token_counts[word] for word in words)
    return scores


def _select_task(scores: dict[TaskType, int]) -> tuple[TaskType, float]:
    """Select a task type and confidence from score map."""
    best_task = max(scores, key=scores.get)
    best_score = scores[best_task]
    if best_score <= 0:
        return TaskType.REVIEW, AMBIGUOUS_CONFIDENCE

    top_scores = sorted(scores.values(), reverse=True)
    second_score = top_scores[1] if len(top_scores) > 1 else 0
    if best_score == second_score:
        return TaskType.REVIEW, 0.35

    confidence = min(1.0, 0.40 + 0.20 * best_score)
    return best_task, confidence


def _build_rationale(task_type: TaskType, scores: dict[TaskType, int]) -> str:
    """Create a compact rationale string for local debugging output."""
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top = ", ".join(f"{task.value}:{value}" for task, value in ranked[:2])
    return f"selected={task_type.value}; scores={top}"
