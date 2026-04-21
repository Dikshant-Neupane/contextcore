"""
CONTEXTCORE — Layer 4 Graph Builder
Converts Layer 1 FileStructure output into SQLite-backed knowledge graph.
"""

from __future__ import annotations

import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from contextcore.layer1_ast.extractor import FileStructure, extract_structure
from contextcore.layer4_graph.schema import GraphNode, GraphEdge, NodeType, EdgeType


class GraphBuilder:
    """
    Builds and maintains a SQLite-backed knowledge graph.
    Indexes Python files, extracting nodes (classes, functions, etc.)
    and edges (contains, calls, imports, etc.).
    """

    def __init__(self, db_path: Path | str = ".contextcore/graph.db"):
        """
        Initialize builder with database path.
        
        Args:
            db_path: Path to SQLite database file. Creates if missing.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema if not already present."""
        # Path from src/contextcore/layer4_graph/builder.py → db/schema.sql at repo root
        schema_sql = Path(__file__).resolve().parent.parent.parent.parent / "db" / "schema.sql"
        if not schema_sql.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_sql}")

        conn = sqlite3.connect(self.db_path)
        schema_text = schema_sql.read_text()
        conn.executescript(schema_text)
        conn.commit()
        conn.close()

    def _get_conn(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def index_file(self, filepath: Path | str) -> None:
        """
        Index a single Python file.
        Extracts FileStructure using Layer 1, converts to graph, saves to DB.
        Re-indexing the same file updates the graph (no duplicates).
        
        Args:
            filepath: Path to Python file to index
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        # Extract structure using Layer 1
        file_struct = extract_structure(filepath)
        if not file_struct.ok:
            # Silently skip files with parse errors (already logged in tests)
            return

        conn = self._get_conn()
        try:
            # Remove old nodes/edges for this file (incremental update)
            conn.execute(
                "DELETE FROM edges WHERE source_id IN (SELECT id FROM nodes WHERE filepath = ?)",
                (str(filepath),),
            )
            conn.execute("DELETE FROM nodes WHERE filepath = ?", (str(filepath),))

            # Create FILE node
            file_node = GraphNode(
                filepath=str(filepath),
                name=filepath.stem,
                node_type=NodeType.FILE,
                line_start=0,
                line_end=file_struct.line_count,
            )
            self._insert_node(conn, file_node)

            # Extract and create IMPORTS edges
            imports = self._extract_imports(filepath)
            for imported_module in imports:
                # Create a synthetic node for the imported module
                import_node = GraphNode(
                    filepath=imported_module,
                    name=imported_module,
                    node_type=NodeType.IMPORT,
                )
                self._insert_node(conn, import_node)

                # Create IMPORTS edge
                edge = GraphEdge(
                    source_id=file_node.id,
                    target_id=import_node.id,
                    edge_type=EdgeType.IMPORTS,
                )
                self._insert_edge(conn, edge)

            # Create CLASS nodes and CONTAINS edges
            for class_struct in file_struct.classes:
                class_node = GraphNode(
                    filepath=str(filepath),
                    name=class_struct.name,
                    node_type=NodeType.CLASS,
                )
                self._insert_node(conn, class_node)

                # FILE contains CLASS
                edge = GraphEdge(
                    source_id=file_node.id,
                    target_id=class_node.id,
                    edge_type=EdgeType.CONTAINS,
                )
                self._insert_edge(conn, edge)

                # Create METHOD nodes under CLASS
                for method in class_struct.methods:
                    method_node = GraphNode(
                        filepath=str(filepath),
                        name=method.name,
                        node_type=NodeType.METHOD,
                    )
                    self._insert_node(conn, method_node)

                    # CLASS contains METHOD
                    edge = GraphEdge(
                        source_id=class_node.id,
                        target_id=method_node.id,
                        edge_type=EdgeType.CONTAINS,
                    )
                    self._insert_edge(conn, edge)

            # Create FUNCTION nodes and CONTAINS edges
            for func_sig in file_struct.functions:
                func_node = GraphNode(
                    filepath=str(filepath),
                    name=func_sig.name,
                    node_type=NodeType.FUNCTION,
                )
                self._insert_node(conn, func_node)

                # FILE contains FUNCTION
                edge = GraphEdge(
                    source_id=file_node.id,
                    target_id=func_node.id,
                    edge_type=EdgeType.CONTAINS,
                )
                self._insert_edge(conn, edge)

            conn.commit()
        finally:
            conn.close()

    def index_directory(self, directory: Path | str) -> None:
        """
        Recursively index all Python files in a directory.
        
        Args:
            directory: Path to directory to scan
        """
        directory = Path(directory)
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        for py_file in directory.rglob("*.py"):
            # Skip hidden files and __pycache__
            if any(part.startswith(".") or part == "__pycache__" for part in py_file.parts):
                continue
            try:
                self.index_file(py_file)
            except Exception:
                # Silently skip files with indexing errors
                pass

    def get_nodes_by_type(self, node_type: str | NodeType) -> list[GraphNode]:
        """
        Retrieve all nodes of a specific type.
        
        Args:
            node_type: NodeType enum member or string (e.g., "FUNCTION", "CLASS")
        
        Returns:
            List of GraphNode objects
        """
        if isinstance(node_type, NodeType):
            node_type = node_type.value
        else:
            node_type = str(node_type).upper()

        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """
                SELECT id, filepath, name, node_type, docstring, line_start, line_end, confidence
                FROM nodes WHERE node_type = ?
                """,
                (node_type,),
            )
            nodes = []
            for row in cursor.fetchall():
                node = GraphNode(
                    filepath=row["filepath"],
                    name=row["name"],
                    node_type=NodeType(row["node_type"]),
                    docstring=row["docstring"],
                    line_start=row["line_start"],
                    line_end=row["line_end"],
                    confidence=row["confidence"],
                )
                nodes.append(node)
            return nodes
        finally:
            conn.close()

    def get_edges_by_type(self, edge_type: str | EdgeType) -> list[GraphEdge]:
        """
        Retrieve all edges of a specific type.
        
        Args:
            edge_type: EdgeType enum member or string (e.g., "IMPORTS", "CONTAINS")
        
        Returns:
            List of GraphEdge objects
        """
        if isinstance(edge_type, EdgeType):
            edge_type = edge_type.value
        else:
            edge_type = str(edge_type).upper()

        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """
                SELECT id, source_id, target_id, edge_type, confidence, metadata
                FROM edges WHERE edge_type = ?
                """,
                (edge_type,),
            )
            edges = []
            for row in cursor.fetchall():
                edge = GraphEdge(
                    source_id=row["source_id"],
                    target_id=row["target_id"],
                    edge_type=EdgeType(row["edge_type"]),
                    confidence=row["confidence"],
                    metadata=row["metadata"],
                )
                edges.append(edge)
            return edges
        finally:
            conn.close()

    def flush(self) -> None:
        """Ensure all data is written to disk. (SQLite auto-commits, but included for API completeness.)"""
        conn = self._get_conn()
        try:
            conn.commit()
        finally:
            conn.close()

    def _insert_node(self, conn: sqlite3.Connection, node: GraphNode) -> None:
        """
        Insert or update a node in the database.
        Uses INSERT OR REPLACE to handle duplicates gracefully.
        """
        conn.execute(
            """
            INSERT OR REPLACE INTO nodes
            (id, filepath, name, node_type, docstring, line_start, line_end, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                node.id,
                node.filepath,
                node.name,
                node.node_type.value,
                node.docstring,
                node.line_start,
                node.line_end,
                node.confidence,
            ),
        )

    def _insert_edge(self, conn: sqlite3.Connection, edge: GraphEdge) -> None:
        """
        Insert or update an edge in the database.
        Uses INSERT OR REPLACE to handle duplicates gracefully.
        """
        metadata_str = None
        if edge.metadata:
            import json
            metadata_str = json.dumps(edge.metadata)

        conn.execute(
            """
            INSERT OR REPLACE INTO edges
            (id, source_id, target_id, edge_type, confidence, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                edge.id,
                edge.source_id,
                edge.target_id,
                edge.edge_type.value,
                edge.confidence,
                metadata_str,
            ),
        )

    def _extract_imports(self, filepath: Path) -> list[str]:
        """
        Extract top-level import statements from a Python file.
        Returns a list of module names (e.g., ["os", "sys", "pathlib"]).
        """
        try:
            from tree_sitter import Language, Parser as _TSParser
            import tree_sitter_python

            source_bytes = filepath.read_bytes()
            language = Language(tree_sitter_python.language())
            parser = _TSParser(language)
            root = parser.parse(source_bytes).root_node

            imports = []
            for child in root.children:
                if child.type == "import_statement":
                    # "import x" or "import x, y, z"
                    text = source_bytes[child.start_byte : child.end_byte].decode("utf-8")
                    # Extract module names from "import X"
                    if text.startswith("import "):
                        module_part = text[7:].strip()
                        for module in module_part.split(","):
                            module = module.split(" as ")[0].strip()
                            imports.append(module)
                elif child.type == "import_from_statement":
                    # "from x import y" or "from x import *"
                    text = source_bytes[child.start_byte : child.end_byte].decode("utf-8")
                    # Extract module name from "from X import Y"
                    if text.startswith("from "):
                        rest = text[5:].split(" import ")[0].strip()
                        imports.append(rest)
            return list(set(imports))  # Remove duplicates
        except Exception:
            # Silently return empty list on parse error
            return []
