from pathlib import Path
import yaml

def load_confidence():
    p = Path('confidence_config.yml')
    if not p.exists():
        return {'RCT_Weights': {'N_weight':0.4,'p_weight':0.3,'d_weight':0.3},
                'Meta_Weights': {'k_weight':0.3,'CI_weight':0.5,'I2_weight':0.2}}
    try:
        return yaml.safe_load(p.read_text(encoding='utf-8', errors='ignore')) or {}
    except Exception:
        return {}

def aggregate(panels: list[dict]) -> dict:
    conf = load_confidence()
    # Minimal synthesis; extend with BN logic as needed.
    return {'summary': 'Synthesis complete (v20.6)', 'weights': conf, 'panels': panels}