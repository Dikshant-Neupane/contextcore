"""
CONTEXTCORE CLI — ADR-009: 4 commands only.
index / query / status / diff
All console output must be ASCII only (ADR-010).
"""

from __future__ import annotations

import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

import typer

from contextcore.layer1_ast.extractor import extract_structure
from contextcore.layer3_intent.classifier import classify_query
from contextcore.layer4_graph.builder import GraphBuilder
from contextcore.layer4_graph.querier import GraphQuerier
from contextcore.layer5_compress.emitter import emit_markdown

app = typer.Typer(add_completion=False, help="CONTEXTCORE — knowledge graph CLI")

DB_PATH = ".contextcore/contextcore.db"
META_PROJECT_PATH = "."
TASK_TYPE_CHOICES = {"AUTO", "DEBUG", "REFACTOR", "SCAFFOLD", "ONBOARD", "REVIEW", "SECURITY"}


def _get_db_path() -> Path:
    return Path(DB_PATH)


def _get_conn(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _db_stats(db_path: Path) -> tuple[int, int]:
    """Return (node_count, edge_count) from the graph DB."""
    conn = _get_conn(db_path)
    try:
        node_count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        edge_count = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        return node_count, edge_count
    finally:
        conn.close()


def _resolve_task_type(query_text: str, task_type: str) -> str:
    """Resolve task type option, using Layer 3 classifier when AUTO is selected."""
    normalized = task_type.strip().upper()
    if normalized not in TASK_TYPE_CHOICES:
        raise ValueError(f"Invalid task type: {task_type}")
    if normalized == "AUTO":
        return classify_query(query_text).task_type.value
    return normalized


def _update_meta(db_path: Path, project_path: str, file_count: int) -> None:
    """Upsert a row in index_meta with current stats."""
    conn = _get_conn(db_path)
    try:
        node_count, edge_count = _db_stats(db_path)
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        existing = conn.execute(
            "SELECT id FROM index_meta WHERE project_path = ?", (project_path,)
        ).fetchone()
        if existing:
            conn.execute(
                """UPDATE index_meta
                   SET last_indexed_at = ?, file_count = ?, node_count = ?, edge_count = ?
                   WHERE project_path = ?""",
                (now, file_count, node_count, edge_count, project_path),
            )
        else:
            conn.execute(
                """INSERT INTO index_meta
                   (project_path, last_indexed_at, file_count, node_count, edge_count)
                   VALUES (?, ?, ?, ?, ?)""",
                (project_path, now, file_count, node_count, edge_count),
            )
        conn.commit()
    finally:
        conn.close()


@app.command()
def index(path: str = typer.Argument(".", help="Project directory to index")) -> None:
    """Index a project directory into the graph."""
    project_path = Path(path).resolve()
    if not project_path.is_dir():
        typer.echo(f"[FAIL] Not a directory: {path}")
        raise typer.Exit(code=1)

    db_path = _get_db_path()
    t0 = time.perf_counter()

    builder = GraphBuilder(db_path=db_path)

    py_files = [
        f for f in project_path.rglob("*.py")
        if not any(p.startswith(".") or p == "__pycache__" for p in f.parts)
    ]

    file_count = 0
    for py_file in py_files:
        try:
            builder.index_file(py_file)
            file_count += 1
        except Exception:
            pass

    _update_meta(db_path, str(project_path), file_count)

    node_count, edge_count = _db_stats(db_path)
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    typer.echo(
        f"[INFO] Indexed {file_count} files | {node_count} nodes | {edge_count} edges | {elapsed_ms}ms"
    )


@app.command()
def query(
    node_name: str = typer.Argument(..., help="Node name or keyword to search for"),
    depth: int = typer.Option(3, help="BFS depth for subgraph expansion"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    task_type: str = typer.Option("AUTO", "--task-type", help="AUTO or explicit task mode"),
) -> None:
    """Retrieve ranked subgraph for a node."""
    db_path = _get_db_path()
    if not db_path.exists():
        typer.echo("[FAIL] No graph found. Run: contextcore index <path>")
        raise typer.Exit(code=1)

    t0 = time.perf_counter()
    querier = GraphQuerier(db_path=db_path)
    try:
        resolved_task_type = _resolve_task_type(node_name, task_type)
    except ValueError as exc:
        typer.echo(f"[FAIL] {exc}")
        raise typer.Exit(code=1)

    result = querier.query(node_name, task_type=resolved_task_type)
    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    if not result.ranked_nodes:
        typer.echo(f"[WARN] No results found for: {node_name}")
        raise typer.Exit(code=0)

    if json_output:
        import json
        nodes_data = [
            {"name": node.name, "filepath": node.filepath, "type": node.node_type.value, "score": round(score, 4)}
            for node, score in result.ranked_nodes
        ]
        typer.echo(json.dumps({"query": node_name, "nodes": nodes_data, "total_tokens": result.total_tokens}))
    else:
        # Emit markdown for each unique file in the result
        from contextcore.layer4_graph.schema import NodeType
        typer.echo(f"## {node_name}\n")
        for node, score in result.ranked_nodes:
            type_label = node.node_type.value
            typer.echo(f"- [{type_label}] {node.name} ({Path(node.filepath).name}) score={score:.3f}")

        typer.echo(
            f"\n[INFO] {result.matched_count} nodes | {result.total_tokens} tokens | {elapsed_ms}ms"
        )


@app.command()
def status() -> None:
    """Show graph statistics."""
    db_path = _get_db_path()
    if not db_path.exists():
        typer.echo("[FAIL] No graph found. Run: contextcore index <path>")
        raise typer.Exit(code=1)

    node_count, edge_count = _db_stats(db_path)
    db_size_bytes = db_path.stat().st_size
    db_size_mb = db_size_bytes / (1024 * 1024)

    conn = _get_conn(db_path)
    try:
        meta = conn.execute(
            "SELECT last_indexed_at, file_count, project_path FROM index_meta ORDER BY id DESC LIMIT 1"
        ).fetchone()
    finally:
        conn.close()

    last_indexed = meta["last_indexed_at"] if meta else "never"
    project_path = meta["project_path"] if meta else "unknown"

    # Count stale files (modified after last index)
    stale_count = 0
    if meta and meta["last_indexed_at"]:
        try:
            last_ts = datetime.fromisoformat(meta["last_indexed_at"])
            p = Path(project_path)
            if p.is_dir():
                for f in p.rglob("*.py"):
                    if not any(part.startswith(".") or part == "__pycache__" for part in f.parts):
                        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
                        if mtime > last_ts:
                            stale_count += 1
        except Exception:
            pass

    typer.echo("[INFO] CONTEXTCORE STATUS")
    typer.echo("[INFO] ==================")
    typer.echo(f"[INFO] Graph:        {db_path}")
    typer.echo(f"[INFO] Nodes:        {node_count}")
    typer.echo(f"[INFO] Edges:        {edge_count}")
    typer.echo(f"[INFO] Last indexed: {last_indexed}")
    typer.echo(f"[INFO] Staleness:    {stale_count} files changed since last index")
    typer.echo(f"[INFO] DB size:      {db_size_mb:.1f} MB")


@app.command()
def diff() -> None:
    """Show what changed since last index."""
    db_path = _get_db_path()
    if not db_path.exists():
        typer.echo("[FAIL] No graph found. Run: contextcore index <path>")
        raise typer.Exit(code=1)

    conn = _get_conn(db_path)
    try:
        meta = conn.execute(
            "SELECT last_indexed_at, project_path FROM index_meta ORDER BY id DESC LIMIT 1"
        ).fetchone()
    finally:
        conn.close()

    if not meta or not meta["last_indexed_at"]:
        typer.echo("[WARN] No index metadata found. Run: contextcore index <path>")
        raise typer.Exit(code=0)

    try:
        last_ts = datetime.fromisoformat(meta["last_indexed_at"])
    except ValueError:
        typer.echo("[WARN] Could not parse last indexed timestamp.")
        raise typer.Exit(code=0)

    project_path = Path(meta["project_path"])
    if not project_path.is_dir():
        typer.echo(f"[WARN] Project path not found: {project_path}")
        raise typer.Exit(code=0)

    stale_files = []
    for f in project_path.rglob("*.py"):
        if not any(part.startswith(".") or part == "__pycache__" for part in f.parts):
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            if mtime > last_ts:
                stale_files.append(f)

    if not stale_files:
        typer.echo("[INFO] No changes since last index.")
    else:
        for f in stale_files:
            typer.echo(f"[WARN] STALE: {f}")
        typer.echo("[INFO] Run: contextcore index to refresh")


if __name__ == "__main__":
    app()
