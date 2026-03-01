import tempfile
import os
import json
from src.cmr.paper_eval import evaluate_paper
from src.cmr.template_scanner import scan_templates

fd, db_path = tempfile.mkstemp(suffix=".db")
os.close(fd)
try:
    scan_templates(db_path=db_path)
    paper = evaluate_paper(
        structured_claims=[
            {
                "iv": "nature_view",
                "dv": "restoration",
                "direction": "increase",
                "effect_size": 0.5,
            }
        ],
        db_path=db_path,
    )
    print(json.dumps(paper.get("template_system_updates", []), indent=2))
finally:
    os.unlink(db_path)
