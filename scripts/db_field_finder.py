#!/usr/bin/env python3
"""
db_field_finder.py — Universal DB Discovery for AI Agents
=========================================================

Scans all SQLite databases in the project and creates a machine-readable
catalogue of every table, column, type, row count, and sample values.

Usage:
    python3 scripts/db_field_finder.py                   # Full scan
    python3 scripts/db_field_finder.py --search belief    # Find tables/cols matching "belief"
    python3 scripts/db_field_finder.py --db data/web_persistence.db  # Scan specific DB

Output: Markdown catalogue to stdout. Also writes JSON to data/db_catalogue.json.

Why this exists:
    AI agents waste time guessing DB paths, table names, and column names.
    This script gives any agent instant, authoritative answers.
"""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".tox"}


def find_all_dbs(root: Path, max_depth: int = 5) -> list[Path]:
    """Find all .db files in the project."""
    dbs = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded dirs
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        # Check depth
        depth = len(Path(dirpath).relative_to(root).parts)
        if depth > max_depth:
            dirnames.clear()
            continue
        for f in filenames:
            if f.endswith(".db"):
                dbs.append(Path(dirpath) / f)
    return sorted(dbs)


def scan_db(db_path: Path, sample_rows: int = 3) -> dict:
    """Scan a single DB and return its catalogue."""
    result = {
        "path": str(db_path),
        "relative_path": str(db_path.relative_to(PROJECT_ROOT)) if db_path.is_relative_to(PROJECT_ROOT) else str(db_path),
        "size_bytes": db_path.stat().st_size if db_path.exists() else 0,
        "size_human": _human_size(db_path.stat().st_size) if db_path.exists() else "0",
        "accessible": False,
        "tables": {},
        "error": None,
    }

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        result["accessible"] = True
    except Exception as e:
        result["error"] = str(e)
        # Try without read-only
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            result["accessible"] = True
        except Exception as e2:
            result["error"] = f"ro: {e} | rw: {e2}"
            return result

    try:
        # Get all tables
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()

        for (table_name,) in tables:
            table_info = {
                "row_count": 0,
                "columns": [],
                "sample_values": {},
                "indexes": [],
            }

            # Row count
            try:
                cnt = conn.execute(f'SELECT COUNT(*) FROM [{table_name}]').fetchone()[0]
                table_info["row_count"] = cnt
            except Exception:
                pass

            # Column info
            try:
                cols = conn.execute(f"PRAGMA table_info([{table_name}])").fetchall()
                for col in cols:
                    col_dict = {
                        "name": col[1],
                        "type": col[2],
                        "notnull": bool(col[3]),
                        "default": col[4],
                        "pk": bool(col[5]),
                    }
                    table_info["columns"].append(col_dict)
            except Exception:
                pass

            # Sample values (first N rows)
            try:
                if table_info["row_count"] > 0:
                    rows = conn.execute(
                        f"SELECT * FROM [{table_name}] LIMIT {sample_rows}"
                    ).fetchall()
                    col_names = [c["name"] for c in table_info["columns"]]
                    for col_name in col_names:
                        values = []
                        for row in rows:
                            val = row[col_name] if col_name in row.keys() else None
                            # Truncate long strings
                            if isinstance(val, str) and len(val) > 200:
                                val = val[:200] + "..."
                            values.append(val)
                        table_info["sample_values"][col_name] = values
            except Exception:
                pass

            # Indexes
            try:
                idxs = conn.execute(
                    f"PRAGMA index_list([{table_name}])"
                ).fetchall()
                for idx in idxs:
                    table_info["indexes"].append(idx[1])
            except Exception:
                pass

            result["tables"][table_name] = table_info

    except Exception as e:
        result["error"] = str(e)
    finally:
        conn.close()

    return result


def search_catalogue(catalogue: list[dict], query: str) -> list[dict]:
    """Search the catalogue for tables/columns matching a query."""
    query_lower = query.lower()
    matches = []

    for db in catalogue:
        for table_name, table_info in db.get("tables", {}).items():
            # Match table name
            table_match = query_lower in table_name.lower()

            # Match column names
            matching_cols = [
                c for c in table_info.get("columns", [])
                if query_lower in c["name"].lower()
            ]

            # Match sample values
            value_matches = []
            for col_name, values in table_info.get("sample_values", {}).items():
                for v in values:
                    if v and query_lower in str(v).lower():
                        value_matches.append((col_name, v))
                        break

            if table_match or matching_cols or value_matches:
                matches.append({
                    "db": db["relative_path"],
                    "db_size": db["size_human"],
                    "table": table_name,
                    "row_count": table_info["row_count"],
                    "table_name_match": table_match,
                    "matching_columns": [c["name"] for c in matching_cols],
                    "value_matches": value_matches[:3],
                    "all_columns": [c["name"] for c in table_info.get("columns", [])],
                })

    return matches


