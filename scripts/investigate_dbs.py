import sqlite3
import os
from pathlib import Path

def check_db(db_path):
    print(f"--- Investigating {db_path} ---")
    if not os.path.exists(db_path):
        print("File does not exist\n")
        return
        
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='beliefs'")
        schema = c.fetchone()
        if schema:
            print("Schema for 'beliefs':")
            print(schema[0])
            
            c.execute("SELECT count(*) FROM beliefs")
            count = c.fetchone()[0]
            print(f"Row count: {count}")
        else:
            print("Table 'beliefs' not found.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
    print()

repo_root = Path(__file__).resolve().parent.parent
check_db(str(repo_root / "data" / "web_persistence.db"))
check_db(str(repo_root / "data" / "web_persistence_v2.db"))
check_db(str(repo_root / "ae.db"))

