
import json
from src.extraction.claim_extractor import extract_claims_from_table, load_vocabulary

# Mock table based on typical "IV affects DV" structure
mock_table = {
    "paper_id": "test_paper",
    "table_id": "TBL-TEST",
    "page": 1,
    "rows": [
        {"text": "Ceiling height increased perceived creativity (p < 0.05)."},
        {"text": "Noise levels reduced cognitive performance, F(1, 20) = 4.5."},
        {"text": "We found a positive correlation between lighting quality and mood (r = 0.6)."}
    ],
    "type": "RESULTS_DESCRIPTIVE"
}

print("Loading vocabulary...")
vocab = load_vocabulary()

print("Testing extraction...")
claims = extract_claims_from_table(mock_table, vocabulary=vocab, method="rule_based")

print(f"Found {len(claims)} claims:")
for c in claims:
    print(json.dumps(c, indent=2))
