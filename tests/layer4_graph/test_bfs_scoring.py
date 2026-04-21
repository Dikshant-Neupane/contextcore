"""
Layer 4 BFS scoring unit tests — T-066 to T-068.
Phase: v2 🟡 ACTIVE (not yet implemented)
Status: ⬜ Write implementation in src/contextcore/layer4_graph/querier.py first.
"""

import pytest


def test_score_direct_match_gt_indirect():
    """T-066: A directly matched node scores higher than a node reached via traversal."""
    from contextcore.layer4_graph.querier import score_node
    direct   = score_node(depth=0, edge_type="DIRECT")
    indirect = score_node(depth=2, edge_type="CALLS")
    assert direct > indirect, (
        f"Direct match score ({direct}) must exceed indirect ({indirect})"
    )


def test_score_inherits_gt_contains():
    """T-067: INHERITS edges carry higher weight than CONTAINS edges at the same depth."""
    from contextcore.layer4_graph.querier import score_node
    inherits = score_node(depth=1, edge_type="INHERITS")
    contains = score_node(depth=1, edge_type="CONTAINS")
    assert inherits >= contains, (
        f"INHERITS score ({inherits}) must be ≥ CONTAINS score ({contains})"
    )


def test_recent_node_bonus_applied():
    """T-068: A recently modified node receives a recency bonus in its score."""
    from contextcore.layer4_graph.querier import score_node
    recent = score_node(depth=1, edge_type="CALLS", days_since_modified=0)
    old    = score_node(depth=1, edge_type="CALLS", days_since_modified=365)
    assert recent >= old, (
        f"Recent node score ({recent}) must be ≥ old node score ({old})"
    )
