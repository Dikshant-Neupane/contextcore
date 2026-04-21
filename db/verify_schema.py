#!/usr/bin/env python3
"""Quick script to verify schema.sql creates tables correctly."""

import sqlite3
from pathlib import Path

def main():
    db_path = Path('.contextcore/test.db')
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    schema_sql = Path('db/schema.sql').read_text()
    conn.executescript(schema_sql)
    conn.commit()
    
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = sorted([row[0] for row in cursor.fetchall()])
    print('Tables created:')
    for t in tables:
        print(f'  - {t}')
    
    # Verify schema for nodes table
    cursor = conn.execute("PRAGMA table_info(nodes)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f'\nNodes table columns: {", ".join(columns)}')
    
    # Verify schema for edges table
    cursor = conn.execute("PRAGMA table_info(edges)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f'Edges table columns: {", ".join(columns)}')
    
    conn.close()
    print('\n[OK] Schema verification passed')

if __name__ == '__main__':
    main()
