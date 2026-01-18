
import os, sqlite3, tempfile
from app.relational_analysis import analyze_conflicts

def test_conflict_insertion(tmp_path, monkeypatch):
    db = tmp_path/'ae.db'
    os.environ['AE_DB'] = str(db)
    con = sqlite3.connect(db)
    con.executescript('''
    CREATE TABLE findings(id INTEGER PRIMARY KEY, article_id INT, finding_text TEXT, ci_lower REAL, ci_upper REAL);
    CREATE TABLE rule_interactions(interaction_id INTEGER PRIMARY KEY AUTOINCREMENT, rule_a_id TEXT, rule_b_id TEXT, interaction_type TEXT, status TEXT DEFAULT 'pending_review', notes TEXT);
    ''')
    con.execute("INSERT INTO findings(article_id,finding_text,ci_lower,ci_upper) VALUES (1,'A->B',0.1,0.2),(2,'A->B',0.3,0.4)")
    con.commit(); con.close()
    analyze_conflicts(str(db))
    con = sqlite3.connect(db)
    n = con.execute("SELECT count(*) FROM rule_interactions WHERE interaction_type='statistical_conflict'").fetchone()[0]
    assert n == 1