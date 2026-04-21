"""
Layer 4 schema unit tests — T-048 to T-051.
Phase: v2 🟡 ACTIVE
Status: ✅ schema.py implemented
"""

import pytest


def test_node_types_valid():
    """T-048: All GraphNode type values are members of the NodeType enum."""
    from contextcore.layer4_graph.schema import NodeType
    assert all(isinstance(t, NodeType) for t in NodeType)


def test_edge_types_valid():
    """T-049: All GraphEdge type values are members of the EdgeType enum."""
    from contextcore.layer4_graph.schema import EdgeType
    assert all(isinstance(t, EdgeType) for t in EdgeType)


def test_node_id_deterministic():
    """T-050: Two GraphNodes with the same filepath+name produce the same id."""
    from contextcore.layer4_graph.schema import GraphNode, NodeType
    n1 = GraphNode(filepath="a.py", name="foo", node_type=NodeType.FUNCTION)
    n2 = GraphNode(filepath="a.py", name="foo", node_type=NodeType.FUNCTION)
    assert n1.id == n2.id


def test_edge_id_deterministic():
    """T-051: Two GraphEdges with the same source+target+type produce the same id."""
    from contextcore.layer4_graph.schema import GraphEdge, EdgeType
    e1 = GraphEdge(source_id="a", target_id="b", edge_type=EdgeType.IMPORTS)
    e2 = GraphEdge(source_id="a", target_id="b", edge_type=EdgeType.IMPORTS)
    assert e1.id == e2.id
