"""
CONTEXTCORE — Gate v4 Kill Tests
Status: 🔒 LOCKED until v3 gate passes.
Target: RBAC + freshness + 3 developer roles on a 500-file project.
"""

import pytest

pytestmark = pytest.mark.skip(
    reason="v4 locked — complete gate_v3 first."
)


def test_v4_gate_rbac_permission_correct():
    """GATE v4 — Kill Test 1: RBAC serves permission-correct context to 3 roles."""
    pass


def test_v4_gate_stale_detection():
    """GATE v4 — Kill Test 2: Stale graph nodes are correctly flagged."""
    pass


def test_v4_gate_artifacts_exist():
    """GATE v4 — Confirm v4 artifacts exist before sealing."""
    pass
