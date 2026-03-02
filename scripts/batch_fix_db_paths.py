#!/usr/bin/env python3
"""
batch_fix_db_paths.py — Patch all scripts to use get_web_db from db_locator.
=============================================================================

For each Python file that hardcodes a web_persistence*.db path without
importing db_locator, this script adds:
  1. An import of get_web_db (or get_web_db_str)
  2. Replaces the hardcoded DEFAULT constant with a call to get_web_db()

This must be reviewed by a human since the patterns vary. Run with --dry-run first.

Usage:
    python3 scripts/batch_fix_db_paths.py --dry-run   # preview changes
    python3 scripts/batch_fix_db_paths.py              # apply changes
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Target patterns: DEFAULT_DB = ..., DB_PATH = ..., db_path = "data/...", etc.
# These are the common patterns from the audit.
CONSTANT_PATTERNS = [
    # Matches: DEFAULT_DB = PROJECT_ROOT / "data" / "web_persistence*.db"
    (
        r'^(\s*)(DEFAULT_DB(?:_PATH)?|DB_PATH|WEB_DB|DEFAULT_WEB_DB)\s*=\s*(?:PROJECT_ROOT\s*/\s*"data"\s*/\s*"web_persistence(?:_v2)?\.db"|Path\(\s*"data/web_persistence(?:_v2)?\.db"\s*\)|"data/web_persistence(?:_v2)?\.db")',
        r'\1\2 = get_web_db()  # Centralized: was hardcoded',
        'from src.services.db_locator import get_web_db',
    ),
    # Matches: db_path = str(get_web_db()) (lowercase, inside functions)
    (
        r'^(\s*)(db_path)\s*=\s*"data/web_persistence(?:_v2)?\.db"',
        r'\1\2 = str(get_web_db())  # Centralized: was hardcoded',
        'from src.services.db_locator import get_web_db',
    ),
]

# Files to skip (already fixed, or special-purpose)
SKIP_FILES = {
    'src/services/db_locator.py',   # The resolver itself
    'scripts/rebuild_web_db.py',    # Intentionally targets specific DBs
    'scripts/diagnose_db_corruption.py',  # Diagnostic tool
}

# Files in tests/ directory — skip
SKIP_PREFIXES = ['tests/', 'test_']


def should_skip(rel_path: str) -> bool:
    if rel_path in SKIP_FILES:
        return True
    return any(rel_path.startswith(p) or rel_path.split('/')[-1].startswith(p) 
               for p in SKIP_PREFIXES)


def has_resolver_import(content: str) -> bool:
    return 'db_locator' in content or 'resolve_web_db' in content or 'get_web_db' in content


def fix_file(filepath: Path, dry_run: bool = True) -> dict:
    """Attempt to fix a single file. Returns change info."""
    content = filepath.read_text(encoding='utf-8')
    rel = str(filepath.relative_to(PROJECT_ROOT))
    
    if should_skip(rel):
        return {"file": rel, "status": "skipped", "reason": "skip list"}
    
    if has_resolver_import(content):
        return {"file": rel, "status": "already_has_resolver"}
    
    lines = content.split('\n')
    modified = False
    import_added = False
    changes = []
    
    for i, line in enumerate(lines):
        for pattern, replacement, import_line in CONSTANT_PATTERNS:
            if re.match(pattern, line):
                old_line = line
                new_line = re.sub(pattern, replacement, line)
                if new_line != old_line:
                    lines[i] = new_line
                    changes.append({"line": i + 1, "old": old_line.strip(), "new": new_line.strip()})
                    modified = True
                    
                    # Add import if not already added
                    if not import_added:
                        # Find the right place to insert import
                        # After the last existing import or sys.path.insert
                        insert_idx = 0
                        for j, l in enumerate(lines):
                            if l.startswith('import ') or l.startswith('from ') or 'sys.path.insert' in l:
                                insert_idx = j + 1
                        
                        # Skip blank lines after imports
                        while insert_idx < len(lines) and lines[insert_idx].strip() == '':
                            insert_idx += 1
                        insert_idx -= 1  # Insert before the blank line
                        
                        lines.insert(insert_idx, import_line)
                        import_added = True
                        # Adjust subsequent line indices
                        if i >= insert_idx:
                            i += 1
                break
    
    if modified:
        if not dry_run:
            filepath.write_text('\n'.join(lines), encoding='utf-8')
        return {"file": rel, "status": "fixed" if not dry_run else "would_fix", "changes": changes}
    
    return {"file": rel, "status": "no_match", "reason": "pattern didn't match"}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch fix hardcoded DB paths")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    # Find all Python files with hardcoded paths
    target_files = []
    for py_file in sorted(PROJECT_ROOT.rglob("*.py")):
        rel = str(py_file.relative_to(PROJECT_ROOT))
        if any(part in {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', '_archive', '_review_package_2026_01_23'} 
               for part in py_file.relative_to(PROJECT_ROOT).parts):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8', errors='replace')
        except (PermissionError, OSError):
            continue
        if re.search(r'web_persistence.*\.db', content):
            if not has_resolver_import(content):
                target_files.append(py_file)
    
    print(f"Found {len(target_files)} files without resolver import")
    
    results = {"fixed": 0, "skipped": 0, "no_match": 0}
    
    for f in target_files:
        result = fix_file(f, dry_run=args.dry_run)
        status = result["status"]
        
        if status in ("fixed", "would_fix"):
            results["fixed"] += 1
            action = "WOULD FIX" if args.dry_run else "FIXED"
            print(f"  {action}: {result['file']}")
            for c in result.get("changes", []):
                print(f"    L{c['line']}: {c['old']}")
                print(f"      → {c['new']}")
        elif status == "skipped":
            results["skipped"] += 1
            print(f"  SKIP: {result['file']} ({result.get('reason', '')})")
        elif status == "no_match":
            results["no_match"] += 1
            print(f"  NO_MATCH: {result['file']} (manual fix needed)")
    
    print(f"\nSummary: {results['fixed']} {'would fix' if args.dry_run else 'fixed'}, "
          f"{results['skipped']} skipped, {results['no_match']} need manual fix")
    
    if args.dry_run:
        print("\nRun without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
