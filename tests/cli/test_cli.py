"""
CLI unit tests — T-071 to T-076.
Phase: v2 ACTIVE
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Path to the sample project used as the indexing target
SAMPLE_PROJECT = Path(__file__).resolve().parent.parent.parent / "sample_project"
CLI_MODULE = [sys.executable, "-m", "contextcore.cli.main"]


def _run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run CLI command in a subprocess and return the result."""
    return subprocess.run(
        CLI_MODULE + list(args),
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )


@pytest.fixture()
def indexed_tmpdir(tmp_path: Path):
    """Fixture: a temp dir with the graph already indexed from sample_project."""
    result = _run_cli("index", str(SAMPLE_PROJECT), cwd=tmp_path)
    assert result.returncode == 0, f"index failed: {result.stdout} {result.stderr}"
    return tmp_path


def test_index_command_runs(tmp_path: Path):
    """T-071: `contextcore index ./project` exits 0 and creates .contextcore/."""
    result = _run_cli("index", str(SAMPLE_PROJECT), cwd=tmp_path)
    assert result.returncode == 0, f"Exit code {result.returncode}: {result.stdout}"
    assert "[INFO]" in result.stdout
    assert "nodes" in result.stdout
    db_path = tmp_path / ".contextcore" / "contextcore.db"
    assert db_path.exists(), ".contextcore/contextcore.db not created"


def test_query_command_runs(indexed_tmpdir: Path):
    """T-072: `contextcore query "..."` exits 0 and prints output."""
    result = _run_cli("query", "User", cwd=indexed_tmpdir)
    assert result.returncode == 0, f"Exit code {result.returncode}: {result.stderr}"
    assert "User" in result.stdout


def test_status_command_runs(indexed_tmpdir: Path):
    """T-073: `contextcore status` exits 0 and prints graph summary."""
    result = _run_cli("status", cwd=indexed_tmpdir)
    assert result.returncode == 0, f"Exit code {result.returncode}: {result.stderr}"
    assert "[INFO] CONTEXTCORE STATUS" in result.stdout
    assert "Nodes:" in result.stdout
    assert "Edges:" in result.stdout


def test_diff_command_runs(indexed_tmpdir: Path):
    """T-074: `contextcore diff` exits 0 and reports changed nodes."""
    result = _run_cli("diff", cwd=indexed_tmpdir)
    assert result.returncode == 0, f"Exit code {result.returncode}: {result.stderr}"
    # Either "No changes" or STALE lines
    assert "[INFO]" in result.stdout or "[WARN]" in result.stdout


def test_query_output_is_markdown(indexed_tmpdir: Path):
    """T-075: Query output starts with a Markdown header."""
    result = _run_cli("query", "User", cwd=indexed_tmpdir)
    assert result.returncode == 0
    # First non-empty line should be a Markdown h2 header
    first_line = next(line for line in result.stdout.splitlines() if line.strip())
    assert first_line.startswith("## "), f"Expected Markdown header, got: {first_line!r}"


def test_json_flag_keeps_markdown_output(indexed_tmpdir: Path):
    """T-076: --json is compatibility-only and still returns Markdown."""
    result = _run_cli("query", "User", "--json", cwd=indexed_tmpdir)
    assert result.returncode == 0, f"Exit code {result.returncode}: {result.stderr}"
    assert "[WARN] --json is deprecated" in result.stdout
    assert "## User" in result.stdout
    assert "## Meta" in result.stdout


def test_query_role_outputs_v4_meta_block(indexed_tmpdir: Path):
    """v4 role mode includes role/staleness metadata in Markdown."""
    result = _run_cli(
        "query",
        "User",
        "--role",
        "maintainer",
        "--stale-after-days",
        "30",
        cwd=indexed_tmpdir,
    )
    assert result.returncode == 0, f"Exit code {result.returncode}: {result.stderr}"
    assert "## Meta" in result.stdout
    assert "- role: maintainer" in result.stdout
    assert "- stale_after_days: 30" in result.stdout
    assert "- elapsed_ms:" in result.stdout


def test_query_with_invalid_role_fails(indexed_tmpdir: Path):
    """Unsupported roles must fail fast with a clear message."""
    result = _run_cli("query", "User", "--role", "intern", cwd=indexed_tmpdir)
    assert result.returncode == 1
    assert "Invalid role" in result.stdout
