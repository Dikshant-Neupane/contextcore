"""
CONTEXTCORE — Gate v3 Kill Tests
Status: 🔒 LOCKED until v2 gate passes.
Target: Intent classifier correctly routes 7/10 natural language prompts.
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="v3 locked — complete gate_v2 first."
)


def test_v3_gate_intent_accuracy_7_of_10():
    """GATE v3 — Kill Test 1: Intent classifier correct on ≥7/10 real prompts."""
    pass


def test_v3_gate_latency_under_150ms():
    """GATE v3 — Kill Test 2: Full pipeline (L1→L3→L4→L5) ≤150ms."""
    pass


def test_v3_gate_artifacts_exist():
    """GATE v3 — Confirm v3 artifacts exist before sealing."""
    pass
