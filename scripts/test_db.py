import sys
from pathlib import Path
# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.services.web_persistence import WebDatabase
from src.services.db_locator import resolve_web_db

def main():
    try:
        db_path = resolve_web_db(None, prefer="integrated")
        if not db_path.exists():
            print(f"DB not found at {db_path}")
            return
        
        db = WebDatabase(str(db_path))
        master_id = db.get_master_web_id()
        print(f"Master Web ID: {master_id}")
        
        web, _ = db.load_web(master_id)
        if not web:
            print("Failed to load web")
            return
            
        print(f"Loaded web with {len(web.beliefs)} beliefs")
        
        envs = set()
        outs = set()
        for b in web.beliefs.values():
            if getattr(b, 'environment_id', None):
                envs.add(b.environment_id)
            if getattr(b, 'outcome_id', None):
                outs.add(b.outcome_id)
                
        print("\nSample Environments:")
        for e in list(envs)[:20]: print(f" - {e}")
        
        print("\nSample Outcomes:")
        for o in list(outs)[:20]: print(f" - {o}")

    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
