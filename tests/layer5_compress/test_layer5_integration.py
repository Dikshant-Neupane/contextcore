"""
Layer 5 end-to-end integration tests — T-013, T-014.
Phase: v1 ✅ ACTIVE
Tests compression ratio on the full sample_project corpus.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from contextcore.layer1_ast.extractor import extract_structure
from contextcore.layer5_compress.emitter import emit_markdown


def _whitespace_tokens(text: str) -> int:
    return len(text.split())


def _compression_ratio(project_root: Path) -> tuple[int, int, float]:
    """Return (raw_tokens, compressed_tokens, ratio) for all .py files under root."""
    raw_total        = 0
    compressed_total = 0
    for py_file in sorted(project_root.rglob("*.py")):
        raw = _whitespace_tokens(py_file.read_text(encoding="utf-8", errors="ignore"))
        if raw == 0:
            continue
        s  = extract_structure(str(py_file))
        md = emit_markdown(s)
        compressed_total += _whitespace_tokens(md) if md else 0
        raw_total        += raw
    ratio = raw_total / compressed_total if compressed_total > 0 else 0
    return raw_total, compressed_total, ratio


def test_compression_ratio_gt_5x(sample_project_dir: Path) -> None:
    """T-013: Full pipeline on sample_project delivers >5x compression (v1 kill test)."""
    _, _, ratio = _compression_ratio(sample_project_dir)
    assert ratio > 5.0, (
        f"Compression ratio {ratio:.2f}x did not beat the v1 kill test threshold of 5x"
    )


def test_compression_ratio_result(sample_project_dir: Path) -> None:
    """T-014: Compression ratio must not regress below 10x from the v1 gate result of 11.38x."""
    raw, compressed, ratio = _compression_ratio(sample_project_dir)
    assert ratio >= 10.0, (
        f"REGRESSION: Compression ratio {ratio:.2f}x dropped below 10x regression floor.\n"
        f"Raw tokens: {raw} | Compressed: {compressed}\n"
        f"v1 gate result was 11.38x — investigate emitter changes."
    )


def test_compression_zero_parse_failures(sample_project_dir: Path) -> None:
    """Every file in sample_project must extract without a parse failure."""
    failures = []
    for py_file in sorted(sample_project_dir.rglob("*.py")):
        s = extract_structure(str(py_file))
        if not s.ok:
            failures.append(f"{py_file.name}: {s.error}")
    assert failures == [], (
        f"Parse failures on {len(failures)} file(s):\n" + "\n".join(failures)
    )


def test_emitter_pipeline_emitter_adapter(
    parser, extractor, emitter, sample_project_dir: Path
) -> None:
    """Full L1→L5 pipeline using the object-adapter API (parser/extractor/emitter fixtures)."""
    py_files = list(sample_project_dir.rglob("*.py"))
    assert len(py_files) >= 10

    failures = []
    for py_file in py_files:
        try:
            pr = parser.parse(py_file)
            fs = extractor.extract(pr)
            md = emitter.emit(fs)
            assert isinstance(md, str)
        except Exception as exc:
            failures.append(f"{py_file.name}: {exc}")

    assert failures == [], "Pipeline adapter failures:\n" + "\n".join(failures)
