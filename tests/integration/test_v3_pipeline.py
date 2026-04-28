"""
v3 pipeline integration test.
Phase: v3 ACTIVE
Requires: src/contextcore/layer3_intent/ implementation
"""

from __future__ import annotations

import time

from contextcore.cli.main import _resolve_task_type
from contextcore.layer3_intent.classifier import classify_query


def test_full_l1_l3_l4_l5_pipeline(
    parser,
    extractor,
    emitter,
    graph_builder,
    graph_querier,
    sample_project_dir,
    class_with_methods_file,
):
    """L1 → L3 → L4 → L5: parse, classify intent, query graph, emit."""
    parse_result = parser.parse(class_with_methods_file)
    structure = extractor.extract(parse_result)
    markdown = emitter.emit(structure)

    assert markdown.startswith("## ")

    graph_builder.index_directory(sample_project_dir)
    prompt = "Why is the user service missing from the project listing flow?"
    intent = classify_query(prompt)
    result = graph_querier.query(prompt, task_type=intent.task_type.value)

    assert intent.task_type.value == "DEBUG"
    assert result.ranked_nodes
    assert result.total_tokens > 0


def test_v3_pipeline_intent_routes_correctly():
    """Intent classifier routes to the correct subgraph mode (DEBUG/REFACTOR/etc.)."""
    prompts = {
        "Why is my BFS subgraph missing edges after indexing?": "DEBUG",
        "Refactor the querier scoring function to be easier to tune.": "REFACTOR",
        "Scaffold a new layer module for intent routing.": "SCAFFOLD",
        "Summarize what the post-commit hook does and where it is installed.": "REVIEW",
        "Are we ever sending source code off-machine? Show enforcement points.": "SECURITY",
    }

    for prompt, expected in prompts.items():
        assert _resolve_task_type(prompt, "AUTO") == expected


def test_v3_pipeline_latency_under_150ms(graph_builder, graph_querier, sample_project_dir):
    """End-to-end latency including intent classification ≤150ms."""
    graph_builder.index_directory(sample_project_dir)

    prompt = "Where is the User model defined?"
    latencies_ms = []
    for _ in range(5):
        t0 = time.perf_counter()
        resolved = _resolve_task_type(prompt, "AUTO")
        result = graph_querier.query(prompt, task_type=resolved)
        latencies_ms.append((time.perf_counter() - t0) * 1000)
        assert result.ranked_nodes

    avg_latency = sum(latencies_ms) / len(latencies_ms)
    assert avg_latency <= 150.0, f"v3 pipeline latency {avg_latency:.1f}ms > 150ms"
