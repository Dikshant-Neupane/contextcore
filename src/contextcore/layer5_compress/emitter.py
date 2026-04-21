"""Layer 5 markdown emitter — emits compact structural Markdown from AST extraction."""

from pathlib import Path

from contextcore.layer1_ast.extractor import ClassStructure, FileStructure, FunctionSignature


def _compact_params(raw: str) -> str:
    """Strip spaces inside parameter lists and drop the bare 'self' argument."""

    inner = raw.strip("()")
    parts = [p.strip() for p in inner.split(",") if p.strip() not in ("", "self")]
    compacted = [
        p.replace(": ", ":").replace(" = ", "=").replace(" =", "=")
        for p in parts
    ]
    return "(" + ",".join(compacted) + ")"


def _format_sig(sig: FunctionSignature) -> str:
    """Render a function signature as a compact token-efficient string."""

    params = _compact_params(sig.params)
    arrow = f"->{sig.return_type.replace(' ', '')}" if sig.return_type else ""
    return f"{sig.name}{params}{arrow}"


def _format_class(cls: ClassStructure) -> str:
    """Render a class with all its methods on one pipe-separated line."""

    method_str = " | ".join(_format_sig(m) for m in cls.methods)
    if method_str:
        return f"+ {cls.name}: {method_str}"
    return f"+ {cls.name}"


def emit_markdown(structure: FileStructure) -> str:
    """Emit compressed structural Markdown from a Layer 1 FileStructure.

    Files with no extractable symbols are skipped (return empty string)
    to avoid emitting overhead tokens for structure-less files.
    """

    if not structure.ok:
        code = structure.error.code if structure.error else "UNKNOWN"
        return f"## {structure.source_path} [ERROR:{code}]"

    if not structure.classes and not structure.functions:
        return ""

    relative = Path(structure.source_path).name
    lines: list[str] = [f"## {relative}"]

    for cls in structure.classes:
        lines.append(_format_class(cls))

    if structure.functions:
        fn_str = " | ".join(_format_sig(f) for f in structure.functions)
        lines.append(f"fn: {fn_str}")

    return "\n".join(lines)
