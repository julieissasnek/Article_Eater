import json
from src.cmr.mechanism_tracing import trace_claim

claim_step3 = {
    "iv": "perceived_restorativeness",
    "dv": "perceived_restorativeness",
    "direction": "increase",
    "relationship": "increase",
    "description": "perceived_restorativeness increase perceived_restorativeness"
}

with open(f"/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/data/templates/VIEW1.json") as f:
    data = json.load(f)
    print(f"VIEW1 Step 3 result: {trace_claim(claim_step3, data)}")
