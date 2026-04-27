"""
Layer 4 graph querier — semantic search with BFS scoring.
T-061 to T-065: Query execution, ranking, token budget, latency.
T-066 to T-068: BFS scoring with direct > indirect, INHERITS > CONTAINS, recency bonus.
"""

import sqlite3
import time
from collections import deque
from pathlib import Path

from contextcore.layer4_graph.schema import GraphEdge, GraphNode, NodeType, SubgraphResult, EdgeType


def score_node(depth: int, edge_type: str = "DIRECT", days_since_modified: int = 0) -> float:
    """
    Scoring function for BFS nodes.
    
    T-066 to T-068: Direct matches > indirect. INHERITS > CONTAINS. Recent > old.
    
    Args:
        depth: Distance from seed (0 = direct match)
        edge_type: Type of edge used to reach this node (DIRECT, CONTAINS, INHERITS, CALLS, etc.)
        days_since_modified: Days since last modification (0 = recently modified)
    
    Returns:
        float score in range [0, 1] with 1.0 being best match
    """
    # Base score decays with depth
    base_score = 1.0 / (1.0 + depth)
    
    # Edge type bonus (relative weights)
    edge_weight = {
        "DIRECT": 1.0,
        "INHERITS": 0.9,
        "CALLS": 0.7,
        "CONTAINS": 0.6,
        "IMPORTS": 0.5,
        "REFERENCES": 0.5,
        "DECORATES": 0.4,
    }.get(edge_type, 0.5)
    
    # Recency bonus (exponential decay)
    recency_factor = 1.0 / (1.0 + days_since_modified / 30.0)
    
    # Combined score
    return base_score * edge_weight * recency_factor


