from dataclasses import dataclass
from typing import List, Dict, Any
import json

@dataclass
class PostTaggerItem:
    raw: str
    canonical: str
    factors: List[str]
    evidence: Dict[str, Any]

@dataclass
class PostTaggerBatch:
    items: List[PostTaggerItem]
    meta: Dict[str, Any]
    def to_json(self) -> str:
        return json.dumps({
            "items":[{
                "raw":it.raw,"canonical":it.canonical,"factors":it.factors,"evidence":it.evidence
            } for it in self.items],
            "meta": self.meta
        }, ensure_ascii=False, indent=2)