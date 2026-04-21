"""
Edge case tests for v1 – run with pytest or directly with python.
"""
import os
import tempfile
import textwrap

import pytest

from contextcore.layer1_ast.parser import parse_file
from contextcore.layer1_ast.extractor import extract_structure
from contextcore.layer5_compress.emitter import emit_markdown


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tmp(content: str) -> str:
    """Write content to a temp .py file and return its path."""
    f = tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8")
    f.write(content)
    f.flush()
    f.close()
    return f.name


# ---------------------------------------------------------------------------
# parse_file edge cases
# ---------------------------------------------------------------------------

def test_parse_file_missing_file():
    r = parse_file("no_such_file_xyz.py")
    assert not r.ok
    assert r.error is not None
    assert r.error.code == "FILE_NOT_FOUND"


def test_parse_file_empty_file():
    p = _tmp("")
    try:
        r = parse_file(p)
        assert r.ok
        assert r.line_count == 0
        assert not r.has_syntax_error
    finally:
        os.unlink(p)


def test_parse_file_syntax_error_does_not_crash():
    p = _tmp("def broken(\n    x = \n")
    try:
        r = parse_file(p)
        assert r.ok          # parse_file succeeds — Tree-sitter is error-tolerant
        assert r.has_syntax_error
    finally:
        os.unlink(p)


def test_parse_file_metadata_fields():
    p = _tmp("x = 1\ny = 2\n")
    try:
        r = parse_file(p)
        assert r.ok
        assert r.line_count == 2
        assert r.byte_length > 0
        assert r.root_type == "module"
        assert r.node_count > 0
        assert r.error is None
    finally:
        os.unlink(p)


# ---------------------------------------------------------------------------
# extract_structure edge cases
# ---------------------------------------------------------------------------

def test_extract_missing_file():
    s = extract_structure("no_such_file_xyz.py")
    assert not s.ok
    assert s.error is not None


def test_extract_empty_file():
    p = _tmp("")
    try:
        s = extract_structure(p)
        assert s.ok
        assert len(s.functions) == 0
        assert len(s.classes) == 0
    finally:
        os.unlink(p)


def test_extract_constants_only():
    p = _tmp("import os\nX = 42\nY: str = 'hello'\n")
    try:
        s = extract_structure(p)
        assert s.ok
        assert len(s.functions) == 0
        assert len(s.classes) == 0
    finally:
        os.unlink(p)


def test_extract_only_top_level_classes():
    """Nested class definitions should NOT appear as top-level classes."""
    p = _tmp(textwrap.dedent("""\
        class Outer:
            class Inner:
                def inner_method(self) -> str: ...
            def outer_method(self) -> int: ...
    """))
    try:
        s = extract_structure(p)
        assert s.ok
        names = [c.name for c in s.classes]
        assert "Outer" in names, "Outer should be a top-level class"
        assert "Inner" not in names, "Inner should NOT be a top-level class"
    finally:
        os.unlink(p)


def test_extract_top_level_function():
    p = _tmp("def greet(name: str) -> str:\n    return f'hi {name}'\n")
    try:
        s = extract_structure(p)
        assert s.ok
        assert len(s.functions) == 1
        assert s.functions[0].name == "greet"
        assert s.functions[0].return_type == "str"
        assert "name:str" in s.functions[0].params.replace(" ", "")
    finally:
        os.unlink(p)


def test_extract_function_no_return_annotation():
    p = _tmp("def legacy(x, y):\n    pass\n")
    try:
        s = extract_structure(p)
        assert s.ok
        assert len(s.functions) == 1
        fn = s.functions[0]
        assert fn.name == "legacy"
        # return_type should be empty string or None — not crash
        assert fn.return_type == "" or fn.return_type is None
    finally:
        os.unlink(p)


def test_extract_decorated_class():
    """@dataclass-decorated classes must be extracted correctly."""
    p = _tmp(textwrap.dedent("""\
        from dataclasses import dataclass

        @dataclass
        class Config:
            def validate(self) -> bool: ...
            def to_dict(self) -> dict: ...
    """))
    try:
        s = extract_structure(p)
        assert s.ok
        names = [c.name for c in s.classes]
        assert "Config" in names, f"Expected Config in {names}"
        config = next(c for c in s.classes if c.name == "Config")
        method_names = [m.name for m in config.methods]
        assert "validate" in method_names
        assert "to_dict" in method_names
    finally:
        os.unlink(p)


def test_extract_multiple_classes_and_functions():
    p = _tmp(textwrap.dedent("""\
        def helper() -> None: ...

        class A:
            def method_a(self) -> int: ...

        class B:
            def method_b(self) -> str: ...

        def util(x: int) -> bool: ...
    """))
    try:
        s = extract_structure(p)
        assert s.ok
        assert len(s.functions) == 2
        assert len(s.classes) == 2
        fn_names = [f.name for f in s.functions]
        assert "helper" in fn_names
        assert "util" in fn_names
        cls_names = [c.name for c in s.classes]
        assert "A" in cls_names
        assert "B" in cls_names
    finally:
        os.unlink(p)


# ---------------------------------------------------------------------------
# emit_markdown edge cases
# ---------------------------------------------------------------------------

def test_emit_empty_structure_returns_empty_string():
    p = _tmp("X = 1\n")
    try:
        s = extract_structure(p)
        md = emit_markdown(s)
        assert md == ""
    finally:
        os.unlink(p)


def test_emit_contains_filename_header():
    p = _tmp("def foo() -> int: ...\n")
    try:
        s = extract_structure(p)
        md = emit_markdown(s)
        # Header should be ## <filename>
        first_line = md.strip().splitlines()[0]
        assert first_line.startswith("## ")
    finally:
        os.unlink(p)


def test_emit_class_prefixed_with_plus():
    p = _tmp(textwrap.dedent("""\
        class MyModel:
            def save(self) -> None: ...
    """))
    try:
        s = extract_structure(p)
        md = emit_markdown(s)
        assert "+ MyModel:" in md
    finally:
        os.unlink(p)


def test_emit_function_prefixed_with_fn():
    p = _tmp("def compute(x: int) -> float: ...\n")
    try:
        s = extract_structure(p)
        md = emit_markdown(s)
        assert "fn:" in md
        assert "compute" in md
    finally:
        os.unlink(p)


def test_emit_self_stripped_from_method_params():
    p = _tmp(textwrap.dedent("""\
        class Svc:
            def act(self, name: str) -> bool: ...
    """))
    try:
        s = extract_structure(p)
        md = emit_markdown(s)
        assert "self" not in md, f"'self' should be stripped from output, got:\n{md}"
    finally:
        os.unlink(p)


def test_emit_failed_structure_returns_empty_string():
    s = extract_structure("nonexistent_file.py")
    assert not s.ok
    md = emit_markdown(s)
    assert md == ""


# ---------------------------------------------------------------------------
# Round-trip: parse → extract → emit
# ---------------------------------------------------------------------------

def test_roundtrip_on_all_sample_files():
    """Every file in sample_project must round-trip without crashing."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parent.parent / "sample_project"
    failures = []
    for py_file in sorted(root.rglob("*.py")):
        try:
            s = extract_structure(str(py_file))
            _ = emit_markdown(s)
        except Exception as e:
            failures.append(f"{py_file.name}: {e}")
    assert failures == [], "Round-trip failures:\n" + "\n".join(failures)
