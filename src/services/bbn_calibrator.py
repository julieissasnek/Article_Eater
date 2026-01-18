
"""Service-level BBN-style confidence helper.

This is intentionally lightweight and file-backed. It does *not*
change the main BN JSON; instead it emits a secondary artifact per finding.

The main Agent-facing calibrator in src/agents/bbn_calibrator.py
remains the authoritative place for aggregate calibration. This module
simply offers a convenient, low-coupling helper for confidence-by-finding.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import json

CONF_PATH = Path("confidence_config.yml")
OUT_DIR = Path("data") / "calibration"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def _read_yaml(p: Path) -> Dict[str, Any]:
    if not p.exists():
        # Same defaults as elsewhere in the repo
        return {"RCT_Weights": {"N_weight": 0.4, "p_weight": 0.3, "d_weight": 0.3}}
    try:
        import yaml  # type: ignore
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {"RCT_Weights": {"N_weight": 0.4, "p_weight": 0.3, "d_weight": 0.3}}

def _calc_confidence(score_N: float, score_p: float, score_d: float) -> float:
    conf = _read_yaml(CONF_PATH).get("RCT_Weights", {})
    wN = float(conf.get("N_weight", 0.4))
    wp = float(conf.get("p_weight", 0.3))
    wd = float(conf.get("d_weight", 0.3))
    val = (wN * score_N) + (wp * score_p) + (wd * score_d)
    return max(0.0, min(1.0, val))

def compute_confidence_for_finding(finding_id: str, stats: Dict[str, Any]) -> float:
    """Compute a simple confidence score and persist a JSON artifact.

    Parameters
    ----------
    finding_id:
        Identifier returned by the graph store for this finding.
    stats:
        Mapping with (at least) p_value, effect_size, sample_size.
    """
    try:
        N = float(stats.get("sample_size") or 0.0)
    except Exception:
        N = 0.0
    try:
        p = float(stats.get("p_value") or 1.0)
    except Exception:
        p = 1.0
    try:
        d = float(stats.get("effect_size") or 0.0)
    except Exception:
        d = 0.0

    # Normalised components
    score_N = min(N / 100.0, 1.0)
    score_p = 1.0 - min(max(p, 0.0), 1.0)
    score_d = min(abs(d) / 1.0, 1.0)

    conf = _calc_confidence(score_N, score_p, score_d)
    out = {
        "finding_id": finding_id,
        "confidence": conf,
        "components": {"N": score_N, "p": score_p, "d": score_d},
    }
    out_path = OUT_DIR / f"{finding_id}.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return conf
