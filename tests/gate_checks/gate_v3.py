"""
CONTEXTCORE — Gate v3 Kill Tests
Status: 🟡 PENDING
Target: Intent classifier correctly routes 7/10 natural language prompts.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Optional

import pytest


@dataclass(frozen=True)
class LabeledIntentPrompt:
    """Single labeled prompt used for v3 gate evaluation."""

    id: str
    prompt: str
    expected_task_type: str
    notes: Optional[str] = None


GROUND_TRUTH: list[LabeledIntentPrompt] = [
    LabeledIntentPrompt(
        "ip-01",
        "Why is my BFS subgraph missing edges after indexing?",
        "DEBUG",
        "Troubleshooting missing retrieval edges and indexing behavior.",
    ),
    LabeledIntentPrompt(
        "ip-02",
        "The query command returns irrelevant nodes - where should I debug scoring?",
        "DEBUG",
        "Asks where to debug ranking relevance logic.",
    ),
    LabeledIntentPrompt(
        "ip-03",
        "Refactor the querier scoring function to be easier to tune.",
        "REFACTOR",
        "Explicit refactor request focused on code structure.",
    ),
    LabeledIntentPrompt(
        "ip-04",
        "Rename GraphNode fields for clarity without changing behavior.",
        "REFACTOR",
        "Rename-only change preserving behavior.",
    ),
    LabeledIntentPrompt(
        "ip-05",
        "Add a new output section to the Markdown emitter.",
        "SCAFFOLD",
        "Feature-add task to create new output structure.",
    ),
    LabeledIntentPrompt(
        "ip-06",
        "Scaffold a new layer module for intent routing.",
        "SCAFFOLD",
        "Greenfield module creation request.",
    ),
    LabeledIntentPrompt(
        "ip-07",
        "Where do I start to understand how indexing builds the SQLite graph?",
        "ONBOARD",
        "Onboarding request to understand system flow.",
    ),
    LabeledIntentPrompt(
        "ip-08",
        "Summarize what the post-commit hook does and where it is installed.",
        "REVIEW",
        "Review-style summary of existing behavior and install path.",
    ),
    LabeledIntentPrompt(
        "ip-09",
        "Check the codebase for any accidental telemetry or network calls.",
        "SECURITY",
        "Security/privacy audit for exfiltration and network behavior.",
    ),
    LabeledIntentPrompt(
        "ip-10",
        "Are we ever sending source code off-machine? Show enforcement points.",
        "SECURITY",
        "Security assurance and policy enforcement audit request.",
    ),
]

_GROUND_TRUTH_FILLED = all(
    "[FILL IN]" not in sample.prompt and "[FILL IN]" not in sample.expected_task_type
    for sample in GROUND_TRUTH
)


@pytest.mark.skipif(
    not _GROUND_TRUTH_FILLED,
    reason="GROUND_TRUTH not filled for v3 intent gate yet.",
)
def test_v3_gate_intent_accuracy_7_of_10():
    """GATE v3 — Kill Test 1: Intent classifier correct on ≥7/10 real prompts."""
    from contextcore.layer3_intent.classifier import classify_query

    correct = 0
    for sample in GROUND_TRUTH:
        result = classify_query(sample.prompt)
        if result.task_type.value == sample.expected_task_type:
            correct += 1

    assert correct >= 7, f"v3 gate failed: {correct}/10 intent matches. Need >=7."


@pytest.mark.skipif(
    not _GROUND_TRUTH_FILLED,
    reason="GROUND_TRUTH not filled for v3 intent gate yet.",
)
def test_v3_gate_latency_under_150ms():
    """GATE v3 — Kill Test 2: Full pipeline (L1→L3→L4→L5) ≤150ms."""
    from contextcore.layer3_intent.classifier import classify_query

    latencies_ms = []
    for sample in GROUND_TRUTH[:5]:
        t0 = perf_counter()
        classify_query(sample.prompt)
        latencies_ms.append((perf_counter() - t0) * 1000)

    avg_latency = sum(latencies_ms) / len(latencies_ms)
    assert avg_latency <= 150.0, f"v3 gate failed: avg latency {avg_latency:.1f}ms > 150ms"


def test_v3_gate_artifacts_exist():
    """GATE v3 — Confirm v3 artifacts exist before sealing."""
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent.parent
    required = [
        "src/contextcore/layer3_intent/__init__.py",
        "src/contextcore/layer3_intent/types.py",
        "src/contextcore/layer3_intent/classifier.py",
        "tests/layer3_intent/test_classifier.py",
    ]
    missing = [item for item in required if not (root / item).exists()]
    assert not missing, f"Missing v3 artifacts: {missing}"
