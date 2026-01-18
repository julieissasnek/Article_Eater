#!/usr/bin/env python3
import sys, json
from pathlib import Path
from datetime import datetime

POLICY_JSON = {
  "preferred_providers": ["gemini", "openai", "anthropic"],
  "eager": {
    "metadata": True,
    "rule_candidacy": True,
    "seven_panel": True,
    "require_llm_for_panels": True,
    "non_admin_fallback_allowed": False
  }
}

def write(p: Path, text: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print("Wrote", p)

def main(dst_root: str):
    root = Path(dst_root)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write(root/"config"/"app.policy.json", json.dumps(POLICY_JSON, indent=2))
    policy_py = '''from __future__ import annotations
import json
from pathlib import Path
from functools import lru_cache

DEFAULT_POLICY = {
    "preferred_providers": ["gemini","openai","anthropic"],
    "eager": {
        "metadata": True,
        "rule_candidacy": True,
        "seven_panel": True,
        "require_llm_for_panels": True,
        "non_admin_fallback_allowed": False
    }
}

@lru_cache(maxsize=1)
def get_policy() -> dict:
    root = Path(__file__).resolve().parents[1]
    p = root / "config" / "app.policy.json"
    if not p.exists():
        return DEFAULT_POLICY
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        merged = DEFAULT_POLICY.copy()
        merged.update(data or {})
        if "eager" in data:
            e = merged["eager"].copy()
            e.update(data["eager"] or {})
            merged["eager"] = e
        return merged
    except Exception:
        return DEFAULT_POLICY
'''
    write(root/"app"/"policy.py", policy_py)
    write(root/"VERSION.txt", f"v19.1.5 ({ts})\n")
    write(root/"config"/"app.version.json", json.dumps({"version":"v19.1.5","timestamp":ts}, indent=2))
    print("Upgrade complete.")
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/upgrade_to_v19_1_5.py <repo_root>")
        sys.exit(1)
    main(sys.argv[1])