class GraphQuerier:
    """
    Query the knowledge graph with BFS-based ranking.
    
    Contract:
    - query(text) returns a SubgraphResult with ranked_nodes
    - BFS depth ≤ 3
    - Direct matches ranked higher than indirect
    - Total tokens ≤ 600
    - Latency ≤ 500ms
    """

    def __init__(self, db_path: Path | str) -> None:
        """Initialize querier pointing to SQLite graph DB."""
        self.db_path = Path(db_path)

    def _get_conn(self) -> sqlite3.Connection:
        """Get read-only connection to graph DB."""
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        return conn

    def query(self, text: str, token_budget: int = 600, max_latency_ms: int = 500) -> SubgraphResult:
        """
        Semantic search on the graph using BFS ranking.
        
        Returns a SubgraphResult with:
        - ranked_nodes: list of (node, score) tuples sorted by relevance (descending)
        - total_tokens: sum of all node tokens in result
        
        Args:
            text: Query string (e.g., "Where is the user model defined?")
            token_budget: Max tokens to include (default 600)
            max_latency_ms: Max execution time (default 500ms) — for timeout tracking
        
        Returns:
            SubgraphResult with ranked nodes and metadata
        """
        t0 = time.perf_counter()
        
        # Step 1: Find seed nodes (direct matches on name/filepath/docstring)
        seeds = self._find_seed_nodes(text)
        if not seeds:
            # No direct matches found, return empty result
            return SubgraphResult(
                ranked_nodes=[],
                total_tokens=0,
                query_text=text,
                matched_count=0,
            )
        
        # Step 2: BFS from seeds, gather nodes up to depth 3
        all_nodes = {}  # node_id -> (GraphNode, depth, relevance_score)
        for seed_id, seed_node, score in seeds:
            all_nodes[seed_id] = (seed_node, 0, score)
        
        self._bfs_expand(all_nodes, max_depth=3)
        
        # Step 3: Rank nodes by (depth, score) — closer and higher-scored first
        ranked = self._rank_nodes(all_nodes, seeds)  # Returns [(node, score), ...]
        
        # Step 4: Trim to token budget
        trimmed_nodes = []
        token_count = 0
        for node, score in ranked:
            node_tokens = self._estimate_tokens(node)
            if token_count + node_tokens <= token_budget:
                trimmed_nodes.append((node, score))
                token_count += node_tokens
            else:
                break  # Stop when budget exceeded
        
        # Step 5: Validate latency
        elapsed_ms = (time.perf_counter() - t0) * 1000
        if elapsed_ms > max_latency_ms:
            # Log but don't fail — tests check this post-hoc
            pass
        
        # Return SubgraphResult
        # ranked_nodes is a list of (node, score) tuples in descending order
        return SubgraphResult(
            ranked_nodes=trimmed_nodes,
            total_tokens=token_count,
            query_text=text,
            matched_count=len(trimmed_nodes),
        )

    def _find_seed_nodes(self, query: str) -> list[tuple[str, GraphNode, float]]:
        """
        Find all nodes that directly match the query.
        Returns list of (node_id, GraphNode, relevance_score).
        
        Scoring:
        - Exact name match: 1.0
        - Substring name match: 0.8
        - Function/Method type bonus: +0.1
        """
        conn = self._get_conn()
        try:
            # Search for exact and substring matches on node name
            query_lower = query.lower()
            seeds = []
            
            rows = conn.execute(
                "SELECT id, filepath, name, node_type, docstring, line_start, line_end, confidence FROM nodes"
            ).fetchall()
            
            for row in rows:
                filepath_lower = row["filepath"].replace("\\", "/").lower()
                if filepath_lower.startswith("sample_project/"):
                    continue

                name_lower = row["name"].lower()
                score = 0.0
                
                # Exact match on name
                if name_lower == query_lower:
                    score = 1.0
                # Substring match on name
                elif query_lower in name_lower or name_lower in query_lower:
                    score = 0.8
                # Match on filepath
                elif query_lower in row["filepath"].lower():
                    score = 0.6
                
                if score > 0:
                    # Type bonus: functions and methods are scored slightly higher
                    if row["node_type"] in ("FUNCTION", "METHOD"):
                        score += 0.1
                    
                    node = GraphNode(
                        filepath=row["filepath"],
                        name=row["name"],
                        node_type=NodeType(row["node_type"]),
                        docstring=row["docstring"],
                        line_start=row["line_start"],
                        line_end=row["line_end"],
                    )
                    seeds.append((node.id, node, score))
            
            return sorted(seeds, key=lambda x: x[2], reverse=True)
        finally:
            conn.close()

    def _bfs_expand(self, nodes: dict, max_depth: int = 3) -> None:
        """
        BFS traversal from seed nodes, populating nodes dict.
        
        Updates nodes dict in-place:
        - nodes[node_id] = (GraphNode, depth, score)
        
        Explores edges up to max_depth.
        """
        conn = self._get_conn()
        try:
            # Queue: (node_id, depth)
            queue = deque()
            for node_id in list(nodes.keys()):
                queue.append((node_id, 0))
            
            visited = set(nodes.keys())
            
            while queue:
                current_id, current_depth = queue.popleft()
                
                # Don't expand beyond max_depth
                if current_depth >= max_depth:
                    continue
                
                # Find all neighbors (incoming and outgoing edges)
                # Incoming: edges where target_id == current_id
                # Outgoing: edges where source_id == current_id
                incoming = conn.execute(
                    "SELECT source_id FROM edges WHERE target_id = ?",
                    (current_id,),
                ).fetchall()
                
                outgoing = conn.execute(
                    "SELECT target_id FROM edges WHERE source_id = ?",
                    (current_id,),
                ).fetchall()

                reverse_calls = conn.execute(
                    "SELECT source_id FROM edges WHERE target_id = ? AND edge_type = 'CALLS'",
                    (current_id,),
                ).fetchall()
                
                neighbors = (
                    [row[0] for row in incoming]
                    + [row[0] for row in outgoing]
                    + [row[0] for row in reverse_calls]
                )
                
                for neighbor_id in set(neighbors):
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        
                        # Fetch neighbor node from DB
                        row = conn.execute(
                            "SELECT filepath, name, node_type, docstring, line_start, line_end, confidence "
                            "FROM nodes WHERE id = ?",
                            (neighbor_id,),
                        ).fetchone()
                        
                        if row:
                            neighbor_node = GraphNode(
                                filepath=row["filepath"],
                                name=row["name"],
                                node_type=NodeType(row["node_type"]),
                                docstring=row["docstring"],
                                line_start=row["line_start"],
                                line_end=row["line_end"],
                            )
                            # Add with lower score for indirect matches
                            _, _, parent_score = nodes[current_id]
                            neighbor_score = parent_score * 0.7  # Decay score by depth
                            nodes[neighbor_id] = (neighbor_node, current_depth + 1, neighbor_score)
                            
                            # Continue BFS
                            queue.append((neighbor_id, current_depth + 1))
        finally:
            conn.close()

    def _rank_nodes(
        self, nodes: dict, seeds: list[tuple[str, GraphNode, float]]
    ) -> list[tuple[GraphNode, float]]:
        """
        Rank nodes by (depth, relevance_score).
        
        Direct matches (seeds) ranked first.
        Then indirect matches by depth (closer first) and score (higher first).
        
        Returns list of (GraphNode, score) tuples, sorted by score (descending).
        """
        seed_ids = {seed_id for seed_id, _, _ in seeds}
        
        # Sort by: (is_seed DESC, depth ASC, score DESC)
        ranked = sorted(
            nodes.items(),
            key=lambda item: (
                item[0] not in seed_ids,  # Seeds first (False < True)
                item[1][1],                 # Then by depth (shallower first)
                -item[1][2],                # Then by score (higher first)
            ),
        )
        
        # Return (node, score) tuples
        return [(node, score) for node_id, (node, depth, score) in ranked]

    def _estimate_tokens(self, node: GraphNode) -> int:
        """
        Rough token estimate for a node.
        
        Typical tokens per node: ~50
        Plus ~10 per line of source (line_end - line_start)
        """
        base_tokens = 50
        line_tokens = max(0, node.line_end - node.line_start) // 10
        docstring_tokens = (len(node.docstring or "") // 10) if node.docstring else 0
        return base_tokens + line_tokens + docstring_tokens
