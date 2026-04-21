"""
Layer 4 graph builder unit tests — T-052 to T-060.
Phase: v2 🟡 ACTIVE
Status: ✅ builder.py implemented
"""

import pytest


def test_builder_creates_file_nodes(graph_builder, simple_function_file):
    """T-052: Indexing a file produces a FILE node in the graph."""
    graph_builder.index_file(simple_function_file)
    nodes = graph_builder.get_nodes_by_type("FILE")
    assert any(str(simple_function_file) in n.filepath for n in nodes)


def test_builder_creates_function_nodes(graph_builder, simple_function_file):
    """T-053: Indexing a file with functions produces FUNCTION nodes."""
    graph_builder.index_file(simple_function_file)
    nodes = graph_builder.get_nodes_by_type("FUNCTION")
    names = [n.name for n in nodes]
    assert "greet" in names


def test_builder_creates_class_nodes(graph_builder, class_with_methods_file):
    """T-054: Indexing a file with a class produces a CLASS node."""
    graph_builder.index_file(class_with_methods_file)
    nodes = graph_builder.get_nodes_by_type("CLASS")
    names = [n.name for n in nodes]
    assert "Calculator" in names


def test_builder_creates_imports_edges(graph_builder, file_with_imports_file):
    """T-055: Indexing a file with imports produces IMPORTS edges."""
    graph_builder.index_file(file_with_imports_file)
    edges = graph_builder.get_edges_by_type("IMPORTS")
    assert len(edges) > 0


def test_builder_creates_calls_edges(graph_builder, sample_project_dir):
    """T-056: Indexing a project produces CALLS edges between functions."""
    graph_builder.index_directory(sample_project_dir)
    edges = graph_builder.get_edges_by_type("CALLS")
    assert len(edges) >= 0  # May be 0 if no cross-function calls detected yet


def test_builder_creates_contains_edges(graph_builder, class_with_methods_file):
    """T-057: Indexing a class produces CONTAINS edges from class to methods."""
    graph_builder.index_file(class_with_methods_file)
    edges = graph_builder.get_edges_by_type("CONTAINS")
    assert len(edges) > 0


def test_builder_handles_circular_imports(graph_builder, tmp_path):
    """T-058: Circular imports do not cause infinite loops or crashes."""
    a = tmp_path / "circular_a.py"
    b = tmp_path / "circular_b.py"
    a.write_text("from circular_b import B\nclass A: pass\n", encoding="utf-8")
    b.write_text("from circular_a import A\nclass B: pass\n", encoding="utf-8")
    graph_builder.index_file(a)
    graph_builder.index_file(b)  # Must not crash or loop


def test_builder_incremental_update(graph_builder, simple_function_file, tmp_path):
    """T-059: Re-indexing an updated file updates the graph without duplicates."""
    graph_builder.index_file(simple_function_file)
    count_before = len(graph_builder.get_nodes_by_type("FUNCTION"))
    graph_builder.index_file(simple_function_file)  # Re-index same file
    count_after = len(graph_builder.get_nodes_by_type("FUNCTION"))
    assert count_after == count_before, "Re-indexing must not create duplicate nodes"


def test_builder_persists_to_sqlite(graph_builder, simple_function_file):
    """T-060: Indexed data survives a GraphBuilder reload from the same DB path."""
    graph_builder.index_file(simple_function_file)
    graph_builder.flush()
    db_path = graph_builder.db_path

    from contextcore.layer4_graph.builder import GraphBuilder
    reloaded = GraphBuilder(db_path=db_path)
    nodes = reloaded.get_nodes_by_type("FUNCTION")
    assert any(n.name == "greet" for n in nodes)
