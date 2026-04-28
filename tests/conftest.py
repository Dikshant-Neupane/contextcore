"""
CONTEXTCORE — Root conftest.py
Shared fixtures available to all test files across all phases.
Phase-locked fixtures raise pytest.skip() if their phase is not active.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# ─── Project roots ─────────────────────────────────────────────────────────
REPO_ROOT    = Path(__file__).resolve().parent.parent
SRC_ROOT     = REPO_ROOT / "src" / "contextcore"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
SAMPLE_DIR   = REPO_ROOT / "sample_project"
RESULTS_DIR  = REPO_ROOT / "tests" / "results"
DB_PATH      = REPO_ROOT / ".contextcore" / "contextcore.db"

# ─── Phase lock ────────────────────────────────────────────────────────────
CURRENT_VERSION = "v4"      # ← AI: update this when a gate passes

VERSION_ORDER = ["v1", "v2", "v3", "v4"]


def phase_is_active(phase: str) -> bool:
    """Return True if the given phase is unlocked in the current version."""
    try:
        return VERSION_ORDER.index(phase) <= VERSION_ORDER.index(CURRENT_VERSION)
    except ValueError:
        return False


def require_phase(phase: str) -> None:
    """Call inside a fixture or test to skip if the phase is not yet active."""
    if not phase_is_active(phase):
        pytest.skip(
            f"Phase {phase} is locked. "
            f"Current active version: {CURRENT_VERSION}. "
            f"Complete gate checks to unlock."
        )


# ─── Thin API adapters ──────────────────────────────────────────────────────
# The underlying code uses functions (parse_file, extract_structure,
# emit_markdown). These wrappers expose a consistent object interface so
# tests can call parser.parse(), extractor.extract(), emitter.emit().


class _ParseAdapter:
    """Wraps parse_file() as a parser.parse(filepath) → ParseResult object."""

    def parse(self, filepath: Path | str):
        from contextcore.layer1_ast.parser import parse_file

        return parse_file(str(filepath))


class _ExtractAdapter:
    """Wraps extract_structure() — accepts filepath OR ParseResult."""

    def extract(self, filepath_or_result):
        from contextcore.layer1_ast.extractor import extract_structure

        # Accept a ParseResult (from _ParseAdapter.parse) or a plain path
        if hasattr(filepath_or_result, "source_path"):
            return extract_structure(str(filepath_or_result.source_path))
        return extract_structure(str(filepath_or_result))


class _EmitAdapter:
    """Wraps emit_markdown() as an emitter.emit(file_structure) → str object."""

    def emit(self, file_structure) -> str:
        from contextcore.layer5_compress.emitter import emit_markdown

        return emit_markdown(file_structure)


# ─── Fixtures: API adapters ─────────────────────────────────────────────────


@pytest.fixture
def parser() -> _ParseAdapter:
    """Layer 1 parser adapter — call parser.parse(filepath) → ParseResult."""
    return _ParseAdapter()


@pytest.fixture
def extractor() -> _ExtractAdapter:
    """Layer 1 extractor adapter — call extractor.extract(parse_result) → FileStructure."""
    return _ExtractAdapter()


@pytest.fixture
def emitter() -> _EmitAdapter:
    """Layer 5 emitter adapter — call emitter.emit(file_structure) → str."""
    return _EmitAdapter()


# ─── Fixtures: Sample fixture files ────────────────────────────────────────


@pytest.fixture(scope="session")
def simple_function_file() -> Path:
    """A minimal Python file with one typed function."""
    p = FIXTURES_DIR / "sample_files" / "simple_function.py"
    assert p.exists(), f"Fixture missing: {p}"
    return p


@pytest.fixture(scope="session")
def class_with_methods_file() -> Path:
    """A Python file with a class and multiple methods."""
    p = FIXTURES_DIR / "sample_files" / "class_with_methods.py"
    assert p.exists(), f"Fixture missing: {p}"
    return p


@pytest.fixture(scope="session")
def file_with_imports_file() -> Path:
    """A Python file with multiple import styles and top-level functions."""
    p = FIXTURES_DIR / "sample_files" / "file_with_imports.py"
    assert p.exists(), f"Fixture missing: {p}"
    return p


@pytest.fixture(scope="session")
def deeply_nested_file() -> Path:
    """A Python file with nested class and function definitions."""
    p = FIXTURES_DIR / "sample_files" / "deeply_nested.py"
    assert p.exists(), f"Fixture missing: {p}"
    return p


@pytest.fixture(scope="session")
def empty_file_fixture() -> Path:
    """An empty Python file."""
    p = FIXTURES_DIR / "sample_files" / "empty_file.py"
    assert p.exists(), f"Fixture missing: {p}"
    return p


@pytest.fixture(scope="session")
def syntax_error_file(tmp_path_factory) -> Path:
    """A Python file with a deliberate syntax error."""
    f = tmp_path_factory.mktemp("edge") / "broken.py"
    f.write_text("def broken(\n    # missing closing paren\n", encoding="utf-8")
    return f


@pytest.fixture(scope="session")
def sample_project_dir() -> Path:
    """The 20-file sample project used for v1 benchmarks."""
    assert SAMPLE_DIR.exists(), f"sample_project/ not found at {SAMPLE_DIR}"
    return SAMPLE_DIR


# ─── Fixtures: Layer 4 (v2 — phase-locked) ─────────────────────────────────


@pytest.fixture
def graph_builder(tmp_path):
    """Layer 4 graph builder with a fresh in-memory SQLite DB."""
    require_phase("v2")
    from contextcore.layer4_graph.builder import GraphBuilder  # noqa: PLC0415

    return GraphBuilder(db_path=tmp_path / "test.db")


@pytest.fixture
def graph_querier(tmp_path):
    """Layer 4 graph querier connected to a fresh test DB."""
    require_phase("v2")
    from contextcore.layer4_graph.querier import GraphQuerier  # noqa: PLC0415

    return GraphQuerier(db_path=tmp_path / "test.db")


@pytest.fixture
def populated_graph(graph_builder, sample_project_dir):
    """
    A graph builder with the full sample_project already indexed.
    Use this when you need a real graph to query against.
    """
    require_phase("v2")
    graph_builder.index_directory(sample_project_dir)
    return graph_builder


# ─── Fixtures: Results dir ─────────────────────────────────────────────────


@pytest.fixture(scope="session", autouse=True)
def ensure_results_dir() -> None:
    """Ensure tests/results/archive/ exists before any test runs."""
    (RESULTS_DIR / "archive").mkdir(parents=True, exist_ok=True)
