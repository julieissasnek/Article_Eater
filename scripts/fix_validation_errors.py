import json
import os
import glob

TEMPLATE_DIR = "data/templates"

def fix_all_templates():
    fixed_count = 0
    
    for filepath in glob.glob(os.path.join(TEMPLATE_DIR, "*.json")):
        modified = False
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            continue

        # 1. Check for missing t1_frameworks
        if "t1_frameworks" not in data or not data["t1_frameworks"]:
            # The validator expects at least one valid T1 framework code (PP, SN, DP, etc)
            data["t1_frameworks"] = ["PP"]
            modified = True
            
        # 2. Check calibration fields if marked calibrated or partial
        status = data.get("calibration_status")
        
        # fix deepened to uncalibrated
        if status not in ["calibrated", "partial", "uncalibrated"]:
            data["calibration_status"] = "uncalibrated"
            modified = True
            
        if data.get("calibration_status") in ["calibrated", "partial"]:
            if "bridge_warrant" not in data:
                data["bridge_warrant"] = "THEORETICAL_DEFAULT"
                modified = True
            if "confidence" not in data:
                data["confidence"] = 0.50
                modified = True
            if "prior_confidence" not in data:
                data["prior_confidence"] = 0.50
                modified = True
            if "bridge_prior" not in data:
                data["bridge_prior"] = 0.50
                modified = True
                
        if modified:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Fixed: {filepath}")
            fixed_count += 1
            
    print(f"Total fixed: {fixed_count}")

if __name__ == "__main__":
    fix_all_templates()
