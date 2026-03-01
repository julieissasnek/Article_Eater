import sqlite3
try:
    conn = sqlite3.connect("data/web_persistence_v2.db")
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM sqlite_master")
    print(cur.fetchone())
    conn.close()
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
