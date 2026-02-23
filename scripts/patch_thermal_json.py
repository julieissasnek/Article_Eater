import json

files = [
    "data/templates/THERMAL_ADAPTIVE_PE_001.json",
    "data/templates/THERMAL_COMFORT_ADAPTIVE_PE_001.json"
]

for filepath in files:
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    if "title" in data and "name" not in data:
        data["name"] = data.pop("title")
        
    if "display_id" not in data:
        data["display_id"] = data["template_id"]
        
    if "status" not in data:
        data["status"] = "calibrated"
        
    if "calibration_panel" not in data:
        data["calibration_panel"] = "THERMAL-I"
        
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
        print(f"Patched {filepath}")
