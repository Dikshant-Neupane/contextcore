"""
CONTEXTCORE — Master Test Runner
Usage:
    python tests/run_all.py              # Run all active tests
    python tests/run_all.py --phase v1   # Run only v1 tests
    python tests/run_all.py --gate       # Run only kill tests
    python tests/run_all.py --full       # Run everything including locked

Outputs:
    tests/results/latest.md             <- Always overwritten
    tests/results/archive/TIMESTAMP.md  <- Permanent record

Exit codes:
    0 = Selected test run passed
    1 = One or more non-gate tests failed
    2 = Kill test failed (phase gate blocked)
"""

from __future__ import annotations

import argparse
import datetime
import re
import subprocess
import sys

# Ensure stdout/stderr can handle Unicode on Windows cp1252 terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
import time
from pathlib import Path

REPO_ROOT   = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "tests" / "results"
ARCHIVE_DIR = RESULTS_DIR / "archive"
VERSION_ORDER = ["v1", "v2", "v3", "v4"]
GATE_REQUIREMENTS = {
    "v1": ("5x compression, 80% accuracy", "11.38x, 100%"),
    "v2": ("8/10 subgraph, <=500ms, <=600tok", "sealed"),
    "v3": ("Intent 7/10 queries", "sealed"),
    "v4": ("RBAC + freshness", "gate passed"),
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="CONTEXTCORE Test Runner")
    p.add_argument("--phase", type=str, help="Run only tests for this phase (v1/v2/v3/v4)")
    p.add_argument("--gate", action="store_true", help="Run only gate kill tests")
    p.add_argument("--full", action="store_true", help="Run all tests including locked")
    p.add_argument("--no-report", action="store_true", help="Skip report generation")
    return p.parse_args()


def build_pytest_args(args: argparse.Namespace) -> list[str]:
    base = [sys.executable, "-m", "pytest", "--tb=short", "-v"]

    if args.gate:
        return base + ["tests/gate_checks/"]

    if args.phase:
        return base + ["tests/", "-k", args.phase]

    if args.full:
        return base + ["tests/"]

    # Default: all tests, ignore generated results dir
    return base + ["tests/", "--ignore=tests/results"]


def run_tests(pytest_args: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        pytest_args,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return result.returncode, result.stdout + result.stderr


def extract_summary(output: str) -> dict[str, int]:
    summary = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0, "total": 0}
    for line in output.splitlines():
        # e.g. "33 passed, 2 skipped in 0.12s" or "===== 33 passed ====="
        if "passed" in line or "failed" in line or "error" in line:
            for count, label in re.findall(r"(\d+) (\w+)", line):
                if label in summary:
                    summary[label] = int(count)
    summary["total"] = summary["passed"] + summary["failed"] + summary["errors"]
    return summary


def get_current_version() -> str:
    """Read the active project phase from tests/conftest.py."""
    conftest_path = REPO_ROOT / "tests" / "conftest.py"
    try:
        content = conftest_path.read_text(encoding="utf-8")
    except OSError:
        return "v1"

    match = re.search(r'^CURRENT_VERSION\s*=\s*["\'](v\d+)["\']', content, re.MULTILINE)
    if not match:
        return "v1"

    current_version = match.group(1)
    return current_version if current_version in VERSION_ORDER else "v1"


def get_sealed_version() -> str:
    """Read the highest sealed project phase from tests/conftest.py."""
    conftest_path = REPO_ROOT / "tests" / "conftest.py"
    try:
        content = conftest_path.read_text(encoding="utf-8")
    except OSError:
        return "v1"

    match = re.search(r'^SEALED_VERSION\s*=\s*["\'](v\d+)["\']', content, re.MULTILINE)
    if not match:
        return "v1"

    sealed_version = match.group(1)
    return sealed_version if sealed_version in VERSION_ORDER else "v1"


