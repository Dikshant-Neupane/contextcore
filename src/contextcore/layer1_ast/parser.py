"""Layer 1 parser skeleton for Python source files."""

from dataclasses import dataclass
from pathlib import Path

from tree_sitter import Language, Parser
import tree_sitter_python


@dataclass(frozen=True)
class ParseError:
    """Describes a parsing failure in a structured form."""

    code: str
    message: str


@dataclass(frozen=True)
class ParseResult:
    """Structured result returned by the parser."""

    ok: bool
    language: str
    source_path: str
    byte_length: int
    line_count: int
    root_type: str | None = None
    node_count: int = 0
    has_syntax_error: bool = False
    error: ParseError | None = None


def _error_result(source_path: Path, code: str, message: str) -> ParseResult:
    """Create a standardized parser error result."""

    return ParseResult(
        ok=False,
        language="python",
        source_path=str(source_path),
        byte_length=0,
        line_count=0,
        error=ParseError(code=code, message=message),
    )


def _count_nodes(root_node: object) -> int:
    """Count nodes in the syntax tree without recursion depth issues."""

    count = 0
    stack = [root_node]
    while stack:
        node = stack.pop()
        count += 1
        stack.extend(node.children)
    return count


def parse_file(filepath: str) -> ParseResult:
    """Parse a Python file into a lightweight, benchmark-ready result."""

    source_path = Path(filepath)
    if not source_path.exists() or not source_path.is_file():
        return _error_result(source_path, "FILE_NOT_FOUND", "Input file does not exist.")

    if source_path.suffix != ".py":
        return _error_result(source_path, "UNSUPPORTED_EXTENSION", "Only .py files are supported in v1.")

    try:
        content = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return _error_result(source_path, "READ_FAILED", str(exc))

    language = Language(tree_sitter_python.language())
    parser = Parser(language)
    tree = parser.parse(content.encode("utf-8"))
    root_node = tree.root_node

    return ParseResult(
        ok=True,
        language="python",
        source_path=str(source_path),
        byte_length=len(content.encode("utf-8")),
        line_count=len(content.splitlines()),
        root_type=root_node.type,
        node_count=_count_nodes(root_node),
        has_syntax_error=root_node.has_error,
        error=None,
    )
