"""
CONTEXTCORE — v1 Integration Pipeline Tests — T-046, T-047.
Phase: v1 ✅ ACTIVE
Tests the full Layer 1 → Layer 5 pipeline end-to-end using the adapter fixtures.
"""

from __future__ import annotations

from pathlib import Path

import pytest


class TestFullV1Pipeline:
    """End-to-end tests for the L1 → L5 pipeline via object adapters."""

    def test_full_l1_l5_pipeline_simple_file(
        self, parser, extractor, emitter, simple_function_file: Path
    ) -> None:
        """T-046: Full pipeline: parse → extract → emit produces valid Markdown."""
        pr = parser.parse(simple_function_file)
        assert pr.ok, f"Parser failed: {pr.error}"

        fs = extractor.extract(pr)
        assert fs.ok, f"Extractor failed: {fs.error}"

        md = emitter.emit(fs)
        assert isinstance(md, str)
        assert len(md) > 0
        assert "## " in md, "Output must contain a Markdown header"

    def test_full_pipeline_on_sample_project(
        self, parser, extractor, emitter, sample_project_dir: Path
    ) -> None:
        """T-047: Pipeline runs cleanly on all 20 files in sample_project."""
        py_files = list(sample_project_dir.rglob("*.py"))
        assert len(py_files) >= 10, f"Expected ≥10 Python files, found {len(py_files)}"

        failures = []
        for py_file in py_files:
            try:
                pr = parser.parse(py_file)
                fs = extractor.extract(pr)
                md = emitter.emit(fs)
                assert isinstance(md, str)
            except Exception as exc:
                failures.append(f"{py_file.name}: {exc}")

        assert not failures, (
            f"Pipeline failed on {len(failures)} file(s):\n"
            + "\n".join(f"  {n}" for n in failures)
        )

    def test_pipeline_compression_ratio_beats_v1_gate(
        self, parser, extractor, emitter, sample_project_dir: Path
    ) -> None:
        """Regression guard — pipeline must not drop below 10x compression (v1 gate: 11.38x)."""
        tiktoken = pytest.importorskip(
            "tiktoken", reason="tiktoken not installed — skipping tiktoken-based ratio test"
        )
        enc = tiktoken.get_encoding("cl100k_base")

        raw_total        = 0
        compressed_total = 0

        for py_file in sample_project_dir.rglob("*.py"):
            raw_tokens = len(enc.encode(py_file.read_text(errors="ignore")))
            if raw_tokens == 0:
                continue
            pr  = parser.parse(py_file)
            fs  = extractor.extract(pr)
            md  = emitter.emit(fs)
            raw_total        += raw_tokens
            compressed_total += len(enc.encode(md)) if md else 0

        ratio = raw_total / compressed_total if compressed_total > 0 else 0
        assert ratio >= 10.0, (
            f"REGRESSION: tiktoken compression ratio {ratio:.2f}x dropped below 10x.\n"
            f"Raw: {raw_total} | Compressed: {compressed_total}"
        )

    def test_pipeline_markdown_structure_preserved(
        self, parser, extractor, emitter, class_with_methods_file: Path
    ) -> None:
        """Structural identifiers from the source must appear in the emitted Markdown."""
        pr = parser.parse(class_with_methods_file)
        fs = extractor.extract(pr)
        md = emitter.emit(fs)

        assert "## " in md
        assert "Calculator" in md

        source = class_with_methods_file.read_text(encoding="utf-8")
        identifiers = [
            w for w in source.split()
            if len(w) > 4 and w.isidentifier()
        ]
        assert any(ident in md for ident in identifiers), (
            "No source identifiers found in Markdown output"
        )
