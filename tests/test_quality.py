"""pytest suite: quality accuracy checks for v1 compression pipeline.

Validates that compressed output passes >=80% of the standard quality
questions and that raw source passes 100% (ground truth sanity check).
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Ensure src/ and benchmarks/ are importable
import sys
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from benchmarks.quality_eval import (
    QUALITY_CHECKS,
    CheckResult,
    _build_compressed_corpus,
    _build_raw_corpus,
    evaluate,
    score,
)

PROJECT_ROOT = REPO_ROOT / "sample_project"


@pytest.fixture(scope="module")
def raw_corpus() -> str:
    """Full raw source text for the sample project."""
    return _build_raw_corpus(PROJECT_ROOT)


@pytest.fixture(scope="module")
def compressed_corpus() -> str:
    """Compressed markdown output for the sample project."""
    return _build_compressed_corpus(PROJECT_ROOT)


@pytest.fixture(scope="module")
def raw_results(raw_corpus: str) -> list[CheckResult]:
    """Evaluated quality checks against raw source."""
    return evaluate(raw_corpus, QUALITY_CHECKS, use_raw_signals=True)


@pytest.fixture(scope="module")
def compressed_results(compressed_corpus: str) -> list[CheckResult]:
    """Evaluated quality checks against compressed output."""
    return evaluate(compressed_corpus, QUALITY_CHECKS, use_raw_signals=False)


def test_raw_corpus_passes_all_checks(raw_results: list[CheckResult]) -> None:
    """Raw source must answer every question (ground truth sanity check)."""
    failures = [r for r in raw_results if not r.passed]
    assert failures == [], (
        f"Raw source failed {len(failures)} checks: "
        + ", ".join(f"Q{r.check.id}" for r in failures)
    )


def test_compressed_output_passes_quality_threshold(
    compressed_results: list[CheckResult],
) -> None:
    """Compressed output must answer >=80% of quality questions (kill test)."""
    accuracy = score(compressed_results)
    failures = [r for r in compressed_results if not r.passed]
    assert accuracy >= 0.80, (
        f"Compressed accuracy {accuracy*100:.0f}% < 80% threshold. "
        f"Failed: {', '.join(f'Q{r.check.id}' for r in failures)}"
    )


@pytest.mark.parametrize("check", QUALITY_CHECKS, ids=lambda c: f"Q{c.id}")
def test_compressed_answers_question(
    check: object, compressed_corpus: str
) -> None:
    """Each individual question is checked so failures are reported per-question."""
    from benchmarks.quality_eval import QualityCheck
    assert isinstance(check, QualityCheck)
    missing = [sig for sig in check.expected_signals if sig not in compressed_corpus]
    assert not missing, (
        f"Q{check.id} missing signals in compressed output: {missing}\n"
        f"Question: {check.question}"
    )
