"""
CONTEXTCORE — Subgraph Accuracy Benchmark
Measures how accurately the querier returns expected nodes for a set of labeled queries.

Usage:
    python benchmarks/subgraph_accuracy.py [--db-path PATH] [--verbose]

Output:
    Accuracy score, per-query breakdown, latency stats.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Add src to path so this runs from repo root without install
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from contextcore.layer4_graph.querier import GraphQuerier

# ---------------------------------------------------------------------------
# Sample labeled queries against the sample_project corpus.
# Each entry: (query_text, expected_node_names_list)
# ---------------------------------------------------------------------------
SAMPLE_QUERIES: list[tuple[str, list[str]]] = [
    ("User", ["User", "user"]),
    ("build_user", ["build_user"]),
    ("ping", ["ping"]),
    ("Project", ["Project", "project"]),
    ("deactivate", ["deactivate", "deactivate_user"]),
    ("health", ["ping", "readiness_check", "build_health_report"]),
    ("listing", ["list_users", "list_projects"]),
    ("config", ["config"]),
    ("math", ["add", "multiply"]),
    ("strings", ["strings"]),
]


def run_benchmark(db_path: Path, verbose: bool = False) -> None:
    if not db_path.exists():
        print(f"[FAIL] DB not found: {db_path}")
        print("[INFO] Run: python -m contextcore.cli.main index <project_path>")
        sys.exit(1)

    querier = GraphQuerier(db_path=db_path)

    passed = 0
    failed = 0
    latencies: list[float] = []
    token_counts: list[int] = []

    print(f"[INFO] Running {len(SAMPLE_QUERIES)} subgraph accuracy queries")
    print(f"[INFO] DB: {db_path}")
    print()

    for query_text, expected_names in SAMPLE_QUERIES:
        t0 = time.perf_counter()
        result = querier.query(query_text)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        latencies.append(elapsed_ms)
        token_counts.append(result.total_tokens)

        returned_names = [node.name for node, _ in result.ranked_nodes]
        hits = [e for e in expected_names if e in returned_names]
        miss = [e for e in expected_names if e not in returned_names]

        ok = len(miss) == 0
        if ok:
            passed += 1
            status = "[PASS]"
        else:
            failed += 1
            status = "[FAIL]"

        if verbose or not ok:
            print(
                f"  {status} query={query_text!r:20s} "
                f"hits={len(hits)}/{len(expected_names)} "
                f"latency={elapsed_ms:.1f}ms tokens={result.total_tokens}"
            )
            if miss:
                print(f"         missed: {miss}")

    accuracy = passed / len(SAMPLE_QUERIES)
    avg_latency = sum(latencies) / len(latencies)
    avg_tokens = sum(token_counts) / len(token_counts)
    max_latency = max(latencies)

    print()
    print(f"[INFO] Accuracy:     {passed}/{len(SAMPLE_QUERIES)} ({accuracy:.0%})")
    print(f"[INFO] Avg latency:  {avg_latency:.1f}ms  (max: {max_latency:.1f}ms)")
    print(f"[INFO] Avg tokens:   {avg_tokens:.0f}")

    gate_pass = accuracy >= 0.8 and avg_latency <= 500 and avg_tokens <= 600
    print()
    if gate_pass:
        print("[PASS] Subgraph accuracy benchmark PASSED (>=80% accuracy, <=500ms, <=600 tokens)")
    else:
        print("[FAIL] Subgraph accuracy benchmark FAILED")
        if accuracy < 0.8:
            print(f"  accuracy {accuracy:.0%} < 80%")
        if avg_latency > 500:
            print(f"  avg latency {avg_latency:.1f}ms > 500ms")
        if avg_tokens > 600:
            print(f"  avg tokens {avg_tokens:.0f} > 600")


def main() -> None:
    parser = argparse.ArgumentParser(description="CONTEXTCORE subgraph accuracy benchmark")
    parser.add_argument(
        "--db-path",
        default=".contextcore/contextcore.db",
        help="Path to the graph database (default: .contextcore/contextcore.db)",
    )
    parser.add_argument("--verbose", action="store_true", help="Print all query results")
    args = parser.parse_args()

    run_benchmark(db_path=Path(args.db_path), verbose=args.verbose)


if __name__ == "__main__":
    main()
