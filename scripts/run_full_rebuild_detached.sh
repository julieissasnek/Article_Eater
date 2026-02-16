#!/usr/bin/env bash
set -euo pipefail

REPO="/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1"
AF_DB="/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/article_finder.db"
cd "$REPO"

remaining_abstracts() {
python3 - <<'PY'
import sqlite3, json
from pathlib import Path
state_path=Path('data/production/realtime_intake_state.json')
state={'last_event_ts':'','last_paper_id':''}
if state_path.exists():
    state=json.loads(state_path.read_text())
conn=sqlite3.connect('/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/article_finder.db')
cur=conn.cursor()
cur.execute('''
SELECT COUNT(*) FROM papers
WHERE abstract IS NOT NULL AND LENGTH(abstract)>=200
  AND (off_topic_flag IS NULL OR off_topic_flag=0)
  AND (
    COALESCE(created_at, retrieved_at, updated_at, '') > ?
    OR (
      COALESCE(created_at, retrieved_at, updated_at, '') = ?
      AND paper_id > ?
    )
  )
''',(state.get('last_event_ts',''),state.get('last_event_ts',''),state.get('last_paper_id','')))
print(cur.fetchone()[0])
conn.close()
PY
}

pending_pdfs() {
python3 - <<'PY'
import csv
from pathlib import Path
p=Path('data/production/realtime_pdf_completion_queue.csv')
if not p.exists():
    print(0)
else:
    rows=list(csv.DictReader(p.open()))
    pending=sum(1 for r in rows if not (r.get('status','').startswith('completed_') or r.get('status')=='missing_pdf'))
    print(pending)
PY
}

summary() {
python3 - <<'PY'
import json, sqlite3
from pathlib import Path
base=Path('data/production')

def linecount(path):
    return sum(1 for _ in path.open()) if path.exists() else 0

print('tables_rows', linecount(base/'realtime_tables.jsonl'))
print('rules_rows', linecount(base/'realtime_rules.jsonl'))

bn=base/'realtime_incremental_bn.json'
if bn.exists():
    d=json.loads(bn.read_text())
    print('bn_nodes', len(d.get('nodes',[])))
    print('bn_edges', len(d.get('edges',{})))

try:
    conn=sqlite3.connect('file:data/web_persistence.db?mode=ro', uri=True)
    cur=conn.cursor()
    cur.execute('SELECT COUNT(*) FROM beliefs')
    print('web_beliefs', cur.fetchone()[0])
    cur.execute('SELECT COUNT(*) FROM constraints')
    print('web_constraints', cur.fetchone()[0])
    conn.close()
except Exception:
    print('web_beliefs', 'NA')
    print('web_constraints', 'NA')
PY
}

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] full_rebuild_start"

abstract_cycle=0
while true; do
  rem=$(remaining_abstracts)
  if [ "$rem" -le 0 ]; then
    break
  fi
  abstract_cycle=$((abstract_cycle+1))
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] abstract_cycle=${abstract_cycle} remaining=${rem}"
  python3 scripts/run_realtime_table_rule_intake.py --limit 5000
  summary

done

pdf_cycle=0
while true; do
  pending=$(pending_pdfs)
  if [ "$pending" -le 0 ]; then
    break
  fi
  pdf_cycle=$((pdf_cycle+1))
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] pdf_cycle=${pdf_cycle} pending=${pending}"
  python3 scripts/process_realtime_pdf_completion_queue.py \
    --batch-size 200 \
    --max-workers 6 \
    --integrate-web \
    --update-bn \
    --bn-state-path data/production/realtime_incremental_bn.json
  summary

done

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] full_rebuild_complete"
summary
