from typing import List, Dict
import yaml
def load_crosswalk(path:str)->Dict:
    try:
        with open(path,'r',encoding='utf-8') as f: return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {"synonyms":{}, "canon_to_factors":{}}
def map_synonym(nrm:str, cw:Dict)->str:
    return cw.get("synonyms",{}).get(nrm, nrm)
def map_factors(canon:str, cw:Dict)->List[str]:
    return list(cw.get("canon_to_factors",{}).get(canon, []))