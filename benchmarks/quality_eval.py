"""Quality accuracy evaluator for v1 compression pipeline.

Defines 10 standard questions about the sample_project corpus.
For each question, checks whether the answer is derivable from:
  - RAW: the full source text (ground truth)
  - COMPRESSED: the structured Markdown output from L1+L5

A question PASSES if the compressed output contains sufficient signal
to reconstruct the correct answer. Score must reach >=80% (8/10).

Each question is represented as a QualityCheck with:
  - question: natural language description
  - expected_signals: list of substrings that must appear in the text
    for the answer to be considered derivable.
  - All signals must be present for a PASS.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from contextcore.layer1_ast.extractor import extract_structure
from contextcore.layer5_compress.emitter import emit_markdown


@dataclass(frozen=True)
class QualityCheck:
    """One evaluatable question with expected evidence signals.

    expected_signals: substrings required in COMPRESSED output.
    raw_signals: substrings required in RAW source (Python notation).
    If raw_signals is empty, expected_signals are used for both.
    """

    id: int
    question: str
    expected_signals: tuple[str, ...]  # compressed output form
    raw_signals: tuple[str, ...] = ()  # raw Python source form (optional override)


QUALITY_CHECKS: tuple[QualityCheck, ...] = (
    QualityCheck(
        id=1,
        question="What function creates a new User and what does it return?",
        expected_signals=("build_user", "->User"),
        raw_signals=("build_user", "-> User"),
    ),
    QualityCheck(
        id=2,
        question="What does the run() entry-point function return?",
        expected_signals=("run()", "->int"),
        raw_signals=("def run(", "-> int"),
    ),
    QualityCheck(
        id=3,
        question="How do you check whether the application is running in production?",
        expected_signals=("is_production", "->bool"),
        raw_signals=("def is_production", "-> bool"),
    ),
    QualityCheck(
        id=4,
        question="What class represents a tracked software project and what methods does it have?",
        expected_signals=("+ Project", "archive()", "set_owner(", "summary()"),
        raw_signals=("class Project", "def archive", "def set_owner", "def summary"),
    ),
    QualityCheck(
        id=5,
        question="What methods does the User class expose publicly?",
        expected_signals=("+ User", "display_name()", "deactivate()", "add_tag(", "to_dict()"),
        raw_signals=("class User", "def display_name", "def deactivate", "def add_tag", "def to_dict"),
    ),
    QualityCheck(
        id=6,
        question="What function paginates a list, and what parameters does it take?",
        expected_signals=("paginate(", "page:int", "page_size:int"),
        raw_signals=("def paginate(", "page: int", "page_size: int"),
    ),
    QualityCheck(
        id=7,
        question="How do you get the file size in kilobytes?",
        expected_signals=("file_size_kb(", "->float"),
        raw_signals=("def file_size_kb(", "-> float"),
    ),
    QualityCheck(
        id=8,
        question="What function builds a startup banner and what argument does it need?",
        expected_signals=("build_banner(", "env:str", "->str"),
        raw_signals=("def build_banner(", "env: str", "-> str"),
    ),
    QualityCheck(
        id=9,
        question="What does archive_project return, and what parameters does it accept?",
        expected_signals=("archive_project(", "project_id:str", "->bool"),
        raw_signals=("def archive_project(", "project_id: str", "-> bool"),
    ),
    QualityCheck(
        id=10,
        question="How do you parse an ID string into its component parts?",
        expected_signals=("parse_id(", "->tuple[str,int]"),
        raw_signals=("def parse_id(", "-> tuple[str, int]"),
    ),
)


def _build_compressed_corpus(project_root: Path) -> str:
    """Emit and concatenate compressed markdown for all project files."""

    parts: list[str] = []
    for source_file in sorted(project_root.rglob("*.py")):
        structure = extract_structure(str(source_file))
        md = emit_markdown(structure)
        if md:
            parts.append(md)
    return "\n".join(parts)


def _build_raw_corpus(project_root: Path) -> str:
    """Concatenate raw source text for all project files."""

    parts: list[str] = []
    for source_file in sorted(project_root.rglob("*.py")):
        parts.append(source_file.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


@dataclass(frozen=True)
class CheckResult:
    """Outcome of evaluating one QualityCheck against a corpus string."""

    check: QualityCheck
    passed: bool
    missing_signals: tuple[str, ...]


def evaluate(
    corpus: str,
    checks: tuple[QualityCheck, ...],
    use_raw_signals: bool = False,
) -> list[CheckResult]:
    """Run all checks against a corpus string and return results.

    When use_raw_signals=True, each check uses its raw_signals override
    (if present) instead of expected_signals.
    """

    results: list[CheckResult] = []
    for check in checks:
        signals = (
            check.raw_signals if use_raw_signals and check.raw_signals
            else check.expected_signals
        )
        missing = tuple(sig for sig in signals if sig not in corpus)
        results.append(CheckResult(check=check, passed=len(missing) == 0, missing_signals=missing))
    return results


def score(results: list[CheckResult]) -> float:
    """Return the fraction of checks that passed."""

    if not results:
        return 0.0
    return sum(1 for r in results if r.passed) / len(results)


def print_report(label: str, results: list[CheckResult]) -> None:
    """Print a human-readable evaluation report."""

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    pct = score(results) * 100
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  Score: {passed}/{total} ({pct:.0f}%)  {'PASS' if pct >= 80 else 'FAIL'}")
    print(f"{'='*60}")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] Q{r.check.id}: {r.check.question}")
        if r.missing_signals:
            print(f"         missing: {', '.join(r.missing_signals)}")


def main() -> None:
    """Run quality checks on raw and compressed corpus and compare."""

    project_root = REPO_ROOT / "sample_project"
    if not project_root.exists():
        print("sample_project/ not found.")
        return

    raw_corpus = _build_raw_corpus(project_root)
    compressed_corpus = _build_compressed_corpus(project_root)

    raw_results = evaluate(raw_corpus, QUALITY_CHECKS, use_raw_signals=True)
    compressed_results = evaluate(compressed_corpus, QUALITY_CHECKS, use_raw_signals=False)

    raw_tokens = len(raw_corpus.split())
    comp_tokens = len(compressed_corpus.split())

    print_report("RAW SOURCE", raw_results)
    print_report("COMPRESSED OUTPUT", compressed_results)

    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"  Raw tokens      : {raw_tokens}")
    print(f"  Compressed tokens: {comp_tokens}")
    print(f"  Compression ratio: {raw_tokens/comp_tokens:.2f}x")
    raw_score = score(raw_results) * 100
    comp_score = score(compressed_results) * 100
    print(f"  Raw accuracy    : {raw_score:.0f}%")
    print(f"  Compressed acc. : {comp_score:.0f}%")
    accuracy_retention = (comp_score / raw_score * 100) if raw_score else 0
    print(f"  Accuracy kept   : {accuracy_retention:.0f}% of raw baseline")
    kill_test = comp_score >= 80
    print(f"  Kill test (>=80%): {'PASSED' if kill_test else 'FAILED'}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
