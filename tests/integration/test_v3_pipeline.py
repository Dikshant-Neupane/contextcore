"""
v3 pipeline integration test — LOCKED until v3 gate passes.
Phase: v3 🔒 LOCKED
Requires: src/contextcore/layer3_intent/ implementation
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="v3 locked — Layer 3 (intent engine) not yet implemented. "
           "Complete gate_v3 kill tests to unlock."
)


def test_full_l1_l3_l4_l5_pipeline():
    """L1 → L3 → L4 → L5: parse, classify intent, query graph, emit."""
    pass


def test_v3_pipeline_intent_routes_correctly():
    """Intent classifier routes to the correct subgraph mode (DEBUG/REFACTOR/etc.)."""
    pass


def test_v3_pipeline_latency_under_150ms():
    """End-to-end latency including intent classification ≤150ms."""
    pass
