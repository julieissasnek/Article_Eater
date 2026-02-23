import json
from pathlib import Path
import sys
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.services.incremental_bn import IncrementalBNBuilder
BN_JSON = PROJECT_ROOT / "data" / "production" / "realtime_incremental_bn.json"

builder = IncrementalBNBuilder(persistence_path=BN_JSON)

edges = list(builder.edges.items())
adj = defaultdict(list)
in_degree = defaultdict(int)

# build graph
for (u, v), e in edges:
    adj[u].append(v)
    in_degree[v] += 1
    if u not in in_degree: in_degree[u] = 0

# khan's algo for topological sort
q = [n for n in in_degree if in_degree[n] == 0]
sorted_nodes = []

while q:
    n = q.pop(0)
    sorted_nodes.append(n)
    for neighbor in adj[n]:
        in_degree[neighbor] -= 1
        if in_degree[neighbor] == 0:
            q.append(neighbor)

if len(sorted_nodes) == len(in_degree):
    print("No cycles detected.")
    sys.exit(0)

print(f"Cycles detected. Initial edges: {len(builder.edges)}")
# remove edges to break cycle by just using the edges we added
builder.edges.clear()

# Add them back but ensuring acyclic structure
# A simple way to guarantee acyclic is to enforce an arbitrary total order on nodes
nodes_list = list(builder.nodes)
node_order = {node: i for i, node in enumerate(nodes_list)}

for (u, v), edge in edges:
    if node_order[u] < node_order[v]:
        builder.edges[(u, v)] = edge

print(f"Edges remaining: {len(builder.edges)}")
builder.save_state()

