import pytest
from src.cmr.template_scanner import scan_templates
from src.cmr.template_matching import build_template_index, match_claims_to_templates
from src.cmr.models import TemplateRecord, get_session
import tempfile
import os
import json

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)
scan_templates(db_path=path)
session = get_session(path)
templates = session.query(TemplateRecord).filter(TemplateRecord.dedup_status == "active").all()
template_index = build_template_index(templates)
print(f"Total active templates: {len(templates)}")
print(f"VIEW1 in index? {'VIEW1' in template_index}")
if "VIEW1" in template_index:
    print(f"VIEW1 keywords: {template_index['VIEW1'].get('keywords')}")

claim = {"iv": "nature_view", "dv": "stress_reduction", "effect_size": 0.5, "sample_n": 46}
extracted = [claim]
matches = match_claims_to_templates(extracted, template_index)

print(f"Matches object length = {len(matches)}")
if matches:
    print(f"Match dict: {matches[0]}")
    for m in matches[0].get("matches", []):
        if m.get("template_id") == "VIEW1":
            print("VIEW1 matched!")

os.unlink(path)
