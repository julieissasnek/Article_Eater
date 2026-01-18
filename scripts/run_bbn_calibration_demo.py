#!/usr/bin/env python3
import json, sys
from src.agents.bbn_calibrator import calibrate
def main(p):
    items=json.loads(open(p,'r',encoding='utf-8').read())
    out=calibrate(items)
    print(json.dumps(out, indent=2))
if __name__=='__main__':
    if len(sys.argv)<2:
        print('Usage: run_bbn_calibration_demo.py <seven_panel.json>'); raise SystemExit(1)
    main(sys.argv[1])