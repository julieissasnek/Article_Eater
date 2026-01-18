#!/usr/bin/env python3
"""Upgrade an existing Article Eater repo to v19.1.4 (Gemini-first, LLM-required).
Usage: python scripts/upgrade_to_v19_1_4.py <repo_root>
Additive, no deletions.
"""
import sys
from pathlib import Path

POLICY_JSON = """{
  "preferred_providers": [
    "gemini",
    "openai",
    "anthropic"
  ],
  "eager": {
    "metadata": true,
    "rule_candidacy": true,
    "seven_panel": true,
    "require_llm_for_panels": true,
    "non_admin_fallback_allowed": false
  }
}"""
POLICY_PY = """from __future__ import annotations
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
"""

def main(dst_root: str):
    root = Path(dst_root)
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "app").mkdir(parents=True, exist_ok=True)
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "config" / "app.policy.json").write_text(POLICY_JSON, encoding="utf-8")
    (root / "app" / "policy.py").write_text(POLICY_PY, encoding="utf-8")
    # Gentle imports in llm_extract.py and policy enforcement in pipeline.py if present
    def gentle_patch_llm(p: Path):
        if not p.exists(): return
        s = p.read_text(encoding="utf-8", errors="ignore")
        if "from .policy import get_policy" not in s:
            s = s.replace("from .security.keys import get_key", "from .security.keys import get_key\nfrom .policy import get_policy")
        p.write_text(s, encoding="utf-8")
    def gentle_patch_pipeline(p: Path):
        if not p.exists(): return
        s = p.read_text(encoding="utf-8", errors="ignore")
        if "from .policy import get_policy" not in s:
            s = s.replace("from .db import connect", "from .db import connect\nfrom .policy import get_policy")
        p.write_text(s, encoding="utf-8")
    gentle_patch_llm(root / "app" / "llm_extract.py")
    gentle_patch_pipeline(root / "app" / "pipeline.py")
    print("Upgrade files written.")
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/upgrade_to_v19_1_4.py <repo_root>"); sys.exit(1)
    main(sys.argv[1])