def build_gate_rows(current_version: str) -> list[str]:
    """Build gate status rows based on the active project phase."""
    try:
        current_index = VERSION_ORDER.index(current_version)
    except ValueError:
        current_index = 0

    try:
        sealed_index = VERSION_ORDER.index(get_sealed_version())
    except ValueError:
        sealed_index = 0

    rows = []
    for index, version in enumerate(VERSION_ORDER):
        required, notes = GATE_REQUIREMENTS[version]
        if index <= sealed_index:
            status = "[PASS] PASSED"
        elif index == current_index:
            status = "[ACTIVE] ACTIVE"
        else:
            status = "[LOCKED] LOCKED"
            notes = "-"

        rows.append(f"| {version} Gate | {status} | {required} | {notes} |")

    return rows


def write_report(
    output: str,
    summary: dict[str, int],
    exit_code: int,
    duration_s: float,
    mode: str,
) -> Path:
    timestamp  = datetime.datetime.now(datetime.UTC)
    ts_str     = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    file_ts    = timestamp.strftime("%Y-%m-%d_%H%M%S")
    status_icon = "✅ ALL PASSED" if exit_code == 0 else "❌ FAILURES DETECTED"
    gate_rows = build_gate_rows(get_current_version())

    lines = [
        "# CONTEXTCORE — Test Run Report",
        f"**Date:** {ts_str}",
        f"**Mode:** {mode}",
        f"**Duration:** {duration_s:.2f}s",
        f"**Status:** {status_icon}",
        "",
        "## Summary",
        "| Metric   | Count |",
        "|----------|-------|",
        f"| ✅ Passed  | {summary['passed']} |",
        f"| ❌ Failed  | {summary['failed']} |",
        f"| ⏭ Skipped | {summary['skipped']} |",
        f"| 💥 Errors  | {summary['errors']} |",
        f"| **Total**  | **{summary['total']}** |",
        "",
        "## Gate Status",
        "| Gate | Status | Required | Notes |",
        "|------|--------|----------|-------|",
        *gate_rows,
        "",
        "## Full Output",
        "```",
        output[:8000],
        "```",
        "",
        f"*Report generated by tests/run_all.py at {ts_str}*",
    ]

    content = "\n".join(lines)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "latest.md").write_text(content, encoding="utf-8")

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = ARCHIVE_DIR / f"{file_ts}.md"
    archive_path.write_text(content, encoding="utf-8")

    return archive_path


def print_gate_verdict(summary: dict[str, int], exit_code: int, mode: str) -> int:
    """Print a mode-aware verdict and return the corresponding process exit code."""
    print("\n" + "═" * 55)
    mode_label = "GATE TESTS" if mode == "gate" else ("FULL TEST SUITE" if mode == "full" else "ALL ACTIVE TESTS")

    if exit_code == 0:
        print(f"[PASS]  {mode_label} PASSED")
        print(
            f"   {summary['passed']} passed | "
            f"{summary['skipped']} skipped | "
            f"{summary['failed']} failed"
        )
        print("\n   [+] Check tests/results/latest.md for full report")
        print("   [+] Update TEST_MANIFEST.md status column")
        return 0

    print("[FAIL]  TESTS FAILED")
    print(
        f"   {summary['passed']} passed | "
        f"{summary['failed']} failed | "
        f"{summary['errors']} errors"
    )
    if mode == "gate":
        print("\n   [!] Phase gate is blocked until kill tests pass.")
        print("   [!] Do NOT advance to next phase until failures are resolved.")
        print("   [+] See tests/results/latest.md for failure details")
        return 2

    print("\n   [+] See tests/results/latest.md for failure details")
    return 1


def main() -> int:
    args     = parse_args()
    mode     = "gate" if args.gate else ("full" if args.full else f"phase={args.phase or 'active'}")
    cmd      = build_pytest_args(args)

    print(f"[TEST] CONTEXTCORE Test Runner | Mode: {mode}")
    print(f"   Command: {' '.join(cmd)}")
    print("─" * 55)

    t_start          = time.perf_counter()
    exit_code, output = run_tests(cmd)
    duration         = time.perf_counter() - t_start

    summary = extract_summary(output)

    if not args.no_report:
        archive_path = write_report(output, summary, exit_code, duration, mode)
        print(f"\n[REPORT] Archived: {archive_path.relative_to(REPO_ROOT)}")

    return print_gate_verdict(summary, exit_code, mode)


if __name__ == "__main__":
    sys.exit(main())
