
from __future__ import annotations
import sqlite3, os
DB = os.environ.get("AE_DB","ae.db")
def _conn(path=None):
    import sqlite3
    return sqlite3.connect(path or DB)

def analyze_conflicts(db_path: str|None=None):
    with _conn(db_path) as con:
        rows = con.execute("SELECT id, antecedent, consequent, measure_direction, ci_lower, ci_upper FROM findings_view").fetchall() if False else []
    # Placeholder selection above expects a view; using direct findings if not present
    with _conn(db_path) as con:
        rows = con.execute("SELECT id, article_id, finding_text, ci_lower, ci_upper FROM findings WHERE ci_lower IS NOT NULL AND ci_upper IS NOT NULL").fetchall()
        # naive: detect non-overlap within same textual key (prototype for full rule alignment)
        seen = {}
        for fid, aid, txt, lo, hi in rows:
            key = txt.strip().lower()
            seen.setdefault(key, []).append((fid, lo, hi))
        for key, arr in seen.items():
            for i in range(len(arr)):
                for j in range(i+1, len(arr)):
                    _i = arr[i]; _j = arr[j]
                    if _i[2] < _j[1] or _j[2] < _i[1]:
                        con.execute("INSERT INTO rule_interactions(rule_a_id, rule_b_id, interaction_type, notes) VALUES (?,?,?,?)",
                                    (str(_i[0]), str(_j[0]), 'statistical_conflict', key))