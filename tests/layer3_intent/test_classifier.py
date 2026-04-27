"""Tests for Layer 3 intent classifier."""

from contextcore.layer3_intent.classifier import classify_query
from contextcore.layer3_intent.types import TaskType


def test_classify_debug_query() -> None:
    result = classify_query("debug why query fails on empty result")
    assert result.task_type == TaskType.DEBUG
    assert result.confidence >= 0.4


def test_classify_refactor_query() -> None:
    result = classify_query("refactor and rename this helper")
    assert result.task_type == TaskType.REFACTOR
    assert result.confidence >= 0.4


def test_classify_scaffold_query() -> None:
    result = classify_query("add new command for indexing")
    assert result.task_type == TaskType.SCAFFOLD
    assert result.confidence >= 0.4


def test_classify_onboard_query() -> None:
    result = classify_query("where is the entry flow for graph building")
    assert result.task_type == TaskType.ONBOARD
    assert result.confidence >= 0.4


def test_classify_review_and_security_queries() -> None:
    review_result = classify_query("review output format and quality")
    security_result = classify_query("check auth permission vulnerability")
    assert review_result.task_type == TaskType.REVIEW
    assert security_result.task_type == TaskType.SECURITY


def test_classifier_handles_ambiguous_or_empty_text() -> None:
    ambiguous = classify_query("hello")
    empty = classify_query("")
    assert ambiguous.task_type == TaskType.REVIEW
    assert empty.task_type == TaskType.REVIEW
    assert ambiguous.confidence <= 0.35
    assert empty.confidence <= 0.35


def test_classifier_priority_rules_debug_over_onboard() -> None:
    result = classify_query("where should I debug missing edges after indexing")
    assert result.task_type == TaskType.DEBUG


def test_classifier_priority_rules_security_and_summary() -> None:
    security = classify_query("check telemetry and network calls in this repo")
    review = classify_query("summarize what the post-commit hook does")
    assert security.task_type == TaskType.SECURITY
    assert review.task_type == TaskType.REVIEW
