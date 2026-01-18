import json, pathlib, statistics
from typing import List, Dict, Any

CONF = pathlib.Path('confidence_config.yml')
OUT = pathlib.Path('calibration/bbn_calibration.json')
OUT.parent.mkdir(parents=True, exist_ok=True)

def _load_conf():
    if CONF.exists():
        import yaml
        return yaml.safe_load(CONF.read_text(encoding='utf-8')) or {}
    return {'RCT_Weights': {'N_weight':0.4,'p_weight':0.3,'d_weight':0.3},
            'Meta_Weights': {'k_weight':0.3,'CI_weight':0.5,'I2_weight':0.2}}

def calibrate(items: List[Dict[str,Any]]) -> Dict[str,Any]:
    w = _load_conf()
    Nw = w.get('RCT_Weights',{}).get('N_weight',0.4)
    pw = w.get('RCT_Weights',{}).get('p_weight',0.3)
    dw = w.get('RCT_Weights',{}).get('d_weight',0.3)
    per = []
    for i in items:
        st = i.get('statistics',{}) or {}
        N = st.get('sample_size') or 0
        p = st.get('p_value') if isinstance(st.get('p_value'), (int,float)) else None
        d = st.get('effect_size') if isinstance(st.get('effect_size'), (int,float)) else None
        p_score = 1.0 - min(max((p if p is not None else 1.0), 0.0), 1.0)
        d_score = min(abs(d or 0.0), 2.0)/2.0
        N_score = min((N or 0)/200.0, 1.0)
        weight = (Nw*N_score + pw*p_score + dw*d_score)
        per.append({
            "finding_text": i.get("finding_text",""),
            "weight_components": {"N":N_score,"p":p_score,"d":d_score},
            "weight": weight,
            "ci": {"lower": st.get("ci_lower"), "upper": st.get("ci_upper")},
            "effect_size_type": st.get("effect_size_type")
        })
    overall = statistics.mean([x["weight"] for x in per]) if per else 0.0
    out = {"version":"v20.6.2","overall_weight": overall, "findings": per}
    OUT.write_text(json.dumps(out, indent=2), encoding='utf-8')
    return out