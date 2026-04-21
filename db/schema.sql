-- CONTEXTCORE — SQLite Graph Database Schema
-- Layer 4: Knowledge Graph storage
-- Created for v2.0

CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    filepath TEXT NOT NULL,
    name TEXT NOT NULL,
    node_type TEXT NOT NULL,  -- FILE, CLASS, FUNCTION, METHOD, IMPORT, CONSTANT, DECORATOR
    docstring TEXT,
    line_start INTEGER DEFAULT 0,
    line_end INTEGER DEFAULT 0,
    confidence REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(filepath, name, node_type)
);

CREATE TABLE IF NOT EXISTS edges (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    edge_type TEXT NOT NULL,  -- IMPORTS, CALLS, CONTAINS, INHERITS, DECORATES, REFERENCES
    confidence REAL DEFAULT 1.0,
    metadata TEXT,  -- JSON-serialized optional metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES nodes(id) ON DELETE CASCADE,
    UNIQUE(source_id, target_id, edge_type)
);

CREATE TABLE IF NOT EXISTS index_meta (
    id INTEGER PRIMARY KEY,
    project_path TEXT NOT NULL,
    last_indexed_at TIMESTAMP,
    file_count INTEGER DEFAULT 0,
    node_count INTEGER DEFAULT 0,
    edge_count INTEGER DEFAULT 0,
    schema_version TEXT DEFAULT '1.0'
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_nodes_filepath ON nodes(filepath);
CREATE INDEX IF NOT EXISTS idx_nodes_name ON nodes(name);
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(edge_type);
CREATE INDEX IF NOT EXISTS idx_edges_source_target ON edges(source_id, target_id);
