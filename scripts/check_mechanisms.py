import sqlite3
import json

def check_mechanisms():
    conn = sqlite3.connect("data/web_persistence_v2.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Check bridges table
    cur.execute("SELECT bridge_type, COUNT(*) as cnt FROM bridges GROUP BY bridge_type")
    bridge_counts = {row['bridge_type']: row['cnt'] for row in cur.fetchall()}
    
    total_bridges = sum(bridge_counts.values())
    print(f"Total Bridges: {total_bridges}")
    for b_type, cnt in bridge_counts.items():
        print(f"  - {b_type}: {cnt}")
        
    print("\n")
    
    # Check constraints for bridges / mechanisms
    cur.execute("SELECT constraint_type, COUNT(*) as cnt FROM constraints GROUP BY constraint_type")
    constraint_counts = {row['constraint_type']: row['cnt'] for row in cur.fetchall()}
    
    total_constraints = sum(constraint_counts.values())
    print(f"Total Constraints: {total_constraints}")
    for c_type, cnt in constraint_counts.items():
        print(f"  - {c_type}: {cnt}")
        
    conn.close()

if __name__ == "__main__":
    check_mechanisms()
