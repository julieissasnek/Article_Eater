
from __future__ import annotations
import math, re, collections

def _tokenize(s:str):
    return re.findall(r"[a-z0-9]+", s.lower())

def embed_text(text: str, dim: int=256) -> list[float]:
    # Simple hashing vectorizer to avoid heavy deps; deterministic and fast.
    vec = [0.0]*dim
    for tok in _tokenize(text):
        h = hash(tok) % dim
        vec[h] += 1.0
    # L2 normalize
    norm = math.sqrt(sum(v*v for v in vec)) or 1.0
    return [v/norm for v in vec]

def cosine(a, b):
    return sum(x*y for x,y in zip(a,b))