"""Tests for Layer 1 parser skeleton."""

from pathlib import Path

from contextcore.layer1_ast.parser import parse_file


def test_parse_file_returns_file_not_found_for_missing_path() -> None:
    """Parser should return a structured error for missing files."""

    result = parse_file("does_not_exist.py")
    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "FILE_NOT_FOUND"


def test_parse_file_returns_metadata_for_valid_python_file(tmp_path: Path) -> None:
    """Parser should return basic metadata for valid Python input."""

    source_file = tmp_path / "example.py"
    source_file.write_text("def demo() -> str:\n    return 'ok'\n", encoding="utf-8")

    result = parse_file(str(source_file))
    assert result.ok is True
    assert result.error is None
    assert result.language == "python"
    assert result.line_count == 2
    assert result.byte_length > 0
