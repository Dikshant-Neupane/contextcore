"""
Layer 5 emitter unit tests — T-009 to T-012.
Phase: v1 ✅ ACTIVE
"""

from __future__ import annotations

from pathlib import Path

from contextcore.layer1_ast.extractor import extract_structure
from contextcore.layer5_compress.emitter import emit_markdown

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def test_emitter_outputs_markdown(simple_function_file: Path) -> None:
    """T-009: emit_markdown produces a non-empty Markdown string with a ## header."""
    s = extract_structure(str(simple_function_file))
    md = emit_markdown(s)
    assert isinstance(md, str), "emit_markdown must return a str"
    assert len(md) > 0, "emit_markdown returned empty string for a structured file"
    assert md.startswith("## "), f"Expected Markdown header, got: {md[:40]!r}"


def test_emitter_no_raw_source(class_with_methods_file: Path) -> None:
    """T-010: emit_markdown output contains no raw function body text."""
    source = class_with_methods_file.read_text(encoding="utf-8")
    s = extract_structure(str(class_with_methods_file))
    md = emit_markdown(s)

    # Body tokens that should NOT appear in compressed output
    for body_token in ("return x + y", "return x - y", 'f"Hello', "pass"):
        assert body_token not in md, (
            f"Function body token {body_token!r} leaked into compressed output"
        )

    # But structural names MUST appear
    assert "Calculator" in md
    assert "add" in md


def test_token_count_compressed_lt_raw(class_with_methods_file: Path) -> None:
    """T-011: Compressed token count is strictly less than raw token count."""
    raw_tokens = len(class_with_methods_file.read_text(encoding="utf-8").split())
    s = extract_structure(str(class_with_methods_file))
    md = emit_markdown(s)
    compressed_tokens = len(md.split())
    assert compressed_tokens < raw_tokens, (
        f"Compressed ({compressed_tokens}) >= raw ({raw_tokens}) — "
        "emitter is not reducing token count"
    )


def test_structure_preserved_in_output(class_with_methods_file: Path) -> None:
    """T-012: All class names and method names appear in the emitted Markdown."""
    s = extract_structure(str(class_with_methods_file))
    md = emit_markdown(s)

    assert "Calculator" in md, "Class name 'Calculator' missing from output"
    for method in ("add", "subtract", "multiply", "divide"):
        assert method in md, f"Method '{method}' missing from output"


def test_emitter_golden_output_simple_function(simple_function_file: Path) -> None:
    """Emitted output matches the golden expected_outputs/simple_function.md file."""
    golden_path = FIXTURES_DIR / "expected_outputs" / "simple_function.md"
    expected = golden_path.read_text(encoding="utf-8").strip()

    s = extract_structure(str(simple_function_file))
    actual = emit_markdown(s).strip()

    assert actual == expected, (
        f"Golden output mismatch.\nExpected:\n{expected}\nActual:\n{actual}"
    )


def test_emitter_golden_output_class_with_methods(class_with_methods_file: Path) -> None:
    """Emitted output matches the golden expected_outputs/class_with_methods.md file."""
    golden_path = FIXTURES_DIR / "expected_outputs" / "class_with_methods.md"
    expected = golden_path.read_text(encoding="utf-8").strip()

    s = extract_structure(str(class_with_methods_file))
    actual = emit_markdown(s).strip()

    assert actual == expected, (
        f"Golden output mismatch.\nExpected:\n{expected}\nActual:\n{actual}"
    )


def test_emitter_golden_output_file_with_imports(file_with_imports_file: Path) -> None:
    """Emitted output matches the golden expected_outputs/file_with_imports.md file."""
    golden_path = FIXTURES_DIR / "expected_outputs" / "file_with_imports.md"
    expected = golden_path.read_text(encoding="utf-8").strip()

    s = extract_structure(str(file_with_imports_file))
    actual = emit_markdown(s).strip()

    assert actual == expected, (
        f"Golden output mismatch.\nExpected:\n{expected}\nActual:\n{actual}"
    )
