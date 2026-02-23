import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.services.incremental_bn import IncrementalBNBuilder
BN_JSON = PROJECT_ROOT / "data" / "production" / "realtime_incremental_bn.json"

builder = IncrementalBNBuilder(persistence_path=BN_JSON)
print(f"Edges before: {len(builder.edges)} Nodes: {len(builder.nodes)}")

# Find the node with the highest degree
degrees = {}
for src, tgt in builder.edges.keys():
    degrees[src] = degrees.get(src, 0) + 1
    degrees[tgt] = degrees.get(tgt, 0) + 1

if not degrees:
    print("No nodes found.")
    sys.exit(0)

central_node = max(degrees, key=degrees.get)
print(f"Central node: {central_node} with degree {degrees[central_node]}")

for node in list(builder.nodes):
    if node != central_node:
        builder.get_or_create_edge(node, central_node)

print(f"Edges after: {len(builder.edges)}")
builder.save_state()

