
import csv
import sqlite3
import json
import logging
from datetime import datetime, timezone
from src.services.db_locator import get_web_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = get_web_db()  # Centralized: was hardcoded
CSV_PATH = "data/review/tranche80_confirmed_rows.csv"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def load_staging_links():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get Master Web ID
    row = cursor.execute("SELECT web_id FROM web_metadata WHERE is_master = 1").fetchone()
    if not row:
        row = cursor.execute("SELECT web_id FROM web_metadata LIMIT 1").fetchone() # Fallback
    
    if not row:
        logger.error("No web found in web_metadata.")
        return
        
    web_id = row['web_id']
    logger.info(f"Using Web ID: {web_id}")

    # Read CSV
    beliefs_count = 0
    constraints_count = 0
    
    with open(CSV_PATH, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            claim_type = row.get('claim_type')
            
            # 1. Handle Beliefs (Findings)
            if claim_type == 'finding':
                # Map CSV columns to beliefs table
                belief_id = row.get('node_id') # e.g. node:doi...
                content = row.get('statement')
                level = 'empirical' # Mapping EMPIRICAL_FINDING -> empirical
                
                # Check if exists
                existing = cursor.execute("SELECT belief_id FROM beliefs WHERE belief_id = ?", (belief_id,)).fetchone()
                if not existing:
                    try:
                        # Serialize scope conditions if available (Sprint 6: Scope Persistence)
                        scope_json = None
                        if isinstance(row, dict):
                            try:
                                from src.services.extraction_to_web import _extract_scope
                                scope_obj = _extract_scope({"study": row.get("study", {})})
                                scope_json = json.dumps(scope_obj.to_dict())
                            except Exception:
                                pass  # Graceful degradation if scope extraction fails

                        cursor.execute("""
                            INSERT INTO beliefs (
                                belief_id, web_id, content, level, status,
                                credence_value, scope, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            belief_id, web_id, content, level, 'active',
                            float(row.get('ae_confidence', 0.5)),
                            scope_json,
                            datetime.now(timezone.utc).isoformat(),
                            datetime.now(timezone.utc).isoformat()
                        ))
                        beliefs_count += 1
                    except sqlite3.IntegrityError as e:
                        logger.warning(f"Failed to insert belief {belief_id}: {e}")

            # 2. Handle Constraints (Theory Links)
            elif claim_type == 'theory_link':
                constraint_id = row.get('claim_id')
                source_id = row.get('source_node_id') # finding
                # target_id from theory_name or target_node_id?
                # CSV Row 9: target_node_id="theory:art". Perfect.
                target_id = row.get('target_node_id').lower()
                
                # Verify source exists (Finding might be missing if processed out of order? No, usually sorted by paper)
                # But CSV order: Finding (row 2-8), then Links (row 9+). So Findings come first. Good.
                
                # Confirm target exists (Theory node) - we checked this manually.
                
                # Map edge type
                constraint_type = 'tier2_theory_link' # As per task spec
                
                # Map direction? 
                # Schema: bidirectional default 0.
                
                # Check if source exists
                existing_source = cursor.execute("SELECT belief_id FROM beliefs WHERE belief_id = ?", (source_id,)).fetchone()
                if not existing_source:
                    # Create placeholder source belief
                    try:
                        # Serialize scope conditions if available (Sprint 6: Scope Persistence)
                        scope_json = None
                        if isinstance(row, dict):
                            try:
                                from src.services.extraction_to_web import _extract_scope
                                scope_obj = _extract_scope({"study": row.get("study", {})})
                                scope_json = json.dumps(scope_obj.to_dict())
                            except Exception:
                                pass  # Graceful degradation if scope extraction fails

                        cursor.execute("""
                            INSERT INTO beliefs (
                                belief_id, web_id, content, level, status,
                                credence_value, scope, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            source_id, web_id, row.get('statement', 'Unknown content'), 'evidence', 'active',
                            float(row.get('ae_confidence', 0.5)),
                            scope_json,
                            datetime.now(timezone.utc).isoformat(),
                            datetime.now(timezone.utc).isoformat()
                        ))
                        beliefs_count += 1
                        logger.info(f"Created missing source belief: {source_id}")
                    except sqlite3.IntegrityError as e:
                        logger.warning(f"Failed to insert source belief {source_id}: {e}")

                existing = cursor.execute("SELECT constraint_id FROM constraints WHERE constraint_id = ?", (constraint_id,)).fetchone()
                if not existing:
                    try:
                        cursor.execute("""
                            INSERT INTO constraints (
                                constraint_id, web_id, source_id, target_id,
                                constraint_type, strength, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            constraint_id, web_id, source_id, target_id,
                            constraint_type, float(row.get('weight', 0.5)),
                            datetime.now(timezone.utc).isoformat()
                        ))
                        constraints_count += 1
                    except sqlite3.IntegrityError as e:
                        logger.warning(f"Failed to insert constraint {constraint_id}: {e}")

    conn.commit()
    conn.close()
    logger.info(f"Loaded {beliefs_count} beliefs and {constraints_count} constraints.")

if __name__ == "__main__":
    load_staging_links()
