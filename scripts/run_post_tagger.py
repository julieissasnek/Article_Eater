#!/usr/bin/env python3
import argparse, json, datetime
from pathlib import Path
from modules.post_tagger.normalize import norm_text
from modules.post_tagger.crosswalk import load_crosswalk, map_synonym, map_factors
from modules.post_tagger.schemas import PostTaggerBatch, PostTaggerItem

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", required=True)
    ap.add_argument("--out", dest="outfile", required=True)
    ap.add_argument("--crosswalk", default="modules/post_tagger/data/cnfa_crosswalk.yaml")
    args = ap.parse_args()
    raw = json.loads(Path(args.infile).read_text(encoding="utf-8"))
    cw = load_crosswalk(args.crosswalk)
    items = []
    for entry in raw:
        tag = entry["tag"] if isinstance(entry, dict) else str(entry)
        nrm = norm_text(tag)
        canon = map_synonym(nrm, cw)
        factors = map_factors(canon, cw)
        items.append(PostTaggerItem(raw=tag, canonical=canon, factors=factors, evidence={"ops":["normalize","synonym-map"],"nrm":nrm}))
    batch = PostTaggerBatch(items=items, meta={"version":"v20.3","ts":datetime.datetime.utcnow().isoformat()+"Z"})
    Path(args.outfile).parent.mkdir(parents=True, exist_ok=True)
    Path(args.outfile).write_text(batch.to_json(), encoding="utf-8")
    print(f"Wrote {len(items)} → {args.outfile}")
if __name__ == "__main__":
    main()