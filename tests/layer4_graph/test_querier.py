"""
Layer 4 graph querier unit tests — T-061 to T-065.
Phase: v2 🟡 ACTIVE (not yet implemented)
Status: ⬜ Write implementation in src/contextcore/layer4_graph/querier.py first.
"""

import pytest


def test_querier_returns_subgraph_result(populated_graph, graph_querier):
    """T-061: query() returns a SubgraphResult with ranked_nodes and total_tokens."""
    result = graph_querier.query("Where is the user model defined?")
    assert result is not None
    assert hasattr(result, "ranked_nodes")
    assert hasattr(result, "total_tokens")
    assert len(result.ranked_nodes) > 0


def test_bfs_depth_3_max(populated_graph, graph_querier):
    """T-062: BFS traversal does not exceed depth 3 from the seed node."""
    result = graph_querier.query("show me the Calculator class")
    depths = [depth for _, depth in result.ranked_nodes]
    assert all(d <= 3 for d in depths), (
        f"BFS exceeded depth 3: {max(depths)}"
    )


def test_direct_match_highest_score(populated_graph, graph_querier):
    """T-063: Directly matched node has a higher relevance score than indirect matches."""
    result = graph_querier.query("greet function")
    scores = [score for _, score in result.ranked_nodes]
    assert scores == sorted(scores, reverse=True), "Nodes must be ranked by descending score"
    assert scores[0] > scores[-1] if len(scores) > 1 else True


def test_result_within_token_budget(populated_graph, graph_querier):
    """T-064: Returned subgraph total_tokens ≤ 600."""
    result = graph_querier.query("main entry point")
    assert result.total_tokens <= 600, (
        f"Subgraph token count {result.total_tokens} exceeds budget of 600"
    )


def test_result_within_latency_budget(populated_graph, graph_querier):
    """T-065: Query latency ≤ 500ms."""
    import time
    t0 = time.perf_counter()
    graph_querier.query("Calculator add method")
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert elapsed_ms <= 500, f"Query took {elapsed_ms:.1f}ms > 500ms budget"
