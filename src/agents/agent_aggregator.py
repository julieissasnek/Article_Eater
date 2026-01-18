from pathlib import Path
import yaml
from typing import List, Dict, Any

def load_confidence() -> dict:
    p = Path('confidence_config.yml')
    if not p.exists():
        return {'RCT_Weights': {'N_weight':0.4,'p_weight':0.3,'d_weight':0.3},
                'Meta_Weights': {'k_weight':0.3,'CI_weight':0.5,'I2_weight':0.2}}
    return yaml.safe_load(p.read_text(encoding='utf-8', errors='ignore')) or {}

def aggregate(panels: List[Dict[str,Any]]) -> Dict[str,Any]:
    conf = load_confidence()
    return {'summary': 'Synthesis complete (v20.6.2)', 'weights': conf, 'panels': panels}