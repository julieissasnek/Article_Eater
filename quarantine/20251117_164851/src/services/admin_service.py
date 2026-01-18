from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import yaml

router = APIRouter()
PROMPTS_DIR = Path('prompts')
CONF_PATH = Path('confidence_config.yml')

def admin_auth():
    # TODO: wire to real RBAC
    return True

@router.get('/prompts', response_class=JSONResponse)
def get_prompts(ok: bool = Depends(admin_auth)):
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for p in PROMPTS_DIR.glob('*'):
        if p.is_file():
            try: c = p.read_text(encoding='utf-8', errors='ignore')
            except Exception: c = ''
            items.append({'name': p.name, 'content': c})
    return {'prompts': items}

@router.post('/prompts/update')
def update_prompt(payload: dict, ok: bool = Depends(admin_auth)):
    name = payload.get('prompt_name')
    content = payload.get('content','')
    if not name or any(x in name for x in ['/', '\\\\']):
        raise HTTPException(status_code=400, detail='Invalid name')
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    (PROMPTS_DIR/name).write_text(content, encoding='utf-8')
    return {'status':'ok','saved':name}

@router.get('/confidence', response_class=JSONResponse)
def get_confidence(ok: bool = Depends(admin_auth)):
    if not CONF_PATH.exists():
        default = {'RCT_Weights': {'N_weight':0.4,'p_weight':0.3,'d_weight':0.3},
                   'Meta_Weights': {'k_weight':0.3,'CI_weight':0.5,'I2_weight':0.2}}
        return {'config': default}
    try:
        data = yaml.safe_load(CONF_PATH.read_text(encoding='utf-8', errors='ignore')) or {}
    except Exception:
        data = {}
    return {'config': data}

@router.post('/confidence/update')
def update_confidence(payload: dict, ok: bool = Depends(admin_auth)):
    with open(CONF_PATH, 'w') as f:
        yaml.safe_dump(payload, f, sort_keys=False)
    return {'status':'ok'}