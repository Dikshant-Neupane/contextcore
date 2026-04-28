"""
CONTEXTCORE — Gate v4 Kill Tests
Status: 🟡 ACTIVE
Target: RBAC + freshness + 3 developer roles on a 500-file project.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest


def test_v4_gate_rbac_permission_correct(graph_builder, graph_querier, sample_project_dir):
    """GATE v4 — Kill Test 1: RBAC serves permission-correct context to 3 roles."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    graph_builder.index_directory(sample_project_dir)
    graph_builder.index_directory(repo_root / "tests")

    developer = graph_querier.query_v4(
        "gate stale detection",
        role="developer",
        task_type="REVIEW",
    )
    auditor = graph_querier.query_v4(
        "gate stale detection",
        role="auditor",
        task_type="REVIEW",
    )
    maintainer = graph_querier.query_v4(
        "gate stale detection",
        role="maintainer",
        task_type="REVIEW",
    )

    assert maintainer.ranked_nodes
    assert auditor.ranked_nodes
    assert not developer.ranked_nodes

    assert all("/tests/" in n.filepath.replace("\\", "/").lower() for n, _ in auditor.ranked_nodes)


def test_v4_gate_stale_detection(graph_builder, graph_querier, tmp_path):
    """GATE v4 — Kill Test 2: Stale graph nodes are correctly flagged."""
    stale_file = tmp_path / "stale_module.py"
    stale_file.write_text("def stale_symbol():\n    return 1\n", encoding="utf-8")

    # Push mtime 45 days into the past.
    old_ts = time.time() - (45 * 24 * 3600)
    os.utime(stale_file, (old_ts, old_ts))

    graph_builder.index_file(stale_file)

    result = graph_querier.query_v4(
        "stale_module",
        role="maintainer",
        stale_after_days=30,
        task_type="REVIEW",
    )
    assert result.ranked_nodes
    assert any(node.name.startswith("[STALE]") for node, _ in result.ranked_nodes)


def test_v4_gate_artifacts_exist():
    """GATE v4 — Confirm v4 artifacts exist before sealing."""
    root = Path(__file__).resolve().parent.parent.parent
    required = [
        "src/contextcore/layer2_temporal/__init__.py",
        "src/contextcore/layer2_temporal/freshness.py",
        "src/contextcore/layer4_graph/rbac.py",
    ]
    missing = [item for item in required if not (root / item).exists()]
    assert not missing, f"Missing v4 artifacts: {missing}"
