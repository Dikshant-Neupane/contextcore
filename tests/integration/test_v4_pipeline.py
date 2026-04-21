"""
v4 pipeline integration test — LOCKED until v4 gate passes.
Phase: v4 🔒 LOCKED
Requires: Full v4 stack (L1+L2+L3+L4+L5) implementation
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="v4 locked — Full stack not yet implemented. "
           "Complete gate_v4 kill tests to unlock."
)


def test_full_stack_pipeline():
    """Full L1→L2→L3→L4→L5 pipeline with temporal graph and RBAC."""
    pass


def test_v4_pipeline_rbac_enforced():
    """Permissions restrict context to role-appropriate nodes."""
    pass


def test_v4_pipeline_stale_nodes_flagged():
    """Nodes older than threshold are flagged as STALE in output."""
    pass
