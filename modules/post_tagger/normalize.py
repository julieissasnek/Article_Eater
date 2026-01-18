import unicodedata, re
def ascii_fold(s): return unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("ascii")
def lemma_lite(s):
    s = re.sub(r'\bmaterials\b','material',s); s = re.sub(r'\blights\b','light',s); s = re.sub(r'\btextures\b','texture',s)
    s = re.sub(r'\bpatterns\b','pattern',s); return s
def norm_text(s:str)->str:
    s = ascii_fold(s.strip()).lower()
    s = re.sub(r'[_\-]+',' ', s); s = re.sub(r'\s+',' ', s); s = re.sub(r'[^a-z0-9\s]','', s)
    return lemma_lite(s).strip()