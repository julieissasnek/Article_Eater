#!/usr/bin/env python3
"""
Analyze High-Signal Beliefs

This script connects to the pruned Web of Belief and extracts a sample
of the 40 THEORETICAL beliefs as well as a sample of beliefs that were
successfully assigned to known scientific domains (cog, social, affect, etc.).
"""

import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "web_persistence.db"

def list_theoretical_beliefs(cursor):
    cursor.execute("""
        SELECT domain, status, substr(content, 1, 100) as content_preview
        FROM beliefs
        WHERE level LIKE '%THEORETICAL%'
        ORDER BY domain, status
    """)
    rows = cursor.fetchall()
    print(f"\n=== THEORETICAL Beliefs ({len(rows)}) ===")
    for row in rows:
        domain = row[0] or "NULL"
        status = row[1]
        content = row[2]
        print(f"[{domain}] ({status}): {content}...")


def sample_domain_beliefs(cursor):
    # Get the counts per domain (excluding NULL/unknown)
    cursor.execute("""
        SELECT domain, COUNT(*) 
        FROM beliefs 
        WHERE domain IS NOT NULL AND domain != 'unknown' AND domain != 'unresolved'
        GROUP BY domain
        ORDER BY COUNT(*) DESC
    """)
    domain_counts = cursor.fetchall()

    print(f"\n=== Domain-Identified EMPIRICAL Beliefs ===")
    for domain, count in domain_counts:
        print(f"\n--- Domain: {domain} (Total: {count}) ---")
        
        # Get up to 3 examples per domain
        cursor.execute("""
            SELECT status, substr(content, 1, 100) as content_preview
            FROM beliefs
            WHERE domain = ? AND level LIKE '%EMPIRICAL%'
            ORDER BY RANDOM()
            LIMIT 3
        """, (domain,))
        
        examples = cursor.fetchall()
        for idx, ex in enumerate(examples, 1):
            status = ex[0]
            content = ex[1]
            print(f"  {idx}. ({status}): {content}...")

if __name__ == "__main__":
    if not DB_PATH.exists():
        print(f"Cannot find database at {DB_PATH}")
        exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    list_theoretical_beliefs(cursor)
    sample_domain_beliefs(cursor)
    
    conn.close()
