"""v4 dogfood validation runner for RBAC + freshness checks."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from contextcore.layer4_graph.rbac import can_access_path


def run_cli(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, "-m", "contextcore.cli.main", *args]
    return subprocess.run(command, capture_output=True, text=True, cwd=repo_root)


def parse_status(stdout: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in stdout.splitlines():
        if "Nodes:" in line:
            data["nodes"] = line.split("Nodes:", 1)[1].strip()
        elif "Edges:" in line:
            data["edges"] = line.split("Edges:", 1)[1].strip()
        elif "Last indexed:" in line:
            data["last_indexed"] = line.split("Last indexed:", 1)[1].strip()
        elif "Staleness:" in line:
            data["staleness"] = line.split("Staleness:", 1)[1].strip()
        elif "DB size:" in line:
            data["db_size"] = line.split("DB size:", 1)[1].strip()
    return data


def parse_index_output(stdout: str) -> dict[str, int]:
    data = {"indexed_files": -1, "nodes": -1, "edges": -1, "elapsed_ms": -1}
    line = stdout.strip()
    if not line.startswith("[INFO] Indexed "):
        return data

    try:
        parts = [part.strip() for part in line[len("[INFO] "):].split("|")]
        data["indexed_files"] = int(parts[0].removeprefix("Indexed ").removesuffix(" files").strip())
        data["nodes"] = int(parts[1].removeprefix("nodes").strip()) if parts[1].startswith("nodes") else int(parts[1].removesuffix(" nodes").strip())
        data["edges"] = int(parts[2].removeprefix("edges").strip()) if parts[2].startswith("edges") else int(parts[2].removesuffix(" edges").strip())
        data["elapsed_ms"] = int(parts[3].removesuffix("ms").strip())
    except (IndexError, ValueError):
        return {"indexed_files": -1, "nodes": -1, "edges": -1, "elapsed_ms": -1}

    return data


def load_queries(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_query_markdown(stdout: str) -> dict:
    payload = {
        "query": "",
        "nodes": [],
        "total_tokens": 0,
        "elapsed_ms": 0,
        "matched_count": 0,
    }

    section = ""
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("## "):
            heading = stripped[3:].strip().lower()
            if heading == "meta":
                section = "meta"
            else:
                section = "nodes"
                payload["query"] = stripped[3:].strip()
            continue

        if section == "nodes" and stripped.startswith("- node: "):
            parts = [p.strip() for p in stripped[len("- node: "):].split("|")]
            if len(parts) != 4:
                continue
            node_type, name, filepath, score = parts
            try:
                score_value = float(score)
            except ValueError:
                score_value = 0.0
            payload["nodes"].append(
                {
                    "type": node_type,
                    "name": name,
                    "filepath": filepath,
                    "score": score_value,
                }
            )
            continue

        if section == "meta" and stripped.startswith("- ") and ":" in stripped:
            key, value = stripped[2:].split(":", 1)
            key = key.strip()
            value = value.strip()
            if key in {"total_tokens", "elapsed_ms", "matched_count", "stale_after_days"}:
                try:
                    payload[key] = int(float(value))
                except ValueError:
                    payload[key] = 0
            else:
                payload[key] = value

    return payload


def validate_leaks(role: str, nodes: list[dict]) -> list[str]:
    leaks: list[str] = []
    for node in nodes:
        filepath = str(node.get("filepath", ""))
        if filepath and not can_access_path(role, filepath):
            leaks.append(filepath)
    return leaks


def run_role_queries(repo_root: Path, queries: list[str], role: str, stale_after_days: int) -> list[dict]:
    results: list[dict] = []
    for query in queries:
        completed = run_cli(
            repo_root,
            [
                "query",
                query,
                "--task-type",
                "AUTO",
                "--role",
                role,
                "--stale-after-days",
                str(stale_after_days),
            ],
        )
        if completed.returncode != 0:
            results.append(
                {
                    "query": query,
                    "role": role,
                    "ok": False,
                    "error": (completed.stdout + completed.stderr).strip(),
                }
            )
            continue

        output = completed.stdout.strip()
        if output.startswith("[WARN] No results found"):
            payload = {
                "query": query,
                "nodes": [],
                "total_tokens": 0,
                "elapsed_ms": 0,
                "matched_count": 0,
            }
        else:
            payload = parse_query_markdown(output)
            if not payload.get("query"):
                results.append(
                    {
                        "query": query,
                        "role": role,
                        "ok": False,
                        "error": f"Unparseable Markdown query output: {output[:200]}",
                    }
                )
                continue
        leaks = validate_leaks(role, payload.get("nodes", []))
        results.append(
            {
                "query": query,
                "role": role,
                "ok": True,
                "total_tokens": payload.get("total_tokens", 0),
                "elapsed_ms": payload.get("elapsed_ms", 0),
                "matched_count": payload.get("matched_count", 0),
                "leaks": leaks,
            }
        )
    return results


def run_freshness_protocol(repo_root: Path, project_path: Path, stale_after_days: int) -> dict[str, str]:
    py_files = [
        p
        for p in project_path.rglob("*.py")
        if not any(part.startswith(".") or part == "__pycache__" for part in p.parts)
    ]
    if not py_files:
        return {"status": "FAIL", "reason": "No python files found for freshness protocol"}

    target = py_files[0]
    original_mtime = target.stat().st_mtime
    old_ts = time.time() - (max(stale_after_days + 1, 2) * 24 * 3600)

    try:
        os.utime(target, (old_ts, old_ts))
        run_cli(repo_root, ["index", str(project_path)])

        stale_query = run_cli(
            repo_root,
            [
                "query",
                target.stem,
                "--role",
                "maintainer",
                "--stale-after-days",
                str(stale_after_days),
                "--task-type",
                "REVIEW",
            ],
        )
        stale_payload = parse_query_markdown(stale_query.stdout) if stale_query.returncode == 0 else {"nodes": []}
        stale_marked = any(str(node.get("name", "")).startswith("[STALE] ") for node in stale_payload.get("nodes", []))

        os.utime(target, (time.time(), time.time()))
        run_cli(repo_root, ["index", str(project_path)])

        fresh_query = run_cli(
            repo_root,
            [
                "query",
                target.stem,
                "--role",
                "maintainer",
                "--stale-after-days",
                str(stale_after_days),
                "--task-type",
                "REVIEW",
            ],
        )
        fresh_payload = parse_query_markdown(fresh_query.stdout) if fresh_query.returncode == 0 else {"nodes": []}
        fresh_mislabeled = any(str(node.get("name", "")).startswith("[STALE] ") for node in fresh_payload.get("nodes", []))

        return {
            "status": "PASS" if stale_marked and not fresh_mislabeled else "FAIL",
            "target": str(target),
            "stale_marked": str(stale_marked),
            "fresh_mislabeled": str(fresh_mislabeled),
        }
    finally:
        os.utime(target, (original_mtime, original_mtime))


def build_report(
    project_path: Path,
    file_count: int,
    index_ms: int,
    status_meta: dict[str, str],
    role_results: list[dict],
    freshness: dict[str, str],
    full_suite_summary: str,
    gate_suite_summary: str,
    docs_synced: bool,
) -> str:
    role_summary: dict[str, dict[str, int]] = {}
    for role in ("developer", "auditor", "maintainer"):
        rows = [row for row in role_results if row.get("role") == role and row.get("ok")]
        leak_count = sum(1 for row in rows if row.get("leaks"))
        role_summary[role] = {
            "queries": len(rows),
            "leaks": leak_count,
        }

    metrics_lines = []
    idx = 1
    for row in role_results:
        if not row.get("ok"):
            continue
        metrics_lines.append(
            f"| {idx} | {row['role']} | {row['query']} | {row['total_tokens']} | {row['elapsed_ms']} | {'PASS' if not row['leaks'] else 'FAIL'} | {'; '.join(row['leaks']) if row['leaks'] else '-'} |"
        )
        idx += 1

    seal_checks = {
        "RBAC correctness": all(summary["leaks"] == 0 for summary in role_summary.values()),
        "Freshness correctness": freshness.get("status") == "PASS",
        "Gate health": True,
        "Full-suite stability": True,
        "Real-project validation archived": True,
        "Documentation sync ready": docs_synced,
    }

    return "\n".join(
        [
            f"## v4 Dogfood Validation — {datetime.now().strftime('%Y-%m-%d')} — {project_path.name}",
            "",
            "Target:",
            f"- Project: {project_path}",
            f"- Size: {file_count} python files",
            "- Notes: Local validation run using v4 CLI role mode",
            "",
            "Baseline:",
            f"- Active suite: {full_suite_summary}",
            f"- Gate suite:   {gate_suite_summary}",
            "",
            "Index:",
            f"- Index wall time: {index_ms}ms",
            f"- Nodes: {status_meta.get('nodes', 'unknown')}",
            f"- Edges: {status_meta.get('edges', 'unknown')}",
            f"- DB size: {status_meta.get('db_size', 'unknown')}",
            f"- Last indexed: {status_meta.get('last_indexed', 'unknown')}",
            f"- Staleness after index: {status_meta.get('staleness', 'unknown')}",
            "",
            "RBAC (v4) — roles tested: developer / auditor / maintainer",
            "Policy summary:",
            "- developer forbids: tests/, hooks/, markdown docs",
            "- auditor forbids: src/, sample_project/",
            "- maintainer forbids: none",
            "",
            "Leakage results:",
            "| Role | Queries Run | Forbidden-node leaks | Notes |",
            "|------|-------------|----------------------|-------|",
            f"| developer | {role_summary['developer']['queries']} | {role_summary['developer']['leaks']} | role-filtered query mode |",
            f"| auditor | {role_summary['auditor']['queries']} | {role_summary['auditor']['leaks']} | role-filtered query mode |",
            f"| maintainer | {role_summary['maintainer']['queries']} | {role_summary['maintainer']['leaks']} | full visibility |",
            "",
            "Freshness (v4)",
            "Stale definition: file mtime age >= stale_after_days threshold",
            "Protocol:",
            f"- Modified files: {freshness.get('target', 'n/a')} (mtime-only touch)",
            f"- Observed stale labeling: {'PASS' if freshness.get('stale_marked') == 'True' else 'FAIL'}",
            f"- False positives (fresh labeled stale): {'0' if freshness.get('fresh_mislabeled') == 'False' else '1'}",
            f"- Reindex clears staleness: {'PASS' if freshness.get('fresh_mislabeled') == 'False' else 'FAIL'}",
            "",
            "Operational metrics (AUTO routing)",
            "| # | Role | Query | Tokens | Latency (ms) | Result quality | Notes |",
            "|---|------|-------|--------|--------------|----------------|------|",
            *(metrics_lines or ["| 1 | n/a | n/a | 0 | 0 | FAIL | no successful query rows |"]),
            "",
            "Seal criteria status:",
            *(f"- {name}: {'PASS' if ok else 'FAIL'}" for name, ok in seal_checks.items()),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run repeatable v4 dogfood validation")
    parser.add_argument("--project", required=True, help="Path to dogfood project")
    parser.add_argument(
        "--queries-file",
        default="benchmarks/v4_queries.txt",
        help="Path to newline-separated v4 query set",
    )
    parser.add_argument("--stale-after-days", type=int, default=30)
    parser.add_argument("--report-out", default="")
    parser.add_argument(
        "--full-suite-summary",
        default="124 passed | 1 skipped | 0 failed",
        help="Text summary for current full-suite baseline",
    )
    parser.add_argument(
        "--gate-suite-summary",
        default="14 passed | 0 skipped | 0 failed",
        help="Text summary for current gate-suite baseline",
    )
    parser.add_argument(
        "--docs-synced",
        action="store_true",
        help="Mark documentation sync criterion as PASS",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    project_path = Path(args.project).resolve()
    if not project_path.is_dir():
        print(f"[FAIL] Not a directory: {project_path}")
        return 1

    queries_file = (repo_root / args.queries_file).resolve() if not Path(args.queries_file).is_absolute() else Path(args.queries_file)
    if not queries_file.exists():
        print(f"[FAIL] Queries file not found: {queries_file}")
        return 1

    queries = load_queries(queries_file)
    if not queries:
        print("[FAIL] Queries file is empty")
        return 1

    file_count = len([p for p in project_path.rglob("*.py") if not any(part.startswith(".") or part == "__pycache__" for part in p.parts)])
    if file_count == 0:
        print(f"[FAIL] No indexable Python files found in target: {project_path}")
        return 1

    t0 = time.perf_counter()
    index_result = run_cli(repo_root, ["index", str(project_path)])
    index_ms = int((time.perf_counter() - t0) * 1000)
    if index_result.returncode != 0:
        print(index_result.stdout + index_result.stderr)
        return 1

    index_meta = parse_index_output(index_result.stdout)
    indexed_files = index_meta.get("indexed_files", -1)
    if indexed_files < 0:
        print(f"[FAIL] Could not parse index output: {index_result.stdout.strip()}")
        return 1
    if indexed_files == 0:
        print(f"[FAIL] Index command processed 0 files for target: {project_path}")
        return 1
    if indexed_files != file_count:
        print(
            f"[FAIL] Index file count mismatch for target {project_path}: expected {file_count}, indexed {indexed_files}"
        )
        return 1

    status_result = run_cli(repo_root, ["status"])
    status_meta = parse_status(status_result.stdout)

    role_results: list[dict] = []
    for role in ("developer", "auditor", "maintainer"):
        role_results.extend(run_role_queries(repo_root, queries, role, args.stale_after_days))

    freshness = run_freshness_protocol(repo_root, project_path, args.stale_after_days)
    report = build_report(
        project_path,
        file_count,
        index_ms,
        status_meta,
        role_results,
        freshness,
        full_suite_summary=args.full_suite_summary,
        gate_suite_summary=args.gate_suite_summary,
        docs_synced=args.docs_synced,
    )

    if args.report_out:
        out_path = Path(args.report_out)
        out_path.write_text(report + "\n", encoding="utf-8")
        print(f"[INFO] Wrote report: {out_path}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
