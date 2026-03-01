import tempfile
import os
import json
from sqlalchemy.orm import Session
from src.cmr.models import get_session, TemplateRecord
from src.cmr.template_scanner import scan_templates
from src.cmr.template_matching import build_template_index, match_claims_to_templates

fd, db_path = tempfile.mkstemp(suffix=".db")
os.close(fd)
try:
    scan_templates(db_path=db_path)
    session = get_session(db_path)
    try:
        records = session.query(TemplateRecord).all()
        index = build_template_index(records)
        claim = {
            "iv": "nature_view_quality",
            "dv": "autonomic_regulation",
            "direction": "increase"
        }
        print("VIEW1 Index:", index.get("VIEW1", {}))
        matches = match_claims_to_templates([claim], index)
        print("\nMATCHES:")
        for match in matches[0].get("matches", []):
            if "VIEW1" in match["template_id"]:
                print("  ", match.get("template_id"), "-", match.get("rationale"), "Score:", match.get("confidence"))
    finally:
        session.close()
finally:
    os.unlink(db_path)
