#!/usr/bin/env python3
"""
Sync master_doc_parts metadata to SQLite database.

Creates and maintains the master_doc_parts table tracking all parts with hashes,
line counts, modification dates, and section coverage.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path("/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/data/article_eater.db")
PARTS_DIR = Path("/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/master_doc_parts")
MANIFEST_PATH = PARTS_DIR / "MANIFEST.md"

# Map part names to section ranges
PART_SECTIONS = {
    "00_FRONTMATTER": ["TOC", "Navigation", "Formula Transition"],
    "PART_I_EXPLANATION_GAP": ["1-32"],
    "PART_II_THEORETICAL": ["33-42"],
    "PART_III_PREDICTION": ["43-47"],
    "PART_IV_CREDENCE": ["48-53"],
    "PART_V_PANEL_CONVENING": ["54-59"],
    "PART_VI_DOMAIN_PANELS": ["60-71"],
    "PART_VII_T15_REDUCTIONS": ["72-78"],
    "PART_VIII_IE_DPT": ["79-83"],
    "PART_IX_WEB_OF_BELIEF": ["84-89"],
    "PART_X_TEMPLATE_LIBRARY": ["X"],
    "PART_XI_ARCH_TYPOLOGY": ["XI"],
    "PART_XII_INTERACTIONS": ["XII"],
    "PART_XIII_LIMITATIONS": ["107-113"],
    "PART_XIV_APPLICATIONS": ["114-118"],
    "PART_XV_TECHNICAL": ["119-124"],
    "PART_XVI_PHILOSOPHY": ["125-127"],
    "PART_XVII_META_EPISTEMOLOGY": ["128-131"],
    "PART_XVIII_INFRASTRUCTURE": ["132-139"],
    "PART_XIX_TERMINOLOGY": ["140"],
    "PART_XX_APPENDIX": ["141-146"],
    "PART_XXI_SOURCE_INDEX": ["147"],
}

def init_db():
    """Create the master_doc_parts table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS master_doc_parts (
            part_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            line_count INTEGER,
            char_count INTEGER,
            sha256 TEXT,
            last_modified TEXT,
            last_assembled TEXT,
            sections TEXT
        )
    ''')

    conn.commit()
    return conn

def load_manifest():
    """Load the manifest file if it exists."""
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            content = f.read()
            # Parse simple markdown table
            parts = {}
            for line in content.split('\n')[10:]:  # Skip header
                if not line.strip() or line.startswith('|---'):
                    continue
                if line.startswith('|'):
                    cells = [c.strip() for c in line.split('|')[1:-1]]
                    if len(cells) >= 5:
                        part_name = cells[0]
                        try:
                            parts[part_name] = {
                                'lines': int(cells[1]),
                                'chars': int(cells[2]),
                                'sha256': cells[3],
                                'last_modified': cells[4],
                            }
                        except (ValueError, IndexError):
                            continue
            return parts
    return {}

def sync_parts(conn):
    """Sync all parts from manifest to database."""
    cursor = conn.cursor()
    manifest = load_manifest()
    now = datetime.now().isoformat()

    for part_id, part_data in manifest.items():
        sections = json.dumps(PART_SECTIONS.get(part_id, []))

        cursor.execute('''
            INSERT OR REPLACE INTO master_doc_parts
            (part_id, filename, line_count, char_count, sha256, last_modified, last_assembled, sections)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            part_id,
            f"{part_id}.md",
            part_data.get('lines', 0),
            part_data.get('chars', 0),
            part_data.get('sha256', ''),
            part_data.get('last_modified', ''),
            now,
            sections,
        ))

    conn.commit()
    print(f"Synced {len(manifest)} parts to database")

def query_parts(conn):
    """Query and display parts from database."""
    cursor = conn.cursor()
    cursor.execute('SELECT part_id, line_count, char_count, sha256 FROM master_doc_parts ORDER BY part_id')
    rows = cursor.fetchall()

    print(f"\nParts in database ({len(rows)} total):\n")
    print(f"{'Part':<30} {'Lines':>8} {'Bytes':>10} {'SHA256':<12}")
    print("-" * 65)

    total_lines = 0
    total_chars = 0

    for part_id, lines, chars, sha256 in rows:
        print(f"{part_id:<30} {lines:>8} {chars:>10} {sha256[:12]}")
        total_lines += lines or 0
        total_chars += chars or 0

    print("-" * 65)
    print(f"{'TOTAL':<30} {total_lines:>8} {total_chars:>10}")

def main():
    print("Initializing database...")
    conn = init_db()

    print("Syncing metadata from manifest...")
    sync_parts(conn)

    print("\nQuerying database...")
    query_parts(conn)

    conn.close()
    print("\nDone.")

if __name__ == '__main__':
    main()
