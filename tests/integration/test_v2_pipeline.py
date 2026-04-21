"""
v2 pipeline integration test — LOCKED until v2 gate passes.
Phase: v2 🔒 LOCKED
Requires: src/contextcore/layer4_graph/ implementation
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="v2 locked — Layer 4 (dependency graph) not yet implemented. "
           "Complete gate_v2 kill tests to unlock."
)


def test_full_l1_l4_l5_pipeline():
    """L1 → L4 → L5: parse file, index to graph, query, emit context slice."""
    pass


def test_v2_pipeline_returns_subgraph():
    """Query returns a ranked subgraph, not the whole project."""
    pass


def test_v2_pipeline_within_token_budget():
    """Returned context slice stays within the ≤600 token budget."""
    pass


def test_v2_pipeline_latency_under_500ms():
    """End-to-end query latency ≤500ms on the sample project."""
    pass
