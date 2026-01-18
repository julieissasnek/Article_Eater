#!/usr/bin/env python3
"""
Smoke test for Article Eater v20.2.1
- Creates a test job (topic query)
- Polls queue status
- Checks for at least one seven-panel row
"""
import argparse, time, sys, json
from pathlib import Path
import requests


def _default_base_from_contract() -> str:
    ports_path = Path(__file__).resolve().parents[1] / 'contracts' / 'ports.json'
    if not ports_path.exists():
        return 'http://127.0.0.1:8000'
    try:
        data = json.loads(ports_path.read_text(encoding='utf-8'))
        host = data.get('ports', {}).get('api', {}).get('host', 8000)
        return f'http://127.0.0.1:{int(host)}'
    except Exception:
        return 'http://127.0.0.1:8000'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=_default_base_from_contract())
    ap.add_argument("--topic", default="natural light AND stress")
    ap.add_argument("--timeout_s", type=int, default=240)
    args = ap.parse_args()

    s = requests.Session()

    # 1) Create a job
    payload = {
        "job_type": "l0_harvest",
        "params": {"query": args.topic},
        # Back-compat fields for older APIs.
        "type": "l0_harvest",
        "query": args.topic,
    }
    r = s.post(f"{args.base}/jobs/", json=payload)
    if r.status_code >= 300:
        print("FAIL create job", r.status_code, r.text); sys.exit(2)
    job = r.json(); job_id = job.get("id") or job.get("job_id")
    print("Created job:", job_id)

    # 2) Poll status
    t0 = time.time()
    while time.time()-t0 < args.timeout_s:
        rq = s.get(f"{args.base}/jobs/{job_id}")
        if rq.status_code >= 300:
            time.sleep(2); continue
        st = rq.json().get("status","")
        print("Status:", st)
        if st.lower() in {"done","complete","completed"}:
            break
        time.sleep(3)
    else:
        print("FAIL timeout waiting for job completion"); sys.exit(3)

    # 3) Check library for seven-panel presence
    rl = s.get(f"{args.base}/library/")
    if rl.status_code >= 300:
        print("FAIL library fetch", rl.status_code, rl.text); sys.exit(4)
    lib = rl.json()
    any_panel = False
    for art in lib if isinstance(lib,list) else lib.get("items",[]):
        panels = art.get("seven_panel") or art.get("sevenPanel") or []
        if panels:
            any_panel = True; break

    print("PASS smoke test" if any_panel else "FAIL no seven-panel found")
    sys.exit(0 if any_panel else 5)

if __name__ == "__main__":
    main()
