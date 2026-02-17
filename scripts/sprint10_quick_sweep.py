
import sys
import os
import sqlite3
import subprocess
from sqlalchemy import create_engine, text

def check_template_db():
    print("\n=== 3.1a Template DB Validation ===")
    if not os.path.exists("ae.db"):
        print("FAIL: ae.db not found")
        return

    try:
        engine = create_engine("sqlite:///ae.db")
        with engine.connect() as conn:
            # Check table existence
            tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='templates'")).fetchall()
            if not tables:
                print("FAIL: 'templates' table not found in ae.db")
                return

            # Total Count
            count = conn.execute(text("SELECT count(*) FROM templates")).scalar()
            print(f"Total TemplateRecords: {count} (Target: 150)")

            # Dedup Status
            print("Dedup Status Breakdown:")
            rows = conn.execute(text("SELECT dedup_status, count(*) FROM templates GROUP BY dedup_status")).fetchall()
            for status, c in rows:
                print(f"  - {status}: {c}")
            
    except Exception as e:
        print(f"ERROR: {e}")

def check_staging_links():
    print("\n=== 3.1b Staging Links Validation ===")
    db_path = "data/web_persistence.db"
    
    # Check constraints table
    if not os.path.exists(db_path) and os.path.exists("web_persistence.db"):
        db_path = "web_persistence.db"
        
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='constraints'")
        if not cur.fetchone():
             print("FAIL: 'constraints' table not found")
             return

        try:
            count = cur.execute("SELECT count(*) FROM constraints WHERE constraint_type = 'tier2_theory_link'").fetchone()[0]
            print(f"Tier 2 Links (tier2_theory_link): {count} (Target: 994)")
        except sqlite3.OperationalError:
            print("FAIL: query error")
    except Exception:
        print("FAIL: DB error")

def check_wis_module():
    print("\n=== 3.1c WIS Module Spot-Check ===")
    try:
        sys.path.append(os.getcwd())
        from src.cmr import wis
        print(f"d=0.5 -> WIS: {wis.cohens_d_to_wis(0.5):.1f}")
    except ImportError:
        print("FAIL: src.cmr.wis not found")
    except Exception as e:
        print(f"ERROR: {e}")

def check_interaction_matrix():
    print("\n=== 3.1d Interaction Matrix Spot-Check ===")
    try:
        from src.cmr import interactions
        print("Checking interactions module import... OK")
    except ImportError:
        print("FAIL: src.cmr.interactions not found")

def check_building_eval():
    print("\n=== 3.1e Building Eval End-to-End ===")
    try:
        from src.cmr import building_eval
        print("Checking building_eval module import... OK")
    except ImportError:
        print("FAIL: src.cmr.building_eval not found")

if __name__ == "__main__":
    print("Starting Sprint 10 Quick Sweep (3.1a-e)...")
    check_template_db()
    check_staging_links()
    check_wis_module()
    check_interaction_matrix()
    check_building_eval()
    print("\nQuick Sweep Complete.")
