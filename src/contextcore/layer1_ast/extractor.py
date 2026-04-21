"""Layer 1 AST structure extractor for Python source files.

Extracts function and class signatures from a parsed syntax tree,
discarding implementation details to produce the compressed input
that Layer 5 will emit as structured Markdown.
"""

from dataclasses import dataclass
from pathlib import Path

from tree_sitter import Language, Parser
import tree_sitter_python

from contextcore.layer1_ast.parser import ParseError


@dataclass(frozen=True)
class FunctionSignature:
    """Signature of a single function or method."""

    name: str
    params: str
    return_type: str | None


@dataclass(frozen=True)
class ClassStructure:
    """Extracted structure of a class definition."""

    name: str
    methods: tuple[FunctionSignature, ...]


@dataclass(frozen=True)
class FileStructure:
    """Full structural extraction result for one source file."""

    ok: bool
    source_path: str
    line_count: int
    byte_length: int
    functions: tuple[FunctionSignature, ...]
    classes: tuple[ClassStructure, ...]
    error: ParseError | None = None


def _node_text(node: object, source_bytes: bytes) -> str:
    """Decode a syntax node's byte span to a string."""

    return source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def _extract_function_sig(node: object, source_bytes: bytes) -> FunctionSignature:
    """Pull name, params, and optional return type from a function_definition node."""

    name = ""
    params = "()"
    return_type: str | None = None
    for child in node.children:
        if child.type == "identifier" and not name:
            name = _node_text(child, source_bytes)
        elif child.type == "parameters":
            params = _node_text(child, source_bytes)
        elif child.type == "type":
            return_type = _node_text(child, source_bytes)
    return FunctionSignature(name=name, params=params, return_type=return_type)


def _extract_class(node: object, source_bytes: bytes) -> ClassStructure:
    """Pull class name and method signatures from a class_definition node."""

    name = ""
    methods: list[FunctionSignature] = []
    for child in node.children:
        if child.type == "identifier" and not name:
            name = _node_text(child, source_bytes)
        elif child.type == "block":
            for block_child in child.children:
                if block_child.type == "function_definition":
                    methods.append(_extract_function_sig(block_child, source_bytes))
                elif block_child.type == "decorated_definition":
                    for inner in block_child.children:
                        if inner.type == "function_definition":
                            methods.append(_extract_function_sig(inner, source_bytes))
    return ClassStructure(name=name, methods=tuple(methods))


def _error_structure(source_path: Path, code: str, message: str) -> FileStructure:
    """Return a standardized failure result."""

    return FileStructure(
        ok=False,
        source_path=str(source_path),
        line_count=0,
        byte_length=0,
        functions=(),
        classes=(),
        error=ParseError(code=code, message=message),
    )


def extract_structure(filepath: str) -> FileStructure:
    """Extract function and class signatures from a Python source file."""

    source_path = Path(filepath)
    if not source_path.exists() or not source_path.is_file():
        return _error_structure(source_path, "FILE_NOT_FOUND", "Input file does not exist.")

    if source_path.suffix != ".py":
        return _error_structure(source_path, "UNSUPPORTED_EXTENSION", "Only .py files are supported in v1.")

    try:
        content = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return _error_structure(source_path, "READ_FAILED", str(exc))

    source_bytes = content.encode("utf-8")
    language = Language(tree_sitter_python.language())
    parser = Parser(language)
    root = parser.parse(source_bytes).root_node

    functions: list[FunctionSignature] = []
    classes: list[ClassStructure] = []

    for child in root.children:
        if child.type == "function_definition":
            functions.append(_extract_function_sig(child, source_bytes))
        elif child.type == "class_definition":
            classes.append(_extract_class(child, source_bytes))
        elif child.type == "decorated_definition":
            # Unwrap decorated classes and functions (e.g. @dataclass, @staticmethod)
            for inner in child.children:
                if inner.type == "function_definition":
                    functions.append(_extract_function_sig(inner, source_bytes))
                elif inner.type == "class_definition":
                    classes.append(_extract_class(inner, source_bytes))

    return FileStructure(
        ok=True,
        source_path=str(source_path),
        line_count=len(content.splitlines()),
        byte_length=len(source_bytes),
        functions=tuple(functions),
        classes=tuple(classes),
        error=None,
    )
