import sqlite3
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.services.incremental_bn import IncrementalBNBuilder

WEB_DB = PROJECT_ROOT / "data" / "web_persistence.db"
BN_JSON = PROJECT_ROOT / "data" / "production" / "realtime_incremental_bn.json"

class DummyBelief:
    def __init__(self, e, o):
        self.environment_id = e
        self.outcome_id = o
        self.credence = 1.0
        self.paper_ids = []

builder = IncrementalBNBuilder(persistence_path=BN_JSON)

conn = sqlite3.connect(WEB_DB)
cur = conn.cursor()
cur.execute("SELECT environment_id, outcome_id FROM beliefs WHERE environment_id IS NOT NULL AND outcome_id IS NOT NULL")
rows = cur.fetchall()
print(f"Found {len(rows)} beliefs to inject")

for e, o in rows:
    b = DummyBelief(e, o)
    builder.observe_belief(b)
    
builder.save_state()
print("Done saving new BN state.")

