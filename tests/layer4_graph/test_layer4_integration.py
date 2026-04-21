"""
Layer 4 end-to-end integration tests — T-069, T-070.
Phase: v2 🟡 ACTIVE
Status: ✅ Builder + querier implemented
"""

import pytest


def test_build_then_query_roundtrip(graph_builder, graph_querier, sample_project_dir):
    """T-069: Index sample_project, then query it — must return non-empty results."""
    graph_builder.index_directory(sample_project_dir)
    result = graph_querier.query("Where is the User model defined?")
    assert len(result.ranked_nodes) > 0
    assert result.total_tokens > 0


def test_incremental_reindex_speed(graph_builder, sample_project_dir, tmp_path):
    """T-070: Re-indexing a single changed file completes in <2s."""
    import time
    graph_builder.index_directory(sample_project_dir)

    # Simulate a single file change
    target = next(sample_project_dir.glob("models/*.py"))
    t0 = time.perf_counter()
    graph_builder.index_file(target)
    elapsed = time.perf_counter() - t0

    assert elapsed < 2.0, (
        f"Incremental re-index of one file took {elapsed:.2f}s > 2s budget"
    )
