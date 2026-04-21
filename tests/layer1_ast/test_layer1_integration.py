"""
Layer 1 end-to-end integration test — T-008.
Phase: v1 ✅ ACTIVE
Tests the parse_file → extract_structure pipeline.
"""

from __future__ import annotations

from pathlib import Path


def test_parser_to_extractor_pipeline(
    parser, extractor, simple_function_file: Path
) -> None:
    """
    T-008: Full Layer 1 pipeline — parse_file → extract_structure.
    ParseResult flows into extractor to produce a valid FileStructure.
    """
    parse_result = parser.parse(simple_function_file)
    assert parse_result.ok, f"Parser failed: {parse_result.error}"
    assert parse_result.root_type == "module"

    file_structure = extractor.extract(parse_result)
    assert file_structure.ok, f"Extractor failed: {file_structure.error}"
    assert (
        len(file_structure.functions) > 0 or len(file_structure.classes) > 0
    ), "Layer 1 pipeline produced an empty structure for a non-empty file"


def test_parser_to_extractor_class_file(
    parser, extractor, class_with_methods_file: Path
) -> None:
    """Layer 1 pipeline correctly extracts a class from a file."""
    parse_result = parser.parse(class_with_methods_file)
    assert parse_result.ok

    file_structure = extractor.extract(parse_result)
    assert file_structure.ok
    class_names = [c.name for c in file_structure.classes]
    assert "Calculator" in class_names


def test_parser_to_extractor_preserves_source_path(
    parser, extractor, simple_function_file: Path
) -> None:
    """Source path is preserved end-to-end through the Layer 1 pipeline."""
    parse_result = parser.parse(simple_function_file)
    file_structure = extractor.extract(parse_result)
    assert str(simple_function_file) in str(file_structure.source_path)
