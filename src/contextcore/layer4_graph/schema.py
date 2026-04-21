"""
CONTEXTCORE — Layer 4 Knowledge Graph Schema
Dataclasses and enums for graph nodes, edges, and query results.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class NodeType(str, Enum):
    """Types of nodes in the knowledge graph."""

    FILE = "FILE"
    CLASS = "CLASS"
    FUNCTION = "FUNCTION"
    METHOD = "METHOD"
    IMPORT = "IMPORT"
    CONSTANT = "CONSTANT"
    DECORATOR = "DECORATOR"

    def __iter__(self):
        """Allow iteration over enum members (for test: all(isinstance(t, NodeType) for t in NodeType))."""
        return iter([member for member in NodeType])


class EdgeType(str, Enum):
    """Types of edges (relationships) in the knowledge graph."""

    IMPORTS = "IMPORTS"  # file imports another module
    CALLS = "CALLS"  # function/method calls another function
    CONTAINS = "CONTAINS"  # class contains a method, file contains class/function
    INHERITS = "INHERITS"  # class inherits from another class
    DECORATES = "DECORATES"  # decorator applied to function/class
    REFERENCES = "REFERENCES"  # general reference

    def __iter__(self):
        """Allow iteration over enum members."""
        return iter([member for member in EdgeType])


class EdgeConfidence(float, Enum):
    """Confidence levels for edge detection (0.0 to 1.0)."""

    HIGH = 1.0  # Syntactically certain (e.g., direct import statement)
    MEDIUM = 0.7  # Likely but inferred (e.g., function call detected in AST)
    LOW = 0.4  # Possible but uncertain (e.g., string-based import)


@dataclass
class GraphNode:
    """
    A node in the knowledge graph representing a code entity.
    
    Attributes:
        filepath: Path to the Python source file containing this node
        name: Identifier (function/class/module name)
        node_type: Category of this node (FILE, CLASS, FUNCTION, etc.)
        docstring: Optional documentation string
        line_start: Start line number in source (0-based)
        line_end: End line number in source (0-based)
        confidence: How confident we are in this node's accuracy (0.0-1.0)
    """

    filepath: str
    name: str
    node_type: NodeType
    docstring: Optional[str] = None
    line_start: int = 0
    line_end: int = 0
    confidence: float = 1.0

    @property
    def id(self) -> str:
        """
        Deterministic ID based on filepath + name + node_type.
        Ensures same code entity always gets same ID.
        """
        content = f"{self.filepath}::{self.name}::{self.node_type.value}".encode("utf-8")
        return hashlib.sha256(content).hexdigest()[:16]

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, GraphNode):
            return False
        return self.id == other.id


@dataclass
class GraphEdge:
    """
    An edge (relationship) in the knowledge graph.
    
    Attributes:
        source_id: ID of source node
        target_id: ID of target node
        edge_type: Category of relationship (IMPORTS, CALLS, etc.)
        confidence: How confident we are in this edge (0.0-1.0)
        metadata: Optional extra data (e.g., argument count for CALLS)
    """

    source_id: str
    target_id: str
    edge_type: EdgeType
    confidence: float = 1.0
    metadata: Optional[dict] = None

    @property
    def id(self) -> str:
        """
        Deterministic ID based on source_id + target_id + edge_type.
        Ensures same relationship always gets same ID.
        """
        content = f"{self.source_id}->{self.target_id}::{self.edge_type.value}".encode("utf-8")
        return hashlib.sha256(content).hexdigest()[:16]

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, GraphEdge):
            return False
        return self.id == other.id


@dataclass
class SubgraphResult:
    """
    Result of a subgraph query.
    
    Attributes:
        ranked_nodes: List of (node, score) or (node, depth) tuples, ranked by relevance
        total_tokens: Total token count for the subgraph (for context budget tracking)
        query_text: The original query text
        matched_count: Number of directly matched nodes (before BFS expansion)
    """

    ranked_nodes: list[tuple]  # List of (GraphNode, float) tuples: score or depth
    total_tokens: int
    query_text: str = ""
    matched_count: int = 0

    def __post_init__(self):
        """Validate total_tokens is reasonable."""
        if self.total_tokens < 0:
            raise ValueError(f"total_tokens must be non-negative, got {self.total_tokens}")
        if self.total_tokens > 10000:
            # Warn but don't fail — some queries may legitimately need more tokens
            pass
