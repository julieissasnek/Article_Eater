import json
import os

TEMPLATES_DIR = "data/templates"

CEILINGS = {
    "CONSTITUTIVE": 0.75,
    "MECHANISM": 0.60,
    "EMPIRICAL_ASSOCIATION": 0.60,
    "FUNCTIONAL": 0.50,
    "CAPACITY": 0.45,
    "ANALOGICAL": 0.35,
    "THEORY_DERIVED": 0.40,
}

def is_calibrated(template):
    status = (template.get("calibration_status") or template.get("status") or "").lower()
    if status == "calibrated":
        return True
    if template.get("calibrated") is True:
        return True
    return False

def clamp_templates():
    total_fixed = 0
    
    for fname in os.listdir(TEMPLATES_DIR):
        if not fname.endswith(".json"):
            continue
            
        json_path = os.path.join(TEMPLATES_DIR, fname)
        with open(json_path, 'r') as f:
            try:
                data = json.load(f)
            except:
                continue
                
        if not is_calibrated(data):
            continue
            
        dirty = False
        
        # Check top-level confidence
        top_warrant = data.get("bridge_warrant", "").strip().upper()
        if top_warrant in CEILINGS:
            ceil = CEILINGS[top_warrant]
            if data.get("confidence", 0) > ceil:
                print(f"{fname}: clamping top-level confidence from {data['confidence']} to {ceil}")
                data["confidence"] = ceil
                dirty = True
                
        # Check mechanism_chain
        chain = data.get("mechanism_chain") or data.get("mechanism_steps") or []
        for i, step in enumerate(chain):
            step_warrant = (step.get("warrant") or step.get("bridge_warrant") or "").strip().upper()
            if step_warrant in CEILINGS:
                ceil = CEILINGS[step_warrant]
                if step.get("confidence", 0) > ceil:
                    print(f"{fname}: clamping mechanism_chain[{i}] confidence from {step['confidence']} to {ceil}")
                    step["confidence"] = ceil
                    dirty = True
                    
        if dirty:
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=4)
            total_fixed += 1
            
    print(f"Repaired files: {total_fixed}")

if __name__ == "__main__":
    clamp_templates()