def print_catalogue_md(catalogue: list[dict], file=sys.stdout):
    """Print catalogue as markdown."""
    total_dbs = len(catalogue)
    accessible = sum(1 for d in catalogue if d["accessible"])
    total_tables = sum(len(d.get("tables", {})) for d in catalogue)

    print(f"# DB Catalogue — {datetime.now().strftime('%Y-%m-%d %H:%M')}", file=file)
    print(f"\n**{total_dbs} databases found, {accessible} accessible, {total_tables} total tables**\n", file=file)

    for db in catalogue:
        rel = db["relative_path"]
        size = db["size_human"]
        acc = "✅" if db["accessible"] else "❌"

        print(f"## {acc} `{rel}` ({size})", file=file)

        if db.get("error"):
            print(f"\n> Error: {db['error']}\n", file=file)
            continue

        if not db.get("tables"):
            print(f"\n*No tables*\n", file=file)
            continue

        for table_name, tinfo in db["tables"].items():
            print(f"\n### `{table_name}` ({tinfo['row_count']} rows)", file=file)
            if tinfo["columns"]:
                print(f"\n| Column | Type | PK | Sample |", file=file)
                print(f"|--------|------|----|--------|", file=file)
                for col in tinfo["columns"]:
                    sample = ""
                    vals = tinfo.get("sample_values", {}).get(col["name"], [])
                    if vals:
                        sample = str(vals[0])[:60] if vals[0] is not None else "NULL"
                    pk = "🔑" if col["pk"] else ""
                    print(f"| `{col['name']}` | {col['type']} | {pk} | {sample} |", file=file)
            print(file=file)


def print_search_md(matches: list[dict], query: str, file=sys.stdout):
    """Print search results as markdown."""
    print(f"# Search Results for '{query}'\n", file=file)
    print(f"**{len(matches)} matches found**\n", file=file)

    for m in matches:
        print(f"## `{m['db']}` → `{m['table']}` ({m['row_count']} rows)", file=file)
        if m["table_name_match"]:
            print(f"  - 📋 **Table name matches**", file=file)
        if m["matching_columns"]:
            print(f"  - 📊 **Matching columns**: {', '.join(f'`{c}`' for c in m['matching_columns'])}", file=file)
        if m["value_matches"]:
            for col, val in m["value_matches"]:
                print(f"  - 🔍 **Value match** in `{col}`: {str(val)[:80]}", file=file)
        print(f"  - All columns: {', '.join(f'`{c}`' for c in m['all_columns'])}", file=file)
        print(file=file)


def _human_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"


def main():
    parser = argparse.ArgumentParser(description="DB Field Finder for AI Agents")
    parser.add_argument("--search", "-s", help="Search for tables/columns matching query")
    parser.add_argument("--db", help="Scan specific DB file")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of markdown")
    parser.add_argument("--save", action="store_true", help="Save catalogue to data/db_catalogue.json")
    parser.add_argument("--max-depth", type=int, default=5, help="Max directory depth")
    parser.add_argument("--samples", type=int, default=3, help="Sample rows per table")
    args = parser.parse_args()

    # Find & scan DBs
    if args.db:
        db_path = Path(args.db)
        if not db_path.is_absolute():
            db_path = PROJECT_ROOT / db_path
        dbs = [db_path]
    else:
        dbs = find_all_dbs(PROJECT_ROOT, args.max_depth)

    print(f"Scanning {len(dbs)} databases...", file=sys.stderr)
    catalogue = []
    for db_path in dbs:
        try:
            entry = scan_db(db_path, args.samples)
            catalogue.append(entry)
        except Exception as e:
            catalogue.append({
                "path": str(db_path),
                "relative_path": str(db_path.relative_to(PROJECT_ROOT)) if db_path.is_relative_to(PROJECT_ROOT) else str(db_path),
                "accessible": False,
                "error": str(e),
                "tables": {},
            })

    # Search or display
    if args.search:
        matches = search_catalogue(catalogue, args.search)
        if args.json:
            print(json.dumps(matches, indent=2, default=str))
        else:
            print_search_md(matches, args.search)
    else:
        if args.json:
            print(json.dumps(catalogue, indent=2, default=str))
        else:
            print_catalogue_md(catalogue)

    # Save
    if args.save:
        out_path = PROJECT_ROOT / "data" / "db_catalogue.json"
        out_path.parent.mkdir(exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(catalogue, f, indent=2, default=str)
        print(f"\nSaved to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
