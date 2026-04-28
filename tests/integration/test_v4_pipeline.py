"""
v4 pipeline integration test.
Phase: v4 🟡 ACTIVE
Requires: Full v4 stack (L1+L2+L3+L4+L5) implementation
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest
from contextcore.cli.main import _resolve_task_type


def test_full_stack_pipeline(
    parser,
    extractor,
    emitter,
    graph_builder,
    graph_querier,
    sample_project_dir,
    class_with_methods_file,
):
    """Full L1→L2→L3→L4→L5 pipeline with temporal graph and RBAC."""
    parse_result = parser.parse(class_with_methods_file)
    structure = extractor.extract(parse_result)
    markdown = emitter.emit(structure)

    assert markdown.startswith("## ")

    graph_builder.index_directory(sample_project_dir)
    query_text = "Where is the User model defined?"
    resolved_task = _resolve_task_type(query_text, "AUTO")
    result = graph_querier.query_v4(
        query_text,
        role="maintainer",
        task_type=resolved_task,
    )
    assert result.ranked_nodes
    assert result.total_tokens > 0


def test_v4_pipeline_rbac_enforced(graph_builder, graph_querier, sample_project_dir):
    """Permissions restrict context to role-appropriate nodes."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    graph_builder.index_directory(sample_project_dir)
    graph_builder.index_directory(repo_root / "tests")

    query_text = "gate stale detection"
    developer = graph_querier.query_v4(query_text, role="developer", task_type="REVIEW")
    auditor = graph_querier.query_v4(query_text, role="auditor", task_type="REVIEW")

    assert not developer.ranked_nodes
    assert auditor.ranked_nodes
    assert all("/tests/" in n.filepath.replace("\\", "/").lower() for n, _ in auditor.ranked_nodes)


def test_v4_pipeline_stale_nodes_flagged(graph_builder, graph_querier, tmp_path):
    """Nodes older than threshold are flagged as STALE in output."""
    stale_file = tmp_path / "stale_component.py"
    stale_file.write_text("def stale_component():\n    return 'ok'\n", encoding="utf-8")

    old_ts = time.time() - (60 * 24 * 3600)
    os.utime(stale_file, (old_ts, old_ts))

    graph_builder.index_file(stale_file)
    result = graph_querier.query_v4(
        "stale_component",
        role="maintainer",
        stale_after_days=30,
        task_type="REVIEW",
    )

    assert result.ranked_nodes
    assert any(node.name.startswith("[STALE]") for node, _ in result.ranked_nodes)
