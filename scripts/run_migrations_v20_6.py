#!/usr/bin/env python3
import sqlite3, sys
def ensure_column(conn, table, column, colspec):
    cur = conn.execute(f"PRAGMA table_info({table})"); cols = [r[1] for r in cur.fetchall()]
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {colspec}")
        print(f"Added {table}.{column}")
def main(db_path='ae.db'):
    conn = sqlite3.connect(db_path)
    try: ensure_column(conn, 'articles', 'raw_abstract', 'TEXT')
    except Exception as e: print('WARN:', e)
    conn.commit(); conn.close(); print('Migration (v20.6.x) complete.')
if __name__=='__main__':
    main(sys.argv[1] if len(sys.argv)>1 else 'ae.db')