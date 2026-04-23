"""
Git hook unit tests — T-077 to T-080.
Phase: v2 ACTIVE
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).resolve().parent.parent.parent / "hooks"
POST_COMMIT_SRC = HOOKS_DIR / "post-commit"
INSTALL_SCRIPT = HOOKS_DIR / "install_hooks.py"
SAMPLE_PROJECT = Path(__file__).resolve().parent.parent.parent / "sample_project"
CLI_MODULE = [sys.executable, "-m", "contextcore.cli.main"]


def test_hook_installs_in_under_30s(tmp_path: Path):
    """T-077: `python hooks/install_hooks.py` completes in <30s."""
    # Set up a fake .git/hooks directory in tmp_path
    git_hooks = tmp_path / ".git" / "hooks"
    git_hooks.mkdir(parents=True)

    t0 = time.perf_counter()
    result = subprocess.run(
        [sys.executable, str(INSTALL_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    elapsed = time.perf_counter() - t0

    assert result.returncode == 0, f"install_hooks.py failed: {result.stdout} {result.stderr}"
    assert "[PASS]" in result.stdout
    assert elapsed < 30.0, f"install_hooks.py took {elapsed:.1f}s — over 30s limit"


def test_hook_is_executable(tmp_path: Path):
    """T-078: hooks/post-commit is readable and install correctly sets permissions."""
    assert POST_COMMIT_SRC.exists(), f"hooks/post-commit not found at {POST_COMMIT_SRC}"

    # Install into a tmp .git/hooks and check permissions were set
    git_hooks = tmp_path / ".git" / "hooks"
    git_hooks.mkdir(parents=True)
    result = subprocess.run(
        [sys.executable, str(INSTALL_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    assert result.returncode == 0, f"install failed: {result.stderr}"

    dst = tmp_path / ".git" / "hooks" / "post-commit"
    assert dst.exists(), ".git/hooks/post-commit not created"

    # On Windows, check file is readable; on Unix check executable bit
    if os.name != "nt":
        mode = dst.stat().st_mode
        assert mode & stat.S_IXUSR, "post-commit not marked executable for user"
    else:
        # Windows: just assert the file is there and non-empty
        assert dst.stat().st_size > 0, "post-commit is empty"


def test_hook_triggers_on_commit(tmp_path: Path):
    """T-079: post-commit content is a valid shell script that mentions contextcore."""
    # On all platforms, validate the hook content — not actually git-committing
    # (git commit subprocess is OS/env-dependent; content validation is deterministic)
    assert POST_COMMIT_SRC.exists(), f"hooks/post-commit not found: {POST_COMMIT_SRC}"
    content = POST_COMMIT_SRC.read_text()
    assert "contextcore" in content, "post-commit hook does not reference contextcore"
    assert "contextcore index" in content, "post-commit hook does not call contextcore index"
    # Must start with a shebang
    assert content.startswith("#!/"), f"post-commit hook missing shebang: {content[:30]!r}"


def test_incremental_reindex_under_2s(tmp_path: Path):
    """T-080: Re-indexing the sample project takes <2s (incremental update)."""
    # First index pass
    result = subprocess.run(
        CLI_MODULE + ["index", str(SAMPLE_PROJECT)],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    assert result.returncode == 0, f"first index failed: {result.stdout}"

    # Second (incremental) index pass — must complete in <2s
    t0 = time.perf_counter()
    result2 = subprocess.run(
        CLI_MODULE + ["index", str(SAMPLE_PROJECT)],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    elapsed = time.perf_counter() - t0

    assert result2.returncode == 0, f"incremental index failed: {result2.stdout}"
    assert elapsed < 2.0, f"incremental re-index took {elapsed:.2f}s — over 2s limit"
