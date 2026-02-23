#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.extract_article_essence import _parse_findings_output


def _assert(condition: bool, message: str) -> None:
    if not condition:
        print(f"[extract_7panel_parsing] FAIL: {message}")
        raise SystemExit(1)


def main() -> None:
    dict_payload = json.dumps({"findings": [{"finding_text": "A"}]})
    list_payload = json.dumps([{"finding_text": "B"}])
    bad_payload = "not json"

    out1 = _parse_findings_output(dict_payload)
    _assert(isinstance(out1, list) and len(out1) == 1, "dict payload not parsed")

    out2 = _parse_findings_output(list_payload)
    _assert(isinstance(out2, list) and len(out2) == 1, "list payload not parsed")

    out3 = _parse_findings_output(bad_payload)
    _assert(out3 == [], "bad payload should return []")

    print("[extract_7panel_parsing] OK")


if __name__ == "__main__":
    sys.exit(main())
