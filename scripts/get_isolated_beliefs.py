import sqlite3
import sys
from pathlib import Path
from src.services.db_locator import resolve_web_db

def get_isolated():
    db_path = resolve_web_db(None, prefer="integrated")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Query for isolated beliefs (belief_id not in constraints as source or target)
    query = """
    SELECT b.belief_id, b.content
    FROM beliefs b
    WHERE b.web_id = 'master:web:accumulated'
      AND b.belief_id NOT IN (
          SELECT source_id FROM constraints WHERE web_id = 'master:web:accumulated'
          UNION
          SELECT target_id FROM constraints WHERE web_id = 'master:web:accumulated'
      )
    LIMIT 5;
    """
    
    rows = conn.execute(query).fetchall()
    for i, r in enumerate(rows):
        print(f"--- Example {i+1} ---")
        print(f"ID: {r['belief_id']}")
        print(f"Content: {r['content'][:300]}")
        print()

if __name__ == '__main__':
    get_isolated()
