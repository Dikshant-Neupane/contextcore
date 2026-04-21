"""Baseline token counting for v1 benchmark comparisons."""

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from contextcore.layer1_ast.extractor import extract_structure
from contextcore.layer5_compress.emitter import emit_markdown


def count_tokens(text: str) -> int:
    """Count tokens using a deterministic whitespace baseline."""

    return len(text.split())


def gather_python_files(root: Path) -> list[Path]:
    """Collect Python files recursively for baseline measurement."""

    return sorted(path for path in root.rglob("*.py") if path.is_file())


def calculate_totals(project_root: Path) -> tuple[int, int, int, int]:
    """Return files count, raw tokens, compressed tokens, and parse failures."""

    total_raw_tokens = 0
    total_compressed_tokens = 0
    total_files = 0
    parse_failures = 0
    for source_file in gather_python_files(project_root):
        text = source_file.read_text(encoding="utf-8", errors="ignore")
        total_raw_tokens += count_tokens(text)

        structure = extract_structure(str(source_file))
        if not structure.ok:
            parse_failures += 1
            continue

        compressed_markdown = emit_markdown(structure)
        total_compressed_tokens += count_tokens(compressed_markdown)
        total_files += 1

    return total_files, total_raw_tokens, total_compressed_tokens, parse_failures


def main() -> None:
    """Print aggregate baseline token stats for a project path."""

    project_root = REPO_ROOT / "sample_project"
    if not project_root.exists():
        print("sample_project/ not found. Create it with test corpus files first.")
        return

    total_files, raw_tokens, compressed_tokens, parse_failures = calculate_totals(project_root)
    ratio = (raw_tokens / compressed_tokens) if compressed_tokens else 0.0

    print(f"files={total_files}")
    print(f"raw_tokens={raw_tokens}")
    print(f"compressed_tokens={compressed_tokens}")
    print(f"compression_ratio={ratio:.2f}")
    print(f"parse_failures={parse_failures}")


if __name__ == "__main__":
    main()
