"""
Layer 1 extractor unit tests — T-003 to T-007.
Phase: v1 ✅ ACTIVE
"""

from __future__ import annotations

from pathlib import Path

from contextcore.layer1_ast.extractor import extract_structure


def test_extract_function_names(simple_function_file: Path) -> None:
    """T-003: extract_structure returns the correct function names."""
    s = extract_structure(str(simple_function_file))
    assert s.ok, f"extract_structure failed: {s.error}"
    names = [f.name for f in s.functions]
    assert "greet" in names, f"Expected 'greet' in functions, got {names}"


def test_extract_class_names(class_with_methods_file: Path) -> None:
    """T-004: extract_structure returns the correct class names."""
    s = extract_structure(str(class_with_methods_file))
    assert s.ok, f"extract_structure failed: {s.error}"
    names = [c.name for c in s.classes]
    assert "Calculator" in names, f"Expected 'Calculator' in classes, got {names}"


def test_extract_imports(file_with_imports_file: Path) -> None:
    """T-005: Files with import statements parse cleanly; top-level functions are extracted."""
    s = extract_structure(str(file_with_imports_file))
    assert s.ok, f"extract_structure failed on file with imports: {s.error}"
    fn_names = [f.name for f in s.functions]
    assert "read_file" in fn_names, f"Expected 'read_file' in functions, got {fn_names}"
    assert "file_exists" in fn_names, f"Expected 'file_exists' in functions, got {fn_names}"


def test_extract_docstrings(simple_function_file: Path) -> None:
    """T-006: Functions with docstrings are extracted correctly — docstrings do not break extraction."""
    s = extract_structure(str(simple_function_file))
    assert s.ok, f"extract_structure failed: {s.error}"
    assert len(s.functions) == 1, f"Expected 1 function, got {len(s.functions)}"
    assert s.functions[0].name == "greet"


def test_extract_function_signatures(simple_function_file: Path) -> None:
    """T-007: Function signatures (params + return type) are extracted accurately."""
    s = extract_structure(str(simple_function_file))
    assert s.ok, f"extract_structure failed: {s.error}"
    fn = s.functions[0]
    assert fn.name == "greet"
    assert "name" in fn.params, f"Expected 'name' in params, got {fn.params!r}"
    assert fn.return_type == "str", f"Expected return type 'str', got {fn.return_type!r}"
